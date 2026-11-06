"""Publish docs/langgraph/trace-full-run.json from the instrumented capture.

The measured file is
docs/langgraph/evidence/r25-instrumented/trace-full-run.instrumented.json.
This module does not call a model. It rewrites the evidence path to the
repo, drops reason fields that are null because the value is now present,
and records that embedding usage was not collected.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from data.rag_settings import ROOT

INSTRUMENTED = (
    ROOT / "docs" / "langgraph" / "evidence" / "r25-instrumented" / "trace-full-run.instrumented.json"
)
DEFAULT_OUT = ROOT / "docs" / "langgraph" / "trace-full-run.json"
EVIDENCE = "docs/langgraph/evidence/r25-instrumented/trace-instrumented.json"
EMBEDDING_USAGE_REASON = (
    "The harness does not collect embedding usage. "
    "Generation usage is not a whole-pipeline token total."
)
NOTE = (
    "Derivado de docs/langgraph/evidence/r25-instrumented/"
    "trace-full-run.instrumented.json. Nodos, run_id, checkpoints y "
    "tokens de generación son los medidos con el grafo compilado y "
    "MemorySaver. La ruta de evidencia apunta al repo. El uso de "
    "embeddings sigue en null porque el harness no lo recoge."
)


def _drop_null_reason(payload: dict, value_key: str, reason_key: str) -> None:
    if payload.get(value_key) is not None and payload.get(reason_key) is None:
        payload.pop(reason_key, None)


def build_export(instrumented_path: Path = INSTRUMENTED) -> dict:
    document = json.loads(instrumented_path.read_text(encoding="utf-8"))
    document["note"] = NOTE
    document["evidence"] = EVIDENCE
    document["currency"] = "CURRENT"
    document["embedding_usage"] = None
    document["embedding_usage_reason"] = EMBEDDING_USAGE_REASON
    _drop_null_reason(document, "tokens", "tokens_reason")
    for run in document["runs"]:
        _drop_null_reason(run, "run_id", "run_id_reason")
        _drop_null_reason(run, "checkpoints", "checkpoints_reason")
        _drop_null_reason(run, "tokens", "tokens_reason")
        _drop_null_reason(run, "model", "model_reason")
        run["embedding_usage"] = None
        run["embedding_usage_reason"] = EMBEDDING_USAGE_REASON
    return document


def write_export(destination: Path, document: dict | None = None) -> dict:
    payload = build_export() if document is None else document
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Publish the instrumented trace export.")
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    args = parser.parse_args()
    destination = Path(args.out)
    document = write_export(destination)
    labels = [item["label"] for item in document["runs"]]
    print(f"wrote {destination} from {INSTRUMENTED.name} runs={','.join(labels)}")


if __name__ == "__main__":
    main()
