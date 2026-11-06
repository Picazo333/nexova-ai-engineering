"""TTL cache: expiry, invalidation, and private keys that are not shared."""

from __future__ import annotations

import logging

from fastapi.testclient import TestClient

from app.cache import (
    ORDERS_LIST,
    SUPPLIERS_LIST,
    CacheScopeError,
    TtlCache,
    fetch_cached,
    make_key,
    reset_cache,
)
from tests.auth_support import bearer, register, token_for


def _contract(**overrides: object) -> dict:
    body = {
        "name": "Contrato caché",
        "country": "Spain",
        "categories": ["job_boards"],
        "monthly_rate": 80,
        "currency": "EUR",
        "status": "active",
    }
    body.update(overrides)
    return body


def _auth(client: TestClient) -> dict[str, str]:
    register(client, "cache-ops@nexova.test", "Ops Caché")
    return {**bearer(token_for(client, "cache-ops@nexova.test")), "Accept": "application/json"}


def test_ttl_expires_and_a_stale_fill_is_discarded() -> None:
    clock = {"now": 1_000.0}
    cache = TtlCache(clock=lambda: clock["now"])
    assert cache.put("k", {"stock": 12}, 30, namespace=ORDERS_LIST, generation=0)
    assert cache.get("k").hit is True
    assert cache.get("k").value == {"stock": 12}
    clock["now"] = 1_029.9
    assert cache.get("k").hit is True
    clock["now"] = 1_030.0
    assert cache.get("k").hit is False

    seen = cache.generation(ORDERS_LIST)
    cache.invalidate_namespace(ORDERS_LIST)
    assert cache.put("k", {"stock": 1}, 30, namespace=ORDERS_LIST, generation=seen) is False
    assert cache.get("k").hit is False


def test_zero_ttl_is_rejected_and_callers_cannot_mutate_the_stored_value() -> None:
    cache = TtlCache()
    try:
        cache.put("k", {"n": 1}, 0, namespace="demo", generation=0)
        raise AssertionError("un TTL de cero no puede guardarse")
    except ValueError:
        pass
    cache.put("k", [{"n": 1}], 10, namespace="demo", generation=0)
    first = cache.get("k")
    assert first.hit is True
    first.value[0]["n"] = 9
    assert cache.get("k").value[0]["n"] == 1


def test_private_keys_include_the_user_and_are_not_shared() -> None:
    try:
        make_key("profiles.me", {}, private=True, user_id=None)
        raise AssertionError("sin usuario no hay clave privada")
    except CacheScopeError:
        pass
    try:
        make_key("profiles.me", {}, private=True, user_id="  ")
        raise AssertionError("un id en blanco no cuenta")
    except CacheScopeError:
        pass
    try:
        make_key(ORDERS_LIST, {"office": ""}, private=False, user_id="user-a")
        raise AssertionError("una clave compartida no lleva usuario")
    except CacheScopeError:
        pass

    left = make_key("profiles.me", {}, private=True, user_id="user-a")
    right = make_key("profiles.me", {}, private=True, user_id="user-b")
    assert left != right
    assert "user:user-a" in left
    assert "shared" not in left
    shared = make_key(ORDERS_LIST, {"office": "Valencia"}, private=False, user_id=None)
    assert shared == "inventory.orders|shared|office=Valencia"

    cache = TtlCache()
    generation = cache.generation("profiles.me")
    cache.put(left, {"email": "a@nexova.test"}, 30, namespace="profiles.me", generation=generation)
    assert cache.get(right).hit is False
    assert cache.get(left).value == {"email": "a@nexova.test"}

    reset_cache(TtlCache())

    def load_profile(user_id: str) -> dict:
        return fetch_cached(
            "profiles.me",
            {},
            30,
            lambda: {"email": f"{user_id}@nexova.test"},
            private=True,
            user_id=user_id,
        )

    assert load_profile("user-a")["email"] == "user-a@nexova.test"
    assert load_profile("user-b")["email"] == "user-b@nexova.test"
    assert load_profile("user-a")["email"] == "user-a@nexova.test"


