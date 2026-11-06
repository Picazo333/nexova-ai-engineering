"""Compiled support-agent graph.

The state is one question, the retrieved payloads, an optional ticket lookup,
the answer, and a status. It does not carry the conversation. Retrieval and
generation call `retrieve` and `generate_answer` from `data/pipelines/rag.py`.
Ticket questions call the read-only incident tool. Neither path calls `query()`.

Every run compiles the graph, checkpoints each step, and writes a JSON trace
that records which source ran, and in what order.
"""

from __future__ import annotations

import logging
import os
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from typing_extensions import TypedDict

from app.agent.errors import GraphStructureError
from app.agent.routing import decide_route, parse_ticket_query
from app.agent.tools.tickets import (
    TICKET_TOOL_TIMEOUT_SECONDS,
    call_with_timeout,
    reader_for_request,
    render_ticket_answer,
)
from data.rag_settings import ROOT

logger = logging.getLogger(__name__)

ALLOWED_STATE_KEYS = {
    "question",
    "context",
    "answer",
    "error",
    "status",
    "route",
    "sources",
    "ticket",
}
HONEST_EN = "I don't have information about that."
HONEST_ES = "No tengo información sobre eso."
MAX_QUESTION_LENGTH = 2000

GenerateFn = Callable[[str, list[dict]], str]
RetrieveFn = Callable[..., list[dict]]


class AgentState(TypedDict, total=False):
    question: str
    context: list[dict]
    answer: str
    error: str
    status: str
    route: str
    sources: list[str]
    ticket: dict


@dataclass
class AgentRun:
    run_id: str
    thread_id: str
    answer: str
    error: str
    status: str
    http_status: int
    trace: dict


_SAVER: InMemorySaver | None = None


def default_checkpointer() -> InMemorySaver:
    global _SAVER
    if _SAVER is None:
        _SAVER = InMemorySaver()
    return _SAVER


def default_retrieve(question: str, **kwargs: Any) -> list[dict]:
    from data.pipelines import rag

    return rag.retrieve(question, **kwargs)


def default_generate(question: str, context: list[dict]) -> str:
    from data.pipelines import rag

    return rag.generate_answer(question, context)


def honest_message(question: str) -> str:
    if _looks_spanish(question):
        return (
            f"{HONEST_ES} La base de conocimiento no devolvió contexto "
            "por encima del umbral, así que no invento una respuesta."
        )
    return (
        f"{HONEST_EN} The knowledge base returned no context above the "
        "threshold, so no answer was invented."
    )


def _looks_spanish(question: str) -> bool:
    if any(mark in question for mark in "áéíóúñÁÉÍÓÚÑ¿¡"):
        return True
    tokens = {token.strip(".,;:!?¿¡\"'()").lower() for token in question.split()}
    return bool(tokens & {"el", "la", "los", "las", "que", "una", "del", "para", "con", "por"})


def receive_question(state: AgentState) -> dict:
    raw = state.get("question", "")
    if not isinstance(raw, str):
        return _rejection("", "La pregunta debe ser texto.", "invalid_question")
    question = raw.strip()
    if not question:
        return _rejection("", "Escribe una pregunta antes de consultar.", "empty_question")
    if len(question) > MAX_QUESTION_LENGTH:
        return _rejection(
            question,
            "La pregunta supera el máximo de 2000 caracteres.",
            "invalid_question",
        )
    return {
        "question": question,
        "context": [],
        "answer": "",
        "error": "",
        "status": "received",
        "route": "",
        "sources": [],
        "ticket": {"outcome": "not_called", "tickets": [], "message": ""},
    }


def _rejection(question: str, error: str, status: str) -> dict:
    return {
        "question": question,
        "context": [],
        "answer": "",
        "error": error,
        "status": status,
    }


def route_after_receive(state: AgentState) -> str:
    if state.get("status") in {"empty_question", "invalid_question"}:
        return "refuse_empty"
    if not str(state.get("question") or "").strip():
        return "refuse_empty"
    return "route_sources"


def refuse_empty(state: AgentState) -> dict:
    status = state.get("status") or "empty_question"
    if status not in {"empty_question", "invalid_question"}:
        status = "empty_question"
    return {
        "answer": "",
        "error": state.get("error") or "Escribe una pregunta antes de consultar.",
        "status": status,
    }


def _with_rag(state: AgentState) -> list[str]:
    sources = [str(item) for item in (state.get("sources") or [])]
    if "rag" not in sources:
        sources.append("rag")
    return sources


