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

from app.config import BACKOFFICE_DIR, cors_origins
from app.pages import render_home, render_not_found, render_privacy, render_server_error
from app.routers.directory_ui import router as directory_router
from app.routers.incidents import router as incidents_router
from routes.suppliers import router as suppliers_router

logger = logging.getLogger("nexova.api")

PUBLIC_HTTP_MESSAGES = {
    404: "No encontrado.",
    405: "Ese método no está admitido en esta ruta.",
}


@asynccontextmanager
async def _lifespan(_app: FastAPI):
    if os.environ.get("SUPPLIERS_AUTOSEED", "1") != "0":
        from seed import seed_suppliers

        inserted, skipped = seed_suppliers()
        logger.info("supplier seed inserted=%s skipped=%s", inserted, skipped)
    yield
    from database import reset_db

    reset_db()


def create_app() -> FastAPI:
    app = FastAPI(
        title="Nexova API",
        docs_url=None,
        redoc_url=None,
        openapi_url="/api/openapi.json",
        lifespan=_lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins(),
        allow_credentials=False,
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Accept", "Content-Type", "X-Report-Fragment", "X-Directory-Fragment"],
    )
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
        if _prefer_json(request):
            if isinstance(exc.detail, dict):
                content = exc.detail
            else:
                content = {
                    "error": "http_error",
                    "message": PUBLIC_HTTP_MESSAGES.get(exc.status_code, "No se pudo completar la solicitud."),
                }
            return JSONResponse(status_code=exc.status_code, content=content)
        if exc.status_code == 404:
            return HTMLResponse(render_not_found(request.url.path), status_code=404)
        return HTMLResponse(render_server_error(), status_code=exc.status_code)

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


def _prefer_json(request: Request) -> bool:
    path = request.url.path
    if path.startswith("/api/") or path == "/suppliers" or path.startswith("/suppliers/"):
        accept = request.headers.get("accept", "")
        if "text/html" in accept and "application/json" not in accept:
            return False
        return True
    accept = request.headers.get("accept", "")
    return "application/json" in accept and "text/html" not in accept


app = create_app()
