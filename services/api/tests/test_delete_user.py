"""DELETE /users/{id} — the account and its profile leave together."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.auth.service import get_profile_by_user_id, get_user_by_email
from tests.auth_support import ADMIN_PASSWORD, PASSWORD, bearer, create_admin, register, token_for


def test_happy_path_removes_the_account_and_the_profile(client: TestClient) -> None:
    created = register(client, "ana@nexova.test")
    headers = bearer(token_for(client, "ana@nexova.test"))
    removed = client.delete(f"/users/{created['id']}", headers=headers)
    assert removed.status_code == 200
    assert removed.json()["email"] == "ana@nexova.test"
    assert "hashed_password" not in removed.json()
    assert get_user_by_email("ana@nexova.test") is None
    assert get_profile_by_user_id(created["id"]) is None
    # The account is gone, so its credentials no longer open a session.
    refused = client.post(
        "/auth/login",
        json={"email": "ana@nexova.test", "password": PASSWORD},
    )
    assert refused.status_code == 401


def test_edge_an_admin_can_remove_someone_else_and_keep_their_own_session(
    client: TestClient,
) -> None:
    other = register(client, "luis@nexova.test", name="Luis")
    create_admin()
    admin_token = token_for(client, "admin@nexova.test", ADMIN_PASSWORD)
    removed = client.delete(f"/users/{other['id']}", headers=bearer(admin_token))
    assert removed.status_code == 200
    assert removed.json()["id"] == other["id"]
    assert get_profile_by_user_id(other["id"]) is None
    # Deleting someone else must not end the admin's own session.
    still = client.get("/auth/me", headers=bearer(admin_token))
    assert still.status_code == 200
    assert still.json()["email"] == "admin@nexova.test"


def test_failure_another_user_cannot_delete_the_account_and_an_unknown_id_is_absent(
    client: TestClient,
) -> None:
    register(client, "ana@nexova.test")
    luis = register(client, "luis@nexova.test", name="Luis")
    headers = bearer(token_for(client, "ana@nexova.test"))
    forbidden = client.delete(f"/users/{luis['id']}", headers=headers)
    assert forbidden.status_code == 403
    # The 403 is a refusal, not a partial delete: Luis is still stored.
    assert get_user_by_email("luis@nexova.test") is not None
    missing = client.delete(
        "/users/00000000-0000-0000-0000-000000000000",
        headers=headers,
    )
    assert missing.status_code == 404
    assert missing.json()["message"] == "No existe un usuario con ese id."
    assert client.delete(f"/users/{luis['id']}").status_code == 401
