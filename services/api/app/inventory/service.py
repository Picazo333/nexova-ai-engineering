"""Inventory rules. Stock is the net of orders, computed in one query.

An outbound row is inserted only after the asset row is locked and the
available quantity is known to cover the request. The lock is the asset row,
so two exits of the same asset cannot both pass the check.
"""

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.inventory.models import Asset, AssetEntry, AssetExit
from app.inventory.schemas import (
    AssetCreate,
    AssetEntryCreate,
    AssetExitCreate,
    AssetRead,
    InventoryOrderRead,
)

OFFICES = {"Valencia", "Miami"}


def _office_filter(office: str | None) -> str | None:
    if office is None:
        return None
    if office not in OFFICES:
        raise HTTPException(status_code=422, detail="office tiene que ser Valencia o Miami.")
    return office


def stock_by_asset(session: Session, asset_id: int | None = None) -> dict[int, int]:
    """SUM(entries) − SUM(exits) for each asset. One statement, not one per row."""
    inbound = (
        select(AssetEntry.asset_id, func.sum(AssetEntry.quantity).label("qty"))
        .group_by(AssetEntry.asset_id)
        .subquery()
    )
    outbound = (
        select(AssetExit.asset_id, func.sum(AssetExit.quantity).label("qty"))
        .group_by(AssetExit.asset_id)
        .subquery()
    )
    statement = select(
        Asset.id,
        (func.coalesce(inbound.c.qty, 0) - func.coalesce(outbound.c.qty, 0)).label("current_stock"),
    ).outerjoin(inbound, inbound.c.asset_id == Asset.id).outerjoin(outbound, outbound.c.asset_id == Asset.id)
    if asset_id is not None:
        statement = statement.where(Asset.id == asset_id)
    found: dict[int, int] = {}
    for row in session.execute(statement).all():
        found[int(row[0])] = int(row[1])
    return found


def _read(asset: Asset, current_stock: int) -> AssetRead:
    assert asset.id is not None
    return AssetRead(
        id=asset.id,
        name=asset.name,
        sku=asset.sku,
        category=asset.category,
        office=asset.office,
        current_stock=current_stock,
    )


def list_assets(session: Session, office: str | None = None) -> list[AssetRead]:
    chosen = _office_filter(office)
    statement = select(Asset).order_by(Asset.id)
    if chosen is not None:
        statement = statement.where(Asset.office == chosen)
    assets = session.exec(statement).all()
    totals = stock_by_asset(session)
    return [_read(asset, totals.get(asset.id or 0, 0)) for asset in assets]


def get_asset(session: Session, asset_id: int) -> AssetRead:
    asset = session.get(Asset, asset_id)
    if asset is None:
        raise HTTPException(status_code=404, detail="No encontramos ese activo.")
    totals = stock_by_asset(session, asset_id)
    return _read(asset, totals.get(asset_id, 0))


def create_asset(session: Session, body: AssetCreate) -> AssetRead:
    name = body.name.strip()
    sku = body.sku.strip()
    if not name or not sku:
        raise HTTPException(status_code=422, detail="name y sku no pueden estar vacíos.")
    asset = Asset(name=name, sku=sku, category=body.category, office=body.office)
    session.add(asset)
    try:
        session.flush()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail="Ya existe un activo con ese sku.") from None
    assert asset.id is not None
    return _read(asset, 0)


def _lock_asset(session: Session, asset_id: int) -> Asset:
    asset = session.exec(select(Asset).where(Asset.id == asset_id).with_for_update()).first()
    if asset is None:
        raise HTTPException(status_code=404, detail="No encontramos ese activo.")
    return asset


