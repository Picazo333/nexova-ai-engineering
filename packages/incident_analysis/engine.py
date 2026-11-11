"""Validate and summarise a Nexova support-ticket CSV.

The field names, allowed values, and invalid-record rules come from
``nexova-BRIEFING`` (4Geeks syllabus,
``content/contexts/incidents-file-analysis``). Customer emails are never
copied into a report, a console line, or an error message.
"""

from __future__ import annotations

import csv
import io
import re
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

REQUIRED_COLUMNS = (
    "ticket_id",
    "date",
    "client_company",
    "category",
    "description",
    "agent_id",
    "status",
    "customer_email",
    "satisfaction_score",
)

CATEGORIES = (
    ("TECHNICAL", "Technical issue with a product or system", "Problema técnico con un producto o sistema"),
    ("BILLING", "Billing query or dispute", "Consulta o disputa de facturación"),
    ("ACCESS", "Login, permissions, or account access problem", "Problema de acceso, login o permisos"),
    ("HR_QUERY", "HR or policy question from a client's staff", "Consulta de RR. HH. o políticas de personal"),
    ("COMPLAINT", "Formal complaint about service quality", "Queja formal sobre la calidad del servicio"),
)

STATUSES = (
    ("OPEN", "Open", "Abierto"),
    ("CLOSED", "Closed", "Cerrado"),
    ("DISCARDED", "Discarded", "Descartado"),
)

SCORE_LABELS = {
    1: ("Very dissatisfied", "Muy insatisfecho"),
    2: ("Dissatisfied", "Insatisfecho"),
    3: ("Neutral", "Neutral"),
    4: ("Satisfied", "Satisfecho"),
    5: ("Very satisfied", "Muy satisfecho"),
}

RULES = (
    ("missing_client_company", "Missing client_company", "Falta client_company"),
    ("invalid_category", "Invalid or missing category", "Categoría ausente o no permitida"),
    ("empty_description", "Empty or short description", "Descripción vacía o de menos de 5 caracteres"),
    ("invalid_agent_id", "Invalid or missing agent_id", "agent_id ausente o distinto de AGT-XX"),
    ("invalid_email", "Invalid or missing email", "Correo ausente o inválido"),
    ("closed_without_score", "Closed ticket, no score", "Estado CLOSED sin satisfaction_score"),
    ("score_out_of_range", "Satisfaction score out of range", "satisfaction_score fuera de 1–5"),
    ("invalid_ticket_id", "Invalid or missing ticket_id", "ticket_id ausente o distinto de NXV-XXXXXX"),
    ("invalid_date", "Invalid or missing date", "Fecha ausente o distinta de YYYY-MM-DD"),
    ("invalid_status", "Invalid or missing status", "Estado ausente o distinto de OPEN, CLOSED o DISCARDED"),
)

CATEGORY_CODES = {code for code, _en, _es in CATEGORIES}
STATUS_CODES = {code for code, _en, _es in STATUSES}
TICKET_RE = re.compile(r"^NXV-\d{6}$")
AGENT_RE = re.compile(r"^AGT-\d{2}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SCORE_RE = re.compile(r"^\d+$")
BAR = "=" * 60
COUNT_WIDTH = 38
TOTAL_WIDTH = 36
PERCENT_WIDTH = 47


class AnalysisError(Exception):
    """A CSV that cannot be analysed. The message never includes row content."""

    def __init__(self, code: str, message_en: str, message_es: str) -> None:
        super().__init__(message_en)
        self.code = code
        self.message_en = message_en
        self.message_es = message_es


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
    if not data or not data.strip() or b"\x00" in data:
        if data and b"\x00" in data:
            raise AnalysisError(
                "invalid_format",
                "The file is not a UTF-8 CSV.",
                "El fichero no es un CSV en UTF-8.",
            )
        raise AnalysisError(
            "empty_file",
            "The file is empty.",
            "El fichero está vacío.",
        )
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise AnalysisError(
            "invalid_format",
            "The file is not a UTF-8 CSV.",
            "El fichero no es un CSV en UTF-8.",
        ) from exc
    return _analyze_text(text, _safe_source_name(source_name))


def _analyze_text(text: str, source_name: str) -> AnalysisReport:
    lines = text.splitlines()
    if not lines or not lines[0].strip():
        raise AnalysisError("empty_file", "The file is empty.", "El fichero está vacío.")
    header_line = lines[0]
    if "," not in header_line and ";" in header_line:
        raise AnalysisError(
            "invalid_delimiter",
            "The separator must be a comma (,).",
            "El separador tiene que ser la coma (,).",
        )
    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames:
        raise AnalysisError(
            "invalid_format",
            "The CSV header is missing.",
            "El CSV no tiene fila de cabecera.",
        )
    fieldnames: list[str] = []
    for raw_name in reader.fieldnames:
        if raw_name is None or not str(raw_name).strip():
            raise AnalysisError(
                "invalid_format",
                "The CSV header has a blank column.",
                "La cabecera del CSV tiene una columna vacía.",
            )
        fieldnames.append(str(raw_name).strip())
    duplicates = sorted({name for name in fieldnames if fieldnames.count(name) > 1})
    if duplicates:
        listed = ", ".join(duplicates)
        raise AnalysisError(
            "duplicate_columns",
            f"The CSV repeats a column: {listed}.",
            f"Hay una columna repetida: {listed}.",
        )
    missing = [column for column in REQUIRED_COLUMNS if column not in fieldnames]
    if missing:
        listed = ", ".join(missing)
        raise AnalysisError(
            "missing_columns",
            f"The CSV is missing required columns: {listed}.",
            f"Faltan columnas obligatorias: {listed}.",
        )

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

    for index, raw_row in enumerate(reader):
        row = {
            (key.strip() if isinstance(key, str) else key): ("" if value is None else str(value))
            for key, value in raw_row.items()
            if isinstance(key, str)
        }
        total += 1
        flags = _flags(row)
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


def _flags(row: dict[str, str]) -> tuple[str, ...]:
    def cell(name: str) -> str:
        return row.get(name, "").strip()

    flags: list[str] = []
    if not TICKET_RE.fullmatch(cell("ticket_id")):
        flags.append("invalid_ticket_id")
    if not _valid_date(cell("date")):
        flags.append("invalid_date")
    if not cell("client_company"):
        flags.append("missing_client_company")
    if cell("category") not in CATEGORY_CODES:
        flags.append("invalid_category")
    if len(cell("description")) < 5:
        flags.append("empty_description")
    if not AGENT_RE.fullmatch(cell("agent_id")):
        flags.append("invalid_agent_id")
    status = cell("status")
    if status not in STATUS_CODES:
        flags.append("invalid_status")
    if "@" not in cell("customer_email"):
        flags.append("invalid_email")
    score = cell("satisfaction_score")
    if status == "CLOSED" and score == "":
        flags.append("closed_without_score")
    if score != "" and not (SCORE_RE.fullmatch(score) and 1 <= int(score) <= 5):
        flags.append("score_out_of_range")
    return tuple(flags)


def _valid_date(value: str) -> bool:
    if not DATE_RE.fullmatch(value):
        return False
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True


def _public_ticket_id(value: str) -> str:
    text = value.strip()
    if not text or "@" in text or any(char in text for char in "\r\n\t<>"):
        return ""
    if len(text) > 32:
        return ""
    return text


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
