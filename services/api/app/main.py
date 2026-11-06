"""Compose the Nexova API, the incidents backoffice, and the supplier directory."""

from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.auth.guide import API_DESCRIPTION, OPENAPI_TAGS
from app.auth.security import AuthConfigError, expire_minutes, jwt_secret, load_local_env
from app.auth.store import reset_auth_db
from app.config import BACKOFFICE_DIR, cors_origins
from app.pages import render_auth_required, render_home, render_not_found, render_privacy, render_server_error
from app.routers.auth import router as auth_router
from app.routers.directory_ui import router as directory_router
from app.routers.incidents import router as incidents_router
from app.routers.profiles import router as profiles_router
from app.routers.users import router as users_router
from routes.suppliers import router as suppliers_router

logger = logging.getLogger("nexova.api")

PUBLIC_HTTP_MESSAGES = {
    401: "Falta un token válido.",
    403: "No tienes permiso para ese recurso.",
    404: "No encontrado.",
    405: "Ese método no está admitido en esta ruta.",
}

API_ROOTS = ("/api/", "/users", "/auth", "/profiles")


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
    yield
    from database import reset_db

    reset_db()
    reset_auth_db()


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
    app.include_router(incidents_router)
    app.include_router(suppliers_router)
    app.include_router(directory_router)
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

    @app.get("/", response_class=HTMLResponse)
    def home() -> HTMLResponse:
        return HTMLResponse(render_home(), headers={"Cache-Control": "no-store"})

    @app.get("/privacidad", response_class=HTMLResponse)
    def privacy() -> HTMLResponse:
        return HTMLResponse(render_privacy(), headers={"Cache-Control": "no-store"})

    @app.exception_handler(StarletteHTTPException)
    async def http_error(request: Request, exc: StarletteHTTPException) -> HTMLResponse | JSONResponse:
        headers = {key: value for key, value in (exc.headers or {}).items()}
        if exc.status_code == 401 and not any(key.lower() == "www-authenticate" for key in headers):
            headers["WWW-Authenticate"] = "Bearer"
        if _error_as_json(request):
            return JSONResponse(status_code=exc.status_code, content=_error_content(exc), headers=headers)
        if exc.status_code in (401, 403):
            message = exc.detail if isinstance(exc.detail, str) else PUBLIC_HTTP_MESSAGES[exc.status_code]
            return HTMLResponse(
                render_auth_required(exc.status_code, message),
                status_code=exc.status_code,
                headers=headers,
            )
        if exc.status_code == 404:
            return HTMLResponse(render_not_found(request.url.path), status_code=404, headers=headers)
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
    if isinstance(exc.detail, dict):
        return exc.detail
    if exc.status_code in (401, 403) and isinstance(exc.detail, str) and exc.detail:
        code = "unauthorized" if exc.status_code == 401 else "forbidden"
        return {"error": code, "message": exc.detail, "detail": exc.detail}
    return {
        "error": "http_error",
        "message": PUBLIC_HTTP_MESSAGES.get(exc.status_code, "No se pudo completar la solicitud."),
    }


def _prefer_json(request: Request) -> bool:
    return _error_as_json(request)


app = create_app()
