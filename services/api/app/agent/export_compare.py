"""Export one RAG trace and one ticket-tool trace side by side.

The ticket row is inserted with ``create_incident`` and read back by the tool.
The generation step of the RAG column is an explicit stand-in: the 4Geeks
model is not configured, and this file does not pass that criterion.
"""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path

from langgraph.checkpoint.memory import InMemorySaver

from app.agent.export_trace import corpus_chunk, quote_context
from app.agent.graph import run_agent
from app.agent.tools.tickets import InProcessIncidentReader, _shared_path
from data.rag_settings import ROOT


def build_comparison(destination: Path) -> dict:
    _shared_path()
    from incident_store import create_incident, reset_incidents_db

    previous = os.environ.get("INCIDENTS_DATA_DIR")
    with tempfile.TemporaryDirectory() as directory:
        os.environ["INCIDENTS_DATA_DIR"] = directory
        reset_incidents_db()
        try:
            row = create_incident(
                {
                    "title": "La caja no emite el contrato",
                    "description": "El cliente no puede descargar el contrato firmado desde el portal.",
                    "category": "technical_failure",
                    "status": "in_progress",
                    "origin": "customer",
                    "branch": "central",
                }
            )
            fee = corpus_chunk(
                "nexova-objection-handling.en.md",
                "objection-handling",
                "Fee objection",
                "en",
            )
            rag = run_agent(
                "Can you drop the executive-search fee from 22% to 15%?",
                retrieve_fn=lambda question, **kwargs: [fee],
                generate_fn=quote_context,
                ticket_reader=InProcessIncidentReader(),
                checkpointer=InMemorySaver(),
                trace_dir=Path(directory),
                metadata={
                    "generation_mode": "explicit_stand_in",
                    "retrieval_mode": "corpus_fixture",
                    "label": "rag",
                },
            )
            def retrieve_must_not_run(*args, **kwargs):
                raise AssertionError("RAG must not run")

            ticket = run_agent(
                f"What is the status of ticket {row['id']}?",
                retrieve_fn=retrieve_must_not_run,
                ticket_reader=InProcessIncidentReader(),
                checkpointer=InMemorySaver(),
                trace_dir=Path(directory),
                metadata={
                    "generation_mode": "not_called",
                    "retrieval_mode": "not_called",
                    "label": "ticket_tool",
                },
            )
            missing = run_agent(
                "What's the status of ticket 482?",
                ticket_reader=InProcessIncidentReader(),
                checkpointer=InMemorySaver(),
                trace_dir=Path(directory),
                metadata={
                    "generation_mode": "not_called",
                    "retrieval_mode": "not_called",
                    "label": "ticket_missing",
                },
            )
        finally:
            reset_incidents_db()
            if previous is None:
                os.environ.pop("INCIDENTS_DATA_DIR", None)
            else:
                os.environ["INCIDENTS_DATA_DIR"] = previous
    document = {
        "note": (
            "Dos columnas y una corrida de reserva. La columna RAG usa un doble "
            "explícito de generación porque GENERATION_* está vacío "
            "(BLOCKED_HITL): no es una respuesta del modelo de 4Geeks. La columna "
            "tool inserta una incidencia con create_incident, la función del "
            "gestor, y la vuelve a leer con la tool. El estado del texto sale de "
            "ese registro. La tercera corrida pide el ticket 482, que no existe, "
            "y no inventa un estado."
        ),
        "live_generation": "BLOCKED_HITL",
        "ticket_transport": "in_process",
        "columns": [
            {"label": "rag", "trace": rag.trace},
            {"label": "ticket_tool", "trace": ticket.trace},
        ],
        "fallback": {"label": "ticket_missing", "trace": missing.trace},
    }
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return document


def main() -> None:
    parser = argparse.ArgumentParser(description="Export RAG and ticket traces side by side.")
    parser.add_argument(
        "--out",
        default=str(ROOT / "docs" / "langgraph" / "traces-side-by-side.json"),
    )
    args = parser.parse_args()
    document = build_comparison(Path(args.out))
    labels = [item["label"] for item in document["columns"]]
    print(f"wrote {args.out} columns={','.join(labels)} fallback={document['fallback']['label']}")


if __name__ == "__main__":
    main()
