"""Compose the Nexova API, the incidents backoffice, and the supplier directory."""

from __future__ import annotations

import html
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.auth.guide import API_DESCRIPTION, OPENAPI_TAGS
from app.auth.security import AuthConfigError, expire_minutes, jwt_secret, load_local_env
from app.auth.store import reset_auth_db
from app.config import BACKOFFICE_DIR, cors_origins
from app.http_catalog import catalog_message, message_from_validation, public_body, safe_detail
from app.pages import (
    render_auth_required,
    render_home,
    render_not_found,
    render_page,
    render_privacy,
    render_server_error,
)
from app.routers.agent import router as agent_router
from app.routers.auth import router as auth_router
from app.routers.directory_ui import router as directory_router
from app.routers.incident_records import router as incident_records_router
from app.routers.incident_ui import router as incident_ui_router
from app.routers.incidents import router as incidents_router
from app.routers.profiles import router as profiles_router
from app.routers.inventory import router as inventory_router
from app.routers.knowledge import router as knowledge_router
from app.routers.users import router as users_router
from routes.suppliers import router as suppliers_router

KNOWLEDGE_UI = Path(__file__).resolve().parents[3] / "uis" / "knowledge-query"
AGENT_UI = Path(__file__).resolve().parents[3] / "uis" / "agent-compare"

logger = logging.getLogger("nexova.api")

API_ROOTS = ("/api/", "/users", "/auth", "/profiles", "/agent", "/inventory")


@asynccontextmanager
async def _lifespan(_app: FastAPI):
    load_local_env()
    try:
        jwt_secret()
        expire_minutes()
    except AuthConfigError:
        logger.error("auth config missing")
        raise
    if os.environ.get("SUPPLIERS_AUTOSEED", "1") != "0":
        from seed import seed_suppliers

        inserted, skipped = seed_suppliers()
        logger.info("supplier seed inserted=%s skipped=%s", inserted, skipped)
    from app.inventory.database import init_databases

    init_databases()
    yield
    from app.inventory.database import reset_engine
    from database import reset_db

    reset_engine()
    reset_db()
    reset_auth_db()
    from incident_store import reset_incidents_db

    reset_incidents_db()


