"""HTTP adapter for incident analysis. Rules live in the shared package."""

from __future__ import annotations

from fastapi import APIRouter, File, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, Response

from app.config import max_upload_bytes
from app.infrastructure.analysis_store import get_store
from app.pages import render_home, render_results_fragment_with_csv
from incident_analysis.engine import AnalysisError, analyze_bytes

router = APIRouter(prefix="/api/incidents", tags=["incidents"])


@router.post("/analyze")
async def analyze(request: Request, file: UploadFile | None = File(default=None)) -> Response:
    if file is None:
        return _error(
            request,
            400,
            "missing_file",
            "Falta el fichero CSV. Envíalo en el campo file.",
        )
    raw = await file.read()
    if len(raw) > max_upload_bytes():
        return _error(
            request,
            413,
            "file_too_large",
            "El fichero supera el tamaño máximo admitido.",
        )
    try:
        report = analyze_bytes(raw, file.filename or "upload.csv")
    except AnalysisError as exc:
        return _error(request, 400, exc.code, exc.message_es)
    payload = report.as_dict()
    csv_text = report.csv_text()
    get_store().save(payload, csv_text)
    if _fragment(request):
        return HTMLResponse(render_results_fragment_with_csv(payload, csv_text))
    if _html_page(request):
        fragment = render_results_fragment_with_csv(payload, csv_text)
        return HTMLResponse(render_home(results_html=fragment))
    return JSONResponse(payload)


@router.get("/results/export")
async def export_results(request: Request) -> Response:
    stored = get_store()
    if stored.payload is None or stored.csv_text is None:
        return _error(
            request,
            404,
            "no_analysis",
            "No hay un análisis guardado. Sube un CSV primero.",
        )
    return Response(
        content=stored.csv_text,
        media_type="text/csv",
        headers={
            "Content-Disposition": 'attachment; filename="results.csv"',
            "Cache-Control": "no-store",
        },
    )


def _error(request: Request, status: int, code: str, message: str) -> Response:
    if _html_page(request) and not _fragment(request):
        return HTMLResponse(render_home(error=message), status_code=status)
    return JSONResponse(
        status_code=status,
        content={"error": code, "message": message},
    )


def _fragment(request: Request) -> bool:
    return request.headers.get("x-report-fragment") == "1"


def _html_page(request: Request) -> bool:
    accept = request.headers.get("accept", "")
    return "text/html" in accept and "application/json" not in accept
