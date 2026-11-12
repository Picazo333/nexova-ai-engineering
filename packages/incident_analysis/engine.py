"""Validate and summarise a Nexova support-ticket CSV.

The field names, allowed values, and invalid-record rules come from
``nexova-BRIEFING`` (4Geeks syllabus,
``content/contexts/incidents-file-analysis``). Customer emails are never
copied into a report, a console line, or an error message.
"""

from __future__ import annotations

import csv
import io
import sys
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

_SHARED = Path(__file__).resolve().parents[1] / "shared"
if str(_SHARED) not in sys.path:
    sys.path.insert(0, str(_SHARED))

from nexova_incidents.csv_rules import (  # noqa: E402
    CATEGORIES,
    RULES,
    SCORE_LABELS,
    STATUSES,
    AnalysisError,
    csv_rows,
    public_ticket_id as _public_ticket_id,
    row_flags,
)

BAR = "=" * 60
COUNT_WIDTH = 38
TOTAL_WIDTH = 36
PERCENT_WIDTH = 47


@dataclass(frozen=True)
class _Detail:
    row_number: int
    line_number: int
    ticket_id: str
    rule_codes: tuple[str, ...]


@dataclass(frozen=True)
class AnalysisReport:
    source_name: str
    total_records: int
    valid_records: int
    invalid_records: int
    rule_counts: dict[str, int]
    category_counts: dict[str, int]
    status_counts: dict[str, int]
    score_counts: dict[int, int]
    closed_records: int
    scored_records: int
    satisfaction_average: str | None
    details: tuple[_Detail, ...]

    def console(self) -> str:
        return _console(self)

    def export_rows(self) -> list[dict[str, str]]:
        return _export_rows(self)

    def csv_text(self) -> str:
        buffer = io.StringIO(newline="")
        writer = csv.writer(buffer, lineterminator="\n")
        writer.writerow(["metric", "label", "value"])
        for row in self.export_rows():
            writer.writerow([row["metric"], row["label"], row["value"]])
        return buffer.getvalue()

    def as_dict(self) -> dict:
        rule_labels = {code: (label_en, label_es) for code, label_en, label_es in RULES}
        category_labels = {code: (label_en, label_es) for code, label_en, label_es in CATEGORIES}
        status_labels = {code: (label_en, label_es) for code, label_en, label_es in STATUSES}
        return {
            "source_name": self.source_name,
            "total_records": self.total_records,
            "valid_records": self.valid_records,
            "invalid_records": self.invalid_records,
            "invalid_breakdown": [
                {
                    "code": code,
                    "label_en": rule_labels[code][0],
                    "label_es": rule_labels[code][1],
                    "count": self.rule_counts[code],
                }
                for code, _en, _es in RULES
            ],
            "categories": [
                {
                    "code": code,
                    "label_en": category_labels[code][0],
                    "label_es": category_labels[code][1],
                    "count": self.category_counts[code],
                    "percentage": _percentage(self.category_counts[code], self.valid_records),
                }
                for code, _en, _es in CATEGORIES
            ],
            "statuses": [
                {
                    "code": code,
                    "label_en": status_labels[code][0],
                    "label_es": status_labels[code][1],
                    "count": self.status_counts[code],
                    "percentage": _percentage(self.status_counts[code], self.valid_records),
                }
                for code, _en, _es in STATUSES
            ],
            "satisfaction": {
                "closed_records": self.closed_records,
                "scored_records": self.scored_records,
                "average": self.satisfaction_average,
                "distribution": [
                    {
                        "score": score,
                        "label_en": SCORE_LABELS[score][0],
                        "label_es": SCORE_LABELS[score][1],
                        "count": self.score_counts[score],
                    }
                    for score in range(1, 6)
                ],
            },
            "invalid_details": [
                {
                    "row_number": detail.row_number,
                    "line_number": detail.line_number,
                    "ticket_id": detail.ticket_id,
                    "rules": [
                        {
                            "code": code,
                            "label_en": rule_labels[code][0],
                            "label_es": rule_labels[code][1],
                        }
                        for code in detail.rule_codes
                    ],
                }
                for detail in self.details
            ],
            "export_rows": self.export_rows(),
            "summary_es": _summary_es(self),
        }


def analyze_bytes(data: bytes, source_name: str) -> AnalysisReport:
    """Analyse a CSV payload. Raises AnalysisError for empty or unreadable files."""
    return _analyze_rows(csv_rows(data), _safe_source_name(source_name))


