"""Unit tests for retrieve() and query(). No live Qdrant and no live model."""

import pytest

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
    assert client.kwargs["limit"] >= 5
    assert client.kwargs["score_threshold"] is None
    assert client.kwargs["collection_name"] == "nexova_knowledge"


def test_literal_term_keeps_a_chunk_the_vector_score_would_drop(monkeypatch):
    """'tarifa' is in the pricing chunk, but a generic question scores it under min_score.

    Vector-only retrieval returns the service-lines neighbor and drops the fee.
    """

    _patch_search(
        monkeypatch,
        [
            _Point(
                0.62,
                {
                    "text": "Nexova opera tres líneas de negocio.",
                    "source_document": "service-lines",
                    "language": "es",
                    "chunk_index": 0,
                    "section": "lineas",
                },
            ),
            _Point(
                0.22,
                {
                    "text": "Tarifa estándar: 22% del salario anual bruto del cargo contratado.",
                    "source_document": "pricing-model",
                    "language": "es",
                    "chunk_index": 0,
                    "section": "Headhunting ejecutivo",
                },
            ),
        ],
    )
    result = retrieve("¿Cuál es la tarifa de Nexova", k=3, min_score=0.4)
    assert any("Tarifa estándar: 22%" in item["text"] for item in result)


def test_off_corpus_words_do_not_promote_a_below_threshold_chunk(monkeypatch):
    _patch_search(
        monkeypatch,
        [
            _Point(
                0.31,
                {
                    "text": "Nexova opera tres líneas de negocio.",
                    "source_document": "service-lines",
                    "language": "es",
                    "chunk_index": 0,
                    "section": "lineas",
                },
            )
        ],
    )
    assert retrieve("¿Quién ganó el mundial de fútbol de 2098?", k=5, min_score=0.4) == []


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


def test_compound_clauses_split_two_real_clauses_only():
    from data.pipelines.rag import compound_clauses

    parts = compound_clauses("¿Cuál es la tarifa de Nexova y quién autoriza una rebaja?")
    assert len(parts) == 2
    assert "tarifa" in parts[0].lower()
    assert "rebaja" in parts[1].lower()
    assert compound_clauses("entrega de 6 y 8 semanas") == ["entrega de 6 y 8 semanas"]


def test_compound_question_retrieves_each_clause_not_only_the_blended_hit(monkeypatch):
    """One embedding of the whole question returns the wrong objection chunk.

    That is what the live call did. Each clause has to be searched, or the
    fee chunk never enters the result.
    """

    asked: list[str] = []

    def fake_embed(text: str) -> list[float]:
        asked.append(text)
        return [1.0, 0.0, float(len(asked))]

    class _Client:
        def query_points(self, **kwargs):
            text = asked[-1].lower()
            if "tarifa" in text and "rebaja" in text:
                payload = {
                    "text": "¿Qué pasa si no estoy conforme con la terna presentada?",
                    "source_document": "objection-handling",
                    "language": "es",
                    "chunk_index": 2,
                    "section": "terna",
                }
            elif "tarifa" in text:
                payload = {
                    "text": "Tarifa estándar: 22% del salario anual bruto del cargo contratado.",
                    "source_document": "pricing-model",
                    "language": "es",
                    "chunk_index": 0,
                    "section": "Headhunting ejecutivo",
                }
            elif "rebaja" in text or "autoriza" in text:
                payload = {
                    "text": "sin aprobación de Marcos Ibáñez",
                    "source_document": "objection-handling",
                    "language": "es",
                    "chunk_index": 0,
                    "section": "22% me parece caro",
                }
            else:
                payload = {
                    "text": "otro",
                    "source_document": "service-lines",
                    "language": "es",
                    "chunk_index": 1,
                    "section": "otro",
                }
            return _Response([_Point(0.88, payload)])

    monkeypatch.setattr("data.process.rag.embed", fake_embed)
    monkeypatch.setattr("data.process.rag.get_qdrant_client", lambda: _Client())
    result = retrieve(
        "¿Cuál es la tarifa de Nexova y quién autoriza una rebaja?",
        k=3,
        min_score=0.4,
    )
    combined = " ".join(item["text"] for item in result)
    assert "Tarifa estándar: 22%" in combined
    assert "Marcos Ibáñez" in combined
    assert len(asked) >= 2


