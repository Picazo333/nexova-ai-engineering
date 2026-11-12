"""Supplier directory HTTP contract: /suppliers."""

from __future__ import annotations

import json
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, RedirectResponse, Response
from pydantic import ValidationError

import directory
from app.auth.deps import get_current_user
from app.directory_page import render_directory
from models import RateUpdate, StatusUpdate, SupplierCreate, SupplierQuery, validation_message

router = APIRouter(tags=["suppliers"], dependencies=[Depends(get_current_user)])

NOT_FOUND = "No existe un proveedor con ese id."


def wants_html(request: Request) -> bool:
    accept = request.headers.get("accept", "")
    if "application/json" in accept and "text/html" not in accept:
        return False
    if "application/json" in request.headers.get("content-type", ""):
        return False
    return "text/html" in accept


def _json_error(status: int, message: str, *, detail: object | None = None) -> JSONResponse:
    body: dict[str, object] = {"message": message}
    if detail is None:
        body["detail"] = message
    else:
        body["detail"] = detail
    return JSONResponse(status_code=status, content=jsonable_encoder(body))


def _validation_error(exc: ValidationError) -> JSONResponse:
    # The Spanish sentence is enough. exc.errors() repeats the submitted input.
    return _json_error(422, validation_message(exc))


async def _object_body(request: Request) -> tuple[dict | JSONResponse, bool]:
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        try:
            payload = await request.json()
        except (json.JSONDecodeError, UnicodeDecodeError, ValueError):
            return _json_error(422, "El cuerpo tiene que ser un objeto JSON."), False
        if not isinstance(payload, dict):
            return _json_error(422, "El cuerpo tiene que ser un objeto JSON."), False
        return payload, False
    form = await request.form()
    categories = form.getlist("categories")
    payload = {
        "name": form.get("name"),
        "country": form.get("country") or None,
        "categories": categories,
        "monthly_rate": form.get("monthly_rate"),
        "currency": form.get("currency") or None,
        "status": form.get("status") or None,
        "contract_renewal_date": form.get("contract_renewal_date") or None,
        "contact_email": form.get("contact_email") or None,
        "notes": form.get("notes") or None,
    }
    return payload, True


def _filters_from_request(request: Request) -> SupplierQuery:
    params = {
        "country": request.query_params.get("country") or None,
        "category": request.query_params.get("category") or None,
        "status": request.query_params.get("status") or None,
    }
    return SupplierQuery.model_validate(params)


def _redirect_target(filters: SupplierQuery, aviso: str, supplier_id: int | None = None) -> str:
    query: dict[str, str] = {}
    if filters.country is not None:
        query["country"] = filters.country.value
    if filters.category is not None:
        query["category"] = filters.category.value
    if filters.status is not None:
        query["status"] = filters.status.value
    query["aviso"] = aviso
    url = "/proveedores"
    if query:
        url += "?" + urlencode(query)
    if supplier_id is not None:
        url += f"#proveedor-{supplier_id}"
    return url


def _html_directory(
    request: Request,
    *,
    status_code: int,
    error: str | None = None,
    form_values: dict | None = None,
) -> Response:
    try:
        filters = _filters_from_request(request)
    except ValidationError as exc:
        page = render_directory(
            suppliers=[],
            total=directory.count_suppliers(),
            filters=SupplierQuery(),
            error=validation_message(exc),
            notice=None,
            form_values=form_values,
        )
        return Response(content=page, status_code=422, media_type="text/html")
    rows = directory.list_suppliers(
        country=filters.country.value if filters.country else None,
        category=filters.category.value if filters.category else None,
        status=filters.status.value if filters.status else None,
    )
    page = render_directory(
        suppliers=rows,
        total=directory.count_suppliers(),
        filters=filters,
        error=error,
        notice=None,
        form_values=form_values,
    )
    return Response(content=page, status_code=status_code, media_type="text/html")


@router.get("/suppliers")
def list_suppliers(
    country: str | None = None,
    category: str | None = None,
    status: str | None = None,
) -> JSONResponse:
    try:
        filters = SupplierQuery.model_validate(
            {"country": country, "category": category, "status": status}
        )
    except ValidationError as exc:
        return _validation_error(exc)
    rows = directory.list_suppliers(
        country=filters.country.value if filters.country else None,
        category=filters.category.value if filters.category else None,
        status=filters.status.value if filters.status else None,
    )
    return JSONResponse(content=rows)


