"""Measure Recall@3 for `data/eval/test-queries.json`.

A hit counts when one of the top 3 ranked chunks has the expected source
document, language, and verbatim span. The ranking uses `min_score=0` so the
threshold does not hide neighbors. A second pass reports how many of those
gold chunks also clear the configured threshold.

A result produced with `RAG_EMBED_BACKEND=fastembed` is diagnostic. It is not
a pass of the 4Geeks embeddings criterion.
"""

from __future__ import annotations

import json
from pathlib import Path

from data.pipelines.rag import retrieve
from data.process.rag import COLLECTION, get_qdrant_client
from data.rag_errors import EmbeddingNotConfigured
from data.rag_settings import ROOT, load_settings

QUERIES_PATH = ROOT / "data" / "eval" / "test-queries.json"
REPORT_PATH = ROOT / "data" / "eval" / "recall-report.json"


def load_queries(path: Path = QUERIES_PATH) -> list[dict]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    queries = payload["queries"]
    if len(queries) < 8:
        raise ValueError("test-queries.json needs at least 8 questions.")
    return queries


def expected_groups(spec: dict) -> list[dict]:
    matches = spec.get("expected_matches")
    if matches:
        return matches
    return [spec]


def is_relevant(payload: dict, spec: dict) -> bool:
    if payload.get("source_document") != spec["expected_source_document"]:
        return False
    if payload.get("language") != spec["language"]:
        return False
    return spec["expected_text_contains"] in str(payload.get("text", ""))


def covers_all(results: list[dict], spec: dict) -> bool:
    return all(any(is_relevant(item, group) for item in results) for group in expected_groups(spec))


def recall_at_3(queries: list[dict] | None = None) -> dict:
    settings = load_settings()
    specs = load_queries() if queries is None else queries
    client = get_qdrant_client()
    if not client.collection_exists(COLLECTION):
        raise RuntimeError("Collection nexova_knowledge is not indexed. Run setup() first.")
    hits = 0
    hits_above_threshold = 0
    rows = []
    for spec in specs:
        ranked = retrieve(spec["question"], k=3, min_score=-1.0)[:3]
        ok = covers_all(ranked, spec)
        hits += int(ok)
        above = False
        if ok:
            filtered = retrieve(spec["question"], k=5, min_score=settings.min_score)
            above = covers_all(filtered, spec)
            hits_above_threshold += int(above)
        rows.append(
            {
                "id": spec["id"],
                "hit": ok,
                "above_min_score": above,
                "top_sources": [item.get("source_document") for item in ranked],
            }
        )
    total = len(specs)
    recall = hits / total if total else 0.0
    official = bool(settings.embedding_remote_ready)
    return {
        "queries": total,
        "hits": hits,
        "recall_at_3": recall,
        "threshold": 0.8,
        "meets_threshold_for_this_embedder": recall >= 0.8,
        "hits_above_configured_min_score": hits_above_threshold,
        "min_score": settings.min_score,
        "embedder": "remote" if official else settings.embed_backend or "unconfigured",
        "official_4geeks_criterion": "measured" if official else "BLOCKED_HITL",
        "rows": rows,
    }


def main() -> int:
    settings = load_settings()
    if not settings.embedding_remote_ready and settings.embed_backend != "fastembed":
        print(
            "BLOCKED_HITL: embeddings are not configured. "
            "Recall@3 was not measured and a mock score is not reported."
        )
        return 2
    try:
        report = recall_at_3()
    except EmbeddingNotConfigured:
        print("BLOCKED_HITL: embeddings are not configured. Recall@3 was not measured.")
        return 2
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {key: value for key, value in report.items() if key != "rows"},
            ensure_ascii=False,
            indent=2,
        )
    )
    print(f"wrote {REPORT_PATH}")
    if report["official_4geeks_criterion"] != "measured":
        print(
            "BLOCKED_HITL: the number above uses the local open-source embedder. "
            "It does not pass the 4Geeks embeddings criterion."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