def create_entry(session: Session, body: AssetEntryCreate, user_uuid: str) -> InventoryOrderRead:
    asset = _lock_asset(session, body.asset_id)
    entry = AssetEntry(
        asset_id=asset.id,
        quantity=body.quantity,
        supplier=body.supplier.strip(),
        office=body.office,
        user_uuid=user_uuid,
    )
    if not entry.supplier:
        raise HTTPException(status_code=422, detail="supplier no puede estar vacío.")
    session.add(entry)
    session.flush()
    assert entry.id is not None and asset.id is not None
    return InventoryOrderRead(
        id=entry.id,
        order_type="inbound",
        asset_id=asset.id,
        asset_name=asset.name,
        asset_sku=asset.sku,
        asset_category=asset.category,
        quantity=entry.quantity,
        office=entry.office,
        created_at=entry.created_at,
        user_uuid=entry.user_uuid,
        supplier=entry.supplier,
    )


def insufficient_stock_message(name: str, available: int, quantity: int) -> str:
    return f"Insufficient stock for asset '{name}'. Available: {available}, requested: {quantity}."


def create_exit(session: Session, body: AssetExitCreate, user_uuid: str) -> InventoryOrderRead:
    asset = _lock_asset(session, body.asset_id)
    assert asset.id is not None
    available = stock_by_asset(session, asset.id).get(asset.id, 0)
    if body.quantity > available:
        raise HTTPException(
            status_code=400,
            detail=insufficient_stock_message(asset.name, available, body.quantity),
        )
    row = AssetExit(
        asset_id=asset.id,
        quantity=body.quantity,
        exit_type=body.exit_type,
        assigned_to=body.assigned_to,
        office=body.office,
        user_uuid=user_uuid,
    )
    session.add(row)
    session.flush()
    assert row.id is not None
    return InventoryOrderRead(
        id=row.id,
        order_type="outbound",
        asset_id=asset.id,
        asset_name=asset.name,
        asset_sku=asset.sku,
        asset_category=asset.category,
        quantity=row.quantity,
        office=row.office,
        created_at=row.created_at,
        user_uuid=row.user_uuid,
        exit_type=row.exit_type,
        assigned_to=row.assigned_to,
    )


def list_orders(session: Session, office: str | None = None) -> list[InventoryOrderRead]:
    """Load orders and their assets with selectinload, not per-row queries."""
    chosen = _office_filter(office)
    entries_stmt = select(AssetEntry).options(selectinload(AssetEntry.asset)).order_by(AssetEntry.created_at, AssetEntry.id)
    exits_stmt = select(AssetExit).options(selectinload(AssetExit.asset)).order_by(AssetExit.created_at, AssetExit.id)
    if chosen is not None:
        entries_stmt = entries_stmt.where(AssetEntry.office == chosen)
        exits_stmt = exits_stmt.where(AssetExit.office == chosen)
    rows: list[InventoryOrderRead] = []
    for entry in session.exec(entries_stmt).all():
        asset = entry.asset
        assert entry.id is not None and asset is not None and asset.id is not None
        rows.append(
            InventoryOrderRead(
                id=entry.id,
                order_type="inbound",
                asset_id=asset.id,
                asset_name=asset.name,
                asset_sku=asset.sku,
                asset_category=asset.category,
                quantity=entry.quantity,
                office=entry.office,
                created_at=entry.created_at,
                user_uuid=entry.user_uuid,
                supplier=entry.supplier,
            )
        )
    for exit_row in session.exec(exits_stmt).all():
        asset = exit_row.asset
        assert exit_row.id is not None and asset is not None and asset.id is not None
        rows.append(
            InventoryOrderRead(
                id=exit_row.id,
                order_type="outbound",
                asset_id=asset.id,
                asset_name=asset.name,
                asset_sku=asset.sku,
                asset_category=asset.category,
                quantity=exit_row.quantity,
                office=exit_row.office,
                created_at=exit_row.created_at,
                user_uuid=exit_row.user_uuid,
                exit_type=exit_row.exit_type,
                assigned_to=exit_row.assigned_to,
            )
        )
    rows.sort(key=lambda item: (item.created_at, item.order_type, item.id))
    return rows