def make_retrieve(retrieve_fn: RetrieveFn) -> Callable[[AgentState], dict]:
    def retrieve_context(state: AgentState) -> dict:
        from data.rag_errors import RagError
        from data.rag_settings import load_settings

        sources = _with_rag(state)
        settings = load_settings()
        try:
            chunks = retrieve_fn(
                state.get("question") or "",
                k=settings.top_k,
                min_score=settings.min_score,
            )
        except RagError:
            if state.get("route") != "both":
                raise
            return {"context": [], "sources": sources, "status": "retrieved", "error": ""}
        if not isinstance(chunks, list):
            raise TypeError("retrieve() devolvió un valor que no es una lista.")
        clean: list[dict] = []
        for item in chunks:
            if not isinstance(item, dict):
                raise TypeError("retrieve() devolvió un fragmento que no es un objeto.")
            payload = dict(item)
            payload.pop("score", None)
            clean.append(payload)
        return {"context": clean, "sources": sources, "status": "retrieved", "error": ""}

    return retrieve_context


def route_after_retrieve(state: AgentState) -> str:
    if state.get("context"):
        return "generate_answer"
    return "insufficient_context"


def insufficient_context(state: AgentState) -> dict:
    return {
        "answer": honest_message(state.get("question") or ""),
        "error": "",
        "status": "insufficient_context",
    }


def make_generate(generate_fn: GenerateFn) -> Callable[[AgentState], dict]:
    def generate_answer_node(state: AgentState) -> dict:
        from data.rag_errors import GenerationCallFailed, RagError

        try:
            answer = generate_fn(state.get("question") or "", list(state.get("context") or []))
            if not isinstance(answer, str) or not answer.strip():
                raise GenerationCallFailed("The generation endpoint returned an empty answer.")
        except RagError:
            if state.get("route") != "both":
                raise
            return {
                "answer": honest_message(state.get("question") or ""),
                "error": "",
                "status": "insufficient_context",
            }
        return {"answer": answer.strip(), "error": "", "status": "answered"}

    return generate_answer_node


def route_sources(state: AgentState) -> dict:
    route = decide_route(state.get("question") or "")
    if route not in {"rag", "ticket", "both"}:
        route = "rag"
    return {
        "route": route,
        "sources": [],
        "ticket": {"outcome": "not_called", "tickets": [], "message": ""},
        "status": "routed",
        "error": "",
    }


def route_after_decision(state: AgentState) -> str:
    if state.get("route") in {"ticket", "both"}:
        return "lookup_ticket"
    return "retrieve_context"


def make_lookup(reader: Any, timeout: float) -> Callable[[AgentState], dict]:
    def lookup_ticket(state: AgentState) -> dict:
        query = parse_ticket_query(state.get("question") or "")
        result = call_with_timeout(lambda: reader.lookup(query), timeout)
        sources = [str(item) for item in (state.get("sources") or [])]
        if "ticket_tool" not in sources:
            sources.append("ticket_tool")
        return {
            "ticket": result,
            "sources": sources,
            "status": "ticket_checked",
            "error": "",
        }

    return lookup_ticket


def route_after_lookup(state: AgentState) -> str:
    if state.get("route") == "both":
        return "retrieve_context"
    return "report_ticket"


def report_ticket(state: AgentState) -> dict:
    ticket = state.get("ticket") if isinstance(state.get("ticket"), dict) else {}
    answer = render_ticket_answer(ticket, state.get("question") or "")
    status = "answered" if ticket.get("outcome") == "found" else "ticket_unavailable"
    return {"answer": answer, "error": "", "status": status}


def route_after_generate(state: AgentState) -> str:
    if state.get("route") == "both":
        return "compose_sources"
    return "finish"


def route_after_insufficient(state: AgentState) -> str:
    if state.get("route") == "both":
        return "compose_sources"
    return "finish"


def compose_sources(state: AgentState) -> dict:
    ticket = state.get("ticket") if isinstance(state.get("ticket"), dict) else {}
    question = state.get("question") or ""
    ticket_text = render_ticket_answer(ticket, question).strip()
    rag_text = str(state.get("answer") or "").strip()
    parts = [part for part in (ticket_text, rag_text) if part]
    rag_answered = state.get("status") == "answered" and bool(rag_text)
    status = "answered" if ticket.get("outcome") == "found" or rag_answered else "ticket_unavailable"
    return {"answer": "\n\n".join(parts), "error": "", "status": status}


