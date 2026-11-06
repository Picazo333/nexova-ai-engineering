"""setup() writes the real Qdrant client in memory and can be repeated."""

import hashlib
import math

from data.process.rag import COLLECTION, chunk_corpus, get_qdrant_client, reset_client_cache, setup


def _vector(text: str) -> list[float]:
    digest = hashlib.sha256(text.encode("utf-8")).digest()
    raw = [((digest[index % len(digest)] / 255) - 0.5) or 0.01 for index in range(16)]
    norm = math.sqrt(sum(value * value for value in raw))
    return [value / norm for value in raw]


def test_setup_is_idempotent_and_stores_briefing_payloads(monkeypatch):
    monkeypatch.setenv("QDRANT_URL", "")
    monkeypatch.setenv("QDRANT_PATH", ":memory:")
    monkeypatch.delenv("RAG_EMBED_BACKEND", raising=False)
    reset_client_cache()
    monkeypatch.setattr("data.process.rag.embed", _vector)
    first = setup()
    client = get_qdrant_client()
    first_records, _offset = client.scroll(
        collection_name=COLLECTION,
        limit=200,
        with_payload=True,
        with_vectors=False,
    )
    second = setup()
    second_records, _offset = client.scroll(
        collection_name=COLLECTION,
        limit=200,
        with_payload=True,
        with_vectors=False,
    )
    expected = len(chunk_corpus())
    assert first["collection"] == "nexova_knowledge"
    assert first["chunk_count"] == expected
    assert second["chunk_count"] == expected
    assert first["distance"] == "cosine"
    assert sorted(record.id for record in first_records) == sorted(record.id for record in second_records)
    payloads = [record.payload for record in second_records]
    assert payloads
    for payload in payloads:
        assert set(payload) == {
            "company",
            "source_document",
            "section",
            "language",
            "chunk_index",
            "text",
        }
        assert payload["company"] == "nexova"
        assert payload["language"] in {"en", "es"}
        assert payload["source_document"] in {
            "service-lines",
            "pricing-model",
            "hiring-process-sla",
            "objection-handling",
        }
        assert "score" not in payload
    reset_client_cache()