def test_supplier_list_hits_then_drops_on_write_and_ignores_a_rejected_write(client: TestClient) -> None:
    headers = _auth(client)
    first = client.get("/suppliers", headers=headers)
    assert first.status_code == 200
    assert first.headers["x-nexova-cache"] == "MISS"
    second = client.get("/suppliers", headers=headers)
    assert second.headers["x-nexova-cache"] == "HIT"
    assert second.json() == first.json()

    rejected = client.post("/suppliers", json={"name": ""}, headers=headers)
    assert rejected.status_code == 422
    assert client.get("/suppliers", headers=headers).headers["x-nexova-cache"] == "HIT"

    created = client.post("/suppliers", json=_contract(), headers=headers)
    assert created.status_code == 201, created.text
    after_create = client.get("/suppliers", headers=headers)
    assert after_create.headers["x-nexova-cache"] == "MISS"
    assert any(row["id"] == created.json()["id"] for row in after_create.json())
    assert client.get("/suppliers", headers=headers).headers["x-nexova-cache"] == "HIT"

    rated = client.patch(
        f"/suppliers/{created.json()['id']}/rate",
        json={"monthly_rate": 140},
        headers=headers,
    )
    assert rated.status_code == 200, rated.text
    after_rate = client.get("/suppliers", headers=headers)
    assert after_rate.headers["x-nexova-cache"] == "MISS"
    stored = next(row for row in after_rate.json() if row["id"] == created.json()["id"])
    assert stored["monthly_rate"] == 140

    spain = client.get("/suppliers?country=Spain", headers=headers)
    assert spain.headers["x-nexova-cache"] == "MISS"
    assert client.get("/suppliers?country=USA", headers=headers).headers["x-nexova-cache"] == "MISS"
    assert client.get("/suppliers?country=Spain", headers=headers).headers["x-nexova-cache"] == "HIT"

    suspended = client.patch(
        f"/suppliers/{created.json()['id']}/status",
        json={"status": "suspended"},
        headers=headers,
    )
    assert suspended.status_code == 200, suspended.text
    after_status = client.get("/suppliers", headers=headers)
    assert after_status.headers["x-nexova-cache"] == "MISS"
    suspended_row = next(row for row in after_status.json() if row["id"] == created.json()["id"])
    assert suspended_row["status"] == "suspended"

    removed = client.delete(f"/suppliers/{created.json()['id']}", headers=headers)
    assert removed.status_code == 200
    after_delete = client.get("/suppliers?country=Spain", headers=headers)
    assert after_delete.headers["x-nexova-cache"] == "MISS"
    assert all(row["id"] != created.json()["id"] for row in after_delete.json())


def test_supplier_list_expires_with_the_ttl(client: TestClient) -> None:
    clock = {"now": 0.0}
    reset_cache(TtlCache(clock=lambda: clock["now"]))
    headers = _auth(client)
    assert client.get("/suppliers", headers=headers).headers["x-nexova-cache"] == "MISS"
    assert client.get("/suppliers", headers=headers).headers["x-nexova-cache"] == "HIT"
    clock["now"] = 59.9
    assert client.get("/suppliers", headers=headers).headers["x-nexova-cache"] == "HIT"
    clock["now"] = 60.0
    expired = client.get("/suppliers", headers=headers)
    assert expired.headers["x-nexova-cache"] == "MISS"
    assert expired.json() == client.get("/suppliers", headers=headers).json()


def test_profile_and_session_are_not_cached(client: TestClient) -> None:
    headers = _auth(client)
    for path in ("/profiles/me", "/auth/me"):
        first = client.get(path, headers=headers)
        second = client.get(path, headers=headers)
        assert first.status_code == 200
        assert "x-nexova-cache" not in first.headers
        assert "x-nexova-cache" not in second.headers
        assert first.json() == second.json()


def test_cache_header_is_visible_to_the_backoffice_origin(client: TestClient) -> None:
    headers = {
        **_auth(client),
        "Origin": "http://127.0.0.1:3001",
    }
    listed = client.get("/suppliers", headers=headers)
    assert listed.status_code == 200
    assert "X-Nexova-Cache" in listed.headers.get("access-control-expose-headers", "")


def test_timing_middleware_logs_each_request(client: TestClient, caplog) -> None:
    caplog.set_level(logging.INFO, logger="api.timing")
    response = client.get("/health")
    assert response.status_code == 200
    assert any("GET /health → 200" in record.message and "ms" in record.message for record in caplog.records)


def test_cached_supplier_namespace_constant_matches_the_key() -> None:
    assert make_key(SUPPLIERS_LIST, {"category": "", "country": "", "status": ""}, private=False, user_id=None).startswith(
        "suppliers.list|shared|"
    )
