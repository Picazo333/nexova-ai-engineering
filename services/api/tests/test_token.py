"""Token decisions: what GET /auth/me accepts, and what the signer refuses."""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from jose import jwt
from tinydb import Query

from app.auth.deps import get_current_user, get_optional_user
from app.auth.security import (
    AuthConfigError,
    TokenError,
    bcrypt_rounds,
    create_access_token,
    decode_access_token,
    expire_minutes,
    hash_password,
    jwt_secret,
    load_local_env,
    verify_password,
)
from app.auth.service import update_user
from app.auth.store import auth_lock, profiles_table, reset_auth_db, users_table
from tests.auth_support import PASSWORD, bearer, register, token_for


def test_happy_path_me_returns_the_caller_named_in_the_token(client: TestClient) -> None:
    created = register(client, "ana@nexova.test", phone="600111222")
    token = token_for(client, "ana@nexova.test")
    me = client.get("/auth/me", headers=bearer(token))
    assert me.status_code == 200
    body = me.json()
    assert body["id"] == created["id"]
    assert body["email"] == "ana@nexova.test"
    assert body["role"] == "user"
    assert body["profile"]["phone"] == "600111222"
    assert "hashed_password" not in body


def test_edge_an_expired_token_is_refused_and_an_older_one_still_works(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    register(client, "ana@nexova.test")
    fresh = token_for(client, "ana@nexova.test")
    monkeypatch.setenv("ACCESS_TOKEN_EXPIRE_MINUTES", "-1")
    logged = client.post(
        "/auth/login",
        json={"email": "ana@nexova.test", "password": PASSWORD},
    )
    assert logged.status_code == 200
    expired = client.get("/auth/me", headers=bearer(logged.json()["access_token"]))
    assert expired.status_code == 401
    assert expired.json()["message"] == "El token no es válido o ha caducado."
    still = client.get("/auth/me", headers=bearer(fresh))
    assert still.status_code == 200
    assert still.json()["email"] == "ana@nexova.test"


def test_edge_a_token_stops_resolving_when_the_store_moves(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    register(client, "ana@nexova.test")
    token = token_for(client, "ana@nexova.test")
    monkeypatch.setenv("AUTH_DATA_DIR", str(tmp_path / "other-auth"))
    reset_auth_db()
    moved = client.get("/auth/me", headers=bearer(token))
    assert moved.status_code == 401
    assert users_table().all() == []


def test_failure_malformed_forged_and_mismatched_tokens_are_rejected(client: TestClient) -> None:
    created = register(client, "ana@nexova.test")
    missing = client.get("/auth/me")
    assert missing.status_code == 401
    assert missing.json()["message"] == "Falta el token de acceso."
    malformed = client.get("/auth/me", headers={"Authorization": "Bearer esto-no-es-un-jwt"})
    assert malformed.status_code == 401
    forged = jwt.encode(
        {"sub": created["id"], "user_uuid": created["id"]},
        "otro-secreto-distinto-de-16",
        algorithm="HS256",
    )
    assert client.get("/auth/me", headers=bearer(forged)).status_code == 401
    # sub and user_uuid are the same person. A disagreement is not a session.
    skewed = jwt.encode(
        {
            "sub": created["id"],
            "user_uuid": "otro-usuario",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
        },
        "test-jwt-secret-local-only",
        algorithm="HS256",
    )
    rejected = client.get("/auth/me", headers=bearer(skewed))
    assert rejected.status_code == 401
    with pytest.raises(TokenError):
        decode_access_token(skewed)


def test_failure_deleted_and_inactive_subjects_lose_the_session(client: TestClient) -> None:
    created = register(client, "ana@nexova.test")
    token = token_for(client, "ana@nexova.test")
    update_user(created["id"], {"is_active": False})
    inactive = client.get("/auth/me", headers=bearer(token))
    assert inactive.status_code == 401
    update_user(created["id"], {"is_active": True})
    assert client.get("/auth/me", headers=bearer(token)).status_code == 200
    with auth_lock():
        users_table().remove(Query().id == created["id"])
    gone = client.get("/auth/me", headers=bearer(token))
    assert gone.status_code == 401


def test_edge_a_user_without_a_profile_is_not_returned_as_me(client: TestClient) -> None:
    created = register(client, "ana@nexova.test")
    token = token_for(client, "ana@nexova.test")
    with auth_lock():
        profiles_table().remove(Query().user_id == created["id"])
    response = client.get("/auth/me", headers=bearer(token))
    assert response.status_code == 404
    assert response.json()["message"] == "Este usuario no tiene perfil."


def test_optional_user_fails_closed_on_a_bad_token(client: TestClient) -> None:
    created = register(client, "ana@nexova.test")
    token = token_for(client, "ana@nexova.test")
    assert get_optional_user(None) is None
    assert get_optional_user("esto-no-es-un-jwt") is None
    found = get_optional_user(token)
    assert found is not None
    assert found["id"] == created["id"]
    assert get_current_user(token)["email"] == "ana@nexova.test"


def test_password_hash_accepts_the_original_and_rejects_a_broken_hash() -> None:
    hashed = hash_password(PASSWORD)
    assert verify_password(PASSWORD, hashed) is True
    assert verify_password("clave-erronea", hashed) is False
    assert verify_password(PASSWORD, "not-a-bcrypt-hash") is False


def test_signer_refuses_a_placeholder_secret_and_a_bad_lifetime(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    assert jwt_secret() == "test-jwt-secret-local-only"
    assert expire_minutes() == 30
    assert bcrypt_rounds() == 4
    monkeypatch.setenv("JWT_SECRET", "change-me")
    with pytest.raises(AuthConfigError):
        jwt_secret()
    monkeypatch.setenv("JWT_SECRET", "short-secret")
    with pytest.raises(AuthConfigError):
        create_access_token("user-1")
    monkeypatch.setenv("JWT_SECRET", "test-jwt-secret-local-only")
    monkeypatch.setenv("ACCESS_TOKEN_EXPIRE_MINUTES", "no-es-un-numero")
    with pytest.raises(AuthConfigError):
        expire_minutes()
    monkeypatch.setenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    monkeypatch.setenv("AUTH_BCRYPT_ROUNDS", "3")
    with pytest.raises(AuthConfigError):
        bcrypt_rounds()
    monkeypatch.setenv("AUTH_BCRYPT_ROUNDS", "muchos")
    with pytest.raises(AuthConfigError):
        hash_password(PASSWORD)


def test_env_file_cannot_replace_a_secret_already_in_the_process(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    env_dir = tmp_path / "env-home"
    env_dir.mkdir()
    (env_dir / ".env").write_text(
        "\n".join(
            [
                "# fixture",
                "",
                "sin-igual",
                "JWT_SECRET=fixture-must-not-replace",
                'AUTH_FIXTURE_MARK="from-file"',
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr("app.config.API_DIR", env_dir)
    monkeypatch.delenv("AUTH_FIXTURE_MARK", raising=False)
    load_local_env()
    assert jwt_secret() == "test-jwt-secret-local-only"
    assert os.environ["AUTH_FIXTURE_MARK"] == "from-file"
    monkeypatch.setattr("app.config.API_DIR", tmp_path / "missing-env-dir")
    load_local_env()
