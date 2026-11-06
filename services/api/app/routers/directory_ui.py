"""Backoffice page for the supplier directory."""

from __future__ import annotations

import html

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from pydantic import ValidationError

import directory
from app.directory_page import notice_for, render_directory, render_fragment
from models import SupplierQuery, validation_message

router = APIRouter(tags=["directory-page"])


def _filters(request: Request) -> SupplierQuery:
    return SupplierQuery.model_validate(
        {
            "country": request.query_params.get("country") or None,
            "category": request.query_params.get("category") or None,
            "status": request.query_params.get("status") or None,
        }
    )


def _rows(filters: SupplierQuery) -> list[dict]:
    return directory.list_suppliers(
        country=filters.country.value if filters.country else None,
        category=filters.category.value if filters.category else None,
        status=filters.status.value if filters.status else None,
    )


@router.get("/proveedores", response_class=HTMLResponse)
def directory_page(request: Request) -> HTMLResponse:
    fragment = request.headers.get("x-directory-fragment") == "1"
    try:
        filters = _filters(request)
    except ValidationError as exc:
        message = validation_message(exc)
        if fragment:
            body = f'<div data-list-state="error"><p>{html.escape(message)}</p></div>'
            return HTMLResponse(body, status_code=422, headers={"Cache-Control": "no-store"})
        page = render_directory(
            suppliers=[],
            total=directory.count_suppliers(),
            filters=SupplierQuery(),
            error=message,
            notice=None,
            form_values=None,
        )
        return HTMLResponse(page, status_code=422, headers={"Cache-Control": "no-store"})
    rows = _rows(filters)
    if fragment:
        return HTMLResponse(
            render_fragment(suppliers=rows, total=directory.count_suppliers(), filters=filters),
            headers={"Cache-Control": "no-store"},
        )
    page = render_directory(
        suppliers=rows,
        total=directory.count_suppliers(),
        filters=filters,
        error=None,
        notice=notice_for(request.query_params.get("aviso")),
        form_values=None,
    )
    return HTMLResponse(page, headers={"Cache-Control": "no-store"})
