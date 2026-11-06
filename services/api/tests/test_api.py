"""HTTP contract for the incidents API and the backoffice pages."""

from __future__ import annotations

import csv
import io
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[3]
OFFICIAL = ROOT / "scripts" / "incidents-nexova.csv"


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("INCIDENTS_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("INCIDENTS_MAX_UPLOAD_BYTES", "1048576")
    from app.infrastructure.analysis_store import reset_store
    from app.main import create_app

    reset_store(tmp_path)
    application = create_app()
    with TestClient(application) as test_client:
        yield test_client


def _emails() -> set[str]:
    found = set()
    with OFFICIAL.open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            email = (row.get("customer_email") or "").strip()
            if email:
                found.add(email)
    return found


def _assert_no_email(text: str) -> None:
    leaked = [email for email in _emails() if email in text]
    assert not leaked, "customer email appeared in an HTTP response"


def test_analyze_json_matches_briefing(client: TestClient) -> None:
    response = client.post(
        "/api/incidents/analyze",
        files={"file": ("incidents-nexova.csv", OFFICIAL.read_bytes(), "text/csv")},
        headers={"Accept": "application/json"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["total_records"] == 100
    assert body["valid_records"] == 96
    assert body["invalid_records"] == 4
    assert body["satisfaction"]["average"] == "3.84"
    assert body["categories"][0]["code"] == "TECHNICAL"
    assert body["categories"][0]["count"] == 28
    _assert_no_email(response.text)
    assert "@" not in response.text


def test_fragment_and_full_page_show_the_same_figures(client: TestClient) -> None:
    files = {"file": ("incidents-nexova.csv", OFFICIAL.read_bytes(), "text/csv")}
    fragment = client.post(
        "/api/incidents/analyze",
        files=files,
        headers={"Accept": "text/html", "X-Report-Fragment": "1"},
    )
    page = client.post(
        "/api/incidents/analyze",
        files=files,
        headers={"Accept": "text/html"},
    )
    assert fragment.status_code == 200
    assert page.status_code == 200
    assert "text/html" in fragment.headers["content-type"]
    for body in (fragment.text, page.text):
        assert "3.84" in body
        assert "NXV-000017" in body
        assert "Vista previa del CSV" in body
        assert "Falta client_company" in body
        _assert_no_email(body)
        assert "@" not in body
    assert "<h1>Análisis de incidencias de soporte</h1>" in page.text


def test_export_after_analyze_is_the_csv(client: TestClient) -> None:
    missing = client.get("/api/incidents/results/export", headers={"Accept": "application/json"})
    assert missing.status_code == 404
    assert missing.json()["error"] == "no_analysis"
    uploaded = client.post(
        "/api/incidents/analyze",
        files={"file": ("incidents-nexova.csv", OFFICIAL.read_bytes(), "text/csv")},
        headers={"Accept": "application/json"},
    )
    assert uploaded.status_code == 200
    exported = client.get("/api/incidents/results/export")
    assert exported.status_code == 200
    assert "text/csv" in exported.headers["content-type"]
    assert "results.csv" in exported.headers["content-disposition"]
    rows = list(csv.DictReader(io.StringIO(exported.text)))
    metrics = {row["metric"]: row["value"] for row in rows}
    assert metrics["valid_records"] == "96"
    assert metrics["satisfaction_average"] == "3.84"
    assert len(rows) == len(uploaded.json()["export_rows"])
    _assert_no_email(exported.text)


def test_input_errors_use_client_status_codes(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    empty = client.post(
        "/api/incidents/analyze",
        files={"file": ("empty.csv", b"", "text/csv")},
        headers={"Accept": "application/json"},
    )
    assert empty.status_code == 400
    assert empty.json()["error"] == "empty_file"
    assert "vacío" in empty.json()["message"]
    missing = client.post("/api/incidents/analyze", headers={"Accept": "application/json"})
    assert missing.status_code == 400
    assert missing.json()["error"] == "missing_file"
    header_only = (
        "ticket_id,date,client_company,category,description,agent_id,status,"
        "customer_email,satisfaction_score\n"
    ).encode()
    no_rows = client.post(
        "/api/incidents/analyze",
        files={"file": ("only-header.csv", header_only, "text/csv")},
        headers={"Accept": "application/json"},
    )
    assert no_rows.status_code == 400
    assert no_rows.json()["error"] == "empty_records"
    monkeypatch.setenv("INCIDENTS_MAX_UPLOAD_BYTES", "8")
    huge = client.post(
        "/api/incidents/analyze",
        files={"file": ("big.csv", b"0123456789", "text/csv")},
        headers={"Accept": "application/json"},
    )
    assert huge.status_code == 413
    html_error = client.post(
        "/api/incidents/analyze",
        files={"file": ("empty.csv", b" ", "text/csv")},
        headers={"Accept": "text/html"},
    )
    assert html_error.status_code == 400
    assert "El fichero está vacío." in html_error.text
    assert "No se pudo analizar" in html_error.text


def test_pages_statuses_and_static_lockup(client: TestClient) -> None:
    home = client.get("/")
    assert home.status_code == 200
    assert "Analizar fichero" in home.text
    assert 'action="/api/incidents/analyze"' in home.text
    assert "signal-horizontal.svg" in home.text
    assert "signal-stacked.svg" in home.text
    privacy = client.get("/privacidad")
    assert privacy.status_code == 200
    assert "no una política legal" in privacy.text
    missing = client.get("/no/existe/ruta")
    assert missing.status_code == 404
    assert "No encontramos esa ruta" in missing.text
    assert "/no/existe/ruta" in missing.text
    escaped = client.get("/no/<script>")
    assert escaped.status_code == 404
    assert "<script>" not in escaped.text
    assert "&lt;script&gt;" in escaped.text
    api_missing = client.get("/api/incidents/no-existe", headers={"Accept": "application/json"})
    assert api_missing.status_code == 404
    assert api_missing.json()["message"] == "No encontrado."
    lockup = client.get("/brand/lockups/signal-horizontal.svg")
    assert lockup.status_code == 200
    assert lockup.content.startswith(b"<svg") or lockup.content.startswith(b"<?xml") or b"<svg" in lockup.content[:200]


def test_server_error_hides_exception_text(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("INCIDENTS_DATA_DIR", str(tmp_path))
    from app.infrastructure.analysis_store import reset_store
    from app.main import create_app

    reset_store(tmp_path)
    application = create_app()

    @application.get("/_boom")
    def boom() -> None:
        raise RuntimeError("secret-sentinel@example.com")

    @application.get("/api/_boom")
    def api_boom() -> None:
        raise RuntimeError("secret-sentinel@example.com")

    with TestClient(application, raise_server_exceptions=False) as test_client:
        page = test_client.get("/_boom")
        api = test_client.get("/api/_boom", headers={"Accept": "application/json"})
    assert page.status_code == 500
    assert "secret-sentinel" not in page.text
    assert "Traceback" not in page.text
    assert "No se pudo completar" in page.text
    assert api.status_code == 500
    assert "secret-sentinel" not in api.text
    assert api.json()["error"] == "internal_error"


def test_saved_analysis_has_no_email(client: TestClient, tmp_path: Path) -> None:
    response = client.post(
        "/api/incidents/analyze",
        files={"file": ("incidents-nexova.csv", OFFICIAL.read_bytes(), "text/csv")},
        headers={"Accept": "application/json"},
    )
    assert response.status_code == 200
    saved = json.loads((tmp_path / "last_analysis.json").read_text(encoding="utf-8"))
    assert "@" not in json.dumps(saved)
    _assert_no_email(json.dumps(saved))
