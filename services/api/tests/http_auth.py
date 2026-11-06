"""Attach a real JWT to a TestClient without changing the assertion under test."""

from __future__ import annotations

from fastapi.testclient import TestClient

OPERATOR_EMAIL = "operador@nexova.test"
OPERATOR_PASSWORD = "clave-segura-1"


def attach_operator(
    client: TestClient,
    *,
    email: str = OPERATOR_EMAIL,
    password: str = OPERATOR_PASSWORD,
    name: str = "Operador Nexova",
) -> str:
    created = client.post(
        "/users",
        json={"email": email, "password": password, "name": name},
    )
    if created.status_code not in (201, 409):
        raise AssertionError(created.text)
    logged = client.post("/auth/login", json={"email": email, "password": password})
    if logged.status_code != 200:
        raise AssertionError(logged.text)
    token = logged.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    return token
