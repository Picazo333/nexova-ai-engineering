"""API-042 — incident analysis decisions. Not the auth module."""

from __future__ import annotations

from fastapi.testclient import TestClient

from incident_analysis.engine import AnalysisError, analyze_bytes
from tests.http_auth import attach_operator

HEADER = (
    "ticket_id,date,client_company,category,description,agent_id,status,"
    "customer_email,satisfaction_score"
)


def _row(**overrides: str) -> str:
    base = {
        "ticket_id": "NXV-000001",
        "date": "2024-01-18",
        "client_company": "FinServ Group",
        "category": "ACCESS",
        "description": "Role permissions not updated",
        "agent_id": "AGT-08",
        "status": "CLOSED",
        "customer_email": "person@example.com",
        "satisfaction_score": "4",
    }
    base.update(overrides)
    return ",".join(base[name] for name in base)


def _csv(*rows: str) -> bytes:
    return (HEADER + "\n" + "\n".join(rows) + "\n").encode("utf-8")


def test_happy_path_counts_a_closed_ticket_and_drops_the_email(client: TestClient) -> None:
    attach_operator(client)
    payload = _csv(_row())
    response = client.post(
        "/api/incidents/analyze",
        files={"file": ("tickets.csv", payload, "text/csv")},
        headers={"Accept": "application/json"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["total_records"] == 1
    assert body["valid_records"] == 1
    assert body["invalid_records"] == 0
    assert body["satisfaction"]["average"] == "4.00"
    # The report decides the counts. It does not decide to keep the customer's email.
    assert "person@example.com" not in response.text
    report = analyze_bytes(payload, "tickets.csv")
    assert report.valid_records == 1
    assert report.satisfaction_average == "4.00"


def test_edge_five_characters_count_and_four_do_not(client: TestClient) -> None:
    attach_operator(client)
    payload = _csv(
        _row(description="1234", ticket_id="NXV-000031", satisfaction_score="1"),
        _row(description="12345", ticket_id="NXV-000032", satisfaction_score="5"),
    )
    response = client.post(
        "/api/incidents/analyze",
        files={"file": ("boundary.csv", payload, "text/csv")},
        headers={"Accept": "application/json"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["valid_records"] == 1
    assert body["invalid_records"] == 1
    # The open ticket's score is not part of the average. Only the closed 5 counts.
    opened = _csv(
        _row(status="OPEN", satisfaction_score="1", ticket_id="NXV-000021"),
        _row(status="CLOSED", satisfaction_score="5", ticket_id="NXV-000022"),
    )
    report = analyze_bytes(opened, "scores.csv")
    assert report.scored_records == 1
    assert report.satisfaction_average == "5.00"


def test_failure_missing_empty_and_export_without_an_analysis(client: TestClient) -> None:
    attach_operator(client)
    missing = client.post("/api/incidents/analyze", headers={"Accept": "application/json"})
    assert missing.status_code == 400
    assert missing.json()["error"] == "missing_file"
    empty = client.post(
        "/api/incidents/analyze",
        files={"file": ("empty.csv", b"", "text/csv")},
        headers={"Accept": "application/json"},
    )
    assert empty.status_code == 400
    assert empty.json()["error"] == "empty_file"
    export = client.get("/api/incidents/results/export", headers={"Accept": "application/json"})
    assert export.status_code == 404
    assert export.json()["error"] == "no_analysis"
    try:
        analyze_bytes(b"", "empty.csv")
    except AnalysisError as exc:
        assert exc.code == "empty_file"
    else:
        raise AssertionError("an empty file is not an analysis")