def create_app() -> FastAPI:
    app = FastAPI(
        title="Nexova API",
        description=API_DESCRIPTION,
        openapi_tags=OPENAPI_TAGS,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/api/openapi.json",
        lifespan=_lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins(),
        allow_credentials=False,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=[
            "Accept",
            "Authorization",
            "Content-Type",
            "X-Report-Fragment",
            "X-Directory-Fragment",
        ],
    )
    app.include_router(auth_router)
    app.include_router(users_router)
    app.include_router(profiles_router)
    app.include_router(incident_records_router)
    app.include_router(incidents_router)
    app.include_router(incident_ui_router)
    app.include_router(suppliers_router)
    app.include_router(directory_router)
    app.include_router(knowledge_router)
    app.include_router(agent_router)
    app.include_router(inventory_router)
    app.mount("/ui", StaticFiles(directory=KNOWLEDGE_UI), name="knowledge-ui")
    app.mount("/css", StaticFiles(directory=BACKOFFICE_DIR / "css"), name="css")
    app.mount("/js", StaticFiles(directory=BACKOFFICE_DIR / "js"), name="js")
    app.mount("/tokens", StaticFiles(directory=BACKOFFICE_DIR / "tokens"), name="tokens")
    app.mount("/brand", StaticFiles(directory=BACKOFFICE_DIR / "brand"), name="brand")

    @app.get("/favicon.svg", include_in_schema=False)
    def favicon_svg() -> FileResponse:
        return FileResponse(BACKOFFICE_DIR / "favicon.svg", media_type="image/svg+xml")

    @app.get("/favicon.ico", include_in_schema=False)
    def favicon_ico() -> FileResponse:
        return FileResponse(BACKOFFICE_DIR / "favicon.svg", media_type="image/svg+xml")

    @app.get("/health", include_in_schema=False)
    def health() -> JSONResponse:
        return JSONResponse({"status": "ok"})

    @app.get("/", response_class=HTMLResponse)
    def home() -> HTMLResponse:
        return HTMLResponse(render_home(), headers={"Cache-Control": "no-store"})

    @app.get("/conocimiento", include_in_schema=False)
    def knowledge_page() -> FileResponse:
        return FileResponse(KNOWLEDGE_UI / "index.html")

    @app.get("/agente", include_in_schema=False)
    def agent_compare_page() -> HTMLResponse:
        from app.agent.compare_page import render_compare_page

        return HTMLResponse(render_compare_page(), headers={"Cache-Control": "no-store"})

    @app.post("/agente", include_in_schema=False)
    async def agent_compare_submit(request: Request) -> HTMLResponse:
        from app.agent.compare_page import render_submitted_page

        form = await request.form()
        lane = str(form.get("lane") or "")
        question = str(form.get("question") or "")
        header = request.headers.get("authorization", "")
        token = header[7:].strip() if header.lower().startswith("bearer ") else None
        return HTMLResponse(
            render_submitted_page(lane=lane, question=question, access_token=token),
            headers={"Cache-Control": "no-store"},
        )

    @app.get("/agente/styles.css", include_in_schema=False)
    def agent_compare_css() -> FileResponse:
        return FileResponse(AGENT_UI / "styles.css", media_type="text/css")

    @app.get("/agente/app.js", include_in_schema=False)
    def agent_compare_js() -> FileResponse:
        return FileResponse(AGENT_UI / "app.js", media_type="text/javascript")

    @app.get("/privacidad", response_class=HTMLResponse)
    def privacy() -> HTMLResponse:
        return HTMLResponse(render_privacy(), headers={"Cache-Control": "no-store"})

    @app.exception_handler(RequestValidationError)
    async def invalid_request(request: Request, exc: RequestValidationError) -> HTMLResponse | JSONResponse:
        message = message_from_validation(exc.errors())
        if _error_as_json(request):
            return JSONResponse(
                status_code=422,
                content={"error": "http_error", "message": message, "detail": message},
            )
        return HTMLResponse(_validation_page(message), status_code=422)

    @app.exception_handler(StarletteHTTPException)
    async def http_error(request: Request, exc: StarletteHTTPException) -> HTMLResponse | JSONResponse:
        headers = {key: value for key, value in (exc.headers or {}).items()}
        if exc.status_code == 401 and not any(key.lower() == "www-authenticate" for key in headers):
            headers["WWW-Authenticate"] = "Bearer"
        if _error_as_json(request):
            return JSONResponse(status_code=exc.status_code, content=_error_content(exc), headers=headers)
        if exc.status_code in (401, 403):
            raw = exc.detail if isinstance(exc.detail, str) else ""
            message = safe_detail(exc.status_code, raw) or catalog_message(exc.status_code)
            return HTMLResponse(
                render_auth_required(exc.status_code, message),
                status_code=exc.status_code,
                headers=headers,
            )
        if exc.status_code == 404:
            return HTMLResponse(render_not_found(request.url.path), status_code=404, headers=headers)
        if exc.status_code == 422 and isinstance(exc.detail, str):
            message = safe_detail(422, exc.detail) or catalog_message(422)
            return HTMLResponse(_validation_page(message), status_code=422, headers=headers)
        return HTMLResponse(render_server_error(), status_code=exc.status_code, headers=headers)

    @app.exception_handler(Exception)
    async def unhandled(request: Request, exc: Exception) -> HTMLResponse | JSONResponse:
        logger.error("unhandled %s", type(exc).__name__)
        if _prefer_json(request):
            return JSONResponse(
                status_code=500,
                content={
                    "error": "internal_error",
                    "message": "No se pudo completar la operación. Inténtalo de nuevo.",
                },
            )
        return HTMLResponse(render_server_error(), status_code=500)

    return app


def _is_api(path: str) -> bool:
    if path == "/suppliers" or path.startswith("/suppliers/"):
        return True
    for prefix in API_ROOTS:
        if path == prefix.rstrip("/") or path.startswith(prefix if prefix.endswith("/") else prefix + "/"):
            return True
    return False


def _prefers_html(request: Request) -> bool:
    accept = request.headers.get("accept", "")
    return "text/html" in accept and "application/json" not in accept


def _error_as_json(request: Request) -> bool:
    if request.headers.get("x-report-fragment") == "1":
        return True
    if request.headers.get("x-directory-fragment") == "1":
        return True
    if _is_api(request.url.path):
        return not _prefers_html(request)
    accept = request.headers.get("accept", "")
    return "application/json" in accept and "text/html" not in accept


def _error_content(exc: StarletteHTTPException) -> dict:
    # 4xx sentences written by the routers stay. 5xx and anything that looks
    # like a trace, a path, or a secret is replaced by the catalog.
    return public_body(exc.status_code, exc.detail)


def _validation_page(message: str) -> str:
    return render_page(
        title="Datos no válidos · Nexova",
        description="La solicitud no se puede aceptar.",
        main=(
            "<h1>Hay datos que no se pueden aceptar</h1>"
            f"<p>{html.escape(message)}</p>"
            '<p class="actions"><a class="button" href="/">Ir al inicio</a></p>'
            "<p>Si se repite, contacta con el soporte interno de Nexova.</p>"
        ),
        current="",
    )


def _prefer_json(request: Request) -> bool:
    return _error_as_json(request)


app = create_app()
