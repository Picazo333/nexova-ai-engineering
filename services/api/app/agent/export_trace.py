"""Write a consultable export of complete graph runs.

The generation step quotes the official document that retrieval returned.
That stand-in is explicit: the 4Geeks generation model is not configured,
and this file is not a pass of the live-answer criterion.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from langgraph.checkpoint.memory import InMemorySaver

from app.agent.graph import run_agent
from data.rag_settings import ROOT

CORPUS = ROOT / "docs" / "company-knowledge-base"


def corpus_chunk(filename: str, source: str, section: str, language: str) -> dict:
    text = (CORPUS / filename).read_text(encoding="utf-8")
    return {
        "company": "nexova",
        "source_document": source,
        "section": section,
        "language": language,
        "chunk_index": 0,
        "text": text,
    }


def quote_context(_question: str, context: list[dict]) -> str:
    blocks = [str(item.get("text") or "").strip() for item in context if str(item.get("text") or "").strip()]
    if not blocks:
        raise RuntimeError("the stand-in was called without context")
    return "\n\n".join(blocks)


def build_export(destination: Path) -> dict:
    fee = corpus_chunk(
        "nexova-objection-handling.en.md",
        "objection-handling",
        "Fee objection",
        "en",
    )
    runs = [
        run_agent(
            "Can you drop the executive-search fee from 22% to 15%?",
            retrieve_fn=lambda question, **kwargs: [fee],
            generate_fn=quote_context,
            checkpointer=InMemorySaver(),
            metadata={
                "generation_mode": "explicit_stand_in",
                "retrieval_mode": "corpus_fixture",
                "label": "full_run_with_briefing_context",
            },
        ),
        run_agent(
            "   ",
            checkpointer=InMemorySaver(),
            metadata={
                "generation_mode": "not_called",
                "retrieval_mode": "not_called",
                "label": "empty_question",
            },
        ),
        run_agent(
            "What is the office wifi password?",
            retrieve_fn=lambda question, **kwargs: [],
            generate_fn=quote_context,
            checkpointer=InMemorySaver(),
            metadata={
                "generation_mode": "not_called",
                "retrieval_mode": "explicit_empty",
                "label": "no_context_above_threshold",
            },
        ),
    ]
    document = {
        "note": (
            "Tres corridas completas del grafo compilado. La primera recorre "
            "recepción, retrieve y generate_answer con un fragmento real de "
            "docs/company-knowledge-base/nexova-objection-handling.en.md. "
            "generate_answer aquí es un doble explícito que cita ese documento: "
            "GENERATION_MODEL_ID, GENERATION_BASE_URL y GENERATION_API_KEY están "
            "vacíos. No es una respuesta del modelo de 4Geeks y no cierra el "
            "criterio de anclaje en vivo (BLOCKED_HITL). Las otras dos corridas "
            "muestran las aristas condicionales: pregunta vacía, y retrieve sin "
            "contexto por encima del umbral."
        ),
        "live_generation": "BLOCKED_HITL",
        "runs": [item.trace for item in runs],
    }
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return document


def main() -> None:
    parser = argparse.ArgumentParser(description="Export complete agent traces.")
    parser.add_argument(
        "--out",
        default=str(ROOT / "docs" / "langgraph" / "trace-full-run.json"),
        help="Destination JSON path.",
    )
    args = parser.parse_args()
    destination = Path(args.out)
    document = build_export(destination)
    labels = [item["label"] for item in document["runs"]]
    print(f"wrote {destination} runs={','.join(labels)}")


if __name__ == "__main__":
    main()