@router.get("/suppliers/{supplier_id}")
def get_supplier(supplier_id: int) -> JSONResponse:
    found = directory.get_supplier(supplier_id)
    if found is None:
        return _json_error(404, NOT_FOUND)
    return JSONResponse(content=found)


@router.post("/suppliers")
async def create_supplier(request: Request) -> Response:
    raw, from_form = await _object_body(request)
    if isinstance(raw, JSONResponse):
        return raw
    try:
        model = SupplierCreate.model_validate(raw)
    except ValidationError as exc:
        message = validation_message(exc)
        if from_form and wants_html(request):
            return _html_directory(request, status_code=422, error=message, form_values=raw)
        return _validation_error(exc)
    created = directory.create_supplier(model)
    if from_form and wants_html(request):
        try:
            filters = _filters_from_request(request)
        except ValidationError:
            filters = SupplierQuery()
        return RedirectResponse(
            _redirect_target(filters, "registrado", created["id"]),
            status_code=303,
        )
    return JSONResponse(status_code=201, content=created)


@router.patch("/suppliers/{supplier_id}/rate")
async def patch_rate(supplier_id: int, request: Request) -> JSONResponse:
    raw, _from_form = await _object_body(request)
    if isinstance(raw, JSONResponse):
        return raw
    try:
        model = RateUpdate.model_validate(raw)
    except ValidationError as exc:
        return _validation_error(exc)
    updated = directory.update_rate(supplier_id, model.monthly_rate)
    if updated is None:
        return _json_error(404, NOT_FOUND)
    return JSONResponse(content=updated)


@router.post("/suppliers/{supplier_id}/rate")
async def post_rate(supplier_id: int, request: Request) -> Response:
    """HTML form fallback. The JSON contract remains PATCH."""
    raw, from_form = await _object_body(request)
    if isinstance(raw, JSONResponse):
        return raw
    try:
        model = RateUpdate.model_validate(raw)
    except ValidationError as exc:
        message = validation_message(exc)
        if from_form and wants_html(request):
            return _html_directory(request, status_code=422, error=message)
        return _validation_error(exc)
    updated = directory.update_rate(supplier_id, model.monthly_rate)
    if updated is None:
        if from_form and wants_html(request):
            return _html_directory(request, status_code=404, error=NOT_FOUND)
        return _json_error(404, NOT_FOUND)
    if from_form and wants_html(request):
        try:
            filters = _filters_from_request(request)
        except ValidationError:
            filters = SupplierQuery()
        return RedirectResponse(
            _redirect_target(filters, "tarifa", supplier_id),
            status_code=303,
        )
    return JSONResponse(content=updated)


@router.patch("/suppliers/{supplier_id}/status")
async def patch_status(supplier_id: int, request: Request) -> JSONResponse:
    raw, _from_form = await _object_body(request)
    if isinstance(raw, JSONResponse):
        return raw
    try:
        model = StatusUpdate.model_validate(raw)
    except ValidationError as exc:
        return _validation_error(exc)
    updated = directory.update_status(supplier_id, model.status.value)
    if updated is None:
        return _json_error(404, NOT_FOUND)
    return JSONResponse(content=updated)


@router.post("/suppliers/{supplier_id}/status")
async def post_status(supplier_id: int, request: Request) -> Response:
    raw, from_form = await _object_body(request)
    if isinstance(raw, JSONResponse):
        return raw
    try:
        model = StatusUpdate.model_validate(raw)
    except ValidationError as exc:
        message = validation_message(exc)
        if from_form and wants_html(request):
            return _html_directory(request, status_code=422, error=message)
        return _validation_error(exc)
    updated = directory.update_status(supplier_id, model.status.value)
    if updated is None:
        if from_form and wants_html(request):
            return _html_directory(request, status_code=404, error=NOT_FOUND)
        return _json_error(404, NOT_FOUND)
    if from_form and wants_html(request):
        try:
            filters = _filters_from_request(request)
        except ValidationError:
            filters = SupplierQuery()
        return RedirectResponse(
            _redirect_target(filters, "estado", supplier_id),
            status_code=303,
        )
    return JSONResponse(content=updated)


@router.delete("/suppliers/{supplier_id}")
def remove_supplier(supplier_id: int) -> JSONResponse:
    removed = directory.delete_supplier(supplier_id)
    if removed is None:
        return _json_error(404, NOT_FOUND)
    return JSONResponse(content=removed)
