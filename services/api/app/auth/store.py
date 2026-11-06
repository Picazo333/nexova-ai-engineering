"""TinyDB file for User and Profile.

Users and profiles stay in this JSON file. They are not SQLModel tables and
they are not created in Supabase or PostgreSQL. Other modules that need the
caller should store the TinyDB id as `user_uuid`.
"""

from __future__ import annotations

import os
import threading
from pathlib import Path

from tinydb import TinyDB
from tinydb.table import Table

from app.config import DEFAULT_DATA_DIR

_lock = threading.Lock()
_db: TinyDB | None = None
_path: Path | None = None


def db_file() -> Path:
    directory = Path(os.environ.get("AUTH_DATA_DIR", str(DEFAULT_DATA_DIR)))
    return directory / "auth.json"


def get_auth_db() -> TinyDB:
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


def reset_auth_db() -> None:
    """Close the cached handle so the next call follows the current env path."""
    global _db, _path
    with _lock:
        if _db is not None:
            _db.close()
        _db = None
        _path = None


def auth_lock() -> threading.Lock:
    return _lock


def users_table() -> Table:
    return get_auth_db().table("users")


def profiles_table() -> Table:
    return get_auth_db().table("profiles")


def reset_tokens_table() -> Table:
    """Hashed single-use password reset tokens. The raw token is not stored."""
    return get_auth_db().table("password_reset_tokens")


def reset_attempts_table() -> Table:
    """Forgot-password attempts, used to cap requests per email per hour."""
    return get_auth_db().table("password_reset_attempts")
