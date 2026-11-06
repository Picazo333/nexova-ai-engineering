"""Inventory routes. Writes require the TinyDB user behind the bearer token."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.auth.deps import get_current_user
from app.inventory.database import get_db
from app.inventory.schemas import AssetCreate, AssetEntryCreate, AssetExitCreate, AssetRead, InventoryOrderRead
from app.inventory.service import create_asset, create_entry, create_exit, get_asset, list_assets, list_orders

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.get("/products", response_model=list[AssetRead])
def read_products(
    session: Annotated[Session, Depends(get_db)],
    office: Annotated[str | None, Query()] = None,
) -> list[AssetRead]:
    return list_assets(session, office)


@router.post("/products", response_model=AssetRead, status_code=201)
def add_product(
    body: AssetCreate,
    session: Annotated[Session, Depends(get_db)],
    user: Annotated[dict, Depends(get_current_user)],
) -> AssetRead:
    del user
    return create_asset(session, body)


@router.get("/products/{asset_id}", response_model=AssetRead)
def read_product(
    asset_id: int,
    session: Annotated[Session, Depends(get_db)],
) -> AssetRead:
    return get_asset(session, asset_id)


@router.post("/orders/inbound", response_model=InventoryOrderRead, status_code=201)
def add_inbound(
    body: AssetEntryCreate,
    session: Annotated[Session, Depends(get_db)],
    user: Annotated[dict, Depends(get_current_user)],
) -> InventoryOrderRead:
    return create_entry(session, body, str(user["id"]))


@router.post("/orders/outbound", response_model=InventoryOrderRead, status_code=201)
def add_outbound(
    body: AssetExitCreate,
    session: Annotated[Session, Depends(get_db)],
    user: Annotated[dict, Depends(get_current_user)],
) -> InventoryOrderRead:
    return create_exit(session, body, str(user["id"]))


@router.get("/orders", response_model=list[InventoryOrderRead])
def read_orders(
    session: Annotated[Session, Depends(get_db)],
    office: Annotated[str | None, Query()] = None,
) -> list[InventoryOrderRead]:
    return list_orders(session, office)
