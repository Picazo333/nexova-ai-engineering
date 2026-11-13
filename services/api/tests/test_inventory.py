"""Inventory against PostgreSQL. SQLite and a missing URL are not a pass.

NEXOVA_TEST_DATABASE_URL points at a real PostgreSQL database. Each test
uses its own schema and drops it afterwards. The rest of the suite never
sees DATABASE_URL.
"""

from __future__ import annotations

import os
import threading
import uuid
from collections.abc import Iterator

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.pool import NullPool
from sqlmodel import Session

from app.inventory.models import Asset, AssetEntry, AssetExit
from app.inventory.schemas import AssetExitCreate, AssetRead
from app.inventory.seed import EXPECTED_STOCK, SEED_USER_UUID
from tests.auth_support import bearer, register, token_for


def test_products_without_database_url_are_503(client: TestClient) -> None:
    response = client.get("/inventory/products")
    assert response.status_code == 503
    body = response.json()
    assert body["error"] == "http_error"
    assert "message" in body
    assert "postgres://" not in response.text
    assert "sqlite" not in response.text.lower()


def test_sqlite_url_is_rejected() -> None:
    from app.inventory.database import InventoryDatabaseError, normalize_database_url

    with pytest.raises(InventoryDatabaseError):
        normalize_database_url("sqlite:///tmp/inventory.db")


def test_stock_is_not_a_column_and_schemas_are_separate() -> None:
    assert "current_stock" not in Asset.__table__.columns
    assert "current_stock" in AssetRead.model_fields
    assert Asset.__table__.columns["sku"].unique is True
    assert not AssetEntry.__table__.columns["user_uuid"].foreign_keys
    assert not AssetExit.__table__.columns["user_uuid"].foreign_keys
    assert AssetEntry.__table__.columns["asset_id"].foreign_keys
    assert AssetExit.__table__.columns["asset_id"].foreign_keys


def test_router_prefix_and_no_global_session() -> None:
    import inspect

    import app.inventory.database as database
    from app.routers.inventory import router

    assert router.prefix == "/inventory"
    assert inspect.isgeneratorfunction(database.get_db)
    source = open(database.__file__, encoding="utf-8").read().split("def get_db", 1)[0]
    assert "session: Session" not in source
    assert "Session = " not in source


def test_openapi_lists_the_inventory_paths(client: TestClient) -> None:
    paths = client.get("/api/openapi.json").json()["paths"]
    for path in (
        "/inventory/products",
        "/inventory/products/{asset_id}",
        "/inventory/orders/inbound",
        "/inventory/orders/outbound",
        "/inventory/orders",
    ):
        assert path in paths
    assert paths["/inventory/products"]["post"]["security"] == [{"OAuth2PasswordBearer": []}]
    assert "security" not in paths["/inventory/products"]["get"]


def _postgres_url() -> str:
    url = os.environ.get("NEXOVA_TEST_DATABASE_URL", "").strip()
    if url.startswith("sqlite"):
        pytest.fail("SQLite no cuenta como PostgreSQL.")
    return url


