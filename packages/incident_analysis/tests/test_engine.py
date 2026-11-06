"""Golden checks against the official Nexova CSV and the briefing rules."""

from __future__ import annotations

import csv
import io
import json
from pathlib import Path

from incident_analysis.engine import AnalysisError, analyze_bytes

ROOT = Path(__file__).resolve().parents[3]
OFFICIAL = ROOT / "scripts" / "incidents-nexova.csv"
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
        "status": "OPEN",
        "customer_email": "person@example.com",
        "satisfaction_score": "",
    }
    base.update(overrides)
    return ",".join(base[name] for name in base)


def _csv(*rows: str) -> bytes:
    return (HEADER + "\n" + "\n".join(rows) + "\n").encode("utf-8")


def _official() -> bytes:
    return OFFICIAL.read_bytes()


def test_official_file_matches_briefing_figures() -> None:
    report = analyze_bytes(_official(), "incidents-nexova.csv")
    assert report.total_records == 100
    assert report.valid_records == 96
    assert report.invalid_records == 4
    assert report.category_counts == {
        "TECHNICAL": 28,
        "BILLING": 18,
        "ACCESS": 21,
        "HR_QUERY": 17,
        "COMPLAINT": 12,
    }
    assert report.status_counts == {"OPEN": 27, "CLOSED": 56, "DISCARDED": 13}
    assert report.rule_counts["missing_client_company"] == 1
    assert report.rule_counts["invalid_category"] == 1
    assert report.rule_counts["invalid_email"] == 1
    assert report.rule_counts["closed_without_score"] == 1
    assert report.rule_counts["empty_description"] == 0
    assert report.rule_counts["invalid_agent_id"] == 0
    assert report.rule_counts["score_out_of_range"] == 0
    assert report.score_counts == {1: 2, 2: 5, 3: 10, 4: 22, 5: 17}
    assert report.scored_records == 56
    assert report.closed_records == 56
    assert report.satisfaction_average == "3.84"
    payload = report.as_dict()
    percentages = {item["code"]: item["percentage"] for item in payload["categories"]}
    assert percentages == {
        "TECHNICAL": "29.2",
        "BILLING": "18.8",
        "ACCESS": "21.9",
        "HR_QUERY": "17.7",
        "COMPLAINT": "12.5",
    }
    status_pct = {item["code"]: item["percentage"] for item in payload["statuses"]}
    assert status_pct == {"OPEN": "28.1", "CLOSED": "58.3", "DISCARDED": "13.5"}


def test_official_console_contains_briefing_lines() -> None:
    console = analyze_bytes(_official(), OFFICIAL.name).console()
    expected = [
        "  NEXOVA — SUPPORT TICKET ANALYSIS",
        "  Source file: incidents-nexova.csv",
        "TOTAL RECORDS IN FILE .......... 100",
        "  ├─ Valid records ................ 96",
        "  └─ Invalid / incomplete .......... 4",
        "  ├─ Missing client_company ........ 1",
        "  ├─ Invalid or missing category ... 1",
        "  ├─ Invalid or missing email ...... 1",
        "  └─ Closed ticket, no score ....... 1",
        "  ├─ TECHNICAL .................... 28  (29.2%)",
        "  ├─ BILLING ...................... 18  (18.8%)",
        "  ├─ ACCESS ....................... 21  (21.9%)",
        "  ├─ HR_QUERY ..................... 17  (17.7%)",
        "  └─ COMPLAINT .................... 12  (12.5%)",
        "  ├─ OPEN ......................... 27  (28.1%)",
        "  ├─ CLOSED ....................... 56  (58.3%)",
        "  └─ DISCARDED .................... 13  (13.5%)",
        "  Scored tickets: 56 of 56",
        "  Average score: 3.84 / 5.00",
        "  ├─ Score 1 (Very dissatisfied) ... 2",
        "  ├─ Score 2 (Dissatisfied) ........ 5",
        "  ├─ Score 3 (Neutral) ............ 10",
        "  ├─ Score 4 (Satisfied) .......... 22",
        "  └─ Score 5 (Very satisfied) ..... 17",
        "Other checked rules with 0 matches: Empty or short description; "
        "Invalid or missing agent_id; Satisfaction score out of range; "
        "Invalid or missing ticket_id; Invalid or missing date; "
        "Invalid or missing status.",
    ]
    for line in expected:
        assert line in console.splitlines()


def test_official_output_never_contains_customer_email() -> None:
    raw = _official()
    report = analyze_bytes(raw, "incidents-nexova.csv")
    rendered = "\n".join(
        [
            report.console(),
            report.csv_text(),
            json.dumps(report.as_dict(), ensure_ascii=False),
        ]
    )
    emails = set()
    text = raw.decode("utf-8-sig")
    for row in csv.DictReader(io.StringIO(text)):
        email = (row.get("customer_email") or "").strip()
        if email:
            emails.add(email)
    leaked = [email for email in emails if email in rendered]
    assert not leaked, "customer email appeared in analysis output"
    assert "@" not in rendered


def test_official_invalid_rows_are_the_four_briefing_cases() -> None:
    details = analyze_bytes(_official(), "x.csv").as_dict()["invalid_details"]
    found = {(item["ticket_id"], tuple(rule["code"] for rule in item["rules"])) for item in details}
    assert found == {
        ("NXV-000017", ("missing_client_company",)),
        ("NXV-000043", ("invalid_category",)),
        ("NXV-000086", ("invalid_email",)),
        ("NXV-000090", ("closed_without_score",)),
    }


