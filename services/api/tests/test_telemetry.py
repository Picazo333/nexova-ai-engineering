"""Stub POST /telemetry/events. It validates the envelope and stores nothing."""

import json
import logging
from pathlib import Path

from fastapi.testclient import TestClient

from app.config import telemetry_endpoint
from app.inventory.service import cost_variance_ratio, median_unit_cost

ROOT = Path(__file__).resolve().parents[3]
VALID = ROOT / "docs" / "telemetry" / "examples" / "valid" / "login_succeeded.json"


def test_telemetry_endpoint_is_read_from_the_environment(monkeypatch) -> None:
    monkeypatch.setenv("TELEMETRY_ENDPOINT", "http://localhost:8000/telemetry/events")
    assert telemetry_endpoint() == "http://localhost:8000/telemetry/events"
    monkeypatch.setenv("TELEMETRY_ENDPOINT", "")
    assert telemetry_endpoint() == ""


def test_stub_accepts_a_batch_and_returns_the_count(client: TestClient, caplog) -> None:
    event = json.loads(VALID.read_text(encoding="utf-8"))
    with caplog.at_level(logging.INFO, logger="nexova.telemetry"):
        response = client.post("/telemetry/events", json={"events": [event, event]})
    assert response.status_code == 200
    assert response.json() == {"received": 2}
    assert "received=2" in caplog.text
    assert "login_succeeded" in caplog.text
    assert "access_token" not in response.text


def test_stub_accepts_text_plain_beacon_body(client: TestClient) -> None:
    event = json.loads(VALID.read_text(encoding="utf-8"))
    response = client.post(
        "/telemetry/events",
        content=json.dumps({"events": [event]}),
        headers={"Content-Type": "text/plain;charset=UTF-8"},
    )
    assert response.status_code == 200
    assert response.json() == {"received": 1}


def test_stub_rejects_a_broken_envelope(client: TestClient) -> None:
    response = client.post(
        "/telemetry/events",
        json={"events": [{"event_type": "login_succeeded"}]},
    )
    assert response.status_code == 422
    body = response.json()
    assert body["detail"] == "El lote no tiene el formato de telemetría."
    assert "password" not in response.text


def test_stub_rejects_an_unknown_event_type(client: TestClient) -> None:
    event = json.loads(VALID.read_text(encoding="utf-8"))
    event["event_type"] = "page_view"
    response = client.post("/telemetry/events", json={"events": [event]})
    assert response.status_code == 422


def test_empty_batch_is_received_as_zero(client: TestClient) -> None:
    response = client.post("/telemetry/events", json={"events": []})
    assert response.status_code == 200
    assert response.json() == {"received": 0}


def test_web_vital_recorded_is_accepted_and_a_bad_one_is_rejected(client: TestClient) -> None:
    vital = json.loads((ROOT / "docs" / "telemetry" / "examples" / "valid" / "web_vital_recorded.json").read_text())
    accepted = client.post("/telemetry/events", json={"events": [vital]})
    assert accepted.status_code == 200, accepted.text
    assert accepted.json() == {"received": 1}

    wrong_version = json.loads(json.dumps(vital))
    wrong_version["schemaVersion"] = "1.0.0"
    assert client.post("/telemetry/events", json={"events": [wrong_version]}).status_code == 422

    unknown_metric = json.loads(json.dumps(vital))
    unknown_metric["properties"]["metric_name"] = "FID"
    assert client.post("/telemetry/events", json={"events": [unknown_metric]}).status_code == 422

    with_email = json.loads(json.dumps(vital))
    with_email["properties"]["email"] = "person@example.com"
    rejected = client.post("/telemetry/events", json={"events": [with_email]})
    assert rejected.status_code == 422
    assert "person@example.com" not in rejected.text


def test_cost_variance_stays_silent_without_history_or_under_the_line() -> None:
    assert median_unit_cost([]) is None
    assert median_unit_cost([0]) is None
    assert median_unit_cost([100, 300]) == 200
    assert median_unit_cost([100, 200, 900]) == 200
    assert cost_variance_ratio(110, 100) is None
    assert cost_variance_ratio(100, 0) is None
    ratio = cost_variance_ratio(130, 100)
    assert ratio == 0.3
