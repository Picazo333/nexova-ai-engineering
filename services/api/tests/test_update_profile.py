"""PUT /profiles/me — the caller can change their own contact data only."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.auth.service import get_profile_by_user_id
from tests.auth_support import bearer, register, token_for


def test_happy_path_updates_name_phone_and_address(client: TestClient) -> None:
    created = register(client, "ana@nexova.test")
    headers = bearer(token_for(client, "ana@nexova.test"))
    response = client.put(
        "/profiles/me",
        json={"name": "Ana Soler", "phone": "600999888", "address": "Gran Vía 2"},
        headers=headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["user_id"] == created["id"]
    assert body["name"] == "Ana Soler"
    assert body["phone"] == "600999888"
    assert body["address"] == "Gran Vía 2"
    stored = get_profile_by_user_id(created["id"])
    assert stored is not None
    assert stored["phone"] == "600999888"


def test_edge_a_blank_name_clears_the_field_and_omitted_fields_stay(client: TestClient) -> None:
    created = register(client, "ana@nexova.test", phone="600111222", address="Calle Mayor 1")
    headers = bearer(token_for(client, "ana@nexova.test"))
    # A name made only of spaces is not a new name: it clears the stored one.
    response = client.put("/profiles/me", json={"name": "   "}, headers=headers)
    assert response.status_code == 200
    assert response.json()["name"] is None
    assert response.json()["phone"] == "600111222"
    assert response.json()["address"] == "Calle Mayor 1"
    stored = get_profile_by_user_id(created["id"])
    assert stored is not None
    assert stored["name"] is None
    assert stored["phone"] == "600111222"


def test_edge_contact_fields_stop_at_their_length_limit(client: TestClient) -> None:
    register(client, "ana@nexova.test")
    headers = bearer(token_for(client, "ana@nexova.test"))
    phone = client.put("/profiles/me", json={"phone": "1" * 41}, headers=headers)
    assert phone.status_code == 422
    assert "40" in phone.text
    kept = client.get("/profiles/me", headers=headers)
    assert kept.json()["phone"] is None


def test_failure_an_empty_change_and_a_missing_token_do_not_write(client: TestClient) -> None:
    created = register(client, "ana@nexova.test")
    headers = bearer(token_for(client, "ana@nexova.test"))
    empty = client.put("/profiles/me", json={}, headers=headers)
    assert empty.status_code == 422
    assert empty.json()["message"] == "No hay cambios."
    extra = client.put(
        "/profiles/me",
        json={"name": "Ana", "role": "admin"},
        headers=headers,
    )
    assert extra.status_code == 422
    assert get_profile_by_user_id(created["id"])["name"] == "Ana Soler"
    missing = client.put("/profiles/me", json={"name": "Intruso"})
    assert missing.status_code == 401
    assert get_profile_by_user_id(created["id"])["name"] == "Ana Soler"
