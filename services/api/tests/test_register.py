"""POST /users — the registration decision: who is stored, and who is refused."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.auth.models import UserCreate
from app.auth.service import ServiceError, create_user, get_user_by_email
from tests.auth_support import PASSWORD, register


def test_happy_path_stores_a_user_role_and_keeps_the_password_out_of_the_response(
    client: TestClient,
) -> None:
    created = register(
        client,
        "ana@nexova.test",
        phone="+34 600 000 001",
        address="Calle Mayor 1",
    )
    assert created["role"] == "user"
    assert created["is_active"] is True
    assert created["profile"]["name"] == "Ana Soler"
    assert created["profile"]["user_id"] == created["id"]
    assert created["profile"]["phone"] == "+34 600 000 001"
    assert "hashed_password" not in created
    # The plain password must not appear anywhere in the response, not even nested.
    assert PASSWORD not in str(created)

    stored = get_user_by_email("ana@nexova.test")
    assert stored is not None
    # What is stored is a bcrypt hash ($2...), never the password itself.
    assert stored["hashed_password"] != PASSWORD
    assert stored["hashed_password"].startswith("$2")
    assert "name" not in stored


def test_edge_blank_contact_fields_are_stored_as_empty_and_email_is_normalized(
    client: TestClient,
) -> None:
    # Spaces around the address are not a second address: the profile keeps nothing.
    created = register(
        client,
        "  ANA@Nexova.test  ",
        name="   ",
        phone="",
        address="   ",
    )
    assert created["email"] == "ana@nexova.test"
    assert created["profile"]["name"] is None
    assert created["profile"]["phone"] is None
    assert created["profile"]["address"] is None
    assert get_user_by_email("ana@nexova.test") is not None


def test_edge_password_of_eight_characters_is_the_shortest_accepted(client: TestClient) -> None:
    response = client.post(
        "/users",
        json={"email": "ocho@nexova.test", "password": "12345678", "name": "Ocho"},
    )
    assert response.status_code == 201
    assert response.json()["email"] == "ocho@nexova.test"
    seven = client.post(
        "/users",
        json={"email": "siete@nexova.test", "password": "1234567"},
    )
    assert seven.status_code == 422
    assert "8 caracteres" in seven.text
    # A refused registration must not leave a half-created account behind.
    assert get_user_by_email("siete@nexova.test") is None


def test_failure_duplicate_email_reports_the_conflict_and_does_not_create_another(
    client: TestClient,
) -> None:
    register(client, "ana@nexova.test")
    again = client.post(
        "/users",
        json={"email": "Ana@nexova.test", "password": PASSWORD, "name": "Otra"},
    )
    # The decision is the conflict sentence, not a generic 409 wrapper.
    assert again.status_code == 409
    assert again.json()["message"] == "Ya existe una cuenta con ese correo."
    assert get_user_by_email("ana@nexova.test") is not None


def test_failure_malformed_email_and_edged_password_are_refused(client: TestClient) -> None:
    missing_domain = client.post(
        "/users",
        json={"email": "ana-nexova.test", "password": PASSWORD},
    )
    assert missing_domain.status_code == 422
    spaced = client.post(
        "/users",
        json={"email": "borde@nexova.test", "password": " clave-segura-1"},
    )
    assert spaced.status_code == 422
    assert "sin espacios al borde" in spaced.text
    # The 422 is not enough: the account must not exist after the refusal.
    assert get_user_by_email("borde@nexova.test") is None
    empty = client.post("/users", json={"email": "vacio@nexova.test", "password": ""})
    assert empty.status_code == 422
    assert get_user_by_email("vacio@nexova.test") is None


def test_failure_registration_cannot_choose_a_role(client: TestClient) -> None:
    rejected = client.post(
        "/users",
        json={"email": "admin-hope@nexova.test", "password": PASSWORD, "role": "admin"},
    )
    assert rejected.status_code == 422
    # The role field is refused and nothing is stored. The service enforces the same list below.
    assert get_user_by_email("admin-hope@nexova.test") is None
    with pytest.raises(ValidationError):
        UserCreate.model_validate(
            {"email": "admin-hope@nexova.test", "password": PASSWORD, "role": "admin"}
        )
    with pytest.raises(ServiceError) as caught:
        create_user(email="owner@nexova.test", password=PASSWORD, role="owner")
    assert caught.value.status_code == 422
    assert caught.value.message == "El rol solo puede ser admin, manager o user."
    assert get_user_by_email("owner@nexova.test") is None
