"""Optional volume for read measurements. Not loaded at startup.

The briefing seed stays the six assets in ``seed.py``. This module adds a
separate, varied set so a timing run can see joins and aggregations. It does
not replace those six rows and it does not run unless a script calls it.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy.engine import Engine
from sqlmodel import Session, select

from app.inventory.models import Asset, AssetEntry, AssetExit
from app.inventory.seed import SEED_USER_UUID

CATEGORIES = ("hardware", "peripherals", "office_supplies", "training_materials")
OFFICES = ("Valencia", "Miami")
SUPPLIERS = (
    "TechDistrib Valencia S.L.",
    "Office Depot Miami",
    "Papelería Ruzafa",
    "Atlantic Peripherals Inc.",
    "Formación Levante",
    "Miami Campus Supply",
)
EXIT_TYPES = ("allocation", "consumption")
NAMES = (
    "Laptop 14 pulgadas",
    "Monitor 24 pulgadas",
    "Dock USB-C",
    "Teclado compacto",
    "Ratón ergonómico",
    "Resma A4",
    "Cuaderno de formación",
    "Auriculares con cable",
)


def seed_volume(
    engine: Engine,
    *,
    assets: int = 480,
    entries_each: int = 12,
    exits_each: int = 4,
) -> dict[str, int]:
    """Insert varied assets and movements. Returns row counts after the insert.

    SKUs use the ``NXV-VOL-`` prefix so they never collide with the briefing
    seed. Quantities on exits stay below the entries of the same asset.
    """
    if assets < 1 or entries_each < 1 or exits_each < 0:
        raise ValueError("assets and entries_each have to be positive")
    start = datetime(2024, 1, 8, 9, 0, tzinfo=timezone.utc)
    with Session(engine) as session:
        already = session.exec(select(Asset.id).where(Asset.sku == "NXV-VOL-0001")).first()
        if already is None:
            created: list[Asset] = []
            for index in range(assets):
                category = CATEGORIES[index % len(CATEGORIES)]
                office = OFFICES[index % len(OFFICES)]
                label = NAMES[index % len(NAMES)]
                asset = Asset(
                    name=f"{label} lote {index + 1}",
                    sku=f"NXV-VOL-{index + 1:04d}",
                    category=category,
                    office=office,
                )
                session.add(asset)
                created.append(asset)
            session.flush()
            for index, asset in enumerate(created):
                assert asset.id is not None
                office = asset.office
                entered = 0
                for nth in range(entries_each):
                    quantity = 4 + ((index + nth * 3) % 17)
                    entered += quantity
                    session.add(
                        AssetEntry(
                            asset_id=asset.id,
                            quantity=quantity,
                            supplier=SUPPLIERS[(index + nth) % len(SUPPLIERS)],
                            office=office,
                            created_at=start + timedelta(days=index % 40, hours=nth),
                            user_uuid=SEED_USER_UUID,
                        )
                    )
                # Keep a positive remainder so later stock checks still pass.
                room = max(entered - exits_each, 1)
                for nth in range(exits_each):
                    quantity = 1 + ((index + nth) % max(room // exits_each, 1))
                    assigned = f"NXV-EMP-{(1000 + (index + nth) % 800):04d}" if nth % 2 == 0 else None
                    session.add(
                        AssetExit(
                            asset_id=asset.id,
                            quantity=quantity,
                            exit_type=EXIT_TYPES[nth % len(EXIT_TYPES)],
                            assigned_to=assigned,
                            office=office,
                            created_at=start + timedelta(days=50 + (index % 20), hours=nth),
                            user_uuid=SEED_USER_UUID,
                        )
                    )
            session.commit()
        asset_count = len(session.exec(select(Asset.id)).all())
        entry_count = len(session.exec(select(AssetEntry.id)).all())
        exit_count = len(session.exec(select(AssetExit.id)).all())
    return {"assets": asset_count, "entries": entry_count, "exits": exit_count}
