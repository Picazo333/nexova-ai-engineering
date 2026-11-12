"""JSON API for the centralized incident manager."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

_SHARED = Path(__file__).resolve().parents[4] / "packages" / "shared"
if str(_SHARED) not in sys.path:
    sys.path.insert(0, str(_SHARED))

from app.auth.deps import get_current_user  # noqa: E402
from incident_store import (  # noqa: E402
    create_incident,
    get_incident,
    list_incidents,
    summary,
    update_status,
)
from nexova_incidents.model import validate_create, validate_filters, validate_transition  # noqa: E402

router = APIRouter(
    prefix="/api/incidents",
    tags=["incident-manager"],
    dependencies=[Depends(get_current_user)],
)


def _validation(errors: list[dict[str, str]]) -> JSONResponse:
    first = errors[0]
    return JSONResponse(
        status_code=400,
        content={
            "error": "validation_error",
            "field": first["field"],
            "message": first["message"],
            "errors": errors,
        },
    )


async def _object(request: Request) -> tuple[object | None, JSONResponse | None]:
    raw = await request.body()
    if not raw:
        return None, _validation([{"field": "body", "message": "El cuerpo tiene que ser un objeto JSON."}])
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return None, _validation([{"field": "body", "message": "El cuerpo tiene que ser un objeto JSON."}])
    if not isinstance(payload, dict):
        return None, _validation([{"field": "body", "message": "El cuerpo tiene que ser un objeto JSON."}])
    return payload, None


@router.get("/summary")
def incident_summary() -> JSONResponse:
    return JSONResponse(summary())


@router.get("")
def incident_list(request: Request) -> JSONResponse:
    params = {
        "status": request.query_params.get("status"),
        "origin": request.query_params.get("origin"),
        "branch": request.query_params.get("branch"),
        "category": request.query_params.get("category"),
    }
    errors = validate_filters(params)
    if errors:
        return _validation(errors)
    rows = list_incidents(
        status=params["status"] or None,
        origin=params["origin"] or None,
        branch=params["branch"] or None,
        category=params["category"] or None,
    )
    return JSONResponse(rows)


@router.post("")
async def incident_create(request: Request) -> JSONResponse:
    payload, problem = await _object(request)
    if problem is not None:
        return problem
    errors = validate_create(payload)
    if errors:
        return _validation(errors)
    assert isinstance(payload, dict)
    created = create_incident(payload)
    return JSONResponse(status_code=201, content=created)


@router.get("/{incident_id}")
def incident_detail(incident_id: str) -> JSONResponse:
    found = get_incident(incident_id)
    if found is None:
        return JSONResponse(
            status_code=404,
            content={"error": "not_found", "message": "No encontramos esa incidencia."},
        )
    return JSONResponse(found)


@router.patch("/{incident_id}/status")
async def incident_status(incident_id: str, request: Request) -> JSONResponse:
    current = get_incident(incident_id)
    if current is None:
        return JSONResponse(
            status_code=404,
            content={"error": "not_found", "message": "No encontramos esa incidencia."},
        )
    payload, problem = await _object(request)
    if problem is not None:
        return problem
    assert isinstance(payload, dict)
    extra = [key for key in payload if key != "status"]
    if extra:
        return _validation(
            [{"field": extra[0], "message": "Esta operación solo cambia el estado."}]
        )
    if "status" not in payload:
        return _validation([{"field": "status", "message": "Indica el estado nuevo."}])
    errors = validate_transition(current["status"], payload.get("status"))
    if errors:
        return _validation(errors)
    updated = update_status(incident_id, payload["status"])
    if updated is None:
        return JSONResponse(
            status_code=404,
            content={"error": "not_found", "message": "No encontramos esa incidencia."},
        )
    return JSONResponse(updated)
