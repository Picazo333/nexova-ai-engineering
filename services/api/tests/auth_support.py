"""Shared setup for auth tests.

The password and the signing secret are local fixtures. They are not accounts
and they are not read from the environment of a real deployment.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

PASSWORD = "clave-segura-1"
ADMIN_PASSWORD = "clave-admin-1"


def register(
    client: TestClient,
    email: str,
    name: str | None = "Ana Soler",
    **extra: object,
) -> dict:
    body: dict[str, object] = {"email": email, "password": PASSWORD}
    if name is not None:
        body["name"] = name
    body.update(extra)
    response = client.post("/users", json=body)
    assert response.status_code == 201, response.text
    return response.json()


def login(client: TestClient, email: str, password: str = PASSWORD) -> dict:
    response = client.post("/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200, response.text
    return response.json()


def token_for(client: TestClient, email: str, password: str = PASSWORD) -> str:
    return login(client, email, password)["access_token"]


def bearer(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def create_admin(email: str = "admin@nexova.test") -> dict:
    """The public register route cannot choose a role, so the admin is stored directly."""
    from app.auth.service import create_user

    return create_user(email=email, password=ADMIN_PASSWORD, role="admin", name="Admin Nexova")
