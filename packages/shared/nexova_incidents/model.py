"""Incident model rules for Nexova.

Field values are the database codes from the centralized-incident-manager
briefing. Display labels are the briefing sentences, in Spanish, because the
backoffice is in Spanish.
"""

from __future__ import annotations

STATUSES = (
    ("open", "Incidencia registrada, sin responsable asignado aún"),
    ("in_progress", "Asignada a un equipo o persona, en gestión activa"),
    ("resolved", "Resuelta y confirmada por quien la reportó o por el responsable"),
    ("discarded", "Registrada por error, duplicada o fuera de alcance"),
)

ORIGINS = (
    ("customer", "Reportada por un cliente corporativo"),
    ("branch", "Reportada por personal de una oficina"),
    ("internal", "Detectada por tecnología, operaciones o dirección"),
)

BRANCHES = (
    ("central", "Central — Sede Valencia"),
    ("valencia_operations", "Valencia — Operaciones"),
    ("miami_office", "Miami Office"),
    ("remote", "Remoto (empleado sin sede fija)"),
)

CATEGORIES = (
    ("technical_failure", "Fallo de sistema o herramienta tecnológica (ATS, HubSpot, Zendesk, infraestructura)"),
    ("process_error", "Error en un proceso operativo: selección, incorporación, formación, facturación"),
    ("client_complaint", "Queja o reclamación de un cliente corporativo sobre el servicio prestado"),
    ("candidate_issue", "Problema reportado por o relacionado con un candidato en proceso de selección"),
    ("staff_issue", "Incidencia interna de RRHH: ausencia, conflicto, accidente, baja"),
    ("sla_breach", "Incumplimiento de SLA comprometido con un cliente"),
    ("data_quality", "Error o inconsistencia en datos de candidatos, clientes o reportes"),
    ("other", "Cualquier incidencia que no encaje en las categorías anteriores"),
)

STATUS_CODES = {code for code, _label in STATUSES}
ORIGIN_CODES = {code for code, _label in ORIGINS}
BRANCH_CODES = {code for code, _label in BRANCHES}
CATEGORY_CODES = {code for code, _label in CATEGORIES}

# open -> in_progress | discarded; in_progress -> resolved | discarded; finals stay.
TRANSITIONS = {
    "open": frozenset({"in_progress", "discarded"}),
    "in_progress": frozenset({"resolved", "discarded"}),
    "resolved": frozenset(),
    "discarded": frozenset(),
}

CREATE_FIELDS = ("title", "description", "category", "status", "origin", "branch")
PUBLIC_FIELDS = CREATE_FIELDS + ("id", "created_at", "updated_at")
TITLE_MAX = 180
DESCRIPTION_MAX = 4000

_STATUS_LIST = ", ".join(code for code, _label in STATUSES)
_ORIGIN_LIST = ", ".join(code for code, _label in ORIGINS)
_BRANCH_LIST = ", ".join(code for code, _label in BRANCHES)
_CATEGORY_LIST = ", ".join(code for code, _label in CATEGORIES)


def label(pairs: tuple[tuple[str, str], ...], code: str) -> str:
    for value, text in pairs:
        if value == code:
            return text
    return code


def _error(field: str, message: str) -> dict[str, str]:
    return {"field": field, "message": message}


def _as_text(value: object, field: str, label_es: str) -> tuple[str | None, dict[str, str] | None]:
    if not isinstance(value, str):
        return None, _error(field, f"{label_es} tiene que ser texto.")
    return value.strip(), None


