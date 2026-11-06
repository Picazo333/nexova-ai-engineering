"""The ticket tool reads the incident manager and does not write to it."""

from pathlib import Path

from fastapi.testclient import TestClient

from app.agent.tools.tickets import HttpIncidentReader, InProcessIncidentReader
from tests.http_auth import attach_operator

ROOT = Path(__file__).resolve().parents[3]


def _incident(**overrides: str) -> dict:
    payload = {
        "title": "La caja no emite el contrato",
        "description": "El cliente no puede descargar el contrato firmado desde el portal.",
        "category": "technical_failure",
        "status": "in_progress",
        "origin": "customer",
        "branch": "central",
    }
    payload.update(overrides)
    return payload


def test_agent_reads_the_incident_created_by_the_api(client: TestClient) -> None:
    attach_operator(client)
    created = client.post("/api/incidents", json=_incident()).json()
    response = client.post(
        "/agent/query",
        json={"question": f"What is the status of ticket {created['id']}?"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["trace"]["sources"] == ["ticket_tool"]
    assert body["trace"]["route"] == "ticket"
    assert body["trace"]["ticket_transport"] == "in_process"
    assert created["status"] in body["answer"]
    assert created["id"] in body["answer"]
    again = client.get(f"/api/incidents/{created['id']}")
    assert again.status_code == 200
    assert again.json() == created
    listed = client.get("/api/incidents")
    assert [row["id"] for row in listed.json()] == [created["id"]]


def test_ticket_question_without_a_token_does_not_invent_a_status(client: TestClient) -> None:
    from incident_store import create_incident

    created = create_incident(_incident())
    response = client.post(
        "/agent/query",
        json={"question": f"What is the status of ticket {created['id']}?"},
    )
    assert response.status_code == 200
    answer = response.json()["answer"]
    assert answer.startswith("I couldn't confirm that ticket's status right now.")
    assert created["status"] not in answer
    assert client.get(f"/api/incidents/{created['id']}").status_code == 401


def test_in_process_reader_matches_the_http_record(client: TestClient) -> None:
    attach_operator(client)
    created = client.post("/api/incidents", json=_incident(status="open")).json()
    result = InProcessIncidentReader().lookup({"ticket_id": created["id"]})
    assert result["outcome"] == "found"
    assert result["tickets"] == [created]


def test_http_reader_only_issues_get(monkeypatch) -> None:
    calls: list[tuple] = []

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return b'{"id":"abc","status":"open","title":"t","description":"d","category":"other","origin":"internal","branch":"remote","created_at":"2026-01-01T00:00:00Z","updated_at":"2026-01-01T00:00:00Z"}'

    def urlopen(request, timeout):
        calls.append((request.get_method(), request.full_url, timeout, request.headers.get("Authorization")))
        return Response()

    reader = HttpIncidentReader(
        "http://incident.test",
        token="local-test-token",
        timeout=4.0,
        urlopen=urlopen,
    )
    found = reader.lookup({"ticket_id": "abc"})
    assert found["outcome"] == "found"
    assert found["tickets"][0]["status"] == "open"
    assert calls == [
        ("GET", "http://incident.test/api/incidents/abc", 4.0, "Bearer local-test-token")
    ]


def test_tool_source_has_no_write_calls() -> None:
    source = (ROOT / "services" / "api" / "app" / "agent" / "tools" / "tickets.py").read_text(encoding="utf-8")
    assert "create_incident" not in source
    assert "update_status" not in source
    assert 'method="POST"' not in source
    assert 'method="PATCH"' not in source
    assert 'method="DELETE"' not in source
    assert 'method="GET"' in source


def test_compare_page_shows_both_routes_and_the_lockup(client: TestClient, monkeypatch) -> None:
    monkeypatch.setattr("data.pipelines.rag.retrieve", lambda question, **kwargs: [])
    page = client.get("/agente")
    assert page.status_code == 200
    assert "Ruta RAG" in page.text
    assert "Ruta tool de tickets" in page.text
    assert 'src="/brand/lockups/signal-horizontal.svg"' in page.text
    assert 'src="/brand/lockups/signal-stacked.svg"' in page.text
    assert "noindex" in page.text
    assert "__RAG_STATE__" not in page.text
    assert "Todavía no hay una corrida" in page.text
    css = client.get("/agente/styles.css")
    assert css.status_code == 200
    assert "400px" in css.text
    assert "280px" in css.text

    posted = client.post(
        "/agente",
        data={"lane": "rag", "question": "What is the office wifi password?"},
    )
    assert posted.status_code == 200
    assert "route_sources" in posted.text
    assert "retrieve_context" in posted.text
    assert "lookup_ticket" not in posted.text
    assert "information about that." in posted.text


def test_compare_page_ticket_lane_uses_the_real_record(client: TestClient) -> None:
    token = attach_operator(client)
    created = client.post("/api/incidents", json=_incident()).json()
    posted = client.post(
        "/agente",
        data={"lane": "tool", "question": f"What is the status of ticket {created['id']}?"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert posted.status_code == 200
    assert "lookup_ticket" in posted.text
    assert created["status"] in posted.text
    assert "Fuentes en orden: ticket_tool." in posted.text
