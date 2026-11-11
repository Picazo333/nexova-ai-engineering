"""Auth settings for every API test. Each test gets its own TinyDB file."""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def auth_environment(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("JWT_SECRET", "test-jwt-secret-local-only")
    monkeypatch.setenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    monkeypatch.setenv("AUTH_BCRYPT_ROUNDS", "4")
    monkeypatch.setenv("AUTH_DATA_DIR", str(tmp_path / "auth"))