def _analyze_rows(rows: list[dict[str, str]], source_name: str) -> AnalysisReport:
    rule_counts = {code: 0 for code, _en, _es in RULES}
    category_counts = {code: 0 for code, _en, _es in CATEGORIES}
    status_counts = {code: 0 for code, _en, _es in STATUSES}
    score_counts = {score: 0 for score in range(1, 6)}
    details: list[_Detail] = []
    total = 0
    valid = 0
    closed = 0
    scored = 0
    points = 0

    for index, row in enumerate(rows):
        total += 1
        flags = row_flags(row)
        if flags:
            for code in flags:
                rule_counts[code] += 1
            details.append(
                _Detail(
                    row_number=index + 1,
                    line_number=index + 2,
                    ticket_id=_public_ticket_id(row.get("ticket_id", "")),
                    rule_codes=flags,
                )
            )
            continue
        valid += 1
        category = row["category"].strip()
        status = row["status"].strip()
        category_counts[category] += 1
        status_counts[status] += 1
        if status == "CLOSED":
            closed += 1
            score = int(row["satisfaction_score"].strip())
            scored += 1
            points += score
            score_counts[score] += 1

    if total == 0:
        raise AnalysisError(
            "empty_records",
            "The CSV has the expected header but no records.",
            "El CSV tiene cabecera pero no contiene registros.",
        )

    return AnalysisReport(
        source_name=source_name,
        total_records=total,
        valid_records=valid,
        invalid_records=total - valid,
        rule_counts=rule_counts,
        category_counts=category_counts,
        status_counts=status_counts,
        score_counts=score_counts,
        closed_records=closed,
        scored_records=scored,
        satisfaction_average=_average(points, scored),
        details=tuple(details),
    )


def _safe_source_name(name: str) -> str:
    base = Path(name or "").name.strip() or "upload.csv"
    if "@" in base or any(char in base for char in "\r\n\t<>"):
        return "upload.csv"
    if len(base) > 180:
        return "upload.csv"
    return base


def _percentage(count: int, total: int) -> str | None:
    if total <= 0:
        return None
    value = (Decimal(count) * Decimal(100) / Decimal(total)).quantize(
        Decimal("0.1"),
        rounding=ROUND_HALF_UP,
    )
    return f"{value:.1f}"


