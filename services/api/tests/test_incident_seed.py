"""Seed idempotency and the CSV-to-model map from the Nexova briefing."""

from __future__ import annotations

import importlib.util
from collections import Counter
from pathlib import Path

import pytest

from nexova_incidents.csv_rules import AnalysisError
from nexova_incidents.transform import idempotency_key, prepare_csv

ROOT = Path(__file__).resolve().parents[3]
OFFICIAL = ROOT / "scripts" / "incidents-nexova.csv"
HEADER = (
    "ticket_id,date,client_company,category,description,agent_id,status,"
    "customer_email,satisfaction_score"
)


def _load_seed():
    spec = importlib.util.spec_from_file_location("seed_incidents", ROOT / "scripts" / "seed_incidents.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _csv(*rows: str) -> bytes:
    return (HEADER + "\n" + "\n".join(rows) + "\n").encode("utf-8")


def test_official_csv_transforms_to_the_briefing_totals() -> None:
    plan = prepare_csv(OFFICIAL.read_bytes())
    assert len(plan.accepted) == 96
    assert len(plan.rejected) == 4
    assert Counter(row.status for row in plan.accepted) == {
        "open": 27,
        "resolved": 56,
        "discarded": 13,
    }
    assert Counter(row.category for row in plan.accepted) == {
        "technical_failure": 49,
        "process_error": 35,
        "client_complaint": 12,
    }
    assert {row.origin for row in plan.accepted} == {"customer"}
    assert {row.branch for row in plan.accepted} == {"central"}
    assert all(row.created_at.endswith("T00:00:00Z") and row.updated_at == row.created_at for row in plan.accepted)
    assert all(row.title == row.description[:120].strip() and row.title for row in plan.accepted)
    assert all(row.source_key.startswith("ticket:NXV-") for row in plan.accepted)
    assert "@" not in " ".join(item.ticket_id for item in plan.rejected)


def test_spaces_before_the_text_do_not_produce_an_empty_title() -> None:
    description = (" " * 120) + "abcde"
    payload = _csv(
        ",".join(
            [
                "NXV-000777",
                "2024-05-01",
                "FinServ Group",
                "TECHNICAL",
                f'"{description}"',
                "AGT-01",
                "OPEN",
                "person@example.com",
                "",
            ]
        )
    )
    plan = prepare_csv(payload)
    assert plan.accepted == ()
    assert plan.rejected[0].messages == ("El título queda vacío al recortar la descripción.",)


def test_closed_maps_to_resolved_and_keeps_the_description() -> None:
    description = "x" * 130
    payload = _csv(
        ",".join(
            [
                "NXV-000778",
                "2024-02-02",
                "FinServ Group",
                "BILLING",
                description,
                "AGT-08",
                "CLOSED",
                "person@example.com",
                "4",
            ]
        )
    )
    plan = prepare_csv(payload)
    assert len(plan.accepted) == 1
    row = plan.accepted[0]
    assert row.status == "resolved"
    assert row.category == "process_error"
    assert row.title == "x" * 120
    assert row.description == description
    assert row.created_at == "2024-02-02T00:00:00Z"


def test_seed_is_idempotent_and_reports_rejected_rows(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setenv("INCIDENTS_DATA_DIR", str(tmp_path))
    from incident_store import count_incidents, reset_incidents_db, summary

    reset_incidents_db()
    seed = _load_seed()
    assert seed.main([str(OFFICIAL)]) == 0
    first = capsys.readouterr().out
    assert "Insertadas: 96" in first
    assert "Rechazadas: 4" in first
    assert "Ya estaban: 0" in first
    assert "@" not in first
    assert seed.main([str(OFFICIAL)]) == 0
    second = capsys.readouterr().out
    assert "Insertadas: 0" in second
    assert "Ya estaban: 96" in second
    assert count_incidents() == 96
    totals = summary()
    assert totals["by_status"] == {
        "open": 27,
        "in_progress": 0,
        "resolved": 56,
        "discarded": 13,
    }
    assert totals["by_category"]["technical_failure"] == 49
    assert totals["by_category"]["process_error"] == 35
    assert totals["by_category"]["client_complaint"] == 12
    assert totals["by_origin"]["customer"] == 96
    assert totals["by_branch"]["central"] == 96
    reset_incidents_db()


def test_missing_ticket_id_falls_back_to_title_and_time(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("INCIDENTS_DATA_DIR", str(tmp_path))
    from incident_store import count_incidents, insert_new, reset_incidents_db

    reset_incidents_db()
    key = idempotency_key("", "Corte de acceso al ATS", "2024-03-03T00:00:00Z")
    assert key == "fallback:Corte de acceso al ATS|2024-03-03T00:00:00Z"
    record = {
        "title": "Corte de acceso al ATS",
        "description": "Corte de acceso al ATS durante la mañana",
        "category": "technical_failure",
        "status": "open",
        "origin": "customer",
        "branch": "central",
        "created_at": "2024-03-03T00:00:00Z",
        "updated_at": "2024-03-03T00:00:00Z",
        "source_key": key,
    }
    assert insert_new(record) is not None
    assert insert_new(dict(record)) is None
    assert count_incidents() == 1
    reset_incidents_db()


def test_unreadable_csv_is_an_analysis_error() -> None:
    with pytest.raises(AnalysisError) as caught:
        prepare_csv(b"")
    assert caught.value.code == "empty_file"