@pytest.fixture()
def inventory_client(tmp_path, monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    url = _postgres_url()
    schema = "inv_" + uuid.uuid4().hex[:16]
    monkeypatch.setenv("DATABASE_URL", url)
    monkeypatch.setenv("INVENTORY_SCHEMA", schema)
    monkeypatch.setenv("INVENTORY_AUTOSEED", "1")
    monkeypatch.setenv("SUPPLIERS_DATA_DIR", str(tmp_path / "suppliers"))
    monkeypatch.setenv("SUPPLIERS_AUTOSEED", "0")
    monkeypatch.setenv("INCIDENTS_DATA_DIR", str(tmp_path / "incidents"))
    from app.auth.store import reset_auth_db
    from app.infrastructure.analysis_store import reset_store
    from app.inventory.database import normalize_database_url, reset_engine
    from app.main import create_app
    from database import reset_db
    from incident_store import reset_incidents_db

    reset_engine()
    reset_db()
    reset_auth_db()
    reset_incidents_db()
    reset_store(tmp_path / "incidents")
    try:
        with TestClient(create_app()) as test_client:
            yield test_client
    finally:
        reset_engine()
        reset_db()
        reset_auth_db()
        reset_incidents_db()
        admin = create_engine(normalize_database_url(url), poolclass=NullPool)
        try:
            with admin.begin() as connection:
                connection.execute(text(f'DROP SCHEMA IF EXISTS "{schema}" CASCADE'))
        finally:
            admin.dispose()


@pytest.fixture()
def token(inventory_client: TestClient) -> str:
    register(inventory_client, "inventario@nexova.test", name="Operaciones IT")
    return token_for(inventory_client, "inventario@nexova.test")


@pytest.mark.skipif(
    not os.environ.get("NEXOVA_TEST_DATABASE_URL", "").strip(),
    reason="NEXOVA_TEST_DATABASE_URL no está definido; no se simula PostgreSQL.",
)
def test_seed_stock_matches_entries_minus_exits(inventory_client: TestClient) -> None:
    listed = inventory_client.get("/inventory/products")
    assert listed.status_code == 200
    body = listed.json()
    assert len(body) == 6
    by_sku = {row["sku"]: row for row in body}
    assert set(by_sku) == set(EXPECTED_STOCK)
    for sku, stock in EXPECTED_STOCK.items():
        assert by_sku[sku]["current_stock"] == stock
        assert "current_stock" not in by_sku[sku] or isinstance(by_sku[sku]["current_stock"], int)
    paper = by_sku["NXV-OFF-001"]
    one = inventory_client.get(f"/inventory/products/{paper['id']}")
    assert one.status_code == 200
    assert one.json()["current_stock"] == 18
    assert one.json()["office"] == "Valencia"
    valencia = inventory_client.get("/inventory/products", params={"office": "Valencia"})
    assert {row["sku"] for row in valencia.json()} == {
        "NXV-IT-001",
        "NXV-PER-001",
        "NXV-OFF-001",
        "NXV-TRN-001",
    }
    assert inventory_client.get("/inventory/products", params={"office": "Lisboa"}).status_code == 422


@pytest.mark.skipif(
    not os.environ.get("NEXOVA_TEST_DATABASE_URL", "").strip(),
    reason="NEXOVA_TEST_DATABASE_URL no está definido; no se simula PostgreSQL.",
)
def test_writes_require_the_tinydb_user(inventory_client: TestClient, token: str) -> None:
    created = inventory_client.post(
        "/inventory/products",
        json={"name": "Docking station", "sku": "NXV-PER-010", "category": "peripherals", "office": "Miami"},
        headers=bearer(token),
    )
    assert created.status_code == 201, created.text
    body = created.json()
    assert body["current_stock"] == 0
    assert "hashed_password" not in body
    asset_id = body["id"]
    anonymous = inventory_client.post(
        "/inventory/products",
        json={"name": "Otro", "sku": "NXV-PER-011", "category": "peripherals", "office": "Miami"},
    )
    assert anonymous.status_code == 401
    rejected = inventory_client.post(
        "/inventory/products",
        json={
            "name": "Con stock",
            "sku": "NXV-PER-012",
            "category": "peripherals",
            "office": "Miami",
            "current_stock": 40,
        },
        headers=bearer(token),
    )
    assert rejected.status_code == 422
    me = inventory_client.get("/auth/me", headers=bearer(token)).json()
    inbound = inventory_client.post(
        "/inventory/orders/inbound",
        json={"asset_id": asset_id, "quantity": 4, "supplier": "Office Depot Miami", "office": "Miami"},
        headers=bearer(token),
    )
    assert inbound.status_code == 201, inbound.text
    assert inbound.json()["user_uuid"] == me["id"]
    assert inbound.json()["asset_sku"] == "NXV-PER-010"
    assert inbound.json()["user_uuid"] != SEED_USER_UUID
    spoofed = inventory_client.post(
        "/inventory/orders/inbound",
        json={
            "asset_id": asset_id,
            "quantity": 1,
            "supplier": "Office Depot Miami",
            "office": "Miami",
            "user_uuid": SEED_USER_UUID,
        },
        headers=bearer(token),
    )
    assert spoofed.status_code == 422
    again = inventory_client.get(f"/inventory/products/{asset_id}")
    assert again.json()["current_stock"] == 4
    missing = inventory_client.post(
        "/inventory/orders/outbound",
        json={
            "asset_id": asset_id,
            "quantity": 1,
            "exit_type": "allocation",
            "office": "Miami",
        },
        headers=bearer(token),
    )
    assert missing.status_code == 422
    consumed = inventory_client.post(
        "/inventory/orders/outbound",
        json={
            "asset_id": asset_id,
            "quantity": 1,
            "exit_type": "consumption",
            "assigned_to": "NXV-EMP-1",
            "office": "Miami",
        },
        headers=bearer(token),
    )
    assert consumed.status_code == 422
    outbound = inventory_client.post(
        "/inventory/orders/outbound",
        json={
            "asset_id": asset_id,
            "quantity": 1,
            "exit_type": "allocation",
            "assigned_to": "NXV-EMP-3300",
            "office": "Miami",
        },
        headers=bearer(token),
    )
    assert outbound.status_code == 201, outbound.text
    assert outbound.json()["user_uuid"] == me["id"]
    assert inventory_client.get(f"/inventory/products/{asset_id}").json()["current_stock"] == 3


@pytest.mark.skipif(
    not os.environ.get("NEXOVA_TEST_DATABASE_URL", "").strip(),
    reason="NEXOVA_TEST_DATABASE_URL no está definido; no se simula PostgreSQL.",
)
def test_outbound_over_stock_is_400_before_any_write(inventory_client: TestClient, token: str) -> None:
    laptop = next(row for row in inventory_client.get("/inventory/products").json() if row["sku"] == "NXV-IT-001")
    before = inventory_client.get("/inventory/orders").json()
    before_exits = [row for row in before if row["order_type"] == "outbound" and row["asset_id"] == laptop["id"]]
    denied = inventory_client.post(
        "/inventory/orders/outbound",
        json={
            "asset_id": laptop["id"],
            "quantity": 13,
            "exit_type": "allocation",
            "assigned_to": "NXV-EMP-1042",
            "office": "Valencia",
        },
        headers=bearer(token),
    )
    assert denied.status_code == 400
    expected = "Insufficient stock for asset 'Laptop 14\" Business'. Available: 12, requested: 13."
    assert denied.json()["detail"] == expected
    after = inventory_client.get("/inventory/orders").json()
    after_exits = [row for row in after if row["order_type"] == "outbound" and row["asset_id"] == laptop["id"]]
    assert len(after_exits) == len(before_exits)
    assert inventory_client.get(f"/inventory/products/{laptop['id']}").json()["current_stock"] == 12
    exact = inventory_client.post(
        "/inventory/orders/outbound",
        json={
            "asset_id": laptop["id"],
            "quantity": 12,
            "exit_type": "consumption",
            "office": "Valencia",
        },
        headers=bearer(token),
    )
    assert exact.status_code == 201, exact.text
    assert inventory_client.get(f"/inventory/products/{laptop['id']}").json()["current_stock"] == 0


@pytest.mark.skipif(
    not os.environ.get("NEXOVA_TEST_DATABASE_URL", "").strip(),
    reason="NEXOVA_TEST_DATABASE_URL no está definido; no se simula PostgreSQL.",
)
def test_orders_include_the_asset_and_the_seed_user(inventory_client: TestClient) -> None:
    response = inventory_client.get("/inventory/orders")
    assert response.status_code == 200
    rows = response.json()
    assert len(rows) == 9
    inbound = [row for row in rows if row["order_type"] == "inbound"]
    outbound = [row for row in rows if row["order_type"] == "outbound"]
    assert len(inbound) == 6
    assert len(outbound) == 3
    assert all(row["user_uuid"] == SEED_USER_UUID for row in rows)
    assert all(row["asset_sku"] and row["asset_name"] for row in rows)
    paper_exit = next(row for row in outbound if row["asset_sku"] == "NXV-OFF-001")
    assert paper_exit["exit_type"] == "consumption"
    assert paper_exit["assigned_to"] is None
    allocation = next(row for row in outbound if row["asset_sku"] == "NXV-IT-001")
    assert allocation["exit_type"] == "allocation"
    assert allocation["assigned_to"] == "NXV-EMP-1042"
    miami = inventory_client.get("/inventory/orders", params={"office": "Miami"})
    assert {row["asset_sku"] for row in miami.json()} == {"NXV-IT-002"}


@pytest.mark.skipif(
    not os.environ.get("NEXOVA_TEST_DATABASE_URL", "").strip(),
    reason="NEXOVA_TEST_DATABASE_URL no está definido; no se simula PostgreSQL.",
)
def test_postgres_enforces_the_foreign_key_and_has_no_user_table(inventory_client: TestClient) -> None:
    from app.inventory.database import get_engine

    engine = get_engine()
    assert engine.dialect.name == "postgresql"
    with engine.connect() as connection:
        version = connection.execute(text("SELECT version()")).scalar()
        assert version is not None
        assert "PostgreSQL" in version
        assert connection.execute(text("SELECT current_schema()")).scalar() != "public"
        columns = connection.execute(
            text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name = 'asset' AND table_schema = current_schema()"
            )
        ).scalars()
        assert "current_stock" not in set(columns)
        tables = connection.execute(
            text(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = current_schema() "
                "AND table_name IN ('user', 'users', 'profile', 'profiles')"
            )
        ).scalars()
        assert list(tables) == []
        constraint = connection.execute(
            text(
                "SELECT pg_get_constraintdef(oid) FROM pg_constraint "
                "WHERE contype = 'f' AND conrelid = 'assetexit'::regclass"
            )
        ).scalar()
        assert constraint is not None
        assert "REFERENCES asset" in constraint
    with Session(engine) as session:
        session.add(
            AssetEntry(
                asset_id=999999,
                quantity=1,
                supplier="Nadie",
                office="Valencia",
                user_uuid="00000000-0000-4000-8000-000000000099",
            )
        )
        with pytest.raises(IntegrityError):
            session.commit()
        session.rollback()
        session.add(
            AssetExit(
                asset_id=1,
                quantity=0,
                exit_type="consumption",
                office="Valencia",
                user_uuid=SEED_USER_UUID,
            )
        )
        with pytest.raises(IntegrityError):
            session.commit()


