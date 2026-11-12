"""TinyDB file for centralized incidents.

The public record matches the briefing model. ``source_key`` is stored only so
the historical CSV can be loaded twice without duplicating rows. It is not
returned by the API.
"""

from __future__ import annotations

import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from tinydb import Query, TinyDB

from app.config import data_dir

_lock = threading.Lock()
_db: TinyDB | None = None
_path: Path | None = None


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def records_file() -> Path:
    return data_dir() / "incident_records.json"


def get_incidents_db() -> TinyDB:
    global _db, _path
    path = records_file()
    if _db is not None and _path == path:
        return _db
    if _db is not None:
        _db.close()
    path.parent.mkdir(parents=True, exist_ok=True)
    _db = TinyDB(path)
    _path = path
    return _db


def reset_incidents_db() -> None:
    """Close the cached handle so the next call follows the current env path."""
    global _db, _path
    with _lock:
        if _db is not None:
            _db.close()
        _db = None
        _path = None


def _public(stored: dict[str, Any]) -> dict[str, Any]:
    from nexova_incidents.model import public_incident

    return public_incident(stored)


def insert_new(record: dict[str, Any]) -> dict[str, Any] | None:
    """Insert when ``source_key`` is new. Return the public row, or None if it already exists."""
    key = record.get("source_key")
    with _lock:
        database = get_incidents_db()
        if key and database.contains(Query().source_key == key):
            return None
        stored = {
            "id": str(uuid.uuid4()),
            "title": record["title"],
            "description": record["description"],
            "category": record["category"],
            "status": record["status"],
            "origin": record["origin"],
            "branch": record["branch"],
            "created_at": record["created_at"],
            "updated_at": record["updated_at"],
            "source_key": key or "",
        }
        database.insert(stored)
    return _public(stored)


def create_incident(fields: dict[str, str]) -> dict[str, Any]:
    now = utc_now()
    created = insert_new(
        {
            "title": fields["title"].strip(),
            "description": fields["description"].strip(),
            "category": fields["category"],
            "status": fields["status"],
            "origin": fields["origin"],
            "branch": fields["branch"],
            "created_at": now,
            "updated_at": now,
            "source_key": f"manual:{uuid.uuid4()}",
        }
    )
    if created is None:
        raise RuntimeError("no se pudo guardar la incidencia")
    return created


def list_incidents(
    *,
    status: str | None = None,
    origin: str | None = None,
    branch: str | None = None,
    category: str | None = None,
) -> list[dict[str, Any]]:
    with _lock:
        rows = [dict(item) for item in get_incidents_db().all()]
    selected = [
        row
        for row in rows
        if (status is None or row.get("status") == status)
        and (origin is None or row.get("origin") == origin)
        and (branch is None or row.get("branch") == branch)
        and (category is None or row.get("category") == category)
    ]
    selected.sort(key=lambda row: (row.get("created_at", ""), row.get("id", "")), reverse=True)
    return [_public(row) for row in selected]


def get_incident(incident_id: str) -> dict[str, Any] | None:
    with _lock:
        found = get_incidents_db().get(Query().id == incident_id)
    if found is None:
        return None
    return _public(dict(found))


def update_status(incident_id: str, status: str) -> dict[str, Any] | None:
    with _lock:
        database = get_incidents_db()
        found = database.get(Query().id == incident_id)
        if found is None:
            return None
        database.update(
            {"status": status, "updated_at": utc_now()},
            Query().id == incident_id,
        )
        updated = database.get(Query().id == incident_id)
    if updated is None:
        return None
    return _public(dict(updated))


def summary() -> dict[str, Any]:
    from nexova_incidents.model import empty_summary

    totals = empty_summary()
    with _lock:
        rows = list(get_incidents_db().all())
    totals["total"] = len(rows)
    for row in rows:
        for bucket, field in (
            ("by_status", "status"),
            ("by_category", "category"),
            ("by_origin", "origin"),
            ("by_branch", "branch"),
        ):
            code = row.get(field)
            if code in totals[bucket]:
                totals[bucket][code] += 1
    return totals


def count_incidents() -> int:
    with _lock:
        return len(get_incidents_db())
