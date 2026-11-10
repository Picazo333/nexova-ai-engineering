"""HTML for the supplier directory. Dynamic text is escaped."""

from __future__ import annotations

import html
import json
from datetime import date, datetime
from urllib.parse import urlencode

from app.pages import render_page
from labels import CATEGORY_LABELS, COUNTRY_LABELS, RENEWAL_WINDOW_DAYS, STATUS_LABELS
from models import ProductCategory, SupplierCurrency, SupplierQuery

NOTICES = {
    "registrado": "Proveedor registrado. Ya está en el directorio.",
    "tarifa": "Tarifa mensual actualizada. La hora del cambio quedó registrada.",
    "estado": "Estado actualizado. El proveedor sigue en el directorio.",
}


def render_directory(
    *,
    suppliers: list[dict],
    total: int,
    filters: SupplierQuery,
    error: str | None,
    notice: str | None,
    form_values: dict | None,
    locked: bool = False,
) -> str:
    main = _page(suppliers, total, filters, error, notice, form_values, locked=locked)
    return render_page(
        title="Directorio de proveedores · Nexova",
        description=(
            "Directorio de contratos externos de Nexova: país, categoría, "
            "tarifa mensual y estado active o suspended."
        ),
        main=main,
        current="suppliers",
        page_script='<script src="/js/suppliers.js"></script>',
    )


def render_fragment(
    *,
    suppliers: list[dict],
    total: int,
    filters: SupplierQuery,
) -> str:
    return _list(suppliers, total, filters)


