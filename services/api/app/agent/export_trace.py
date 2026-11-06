"""Publish the trace export from the recorded 4Geeks run.

The file `docs/langgraph/evidence/llm-live/02-run-agent-live.json` is the
capture. This module does not call the model and does not fill timings or
token counts that are absent from that file.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from data.rag_settings import ROOT

LIVE_PATH = ROOT / "docs" / "langgraph" / "evidence" / "llm-live" / "02-run-agent-live.json"
README_PATH = ROOT / "docs" / "langgraph" / "evidence" / "llm-live" / "README.md"
DEFAULT_OUT = ROOT / "docs" / "langgraph" / "trace-full-run.json"
BASE_URL = "https://llm.4geeks.ai/v1"


def _sources(answer: str) -> list[dict]:
    found: list[dict] = []
    for raw in answer.splitlines():
        line = raw.strip()
        if line.startswith("Sources:"):
            line = line.split(":", 1)[1].strip()
        if " — " not in line:
            continue
        document, section = line.split(" — ", 1)
        document = document.strip()
        section = section.strip()
        if not document or not section or " " in document:
            continue
        found.append({"source_document": document, "section": section})
    return found


def _nodes(status: str, answer: str) -> tuple[list[dict] | None, str | None]:
    """Node names follow the compiled graph for this status.

    The capture does not include each node's payload. Outputs we do not have
    stay null.
    """

    if status == "answered":
        names = ["receive_question", "retrieve_context", "generate_answer"]
        basis = (
            "status answered solo lo escribe generate_answer, "
            "después de receive_question y retrieve_context."
        )
    elif status == "insufficient_context":
        names = ["receive_question", "retrieve_context", "insufficient_context"]
        basis = (
            "status insufficient_context solo lo escribe ese nodo, "
            "después de receive_question y retrieve_context, y no llama al modelo."
        )
    else:
        return None, f"02-run-agent-live.json no define un camino de nodos para status {status}."
    nodes = []
    for order, name in enumerate(names, start=1):
        carries_answer = name in {"generate_answer", "insufficient_context"}
        nodes.append(
            {
                "order": order,
                "node": name,
                "output": {"answer": answer, "status": status} if carries_answer else None,
                "output_reason": None
                if carries_answer
                else "02-run-agent-live.json no incluye la salida de este nodo.",
            }
        )
    return nodes, basis


def build_export(live_path: Path = LIVE_PATH, readme_path: Path = README_PATH) -> dict:
    live = json.loads(live_path.read_text(encoding="utf-8"))
    readme = readme_path.read_text(encoding="utf-8")
    if BASE_URL not in readme:
        raise ValueError("El README de la evidencia no declara la base del modelo.")
    model = live.get("modelo_generacion")
    embedder = live.get("modelo_embeddings")
    runs = []
    for item in live["resultados"]:
        answer = item.get("answer") or ""
        status = item.get("status")
        nodes, basis = _nodes(status, answer)
        called = status == "answered"
        runs.append(
            {
                "label": "live_fee_grounding" if called else "live_outside_corpus",
                "question": item.get("pregunta"),
                "status": status,
                "answer": answer,
                "error": item.get("error", ""),
                "latencia_s": item.get("latencia_s"),
                "generation_mode": "live" if called else "not_called",
                "model": model if called else None,
                "model_reason": None
                if called
                else "Esta corrida no llamó al modelo de generación. El id configurado en la captura es modelo_generacion.",
                "configured_generation_model": model,
                "embedding_model": embedder,
                "generation_base_url": BASE_URL if called else None,
                "sources": _sources(answer),
                "nodes": nodes,
                "nodes_basis": basis,
                "checkpoints": None,
                "checkpoints_reason": "02-run-agent-live.json no incluye checkpoints.",
                "tokens": None,
                "tokens_reason": "02-run-agent-live.json no incluye tokens.",
                "run_id": None,
                "run_id_reason": "02-run-agent-live.json no incluye run_id.",
            }
        )
    return {
        "note": (
            "Export de la corrida live registrada en "
            "docs/langgraph/evidence/llm-live/02-run-agent-live.json. "
            "La respuesta de la tarifa sale del modelo de generación indicado. "
            "Los campos que esa captura no trae están en null con su razón. "
            "No se añadieron tiempos ni tokens distintos de latencia_s."
        ),
        "live_generation": "measured",
        "currency": "CURRENT",
        "evidence": "docs/langgraph/evidence/llm-live/02-run-agent-live.json",
        "hora": live.get("hora"),
        "modelo_generacion": model,
        "modelo_embeddings": embedder,
        "generation_base_url": BASE_URL,
        "generation_base_url_source": "docs/langgraph/evidence/llm-live/README.md",
        "tokens": None,
        "tokens_reason": "02-run-agent-live.json no incluye tokens.",
        "runs": runs,
    }


def write_export(destination: Path, document: dict | None = None) -> dict:
    payload = build_export() if document is None else document
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Write the live trace export.")
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    args = parser.parse_args()
    destination = Path(args.out)
    document = write_export(destination)
    labels = [item["label"] for item in document["runs"]]
    print(f"wrote {destination} runs={','.join(labels)} model={document['modelo_generacion']}")


if __name__ == "__main__":
    main()
