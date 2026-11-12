"""SQLModel tables for Nexova equipment inventory.

Names and columns follow the backend briefing: Asset, AssetEntry, AssetExit.
`current_stock` is not a column. `user_uuid` points at a TinyDB user and has
no foreign key and no user table here.
"""

from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, DateTime
from sqlmodel import Field, Relationship, SQLModel


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Asset(SQLModel, table=True):
    __tablename__ = "asset"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=200)
    sku: str = Field(max_length=64, unique=True, index=True)
    category: str = Field(max_length=32)
    office: str = Field(max_length=32, index=True)
    entries: list["AssetEntry"] = Relationship(back_populates="asset")
    exits: list["AssetExit"] = Relationship(back_populates="asset")


class AssetEntry(SQLModel, table=True):
    __tablename__ = "assetentry"
    __table_args__ = (CheckConstraint("quantity > 0", name="ck_assetentry_quantity_positive"),)

    id: int | None = Field(default=None, primary_key=True)
    asset_id: int = Field(foreign_key="asset.id", index=True)
    quantity: int
    supplier: str = Field(max_length=200)
    office: str = Field(max_length=32)
    unit_cost_minor: int | None = Field(default=None)
    created_at: datetime = Field(
        default_factory=_utcnow,
        sa_type=DateTime(timezone=True),
    )
    user_uuid: str = Field(max_length=64, index=True)
    asset: Asset | None = Relationship(back_populates="entries")


class AssetExit(SQLModel, table=True):
    __tablename__ = "assetexit"
    __table_args__ = (CheckConstraint("quantity > 0", name="ck_assetexit_quantity_positive"),)

    id: int | None = Field(default=None, primary_key=True)
    asset_id: int = Field(foreign_key="asset.id", index=True)
    quantity: int
    exit_type: str = Field(max_length=32)
    assigned_to: str | None = Field(default=None, max_length=200)
    office: str = Field(max_length=32)
    created_at: datetime = Field(
        default_factory=_utcnow,
        sa_type=DateTime(timezone=True),
    )
    user_uuid: str = Field(max_length=64, index=True)
    asset: Asset | None = Relationship(back_populates="exits")
