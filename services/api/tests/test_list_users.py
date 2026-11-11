"""GET /users — who appears in the directory, and in which order."""

from __future__ import annotations

from fastapi.testclient import TestClient
from tinydb import Query

from app.auth.service import list_users
from app.auth.store import auth_lock, users_table
from tests.auth_support import bearer, register, token_for


def test_happy_path_lists_accounts_by_creation_without_the_password(client: TestClient) -> None:
    first = register(client, "ana@nexova.test", name="Ana")
    second = register(client, "luis@nexova.test", name="Luis")
    # Force an order the clock cannot tie: Luis was stored first.
    with auth_lock():
        users_table().update(
            {"created_at": "2000-01-01T00:00:00+00:00"},
            Query().id == second["id"],
        )
    response = client.get("/users", headers=bearer(token_for(client, "ana@nexova.test")))
    assert response.status_code == 200
    rows = response.json()
    assert [row["email"] for row in rows] == ["luis@nexova.test", "ana@nexova.test"]
    assert all("hashed_password" not in row for row in rows)
    assert rows[1]["id"] == first["id"]
    assert rows[0]["role"] == "user"


def test_edge_a_single_account_is_the_whole_list(client: TestClient) -> None:
    created = register(client, "ana@nexova.test")
    response = client.get("/users", headers=bearer(token_for(client, "ana@nexova.test")))
    assert response.status_code == 200
    assert [row["id"] for row in response.json()] == [created["id"]]
    assert list_users()[0]["email"] == "ana@nexova.test"


def test_edge_the_service_list_is_empty_before_anyone_registers() -> None:
    assert list_users() == []


def test_failure_without_a_token_the_directory_stays_closed(client: TestClient) -> None:
    register(client, "ana@nexova.test")
    response = client.get("/users")
    assert response.status_code == 401
    assert response.json()["message"] == "Falta el token de acceso."
