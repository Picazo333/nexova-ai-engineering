"""GET /users/{id} — a person may read their own credentials; an admin may read another's."""

from __future__ import annotations

from fastapi.testclient import TestClient

from tests.auth_support import ADMIN_PASSWORD, bearer, create_admin, register, token_for


def test_happy_path_returns_the_caller_and_not_the_password(client: TestClient) -> None:
    created = register(client, "ana@nexova.test", phone="600111222", address="Gran Vía 2")
    response = client.get(
        f"/users/{created['id']}",
        headers=bearer(token_for(client, "ana@nexova.test")),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "ana@nexova.test"
    assert body["profile"]["phone"] == "600111222"
    assert body["profile"]["address"] == "Gran Vía 2"
    assert "hashed_password" not in body


def test_edge_an_admin_can_read_another_account_without_receiving_the_hash(
    client: TestClient,
) -> None:
    other = register(client, "luis@nexova.test", name="Luis")
    create_admin()
    response = client.get(
        f"/users/{other['id']}",
        headers=bearer(token_for(client, "admin@nexova.test", ADMIN_PASSWORD)),
    )
    assert response.status_code == 200
    assert response.json()["email"] == "luis@nexova.test"
    assert response.json()["profile"]["name"] == "Luis"
    assert "hashed_password" not in response.json()


def test_failure_another_user_is_forbidden_and_an_unknown_id_is_absent(
    client: TestClient,
) -> None:
    ana = register(client, "ana@nexova.test")
    luis = register(client, "luis@nexova.test", name="Luis")
    headers = bearer(token_for(client, "ana@nexova.test"))
    forbidden = client.get(f"/users/{luis['id']}", headers=headers)
    assert forbidden.status_code == 403
    assert "otro usuario" in forbidden.json()["message"]
    missing = client.get(
        "/users/00000000-0000-0000-0000-000000000000",
        headers=headers,
    )
    assert missing.status_code == 404
    assert missing.json()["message"] == "No existe un usuario con ese id."
    assert client.get(f"/users/{ana['id']}").status_code == 401
