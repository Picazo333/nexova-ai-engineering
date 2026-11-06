"""Time the heavy reads before and, when the cache is installed, after.

Uses PostgreSQL from DATABASE_URL or NEXOVA_TEST_DATABASE_URL. Creates a
private schema and drops it at the end. Prints one JSON object.
"""

from __future__ import annotations

import json
import os
import statistics
import tempfile
import time
import uuid
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool


def _url() -> str:
    raw = os.environ.get("DATABASE_URL", "").strip() or os.environ.get("NEXOVA_TEST_DATABASE_URL", "").strip()
    if not raw:
        raise SystemExit("Falta DATABASE_URL o NEXOVA_TEST_DATABASE_URL.")
    return raw


def _percentile(samples: list[float], fraction: float) -> float:
    if not samples:
        return 0.0
    ordered = sorted(samples)
    index = min(len(ordered) - 1, max(0, round((len(ordered) - 1) * fraction)))
    return ordered[index]


def _time(call, rounds: int = 21) -> dict[str, float]:
    samples: list[float] = []
    for _ in range(rounds):
        started = time.perf_counter()
        call()
        samples.append((time.perf_counter() - started) * 1000)
    warm = samples[0]
    rest = samples[1:]
    return {
        "warmup_ms": round(warm, 2),
        "median_ms": round(statistics.median(rest), 2),
        "p95_ms": round(_percentile(rest, 0.95), 2),
        "min_ms": round(min(rest), 2),
        "rounds": len(rest),
    }


