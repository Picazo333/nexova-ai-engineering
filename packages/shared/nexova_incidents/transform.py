"""CSV row to incident model, using the Nexova briefing maps.

``ticket_id`` is only the idempotency key. It is not a field of the model.
"""

from __future__ import annotations

from dataclasses import dataclass

from nexova_incidents.csv_rules import RULE_LABELS_ES, csv_rows, public_ticket_id, row_flags

CSV_STATUS_TO_MODEL = {
    "OPEN": "open",
    "CLOSED": "resolved",
    "DISCARDED": "discarded",
}

CSV_CATEGORY_TO_MODEL = {
    "TECHNICAL": "technical_failure",
    "BILLING": "process_error",
    "ACCESS": "technical_failure",
    "HR_QUERY": "process_error",
    "COMPLAINT": "client_complaint",
}

TITLE_LIMIT = 120


@dataclass(frozen=True)
class RejectedRow:
    line_number: int
    ticket_id: str
    messages: tuple[str, ...]


@dataclass(frozen=True)
class PreparedRow:
    line_number: int
    title: str
    description: str
    category: str
    status: str
    origin: str
    branch: str
    created_at: str
    updated_at: str
    source_key: str


@dataclass(frozen=True)
class SeedPlan:
    accepted: tuple[PreparedRow, ...]
    rejected: tuple[RejectedRow, ...]


def idempotency_key(ticket_id: str, title: str, created_at: str) -> str:
    """Prefer the CSV ticket id. Without one, title plus creation time."""
    ticket = ticket_id.strip()
    if ticket:
        return f"ticket:{ticket}"
    return f"fallback:{title}|{created_at}"


def prepare_csv(data: bytes) -> SeedPlan:
    """Validate with the analyzer rules, then map the rows that pass.

    File-level problems raise AnalysisError. A row that fails validation or
    cannot be mapped is listed in ``rejected`` and is not accepted.
    """
    rows = csv_rows(data)
    accepted: list[PreparedRow] = []
    rejected: list[RejectedRow] = []
    for index, row in enumerate(rows):
        line_number = index + 2
        ticket = public_ticket_id(row.get("ticket_id", ""))
        flags = row_flags(row)
        if flags:
            rejected.append(
                RejectedRow(
                    line_number=line_number,
                    ticket_id=ticket,
                    messages=tuple(RULE_LABELS_ES[code] for code in flags),
                )
            )
            continue
        prepared, problem = _map_row(row, line_number, ticket)
        if problem is not None:
            rejected.append(problem)
            continue
        accepted.append(prepared)
    return SeedPlan(accepted=tuple(accepted), rejected=tuple(rejected))


def _map_row(row: dict[str, str], line_number: int, ticket: str) -> tuple[PreparedRow | None, RejectedRow | None]:
    description = row.get("description", "")
    title = description[:TITLE_LIMIT].strip()
    if not title:
        return None, RejectedRow(
            line_number=line_number,
            ticket_id=ticket,
            messages=("El título queda vacío al recortar la descripción.",),
        )
    status = CSV_STATUS_TO_MODEL.get(row.get("status", "").strip())
    if status is None:
        return None, RejectedRow(
            line_number=line_number,
            ticket_id=ticket,
            messages=("El estado del CSV no tiene equivalente en el gestor.",),
        )
    category = CSV_CATEGORY_TO_MODEL.get(row.get("category", "").strip())
    if category is None:
        return None, RejectedRow(
            line_number=line_number,
            ticket_id=ticket,
            messages=("La categoría del CSV no tiene equivalente en el gestor.",),
        )
    created_at = f"{row.get('date', '').strip()}T00:00:00Z"
    return (
        PreparedRow(
            line_number=line_number,
            title=title,
            description=description,
            category=category,
            status=status,
            origin="customer",
            branch="central",
            created_at=created_at,
            updated_at=created_at,
            source_key=idempotency_key(ticket, title, created_at),
        ),
        None,
    )
