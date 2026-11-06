"""HTML pages for the backoffice. Dynamic text is escaped."""

from __future__ import annotations

import html
from pathlib import Path

from app.config import BACKOFFICE_DIR

PARTIALS = BACKOFFICE_DIR / "partials"


def render_home(*, error: str | None = None, results_html: str | None = None) -> str:
    main = _read("home.html")
    if error:
        main = main.replace("<!--ERROR_HIDDEN-->", "")
        main = main.replace("<!--ERROR_MESSAGE-->", html.escape(error))
    else:
        main = main.replace("<!--ERROR_HIDDEN-->", "hidden")
        main = main.replace("<!--ERROR_MESSAGE-->", "")
    if results_html is None:
        main = main.replace("<!--RESULTS_STATE-->", "idle")
        main = main.replace("<!--RESULTS_HTML-->", _read("idle.html"))
    else:
        main = main.replace("<!--RESULTS_STATE-->", "success")
        main = main.replace("<!--RESULTS_HTML-->", results_html)
    return _layout(
        title="Análisis de incidencias de soporte · Nexova",
        description=(
            "Carga el CSV de tickets del helpdesk legado de Nexova y consulta "
            "válidos, inválidos, categoría, estado y satisfacción."
        ),
        main=main,
        current="analysis",
    )


def render_privacy() -> str:
    return _layout(
        title="Privacidad de los datos de incidencias · Nexova",
        description="Qué hace la herramienta con el CSV de tickets y qué no guarda.",
        main=_read("privacy.html"),
        current="privacy",
    )


def render_not_found(path: str) -> str:
    body = _read("not-found.html").replace("<!--PATH-->", html.escape(path))
    return _layout(
        title="Ruta no encontrada · Nexova",
        description="Esa ruta no existe en el backoffice de incidencias.",
        main=body,
        current="",
    )


def render_server_error() -> str:
    return _layout(
        title="Error de la aplicación · Nexova",
        description="La aplicación no pudo completar la operación.",
        main=_read("server-error.html"),
        current="",
    )


def render_auth_required(status: int, message: str) -> str:
    if status == 403:
        title = "No puedes hacer eso"
        description = "La sesión es válida, pero este recurso no es tuyo."
    else:
        title = "Hace falta una sesión"
        description = "Esta operación pide un token de acceso."
    safe = html.escape(message)
    body = (
        f"<h1>{html.escape(title)}</h1>"
        f"<p>{safe}</p>"
        "<p>Entra con el formulario de esta página. El token se guarda en la pestaña "
        "y cada llamada lleva la cabecera Authorization. No hay cookie de sesión.</p>"
    )
    return _layout(
        title=f"{title} · Nexova",
        description=description,
        main=body,
        current="",
    )


def render_results_fragment(payload: dict) -> str:
    """Success markup shared by the no-JS page and the fetch response."""
    source = html.escape(str(payload["source_name"]))
    summary = html.escape(str(payload["summary_es"]))
    parts = [
        '<div class="report" data-motion-node>',
        '<h2 id="report-title" tabindex="-1">Resultado</h2>',
        f'<p id="report-summary">{summary}</p>',
        _totals(payload),
        _rules(payload),
        _breakdown(
            "Desglose por categoría (registros válidos)",
            "Código",
            "Descripción",
            payload["categories"],
        ),
        _breakdown(
            "Desglose por estado (registros válidos)",
            "Estado",
            "Significado",
            payload["statuses"],
        ),
        _satisfaction(payload),
        _details(payload),
        _preview(payload),
        '<p class="actions"><a class="button" data-export href="/api/incidents/results/export">'
        "Descargar resultados CSV</a></p>",
        f'<pre id="export-csv" hidden>{html.escape(_csv_from_rows(payload["export_rows"]))}</pre>',
        "</div>",
    ]
    fragment = "".join(parts)
    if "@" in fragment or source != html.escape(str(payload["source_name"])):
        raise RuntimeError("refusing to render a fragment that contains @")
    return fragment


def _totals(payload: dict) -> str:
    rows = [
        ["Registros en el fichero", str(payload["total_records"])],
        ["Válidos", str(payload["valid_records"])],
        ["Inválidos o incompletos", str(payload["invalid_records"])],
    ]
    return _table(
        "Totales del fichero",
        ["Métrica", "Cantidad"],
        rows,
        numeric={1},
        scroll_label="Desplazamiento horizontal de los totales",
    )


def _rules(payload: dict) -> str:
    rows = [
        [item["label_es"], item["code"], str(item["count"])]
        for item in payload["invalid_breakdown"]
    ]
    table = _table(
        "Registros inválidos por tipo de problema",
        ["Problema", "Regla", "Registros"],
        rows,
        numeric={2},
        scroll_label="Desplazamiento horizontal de los registros inválidos",
    )
    note = (
        "<p>Un registro cuenta una vez en el total de inválidos, aunque active "
        "varias reglas. La tabla muestra cada regla por separado. El correo no "
        "se incluye.</p>"
    )
    return table + note


def _breakdown(caption: str, code_header: str, label_header: str, items: list[dict]) -> str:
    rows = []
    for item in items:
        percentage = item["percentage"]
        shown = "n/a" if percentage is None else f"{percentage}%"
        rows.append([item["code"], item["label_es"], str(item["count"]), shown])
    return _table(
        caption,
        [code_header, label_header, "Válidos", "Porcentaje"],
        rows,
        numeric={2, 3},
        scroll_label=f"Desplazamiento horizontal: {caption}",
    )


