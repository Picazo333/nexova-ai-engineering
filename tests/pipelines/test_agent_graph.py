"""Evals for the support-agent graph.

Routing and checkpoint checks use explicit doubles. They do not call the
4Geeks generation model. The live grounding eval skips when that model is
not configured; a double is not a pass of that criterion.
"""

from pathlib import Path

import pytest
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph

from app.agent.errors import GraphStructureError
from app.agent.graph import (
    AgentState,
    assert_state_schema,
    compile_agent,
    compile_builder,
    resume_agent,
    run_agent,
)
from data.rag_settings import load_settings

ROOT = Path(__file__).resolve().parents[2]
CORPUS = ROOT / "docs" / "company-knowledge-base"


def _chunk(filename: str, source: str, section: str, language: str) -> dict:
    text = (CORPUS / filename).read_text(encoding="utf-8")
    return {
        "company": "nexova",
        "source_document": source,
        "section": section,
        "language": language,
        "chunk_index": 0,
        "text": text,
    }


def _run(question: str, chunk: dict | None, tmp_path: Path, *, empty: bool = False):
    seen: dict = {}

    def retrieve(query: str, **kwargs):
        seen["retrieve"] = query
        if empty:
            return []
        return [chunk]

    def generate(query: str, context: list[dict]) -> str:
        seen["generate_context"] = context
        return "STAND_IN_NOT_A_MODEL"

    result = run_agent(
        question,
        retrieve_fn=retrieve,
        generate_fn=generate,
        checkpointer=InMemorySaver(),
        trace_dir=tmp_path,
    )
    return result, seen


def test_eval_discount_trace_keeps_the_briefing_approval_fact(tmp_path):
    chunk = _chunk(
        "nexova-objection-handling.en.md",
        "objection-handling",
        "Fee objection",
        "en",
    )
    assert "Marcos" in chunk["text"] and "22%" in chunk["text"]
    result, seen = _run(
        "Can you drop the executive-search fee from 22% to 15%?",
        chunk,
        tmp_path,
    )
    names = [item["node"] for item in result.trace["nodes"]]
    assert names == ["receive_question", "route_sources", "retrieve_context", "generate_answer"]
    assert names.index("retrieve_context") < names.index("generate_answer")
    handed = seen["generate_context"][0]["text"]
    assert "Marcos" in handed and "22%" in handed
    assert handed == result.trace["nodes"][2]["output"]["context"][0]["text"]
    assert result.answer == "STAND_IN_NOT_A_MODEL"
    statuses = [item["status"] for item in result.trace["checkpoints"]]
    assert "received" in statuses
    assert "retrieved" in statuses
    assert "answered" in statuses
    assert result.trace["checkpoint_count"] >= 3


def test_eval_training_price_trace_keeps_the_briefing_amount(tmp_path):
    chunk = _chunk("nexova-pricing-model.en.md", "pricing-model", "Corporate training", "en")
    assert "6,200" in chunk["text"]
    result, seen = _run(
        "How much does an 8-week training program cost?",
        chunk,
        tmp_path,
    )
    names = [item["node"] for item in result.trace["nodes"]]
    assert names.index("retrieve_context") < names.index("generate_answer")
    assert "6,200" in seen["generate_context"][0]["text"]
    assert result.trace["nodes"][2]["output"]["context"][0]["source_document"] == "pricing-model"


def test_eval_sla_trace_keeps_the_briefing_escalation(tmp_path):
    chunk = _chunk(
        "nexova-hiring-process-sla.en.md",
        "hiring-process-sla",
        "Committed delivery times",
        "en",
    )
    assert "Javier Almeida" in chunk["text"]
    assert "averages" in chunk["text"].lower() or "average" in chunk["text"].lower()
    result, seen = _run(
        "What happens if an executive search has no candidate after 4 weeks?",
        chunk,
        tmp_path,
    )
    assert [item["node"] for item in result.trace["nodes"]][:3] == [
        "receive_question",
        "route_sources",
        "retrieve_context",
    ]
    assert "Javier Almeida" in seen["generate_context"][0]["text"]
    stored = (tmp_path / f"{result.run_id}.json").read_text(encoding="utf-8")
    assert "Javier Almeida" in stored
    assert result.trace["checkpoint_count"] >= 3


def test_eval_empty_question_skips_retrieval(tmp_path, monkeypatch):
    def retrieve(*args, **kwargs):
        raise AssertionError("retrieve must not run for an empty question")

    monkeypatch.setattr("data.pipelines.rag.retrieve", retrieve)
    result = run_agent("   ", checkpointer=InMemorySaver(), trace_dir=tmp_path)
    assert [item["node"] for item in result.trace["nodes"]] == ["receive_question", "refuse_empty"]
    assert result.status == "empty_question"
    assert result.http_status == 422
    assert "consultar" in result.error


def test_eval_empty_context_answers_honestly_without_generation(tmp_path):
    def generate(*args, **kwargs):
        raise AssertionError("generate_answer must not run without context")

    result = run_agent(
        "What is the office wifi password?",
        retrieve_fn=lambda question, **kwargs: [],
        generate_fn=generate,
        checkpointer=InMemorySaver(),
        trace_dir=tmp_path,
    )
    assert [item["node"] for item in result.trace["nodes"]] == [
        "receive_question",
        "route_sources",
        "retrieve_context",
        "insufficient_context",
    ]
    assert result.answer.startswith("I don't have information about that.")
    assert result.status == "insufficient_context"


