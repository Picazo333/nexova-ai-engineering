"""Auth settings for every API test. Each test gets its own TinyDB file."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def auth_environment(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    monkeypatch.setenv("JWT_SECRET", "test-jwt-secret-local-only")
    monkeypatch.setenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    monkeypatch.setenv("AUTH_BCRYPT_ROUNDS", "4")
    monkeypatch.setenv("AUTH_DATA_DIR", str(tmp_path / "auth"))
    monkeypatch.setenv("EMAIL_TRANSPORT", "mock")
    monkeypatch.setenv("PUBLIC_APP_URL", "http://127.0.0.1:3000")
    monkeypatch.setenv("PASSWORD_RESET_EXPIRE_MINUTES", "30")
    monkeypatch.setenv("PASSWORD_RESET_MAX_PER_HOUR", "5")
    monkeypatch.delenv("RESEND_API_KEY", raising=False)
    monkeypatch.delenv("SENDGRID_API_KEY", raising=False)
    monkeypatch.delenv("PASSWORD_RESET_CAPTURE_FILE", raising=False)
    # Inventory tests opt in with NEXOVA_TEST_DATABASE_URL. A developer URL
    # must not make the rest of the suite open PostgreSQL.
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("INVENTORY_SCHEMA", raising=False)
    from app.auth.mailer import clear_mock_outbox
    from app.auth.store import reset_auth_db

    clear_mock_outbox()
    reset_auth_db()
    yield
    clear_mock_outbox()
    reset_auth_db()


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    """Isolated supplier and incident files. The client does not carry a token."""
    monkeypatch.setenv("SUPPLIERS_DATA_DIR", str(tmp_path / "suppliers"))
    monkeypatch.setenv("SUPPLIERS_AUTOSEED", "0")
    monkeypatch.setenv("INCIDENTS_DATA_DIR", str(tmp_path / "incidents"))
    from app.auth.store import reset_auth_db
    from app.infrastructure.analysis_store import reset_store
    from app.main import create_app
    from database import reset_db

    from incident_store import reset_incidents_db

    reset_db()
    reset_auth_db()
    reset_incidents_db()
    reset_store(tmp_path / "incidents")
    with TestClient(create_app()) as test_client:
        yield test_client
    reset_db()
    reset_auth_db()
    reset_incidents_db()
