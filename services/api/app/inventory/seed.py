"""Minimum inventory rows from the Nexova backend briefing.

Product names, SKUs, categories and offices are the English briefing values.
The Spanish briefing translates the same six assets. Supplier names are the
examples given there. `assigned_to` is an employee id, not a person's name.
`SEED_USER_UUID` marks rows loaded at startup. It is not a login. Orders
created through the API store the TinyDB id of the authenticated user.
"""

from datetime import datetime, timezone

from sqlalchemy.engine import Engine
from sqlmodel import Session, select

from app.inventory.models import Asset, AssetEntry, AssetExit

SEED_USER_UUID = "00000000-0000-4000-8000-000000000201"

# Net stock after these rows:
# NXV-IT-001 = 10 + 5 - 3 = 12
# NXV-IT-002 = 8 - 2 = 6
# NXV-PER-001 = 20
# NXV-PER-002 = 0
# NXV-OFF-001 = 30 - 12 = 18
# NXV-TRN-001 = 15
ASSETS: tuple[dict[str, str], ...] = (
    {"name": 'Laptop 14" Business', "sku": "NXV-IT-001", "category": "hardware", "office": "Valencia"},
    {"name": 'Laptop 14" Business', "sku": "NXV-IT-002", "category": "hardware", "office": "Miami"},
    {"name": "Ergonomic mouse", "sku": "NXV-PER-001", "category": "peripherals", "office": "Valencia"},
    {"name": "USB-C Hub", "sku": "NXV-PER-002", "category": "peripherals", "office": "Miami"},
    {"name": "A4 paper ream", "sku": "NXV-OFF-001", "category": "office_supplies", "office": "Valencia"},
    {
        "name": "Leadership training workbook",
        "sku": "NXV-TRN-001",
        "category": "training_materials",
        "office": "Valencia",
    },
)

# (sku, quantity, supplier, office, minute offset)
ENTRIES: tuple[tuple[str, int, str, str, int], ...] = (
    ("NXV-IT-001", 10, "TechDistrib Valencia S.L.", "Valencia", 0),
    ("NXV-IT-001", 5, "TechDistrib Valencia S.L.", "Valencia", 1),
    ("NXV-IT-002", 8, "Office Depot Miami", "Miami", 2),
    ("NXV-PER-001", 20, "TechDistrib Valencia S.L.", "Valencia", 3),
    ("NXV-OFF-001", 30, "TechDistrib Valencia S.L.", "Valencia", 4),
    ("NXV-TRN-001", 15, "TechDistrib Valencia S.L.", "Valencia", 5),
)

# (sku, quantity, exit_type, assigned_to, office, minute offset)
EXITS: tuple[tuple[str, int, str, str | None, str, int], ...] = (
    ("NXV-IT-001", 3, "allocation", "NXV-EMP-1042", "Valencia", 6),
    ("NXV-IT-002", 2, "allocation", "NXV-EMP-2201", "Miami", 7),
    ("NXV-OFF-001", 12, "consumption", None, "Valencia", 8),
)

EXPECTED_STOCK: dict[str, int] = {
    "NXV-IT-001": 12,
    "NXV-IT-002": 6,
    "NXV-PER-001": 20,
    "NXV-PER-002": 0,
    "NXV-OFF-001": 18,
    "NXV-TRN-001": 15,
}


def _stamp(minute: int) -> datetime:
    return datetime(2026, 3, 2, 9, minute, tzinfo=timezone.utc)


def seed_if_empty(engine: Engine) -> int:
    """Insert the briefing rows once. Returns how many assets were inserted."""
    with Session(engine) as session:
        if session.exec(select(Asset.id)).first() is not None:
            return 0
        by_sku: dict[str, Asset] = {}
        for row in ASSETS:
            asset = Asset(**row)
            session.add(asset)
            by_sku[row["sku"]] = asset
        session.flush()
        for sku, quantity, supplier, office, minute in ENTRIES:
            session.add(
                AssetEntry(
                    asset_id=by_sku[sku].id,
                    quantity=quantity,
                    supplier=supplier,
                    office=office,
                    created_at=_stamp(minute),
                    user_uuid=SEED_USER_UUID,
                )
            )
        for sku, quantity, exit_type, assigned_to, office, minute in EXITS:
            session.add(
                AssetExit(
                    asset_id=by_sku[sku].id,
                    quantity=quantity,
                    exit_type=exit_type,
                    assigned_to=assigned_to,
                    office=office,
                    created_at=_stamp(minute),
                    user_uuid=SEED_USER_UUID,
                )
            )
        session.commit()
        return len(ASSETS)