@pytest.mark.skipif(
    not os.environ.get("NEXOVA_TEST_DATABASE_URL", "").strip(),
    reason="NEXOVA_TEST_DATABASE_URL no está definido; no se simula PostgreSQL.",
)
def test_listing_orders_does_not_query_once_per_row(inventory_client: TestClient) -> None:
    from app.inventory.database import get_engine

    engine = get_engine()
    selects: list[str] = []

    def before(_conn, _cursor, statement, _parameters, _context, _executemany) -> None:
        sql = " ".join(statement.split())
        if sql.lower().startswith("select"):
            selects.append(sql)

    event.listen(engine, "before_cursor_execute", before)
    try:
        response = inventory_client.get("/inventory/orders")
    finally:
        event.remove(engine, "before_cursor_execute", before)
    assert response.status_code == 200
    assert len(response.json()) == 9
    assert len(selects) <= 6, selects


@pytest.mark.skipif(
    not os.environ.get("NEXOVA_TEST_DATABASE_URL", "").strip(),
    reason="NEXOVA_TEST_DATABASE_URL no está definido; no se simula PostgreSQL.",
)
def test_orders_cache_hits_until_a_successful_write(inventory_client: TestClient, token: str) -> None:
    products = inventory_client.get("/inventory/products")
    assert products.status_code == 200
    assert "x-nexova-cache" not in products.headers
    laptop = next(row for row in products.json() if row["sku"] == "NXV-IT-001")

    first = inventory_client.get("/inventory/orders")
    assert first.status_code == 200
    assert first.headers["x-nexova-cache"] == "MISS"
    assert len(first.json()) == 9
    second = inventory_client.get("/inventory/orders")
    assert second.headers["x-nexova-cache"] == "HIT"
    assert second.json() == first.json()

    miami = inventory_client.get("/inventory/orders?office=Miami")
    assert miami.headers["x-nexova-cache"] == "MISS"
    assert inventory_client.get("/inventory/orders?office=Miami").headers["x-nexova-cache"] == "HIT"
    assert inventory_client.get("/inventory/orders").headers["x-nexova-cache"] == "HIT"

    denied = inventory_client.post(
        "/inventory/orders/outbound",
        json={
            "asset_id": laptop["id"],
            "quantity": 10000,
            "exit_type": "consumption",
            "office": "Valencia",
        },
        headers=bearer(token),
    )
    assert denied.status_code == 400, denied.text
    assert inventory_client.get("/inventory/orders").headers["x-nexova-cache"] == "HIT"

    created = inventory_client.post(
        "/inventory/orders/inbound",
        json={
            "asset_id": laptop["id"],
            "quantity": 1,
            "supplier": "TechDistrib Valencia S.L.",
            "office": "Valencia",
        },
        headers=bearer(token),
    )
    assert created.status_code == 201, created.text
    fresh = inventory_client.get("/inventory/orders")
    assert fresh.headers["x-nexova-cache"] == "MISS"
    assert len(fresh.json()) == 10
    assert inventory_client.get("/inventory/orders?office=Miami").headers["x-nexova-cache"] == "MISS"


