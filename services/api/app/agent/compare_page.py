"""Side-by-side page for one RAG run and one ticket-tool run."""

from __future__ import annotations

import html
from pathlib import Path

_PAGE = Path(__file__).resolve().parents[4] / "uis" / "agent-compare" / "index.html"

_IDLE_BODY = "<p>Todavía no hay una corrida en esta columna. Escribe la pregunta y consulta.</p>"
_IDLE_TRACE = "<p>La traza aparece aquí cuando la corrida termina.</p>"


def render_compare_page(
    *,
    rag: dict | None = None,
    tool: dict | None = None,
    rag_question: str = "",
    tool_question: str = "",
) -> str:
    template = _PAGE.read_text(encoding="utf-8")
    replacements = {
        "__RAG_STATE__": _state(rag),
        "__TOOL_STATE__": _state(tool),
        "__RAG_QUESTION__": html.escape(rag_question),
        "__TOOL_QUESTION__": html.escape(tool_question),
        "__RAG_BODY__": _body(rag),
        "__TOOL_BODY__": _body(tool),
        "__RAG_TRACE__": _trace(rag),
        "__TOOL_TRACE__": _trace(tool),
    }
    for key, value in replacements.items():
        template = template.replace(key, value)
    return template


def render_submitted_page(*, lane: str, question: str, access_token: str | None) -> str:
    column = _run(question, access_token)
    if lane == "tool":
        return render_compare_page(tool=column, tool_question=question)
    return render_compare_page(rag=column, rag_question=question)


def _run(question: str, access_token: str | None) -> dict:
    from app.agent.graph import run_agent

    result = run_agent(question, access_token=access_token)
    if result.http_status == 200:
        state = "empty" if result.status in {"ticket_unavailable", "insufficient_context"} else "success"
        return {"state": state, "answer": result.answer, "error": "", "trace": result.trace}
    return {
        "state": "error",
        "answer": "",
        "error": result.error or "No se pudo consultar.",
        "trace": result.trace,
    }


def _state(column: dict | None) -> str:
    if not column:
        return "idle"
    state = str(column.get("state") or "idle")
    if state not in {"idle", "loading", "success", "empty", "error"}:
        return "idle"
    return state


def _body(column: dict | None) -> str:
    if not column or column.get("state") in {None, "idle"}:
        return _IDLE_BODY
    if column.get("state") == "error":
        message = str(column.get("error") or "No se pudo consultar.")
        return (
            '<div role="alert">'
            "<p class=\"result-title\">No se pudo consultar</p>"
            f"<p>{html.escape(message)}</p>"
            "<p>Revisa la pregunta y vuelve a consultar. El texto que escribiste se conserva.</p>"
            "</div>"
        )
    answer = str(column.get("answer") or "").strip()
    if not answer:
        return _IDLE_BODY
    paragraphs = "".join(f"<p>{html.escape(line)}</p>" for line in answer.splitlines() if line.strip())
    if column.get("state") == "empty":
        return (
            "<p class=\"result-title\">Sin dato confirmado</p>"
            f"{paragraphs}"
            "<p>Puedes reintentar con otro id o volver a la base de conocimiento.</p>"
        )
    return paragraphs or _IDLE_BODY


def _trace(column: dict | None) -> str:
    trace = (column or {}).get("trace") if column else None
    if not isinstance(trace, dict):
        return _IDLE_TRACE
    sources = [str(item) for item in (trace.get("sources") or [])]
    order = " → ".join(sources) if sources else "ninguna"
    route = str(trace.get("route") or "sin ruta")
    items = []
    for step in trace.get("nodes") or []:
        if not isinstance(step, dict):
            continue
        items.append(
            f"<li><span class=\"node-name\">{html.escape(str(step.get('order')))}. "
            f"{html.escape(str(step.get('node')))}</span></li>"
        )
    return (
        f"<p>Ruta decidida: {html.escape(route)}. Fuentes en orden: {html.escape(order)}.</p>"
        f"<ol>{''.join(items)}</ol>"
    )
