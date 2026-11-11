"""Load the briefing suppliers into TinyDB without duplicating names.

Run from services/api:

    uv run seed
"""

from __future__ import annotations

from pydantic import ValidationError

from directory import insert_missing
from models import SupplierCreate
from seed_data import SUPPLIERS_SEED


def validated_seed(records: list[dict] | None = None) -> list[SupplierCreate]:
    """Validate every record before any write. A bad record aborts the batch."""
    raw_records = SUPPLIERS_SEED if records is None else records
    return [SupplierCreate.model_validate(item) for item in raw_records]


def seed_suppliers(records: list[dict] | None = None) -> tuple[int, int]:
    models = validated_seed(records)
    return insert_missing(models)


def main() -> None:
    try:
        inserted, skipped = seed_suppliers()
    except ValidationError as exc:
        print("No se insertó ningún registro. Los datos no pasaron la validación.")
        raise SystemExit(1) from exc
    print(f"Se insertaron {inserted} registros.")
    print(f"Se omitieron {skipped} registros ya presentes.")


if __name__ == "__main__":
    main()
