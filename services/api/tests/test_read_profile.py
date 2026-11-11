"""GET /profiles/me — the profile that belongs to the token, nothing else."""

from __future__ import annotations

from fastapi.testclient import TestClient

from tests.auth_support import bearer, register, token_for


def test_happy_path_returns_the_contact_fields_stored_at_registration(
    client: TestClient,
) -> None:
    created = register(
        client,
        "ana@nexova.test",
        phone="600111222",
        address="Calle de Colón 1",
    )
    response = client.get("/profiles/me", headers=bearer(token_for(client, "ana@nexova.test")))
    assert response.status_code == 200
    body = response.json()
    assert body["user_id"] == created["id"]
    assert body["name"] == "Ana Soler"
    assert body["phone"] == "600111222"
    assert body["address"] == "Calle de Colón 1"
    assert "email" not in body
    assert "hashed_password" not in body


def test_edge_a_profile_without_contact_data_returns_empty_fields(client: TestClient) -> None:
    created = register(client, "ana@nexova.test", name=None)
    response = client.get("/profiles/me", headers=bearer(token_for(client, "ana@nexova.test")))
    assert response.status_code == 200
    body = response.json()
    assert body["user_id"] == created["id"]
    assert body["name"] is None
    assert body["phone"] is None
    assert body["address"] is None


def test_failure_missing_and_malformed_tokens_do_not_reveal_a_profile(client: TestClient) -> None:
    register(client, "ana@nexova.test", phone="600111222")
    missing = client.get("/profiles/me")
    assert missing.status_code == 401
    assert missing.json()["message"] == "Falta el token de acceso."
    # A refused request must not leak the profile, not even in the error body.
    assert "600111222" not in missing.text
    malformed = client.get("/profiles/me", headers={"Authorization": "Bearer no-es-jwt"})
    assert malformed.status_code == 401
    assert "Ana Soler" not in malformed.text
