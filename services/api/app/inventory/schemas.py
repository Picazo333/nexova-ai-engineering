"""Pydantic request and response models for inventory.

These classes are not SQLModel tables. `current_stock` exists only on the
asset response. A client cannot send it, and a client cannot choose
`user_uuid`: the route writes the id from the TinyDB user.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

Category = Literal["hardware", "peripherals", "office_supplies", "training_materials"]
Office = Literal["Valencia", "Miami"]
ExitType = Literal["allocation", "consumption"]


class AssetCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=200)
    sku: str = Field(min_length=1, max_length=64)
    category: Category
    office: Office


class AssetRead(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: int
    name: str
    sku: str
    category: str
    office: str
    current_stock: int


class AssetEntryCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    asset_id: int
    quantity: int = Field(gt=0)
    supplier: str = Field(min_length=1, max_length=200)
    office: Office
    unit_cost_minor: int | None = Field(default=None, ge=0, le=100_000_000_000)


class AssetExitCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    asset_id: int
    quantity: int = Field(gt=0)
    exit_type: ExitType
    assigned_to: str | None = None
    office: Office

    @model_validator(mode="after")
    def assigned_to_follows_exit_type(self) -> "AssetExitCreate":
        if self.exit_type == "allocation":
            if self.assigned_to is None or not self.assigned_to.strip():
                raise ValueError("assigned_to es obligatorio cuando exit_type es allocation.")
            self.assigned_to = self.assigned_to.strip()
        elif self.assigned_to is not None:
            raise ValueError("assigned_to tiene que ser nulo cuando exit_type es consumption.")
        return self


class InventoryOrderRead(BaseModel):
    """One inbound or outbound row, with the asset loaded in the same query."""

    model_config = ConfigDict(extra="forbid")

    id: int
    order_type: Literal["inbound", "outbound"]
    asset_id: int
    asset_name: str
    asset_sku: str
    asset_category: str
    quantity: int
    office: str
    created_at: datetime
    user_uuid: str
    supplier: str | None = None
    exit_type: str | None = None
    assigned_to: str | None = None
    unit_cost_minor: int | None = None
    historical_unit_cost_minor: int | None = None
    variance_ratio: float | None = None
