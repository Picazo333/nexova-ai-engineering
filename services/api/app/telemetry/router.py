"""POST /telemetry/events. Validates each event and stores the valid ones."""

from __future__ import annotations

import json
import logging
from typing import Any

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, ConfigDict

from app.config import telemetry_endpoint
from app.telemetry.schemas import TelemetryEvent
from app.telemetry.store import TelemetryStoreError, insert_events, timestamp_of
from app.telemetry.validate import EventRejected, parse_event

logger = logging.getLogger("nexova.telemetry")
if not logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(_handler)
    logger.setLevel(logging.INFO)

router = APIRouter(prefix="/telemetry", tags=["telemetry"])

MAX_BATCH = 500
_ENVELOPE_ERROR = "El lote no tiene el formato de telemetría."


class IngestResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    received: int
    stored: int
    rejected: int


def _reject(reasons: dict[str, int], reason: str) -> None:
    reasons[reason] = reasons.get(reason, 0) + 1


def _log(received: int, stored: int, rejected: int, accepted: list[TelemetryEvent], reasons: dict[str, int]) -> None:
    reason_text = ",".join(f"{key}:{reasons[key]}" for key in sorted(reasons))
    logger.info(
        "telemetry received=%s stored=%s rejected=%s event_types=%s rejected_reasons=%s endpoint_set=%s",
        received,
        stored,
        rejected,
        ",".join(event.event_type for event in accepted),
        reason_text,
        bool(telemetry_endpoint()),
    )


@router.post("/events", response_model=IngestResult)
async def receive_events(request: Request) -> IngestResult:
    # The list items stay raw. Typing them as TelemetryEvent would reject the
    # whole request with 422 when a single event is invalid.
    raw_body = await request.body()
    try:
        payload = json.loads(raw_body) if raw_body else None
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=422, detail=_ENVELOPE_ERROR) from exc
    if not isinstance(payload, dict) or set(payload) != {"events"} or not isinstance(payload["events"], list):
        raise HTTPException(status_code=422, detail=_ENVELOPE_ERROR)
    items: list[Any] = payload["events"]
    if len(items) > MAX_BATCH:
        raise HTTPException(status_code=422, detail="El lote supera 500 eventos.")

    accepted: list[TelemetryEvent] = []
    reasons: dict[str, int] = {}
    for item in items:
        try:
            event = parse_event(item)
            timestamp_of(event.timestamp)
        except EventRejected as exc:
            _reject(reasons, exc.reason)
            continue
        except ValueError:
            _reject(reasons, "timestamp")
            continue
        accepted.append(event)

    received = len(items)
    rejected = received - len(accepted)
    if not accepted:
        _log(received, 0, rejected, accepted, reasons)
        return IngestResult(received=received, stored=0, rejected=rejected)
    try:
        stored = insert_events(accepted)
    except TelemetryStoreError as exc:
        logger.error("telemetry store_failed received=%s rejected=%s", received, rejected)
        raise HTTPException(status_code=503, detail="La telemetría no tiene base de datos.") from exc
    _log(received, stored, rejected, accepted, reasons)
    return IngestResult(received=received, stored=stored, rejected=rejected)
