"""POST /telemetry/events. Validates the envelope, logs the types, stores nothing."""

from __future__ import annotations

import json
import logging

from fastapi import APIRouter, HTTPException, Request
from pydantic import ValidationError

from app.config import telemetry_endpoint
from app.telemetry.schemas import TelemetryBatch

logger = logging.getLogger("nexova.telemetry")
if not logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(_handler)
    logger.setLevel(logging.INFO)
router = APIRouter(prefix="/telemetry", tags=["telemetry"])


@router.post("/events")
async def receive_events(request: Request) -> dict[str, int]:
    # The frontend flush uses JSON. sendBeacon uses text/plain so the browser
    # can send it without a preflight while the tab is closing. Both bodies
    # are the same document.
    raw = await request.body()
    try:
        payload = json.loads(raw) if raw else None
        batch = TelemetryBatch.model_validate(payload)
    except (json.JSONDecodeError, ValidationError, TypeError) as exc:
        raise HTTPException(status_code=422, detail="El lote no tiene el formato de telemetría.") from exc
    configured = telemetry_endpoint()
    types = [event.event_type for event in batch.events]
    logger.info(
        "telemetry received=%s event_types=%s endpoint_set=%s",
        len(batch.events),
        ",".join(types),
        bool(configured),
    )
    return {"received": len(batch.events)}
