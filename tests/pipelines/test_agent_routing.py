"""Routing and fallback evals for the ticket tool.

Retrieval and generation doubles are explicit. They are not a pass of the
live-model criterion. The ticket rows come from the incident manager.
"""

import time
from pathlib import Path

from langgraph.checkpoint.memory import InMemorySaver

from app.agent.graph import run_agent
from app.agent.tools.tickets import (
    FALLBACK_EN,
    FALLBACK_ES,
    TICKET_TOOL_TIMEOUT_SECONDS,
    InProcessIncidentReader,
)

ROOT = Path(__file__).resolve().parents[2]
CORPUS = ROOT / "docs" / "company-knowledge-base"

INCIDENT = {
    "title": "La caja no emite el contrato",
    "description": "El cliente no puede descargar el contrato firmado desde el portal.",
    "category": "technical_failure",
    "status": "in_progress",
    "origin": "customer",
    "branch": "central",
}


def _store(tmp_path, monkeypatch):
    monkeypatch.setenv("INCIDENTS_DATA_DIR", str(tmp_path / "incidents"))
    from incident_store import create_incident, reset_incidents_db

    reset_incidents_db()
    return create_incident(INCIDENT)


def _policy_chunk() -> dict:
    text = (CORPUS / "nexova-objection-handling.en.md").read_text(encoding="utf-8")
    return {
        "company": "nexova",
        "source_document": "objection-handling",
        "section": "Fee objection",
        "language": "en",
        "chunk_index": 0,
        "text": text,
    }


def test_committed_side_by_side_traces_show_rag_then_tool():
    import json

    document = json.loads((ROOT / "docs" / "langgraph" / "traces-side-by-side.json").read_text(encoding="utf-8"))
    assert document["live_generation"] == "live"
    assert document["live_source"] == "evidence/llm-live/02-api-agent-query.txt"
    assert document["ticket_transport"] == "in_process"
    by_label = {item["label"]: item["trace"] for item in document["columns"]}
    rag = by_label["rag"]
    ticket = by_label["ticket_tool"]
    assert rag["sources"] == ["rag"]
    assert rag["generation_mode"] == "pipeline"
    assert rag["run_id"] == "6f2faf5b-3ee5-4f61-973b-7027108e1a6e"
    assert "22%" in rag["answer"] and "Marcos" in rag["answer"]
    assert "lookup_ticket" not in [item["node"] for item in rag["nodes"]]
    assert ticket["sources"] == ["ticket_tool"]
    assert "retrieve_context" not in [item["node"] for item in ticket["nodes"]]
    stored = ticket["nodes"][2]["output"]["ticket"]["tickets"][0]
    assert stored["status"] in ticket["answer"]
    assert stored["id"] in ticket["answer"]
    fallback = document["fallback"]["trace"]
    assert fallback["sources"] == ["ticket_tool"]
    assert fallback["answer"].startswith("I couldn't confirm that ticket's status right now.")
    for code in ("open", "in_progress", "resolved", "discarded"):
        assert code not in fallback["answer"]


def test_timeout_constant_is_numeric_and_inside_the_brief():
    assert isinstance(TICKET_TOOL_TIMEOUT_SECONDS, float)
    assert TICKET_TOOL_TIMEOUT_SECONDS == 4.0
    assert 3 <= TICKET_TOOL_TIMEOUT_SECONDS <= 5


def test_eval_ticket_question_uses_the_tool_not_the_rag(tmp_path, monkeypatch):
    row = _store(tmp_path, monkeypatch)

    def retrieve(*args, **kwargs):
        raise AssertionError("RAG retrieve must not run for a ticket question")

    result = run_agent(
        f"What is the status of ticket {row['id']}?",
        retrieve_fn=retrieve,
        ticket_reader=InProcessIncidentReader(),
        checkpointer=InMemorySaver(),
        trace_dir=tmp_path,
    )
    names = [item["node"] for item in result.trace["nodes"]]
    assert names == ["receive_question", "route_sources", "lookup_ticket", "report_ticket"]
    assert result.trace["route"] == "ticket"
    assert result.trace["sources"] == ["ticket_tool"]
    assert result.trace["ticket_transport"] == "in_process"
    assert row["status"] in result.answer
    assert row["id"] in result.answer
    assert "technical_failure" in result.answer
    assert result.status == "answered"
    stored = result.trace["nodes"][2]["output"]["ticket"]["tickets"][0]
    assert stored["status"] == row["status"]
    assert stored["created_at"] == row["created_at"]
    assert "source_key" not in stored


