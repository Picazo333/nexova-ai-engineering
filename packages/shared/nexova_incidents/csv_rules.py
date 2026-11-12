"""Row and file checks for the Nexova support-ticket CSV.

These are the analyzer rules. A row that fails here is not a historical
incident. Messages never include cell values or email addresses.
"""

from __future__ import annotations

import csv
import io
import re
from datetime import date

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
RULE_LABELS_ES = {code: label_es for code, _en, label_es in RULES}


class AnalysisError(Exception):
    """A CSV that cannot be analysed. The message never includes row content."""

    def __init__(self, code: str, message_en: str, message_es: str) -> None:
        super().__init__(message_en)
        self.code = code
        self.message_en = message_en
        self.message_es = message_es


def csv_rows(data: bytes) -> list[dict[str, str]]:
    """Decode a ticket CSV and return one dict per data row.

    Raises AnalysisError for an empty file, a bad encoding, or a header that
    does not match the analyzer contract. An empty record list means the
    header was valid and there were no data rows.
    """
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
    return rows_from_text(text)


def rows_from_text(text: str) -> list[dict[str, str]]:
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
    rows: list[dict[str, str]] = []
    for raw_row in reader:
        row = {
            (key.strip() if isinstance(key, str) else key): ("" if value is None else str(value))
            for key, value in raw_row.items()
            if isinstance(key, str)
        }
        rows.append(row)
    return rows


def row_flags(row: dict[str, str]) -> tuple[str, ...]:
    """Return the analyzer rule codes that this row breaks. Empty means valid."""

    def cell(name: str) -> str:
        return row.get(name, "").strip()

    flags: list[str] = []
    if not TICKET_RE.fullmatch(cell("ticket_id")):
        flags.append("invalid_ticket_id")
    if not valid_date(cell("date")):
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


def valid_date(value: str) -> bool:
    if not DATE_RE.fullmatch(value):
        return False
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True


def public_ticket_id(value: str) -> str:
    text = value.strip()
    if not text or "@" in text or any(char in text for char in "\r\n\t<>"):
        return ""
    if len(text) > 32:
        return ""
    return text
