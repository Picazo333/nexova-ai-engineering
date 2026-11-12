"""HTML for incident registration, the list, and the summary."""

from __future__ import annotations

import html
import json
import sys
from pathlib import Path

_SHARED = Path(__file__).resolve().parents[3] / "packages" / "shared"
if str(_SHARED) not in sys.path:
    sys.path.insert(0, str(_SHARED))

from app.pages import render_page  # noqa: E402
from nexova_incidents.model import (  # noqa: E402
    BRANCHES,
    CATEGORIES,
    ORIGINS,
    STATUSES,
    TRANSITIONS,
    label,
)

_LABELS = {
    "statuses": [{"value": code, "label": text} for code, text in STATUSES],
    "origins": [{"value": code, "label": text} for code, text in ORIGINS],
    "branches": [{"value": code, "label": text} for code, text in BRANCHES],
    "categories": [{"value": code, "label": text} for code, text in CATEGORIES],
    "transitions": {code: sorted(targets) for code, targets in TRANSITIONS.items()},
}


def render_register(
    *,
    values: dict[str, str] | None = None,
    errors: list[dict[str, str]] | None = None,
    confirmation: str | None = None,
    form_error: str | None = None,
) -> str:
    values = values or {}
    errors = errors or []
    by_field = {item["field"]: item["message"] for item in errors}
    parts = [
        "<h1>Registrar una incidencia</h1>",
        "<p class=\"lead\">Registra un problema de un cliente, de una sede o del equipo interno. "
        "El identificador y las fechas los asigna el sistema al guardar.</p>",
        _banner("incident-form-error", form_error, "alert"),
        '<p id="incident-form-cta" class="actions"' + ("" if form_error else " hidden") + ">"
        '<a class="button button-secondary" href="/incidencias">Ir al panel</a> '
        '<a class="button button-secondary" href="/">Ir al inicio</a></p>',
        _banner("incident-confirmation", confirmation, "status"),
        "<form id=\"incident-form\" method=\"post\" action=\"/incidencias/nueva\">",
        _field("title", "Título", "text", values.get("title", ""), by_field.get("title"), maxlength="180"),
        _area("description", "Descripción", values.get("description", ""), by_field.get("description")),
        _select("category", "Categoría", CATEGORIES, values.get("category", ""), by_field.get("category"), required=True),
        _select("status", "Estado inicial", STATUSES, values.get("status", "open"), by_field.get("status"), required=True),
        _select("origin", "Origen", ORIGINS, values.get("origin", ""), by_field.get("origin"), required=True),
        _branch(values.get("branch", ""), by_field.get("branch"), values.get("origin") == "branch"),
        "<p id=\"incident-form-status\" role=\"status\"></p>",
        "<p class=\"actions\"><button class=\"button\" id=\"incident-submit\" type=\"submit\">Registrar incidencia</button></p>",
        "</form>",
        "<p>Los campos marcados se comprueban antes de enviar. Si la API rechaza un dato, el aviso queda junto a ese campo.</p>",
    ]
    return render_page(
        title="Registrar una incidencia · Nexova",
        description="Formulario para registrar una incidencia de Nexova: título, descripción, categoría, estado, origen y sede.",
        main="".join(parts),
        current="register",
        page_script='<script src="/js/incidents-manager.js"></script>',
    )