def main() -> None:
    os.environ["DATABASE_URL"] = _url()
    schema = "cachem_" + uuid.uuid4().hex[:12]
    os.environ["INVENTORY_SCHEMA"] = schema
    os.environ["INVENTORY_AUTOSEED"] = "0"
    supplier_dir = tempfile.mkdtemp(prefix="nexova-suppliers-")
    os.environ["SUPPLIERS_DATA_DIR"] = supplier_dir
    os.environ["SUPPLIERS_AUTOSEED"] = "0"

    from app.inventory.database import create_all, get_engine, normalize_database_url, reset_engine
    from app.inventory.service import get_asset, list_assets, list_orders
    from app.inventory.volume import seed_volume
    from database import reset_db
    from models import SupplierCreate
    from sqlmodel import Session

    import directory

    reset_engine()
    reset_db()
    engine = get_engine()
    create_all(engine)
    counts = seed_volume(engine, assets=480, entries_each=12, exits_each=4)

    countries = ("Spain", "USA")
    categories = (
        "job_boards",
        "ats_software",
        "assessment_tools",
        "training_platforms",
        "payroll_and_hr_software",
        "video_interview",
        "background_check",
        "office_and_facilities",
    )
    statuses = ("active", "suspended")
    currencies = ("EUR", "USD")
    for index in range(1500):
        directory.create_supplier(
            SupplierCreate(
                name=f"Contrato volumen {index + 1} {categories[index % len(categories)]}",
                country=countries[index % 2],
                categories=[categories[index % len(categories)]],
                monthly_rate=120 + (index % 90) * 15.5,
                currency=currencies[index % 2],
                status=statuses[0 if index % 5 else 1],
                contract_renewal_date=f"2026-{(index % 12) + 1:02d}-15",
                contact_email=f"ops{index + 1}@proveedor-volumen.test",
                notes=f"Renovación {index % 4} de la sede {countries[index % 2]}.",
            )
        )

    def _session_call(fn):
        def run():
            with Session(engine) as session:
                return fn(session)

        return run

    with Session(engine) as session:
        first_id = list_assets(session)[0].id

    from app.cache import reset_cache

    reset_cache()
    uncached = {
        "list_assets": _time(_session_call(lambda session: list_assets(session))),
        "list_assets_valencia": _time(_session_call(lambda session: list_assets(session, "Valencia"))),
        "list_orders": _time(_session_call(lambda session: list_orders(session))),
        "get_asset": _time(_session_call(lambda session: get_asset(session, first_id))),
        "list_suppliers": _time(
            lambda: directory._list_suppliers_uncached(country=None, category=None, status=None)
        ),
        "list_suppliers_spain": _time(
            lambda: directory._list_suppliers_uncached(country="Spain", category=None, status=None)
        ),
        "get_supplier": _time(lambda: directory.get_supplier(1)),
    }

    os.environ["JWT_SECRET"] = "measure-only-local"
    os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"
    os.environ["AUTH_BCRYPT_ROUNDS"] = "4"
    os.environ["EMAIL_TRANSPORT"] = "mock"
    os.environ["AUTH_DATA_DIR"] = tempfile.mkdtemp(prefix="nexova-auth-")
    os.environ["PUBLIC_APP_URL"] = "http://127.0.0.1:3000"
    root = Path(__file__).resolve().parents[3]
    import sys

    for extra in (root / "packages", root / "packages" / "shared", root):
        entry = str(extra)
        if entry not in sys.path:
            sys.path.insert(0, entry)
    from app.main import create_app
    from fastapi.testclient import TestClient

    with TestClient(create_app()) as client:
        created = client.post(
            "/users",
            json={"email": "medida@nexova.test", "password": "clave-segura-1", "name": "Medida"},
        )
        token = client.post(
            "/auth/login",
            json={"email": "medida@nexova.test", "password": "clave-segura-1"},
        ).json()["access_token"]
        assert created.status_code == 201
    auth = {"Accept": "application/json", "Authorization": f"Bearer {token}"}
    # A new client does not keep the in-process cache. Time inside one process.
    reset_cache()
    cached_http = {}
    with TestClient(create_app()) as client:
        def once(path: str, headers: dict) -> tuple[float, str | None, int]:
            started = time.perf_counter()
            response = client.get(path, headers=headers)
            return (time.perf_counter() - started) * 1000, response.headers.get("x-nexova-cache"), response.status_code

        def series(path: str, headers: dict) -> dict:
            rows = [once(path, headers) for _ in range(8)]
            assert all(status == 200 for _, _, status in rows), rows
            miss = rows[0][0]
            hits = [item[0] for item in rows[1:]]
            return {
                "miss_ms": round(miss, 2),
                "hit_median_ms": round(statistics.median(hits), 2),
                "hit_min_ms": round(min(hits), 2),
                "marks": [item[1] for item in rows],
            }

        cached_http = {
            "orders": series("/inventory/orders", {"Accept": "application/json"}),
            "orders_valencia": series("/inventory/orders?office=Valencia", {"Accept": "application/json"}),
            "products": series("/inventory/products", {"Accept": "application/json"}),
            "suppliers": series("/suppliers", auth),
            "suppliers_spain": series("/suppliers?country=Spain", auth),
            "profile": series("/profiles/me", auth),
        }

    briefing_schema = "cacheb_" + uuid.uuid4().hex[:12]
    os.environ["INVENTORY_SCHEMA"] = briefing_schema
    reset_engine()
    briefing_engine = get_engine()
    create_all(briefing_engine)
    from app.inventory.models import AssetEntry, AssetExit
    from app.inventory.seed import seed_if_empty
    from sqlmodel import select as sql_select

    seeded_assets = seed_if_empty(briefing_engine)

    def _brief_call(fn):
        def run():
            with Session(briefing_engine) as session:
                return fn(session)

        return run

    briefing_orders = _time(_brief_call(lambda session: list_orders(session)))
    briefing_assets = _time(_brief_call(lambda session: list_assets(session)))
    with Session(briefing_engine) as session:
        briefing_rows = {
            "assets": seeded_assets,
            "entries": len(session.exec(sql_select(AssetEntry.id)).all()),
            "exits": len(session.exec(sql_select(AssetExit.id)).all()),
        }

    report = {
        "postgres": "PostgreSQL 16.15 local",
        "volume_schema": schema,
        "rows": counts,
        "suppliers": 1500,
        "briefing_rows": briefing_rows,
        "uncached_volume": uncached,
        "http_after_cache": cached_http,
        "uncached_briefing_orders": briefing_orders,
        "uncached_briefing_assets": briefing_assets,
    }
    print(json.dumps(report, indent=2))

    reset_engine()
    reset_db()
    admin = create_engine(normalize_database_url(os.environ["DATABASE_URL"]), poolclass=NullPool)
    try:
        with admin.begin() as connection:
            for name in (schema, briefing_schema):
                connection.execute(text(f'DROP SCHEMA IF EXISTS "{name}" CASCADE'))
    finally:
        admin.dispose()
    Path(supplier_dir, "suppliers.json").unlink(missing_ok=True)


if __name__ == "__main__":
    main()