def test_export_is_one_metric_per_row() -> None:
    report = analyze_bytes(_official(), "incidents-nexova.csv")
    rows = list(csv.DictReader(io.StringIO(report.csv_text())))
    assert rows[0].keys() == {"metric", "label", "value"}
    assert len(rows) == len(report.export_rows())
    metrics = {row["metric"]: row["value"] for row in rows}
    assert metrics["total_records"] == "100"
    assert metrics["valid_records"] == "96"
    assert metrics["invalid_records"] == "4"
    assert metrics["category_TECHNICAL"] == "28"
    assert metrics["category_BILLING_pct"] == "18.8"
    assert metrics["status_CLOSED"] == "56"
    assert metrics["satisfaction_average"] == "3.84"
    assert metrics["satisfaction_score_5"] == "17"
    assert all(len(row) == 3 for row in rows)


def test_each_invalid_rule_and_a_row_with_two_rules() -> None:
    report = analyze_bytes(
        _csv(
            _row(client_company="", description="abc", ticket_id="NXV-000010"),
            _row(category="OTHER", ticket_id="NXV-000011"),
            _row(description="tiny", ticket_id="NXV-000012"),
            _row(agent_id="AGT-7", ticket_id="NXV-000013"),
            _row(customer_email="not-an-email", ticket_id="NXV-000014"),
            _row(status="CLOSED", satisfaction_score="", ticket_id="NXV-000015"),
            _row(satisfaction_score="9", ticket_id="NXV-000016"),
            _row(ticket_id="BAD", date="2024-02-31", status="open"),
            _row(ticket_id="NXV-000017", status="CLOSED", satisfaction_score="4"),
        ),
        "synthetic.csv",
    )
    assert report.total_records == 9
    assert report.valid_records == 1
    assert report.invalid_records == 8
    assert report.rule_counts["missing_client_company"] == 1
    assert report.rule_counts["empty_description"] == 2
    assert report.rule_counts["invalid_category"] == 1
    assert report.rule_counts["invalid_agent_id"] == 1
    assert report.rule_counts["invalid_email"] == 1
    assert report.rule_counts["closed_without_score"] == 1
    assert report.rule_counts["score_out_of_range"] == 1
    assert report.rule_counts["invalid_ticket_id"] == 1
    assert report.rule_counts["invalid_date"] == 1
    assert report.rule_counts["invalid_status"] == 1
    assert report.satisfaction_average == "4.00"
    rendered = json.dumps(report.as_dict())
    assert "not-an-email" not in rendered
    multi = next(item for item in report.details if item.ticket_id == "NXV-000010")
    assert multi.rule_codes == ("missing_client_company", "empty_description")


def test_open_ticket_score_is_not_part_of_the_average() -> None:
    report = analyze_bytes(
        _csv(
            _row(status="OPEN", satisfaction_score="1", ticket_id="NXV-000021"),
            _row(status="CLOSED", satisfaction_score="5", ticket_id="NXV-000022"),
        ),
        "scores.csv",
    )
    assert report.valid_records == 2
    assert report.scored_records == 1
    assert report.satisfaction_average == "5.00"


def test_short_description_boundary() -> None:
    report = analyze_bytes(
        _csv(
            _row(description="1234", ticket_id="NXV-000031"),
            _row(description="12345", ticket_id="NXV-000032"),
        ),
        "desc.csv",
    )
    assert report.invalid_records == 1
    assert report.valid_records == 1


def test_empty_header_only_delimiter_and_missing_column() -> None:
    with_raises = analyze_bytes
    try:
        with_raises(b"", "empty.csv")
    except AnalysisError as exc:
        assert exc.code == "empty_file"
    else:
        raise AssertionError("empty file should fail")
    try:
        with_raises((HEADER + "\n").encode(), "header.csv")
    except AnalysisError as exc:
        assert exc.code == "empty_records"
    else:
        raise AssertionError("header only should fail")
    try:
        with_raises("ticket_id;date\nNXV-000001;2024-01-01\n".encode(), "semi.csv")
    except AnalysisError as exc:
        assert exc.code == "invalid_delimiter"
    else:
        raise AssertionError("semicolon file should fail")
    try:
        with_raises(b"ticket_id,date\nsecret-sentinel@example.com,2024-01-01\n", "bad.csv")
    except AnalysisError as exc:
        assert exc.code == "missing_columns"
        assert "client_company" in exc.message_es
        assert "secret-sentinel@example.com" not in exc.message_en
        assert "secret-sentinel@example.com" not in exc.message_es
    else:
        raise AssertionError("missing columns should fail")


def test_utf8_bom_is_accepted() -> None:
    payload = b"\xef\xbb\xbf" + _csv(_row(ticket_id="NXV-000041"))
    report = analyze_bytes(payload, "bom.csv")
    assert report.valid_records == 1


def test_binary_file_is_rejected_without_echoing_bytes() -> None:
    try:
        analyze_bytes(b"\x00\x01not-an-email", "bin.csv")
    except AnalysisError as exc:
        assert exc.code == "invalid_format"
        assert "not-an-email" not in exc.message_en
    else:
        raise AssertionError("binary file should fail")