def _guard(fn: Callable[[AgentState], dict]) -> Callable[[AgentState], dict]:
    def inner(state: AgentState) -> dict:
        _reject_unknown_keys(state, "El estado de entrada")
        update = fn(state) or {}
        _reject_unknown_keys(update, "La salida de un nodo")
        return update

    return inner


def _reject_unknown_keys(payload: dict, label: str) -> None:
    unknown = set(payload) - ALLOWED_STATE_KEYS
    if unknown:
        raise GraphStructureError(
            f"{label} tiene claves fuera del estado declarado: {', '.join(sorted(unknown))}."
        )


def assert_state_schema(schema: type) -> None:
    keys = set(getattr(schema, "__annotations__", {}) or {})
    forbidden = keys & {"messages", "history", "conversation", "chat_history", "historial"}
    if forbidden:
        raise GraphStructureError(
            "El estado no se puede compilar: arrastra historial de conversación "
            f"({', '.join(sorted(forbidden))}). Las claves permitidas son "
            f"{', '.join(sorted(ALLOWED_STATE_KEYS))}."
        )
    if keys != ALLOWED_STATE_KEYS:
        raise GraphStructureError(
            "El estado no se puede compilar: las claves tienen que ser "
            f"{', '.join(sorted(ALLOWED_STATE_KEYS))}. Llegaron "
            f"{', '.join(sorted(keys)) or 'ninguna'}."
        )


def assert_graph_structure(builder: StateGraph) -> None:
    nodes = set(builder.nodes)
    adjacency: dict[str, set[str]] = {START: set()}
    for name in nodes:
        adjacency.setdefault(name, set())
    for source, target in builder.edges:
        _require_endpoint(source, nodes)
        _require_endpoint(target, nodes)
        adjacency.setdefault(source, set()).add(target)
    for source, branches in builder.branches.items():
        _require_endpoint(source, nodes)
        destinations: list[str] = []
        for spec in branches.values():
            ends = getattr(spec, "ends", None) or {}
            if isinstance(ends, dict):
                destinations.extend(str(value) for value in ends.values())
            else:
                destinations.extend(str(value) for value in ends)
        if not destinations:
            raise GraphStructureError(
                f"El nodo {source} tiene una arista condicional sin destinos."
            )
        for target in destinations:
            _require_endpoint(target, nodes)
            adjacency.setdefault(source, set()).add(target)
    reachable = _walk(adjacency, START)
    orphans = sorted(name for name in nodes if name not in reachable)
    if orphans:
        raise GraphStructureError(
            "El grafo no se puede compilar: hay nodos sin conexión desde la entrada: "
            + ", ".join(orphans)
            + "."
        )
    reverse: dict[str, set[str]] = {}
    for source, targets in adjacency.items():
        for target in targets:
            reverse.setdefault(target, set()).add(source)
    ending = _walk(reverse, END)
    dangling = sorted(name for name in nodes if name not in ending)
    if dangling:
        raise GraphStructureError(
            "El grafo no se puede compilar: hay nodos que no alcanzan el final: "
            + ", ".join(dangling)
            + "."
        )


def _require_endpoint(name: str, nodes: set[str]) -> None:
    if name in {START, END} or name in nodes:
        return
    raise GraphStructureError(
        f"El grafo no se puede compilar: la arista apunta al nodo desconocido {name}."
    )


def _walk(adjacency: dict[str, set[str]], origin: str) -> set[str]:
    seen: set[str] = set()
    stack = [origin]
    while stack:
        current = stack.pop()
        for nxt in adjacency.get(current, ()):
            if nxt not in seen:
                seen.add(nxt)
                stack.append(nxt)
    return seen


