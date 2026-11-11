"""POST /auth/login — credential decision and the token that follows from it."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from jose import jwt

from app.auth.service import create_user, update_user
from tests.auth_support import PASSWORD, login, register


def test_happy_path_signs_a_token_whose_subject_is_the_stored_id(client: TestClient) -> None:
    created = register(client, "ana@nexova.test")
    body = login(client, "ana@nexova.test")
    assert body["token_type"] == "bearer"
    assert body["user_uuid"] == created["id"]
    assert body["expires_in"] == 30 * 60
    payload = jwt.decode(
        body["access_token"],
        "test-jwt-secret-local-only",
        algorithms=["HS256"],
    )
    assert payload["sub"] == created["id"]
    assert payload["user_uuid"] == created["id"]
    assert "hashed_password" not in body


def test_edge_form_login_accepts_the_swagger_username_field(client: TestClient) -> None:
    created = register(client, "ana@nexova.test")
    response = client.post(
        "/auth/login",
        data={"username": "Ana@Nexova.test", "password": PASSWORD},
    )
    assert response.status_code == 200
    assert response.json()["user_uuid"] == created["id"]
    assert "set-cookie" not in {key.lower() for key in response.headers}


def test_edge_spaces_are_not_an_empty_password_but_they_do_not_match(client: TestClient) -> None:
    # Login only rejects a missing password. A password of spaces is present,
    # so the decision moves to the credential check and fails closed.
    register(client, "ana@nexova.test")
    response = client.post(
        "/auth/login",
        json={"email": "ana@nexova.test", "password": "        "},
    )
    assert response.status_code == 401
    assert response.json()["message"] == "El correo o la contraseña no son válidos."


def test_failure_unknown_email_and_wrong_password_share_one_message(client: TestClient) -> None:
    register(client, "ana@nexova.test")
    wrong = client.post(
        "/auth/login",
        json={"email": "ana@nexova.test", "password": "clave-erronea"},
    )
    missing = client.post(
        "/auth/login",
        json={"email": "nadie@nexova.test", "password": PASSWORD},
    )
    assert wrong.status_code == 401
    assert missing.status_code == 401
    # Same sentence on purpose: the caller must not learn whether the email exists.
    assert wrong.json()["message"] == missing.json()["message"]
    assert wrong.json()["message"] == "El correo o la contraseña no son válidos."


def test_failure_inactive_account_is_rejected_with_the_same_sentence(client: TestClient) -> None:
    record = create_user(email="baja@nexova.test", password=PASSWORD, name="Baja")
    # Deactivated in the store: the login must refuse it with the same sentence as a wrong password.
    update_user(record["id"], {"is_active": False})
    refused = client.post(
        "/auth/login",
        json={"email": "baja@nexova.test", "password": PASSWORD},
    )
    assert refused.status_code == 401
    assert refused.json()["message"] == "El correo o la contraseña no son válidos."


def test_failure_empty_password_is_rejected_before_any_account_lookup(client: TestClient) -> None:
    register(client, "ana@nexova.test")
    empty = client.post("/auth/login", json={"email": "ana@nexova.test", "password": ""})
    assert empty.status_code == 422
    assert empty.json()["message"] == "La contraseña es obligatoria."
    not_json = client.post(
        "/auth/login",
        content="[1, 2]",
        headers={"content-type": "application/json"},
    )
    assert not_json.status_code == 422
    assert not_json.json()["message"] == "El cuerpo tiene que ser un objeto JSON."
    broken = client.post(
        "/auth/login",
        content="{",
        headers={"content-type": "application/json"},
    )
    assert broken.status_code == 422
    assert broken.json()["message"] == "El cuerpo tiene que ser un objeto JSON."


def test_failure_without_a_signing_secret_the_login_does_not_invent_one(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.auth.security import AuthConfigError, create_access_token

    register(client, "ana@nexova.test")
    monkeypatch.delenv("JWT_SECRET")
    with pytest.raises(AuthConfigError) as caught:
        create_access_token("user-1")
    assert "JWT_SECRET" in str(caught.value)
    response = client.post(
        "/auth/login",
        json={"email": "ana@nexova.test", "password": PASSWORD},
    )
    # The signer refuses the call. The HTTP body stays generic and carries no token.
    assert response.status_code == 500
    assert "access_token" not in response.json()
    assert "JWT_SECRET" not in response.text