def _page(
    suppliers: list[dict],
    total: int,
    filters: SupplierQuery,
    error: str | None,
    notice: str | None,
    form_values: dict | None,
    *,
    locked: bool = False,
) -> str:
    values = _form_defaults(form_values)
    error_hidden = "" if error else "hidden"
    notice_hidden = "" if notice else "hidden"
    state = {
        "country": filters.country.value if filters.country else "",
        "category": filters.category.value if filters.category else "",
        "status": filters.status.value if filters.status else "",
    }
    blob = json.dumps(state, ensure_ascii=False).replace("<", "\\u003c")
    return f"""
<h1>Directorio de proveedores</h1>
<p class="lead">Contratos externos de Nexova que Patricia Solís mantenía en una hoja de cálculo. Cada fila muestra el proveedor, el país del contrato, la categoría, la tarifa mensual y si está activo o suspendido.</p>
<p id="filter-memory">El país, la categoría y el estado elegidos se conservan en esta pestaña al ir a otra sección y volver.</p>
<p id="directory-status" role="status"></p>
<div id="directory-error" class="error-banner" role="alert" tabindex="-1" {error_hidden}>
  <h2>No se pudo guardar</h2>
  <p id="directory-error-text">{html.escape(error or "")}</p>
  <p class="actions"><button class="button button-secondary" id="directory-retry" type="button">Reintentar la carga del listado</button><a class="button button-secondary" href="/">Ir al inicio</a></p>
  <p>Si se repite, contacta con el soporte interno de Nexova.</p>
</div>
<p id="directory-notice" role="status" {notice_hidden}>{html.escape(notice or "")}</p>
<section class="panel" aria-labelledby="filtros-titulo">
  <h2 id="filtros-titulo">Filtrar el directorio</h2>
  <form id="directory-filters" method="get" action="/proveedores">
    <div class="filter-grid">
      <div>
        <label for="filter-country">País</label>
        <select id="filter-country" name="country">{_options(COUNTRY_LABELS, state["country"], "Todos los países")}</select>
      </div>
      <div>
        <label for="filter-category">Categoría</label>
        <select id="filter-category" name="category">{_options(CATEGORY_LABELS, state["category"], "Todas las categorías")}</select>
      </div>
      <div>
        <label for="filter-status">Estado</label>
        <select id="filter-status" name="status">{_options(STATUS_LABELS, state["status"], "Todos los estados")}</select>
      </div>
    </div>
    <p class="actions">
      <button class="button" type="submit">Aplicar filtros</button>
      <a class="button button-secondary" href="/proveedores">Quitar filtros</a>
    </p>
    <noscript><p>Sin JavaScript, Aplicar filtros recarga esta página con el listado ya filtrado.</p></noscript>
  </form>
</section>
<section aria-labelledby="listado-titulo">
  <h2 id="listado-titulo">Proveedores</h2>
  <div id="directory-list" data-state="{'locked' if locked else 'success'}" aria-busy="false" tabindex="-1">
    {_locked_list() if locked else _list(suppliers, total, filters)}
  </div>
</section>
<section class="panel" aria-labelledby="alta-titulo">
  <h2 id="alta-titulo">Registrar proveedor</h2>
  <p>Spain usa EUR y USA usa USD. Si el país y la moneda no coinciden, o la tarifa no es mayor que cero, la API rechaza el alta y no lo guarda.</p>
  <form id="create-supplier" method="post" action="/suppliers" accept-charset="utf-8">
    <div class="form-grid two">
      <div>
        <label for="supplier-name">Nombre</label>
        <input id="supplier-name" name="name" type="text" required maxlength="200" value="{html.escape(values["name"])}" autocomplete="organization">
      </div>
      <div>
        <label for="supplier-country">País del contrato</label>
        <select id="supplier-country" name="country" required>
          <option value="">Elige un país</option>
          {_options(COUNTRY_LABELS, values["country"], "")}
        </select>
      </div>
      <div>
        <label for="supplier-rate">Tarifa mensual</label>
        <input id="supplier-rate" name="monthly_rate" type="number" inputmode="decimal" min="0.01" step="0.01" required value="{html.escape(values["monthly_rate"])}">
      </div>
      <div>
        <label for="supplier-currency">Moneda</label>
        <select id="supplier-currency" name="currency" required>
          {_currency_options(values["currency"])}
        </select>
      </div>
      <div>
        <label for="supplier-status">Estado</label>
        <select id="supplier-status" name="status" required>
          {_options(STATUS_LABELS, values["status"] or "active", "")}
        </select>
      </div>
      <div>
        <label for="supplier-renewal">Fecha de renovación</label>
        <input id="supplier-renewal" name="contract_renewal_date" type="date" value="{html.escape(values["contract_renewal_date"])}" aria-describedby="renewal-hint">
        <p id="renewal-hint">Se guarda como AAAA-MM-DD. Si cae en los próximos 60 días, o ya venció, la fila lo marca.</p>
      </div>
      <div>
        <label for="supplier-email">Correo de contacto</label>
        <input id="supplier-email" name="contact_email" type="email" value="{html.escape(values["contact_email"])}" autocomplete="off">
      </div>
    </div>
    <fieldset>
      <legend>Categorías de producto</legend>
      <div class="checks">{_category_checks(values["categories"])}</div>
    </fieldset>
    <div>
      <label for="supplier-notes">Notas</label>
      <textarea id="supplier-notes" name="notes" rows="3">{html.escape(values["notes"])}</textarea>
    </div>
    <p id="create-error" role="alert" tabindex="-1" hidden></p>
    <p class="actions"><button class="button" id="create-submit" type="submit">Registrar proveedor</button></p>
    <noscript><p>Sin JavaScript el formulario envía el alta a la API y vuelve a esta página.</p></noscript>
  </form>
</section>
<script type="application/json" id="directory-state">{blob}</script>
"""


def _locked_list() -> str:
    return (
        '<div data-list-state="locked">'
        "<h3>Hace falta una sesión</h3>"
        "<p>Entra con tu correo para ver tarifas, contactos y estados. "
        "Sin token esta página no incluye esos datos.</p>"
        "</div>"
    )