def build_graph(
    retrieve_fn: RetrieveFn,
    generate_fn: GenerateFn,
    ticket_reader: Any,
    ticket_timeout: float,
) -> StateGraph:
    builder = StateGraph(AgentState)
    builder.add_node("receive_question", _guard(receive_question))
    builder.add_node("route_sources", _guard(route_sources))
    builder.add_node("retrieve_context", _guard(make_retrieve(retrieve_fn)))
    builder.add_node("lookup_ticket", _guard(make_lookup(ticket_reader, ticket_timeout)))
    builder.add_node("report_ticket", _guard(report_ticket))
    builder.add_node("generate_answer", _guard(make_generate(generate_fn)))
    builder.add_node("compose_sources", _guard(compose_sources))
    builder.add_node("refuse_empty", _guard(refuse_empty))
    builder.add_node("insufficient_context", _guard(insufficient_context))
    builder.add_edge(START, "receive_question")
    builder.add_conditional_edges(
        "receive_question",
        route_after_receive,
        {"route_sources": "route_sources", "refuse_empty": "refuse_empty"},
    )
    builder.add_conditional_edges(
        "route_sources",
        route_after_decision,
        {"retrieve_context": "retrieve_context", "lookup_ticket": "lookup_ticket"},
    )
    builder.add_conditional_edges(
        "lookup_ticket",
        route_after_lookup,
        {"retrieve_context": "retrieve_context", "report_ticket": "report_ticket"},
    )
    builder.add_conditional_edges(
        "retrieve_context",
        route_after_retrieve,
        {
            "generate_answer": "generate_answer",
            "insufficient_context": "insufficient_context",
        },
    )
    builder.add_conditional_edges(
        "generate_answer",
        route_after_generate,
        {"compose_sources": "compose_sources", "finish": END},
    )
    builder.add_conditional_edges(
        "insufficient_context",
        route_after_insufficient,
        {"compose_sources": "compose_sources", "finish": END},
    )
    builder.add_edge("report_ticket", END)
    builder.add_edge("compose_sources", END)
    builder.add_edge("refuse_empty", END)
    return builder


def compile_builder(
    builder: StateGraph,
    *,
    schema: type = AgentState,
    checkpointer: InMemorySaver | None = None,
    interrupt_after: list[str] | None = None,
):
    """Compile only after the state and the edges have been checked."""

    assert_state_schema(schema)
    assert_graph_structure(builder)
    kwargs: dict = {}
    if checkpointer is not None:
        kwargs["checkpointer"] = checkpointer
    if interrupt_after:
        kwargs["interrupt_after"] = interrupt_after
    try:
        return builder.compile(**kwargs)
    except GraphStructureError:
        raise
    except Exception as exc:
        raise GraphStructureError(f"El grafo no se pudo compilar: {exc}") from exc


def _transport_name(reader: Any) -> str:
    name = type(reader).__name__
    if name == "HttpIncidentReader":
        return "http"
    if name == "InProcessIncidentReader":
        return "in_process"
    if name == "DeniedReader":
        return "denied"
    return "injected"


def compile_agent(
    *,
    retrieve_fn: RetrieveFn | None = None,
    generate_fn: GenerateFn | None = None,
    checkpointer: InMemorySaver | None = None,
    interrupt_after: list[str] | None = None,
    ticket_reader: Any | None = None,
    ticket_timeout: float | None = None,
    access_token: str | None = None,
):
    timeout = TICKET_TOOL_TIMEOUT_SECONDS if ticket_timeout is None else float(ticket_timeout)
    reader = ticket_reader if ticket_reader is not None else reader_for_request(access_token, timeout)
    builder = build_graph(
        retrieve_fn or default_retrieve,
        generate_fn or default_generate,
        reader,
        timeout,
    )
    compiled = compile_builder(
        builder,
        checkpointer=checkpointer if checkpointer is not None else default_checkpointer(),
        interrupt_after=interrupt_after,
    )
    compiled.ticket_transport = _transport_name(reader)  # type: ignore[attr-defined]
    return compiled


def run_agent(
    question: str,
    *,
    retrieve_fn: RetrieveFn | None = None,
    generate_fn: GenerateFn | None = None,
    checkpointer: InMemorySaver | None = None,
    thread_id: str | None = None,
    trace_dir: Path | str | None = None,
    interrupt_after: list[str] | None = None,
    metadata: dict | None = None,
    ticket_reader: Any | None = None,
    ticket_timeout: float | None = None,
    access_token: str | None = None,
) -> AgentRun:
    compiled = compile_agent(
        retrieve_fn=retrieve_fn,
        generate_fn=generate_fn,
        checkpointer=checkpointer,
        interrupt_after=interrupt_after,
        ticket_reader=ticket_reader,
        ticket_timeout=ticket_timeout,
        access_token=access_token,
    )
    return execute(
        compiled,
        question,
        thread_id or str(uuid.uuid4()),
        trace_dir=trace_dir,
        metadata=metadata,
    )


