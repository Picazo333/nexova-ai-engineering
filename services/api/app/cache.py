"""In-process TTL cache for repeated reads.

One process, one dictionary. This API runs as a single uvicorn process, so a
write in this process can drop the entries it just changed. The TTL is still
mandatory: a value without an expiry would survive a missed invalidation, and
another process would never see the write.

Private payloads use a different key per user. ``make_key`` rejects a private
entry with no user and a shared entry that tries to carry one.
"""

from __future__ import annotations

import threading
import time
from collections.abc import Callable, Mapping
from contextvars import ContextVar
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

T = TypeVar("T")

SUPPLIERS_LIST = "suppliers.list"
SUPPLIERS_LIST_JSON = "suppliers.list.json"
ORDERS_LIST = "inventory.orders"
SUPPLIERS_LIST_TTL_SECONDS = 60.0
ORDERS_LIST_TTL_SECONDS = 30.0

@dataclass
class _RequestBook:
    """Shared with the endpoint thread. Mutating it is visible to the middleware.

    A sync route runs in a threadpool. That thread receives a copy of the
    context, so replacing a ContextVar there never reaches the middleware.
    The copy still points at this same object.
    """

    mark: str | None = None
    pending: set[str] | None = None

    def __post_init__(self) -> None:
        if self.pending is None:
            self.pending = set()


_book: ContextVar[_RequestBook | None] = ContextVar("nexova_cache_book", default=None)


class CacheScopeError(ValueError):
    """The key would hide private data under a shared scope, or the reverse."""


@dataclass(frozen=True)
class CacheHit(Generic[T]):
    hit: bool
    value: T | None


def make_key(
    namespace: str,
    parts: Mapping[str, str],
    *,
    private: bool,
    user_id: str | None,
) -> str:
    """Build a cache key. Private data always includes the user id."""
    if not namespace or any(character in namespace for character in "|\n\r"):
        raise ValueError("El namespace de la caché no es válido.")
    if private:
        owner = (user_id or "").strip()
        if not owner:
            raise CacheScopeError("Un dato privado necesita el id del usuario en la clave.")
        scope = f"user:{owner}"
    else:
        if user_id is not None and str(user_id).strip():
            raise CacheScopeError("Una clave compartida no puede llevar un id de usuario.")
        scope = "shared"
    encoded = "&".join(f"{name}={parts[name]}" for name in sorted(parts))
    return f"{namespace}|{scope}|{encoded}"


def _snapshot(value: Any) -> Any:
    if isinstance(value, list):
        return [_snapshot(item) for item in value]
    if isinstance(value, dict):
        return {key: _snapshot(item) for key, item in value.items()}
    copy = getattr(value, "model_copy", None)
    if copy is not None:
        return copy(deep=True)
    return value


@dataclass
class _Slot:
    expires_at: float
    generation: int
    namespace: str
    value: Any


class TtlCache:
    """Dictionary with a per-entry expiry and a per-namespace generation.

    ``put`` refuses a value whose generation is older than the current one, so
    a read that started before a write cannot repopulate the cache with the
    rows it saw.
    """

    def __init__(self, clock: Callable[[], float] | None = None) -> None:
        self._clock = clock or time.monotonic
        self._lock = threading.Lock()
        self._items: dict[str, _Slot] = {}
        self._generation: dict[str, int] = {}

    def generation(self, namespace: str) -> int:
        with self._lock:
            return self._generation.get(namespace, 0)

    def get(self, key: str) -> CacheHit[Any]:
        now = self._clock()
        with self._lock:
            slot = self._items.get(key)
            if slot is None:
                return CacheHit(False, None)
            current = self._generation.get(slot.namespace, 0)
            if now >= slot.expires_at or slot.generation != current:
                self._items.pop(key, None)
                return CacheHit(False, None)
            return CacheHit(True, _snapshot(slot.value))

    def put(
        self,
        key: str,
        value: Any,
        ttl_seconds: float,
        *,
        namespace: str,
        generation: int,
    ) -> bool:
        if ttl_seconds <= 0:
            raise ValueError("El TTL tiene que ser mayor que cero.")
        stored = _snapshot(value)
        with self._lock:
            if self._generation.get(namespace, 0) != generation:
                return False
            self._items[key] = _Slot(
                expires_at=self._clock() + ttl_seconds,
                generation=generation,
                namespace=namespace,
                value=stored,
            )
            return True

    def invalidate_namespace(self, namespace: str) -> int:
        with self._lock:
            self._generation[namespace] = self._generation.get(namespace, 0) + 1
            stale = [key for key, slot in self._items.items() if slot.namespace == namespace]
            for key in stale:
                del self._items[key]
            return len(stale)


_cache = TtlCache()


def get_cache() -> TtlCache:
    return _cache


def reset_cache(cache: TtlCache | None = None) -> None:
    """Tests pass their own clock. Production calls this with no argument."""
    global _cache
    _cache = cache or TtlCache()


def mark_cache(status: str) -> None:
    book = _book.get()
    if book is not None and status in ("HIT", "MISS"):
        book.mark = status


def schedule_invalidation(namespace: str) -> None:
    """Drop a namespace after the response, once the database commit has run.

    Outside a request there is no commit to wait for, so the drop is immediate.
    """
    book = _book.get()
    if book is None or book.pending is None:
        get_cache().invalidate_namespace(namespace)
        return
    book.pending.add(namespace)


def fetch_cached(
    namespace: str,
    parts: Mapping[str, str],
    ttl_seconds: float,
    load: Callable[[], T],
    *,
    private: bool,
    user_id: str | None,
) -> T:
    key = make_key(namespace, parts, private=private, user_id=user_id)
    cache = get_cache()
    generation = cache.generation(namespace)
    found = cache.get(key)
    if found.hit:
        mark_cache("HIT")
        return found.value  # type: ignore[return-value]
    value = load()
    cache.put(key, value, ttl_seconds, namespace=namespace, generation=generation)
    mark_cache("MISS")
    return value


def begin_request() -> object:
    return _book.set(_RequestBook())


def finish_request(token: object, status_code: int) -> str | None:
    book = _book.get()
    if book is not None and status_code < 400:
        for namespace in book.pending or ():
            get_cache().invalidate_namespace(namespace)
    mark = book.mark if book is not None else None
    _book.reset(token)  # type: ignore[arg-type]
    if mark in ("HIT", "MISS"):
        return mark
    return None
