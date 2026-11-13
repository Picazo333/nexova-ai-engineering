"""Runtime settings read from the environment."""

from __future__ import annotations

import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
BACKOFFICE_DIR = REPO_ROOT / "uis" / "backoffice"
API_DIR = Path(__file__).resolve().parents[1]
DEFAULT_DATA_DIR = API_DIR / ".data"
DEFAULT_MAX_UPLOAD_BYTES = 32 * 1024 * 1024
DEFAULT_CORS_ORIGINS = (
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
)


def max_upload_bytes() -> int:
    raw = os.environ.get("INCIDENTS_MAX_UPLOAD_BYTES", str(DEFAULT_MAX_UPLOAD_BYTES))
    return int(raw)


def data_dir() -> Path:
    return Path(os.environ.get("INCIDENTS_DATA_DIR", str(DEFAULT_DATA_DIR)))


def cors_origins() -> list[str]:
    raw = os.environ.get("INCIDENTS_CORS_ORIGINS", ",".join(DEFAULT_CORS_ORIGINS))
    return [item.strip() for item in raw.split(",") if item.strip()]


def telemetry_endpoint() -> str:
    """Declared URL. Storage stays on this service and does not forward the batch."""
    return os.environ.get("TELEMETRY_ENDPOINT", "").strip()
