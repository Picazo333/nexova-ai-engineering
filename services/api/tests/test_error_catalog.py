"""Error bodies stay human and do not carry a stack or a secret."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.http_catalog import CATALOG, catalog_message, message_from_validation, public_body, safe_detail

PASSWORD = "1234567"
SENTINEL = "secret-sentinel"


def test_catalog_has_a_sentence_for_each_public_code() -> None:
    for status in (400, 401, 403, 404, 405, 409, 413, 422, 500):
        sentence = CATALOG[status]
        assert sentence
        assert "Traceback" not in sentence
        assert "JWT_SECRET" not in sentence
        assert catalog_message(status) == (CATALOG[500] if status >= 500 else sentence)


def test_public_body_keeps_spanish_decisions_and_drops_traces() -> None:
    kept = public_body(409, "Ya existe una cuenta con ese correo.")
    assert kept["message"] == "Ya existe una cuenta con ese correo."
    assert kept["detail"] == kept["message"]

    empty_password = public_body(422, "La contraseña es obligatoria.")
    assert empty_password["message"] == "La contraseña es obligatoria."

    leaked = public_body(
        422,
        'Traceback (most recent call last): File "/workspace/services/api/.env" JWT_SECRET=super',
    )
    blob = str(leaked)
    assert "Traceback" not in blob
    assert "JWT_SECRET" not in blob
    assert "/workspace" not in blob
    assert ".env" not in blob

    crashed = public_body(500, f"{SENTINEL} Traceback line")
    assert SENTINEL not in str(crashed)
    assert crashed["message"] == CATALOG[500]
    assert safe_detail(500, "cualquier texto") is None


def test_validation_messages_omit_the_submitted_value() -> None:
    sentence = message_from_validation(
        [
            {
                "loc": ("body", "password"),
                "msg": "Value error, La contraseña tiene que tener al menos 8 caracteres, sin espacios al borde.",
                "input": PASSWORD,
            }
        ]
    )
    assert "8 caracteres" in sentence
    assert PASSWORD not in sentence


def test_register_422_does_not_echo_the_password_or_a_stack(client: TestClient) -> None:
    response = client.post(
        "/users",
        json={"email": "eco@nexova.test", "password": PASSWORD},
    )
    assert response.status_code == 422
    assert "8 caracteres" in response.text
    assert PASSWORD not in response.text
    lowered = response.text.lower()
    assert "traceback" not in lowered
    assert "jwt_secret" not in lowered
    assert "hashed_password" not in lowered


def test_conflict_and_empty_password_stay_in_spanish(client: TestClient) -> None:
    created = client.post(
        "/users",
        json={"email": "ana@nexova.test", "password": "clave-segura-1", "name": "Ana"},
    )
    assert created.status_code == 201
    again = client.post(
        "/users",
        json={"email": "ana@nexova.test", "password": "clave-segura-1"},
    )
    assert again.status_code == 409
    assert again.json()["message"] == "Ya existe una cuenta con ese correo."
    assert "traceback" not in again.text.lower()

    empty = client.post(
        "/auth/login",
        json={"email": "ana@nexova.test", "password": ""},
    )
    assert empty.status_code == 422
    assert empty.json()["message"] == "La contraseña es obligatoria."
    assert "traceback" not in empty.text.lower()


def test_login_without_a_signing_secret_hides_the_configuration(
    client: TestClient,
    monkeypatch,
) -> None:
    created = client.post(
        "/users",
        json={"email": "ana@nexova.test", "password": "clave-segura-1", "name": "Ana"},
    )
    assert created.status_code == 201
    monkeypatch.delenv("JWT_SECRET")
    denied = client.post(
        "/auth/login",
        json={"email": "ana@nexova.test", "password": "clave-segura-1"},
    )
    assert denied.status_code == 500
    assert "JWT_SECRET" not in denied.text
    assert ".env" not in denied.text
    assert "Traceback" not in denied.text
    assert "/workspace" not in denied.text
    assert "access_token" not in denied.json()
    assert denied.json()["message"] == CATALOG[500]
