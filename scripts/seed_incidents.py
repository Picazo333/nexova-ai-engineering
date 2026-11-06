#!/usr/bin/env python3
"""Load historical Nexova support tickets into the incident manager.

The CSV is the incidents-file-analyzer file. Invalid rows are not inserted.
Running the script again does not duplicate a ticket_id already stored.
Emails and descriptions are not printed.

From the repository root, with the API virtualenv:

    services/api/.venv/bin/python scripts/seed_incidents.py

Optional path and data directory:

    INCIDENTS_DATA_DIR=services/api/.data \\
      services/api/.venv/bin/python scripts/seed_incidents.py scripts/incidents-nexova.csv
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for entry in (ROOT / "services" / "api", ROOT / "packages", ROOT / "packages" / "shared"):
    text = str(entry)
    if text not in sys.path:
        sys.path.insert(0, text)

from nexova_incidents.csv_rules import AnalysisError  # noqa: E402
from nexova_incidents.transform import SeedPlan, prepare_csv  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Carga el CSV histórico de incidencias de Nexova.")
    parser.add_argument(
        "csv_path",
        nargs="?",
        default=str(ROOT / "scripts" / "incidents-nexova.csv"),
        help="CSV del analizador (por defecto scripts/incidents-nexova.csv)",
    )
    args = parser.parse_args(argv)
    path = Path(args.csv_path)
    if not path.is_file():
        print(f"error: no está el fichero {path.name}", file=sys.stderr)
        return 1
    try:
        raw = path.read_bytes()
    except OSError:
        print("error: no se pudo leer el fichero.", file=sys.stderr)
        return 1
    try:
        plan = prepare_csv(raw)
    except AnalysisError as exc:
        print(f"error: {exc.message_es}", file=sys.stderr)
        return 1

    try:
        from incident_store import insert_new
    except ImportError:
        print("error: no está disponible el almacén de incidencias.", file=sys.stderr)
        return 1

    inserted = 0
    skipped = 0
    for row in plan.accepted:
        try:
            stored = insert_new(_record(row))
        except OSError:
            print("error: no se pudo guardar la incidencia.", file=sys.stderr)
            return 1
        if stored is None:
            skipped += 1
        else:
            inserted += 1
    sys.stdout.write(render_report(path.name, inserted, skipped, plan))
    return 0


def _record(row) -> dict:
    return {
        "title": row.title,
        "description": row.description,
        "category": row.category,
        "status": row.status,
        "origin": row.origin,
        "branch": row.branch,
        "created_at": row.created_at,
        "updated_at": row.updated_at,
        "source_key": row.source_key,
    }


def render_report(source_name: str, inserted: int, skipped: int, plan: SeedPlan) -> str:
    lines = [
        "NEXOVA — CARGA DE INCIDENCIAS HISTÓRICAS",
        f"Fichero: {source_name}",
        f"Insertadas: {inserted}",
        f"Ya estaban: {skipped}",
        f"Rechazadas: {len(plan.rejected)}",
        "",
    ]
    if plan.rejected:
        lines.append("Registros no insertados:")
        for item in plan.rejected:
            ticket = item.ticket_id or "sin ticket"
            reasons = "; ".join(item.messages)
            lines.append(f"  línea {item.line_number}  {ticket}  {reasons}")
        lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
