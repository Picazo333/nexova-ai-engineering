#!/usr/bin/env python3
"""Validate event-schemas.json against the plan and the example events.

Exit 0 prints one PASS line per check. Exit 1 prints FAIL lines.
This script does not emit telemetry and does not import the API.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from jsonschema import Draft7Validator, FormatChecker

ROOT = Path(__file__).resolve().parent
SCHEMA_PATH = ROOT / "event-schemas.json"
PLAN_PATH = ROOT / "telemetry-plan.md"
VALID_DIR = ROOT / "examples" / "valid"
INVALID_DIR = ROOT / "examples" / "invalid"

ENVELOPE = [
    "eventId",
    "timestamp",
    "sessionId",
    "userId",
    "event_type",
    "schemaVersion",
    "requestId",
    "properties",
]
MANDATORY = {
    "inbound_order_created",
    "outbound_order_created",
    "stock_threshold_triggered",
    "direct_stock_edit_rejected",
    "kit_cost_variance_detected",
}
CATEGORIES = {"business", "authentication", "performance", "errors", "navigation"}
FLOOR = {"office", "product_id", "product_category", "programme_id", "quantity", "currency"}


def split_row(line: str) -> list[str]:
    cells: list[str] = []
    buf: list[str] = []
    escaped = False
    for char in line:
        if escaped:
            buf.append(char)
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if char == "|":
            cells.append("".join(buf).strip())
            buf = []
            continue
        buf.append(char)
    cells.append("".join(buf).strip())
    if cells and cells[0] == "":
        cells = cells[1:]
    if cells and cells[-1] == "":
        cells = cells[:-1]
    return cells


def parse_plan(text: str) -> dict[str, dict]:
    chunks = text.split("<!-- event:")
    found: dict[str, dict] = {}
    for chunk in chunks[1:]:
        header, _, body = chunk.partition("-->")
        parts = [piece.strip() for piece in header.split("|")]
        name = parts[0].strip()
        meta = {}
        for piece in parts[1:]:
            key, value = piece.split(":", 1)
            meta[key.strip()] = value.strip()
        required = _keys(body, "Obligatorias:")
        allow = _keys(body, "Allowlist:")
        table = _table(body)
        found[name] = {
            "origin": meta["origin"],
            "category": meta["category"],
            "delivery": meta["delivery"],
            "required": required,
            "allow": allow,
            "table": table,
            "sentence_ok": "porque necesitamos saber" in body and "decisión" in body,
        }
    return found


def _keys(body: str, label: str) -> list[str]:
    for line in body.splitlines():
        if line.startswith(label):
            return [piece.strip() for piece in line[len(label) :].split(",") if piece.strip()]
    raise KeyError(label)


def _table(body: str) -> dict[str, str]:
    lines = body.splitlines()
    start = None
    for index, line in enumerate(lines):
        if line.startswith("| Propiedad |"):
            start = index + 2
            break
    if start is None:
        return {}
    rows: dict[str, str] = {}
    for line in lines[start:]:
        if not line.startswith("|"):
            break
        cells = split_row(line)
        if len(cells) < 3:
            continue
        rows[cells[0].strip("`")] = cells[2]
    return rows


def main() -> int:
    failures: list[str] = []
    passes: list[str] = []

    def check(ok: bool, label: str) -> None:
        if ok:
            passes.append(label)
        else:
            failures.append(label)

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft7Validator.check_schema(schema)
    passes.append("el esquema draft-07 compila")
    validator = Draft7Validator(schema, format_checker=FormatChecker())

    check(schema.get("additionalProperties") is False, "el sobre rechaza claves de más")
    check(schema.get("required") == ENVELOPE, "el sobre exige los ocho campos del enunciado")
    definitions = schema["definitions"]
    enum = schema["properties"]["event_type"]["enum"]
    check(enum == list(definitions), "el enum de event_type coincide 1:1 con las definiciones")
    for name, definition in definitions.items():
        check(definition.get("additionalProperties") is False, f"{name} tiene allowlist cerrada")

    plan = parse_plan(PLAN_PATH.read_text(encoding="utf-8"))
    check(set(plan) == set(enum), "el plan y el esquema nombran los mismos eventos")

    for name in enum:
        definition = definitions[name]
        card = plan[name]
        meta = definition["x-nexova"]
        check(card["origin"] == meta["origin"], f"{name} origen {card['origin']}")
        check(card["category"] == meta["category"], f"{name} categoría {card['category']}")
        check(card["delivery"] == meta["delivery"], f"{name} entrega {card['delivery']}")
        check(set(card["required"]) == set(definition["required"]), f"{name} obligatorias")
        check(set(card["allow"]) == set(definition["properties"]), f"{name} allowlist")
        check(set(card["table"]) == set(definition["properties"]), f"{name} tabla de propiedades")
        for key, flag in card["table"].items():
            must = key in definition["required"]
            check((flag == "sí") == must, f"{name}.{key} marcado {flag}")
        check(card["sentence_ok"], f"{name} tiene hipótesis y decisión")
        if meta["origin"] == "mandatory":
            check(FLOOR <= set(definition["required"]), f"{name} lleva el piso del briefing")

    check(MANDATORY <= set(enum), "están las cinco métricas obligatorias")
    identified = [name for name in enum if definitions[name]["x-nexova"]["origin"] == "identified"]
    check(len(identified) >= 8, f"hay {len(identified)} eventos identificados")
    covered = {definitions[name]["x-nexova"]["category"] for name in identified}
    check(len(covered & CATEGORIES) >= 3, f"los identificados cubren {sorted(covered)}")

    valid_files = sorted(VALID_DIR.glob("*.json"))
    seen = set()
    valid_ok = True
    for path in valid_files:
        event = json.loads(path.read_text(encoding="utf-8"))
        errors = list(validator.iter_errors(event))
        if errors:
            valid_ok = False
            failures.append(f"{path.name} válido rechazado: {errors[0].message}")
        else:
            seen.add(event["event_type"])
    check(valid_ok and seen == set(enum), f"{len(valid_files)} ejemplos válidos cubren los {len(enum)} eventos")

    invalid_ok = True
    invalid_files = sorted(INVALID_DIR.glob("*.json"))
    for path in invalid_files:
        event = json.loads(path.read_text(encoding="utf-8"))
        if not list(validator.iter_errors(event)):
            invalid_ok = False
            failures.append(f"{path.name} inválido fue aceptado")
    check(invalid_ok and len(invalid_files) >= 6, f"{len(invalid_files)} ejemplos inválidos se rechazan")

    for line in passes:
        print("PASS", line)
    for line in failures:
        print("FAIL", line)
    print(f"summary pass={len(passes)} fail={len(failures)}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