def execute(
    compiled: Any,
    question: str,
    thread_id: str,
    *,
    trace_dir: Path | str | None = None,
    metadata: dict | None = None,
) -> AgentRun:
    return _drive(compiled, {"question": question}, thread_id, trace_dir=trace_dir, metadata=metadata)


def resume_agent(
    compiled: Any,
    thread_id: str,
    *,
    trace_dir: Path | str | None = None,
    metadata: dict | None = None,
) -> AgentRun:
    return _drive(compiled, None, thread_id, trace_dir=trace_dir, metadata=metadata)


def _drive(
    compiled: Any,
    graph_input: dict | None,
    thread_id: str,
    *,
    trace_dir: Path | str | None,
    metadata: dict | None,
) -> AgentRun:
    run_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    executed: list[dict] = []
    values: dict = {}
    try:
        for update in compiled.stream(graph_input, config, stream_mode="updates"):
            for name, payload in update.items():
                if name.startswith("__"):
                    continue
                executed.append({"node": name, "output": _public_output(payload)})
        snapshot = compiled.get_state(config)
        values = dict(snapshot.values or {})
        if snapshot.next:
            status = "paused"
            answer = str(values.get("answer") or "")
            error = ""
        else:
            status = str(values.get("status") or "failed")
            answer = str(values.get("answer") or "")
            error = str(values.get("error") or "")
    except Exception as exc:
        status, error = _classify(exc)
        answer = ""
        executed.append({"node": "error", "output": {"status": status, "error": error}})
        logger.warning("agent run failed status=%s", status)
        snapshot = None
    trace = _trace_document(
        run_id=run_id,
        thread_id=thread_id,
        question=_question_from(graph_input, executed),
        status=status,
        answer=answer,
        error=error,
        nodes=executed,
        compiled=compiled,
        config=config,
        metadata=metadata,
        state_values=values,
        ticket_transport=str(getattr(compiled, "ticket_transport", "") or ""),
    )
    save_trace(trace, resolve_trace_dir(trace_dir))
    return AgentRun(
        run_id=run_id,
        thread_id=thread_id,
        answer=answer,
        error=error,
        status=status,
        http_status=_http_status(status, answer),
        trace=trace,
    )


def _question_from(graph_input: dict | None, nodes: list[dict]) -> str:
    if isinstance(graph_input, dict):
        raw = graph_input.get("question", "")
        return raw if isinstance(raw, str) else ""
    for item in nodes:
        output = item.get("output") or {}
        if item.get("node") == "receive_question" and output.get("question"):
            return str(output["question"])
    return ""


def _public_output(payload: Any) -> dict:
    if not isinstance(payload, dict):
        return {}
    _reject_unknown_keys(payload, "La salida de un nodo")
    output = dict(payload)
    context = output.get("context")
    if isinstance(context, list):
        output["context"] = [_public_chunk(item) for item in context]
    ticket = output.get("ticket")
    if isinstance(ticket, dict):
        output["ticket"] = _public_ticket(ticket)
    sources = output.get("sources")
    if isinstance(sources, list):
        output["sources"] = [str(item) for item in sources if str(item) in {"rag", "ticket_tool"}]
    return output


def _public_ticket(payload: dict) -> dict:
    from app.agent.tools.tickets import PUBLIC_FIELDS

    tickets = []
    raw_rows = payload.get("tickets")
    if isinstance(raw_rows, list):
        for row in raw_rows:
            if not isinstance(row, dict):
                continue
            tickets.append({key: row[key] for key in PUBLIC_FIELDS if isinstance(row.get(key), str)})
    return {
        "outcome": str(payload.get("outcome") or ""),
        "message": str(payload.get("message") or ""),
        "tickets": tickets,
    }


def _public_chunk(item: Any) -> dict:
    if not isinstance(item, dict):
        return {}
    chunk = dict(item)
    for secret in ("score", "api_key", "token", "authorization"):
        chunk.pop(secret, None)
    return chunk


def _classify(exc: Exception) -> tuple[str, str]:
    from data.rag_errors import (
        EmbeddingCallFailed,
        EmbeddingNotConfigured,
        GenerationCallFailed,
        GenerationNotConfigured,
        ModelIdConflict,
        RagError,
    )

    if isinstance(exc, GenerationNotConfigured):
        return "generation_not_configured", str(exc)
    if isinstance(exc, EmbeddingNotConfigured):
        return "embedding_not_configured", str(exc)
    if isinstance(exc, (GenerationCallFailed, EmbeddingCallFailed, ModelIdConflict, RagError)):
        return "failed", str(exc)
    if isinstance(exc, GraphStructureError):
        return "failed", str(exc)
    if isinstance(exc, ValueError):
        return "failed", str(exc)
    return "failed", "El agente no pudo completar la respuesta."