@pytest.mark.skipif(
    not os.environ.get("NEXOVA_TEST_DATABASE_URL", "").strip(),
    reason="NEXOVA_TEST_DATABASE_URL no está definido; no se simula PostgreSQL.",
)
def test_two_exits_cannot_oversell_the_same_asset(inventory_client: TestClient, token: str) -> None:
    from app.inventory.database import get_engine
    from app.inventory.service import create_exit

    created = inventory_client.post(
        "/inventory/products",
        json={"name": "Headset", "sku": "NXV-PER-090", "category": "peripherals", "office": "Valencia"},
        headers=bearer(token),
    )
    assert created.status_code == 201, created.text
    asset_id = created.json()["id"]
    inbound = inventory_client.post(
        "/inventory/orders/inbound",
        json={"asset_id": asset_id, "quantity": 5, "supplier": "TechDistrib Valencia S.L.", "office": "Valencia"},
        headers=bearer(token),
    )
    assert inbound.status_code == 201, inbound.text
    me = inventory_client.get("/auth/me", headers=bearer(token)).json()["id"]
    engine = get_engine()
    barrier = threading.Barrier(2)
    results: list[int] = []

    def worker() -> None:
        body = AssetExitCreate(
            asset_id=asset_id,
            quantity=4,
            exit_type="consumption",
            office="Valencia",
        )
        with Session(engine) as session:
            barrier.wait(timeout=5)
            try:
                create_exit(session, body, me)
                session.commit()
                results.append(201)
            except HTTPException as exc:
                session.rollback()
                results.append(exc.status_code)

    threads = [threading.Thread(target=worker), threading.Thread(target=worker)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=10)
    assert sorted(results) == [201, 400]
    assert inventory_client.get(f"/inventory/products/{asset_id}").json()["current_stock"] == 1


