"""One INSERT for the valid events of a batch. The table is append-only."""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from sqlalchemy import text
from sqlalchemy.engine import Connection, Engine

from app.telemetry.schemas import TelemetryEvent

logger = logging.getLogger("nexova.telemetry")

SQL_PATH = Path(__file__).resolve().parent / "sql" / "001_telemetry_events.sql"
_APPLIED: set[tuple[str, str]] = set()

ERROR_TYPES = frozenset({"frontend_exception_recorded", "api_response_failed"})
WARN_TYPES = frozenset(
    {
        "login_failed",
        "credential_rejected",
        "session_expired",
        "stock_threshold_triggered",
        "direct_stock_edit_rejected",
        "kit_cost_variance_detected",
        "order_validation_failed",
        "catalogue_gap_recorded",
        "api_latency_recorded",
    }
)
VALUE_PROPERTY = {
    "web_vital_recorded": "value",
    "api_latency_recorded": "duration_ms",
    "page_load_recorded": "duration_ms",
    "api_response_failed": "duration_ms",
    "kit_cost_variance_detected": "variance_ratio",
    "stock_threshold_triggered": "current_stock",
    "inbound_order_created": "quantity",
    "outbound_order_created": "quantity",
    "order_validation_failed": "quantity",
    "login_succeeded": "expires_in_seconds",
}
_ENVELOPE = ("eventId", "sessionId", "userId", "schemaVersion", "requestId")
_SERVICES = frozenset({"api", "backoffice", "portal"})


class TelemetryStoreError(RuntimeError):
    """The batch could not be written. Nothing from it was committed."""


def reset_telemetry_cache() -> None:
    _APPLIED.clear()


def _statements(script: str) -> list[str]:
    """Split a SQL script. Semicolons inside quotes stay in the statement."""
    parts: list[str] = []
    buf: list[str] = []
    dollar = False
    single = False
    index = 0
    while index < len(script):
        if not single and script.startswith("$$", index):
            dollar = not dollar
            buf.append("$$")
            index += 2
            continue
        char = script[index]
        if char == "'" and not dollar:
            if single and script.startswith("''", index):
                buf.append("''")
                index += 2
                continue
            single = not single
            buf.append(char)
            index += 1
            continue
        if char == ";" and not dollar and not single:
            statement = "".join(buf).strip()
            if statement:
                parts.append(statement)
            buf = []
            index += 1
            continue
        buf.append(char)
        index += 1
    tail = "".join(buf).strip()
    if tail:
        parts.append(tail)
    return parts


def ensure_telemetry_table(engine: Engine) -> None:
    from app.inventory.database import inventory_schema

    key = (str(engine.url), inventory_schema())
    if key in _APPLIED:
        return
    script = SQL_PATH.read_text(encoding="utf-8")
    with engine.begin() as connection:
        for statement in _statements(script):
            connection.exec_driver_sql(statement)
    _APPLIED.add(key)


def timestamp_of(value: str) -> datetime:
    text_value = value[:-1] + "+00:00" if value.endswith("Z") else value
    parsed = datetime.fromisoformat(text_value)
    if parsed.tzinfo is None:
        raise ValueError("timestamp sin zona")
    return parsed


def service_of(event: TelemetryEvent) -> str:
    app = event.properties.get("app")
    if isinstance(app, str) and app in _SERVICES:
        return app
    surface = event.properties.get("surface")
    if isinstance(surface, str) and surface in _SERVICES:
        return surface
    return "backoffice"


def level_of(event: TelemetryEvent) -> str:
    if event.event_type == "web_vital_recorded" and event.properties.get("rating") == "poor":
        return "warn"
    if event.event_type in ERROR_TYPES:
        return "error"
    if event.event_type in WARN_TYPES:
        return "warn"
    return "info"


def value_of(event: TelemetryEvent) -> int | float | None:
    key = VALUE_PROPERTY.get(event.event_type)
    if key is None:
        return None
    raw = event.properties.get(key)
    if isinstance(raw, bool) or not isinstance(raw, (int, float)):
        return None
    return raw