def test_compound_question_outside_the_corpus_stays_empty(monkeypatch):
    monkeypatch.setattr("data.process.rag.embed", lambda text: [0.2, 0.1])

    class _Empty:
        def query_points(self, **kwargs):
            return _Response([])

    monkeypatch.setattr("data.process.rag.get_qdrant_client", lambda: _Empty())
    assert (
        retrieve(
            "¿Cuál es la capital de Mongolia y cuántos habitantes tiene?",
            k=5,
            min_score=0.4,
        )
        == []
    )


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


_FULL_ANSWER = (
    "En promedio, una búsqueda ejecutiva tarda entre 6 y 8 semanas desde el briefing "
    "hasta la terna final.\n\nSources: hiring-process-sla — Tiempos de entrega"
)


class _ScriptedCompletions:
    def __init__(self, script):
        self.script = list(script)
        self.calls = 0

    def create(self, **kwargs):
        self.calls += 1
        content, finish_reason = self.script.pop(0)
        message = type("Message", (), {"content": content})()
        choice = type("Choice", (), {"message": message, "finish_reason": finish_reason})()
        return type("Response", (), {"choices": [choice]})()


def _scripted_openai(monkeypatch, script):
    completions = _ScriptedCompletions(script)

    class _Client:
        def __init__(self, **kwargs):
            self.kwargs = kwargs
            self.chat = type("Chat", (), {"completions": completions})()

    monkeypatch.setattr("openai.OpenAI", _Client)
    return completions


def _generation_env(monkeypatch):
    monkeypatch.setenv("GENERATION_MODEL_ID", "gen-model")
    monkeypatch.setenv("GENERATION_BASE_URL", "https://example.invalid/v1")
    monkeypatch.setenv("GENERATION_API_KEY", "test-key")
    monkeypatch.setenv("EMBEDDING_MODEL_ID", "embed-model")


def test_complete_chat_retries_truncated_gra_and_does_not_return_it(monkeypatch):
    from data.pipelines.rag import complete_chat
    from data.rag_settings import load_settings

    _generation_env(monkeypatch)
    completions = _scripted_openai(
        monkeypatch,
        [("Gra", "stop"), (_FULL_ANSWER, "stop")],
    )
    result = complete_chat([{"role": "user", "content": "¿Cuánto tarda?"}], load_settings())
    assert result == _FULL_ANSWER
    assert result != "Gra"
    assert "Gra" not in result
    assert completions.calls == 2


def test_complete_chat_rejects_finish_reason_length(monkeypatch):
    from data.pipelines.rag import complete_chat
    from data.rag_errors import GenerationCallFailed
    from data.rag_settings import load_settings

    _generation_env(monkeypatch)
    cut = "En promedio, una búsqueda ejecutiva tarda " * 8
    completions = _scripted_openai(
        monkeypatch,
        [(cut, "length"), (cut, "length")],
    )
    with pytest.raises(GenerationCallFailed) as caught:
        complete_chat([{"role": "user", "content": "¿Cuánto tarda?"}], load_settings())
    assert completions.calls == 2
    assert "length" in str(caught.value)
    assert cut not in str(caught.value)
    assert "Gra" not in str(caught.value)


def test_complete_chat_does_not_accept_gra_after_the_bounded_retry(monkeypatch):
    from data.pipelines.rag import complete_chat
    from data.rag_errors import GenerationCallFailed
    from data.rag_settings import load_settings

    _generation_env(monkeypatch)
    completions = _scripted_openai(monkeypatch, [("Gra", "stop"), ("Gra", None)])
    with pytest.raises(GenerationCallFailed) as caught:
        complete_chat([{"role": "user", "content": "¿Cuánto tarda?"}], load_settings())
    assert completions.calls == 2
    assert "Gra" not in str(caught.value)
    assert "too_short" in str(caught.value) or "missing_finish_reason" in str(caught.value)


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
    assert "two short paragraphs" in text


def test_complete_chat_requests_a_token_budget_above_the_old_cap(monkeypatch):
    from data.pipelines.rag import complete_chat
    from data.rag_settings import load_settings

    _generation_env(monkeypatch)
    completions = _scripted_openai(monkeypatch, [(_FULL_ANSWER, "stop")])
    # The scripted client records kwargs via a wrapper installed below.
    seen: dict = {}
    original = completions.create

    def _capture(**kwargs):
        seen.update(kwargs)
        return original(**kwargs)

    completions.create = _capture
    complete_chat([{"role": "user", "content": "¿Cuánto tarda?"}], load_settings())
    assert seen["max_tokens"] >= 1500
    assert seen["max_tokens"] > 700