def _satisfaction(payload: dict) -> str:
    block = payload["satisfaction"]
    average = block["average"]
    if average is None:
        lead = "No hay tickets CLOSED válidos con puntuación."
    else:
        lead = (
            f"Puntuaciones registradas: {block['scored_records']} de "
            f"{block['closed_records']}. Media: {average} / 5.00."
        )
    rows = [
        [str(item["score"]), item["label_es"], str(item["count"])]
        for item in block["distribution"]
    ]
    table = _table(
        "Índice de satisfacción (tickets CLOSED válidos)",
        ["Puntuación", "Significado", "Tickets"],
        rows,
        numeric={0, 2},
        scroll_label="Desplazamiento horizontal del índice de satisfacción",
    )
    return f"<p>{html.escape(lead)}</p>" + table


def _details(payload: dict) -> str:
    details = payload["invalid_details"]
    if not details:
        return (
            "<h3>Detalle de registros inválidos</h3>"
            "<p>Este fichero no tiene registros inválidos.</p>"
        )
    rows = []
    for item in details:
        ticket = item["ticket_id"] or "—"
        rules = "; ".join(rule["label_es"] for rule in item["rules"])
        rows.append([str(item["line_number"]), str(item["row_number"]), ticket, rules])
    table = _table(
        "Detalle de registros inválidos",
        ["Línea del CSV", "Fila de datos", "Ticket", "Problema"],
        rows,
        numeric={0, 1},
        scroll_label="Desplazamiento horizontal del detalle de inválidos",
    )
    return "<h3>Detalle de registros inválidos</h3>" + table


def _preview(payload: dict) -> str:
    rows = [[row["metric"], row["label"], row["value"]] for row in payload["export_rows"]]
    table = _table(
        "Vista previa del CSV de exportación",
        ["metric", "label", "value"],
        rows,
        numeric=set(),
        scroll_label="Desplazamiento horizontal de la vista previa del CSV",
    )
    intro = (
        "<h3>Vista previa del CSV</h3>"
        "<p>Esta tabla es el fichero results.csv: una métrica por fila. "
        "La descarga usa el mismo contenido.</p>"
    )
    return intro + table


def _csv_from_rows(rows: list[dict]) -> str:
    # The stored CSV is authoritative. This helper is only a fallback if the
    # caller did not pass the exact text; the router overwrites the pre with
    # the stored CSV via replace after render. Kept for a complete fragment.
    lines = ["metric,label,value"]
    for row in rows:
        lines.append(",".join(_csv_cell(row[key]) for key in ("metric", "label", "value")))
    return "\n".join(lines) + "\n"


def _csv_cell(value: str) -> str:
    text = str(value)
    if any(char in text for char in ",\"\n"):
        return '"' + text.replace('"', '""') + '"'
    return text


def render_results_fragment_with_csv(payload: dict, csv_text: str) -> str:
    fragment = render_results_fragment(payload)
    start = fragment.find('<pre id="export-csv" hidden>')
    end = fragment.find("</pre>", start)
    if start < 0 or end < 0:
        raise RuntimeError("export preview is missing")
    escaped = html.escape(csv_text)
    if "@" in csv_text:
        raise RuntimeError("refusing to render a CSV that contains @")
    return fragment[: start + len('<pre id="export-csv" hidden>')] + escaped + fragment[end:]


def _table(
    caption: str,
    headers: list[str],
    rows: list[list[str]],
    *,
    numeric: set[int],
    scroll_label: str,
) -> str:
    head = "".join(
        f'<th scope="col"{_num(index, numeric)}>{html.escape(header)}</th>'
        for index, header in enumerate(headers)
    )
    body_rows = []
    for row in rows:
        cells = []
        for index, value in enumerate(row):
            tag = "th" if index == 0 else "td"
            scope = ' scope="row"' if index == 0 else ""
            cells.append(
                f"<{tag}{scope}{_num(index, numeric)}>{html.escape(str(value))}</{tag}>"
            )
        body_rows.append("<tr>" + "".join(cells) + "</tr>")
    return (
        f'<div class="table-scroll" tabindex="0" aria-label="{html.escape(scroll_label)}">'
        "<table>"
        f"<caption>{html.escape(caption)}</caption>"
        f"<thead><tr>{head}</tr></thead>"
        f"<tbody>{''.join(body_rows)}</tbody>"
        "</table></div>"
    )


def _num(index: int, numeric: set[int]) -> str:
    return ' class="num"' if index in numeric else ""


def render_page(
    *,
    title: str,
    description: str,
    main: str,
    current: str,
    page_script: str = "",
) -> str:
    return _layout(
        title=title,
        description=description,
        main=main,
        current=current,
        page_script=page_script,
    )


def _layout(*, title: str, description: str, main: str, current: str, page_script: str = "") -> str:
    template = _read("layout.html")
    main = _with_session(main)
    return (
        template.replace("{{TITLE}}", html.escape(title))
        .replace("{{DESCRIPTION}}", html.escape(description))
        .replace("{{MAIN}}", main)
        .replace("{{PAGE_SCRIPT}}", page_script)
        .replace("{{CURRENT_ANALYSIS}}", ' aria-current="page"' if current == "analysis" else "")
        .replace("{{CURRENT_SUPPLIERS}}", ' aria-current="page"' if current == "suppliers" else "")
        .replace("{{CURRENT_PRIVACY}}", ' aria-current="page"' if current == "privacy" else "")
    )


def _with_session(main: str) -> str:
    panel = _read("session.html")
    marker = "</h1>"
    if marker in main:
        return main.replace(marker, marker + panel, 1)
    return panel + main


def _read(name: str) -> str:
    return (PARTIALS / name).read_text(encoding="utf-8")


def partials_dir() -> Path:
    return PARTIALS
