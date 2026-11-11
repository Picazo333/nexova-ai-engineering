"""PUT /users/{id} — which credential changes are allowed."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.auth.service import get_user_by_email
from tests.auth_support import ADMIN_PASSWORD, PASSWORD, bearer, create_admin, register, token_for


def test_happy_path_replaces_the_email_and_the_password(client: TestClient) -> None:
    created = register(client, "ana@nexova.test")
    headers = bearer(token_for(client, "ana@nexova.test"))
    updated = client.put(
        f"/users/{created['id']}",
        json={"email": "ana.soler@nexova.test", "password": "clave-nueva-2"},
        headers=headers,
    )
    assert updated.status_code == 200
    assert updated.json()["email"] == "ana.soler@nexova.test"
    assert "hashed_password" not in updated.json()
    # The new password is never echoed back in the response body.
    assert "clave-nueva-2" not in updated.text
    # Proof that the password changed: the old one no longer opens a session.
    old = client.post(
        "/auth/login",
        json={"email": "ana.soler@nexova.test", "password": PASSWORD},
    )
    assert old.status_code == 401
    new = client.post(
        "/auth/login",
        json={"email": "ana.soler@nexova.test", "password": "clave-nueva-2"},
    )
    assert new.status_code == 200
    stored = get_user_by_email("ana.soler@nexova.test")
    assert stored is not None
    # What is stored is a hash, not the new plain password.
    assert stored["hashed_password"] != "clave-nueva-2"


def test_edge_the_same_email_is_not_a_conflict_and_an_empty_change_is_refused(
    client: TestClient,
) -> None:
    created = register(client, "ana@nexova.test")
    headers = bearer(token_for(client, "ana@nexova.test"))
    same = client.put(
        f"/users/{created['id']}",
        json={"email": "Ana@nexova.test"},
        headers=headers,
    )
    assert same.status_code == 200
    assert same.json()["email"] == "ana@nexova.test"
    empty = client.put(f"/users/{created['id']}", json={}, headers=headers)
    assert empty.status_code == 422
    assert empty.json()["message"] == "No hay cambios."


def test_edge_eight_character_password_replaces_the_previous_one(client: TestClient) -> None:
    created = register(client, "ana@nexova.test")
    headers = bearer(token_for(client, "ana@nexova.test"))
    updated = client.put(
        f"/users/{created['id']}",
        json={"password": "12345678"},
        headers=headers,
    )
    assert updated.status_code == 200
    # Eight characters is the minimum, so the new password must open a session.
    logged = client.post(
        "/auth/login",
        json={"email": "ana@nexova.test", "password": "12345678"},
    )
    assert logged.status_code == 200


def test_failure_role_active_flag_and_other_people_are_blocked(client: TestClient) -> None:
    ana = register(client, "ana@nexova.test")
    luis = register(client, "luis@nexova.test", name="Luis")
    headers = bearer(token_for(client, "ana@nexova.test"))
    role = client.put(f"/users/{ana['id']}", json={"role": "manager"}, headers=headers)
    assert role.status_code == 403
    assert role.json()["message"] == "Solo un admin puede cambiar el rol."
    active = client.put(f"/users/{ana['id']}", json={"is_active": False}, headers=headers)
    assert active.status_code == 403
    assert "desactivar" in active.json()["message"]
    other = client.put(
        f"/users/{luis['id']}",
        json={"email": "otro@nexova.test"},
        headers=headers,
    )
    assert other.status_code == 403
    # The 403 wrote nothing: Luis keeps his email and no account took the new one.
    assert get_user_by_email("luis@nexova.test") is not None
    assert get_user_by_email("otro@nexova.test") is None
    short = client.put(
        f"/users/{ana['id']}",
        json={"password": "corta"},
        headers=headers,
    )
    assert short.status_code == 422
    # The short password was refused, so the original one still logs in.
    still = client.post(
        "/auth/login",
        json={"email": "ana@nexova.test", "password": PASSWORD},
    )
    assert still.status_code == 200


def test_failure_a_taken_email_is_a_conflict_and_an_admin_can_change_the_role(
    client: TestClient,
) -> None:
    ana = register(client, "ana@nexova.test")
    luis = register(client, "luis@nexova.test", name="Luis")
    headers = bearer(token_for(client, "ana@nexova.test"))
    taken = client.put(
        f"/users/{ana['id']}",
        json={"email": "luis@nexova.test"},
        headers=headers,
    )
    assert taken.status_code == 409
    assert taken.json()["message"] == "Ya existe una cuenta con ese correo."
    create_admin()
    admin = bearer(token_for(client, "admin@nexova.test", ADMIN_PASSWORD))
    promoted = client.put(f"/users/{luis['id']}", json={"role": "manager"}, headers=admin)
    assert promoted.status_code == 200
    assert promoted.json()["role"] == "manager"
    assert promoted.json()["profile"]["name"] == "Luis"
    unknown = client.put(
        "/users/00000000-0000-0000-0000-000000000000",
        json={"email": "nuevo@nexova.test"},
        headers=admin,
    )
    assert unknown.status_code == 404
