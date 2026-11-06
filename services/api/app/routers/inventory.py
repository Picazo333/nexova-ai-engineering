"""Inventory routes. Writes require the TinyDB user behind the bearer token."""

import json
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlmodel import Session

from app.auth.deps import get_current_user
from app.cache import ORDERS_LIST, ORDERS_LIST_TTL_SECONDS, fetch_cached, schedule_invalidation
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
    created = create_entry(session, body, str(user["id"]))
    schedule_invalidation(ORDERS_LIST)
    return created


@router.post("/orders/outbound", response_model=InventoryOrderRead, status_code=201)
def add_outbound(
    body: AssetExitCreate,
    session: Annotated[Session, Depends(get_db)],
    user: Annotated[dict, Depends(get_current_user)],
) -> InventoryOrderRead:
    created = create_exit(session, body, str(user["id"]))
    schedule_invalidation(ORDERS_LIST)
    return created


def _orders_body(rows: list[InventoryOrderRead]) -> bytes:
    # The hit returns these bytes. Building the models is the expensive part;
    # encoding them again on every hit would spend most of the saved time.
    payload = [row.model_dump(mode="json") for row in rows]
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


@router.get("/orders", response_model=list[InventoryOrderRead])
def read_orders(
    session: Annotated[Session, Depends(get_db)],
    office: Annotated[str | None, Query()] = None,
) -> Response:
    # The history is the same document for every reader. user_uuid is who
    # recorded the movement, not who is looking. A per-user key would copy
    # the same rows without hiding anything private.
    body = fetch_cached(
        ORDERS_LIST,
        {"office": office or ""},
        ORDERS_LIST_TTL_SECONDS,
        lambda: _orders_body(list_orders(session, office)),
        private=False,
        user_id=None,
    )
    return Response(content=body, media_type="application/json")