def render_panel(
    *,
    items: list[dict] | None,
    summary: dict | None,
    filters: dict[str, str],
    list_state: str,
    list_message: str | None = None,
    summary_state: str,
    summary_message: str | None = None,
) -> str:
    parts = [
        "<h1>Panel de incidencias</h1>",
        "<p class=\"lead\">Totales de la empresa y listado filtrable por estado, origen, sede y categoría.</p>",
        "<section id=\"incident-summary\" class=\"panel\" aria-labelledby=\"summary-title\" "
        f'data-state="{html.escape(summary_state)}">',
        "<h2 id=\"summary-title\">Resumen</h2>",
        '<div id="incident-summary-body">',
        _summary_body(summary, summary_state, summary_message),
        "</div></section>",
        "<section class=\"panel\" aria-labelledby=\"list-title\">",
        "<h2 id=\"list-title\">Incidencias</h2>",
        _filters(filters),
        '<p id="incident-list-status" role="status"></p>',
        '<div id="incident-list-error" class="error-banner" role="alert" tabindex="-1" hidden>',
        '<p id="incident-list-error-text"></p>',
        '<p class="actions"><button class="button button-secondary" id="incident-retry" type="button">Reintentar</button>'
        '<a class="button button-secondary" href="/">Ir al inicio</a></p>',
        "<p>Si se repite, contacta con el soporte interno de Nexova.</p>",
        "</div>",
        f'<div id="incident-list" data-state="{html.escape(list_state)}">',
        _list_body(items, list_state, list_message, filters),
        "</div></section>",
        f'<script type="application/json" id="incident-labels">{json.dumps(_LABELS, ensure_ascii=True)}</script>',
    ]
    return render_page(
        title="Panel de incidencias · Nexova",
        description="Listado de incidencias de Nexova con filtros y totales por estado, categoría, origen y sede.",
        main="".join(parts),
        current="panel",
        page_script='<script src="/js/incidents-manager.js"></script>',
    )


def _summary_body(summary: dict | None, state: str, message: str | None) -> str:
    if state == "locked":
        return "<p>Entra con tu sesión para ver los totales.</p>"
    if state == "error":
        return (
            "<div class=\"error-banner\">"
            "<p id=\"incident-summary-error\">No se pudo cargar el resumen. El listado de abajo sigue disponible.</p>"
            "<p class=\"actions\"><button class=\"button button-secondary\" id=\"incident-summary-retry\" type=\"button\">Reintentar el resumen</button>"
            "<a class=\"button button-secondary\" href=\"/\">Ir al inicio</a></p>"
            "<p>Si se repite, contacta con el soporte interno de Nexova.</p></div>"
        )
    if summary is None:
        return '<p class="loading-state">Cargando el resumen…</p>'
    groups = (
        ("Por estado", "by_status", STATUSES),
        ("Por categoría", "by_category", CATEGORIES),
        ("Por origen", "by_origin", ORIGINS),
        ("Por sede", "by_branch", BRANCHES),
    )
    blocks = ["<div class=\"summary-grid\">"]
    for title, key, pairs in groups:
        rows = [[code, str(summary[key].get(code, 0)), text] for code, text in pairs]
        blocks.append(
            _table(title, ["Código", "Total", "Significado"], rows, numeric={1}, scroll=f"Desplazamiento: {title}")
        )
    total = summary.get("total", 0)
    blocks.append(f"<p id=\"incident-summary-total\">Total de incidencias: {int(total)}.</p>")
    blocks.append("</div>")
    if message:
        blocks.append(f"<p>{html.escape(message)}</p>")
    return "".join(blocks)


def _list_body(items: list[dict] | None, state: str, message: str | None, filters: dict[str, str]) -> str:
    if state == "locked":
        return '<div data-list-state="locked"><h3>Hace falta una sesión</h3><p>Entra para ver las incidencias registradas.</p></div>'
    if state == "error":
        return (
            '<div data-list-state="error"><h3>No se pudo cargar el listado</h3>'
            f"<p>{html.escape(message or 'Inténtalo de nuevo.')}</p></div>"
        )
    if state == "loading":
        return '<div data-list-state="loading"><p>Cargando incidencias…</p></div>'
    rows = items or []
    if not rows:
        active = any(filters.values())
        if active:
            text = "Ninguna incidencia coincide con esos filtros. Quita uno o registra una incidencia nueva."
        else:
            text = "Todavía no hay incidencias. Registra la primera desde el formulario."
        return (
            '<div data-list-state="empty">'
            f"<h3>Sin incidencias para mostrar</h3><p>{html.escape(text)}</p>"
            '<p><a class="button" href="/incidencias/nueva">Registrar incidencia</a></p></div>'
        )
    body = []
    for item in rows:
        body.append(_incident_row(item))
    table = (
        '<div data-list-state="ready">'
        f"<p>Mostrando {len(rows)} incidencias con los filtros actuales.</p>"
        '<div class="table-scroll" tabindex="0" aria-label="Desplazamiento horizontal del listado de incidencias">'
        "<table><caption>Incidencias registradas</caption><thead><tr>"
        "<th scope=\"col\">Título</th><th scope=\"col\">Categoría</th><th scope=\"col\">Origen</th>"
        "<th scope=\"col\">Sede</th><th scope=\"col\">Estado</th><th scope=\"col\">Alta</th>"
        "</tr></thead><tbody>"
        + "".join(body)
        + "</tbody></table></div></div>"
    )
    return table


