"""Unit tests for retrieve() and query(). No live Qdrant and no live model."""

from data.pipelines.rag import SYSTEM_PROMPT, query, retrieve
from data.rag_errors import GenerationNotConfigured


class _Point:
    def __init__(self, score, payload):
        self.score = score
        self.payload = payload


class _Response:
    def __init__(self, points):
        self.points = points


class _Client:
    def __init__(self, points):
        self.points = points
        self.kwargs = None

    def query_points(self, **kwargs):
        self.kwargs = kwargs
        return _Response(self.points)


def _patch_search(monkeypatch, points):
    client = _Client(points)
    monkeypatch.setattr("data.process.rag.embed", lambda text: [1.0, 0.0])
    monkeypatch.setattr("data.process.rag.get_qdrant_client", lambda: client)
    return client


def test_retrieve_excludes_scores_below_min_score_and_can_return_fewer_than_k(monkeypatch):
    client = _patch_search(
        monkeypatch,
        [
            _Point(0.91, {"text": "high", "source_document": "pricing-model"}),
            _Point(0.2, {"text": "low", "source_document": "service-lines"}),
            _Point(0.55, {"text": "mid", "source_document": "hiring-process-sla"}),
        ],
    )
    result = retrieve("fee", k=5, min_score=0.4)
    assert [item["text"] for item in result] == ["high", "mid"]
    assert len(result) < 5
    assert all(isinstance(item, dict) for item in result)
    assert "score" not in result[0]
    assert client.kwargs["limit"] == 5
    assert client.kwargs["score_threshold"] == 0.4
    assert client.kwargs["collection_name"] == "nexova_knowledge"


def test_retrieve_stops_at_k_even_when_more_hits_clear_the_threshold(monkeypatch):
    _patch_search(
        monkeypatch,
        [
            _Point(0.9, {"text": "a"}),
            _Point(0.8, {"text": "b"}),
            _Point(0.7, {"text": "c"}),
        ],
    )
    result = retrieve("fee", k=2, min_score=0.4)
    assert [item["text"] for item in result] == ["a", "b"]


def test_retrieve_can_return_nothing(monkeypatch):
    _patch_search(monkeypatch, [_Point(0.1, {"text": "irrelevant"})])
    assert retrieve("fee", k=5, min_score=0.4) == []


def test_query_returns_model_output_and_does_not_skip_generation(monkeypatch):
    raw = "RAW_CHUNK_TEXT_XYZ"
    monkeypatch.setattr(
        "data.pipelines.rag.retrieve",
        lambda question, **kwargs: [
            {
                "text": raw,
                "source_document": "pricing-model",
                "section": "Corporate training",
                "language": "en",
            }
        ],
    )

    def fake_complete(messages, settings):
        assert raw in messages[1]["content"]
        assert settings.generation_model_id == "gen-model"
        assert settings.generation_model_id != settings.embedding_model_id
        return "Generated answer only."

    monkeypatch.setenv("GENERATION_MODEL_ID", "gen-model")
    monkeypatch.setenv("GENERATION_BASE_URL", "https://example.invalid/v1")
    monkeypatch.setenv("GENERATION_API_KEY", "test-key")
    monkeypatch.setenv("EMBEDDING_MODEL_ID", "embed-model")
    monkeypatch.setattr("data.pipelines.rag.complete_chat", fake_complete)
    assert query("How much does an 8-week training program cost?") == "Generated answer only."


def test_empty_retrieve_still_asks_the_model_not_to_invent(monkeypatch):
    monkeypatch.setattr("data.pipelines.rag.retrieve", lambda question, **kwargs: [])

    def fake_complete(messages, settings):
        assert "(no retrieved context)" in messages[1]["content"]
        assert "does not have enough information" in messages[0]["content"]
        return "The knowledge base does not have enough information."

    monkeypatch.setenv("GENERATION_MODEL_ID", "gen-model")
    monkeypatch.setenv("GENERATION_BASE_URL", "https://example.invalid/v1")
    monkeypatch.setenv("GENERATION_API_KEY", "test-key")
    monkeypatch.setenv("EMBEDDING_MODEL_ID", "embed-model")
    monkeypatch.setattr("data.pipelines.rag.complete_chat", fake_complete)
    assert "enough information" in query("What is the office wifi password?")


def test_query_without_generation_config_does_not_invent_an_answer(monkeypatch):
    monkeypatch.setattr("data.pipelines.rag.retrieve", lambda question, **kwargs: [])
    monkeypatch.delenv("GENERATION_MODEL_ID", raising=False)
    monkeypatch.delenv("GENERATION_BASE_URL", raising=False)
    monkeypatch.delenv("GENERATION_API_KEY", raising=False)
    monkeypatch.delenv("RAG_EMBED_BACKEND", raising=False)
    try:
        query("How much does an 8-week training program cost?")
    except GenerationNotConfigured as exc:
        assert "not configured" in str(exc).lower() or "not configured" in str(exc)
        assert "6,200" not in str(exc)
    else:
        raise AssertionError("query() invented an answer without a generation model")


def test_prompt_carries_the_briefing_voice_and_commercial_rules():
    text = SYSTEM_PROMPT
    assert "Nexova salesperson" in text
    assert "only the retrieved context" in text
    assert "does not have enough information" in text
    assert "Marcos Ibáñez" in text
    assert "22%" in text
    assert "averages" in text
    assert "6-month replacement guarantee" in text
    assert "conflict of interest" in text
    assert "Sources:" in text
