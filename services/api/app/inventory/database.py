"""Two databases: the existing TinyDB auth client, and SQLModel on PostgreSQL.

The SQLModel engine is a pool, not a session. `get_db` opens a session for
one request and closes it. Nothing in this module keeps a session at import
time. SQLite is rejected: it cannot satisfy the PostgreSQL criteria.
"""

from __future__ import annotations

import logging
import os
import re
from collections.abc import Iterator

from fastapi import HTTPException
from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine
from sqlalchemy.pool import NullPool
from sqlmodel import Session, SQLModel

logger = logging.getLogger("nexova.api")

_SCHEMA = re.compile(r"^[a-z][a-z0-9_]{0,62}$")
_engine: Engine | None = None
_engine_key: tuple[str, str] | None = None


class InventoryDatabaseError(RuntimeError):
    """DATABASE_URL is missing or is not a PostgreSQL URL."""


def database_url() -> str:
    return os.environ.get("DATABASE_URL", "").strip()


def inventory_schema() -> str:
    raw = os.environ.get("INVENTORY_SCHEMA", "").strip() or "public"
    if not _SCHEMA.match(raw):
        raise InventoryDatabaseError("INVENTORY_SCHEMA no es un identificador válido.")
    return raw


def normalize_database_url(url: str) -> str:
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://") :]
    if url.startswith("postgresql://"):
        url = "postgresql+psycopg2://" + url[len("postgresql://") :]
    if url.startswith("sqlite"):
        raise InventoryDatabaseError("SQLite no es el almacén de inventario.")
    if not url.startswith("postgresql+psycopg2://"):
        raise InventoryDatabaseError("DATABASE_URL tiene que ser una URI de PostgreSQL.")
    return url


def _transaction_pooler(url: str) -> bool:
    lowered = url.lower()
    return "pgbouncer=true" in lowered or ":6543/" in lowered or ":6543?" in lowered


def reset_engine() -> None:
    """Drop the cached pool. Tests use this between schemas."""
    global _engine, _engine_key
    if _engine is not None:
        _engine.dispose()
    _engine = None
    _engine_key = None


def get_engine() -> Engine:
    global _engine, _engine_key
    raw = database_url()
    if not raw:
        raise InventoryDatabaseError("Falta DATABASE_URL. El inventario no tiene PostgreSQL.")
    url = normalize_database_url(raw)
    schema = inventory_schema()
    key = (url, schema)
    if _engine is not None and _engine_key == key:
        return _engine
    reset_engine()
    _ensure_schema(url, schema)
    kwargs: dict = {"pool_pre_ping": True}
    if _transaction_pooler(url):
        kwargs = {"poolclass": NullPool}
    engine = create_engine(url, **kwargs)
    if schema != "public":

        @event.listens_for(engine, "connect")
        def _search_path(dbapi_connection, _record) -> None:
            cursor = dbapi_connection.cursor()
            cursor.execute(f'SET search_path TO "{schema}"')
            cursor.close()

    _engine = engine
    _engine_key = key
    return engine


def _ensure_schema(url: str, schema: str) -> None:
    if schema == "public":
        return
    admin = create_engine(url, poolclass=NullPool)
    try:
        with admin.begin() as connection:
            connection.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema}"'))
    finally:
        admin.dispose()


def create_all(engine: Engine) -> None:
    """Create inventory tables. Learning setup only: not a migration tool."""
    from app.inventory import models as _models

    del _models
    SQLModel.metadata.create_all(engine)


def ensure_unit_cost_column(engine: Engine) -> None:
    """Add the capture-phase cost column on databases created before it existed.

    create_all does not alter an existing table. The column stays nullable:
    a row without a cost is not a variance.
    """
    with engine.begin() as connection:
        connection.execute(text("ALTER TABLE assetentry ADD COLUMN IF NOT EXISTS unit_cost_minor INTEGER"))


def init_databases() -> None:
    """Open TinyDB auth and, when DATABASE_URL is set, the SQLModel engine."""
    from app.auth.store import get_auth_db

    get_auth_db()
    if not database_url():
        logger.info("inventory: DATABASE_URL ausente; /inventory responderá 503")
        return
    engine = get_engine()
    create_all(engine)
    ensure_unit_cost_column(engine)
    if os.environ.get("INVENTORY_AUTOSEED", "1") != "0":
        from app.inventory.seed import seed_if_empty

        seed_if_empty(engine)


def get_db() -> Iterator[Session]:
    """One SQLModel session per request. There is no module-level session."""
    try:
        engine = get_engine()
    except InventoryDatabaseError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
