"""Decide whether a question needs the knowledge base, the ticket tool, or both.

The decision reads the question text. It does not call a model and it does not
ask the user to name a source.
"""

from __future__ import annotations

import re
import unicodedata

_UUID = re.compile(
    r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b"
)
_ID_AFTER = re.compile(
    r"\b(?:ticket|tickets|incidencia|incidencias|incidente|incidentes|incident|incidents)"
    r"\s+#?([A-Za-z0-9_-]{1,80})\b",
    re.IGNORECASE,
)

_TICKET_TOKENS = {
    "ticket",
    "tickets",
    "incidencia",
    "incidencias",
    "incidente",
    "incidentes",
}
_INCIDENT_TOKENS = {"incident", "incidents"}
_STATUS_CUES = {"status", "estado", "estados"}
_POLICY_TOKENS = {
    "fee",
    "fees",
    "tarifa",
    "tarifas",
    "precio",
    "precios",
    "price",
    "pricing",
    "cost",
    "cuesta",
    "cuestan",
    "sla",
    "policy",
    "policies",
    "politica",
    "politicas",
    "procedimiento",
    "procedimientos",
    "procedure",
    "procedures",
    "proceso",
    "procesos",
    "process",
    "training",
    "formacion",
    "objection",
    "objections",
    "objecion",
    "objeciones",
    "warranty",
    "garantia",
    "headhunting",
    "knowledge",
}
_STATUS_ALIASES = {
    "open": "open",
    "abierta": "open",
    "abiertas": "open",
    "abierto": "open",
    "abiertos": "open",
    "in_progress": "in_progress",
    "progress": "in_progress",
    "progreso": "in_progress",
    "resolved": "resolved",
    "resuelta": "resolved",
    "resueltas": "resolved",
    "resuelto": "resolved",
    "resueltos": "resolved",
    "discarded": "discarded",
    "descartada": "discarded",
    "descartadas": "discarded",
    "descartado": "discarded",
    "descartados": "discarded",
}


def _fold(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(char for char in decomposed if not unicodedata.combining(char))


def tokens_of(question: str) -> set[str]:
    folded = _fold(question).lower()
    found: set[str] = set()
    for raw in folded.split():
        token = raw.strip(".,;:!?¿¡\"'()[]{}#")
        if token:
            found.add(token)
    return found


def _known_filter_token(token: str) -> bool:
    if token in _STATUS_ALIASES or token in _STATUS_CUES:
        return True
    try:
        from app.agent.tools.tickets import known_filter_codes
    except Exception:
        return False
    return token in known_filter_codes()


def extract_ticket_id(question: str) -> str:
    match = _UUID.search(question)
    if match:
        return match.group(0)
    found = _ID_AFTER.search(question)
    if not found:
        return ""
    token = found.group(1)
    if not any(char.isdigit() for char in token):
        return ""
    if _known_filter_token(token.lower()):
        return ""
    return token


def extract_filters(question: str) -> dict[str, str]:
    tokens = tokens_of(question)
    filters: dict[str, str] = {}
    for token in tokens:
        code = _STATUS_ALIASES.get(token)
        if code and "status" not in filters:
            filters["status"] = code
    try:
        from app.agent.tools.tickets import known_filter_codes
    except Exception:
        return filters
    allowed = known_filter_codes()
    for field, codes in allowed.items():
        if field == "status":
            continue
        for token in tokens:
            if token in codes and field not in filters:
                filters[field] = token
    return filters


def parse_ticket_query(question: str) -> dict[str, str]:
    """Tool input. A ticket id wins over list filters when both are present."""

    query: dict[str, str] = {}
    ticket_id = extract_ticket_id(question)
    if ticket_id:
        query["ticket_id"] = ticket_id
        return query
    query.update(extract_filters(question))
    return query


def has_ticket_signal(question: str) -> bool:
    tokens = tokens_of(question)
    if tokens & _TICKET_TOKENS:
        return True
    if extract_ticket_id(question):
        return True
    if tokens & _INCIDENT_TOKENS and (tokens & _STATUS_CUES or extract_ticket_id(question)):
        return True
    return False


def has_policy_signal(question: str) -> bool:
    tokens = tokens_of(question)
    if tokens & _POLICY_TOKENS:
        return True
    return "sla" in _fold(question).lower()


def decide_route(question: str) -> str:
    """Return ``rag``, ``ticket``, or ``both``."""

    ticket = has_ticket_signal(question)
    policy = has_policy_signal(question)
    if ticket and policy:
        return "both"
    if ticket:
        return "ticket"
    return "rag"