def _http_status(status: str, answer: str) -> int:
    if status == "paused":
        return 200
    if status in {"answered", "insufficient_context", "ticket_unavailable"} and answer.strip():
        return 200
    if status in {"empty_question", "invalid_question"}:
        return 422
    if status in {"generation_not_configured", "embedding_not_configured"}:
        return 503
    return 502


def _trace_document(
    *,
    run_id: str,
    thread_id: str,
    question: str,
    status: str,
    answer: str,
    error: str,
    nodes: list[dict],
    compiled: Any,
    config: dict,
    metadata: dict | None,
    state_values: dict | None = None,
    ticket_transport: str = "",
) -> dict:
    numbered = []
    for index, item in enumerate(nodes, start=1):
        numbered.append({"order": index, "node": item["node"], "output": item["output"]})
    checkpoints = _checkpoints(compiled, config)
    values = state_values or {}
    route = _route_from(numbered, values)
    document = {
        "run_id": run_id,
        "thread_id": thread_id,
        "question": question,
        "status": status,
        "answer": answer,
        "error": error,
        "nodes": numbered,
        "checkpoints": checkpoints,
        "checkpoint_count": len(checkpoints),
        "generation_mode": "pipeline",
        "retrieval_mode": "pipeline",
        "route": route,
        "sources": _sources_from(numbered, values),
    }
    if metadata:
        document.update(metadata)
    document["route"] = route
    document["sources"] = _sources_from(numbered, values)
    if route in {"ticket", "both"} and ticket_transport:
        document["ticket_transport"] = ticket_transport
    return document


def _route_from(nodes: list[dict], values: dict) -> str:
    route = str(values.get("route") or "")
    if route in {"rag", "ticket", "both"}:
        return route
    for item in nodes:
        output = item.get("output") or {}
        if item.get("node") == "route_sources" and str(output.get("route") or "") in {"rag", "ticket", "both"}:
            return str(output["route"])
    return ""


def _sources_from(nodes: list[dict], values: dict) -> list[str]:
    stored = values.get("sources")
    if isinstance(stored, list) and stored:
        return [str(item) for item in stored if str(item) in {"rag", "ticket_tool"}]
    found: list[str] = []
    for item in nodes:
        output = item.get("output") or {}
        for name in output.get("sources") or []:
            text = str(name)
            if text in {"rag", "ticket_tool"} and text not in found:
                found.append(text)
    return found


def _checkpoints(compiled: Any, config: dict) -> list[dict]:
    try:
        snapshots = list(compiled.get_state_history(config))
    except Exception:
        logger.warning("checkpoint history unavailable")
        return []
    rows = []
    for snapshot in reversed(snapshots):
        values = dict(snapshot.values or {})
        metadata = dict(snapshot.metadata or {})
        rows.append(
            {
                "step": metadata.get("step"),
                "source": metadata.get("source"),
                "next": [str(item) for item in snapshot.next],
                "status": str(values.get("status") or ""),
                "context_count": len(values.get("context") or []),
                "has_answer": bool(values.get("answer")),
            }
        )
    return rows


def resolve_trace_dir(trace_dir: Path | str | None) -> Path:
    if trace_dir is not None and str(trace_dir).strip():
        path = Path(trace_dir)
    else:
        raw = os.environ.get("AGENT_TRACE_DIR", "").strip()
        path = Path(raw) if raw else ROOT / "data" / "agent_traces"
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_trace(trace: dict, directory: Path) -> Path:
    run_id = str(trace.get("run_id") or "")
    if not _is_uuid(run_id):
        raise ValueError("run_id must be a UUID.")
    destination = directory / f"{run_id}.json"
    import json

    destination.write_text(json.dumps(trace, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return destination


def load_trace(run_id: str, directory: Path | None = None) -> dict | None:
    if not _is_uuid(run_id):
        return None
    path = resolve_trace_dir(directory) / f"{run_id}.json"
    if not path.is_file():
        return None
    import json

    return json.loads(path.read_text(encoding="utf-8"))


def _is_uuid(value: str) -> bool:
    try:
        uuid.UUID(value)
    except ValueError:
        return False
    return True