def _average(points: int, scored: int) -> str | None:
    if scored <= 0:
        return None
    value = (Decimal(points) / Decimal(scored)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return f"{value:.2f}"


def _fit(prefix: str, label: str, value: str, width: int) -> str:
    dots = width - len(prefix) - len(label) - 2 - len(value)
    if dots < 2:
        dots = 2
    return f"{prefix}{label} {'.' * dots} {value}"


def _tree(pairs: list[tuple[str, str]], width: int) -> list[str]:
    lines: list[str] = []
    last = len(pairs) - 1
    for index, (label, value) in enumerate(pairs):
        prefix = "  └─ " if index == last else "  ├─ "
        lines.append(_fit(prefix, label, value, width))
    return lines


def _count_percent_value(count: int, percentage: str | None, pad: int) -> str:
    shown = f"{count:>{pad}}"
    if percentage is None:
        return shown
    return f"{shown}  ({percentage}%)"


def _console(report: AnalysisReport) -> str:
    lines = [
        BAR,
        "  NEXOVA — SUPPORT TICKET ANALYSIS",
        f"  Source file: {report.source_name}",
        BAR,
        "",
        _fit("", "TOTAL RECORDS IN FILE", str(report.total_records), TOTAL_WIDTH),
    ]
    lines.extend(
        _tree(
            [
                ("Valid records", str(report.valid_records)),
                ("Invalid / incomplete", str(report.invalid_records)),
            ],
            COUNT_WIDTH,
        )
    )
    lines.append("")
    lines.append("INVALID RECORDS BREAKDOWN")
    fired = [(label_en, str(report.rule_counts[code])) for code, label_en, _es in RULES if report.rule_counts[code]]
    if fired:
        lines.extend(_tree(fired, COUNT_WIDTH))
    else:
        lines.append("  (no invalid records)")
    silent = [label_en for code, label_en, _es in RULES if report.rule_counts[code] == 0]
    lines.append("")
    lines.append("BREAKDOWN BY CATEGORY (valid records)")
    category_pad = max(2, *(len(str(count)) for count in report.category_counts.values()))
    lines.extend(
        _tree(
            [
                (
                    code,
                    _count_percent_value(
                        report.category_counts[code],
                        _percentage(report.category_counts[code], report.valid_records),
                        category_pad,
                    ),
                )
                for code, _en, _es in CATEGORIES
            ],
            PERCENT_WIDTH,
        )
    )
    lines.append("")
    lines.append("BREAKDOWN BY STATUS (valid records)")
    status_pad = max(2, *(len(str(count)) for count in report.status_counts.values()))
    lines.extend(
        _tree(
            [
                (
                    code,
                    _count_percent_value(
                        report.status_counts[code],
                        _percentage(report.status_counts[code], report.valid_records),
                        status_pad,
                    ),
                )
                for code, _en, _es in STATUSES
            ],
            PERCENT_WIDTH,
        )
    )
    lines.append("")
    lines.append("SATISFACTION INDEX (closed tickets)")
    lines.append(f"  Scored tickets: {report.scored_records} of {report.closed_records}")
    if report.satisfaction_average is None:
        lines.append("  Average score: n/a")
    else:
        lines.append(f"  Average score: {report.satisfaction_average} / 5.00")
    lines.extend(
        _tree(
            [
                (f"Score {score} ({SCORE_LABELS[score][0]})", str(report.score_counts[score]))
                for score in range(1, 6)
            ],
            COUNT_WIDTH,
        )
    )
    if silent:
        lines.append("")
        lines.append("Other checked rules with 0 matches: " + "; ".join(silent) + ".")
    lines.append("")
    lines.append(BAR)
    return "\n".join(lines) + "\n"


def _summary_es(report: AnalysisReport) -> str:
    if report.satisfaction_average is None:
        average = "no hay tickets CLOSED válidos con puntuación"
    else:
        average = f"el índice de satisfacción es {report.satisfaction_average} / 5.00"
    return (
        f"El fichero {report.source_name} tiene {report.total_records} filas: "
        f"{report.valid_records} válidas y {report.invalid_records} inválidas. "
        f"{average[:1].upper() + average[1:]}."
    )


def _export_rows(report: AnalysisReport) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = [
        {"metric": "source_file", "label": "Source file", "value": report.source_name},
        {"metric": "total_records", "label": "TOTAL RECORDS IN FILE", "value": str(report.total_records)},
        {"metric": "valid_records", "label": "Valid records", "value": str(report.valid_records)},
        {"metric": "invalid_records", "label": "Invalid / incomplete", "value": str(report.invalid_records)},
    ]
    for code, label_en, _es in RULES:
        rows.append(
            {
                "metric": f"invalid_{code}",
                "label": label_en,
                "value": str(report.rule_counts[code]),
            }
        )
    for code, _en, _es in CATEGORIES:
        percentage = _percentage(report.category_counts[code], report.valid_records)
        rows.append(
            {
                "metric": f"category_{code}",
                "label": f"Category {code}",
                "value": str(report.category_counts[code]),
            }
        )
        rows.append(
            {
                "metric": f"category_{code}_pct",
                "label": f"Category {code} percentage",
                "value": "n/a" if percentage is None else percentage,
            }
        )
    for code, _en, _es in STATUSES:
        percentage = _percentage(report.status_counts[code], report.valid_records)
        rows.append(
            {
                "metric": f"status_{code}",
                "label": f"Status {code}",
                "value": str(report.status_counts[code]),
            }
        )
        rows.append(
            {
                "metric": f"status_{code}_pct",
                "label": f"Status {code} percentage",
                "value": "n/a" if percentage is None else percentage,
            }
        )
    rows.append(
        {
            "metric": "satisfaction_closed_records",
            "label": "Closed tickets with analysis",
            "value": str(report.closed_records),
        }
    )
    rows.append(
        {
            "metric": "satisfaction_scored_records",
            "label": "Scored closed tickets",
            "value": str(report.scored_records),
        }
    )
    rows.append(
        {
            "metric": "satisfaction_average",
            "label": "Average satisfaction score",
            "value": "n/a" if report.satisfaction_average is None else report.satisfaction_average,
        }
    )
    for score in range(1, 6):
        rows.append(
            {
                "metric": f"satisfaction_score_{score}",
                "label": f"Score {score} ({SCORE_LABELS[score][0]})",
                "value": str(report.score_counts[score]),
            }
        )
    return rows
