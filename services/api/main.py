"""Alternate entrypoint: `uvicorn main:app` from services/api.

The composed application lives in app.main so the incidents backoffice and the
supplier directory share one process.
"""

from app.main import app

__all__ = ["app"]