def _incident_row(item: dict) -> str:
    incident_id = str(item["id"])
    current = str(item["status"])
    options = [current, *sorted(TRANSITIONS.get(current, frozenset()))]
    # Keep the current value first and drop duplicates.
    seen: list[str] = []
    for code in options:
        if code not in seen:
            seen.append(code)
    option_html = []
    for code in seen:
        selected = " selected" if code == current else ""
        option_html.append(
            f'<option value="{html.escape(code)}"{selected}>{html.escape(label(STATUSES, code))}</option>'
        )
    disabled = " disabled" if not TRANSITIONS.get(current) else ""
    described = f"status-hint-{incident_id}"
    return (
        f'<tr id="incidencia-{html.escape(incident_id)}" data-id="{html.escape(incident_id)}" data-status="{html.escape(current)}">'
        f'<th scope="row">{html.escape(item["title"])}'
        f'<details><summary>Ver descripción</summary><p>{html.escape(item["description"])}</p></details></th>'
        f"<td>{html.escape(label(CATEGORIES, item['category']))}</td>"
        f"<td>{html.escape(label(ORIGINS, item['origin']))}</td>"
        f"<td>{html.escape(label(BRANCHES, item['branch']))}</td>"
        "<td>"
        f'<label for="status-{html.escape(incident_id)}">Cambiar estado</label>'
        f'<select id="status-{html.escape(incident_id)}" data-status-select '
        f'data-current="{html.escape(current)}"{disabled} aria-describedby="{described}">'
        + "".join(option_html)
        + "</select>"
        f'<p id="{described}" class="field-hint"></p>'
        "</td>"
        f'<td class="code">{html.escape(item["created_at"])}</td>'
        "</tr>"
    )


def _filters(filters: dict[str, str]) -> str:
    return (
        '<form id="incident-filters" method="get" action="/incidencias">'
        '<div class="filter-grid">'
        + _select("status", "Estado", STATUSES, filters.get("status", ""), None, required=False, blank="Todos")
        + _select("origin", "Origen", ORIGINS, filters.get("origin", ""), None, required=False, blank="Todos")
        + _select("branch", "Sede", BRANCHES, filters.get("branch", ""), None, required=False, blank="Todas")
        + _select("category", "Categoría", CATEGORIES, filters.get("category", ""), None, required=False, blank="Todas")
        + "</div>"
        '<p class="actions"><button class="button" type="submit">Aplicar filtros</button></p>'
        '<p id="filter-count-note">Los contadores del resumen son el total de la empresa. '
        "Los cuatro filtros se combinan y el listado muestra solo las coincidencias.</p>"
        "</form>"
    )


def _branch(value: str, error: str | None, highlighted: bool) -> str:
    flag = "1" if highlighted else "0"
    hidden = "" if highlighted else " hidden"
    return (
        f'<div id="branch-field" class="branch-field" data-highlight="{flag}">'
        f'<p id="branch-reminder"{hidden}>Estás reportando desde una sede concreta. Elige la oficina de Nexova.</p>'
        + _select("branch", "Sede", BRANCHES, value, error, required=True, describedby="branch-reminder")
        + "</div>"
    )


