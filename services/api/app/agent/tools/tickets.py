"""Read-only lookup of live incidents.

The input and the output use the public fields of the incident manager
(``GET /api/incidents`` and ``GET /api/incidents/{id}``). The default reader
calls that manager in-process, through ``incident_store``. Set
``INCIDENT_API_BASE_URL`` to call the same routes over HTTP instead.

Nothing in this module creates, updates, or deletes an incident.
"""

from __future__ import annotations

import json
import os
import sys
import threading
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Callable

# Same 3–5 s band the brief asks for. The graph uses this value unless a test
# passes a shorter one to prove the fallback.
TICKET_TOOL_TIMEOUT_SECONDS = 4.0

PUBLIC_FIELDS = (
    "id",
    "title",
    "description",
    "category",
    "status",
    "origin",
    "branch",
    "created_at",
    "updated_at",
)
FILTER_FIELDS = ("status", "origin", "branch", "category")

FALLBACK_EN = "I couldn't confirm that ticket's status right now."
FALLBACK_ES = "No pude confirmar el estado de ese ticket ahora mismo."

UrlOpen = Callable[..., Any]


def _shared_path() -> None:
    shared = Path(__file__).resolve().parents[5] / "packages" / "shared"
    text = str(shared)
    if text not in sys.path:
        sys.path.insert(0, text)


def known_filter_codes() -> dict[str, set[str]]:
    _shared_path()
    from nexova_incidents.model import BRANCH_CODES, CATEGORY_CODES, ORIGIN_CODES, STATUS_CODES

    return {
        "status": set(STATUS_CODES),
        "origin": set(ORIGIN_CODES),
        "branch": set(BRANCH_CODES),
        "category": set(CATEGORY_CODES),
    }


def empty_output(outcome: str, message: str) -> dict[str, Any]:
    return {"outcome": outcome, "tickets": [], "message": message}


