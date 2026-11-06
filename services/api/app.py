"""ASGI app: knowledge routes plus the query page."""

from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from data.rag_settings import ROOT
from services.api.routers.knowledge import router

UI_DIR = ROOT / "uis" / "knowledge-query"


def create_app() -> FastAPI:
    logging.basicConfig(level=logging.INFO)
    app = FastAPI(title="Nexova knowledge", docs_url="/docs", redoc_url=None)
    app.include_router(router)

    @app.get("/health", include_in_schema=False)
    def health() -> dict:
        return {"status": "ok"}

    @app.get("/", include_in_schema=False)
    def home() -> FileResponse:
        return FileResponse(UI_DIR / "index.html")

    @app.exception_handler(StarletteHTTPException)
    async def http_error(request, exc: StarletteHTTPException):
        accept = request.headers.get("accept", "")
        if exc.status_code == 404 and "text/html" in accept and "application/json" not in accept:
            return FileResponse(UI_DIR / "404.html", status_code=404)
        return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)

    app.mount("/ui", StaticFiles(directory=UI_DIR), name="ui")
    return app


app = create_app()