def _field(name: str, label_text: str, kind: str, value: str, error: str | None, maxlength: str) -> str:
    error_id = f"{name}-error"
    described = f' aria-describedby="{error_id}"' if error else ""
    invalid = ' aria-invalid="true"' if error else ""
    message = f'<p class="field-error" id="{error_id}">{html.escape(error)}</p>' if error else f'<p class="field-error" id="{error_id}" hidden></p>'
    return (
        "<div>"
        f'<label for="incident-{name}">{html.escape(label_text)}</label>'
        f'<input id="incident-{name}" name="{name}" type="{kind}" required maxlength="{maxlength}" '
        f'value="{html.escape(value)}"{described}{invalid}>'
        f"{message}</div>"
    )


def _area(name: str, label_text: str, value: str, error: str | None) -> str:
    error_id = f"{name}-error"
    described = f' aria-describedby="{error_id}"' if error else ""
    invalid = ' aria-invalid="true"' if error else ""
    message = f'<p class="field-error" id="{error_id}">{html.escape(error)}</p>' if error else f'<p class="field-error" id="{error_id}" hidden></p>'
    return (
        "<div>"
        f'<label for="incident-{name}">{html.escape(label_text)}</label>'
        f'<textarea id="incident-{name}" name="{name}" required maxlength="4000"{described}{invalid}>'
        f"{html.escape(value)}</textarea>{message}</div>"
    )


def _select(
    name: str,
    label_text: str,
    pairs: tuple[tuple[str, str], ...],
    value: str,
    error: str | None,
    *,
    required: bool,
    blank: str | None = "Elige una opción",
    describedby: str | None = None,
) -> str:
    error_id = f"{name}-error"
    described_ids = [item for item in (describedby, error_id if error else None) if item]
    described = f' aria-describedby="{" ".join(described_ids)}"' if described_ids else ""
    invalid = ' aria-invalid="true"' if error else ""
    required_attr = " required" if required else ""
    options = []
    if blank is not None:
        options.append(f'<option value="">{html.escape(blank)}</option>')
    for code, text in pairs:
        selected = " selected" if code == value else ""
        options.append(f'<option value="{html.escape(code)}"{selected}>{html.escape(text)}</option>')
    message = (
        f'<p class="field-error" id="{error_id}">{html.escape(error)}</p>'
        if error
        else f'<p class="field-error" id="{error_id}" hidden></p>'
    )
    prefix = "incident-" if name != "status" or required else ""
    # Filter selects use the bare name so the query string matches the API.
    field_id = f"incident-{name}" if required or name in {"title"} else f"filter-{name}"
    if name in {"category", "status", "origin", "branch"} and not required:
        field_id = f"filter-{name}"
    elif name in {"category", "status", "origin", "branch", "title", "description"}:
        field_id = f"incident-{name}"
    return (
        "<div>"
        f'<label for="{field_id}">{html.escape(label_text)}</label>'
        f'<select id="{field_id}" name="{name}"{required_attr}{described}{invalid}>'
        + "".join(options)
        + f"</select>{message}</div>"
    )


def _banner(element_id: str, message: str | None, role: str) -> str:
    kind = "confirmation" if role == "status" else "form-error error-banner"
    if not message:
        return f'<p id="{element_id}" class="{kind}" role="{role}" hidden></p>'
    return (
        f'<p id="{element_id}" class="{kind}" role="{role}" tabindex="-1" '
        f'data-just-saved="1">{html.escape(message)}</p>'
    )


def _table(caption: str, headers: list[str], rows: list[list[str]], *, numeric: set[int], scroll: str) -> str:
    head = "".join(f'<th scope="col">{html.escape(header)}</th>' for header in headers)
    body = []
    for row in rows:
        cells = []
        for index, value in enumerate(row):
            tag = "th" if index == 0 else "td"
            scope = ' scope="row"' if index == 0 else ""
            num = ' class="num"' if index in numeric else ""
            cells.append(f"<{tag}{scope}{num}>{html.escape(value)}</{tag}>")
        body.append("<tr>" + "".join(cells) + "</tr>")
    return (
        f'<div class="table-scroll" tabindex="0" aria-label="{html.escape(scroll)}">'
        f"<table><caption>{html.escape(caption)}</caption><thead><tr>{head}</tr></thead>"
        f"<tbody>{''.join(body)}</tbody></table></div>"
    )
