"""Backoffice pages for registering and reviewing incidents."""

from __future__ import annotations

import sys
from pathlib import Path

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

_SHARED = Path(__file__).resolve().parents[4] / "packages" / "shared"
if str(_SHARED) not in sys.path:
    sys.path.insert(0, str(_SHARED))

from app.auth.deps import get_optional_user  # noqa: E402
from app.incident_pages import render_panel, render_register  # noqa: E402
from incident_store import create_incident, list_incidents, summary  # noqa: E402
from nexova_incidents.model import validate_create, validate_filters  # noqa: E402

router = APIRouter(tags=["incident-pages"])


def _filters(request: Request) -> dict[str, str]:
    return {
        "status": request.query_params.get("status") or "",
        "origin": request.query_params.get("origin") or "",
        "branch": request.query_params.get("branch") or "",
        "category": request.query_params.get("category") or "",
    }


@router.get("/incidencias", response_class=HTMLResponse)
def incidents_panel(request: Request, user: dict | None = Depends(get_optional_user)) -> HTMLResponse:
    filters = _filters(request)
    if user is None:
        page = render_panel(
            items=None,
            summary=None,
            filters=filters,
            list_state="locked",
            summary_state="locked",
        )
        return HTMLResponse(page, headers={"Cache-Control": "no-store"})
    errors = validate_filters(filters)
    if errors:
        page = render_panel(
            items=None,
            summary=summary(),
            filters={key: "" for key in filters},
            list_state="error",
            list_message=errors[0]["message"],
            summary_state="ready",
        )
        return HTMLResponse(page, status_code=400, headers={"Cache-Control": "no-store"})
    items = list_incidents(
        status=filters["status"] or None,
        origin=filters["origin"] or None,
        branch=filters["branch"] or None,
        category=filters["category"] or None,
    )
    page = render_panel(
        items=items,
        summary=summary(),
        filters=filters,
        list_state="ready" if items else "empty",
        summary_state="ready",
    )
    return HTMLResponse(page, headers={"Cache-Control": "no-store"})


@router.get("/incidencias/nueva", response_class=HTMLResponse)
def incidents_register_form() -> HTMLResponse:
    return HTMLResponse(
        render_register(values={"status": "open"}),
        headers={"Cache-Control": "no-store"},
    )


@router.post("/incidencias/nueva", response_class=HTMLResponse)
async def incidents_register_submit(
    request: Request,
    user: dict | None = Depends(get_optional_user),
) -> HTMLResponse:
    form = await request.form()
    payload = {key: str(form.get(key) or "") for key in ("title", "description", "category", "status", "origin", "branch")}
    if user is None:
        page = render_register(
            values=payload,
            form_error="Hace falta una sesión en esta pestaña para registrar la incidencia. Entra y vuelve a enviarla. Los datos del formulario se conservan.",
        )
        return HTMLResponse(page, status_code=401, headers={"Cache-Control": "no-store"})
    errors = validate_create(payload)
    if errors:
        page = render_register(values=payload, errors=errors, form_error="Revisa los campos marcados.")
        return HTMLResponse(page, status_code=400, headers={"Cache-Control": "no-store"})
    created = create_incident(payload)
    page = render_register(
        values={"status": "open"},
        confirmation=f"Incidencia registrada. Identificador {created['id']}.",
    )
    return HTMLResponse(page, status_code=201, headers={"Cache-Control": "no-store"})
