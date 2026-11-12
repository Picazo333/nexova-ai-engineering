"""POST /telemetry/events stores valid events and counts the rejected ones.

PostgreSQL comes from NEXOVA_TEST_DATABASE_URL. A missing URL skips the
tests that write. It is not a pass, and nothing here uses SQLite.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import uuid
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, text
from sqlalchemy.pool import NullPool

from app.config import telemetry_endpoint
from app.inventory.service import cost_variance_ratio, median_unit_cost
from app.telemetry.schemas import TelemetryEvent

ROOT = Path(__file__).resolve().parents[3]
VALID = ROOT / "docs" / "telemetry" / "examples" / "valid"
INVALID = ROOT / "docs" / "telemetry" / "examples" / "invalid"
SCHEMA_FILE = ROOT / "docs" / "telemetry" / "event-schemas.json"
MODEL_FILE = Path(__file__).resolve().parents[1] / "app" / "telemetry" / "schemas.py"
MODEL_SHA256 = "f03ed2b0352a2911d70398ffcc74edfc8237978c415a7c8721a507f733e052d0"

needs_postgres = pytest.mark.skipif(
    not os.environ.get("NEXOVA_TEST_DATABASE_URL", "").strip(),
    reason="NEXOVA_TEST_DATABASE_URL no está definido; no se simula PostgreSQL.",
)


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _postgres_url() -> str:
    url = os.environ.get("NEXOVA_TEST_DATABASE_URL", "").strip()
    if url.startswith("sqlite"):
        pytest.fail("SQLite no cuenta como PostgreSQL.")
    return url


@pytest.fixture()
def telemetry_client(tmp_path, monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    url = _postgres_url()
    schema = "tel_" + uuid.uuid4().hex[:16]
    monkeypatch.setenv("DATABASE_URL", url)
    monkeypatch.setenv("INVENTORY_SCHEMA", schema)
    monkeypatch.setenv("INVENTORY_AUTOSEED", "0")
    monkeypatch.setenv("SUPPLIERS_DATA_DIR", str(tmp_path / "suppliers"))
    monkeypatch.setenv("SUPPLIERS_AUTOSEED", "0")
    monkeypatch.setenv("INCIDENTS_DATA_DIR", str(tmp_path / "incidents"))
    from app.auth.store import reset_auth_db
    from app.infrastructure.analysis_store import reset_store
    from app.inventory.database import normalize_database_url, reset_engine
    from app.main import create_app
    from database import reset_db
    from incident_store import reset_incidents_db

    reset_engine()
    reset_db()
    reset_auth_db()
    reset_incidents_db()
    reset_store(tmp_path / "incidents")
    try:
        with TestClient(create_app()) as test_client:
            yield test_client
    finally:
        reset_engine()
        reset_db()
        reset_auth_db()
        reset_incidents_db()
        admin = create_engine(normalize_database_url(url), poolclass=NullPool)
        try:
            with admin.begin() as connection:
                connection.execute(text(f'DROP SCHEMA IF EXISTS "{schema}" CASCADE'))
        finally:
            admin.dispose()


def _rows() -> list[dict]:
    from app.inventory.database import get_engine

    with get_engine().begin() as connection:
        result = connection.execute(
            text(
                "SELECT service, event_type, level, value, message, tags "
                "FROM telemetry_events ORDER BY event_type, id"
            )
        )
        found = []
        for row in result.mappings():
            item = dict(row)
            if isinstance(item["tags"], str):
                item["tags"] = json.loads(item["tags"])
            found.append(item)
        return found


def test_telemetry_endpoint_is_read_from_the_environment(monkeypatch) -> None:
    monkeypatch.setenv("TELEMETRY_ENDPOINT", "http://localhost:8000/telemetry/events")
    assert telemetry_endpoint() == "http://localhost:8000/telemetry/events"
    monkeypatch.setenv("TELEMETRY_ENDPOINT", "")
    assert telemetry_endpoint() == ""


def test_telemetry_event_model_is_unchanged() -> None:
    digest = hashlib.sha256(MODEL_FILE.read_bytes()).hexdigest()
    assert digest == MODEL_SHA256
    source = MODEL_FILE.read_text(encoding="utf-8")
    assert "events: list[TelemetryEvent]" in source


def test_handler_validates_per_event_and_ignores_the_schema_id_filename() -> None:
    router_source = (MODEL_FILE.parent / "router.py").read_text(encoding="utf-8")
    validate_source = (MODEL_FILE.parent / "validate.py").read_text(encoding="utf-8")
    assert "TelemetryEvent.model_validate" in validate_source
    assert "events: list[TelemetryEvent]" not in router_source
    assert "TelemetryBatch" not in router_source
    assert "event-envelope" not in validate_source
    assert "1.0.0.json" not in validate_source
    from app.telemetry.validate import schema_path

    opened = schema_path()
    assert opened == SCHEMA_FILE
    document = json.loads(opened.read_text(encoding="utf-8"))
    assert "web_vital_recorded" in document["properties"]["event_type"]["enum"]
    assert document["x-nexova"]["schemaVersion"]


def test_model_validate_is_on_the_reject_path(client: TestClient, monkeypatch) -> None:
    calls = {"n": 0}
    original = TelemetryEvent.model_validate

    def wrapped(value):
        calls["n"] += 1
        return original(value)

    monkeypatch.setattr(TelemetryEvent, "model_validate", staticmethod(wrapped))
    event = _load(VALID / "login_succeeded.json")
    event["event_type"] = "page_view"
    response = client.post("/telemetry/events", json={"events": [event]})
    assert calls["n"] == 1
    assert response.status_code == 200
    assert response.json() == {"received": 1, "stored": 0, "rejected": 1}
    assert "page_view" not in response.text


def test_unparseable_envelope_is_422(client: TestClient) -> None:
    response = client.post("/telemetry/events", json={"events": "no"})
    assert response.status_code == 422
    body = response.json()
    assert body["detail"] == "El lote no tiene el formato de telemetría."
    assert client.post("/telemetry/events", json={"extra": True, "events": []}).status_code == 422
    assert client.post("/telemetry/events", content=b"not-json", headers={"Content-Type": "text/plain"}).status_code == 422


def test_invalid_event_does_not_fail_the_batch(client: TestClient) -> None:
    event = _load(VALID / "login_succeeded.json")
    event["event_type"] = "page_view"
    response = client.post("/telemetry/events", json={"events": [event]})
    assert response.status_code == 200
    assert response.json() == {"received": 1, "stored": 0, "rejected": 1}


def test_empty_batch_stores_nothing(client: TestClient) -> None:
    response = client.post("/telemetry/events", json={"events": []})
    assert response.status_code == 200
    assert response.json() == {"received": 0, "stored": 0, "rejected": 0}


def test_valid_events_without_a_database_are_503(client: TestClient) -> None:
    event = _load(VALID / "login_succeeded.json")
    response = client.post("/telemetry/events", json={"events": [event]})
    assert response.status_code == 503
    assert "stored" not in response.text
    assert "postgres://" not in response.text
    assert "postgresql://" not in response.text


def test_web_vital_rejects_a_bad_version_metric_or_email_without_echoing_it(client: TestClient) -> None:
    vital = _load(VALID / "web_vital_recorded.json")
    wrong_version = json.loads(json.dumps(vital))
    wrong_version["schemaVersion"] = "1.0.0"
    unknown_metric = json.loads(json.dumps(vital))
    unknown_metric["properties"]["metric_name"] = "FID"
    with_email = json.loads(json.dumps(vital))
    with_email["properties"]["email"] = "person@example.com"
    for broken in (wrong_version, unknown_metric, with_email):
        response = client.post("/telemetry/events", json={"events": [broken]})
        assert response.status_code == 200
        assert response.json() == {"received": 1, "stored": 0, "rejected": 1}
        assert "person@example.com" not in response.text


def test_oversized_batch_is_422(client: TestClient) -> None:
    response = client.post("/telemetry/events", json={"events": [{} for _ in range(501)]})
    assert response.status_code == 422
    assert response.json()["detail"] == "El lote supera 500 eventos."


def test_cost_variance_stays_silent_without_history_or_under_the_line() -> None:
    assert median_unit_cost([]) is None
    assert median_unit_cost([0]) is None
    assert median_unit_cost([100, 300]) == 200
    assert median_unit_cost([100, 200, 900]) == 200
    assert cost_variance_ratio(110, 100) is None
    assert cost_variance_ratio(100, 0) is None
    ratio = cost_variance_ratio(130, 100)
    assert ratio == 0.3


@needs_postgres
def test_batch_is_stored_and_logged(telemetry_client: TestClient, caplog) -> None:
    event = _load(VALID / "login_succeeded.json")
    with caplog.at_level(logging.INFO, logger="nexova.telemetry"):
        response = telemetry_client.post("/telemetry/events", json={"events": [event, event]})
    assert response.status_code == 200
    assert response.json() == {"received": 2, "stored": 2, "rejected": 0}
    assert "received=2" in caplog.text
    assert "stored=2" in caplog.text
    assert "rejected=0" in caplog.text
    assert "login_succeeded" in caplog.text
    assert "access_token" not in response.text
    rows = _rows()
    assert len(rows) == 2
    assert rows[0]["event_type"] == "login_succeeded"
    assert rows[0]["level"] == "info"
    assert rows[0]["service"] == "backoffice"
    assert float(rows[0]["value"]) == 1800


@needs_postgres
def test_text_plain_beacon_is_stored(telemetry_client: TestClient) -> None:
    event = _load(VALID / "login_succeeded.json")
    response = telemetry_client.post(
        "/telemetry/events",
        content=json.dumps({"events": [event]}),
        headers={"Content-Type": "text/plain;charset=UTF-8"},
    )
    assert response.status_code == 200
    assert response.json() == {"received": 1, "stored": 1, "rejected": 0}


@needs_postgres
def test_partial_batch_keeps_valid_rows_in_one_insert(telemetry_client: TestClient, caplog) -> None:
    from app.inventory.database import get_engine

    inbound = _load(VALID / "inbound_order_created.json")
    outbound = _load(VALID / "outbound_order_created.json")
    failed = _load(VALID / "login_failed.json")
    vital = _load(VALID / "web_vital_recorded.json")
    extra = _load(INVALID / "extra-property.json")
    mismatch = _load(INVALID / "currency-office-mismatch.json")
    unknown = json.loads(json.dumps(failed))
    unknown["event_type"] = "page_view"
    payload = {
        "events": [inbound, "no", extra, outbound, failed, mismatch, vital, unknown],
    }
    engine = get_engine()
    inserts: list[str] = []

    def before(_conn, _cursor, statement, _parameters, _context, _executemany) -> None:
        sql = " ".join(statement.split()).lower()
        if "insert into telemetry_events" in sql:
            inserts.append(sql)

    event.listen(engine, "before_cursor_execute", before)
    try:
        with caplog.at_level(logging.INFO, logger="nexova.telemetry"):
            response = telemetry_client.post("/telemetry/events", json=payload)
    finally:
        event.remove(engine, "before_cursor_execute", before)

    assert response.status_code == 200, response.text
    assert response.json() == {"received": 8, "stored": 4, "rejected": 4}
    assert len(inserts) == 1
    assert inserts[0].count("insert into") == 1
    assert "ada@nexova.test" not in response.text
    assert "ada@nexova.test" not in caplog.text
    assert "stored=4" in caplog.text
    assert "rejected=4" in caplog.text
    assert "rejected_reasons=" in caplog.text

    rows = {row["event_type"]: row for row in _rows()}
    assert set(rows) == {
        "inbound_order_created",
        "outbound_order_created",
        "login_failed",
        "web_vital_recorded",
    }
    stored_inbound = rows["inbound_order_created"]
    assert stored_inbound["service"] == "backoffice"
    assert stored_inbound["level"] == "info"
    assert float(stored_inbound["value"]) == 10
    tags = stored_inbound["tags"]
    assert tags["office"] == "valencia"
    assert tags["product_category"] == "onboarding_equipment"
    assert tags["programme_id"] == "unassigned"
    assert tags["currency"] == "EUR"
    assert tags["eventId"] == inbound["eventId"]
    assert tags["sessionId"] == inbound["sessionId"]
    assert tags["userId"] == inbound["userId"]
    assert tags["schemaVersion"] == inbound["schemaVersion"]
    assert tags["requestId"] == inbound["requestId"]
    assert "supplier_email" not in tags
    assert set(tags) == set(_ENVELOPE_KEYS) | set(inbound["properties"])
    assert rows["login_failed"]["level"] == "warn"
    assert rows["login_failed"]["value"] is None
    assert rows["web_vital_recorded"]["tags"]["schemaVersion"] == "1.1.0"
    assert float(rows["web_vital_recorded"]["value"]) == 3200
    assert rows["web_vital_recorded"]["service"] == "backoffice"


_ENVELOPE_KEYS = ("eventId", "sessionId", "userId", "schemaVersion", "requestId")


@needs_postgres
def test_catalogue_examples_share_one_insert(telemetry_client: TestClient) -> None:
    from app.inventory.database import get_engine

    document = json.loads(SCHEMA_FILE.read_text(encoding="utf-8"))
    enum = set(document["properties"]["event_type"]["enum"])
    events = [_load(path) for path in sorted(VALID.glob("*.json"))]
    assert {event["event_type"] for event in events} == enum
    assert any(event["event_type"] == "web_vital_recorded" for event in events)
    engine = get_engine()
    inserts: list[str] = []

    def before(_conn, _cursor, statement, _parameters, _context, _executemany) -> None:
        sql = " ".join(statement.split()).lower()
        if "insert into telemetry_events" in sql:
            inserts.append(sql)

    event.listen(engine, "before_cursor_execute", before)
    try:
        response = telemetry_client.post("/telemetry/events", json={"events": events})
    finally:
        event.remove(engine, "before_cursor_execute", before)
    assert response.status_code == 200, response.text
    assert response.json() == {"received": len(events), "stored": len(events), "rejected": 0}
    assert len(inserts) == 1
    rows = _rows()
    assert {row["event_type"] for row in rows} == enum
    by_type = {row["event_type"]: row for row in rows}
    assert by_type["frontend_exception_recorded"]["level"] == "error"
    assert by_type["api_response_failed"]["level"] == "error"
    assert by_type["session_expired"]["service"] == "api"
    assert by_type["page_load_recorded"]["service"] == "backoffice"
    assert "b7b32534990c138f77d0b6a7d0d9d0d58ad07faca7c6d5ab1d69c54bcc459036" in by_type["frontend_exception_recorded"]["tags"]["message_sha256"]
    assert "Cannot read" not in json.dumps(by_type["frontend_exception_recorded"]["tags"])


@needs_postgres
def test_table_shape_indexes_and_immutability(telemetry_client: TestClient) -> None:
    from app.inventory.database import get_engine
    from app.telemetry.store import ensure_telemetry_table, reset_telemetry_cache

    event = _load(VALID / "inbound_order_created.json")
    assert telemetry_client.post("/telemetry/events", json={"events": [event]}).status_code == 200
    engine = get_engine()
    reset_telemetry_cache()
    ensure_telemetry_table(engine)
    with engine.begin() as connection:
        columns = list(
            connection.execute(
                text(
                    "SELECT column_name, data_type, is_nullable, column_default "
                    "FROM information_schema.columns "
                    "WHERE table_schema = current_schema() AND table_name = 'telemetry_events' "
                    "ORDER BY ordinal_position"
                )
            )
        )
        indexes = list(
            connection.execute(
                text(
                    "SELECT indexname, indexdef FROM pg_indexes "
                    "WHERE schemaname = current_schema() AND tablename = 'telemetry_events'"
                )
            )
        )
        triggers = list(
            connection.execute(
                text(
                    "SELECT tgname FROM pg_trigger "
                    "WHERE tgrelid = 'telemetry_events'::regclass AND NOT tgisinternal"
                )
            )
        )
    names = [row[0] for row in columns]
    assert names == ["id", "timestamp", "service", "event_type", "level", "value", "message", "tags"]
    kinds = {row[0]: row[1] for row in columns}
    assert kinds["id"] == "uuid"
    assert kinds["timestamp"] == "timestamp with time zone"
    assert kinds["service"] == "text"
    assert kinds["event_type"] == "text"
    assert kinds["level"] == "text"
    assert kinds["value"] == "numeric"
    assert kinds["message"] == "text"
    assert kinds["tags"] == "jsonb"
    defaults = {row[0]: row[3] or "" for row in columns}
    assert "gen_random_uuid()" in defaults["id"]
    assert "info" in defaults["level"]
    assert "{}" in defaults["tags"]
    indexdef = " ".join(row[1].lower() for row in indexes)
    assert "telemetry_events_timestamp_idx" in indexdef
    assert "telemetry_events_event_type_idx" in indexdef
    assert "telemetry_events_tags_gin_idx" in indexdef
    assert "using gin" in indexdef
    assert {row[0] for row in triggers} >= {
        "telemetry_events_no_update",
        "telemetry_events_no_delete",
        "telemetry_events_no_truncate",
    }
    for statement in (
        "UPDATE telemetry_events SET message = 'cambiado'",
        "DELETE FROM telemetry_events",
        "TRUNCATE telemetry_events",
    ):
        with pytest.raises(Exception, match="solo escritura"):
            with engine.begin() as connection:
                connection.execute(text(statement))
    assert len(_rows()) == 1
