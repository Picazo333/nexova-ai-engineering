"""Per-event checks. The schema file is docs/telemetry/event-schemas.json.

The `$id` inside that document is a URI. This module does not turn that URI
into a filesystem path.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from jsonschema import Draft7Validator, FormatChecker
from pydantic import ValidationError

from app.telemetry.schemas import TelemetryEvent

_FILENAME = "event-schemas.json"


class EventRejected(Exception):
    """One event failed. The rest of the batch continues."""

    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(reason)


def schema_path() -> Path:
    """Find the catalogue by directory, walking up from this file."""
    for parent in Path(__file__).resolve().parents:
        candidate = parent / "docs" / "telemetry" / _FILENAME
        if candidate.is_file():
            return candidate
    raise FileNotFoundError("docs/telemetry/event-schemas.json")


@lru_cache(maxsize=1)
def event_validator() -> Draft7Validator:
    document = json.loads(schema_path().read_text(encoding="utf-8"))
    Draft7Validator.check_schema(document)
    return Draft7Validator(document, format_checker=FormatChecker())


def parse_event(raw: Any) -> TelemetryEvent:
    """Validate one raw item. TelemetryEvent is the envelope contract, unchanged."""
    if not isinstance(raw, dict):
        raise EventRejected("not_object")
    try:
        event = TelemetryEvent.model_validate(raw)
    except ValidationError as exc:
        raise EventRejected("envelope") from exc
    if next(event_validator().iter_errors(raw), None) is not None:
        raise EventRejected("schema")
    return event