def _list(suppliers: list[dict], total: int, filters: SupplierQuery) -> str:
    shown = len(suppliers)
    summary = _summary(shown, total, filters)
    if shown == 0 and total == 0:
        return (
            '<div data-list-state="empty">'
            f"<p>{html.escape(summary)}</p>"
            "<h3>El directorio está vacío</h3>"
            "<p>Registra el primer proveedor con el formulario de esta página, o carga los contratos del briefing con el seeder.</p>"
            "</div>"
        )
    if shown == 0:
        return (
            '<div data-list-state="empty">'
            f"<p>{html.escape(summary)}</p>"
            "<h3>Ningún proveedor coincide</h3>"
            "<p>No hay contratos con este país, esta categoría y este estado.</p>"
            '<p><a class="button button-secondary" href="/proveedores">Quitar filtros</a></p>'
            "</div>"
        )
    query = _query(filters)
    rows = "".join(_row(item, query) for item in suppliers)
    return (
        f'<div data-list-state="success"><p>{html.escape(summary)}</p>'
        '<div class="table-scroll" tabindex="0" aria-label="Desplazamiento horizontal del directorio de proveedores">'
        "<table>"
        "<caption>Proveedores del directorio de Nexova</caption>"
        "<thead><tr>"
        '<th scope="col">Nombre</th>'
        '<th scope="col">País</th>'
        '<th scope="col">Categorías</th>'
        '<th scope="col">Tarifa mensual</th>'
        '<th scope="col">Estado</th>'
        '<th scope="col">Actualización de tarifa</th>'
        '<th scope="col">Renovación</th>'
        '<th scope="col">Contacto y notas</th>'
        '<th scope="col">Acciones</th>'
        "</tr></thead><tbody>"
        f"{rows}</tbody></table></div>"
        "<p>Una renovación dentro de los próximos 60 días, o ya vencida, se marca con texto en la fila.</p>"
        "</div>"
    )


def _summary(shown: int, total: int, filters: SupplierQuery) -> str:
    bits: list[str] = []
    if filters.country is not None:
        bits.append(COUNTRY_LABELS[filters.country.value])
    if filters.category is not None:
        bits.append(CATEGORY_LABELS[filters.category.value])
    if filters.status is not None:
        bits.append(STATUS_LABELS[filters.status.value])
    noun = "proveedor" if shown == 1 else "proveedores"
    if bits:
        return f"{shown} {noun} con estos filtros, de {total} en el directorio. Filtro: {', '.join(bits)}."
    return f"{shown} {noun} en el directorio."


def _row(item: dict, query: str) -> str:
    supplier_id = int(item["id"])
    name = str(item["name"])
    country = str(item["country"])
    status = str(item["status"])
    categories = ", ".join(
        f"{CATEGORY_LABELS.get(code, code)} ({code})" for code in item.get("categories") or []
    )
    rate = f"{float(item['monthly_rate']):.2f} {item['currency']}"
    renewal_kind, renewal_text = _renewal(item.get("contract_renewal_date"))
    if renewal_kind == "none":
        renewal_html = html.escape(renewal_text)
    else:
        renewal_html = (
            f'<span class="badge badge-{html.escape(renewal_kind)}">{html.escape(renewal_text)}</span>'
        )
    next_status = "suspended" if status == "active" else "active"
    next_label = "Suspender" if status == "active" else "Activar"
    contact = item.get("contact_email") or ""
    notes = item.get("notes") or ""
    contact_html = "Sin correo"
    if contact:
        safe = html.escape(contact)
        contact_html = f'<a href="mailto:{safe}">{safe}</a>'
    notes_html = f"<p>{html.escape(notes)}</p>" if notes else ""
    badge = "badge-active" if status == "active" else "badge-suspended"
    action = f"/suppliers/{supplier_id}/rate{query}"
    status_action = f"/suppliers/{supplier_id}/status{query}"
    anchor = f"proveedor-{supplier_id}"
    return (
        f'<tr id="{anchor}" data-status="{html.escape(status)}" data-supplier-id="{supplier_id}">'
        f'<th scope="row">{html.escape(name)}</th>'
        f"<td>{html.escape(COUNTRY_LABELS.get(country, country))} ({html.escape(country)})</td>"
        f"<td>{html.escape(categories)}</td>"
        f'<td class="num">{html.escape(rate)}</td>'
        f'<td><span class="badge {badge}">{html.escape(STATUS_LABELS[status])} ({html.escape(status)})</span></td>'
        f"<td>{html.escape(_timestamp(str(item['updated_at'])))}</td>"
        f"<td>{renewal_html}</td>"
        f"<td>{contact_html}{notes_html}</td>"
        "<td>"
        f'<form class="rate-form" method="post" action="{html.escape(action)}" novalidate>'
        f'<label for="rate-{supplier_id}">Tarifa mensual de {html.escape(name)}</label>'
        f'<input id="rate-{supplier_id}" name="monthly_rate" type="number" inputmode="decimal" min="0.01" step="0.01" required value="{float(item["monthly_rate"]):.2f}">'
        '<button class="button" type="submit">Actualizar tarifa</button>'
        "</form>"
        f'<form class="status-form" method="post" action="{html.escape(status_action)}">'
        f'<input type="hidden" name="status" value="{next_status}">'
        f'<button class="button button-secondary" type="submit">{next_label} a {html.escape(name)}</button>'
        "</form>"
        "</td></tr>"
    )