@pytest.mark.skipif(
    not os.environ.get("NEXOVA_TEST_DATABASE_URL", "").strip(),
    reason="NEXOVA_TEST_DATABASE_URL no está definido; no se simula PostgreSQL.",
)
def test_unit_cost_variance_uses_prior_rows_of_the_same_supplier(inventory_client: TestClient, token: str) -> None:
    products = inventory_client.get("/inventory/products").json()
    laptop = next(row for row in products if row["sku"] == "NXV-IT-001")
    first = inventory_client.post(
        "/inventory/orders/inbound",
        json={
            "asset_id": laptop["id"],
            "quantity": 1,
            "supplier": "TechDistrib Valencia S.L.",
            "office": "Valencia",
            "unit_cost_minor": 10000,
        },
        headers=bearer(token),
    )
    assert first.status_code == 201, first.text
    assert first.json()["unit_cost_minor"] == 10000
    assert first.json()["historical_unit_cost_minor"] is None
    assert first.json()["variance_ratio"] is None
    second = inventory_client.post(
        "/inventory/orders/inbound",
        json={
            "asset_id": laptop["id"],
            "quantity": 1,
            "supplier": "TechDistrib Valencia S.L.",
            "office": "Valencia",
            "unit_cost_minor": 13000,
        },
        headers=bearer(token),
    )
    assert second.status_code == 201, second.text
    assert second.json()["historical_unit_cost_minor"] == 10000
    assert second.json()["variance_ratio"] == 0.3
    quiet = inventory_client.post(
        "/inventory/orders/inbound",
        json={
            "asset_id": laptop["id"],
            "quantity": 1,
            "supplier": "Otro proveedor",
            "office": "Valencia",
            "unit_cost_minor": 50000,
        },
        headers=bearer(token),
    )
    assert quiet.status_code == 201, quiet.text
    assert quiet.json()["variance_ratio"] is None