def test_eval_spanish_gap_uses_the_spanish_honest_answer(tmp_path):
    result = run_agent(
        "¿Cuál es la clave del wifi de la oficina?",
        retrieve_fn=lambda question, **kwargs: [],
        checkpointer=InMemorySaver(),
        trace_dir=tmp_path,
    )
    assert result.answer.startswith("No tengo información sobre eso.")


def test_resume_continues_from_the_retrieve_checkpoint(tmp_path):
    chunk = _chunk("nexova-pricing-model.en.md", "pricing-model", "Executive headhunting", "en")
    seen: dict = {}

    def generate(question: str, context: list[dict]) -> str:
        seen["context"] = context
        return "STAND_IN_NOT_A_MODEL"

    compiled = compile_agent(
        retrieve_fn=lambda question, **kwargs: [chunk],
        generate_fn=generate,
        checkpointer=InMemorySaver(),
        interrupt_after=["retrieve_context"],
    )
    paused = run_paused(compiled, "What is the standard fee?", tmp_path)
    assert paused.status == "paused"
    assert [item["node"] for item in paused.trace["nodes"]] == [
        "receive_question",
        "route_sources",
        "retrieve_context",
    ]
    continued = resume_agent(compiled, paused.thread_id, trace_dir=tmp_path)
    assert continued.status == "answered"
    assert [item["node"] for item in continued.trace["nodes"]] == ["generate_answer"]
    assert "22%" in seen["context"][0]["text"]


def run_paused(compiled, question: str, tmp_path: Path):
    from app.agent.graph import execute

    return execute(compiled, question, "thread-resume-1", trace_dir=tmp_path)


def test_compile_rejects_an_unconnected_node():
    builder = StateGraph(AgentState)
    builder.add_node("receive_question", lambda state: {"status": "received"})
    builder.add_node("orphan", lambda state: {"status": "received"})
    builder.add_edge(START, "receive_question")
    builder.add_edge("receive_question", END)
    with pytest.raises(GraphStructureError, match="sin conexión"):
        compile_builder(builder)


def test_compile_rejects_an_unknown_conditional_target():
    builder = StateGraph(AgentState)
    builder.add_node("receive_question", lambda state: {"status": "received"})
    builder.add_edge(START, "receive_question")
    builder.add_conditional_edges(
        "receive_question",
        lambda state: "missing",
        {"missing": "missing"},
    )
    with pytest.raises(GraphStructureError, match="desconocido"):
        compile_builder(builder)


def test_compile_rejects_conversation_history_in_the_state():
    class HistoryState(dict):
        __annotations__ = {"question": str, "messages": list}

    with pytest.raises(GraphStructureError, match="historial"):
        assert_state_schema(HistoryState)


def test_graph_source_reuses_pipeline_functions():
    source = (ROOT / "services" / "api" / "app" / "agent" / "graph.py").read_text(encoding="utf-8")
    assert "rag.retrieve" in source
    assert "rag.generate_answer" in source
    assert ".query(" not in source
    rag = (ROOT / "data" / "pipelines" / "rag.py").read_text(encoding="utf-8")
    assert "def retrieve(" in rag
    assert "def generate_answer(" in rag
    assert "def query(" in rag


def test_committed_trace_export_shows_a_full_run():
    document_path = ROOT / "docs" / "langgraph" / "trace-full-run.json"
    import json

    document = json.loads(document_path.read_text(encoding="utf-8"))
    assert document["live_generation"] == "BLOCKED_HITL"
    by_label = {item["label"]: item for item in document["runs"]}
    full = by_label["full_run_with_briefing_context"]
    assert [item["node"] for item in full["nodes"]] == [
        "receive_question",
        "route_sources",
        "retrieve_context",
        "generate_answer",
    ]
    assert full["generation_mode"] == "explicit_stand_in"
    assert full["checkpoint_count"] >= 3
    context_text = full["nodes"][2]["output"]["context"][0]["text"]
    assert "Marcos" in context_text and "22%" in context_text
    assert "Marcos" in full["answer"] and "22%" in full["answer"]
    empty = by_label["empty_question"]
    assert [item["node"] for item in empty["nodes"]] == ["receive_question", "refuse_empty"]
    gap = by_label["no_context_above_threshold"]
    assert gap["nodes"][-1]["node"] == "insufficient_context"
    assert gap["answer"].startswith("I don't have information about that.")


def test_eval_live_answer_is_grounded_in_the_briefing(tmp_path):
    settings = load_settings()
    if not (settings.generation_remote_ready and settings.embedding_remote_ready):
        pytest.skip(
            "BLOCKED_HITL: GENERATION_* and EMBEDDING_* are empty. "
            "A stand-in answer is not a pass of live grounding."
        )
    result = run_agent(
        "Can you drop the executive-search fee from 22% to 15%?",
        trace_dir=tmp_path,
    )
    assert result.status == "answered", result.error
    assert "22%" in result.answer
    assert "Marcos" in result.answer or "Ibáñez" in result.answer