def test_eval_policy_question_uses_the_rag_not_the_tool(tmp_path):
    chunk = _policy_chunk()

    def lookup_explodes(query):
        raise AssertionError("the ticket tool must not run for a policy question")

    class Reader:
        def lookup(self, query):
            return lookup_explodes(query)

    result = run_agent(
        "Can you drop the executive-search fee from 22% to 15%?",
        retrieve_fn=lambda question, **kwargs: [chunk],
        generate_fn=lambda question, context: "STAND_IN_NOT_A_MODEL",
        ticket_reader=Reader(),
        checkpointer=InMemorySaver(),
        trace_dir=tmp_path,
    )
    names = [item["node"] for item in result.trace["nodes"]]
    assert "lookup_ticket" not in names
    assert names.index("retrieve_context") < names.index("generate_answer")
    assert result.trace["route"] == "rag"
    assert result.trace["sources"] == ["rag"]
    assert "ticket_transport" not in result.trace
    assert "22%" in result.trace["nodes"][2]["output"]["context"][0]["text"]


def test_eval_missing_ticket_does_not_invent_a_status(tmp_path, monkeypatch):
    _store(tmp_path, monkeypatch)

    def retrieve(*args, **kwargs):
        raise AssertionError("a missing ticket must not fall through to the RAG")

    result = run_agent(
        "What's the status of ticket 482?",
        retrieve_fn=retrieve,
        ticket_reader=InProcessIncidentReader(),
        checkpointer=InMemorySaver(),
        trace_dir=tmp_path,
    )
    assert result.trace["sources"] == ["ticket_tool"]
    assert result.status == "ticket_unavailable"
    assert result.answer.startswith(FALLBACK_EN)
    for code in ("open", "in_progress", "resolved", "discarded"):
        assert code not in result.answer
    assert result.trace["nodes"][2]["output"]["ticket"]["outcome"] == "not_found"


def test_eval_timeout_does_not_invent_a_status(tmp_path):
    class Slow:
        def lookup(self, query):
            time.sleep(2)
            return {
                "outcome": "found",
                "tickets": [{"id": "late", "status": "resolved", "title": "late"}],
                "message": "",
            }

    started = time.monotonic()
    result = run_agent(
        "What is the status of ticket 482?",
        retrieve_fn=lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("no rag")),
        ticket_reader=Slow(),
        ticket_timeout=0.2,
        checkpointer=InMemorySaver(),
        trace_dir=tmp_path,
    )
    elapsed = time.monotonic() - started
    assert elapsed < 1
    assert result.status == "ticket_unavailable"
    assert result.answer.startswith(FALLBACK_EN)
    assert "resolved" not in result.answer
    assert "late" not in result.answer
    assert result.trace["nodes"][2]["output"]["ticket"]["outcome"] == "timeout"


def test_eval_spanish_missing_ticket_uses_the_spanish_fallback(tmp_path, monkeypatch):
    _store(tmp_path, monkeypatch)
    result = run_agent(
        "¿En qué estado está el ticket 482?",
        ticket_reader=InProcessIncidentReader(),
        checkpointer=InMemorySaver(),
        trace_dir=tmp_path,
    )
    assert result.answer.startswith(FALLBACK_ES)
    assert result.trace["route"] == "ticket"
    for code in ("open", "in_progress", "resolved", "discarded"):
        assert code not in result.answer


def test_eval_both_sources_keep_order_and_do_not_invent_the_ticket(tmp_path, monkeypatch):
    row = _store(tmp_path, monkeypatch)
    chunk = _policy_chunk()
    result = run_agent(
        f"What is the status of ticket {row['id']} and can we drop the fee from 22% to 15%?",
        retrieve_fn=lambda question, **kwargs: [chunk],
        generate_fn=lambda question, context: "The fee stays at 22%.",
        ticket_reader=InProcessIncidentReader(),
        checkpointer=InMemorySaver(),
        trace_dir=tmp_path,
    )
    names = [item["node"] for item in result.trace["nodes"]]
    assert names.index("lookup_ticket") < names.index("retrieve_context")
    assert names.index("retrieve_context") < names.index("generate_answer")
    assert names[-1] == "compose_sources"
    assert result.trace["route"] == "both"
    assert result.trace["sources"] == ["ticket_tool", "rag"]
    assert row["status"] in result.answer
    assert "22%" in result.answer


def test_open_filter_reads_the_real_list(tmp_path, monkeypatch):
    monkeypatch.setenv("INCIDENTS_DATA_DIR", str(tmp_path / "incidents"))
    from incident_store import create_incident, reset_incidents_db

    reset_incidents_db()
    open_row = create_incident({**INCIDENT, "status": "open"})
    create_incident({**INCIDENT, "status": "resolved", "title": "Ya cerrada"})
    result = run_agent(
        "¿Qué incidencias abiertas hay?",
        ticket_reader=InProcessIncidentReader(),
        checkpointer=InMemorySaver(),
        trace_dir=tmp_path,
    )
    assert result.trace["sources"] == ["ticket_tool"]
    assert open_row["id"] in result.answer
    assert "open" in result.answer
    tickets = result.trace["nodes"][2]["output"]["ticket"]["tickets"]
    assert [item["id"] for item in tickets] == [open_row["id"]]