def _renewal(value: object) -> tuple[str, str]:
    if not value:
        return "none", "Sin fecha de renovación"
    try:
        renewal = date.fromisoformat(str(value))
    except ValueError:
        return "none", str(value)
    delta = (renewal - date.today()).days
    if delta < 0:
        return "overdue", f"{renewal.isoformat()} · Renovación vencida"
    if delta == 0:
        return "upcoming", f"{renewal.isoformat()} · Renovación hoy"
    if delta <= RENEWAL_WINDOW_DAYS:
        return "upcoming", f"{renewal.isoformat()} · Renovación en {delta} días"
    return "none", renewal.isoformat()


def _timestamp(value: str) -> str:
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return value
    return parsed.strftime("%Y-%m-%d %H:%M:%S UTC")


def _query(filters: SupplierQuery) -> str:
    params: dict[str, str] = {}
    if filters.country is not None:
        params["country"] = filters.country.value
    if filters.category is not None:
        params["category"] = filters.category.value
    if filters.status is not None:
        params["status"] = filters.status.value
    if not params:
        return ""
    return "?" + urlencode(params)


def _options(labels: dict[str, str], selected: str, blank_label: str) -> str:
    parts: list[str] = []
    if blank_label:
        parts.append(f'<option value="">{html.escape(blank_label)}</option>')
    for code, label in labels.items():
        mark = " selected" if code == selected else ""
        parts.append(
            f'<option value="{html.escape(code)}"{mark}>{html.escape(label)} ({html.escape(code)})</option>'
        )
    return "".join(parts)


def _currency_options(selected: str) -> str:
    current = selected or SupplierCurrency.eur.value
    parts = []
    for item in SupplierCurrency:
        mark = " selected" if item.value == current else ""
        parts.append(f'<option value="{item.value}"{mark}>{item.value}</option>')
    return "".join(parts)


def _category_checks(selected: list[str]) -> str:
    parts = []
    chosen = set(selected)
    for item in ProductCategory:
        mark = " checked" if item.value in chosen else ""
        field_id = f"category-{item.value}"
        label = CATEGORY_LABELS[item.value]
        parts.append(
            "<label>"
            f'<input id="{field_id}" type="checkbox" name="categories" value="{item.value}"{mark}>'
            f" {html.escape(label)} ({item.value})"
            "</label>"
        )
    return "".join(parts)


def _form_defaults(form_values: dict | None) -> dict[str, str | list[str]]:
    raw = form_values or {}
    categories = raw.get("categories") or []
    if isinstance(categories, str):
        categories = [categories]
    rate = raw.get("monthly_rate")
    return {
        "name": "" if raw.get("name") is None else str(raw.get("name")),
        "country": "" if raw.get("country") is None else str(raw.get("country")),
        "categories": [str(item) for item in categories],
        "monthly_rate": "" if rate is None else str(rate),
        "currency": "" if raw.get("currency") is None else str(raw.get("currency")),
        "status": "" if raw.get("status") is None else str(raw.get("status")),
        "contract_renewal_date": ""
        if not raw.get("contract_renewal_date")
        else str(raw.get("contract_renewal_date")),
        "contact_email": "" if not raw.get("contact_email") else str(raw.get("contact_email")),
        "notes": "" if not raw.get("notes") else str(raw.get("notes")),
    }


def notice_for(code: str | None) -> str | None:
    if code is None:
        return None
    return NOTICES.get(code)