def found_output(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {"outcome": "found", "tickets": [_public_row(row) for row in rows], "message": ""}


def _public_row(row: dict[str, Any]) -> dict[str, str]:
    clean: dict[str, str] = {}
    for key in PUBLIC_FIELDS:
        value = row.get(key, "")
        if not isinstance(value, str):
            continue
        clean[key] = value
    return clean


def _spanish(question: str) -> bool:
    if any(mark in question for mark in "áéíóúñÁÉÍÓÚÑ¿¡"):
        return True
    tokens = {token.strip(".,;:!?¿¡\"'()").lower() for token in question.split()}
    return bool(tokens & {"el", "la", "los", "las", "que", "una", "del", "para", "con", "por", "está", "estado"})


def _fallback(question: str) -> str:
    return FALLBACK_ES if _spanish(question) else FALLBACK_EN


def _labels(field: str, code: str) -> str:
    _shared_path()
    from nexova_incidents.model import BRANCHES, CATEGORIES, ORIGINS, STATUSES, label

    pairs = {
        "status": STATUSES,
        "category": CATEGORIES,
        "origin": ORIGINS,
        "branch": BRANCHES,
    }[field]
    return label(pairs, code)


def _one_line(row: dict[str, str], question: str) -> str:
    status = row.get("status", "")
    category = row.get("category", "")
    origin = row.get("origin", "")
    branch = row.get("branch", "")
    if _spanish(question):
        return (
            f"El ticket {row.get('id', '')} está en {status} ({_labels('status', status)}). "
            f"Categoría: {category} ({_labels('category', category)}). "
            f"Origen: {origin} ({_labels('origin', origin)}). "
            f"Sede: {branch} ({_labels('branch', branch)}). "
            f"Abierto el {row.get('created_at', '')}. "
            f"Actualizado el {row.get('updated_at', '')}. "
            f"Título: {row.get('title', '')}."
        )
    return (
        f"Ticket {row.get('id', '')} is {status} ({_labels('status', status)}). "
        f"Category: {category} ({_labels('category', category)}). "
        f"Origin: {origin} ({_labels('origin', origin)}). "
        f"Branch: {branch} ({_labels('branch', branch)}). "
        f"Opened {row.get('created_at', '')}. "
        f"Updated {row.get('updated_at', '')}. "
        f"Title: {row.get('title', '')}."
    )


def render_ticket_answer(payload: dict[str, Any], question: str) -> str:
    """Answer from the tool payload only. A failure never names a status code."""

    outcome = str(payload.get("outcome") or "")
    tickets = payload.get("tickets") if isinstance(payload.get("tickets"), list) else []
    if outcome == "found" and tickets:
        lines = []
        for row in tickets[:20]:
            if isinstance(row, dict):
                lines.append(_one_line({key: str(row.get(key) or "") for key in PUBLIC_FIELDS}, question))
        extra = len(tickets) - len(lines)
        if extra > 0:
            if _spanish(question):
                lines.append(f"Hay {extra} incidencias más en el resultado de la tool.")
            else:
                lines.append(f"{extra} more incidents are in the tool result.")
        return "\n".join(lines)
    sentence = _fallback(question)
    if outcome == "empty":
        detail = (
            "No hay incidencias que coincidan con ese filtro."
            if _spanish(question)
            else "No incidents match that filter."
        )
    elif outcome == "timeout":
        detail = (
            "El gestor de incidentes no respondió dentro del tiempo límite."
            if _spanish(question)
            else "The incident manager did not respond before the timeout."
        )
    elif outcome == "unauthorized":
        detail = (
            "El gestor de incidentes pide un token de acceso válido."
            if _spanish(question)
            else "The incident manager requires a valid access token."
        )
    elif outcome == "invalid":
        detail = (
            "La pregunta no trae un id de ticket ni un filtro que el gestor acepte."
            if _spanish(question)
            else "The question has no ticket id and no filter the incident manager accepts."
        )
    elif outcome == "not_found":
        detail = (
            "Ese id no está en el gestor de incidentes."
            if _spanish(question)
            else "That id is not in the incident manager."
        )
    else:
        detail = (
            "El gestor de incidentes no completó la consulta."
            if _spanish(question)
            else "The incident manager did not complete the lookup."
        )
    return f"{sentence} {detail}"


def call_with_timeout(action: Callable[[], dict[str, Any]], timeout: float) -> dict[str, Any]:
    """Run ``action`` and return a timeout payload if it is still going."""

    if timeout <= 0:
        raise ValueError("timeout must be a positive number of seconds")
    box: dict[str, Any] = {}

    def target() -> None:
        try:
            box["value"] = action()
        except Exception as exc:  # noqa: BLE001 — the graph turns this into a fallback
            box["error"] = exc

    worker = threading.Thread(target=target, daemon=True)
    worker.start()
    worker.join(timeout)
    if worker.is_alive():
        return empty_output("timeout", "timeout")
    if "error" in box:
        return empty_output("error", type(box["error"]).__name__)
    value = box.get("value")
    if not isinstance(value, dict):
        return empty_output("error", "bad_result")
    return value


class DeniedReader:
    """Used when the caller has no valid token. It does not touch the store."""

    def lookup(self, query: dict[str, str]) -> dict[str, Any]:
        return empty_output("unauthorized", "unauthorized")


class InProcessIncidentReader:
    """Calls ``get_incident`` / ``list_incidents`` and no write function."""

    def lookup(self, query: dict[str, str]) -> dict[str, Any]:
        ticket_id = (query.get("ticket_id") or "").strip()
        if ticket_id:
            from incident_store import get_incident

            found = get_incident(ticket_id)
            if found is None:
                return empty_output("not_found", "not_found")
            return found_output([found])
        filters = {key: query[key] for key in FILTER_FIELDS if query.get(key)}
        if not filters:
            return empty_output("invalid", "invalid")
        allowed = known_filter_codes()
        for key, value in filters.items():
            if value not in allowed[key]:
                return empty_output("invalid", "invalid")
        from incident_store import list_incidents

        rows = list_incidents(
            status=filters.get("status"),
            origin=filters.get("origin"),
            branch=filters.get("branch"),
            category=filters.get("category"),
        )
        if not rows:
            return empty_output("empty", "empty")
        return found_output(rows)


class HttpIncidentReader:
    """``GET`` the incident routes. The token comes from the caller or the env."""

    def __init__(
        self,
        base_url: str,
        token: str = "",
        timeout: float = TICKET_TOOL_TIMEOUT_SECONDS,
        urlopen: UrlOpen | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.token = token.strip()
        self.timeout = timeout
        self._urlopen = urlopen or urllib.request.urlopen

    def lookup(self, query: dict[str, str]) -> dict[str, Any]:
        ticket_id = (query.get("ticket_id") or "").strip()
        if ticket_id:
            if not _safe_id(ticket_id):
                return empty_output("invalid", "invalid")
            url = f"{self.base_url}/api/incidents/{urllib.parse.quote(ticket_id, safe='')}"
            status, payload = self._get(url)
            if status == "timeout":
                return empty_output("timeout", "timeout")
            if status == "unauthorized":
                return empty_output("unauthorized", "unauthorized")
            if status == "not_found":
                return empty_output("not_found", "not_found")
            if status != "ok" or not isinstance(payload, dict):
                return empty_output("error", status)
            return found_output([payload])
        filters = {key: query[key] for key in FILTER_FIELDS if query.get(key)}
        if not filters:
            return empty_output("invalid", "invalid")
        allowed = known_filter_codes()
        for key, value in filters.items():
            if value not in allowed[key]:
                return empty_output("invalid", "invalid")
        url = f"{self.base_url}/api/incidents?{urllib.parse.urlencode(filters)}"
        status, payload = self._get(url)
        if status == "timeout":
            return empty_output("timeout", "timeout")
        if status == "unauthorized":
            return empty_output("unauthorized", "unauthorized")
        if status != "ok" or not isinstance(payload, list):
            return empty_output("error", status)
        if not payload:
            return empty_output("empty", "empty")
        return found_output([row for row in payload if isinstance(row, dict)])

    def _get(self, url: str) -> tuple[str, Any]:
        headers = {"Accept": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        request = urllib.request.Request(url, headers=headers, method="GET")
        try:
            with self._urlopen(request, timeout=self.timeout) as response:
                raw = response.read()
        except TimeoutError:
            return "timeout", None
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                return "not_found", None
            if exc.code == 401:
                return "unauthorized", None
            return "error", None
        except urllib.error.URLError as exc:
            reason = getattr(exc, "reason", exc)
            if isinstance(reason, TimeoutError) or "timed out" in str(reason).lower():
                return "timeout", None
            return "error", None
        except Exception:
            return "error", None
        try:
            return "ok", json.loads(raw.decode("utf-8"))
        except (UnicodeError, json.JSONDecodeError):
            return "error", None


def _safe_id(value: str) -> bool:
    if not value or len(value) > 80:
        return False
    return all(char.isalnum() or char in "-_" for char in value)


def _token_allows_read(access_token: str | None) -> bool:
    if not access_token:
        return False
    try:
        from app.auth.security import AuthConfigError, TokenError, decode_access_token
        from app.auth.service import get_user_by_id
    except Exception:
        return False
    try:
        payload = decode_access_token(access_token)
    except (AuthConfigError, TokenError):
        return False
    record = get_user_by_id(str(payload.get("sub") or ""))
    return bool(record and record.get("is_active", False))


def reader_for_request(
    access_token: str | None,
    timeout: float = TICKET_TOOL_TIMEOUT_SECONDS,
) -> DeniedReader | InProcessIncidentReader | HttpIncidentReader:
    """HTTP when ``INCIDENT_API_BASE_URL`` is set; otherwise the in-process store.

    The in-process path still checks the bearer token the incident routes
    require. No token is written into the graph state.
    """

    base = os.environ.get("INCIDENT_API_BASE_URL", "").strip()
    if base:
        token = (access_token or os.environ.get("INCIDENT_API_TOKEN", "")).strip()
        return HttpIncidentReader(base, token, timeout=timeout)
    if not _token_allows_read(access_token):
        return DeniedReader()
    return InProcessIncidentReader()