def validate_create(payload: object) -> list[dict[str, str]]:
    """Return every problem in a create body. An empty list means it can be stored."""
    if not isinstance(payload, dict):
        return [_error("body", "El cuerpo tiene que ser un objeto JSON.")]
    errors: list[dict[str, str]] = []
    unknown = [key for key in payload if key not in CREATE_FIELDS]
    for key in unknown:
        if key in {"id", "created_at", "updated_at"}:
            errors.append(_error(key, "El identificador y las fechas los asigna el sistema."))
        else:
            errors.append(_error(str(key), "Ese campo no forma parte de la incidencia."))

    title_raw = payload.get("title")
    if "title" not in payload or title_raw is None:
        errors.append(_error("title", "El título es obligatorio."))
    else:
        title, problem = _as_text(title_raw, "title", "El título")
        if problem:
            errors.append(problem)
        elif not title:
            errors.append(_error("title", "El título es obligatorio."))
        elif len(title) > TITLE_MAX:
            errors.append(_error("title", f"El título no puede pasar de {TITLE_MAX} caracteres."))

    description_raw = payload.get("description")
    if "description" not in payload or description_raw is None:
        errors.append(_error("description", "La descripción es obligatoria."))
    else:
        description, problem = _as_text(description_raw, "description", "La descripción")
        if problem:
            errors.append(problem)
        elif not description:
            errors.append(_error("description", "La descripción es obligatoria."))
        elif len(description) > DESCRIPTION_MAX:
            errors.append(
                _error("description", f"La descripción no puede pasar de {DESCRIPTION_MAX} caracteres.")
            )

    _choice(payload, "category", "La categoría", CATEGORY_CODES, _CATEGORY_LIST, errors)
    _choice(payload, "status", "El estado", STATUS_CODES, _STATUS_LIST, errors)
    _choice(payload, "origin", "El origen", ORIGIN_CODES, _ORIGIN_LIST, errors)
    _choice(payload, "branch", "La sede", BRANCH_CODES, _BRANCH_LIST, errors)
    return errors


def _choice(
    payload: dict,
    field: str,
    label_es: str,
    allowed: set[str],
    listed: str,
    errors: list[dict[str, str]],
) -> None:
    required = {
        "category": "La categoría es obligatoria.",
        "status": "El estado es obligatorio.",
        "origin": "El origen es obligatorio.",
        "branch": "La sede es obligatoria.",
    }
    if field not in payload or payload.get(field) is None or payload.get(field) == "":
        errors.append(_error(field, required[field]))
        return
    value = payload.get(field)
    if not isinstance(value, str) or value not in allowed:
        errors.append(_error(field, f"{label_es} solo puede ser: {listed}."))


def validate_filters(params: dict[str, str | None]) -> list[dict[str, str]]:
    """Empty or missing query params mean no filter. Any other value must be a code."""
    checks = (
        ("status", "El estado", STATUS_CODES, _STATUS_LIST),
        ("origin", "El origen", ORIGIN_CODES, _ORIGIN_LIST),
        ("branch", "La sede", BRANCH_CODES, _BRANCH_LIST),
        ("category", "La categoría", CATEGORY_CODES, _CATEGORY_LIST),
    )
    errors: list[dict[str, str]] = []
    for field, label_es, allowed, listed in checks:
        value = params.get(field)
        if value is None or value == "":
            continue
        if value not in allowed:
            errors.append(_error(field, f"{label_es} solo puede ser: {listed}."))
    return errors


def validate_transition(current: str, target: object) -> list[dict[str, str]]:
    if not isinstance(target, str) or target not in STATUS_CODES:
        return [_error("status", f"El estado solo puede ser: {_STATUS_LIST}.")]
    if target == current:
        return [_error("status", "Elige un estado distinto del actual.")]
    allowed = TRANSITIONS.get(current, frozenset())
    if target in allowed:
        return []
    if current == "open":
        message = "Desde abierta solo se puede pasar a en progreso o descartada."
    elif current == "in_progress":
        message = "Desde en progreso solo se puede pasar a resuelta o descartada."
    elif current == "resolved":
        message = "Una incidencia resuelta ya no cambia de estado."
    else:
        message = "Una incidencia descartada ya no cambia de estado."
    return [_error("status", message)]


def empty_summary() -> dict:
    return {
        "total": 0,
        "by_status": {code: 0 for code, _label in STATUSES},
        "by_category": {code: 0 for code, _label in CATEGORIES},
        "by_origin": {code: 0 for code, _label in ORIGINS},
        "by_branch": {code: 0 for code, _label in BRANCHES},
    }


def public_incident(stored: dict) -> dict:
    """The API shape. The seed key stays in TinyDB and is not a model field."""
    return {
        "id": stored["id"],
        "title": stored["title"],
        "description": stored["description"],
        "category": stored["category"],
        "status": stored["status"],
        "origin": stored["origin"],
        "branch": stored["branch"],
        "created_at": stored["created_at"],
        "updated_at": stored["updated_at"],
    }
