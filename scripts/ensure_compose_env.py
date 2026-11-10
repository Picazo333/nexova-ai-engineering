#!/usr/bin/env python3
"""Fill the gitignored root .env for Compose.

Blank keys get a local value. A secret that is already set is left untouched
and is never printed.
"""

from __future__ import annotations

import secrets
import stat
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT / ".env"
EXAMPLE_PATH = ROOT / ".env.example"

PLACEHOLDERS = {
    "",
    "change-me",
    "changeme",
    "replace-with-a-long-local-secret",
}

DEFAULTS = {
    "API_INTERNAL_URL": "http://services:8000",
    "QDRANT_URL": "http://qdrant:6333",
    "ACCESS_TOKEN_EXPIRE_MINUTES": "30",
    "PUBLIC_APP_URL": "http://127.0.0.1:3000",
    "NEXT_PUBLIC_PORTAL_URL": "http://127.0.0.1:3000",
    "NEXT_PUBLIC_API_ORIGIN": "http://127.0.0.1:8000",
    "WATCHPACK_POLLING": "true",
    "WATCHFILES_FORCE_POLLING": "true",
    "PASSWORD_RESET_EXPIRE_MINUTES": "30",
    "PASSWORD_RESET_MAX_PER_HOUR": "5",
}


def _blank(value: str) -> bool:
    return value.strip().strip('"').strip("'") in PLACEHOLDERS


def fill(text: str, *, secret: str | None = None) -> str:
    """Return text with empty Compose keys filled. Does not replace real values."""

    lines = text.splitlines()
    seen: set[str] = set()
    output: list[str] = []
    for line in lines:
        if not line or line.lstrip().startswith("#") or "=" not in line:
            output.append(line)
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        seen.add(key)
        if key == "JWT_SECRET" and _blank(value):
            output.append(f"JWT_SECRET={secret or secrets.token_urlsafe(32)}")
            continue
        if key in DEFAULTS and _blank(value):
            output.append(f"{key}={DEFAULTS[key]}")
            continue
        output.append(line)
    if "JWT_SECRET" not in seen:
        output.append(f"JWT_SECRET={secret or secrets.token_urlsafe(32)}")
    for key, value in DEFAULTS.items():
        if key not in seen:
            output.append(f"{key}={value}")
    body = "\n".join(output)
    if not body.endswith("\n"):
        body += "\n"
    return body


def main() -> None:
    if ENV_PATH.exists():
        source = ENV_PATH.read_text(encoding="utf-8")
    elif EXAMPLE_PATH.exists():
        source = EXAMPLE_PATH.read_text(encoding="utf-8")
    else:
        source = ""
    ENV_PATH.write_text(fill(source), encoding="utf-8")
    ENV_PATH.chmod(stat.S_IRUSR | stat.S_IWUSR)
    print("Listo .env. Los secretos no se muestran.")


if __name__ == "__main__":
    main()