def message_of(event: TelemetryEvent) -> str:
    props = event.properties
    kind = event.event_type
    if kind == "inbound_order_created":
        text_value = f"entrada {props['quantity']} {props['product_sku']} {props['office']}"
    elif kind == "outbound_order_created":
        text_value = f"salida {props['quantity']} {props['product_sku']} {props['office']}"
    elif kind == "login_failed":
        text_value = "login rechazado"
    elif kind == "credential_rejected":
        text_value = f"credencial rechazada {props.get('failure_code', '')}".strip()
    elif kind == "frontend_exception_recorded":
        text_value = f"{props.get('error_name', 'error')} {props.get('path_template', '')}".strip()
    elif kind == "web_vital_recorded":
        text_value = f"{props.get('metric_name', '')} {props.get('rating', '')} {props.get('path_template', '')}".strip()
    elif kind == "api_latency_recorded":
        text_value = f"{props.get('http_method', '')} {props.get('route_template', '')} {props.get('status_code', '')}".strip()
    elif kind == "stock_threshold_triggered":
        text_value = f"stock {props.get('product_sku', '')} {props.get('current_stock', '')}".strip()
    elif kind == "kit_cost_variance_detected":
        text_value = f"desviación {props.get('product_sku', '')} {props.get('variance_ratio', '')}".strip()
    else:
        text_value = kind
    return text_value[:240]


def tags_of(event: TelemetryEvent) -> dict[str, Any]:
    """Allowlisted properties plus the five envelope fields the plan analyses."""
    tags: dict[str, Any] = {
        "eventId": event.eventId,
        "sessionId": event.sessionId,
        "userId": event.userId,
        "schemaVersion": event.schemaVersion,
        "requestId": event.requestId,
    }
    for key, value in event.properties.items():
        if key in _ENVELOPE:
            raise TelemetryStoreError("tag")
        tags[key] = value
    return tags


def row_of(event: TelemetryEvent) -> dict[str, Any]:
    return {
        "timestamp": timestamp_of(event.timestamp),
        "service": service_of(event),
        "event_type": event.event_type,
        "level": level_of(event),
        "value": value_of(event),
        "message": message_of(event),
        "tags": tags_of(event),
    }


def insert_events(events: list[TelemetryEvent]) -> int:
    """Insert every row in one statement and one transaction."""
    if not events:
        return 0
    from app.inventory.database import InventoryDatabaseError, get_engine

    try:
        engine = get_engine()
        ensure_telemetry_table(engine)
    except InventoryDatabaseError as exc:
        raise TelemetryStoreError("database") from exc
    rows = [row_of(event) for event in events]
    columns = ("timestamp", "service", "event_type", "level", "value", "message", "tags")
    values_sql: list[str] = []
    params: dict[str, Any] = {}
    for index, row in enumerate(rows):
        slots: list[str] = []
        for column in columns:
            name = f"{column}_{index}"
            if column == "tags":
                slots.append(f"CAST(:{name} AS jsonb)")
                params[name] = json.dumps(row[column], ensure_ascii=False, separators=(",", ":"))
            else:
                slots.append(f":{name}")
                params[name] = row[column]
        values_sql.append("(" + ", ".join(slots) + ")")
    statement = (
        "INSERT INTO telemetry_events (timestamp, service, event_type, level, value, message, tags) VALUES "
        + ", ".join(values_sql)
        + " RETURNING id"
    )
    try:
        with engine.begin() as connection:
            stored = _insert(connection, statement, params, len(rows))
    except TelemetryStoreError:
        raise
    except Exception as exc:
        logger.error("telemetry insert failed %s", type(exc).__name__)
        raise TelemetryStoreError(type(exc).__name__) from exc
    return stored


def _insert(connection: Connection, statement: str, params: dict[str, Any], expected: int) -> int:
    result = connection.execute(text(statement), params)
    ids = result.scalars().all()
    if len(ids) != expected:
        raise TelemetryStoreError("rowcount")
    return len(ids)
