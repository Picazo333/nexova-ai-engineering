"""HTTP contract of the centralized incident manager."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from tests.http_auth import attach_operator

BRANCH_LABELS = (
    "Central — Sede Valencia",
    "Valencia — Operaciones",
    "Miami Office",
    "Remoto (empleado sin sede fija)",
)


def _incident(**overrides: str) -> dict:
    payload = {
        "title": "La caja no emite el contrato",
        "description": "El cliente no puede descargar el contrato firmado desde el portal.",
        "category": "technical_failure",
        "status": "open",
        "origin": "customer",
        "branch": "central",
    }
    payload.update(overrides)
    return payload


def test_create_list_detail_and_summary(client: TestClient) -> None:
    attach_operator(client)
    empty = client.get("/api/incidents")
    assert empty.status_code == 200
    assert empty.json() == []
    zeroes = client.get("/api/incidents/summary")
    assert zeroes.status_code == 200
    body = zeroes.json()
    assert body["total"] == 0
    assert body["by_status"]["open"] == 0
    assert body["by_category"]["sla_breach"] == 0
    assert body["by_branch"]["remote"] == 0
    assert body["by_origin"]["internal"] == 0

    created = client.post("/api/incidents", json=_incident())
    assert created.status_code == 201
    stored = created.json()
    assert set(stored) == {
        "id",
        "title",
        "description",
        "category",
        "status",
        "origin",
        "branch",
        "created_at",
        "updated_at",
    }
    assert "source_key" not in stored
    detail = client.get(f"/api/incidents/{stored['id']}")
    assert detail.status_code == 200
    assert detail.json()["title"] == stored["title"]
    missing = client.get("/api/incidents/no-existe")
    assert missing.status_code == 404
    assert missing.json()["message"] == "No encontramos esa incidencia."
    assert "Traceback" not in missing.text


def test_validation_names_the_field_in_spanish(client: TestClient) -> None:
    attach_operator(client)
    rejected = client.post("/api/incidents", json={})
    assert rejected.status_code == 400
    body = rejected.json()
    assert body["field"] == "title"
    assert "título" in body["message"].lower() or "titulo" in body["message"].lower()
    fields = {item["field"] for item in body["errors"]}
    assert {"title", "description", "category", "status", "origin", "branch"} <= fields
    bad = client.post("/api/incidents", json=_incident(category="TECHNICAL", branch="hq"))
    assert bad.status_code == 400
    assert bad.json()["field"] == "category"
    assert "technical_failure" in bad.json()["message"]
    broken = client.post(
        "/api/incidents",
        content=b"[]",
        headers={"Content-Type": "application/json"},
    )
    assert broken.status_code == 400
    assert broken.json()["message"] == "El cuerpo tiene que ser un objeto JSON."
    filtered = client.get("/api/incidents", params={"status": "CLOSED"})
    assert filtered.status_code == 400
    assert filtered.json()["field"] == "status"


def test_status_lifecycle_and_filters(client: TestClient) -> None:
    attach_operator(client)
    first = client.post("/api/incidents", json=_incident(branch="miami_office")).json()
    second = client.post(
        "/api/incidents",
        json=_incident(
            title="Queja por el SLA de selección",
            description="El cliente dice que la terna llegó fuera de plazo.",
            category="sla_breach",
            origin="branch",
            branch="valencia_operations",
            status="in_progress",
        ),
    ).json()
    skipped = client.patch(f"/api/incidents/{first['id']}/status", json={"status": "resolved"})
    assert skipped.status_code == 400
    assert skipped.json()["field"] == "status"
    assert client.get(f"/api/incidents/{first['id']}").json()["status"] == "open"
    moved = client.patch(f"/api/incidents/{first['id']}/status", json={"status": "in_progress"})
    assert moved.status_code == 200
    resolved = client.patch(f"/api/incidents/{first['id']}/status", json={"status": "resolved"})
    assert resolved.status_code == 200
    final = client.patch(f"/api/incidents/{first['id']}/status", json={"status": "open"})
    assert final.status_code == 400
    assert client.get(f"/api/incidents/{first['id']}").json()["status"] == "resolved"

    combined = client.get(
        "/api/incidents",
        params={"origin": "branch", "branch": "valencia_operations", "category": "sla_breach", "status": "in_progress"},
    )
    assert combined.status_code == 200
    rows = combined.json()
    assert [row["id"] for row in rows] == [second["id"]]
    assert client.get("/api/incidents", params={"branch": "remote"}).json() == []


def test_pages_expose_the_form_the_menu_and_branch_labels(client: TestClient) -> None:
    page = client.get("/incidencias/nueva")
    assert page.status_code == 200
    assert "<h1>Registrar una incidencia</h1>" in page.text
    assert 'href="/incidencias/nueva"' in page.text
    assert 'href="/incidencias"' in page.text
    for label in BRANCH_LABELS:
        assert label in page.text
    assert 'id="branch-field"' in page.text
    assert "signal-horizontal.svg" in page.text
    locked = client.get("/incidencias")
    assert locked.status_code == 200
    assert "Hace falta una sesión" in locked.text
    assert "Reintentar" in locked.text

    attach_operator(client)
    client.post("/api/incidents", json=_incident(title="<script>alert(1)</script>"))
    panel = client.get("/incidencias")
    assert panel.status_code == 200
    assert "Total de incidencias: 1." in panel.text
    assert "<script>alert" not in panel.text
    assert "&lt;script&gt;" in panel.text
    assert "Por categoría" in panel.text
    assert "sla_breach" in panel.text

    client.headers.pop("Authorization", None)
    kept = client.post("/incidencias/nueva", data={"title": "Se conserva", "description": ""})
    assert kept.status_code == 401
    assert "Se conserva" in kept.text
    assert "Hace falta una sesión" in kept.text


def test_internal_error_does_not_return_the_exception(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("JWT_SECRET", "test-jwt-secret-local-only")
    monkeypatch.setenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    monkeypatch.setenv("AUTH_BCRYPT_ROUNDS", "4")
    monkeypatch.setenv("AUTH_DATA_DIR", str(tmp_path / "auth"))
    monkeypatch.setenv("SUPPLIERS_DATA_DIR", str(tmp_path / "suppliers"))
    monkeypatch.setenv("SUPPLIERS_AUTOSEED", "0")
    monkeypatch.setenv("INCIDENTS_DATA_DIR", str(tmp_path / "incidents"))
    from app.auth.store import reset_auth_db
    from app.main import create_app
    from incident_store import reset_incidents_db

    reset_auth_db()
    reset_incidents_db()
    application = create_app()

    import app.routers.incident_records as records

    def boom(*_args, **_kwargs):
        raise RuntimeError("secret-sentinel Traceback line")

    records.list_incidents = boom
    with TestClient(application, raise_server_exceptions=False) as test_client:
        attach_operator(test_client)
        response = test_client.get("/api/incidents", headers={"Accept": "application/json"})
    assert response.status_code == 500
    assert response.json()["error"] == "internal_error"
    assert "secret-sentinel" not in response.text
    assert "Traceback" not in response.text
    reset_incidents_db()
    reset_auth_db()
