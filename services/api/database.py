"""TinyDB file for the supplier directory.

The file stays on disk under services/api/.data (or SUPPLIERS_DATA_DIR) so a
restart of the API process reads the same records.
"""

from __future__ import annotations

import os
import threading
from pathlib import Path

from tinydb import TinyDB

from app.config import DEFAULT_DATA_DIR

_lock = threading.Lock()
_db: TinyDB | None = None
_path: Path | None = None


def db_file() -> Path:
    directory = Path(os.environ.get("SUPPLIERS_DATA_DIR", str(DEFAULT_DATA_DIR)))
    return directory / "suppliers.json"


def get_db() -> TinyDB:
    global _db, _path
    path = db_file()
    if _db is not None and _path == path:
        return _db
    if _db is not None:
        _db.close()
    path.parent.mkdir(parents=True, exist_ok=True)
    _db = TinyDB(path)
    _path = path
    return _db


def reset_db() -> None:
    """Close the cached handle so the next call follows the current env path."""
    global _db, _path
    with _lock:
        if _db is not None:
            _db.close()
        _db = None
        _path = None


def db_lock() -> threading.Lock:
    return _lock
