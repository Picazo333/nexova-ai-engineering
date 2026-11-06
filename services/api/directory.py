"""Validated reads and writes. Callers validate with Pydantic before these functions."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from tinydb.table import Document

from database import db_lock, get_db
from models import SupplierCreate, SupplierPublic


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _public(document: Document) -> dict[str, Any]:
    payload = dict(document)
    payload["id"] = document.doc_id
    return SupplierPublic.model_validate(payload).as_dict()


def _drop_supplier_list() -> None:
    # The write is already in TinyDB. Drop the list now, not on a timer.
    from app.cache import SUPPLIERS_LIST, SUPPLIERS_LIST_JSON, get_cache

    cache = get_cache()
    cache.invalidate_namespace(SUPPLIERS_LIST)
    cache.invalidate_namespace(SUPPLIERS_LIST_JSON)


def create_supplier(model: SupplierCreate) -> dict[str, Any]:
    stored = model.model_dump(mode="json")
    stored["updated_at"] = _now()
    with db_lock():
        doc_id = get_db().insert(stored)
        document = get_db().get(doc_id=doc_id)
    if document is None:
        raise RuntimeError("el proveedor insertado no se pudo leer")
    _drop_supplier_list()
    return _public(document)


def _list_suppliers_uncached(
    *,
    country: str | None,
    category: str | None,
    status: str | None,
) -> list[dict[str, Any]]:
    with db_lock():
        documents = list(get_db())
    documents.sort(key=lambda item: item.doc_id)
    rows: list[dict[str, Any]] = []
    for document in documents:
        if country is not None and document.get("country") != country:
            continue
        categories = document.get("categories") or []
        if category is not None and category not in categories:
            continue
        if status is not None and document.get("status") != status:
            continue
        rows.append(_public(document))
    return rows


def list_suppliers(
    *,
    country: str | None = None,
    category: str | None = None,
    status: str | None = None,
) -> list[dict[str, Any]]:
    """Same filters as before. Repeated identical filters reuse the list for 60 s.

    A create, rate change, status change or delete drops the namespace first.
    The payload does not vary by user: every authenticated reader sees the
    same contract. The key stays shared for that reason.
    """
    from app.cache import SUPPLIERS_LIST, SUPPLIERS_LIST_TTL_SECONDS, fetch_cached

    return fetch_cached(
        SUPPLIERS_LIST,
        {
            "country": country or "",
            "category": category or "",
            "status": status or "",
        },
        SUPPLIERS_LIST_TTL_SECONDS,
        lambda: _list_suppliers_uncached(country=country, category=category, status=status),
        private=False,
        user_id=None,
    )


def get_supplier(supplier_id: int) -> dict[str, Any] | None:
    with db_lock():
        document = get_db().get(doc_id=supplier_id)
    if document is None:
        return None
    return _public(document)


def update_rate(supplier_id: int, monthly_rate: float) -> dict[str, Any] | None:
    with db_lock():
        database = get_db()
        document = database.get(doc_id=supplier_id)
        if document is None:
            return None
        database.update(
            {"monthly_rate": monthly_rate, "updated_at": _now()},
            doc_ids=[supplier_id],
        )
        updated = database.get(doc_id=supplier_id)
    if updated is None:
        return None
    _drop_supplier_list()
    return _public(updated)


def update_status(supplier_id: int, status: str) -> dict[str, Any] | None:
    with db_lock():
        database = get_db()
        document = database.get(doc_id=supplier_id)
        if document is None:
            return None
        database.update({"status": status}, doc_ids=[supplier_id])
        updated = database.get(doc_id=supplier_id)
    if updated is None:
        return None
    _drop_supplier_list()
    return _public(updated)


def delete_supplier(supplier_id: int) -> dict[str, Any] | None:
    with db_lock():
        database = get_db()
        document = database.get(doc_id=supplier_id)
        if document is None:
            return None
        removed = _public(document)
        database.remove(doc_ids=[supplier_id])
    _drop_supplier_list()
    return removed


def count_suppliers() -> int:
    with db_lock():
        return len(get_db())


def insert_missing(models: list[SupplierCreate]) -> tuple[int, int]:
    """Insert models whose name is not already stored. Returns (inserted, skipped)."""
    inserted = 0
    skipped = 0
    stamped = _now()
    with db_lock():
        database = get_db()
        present = {document.get("name") for document in database}
        for model in models:
            if model.name in present:
                skipped += 1
                continue
            stored = model.model_dump(mode="json")
            stored["updated_at"] = stamped
            database.insert(stored)
            present.add(model.name)
            inserted += 1
    if inserted:
        _drop_supplier_list()
    return inserted, skipped
