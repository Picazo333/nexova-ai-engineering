"""embed() keeps the generation model and the forbidden token out of the call."""

from data.process.rag import embed
from data.rag_errors import EmbeddingNotConfigured, ModelIdConflict


def _clear(monkeypatch):
    for name in (
        "EMBEDDING_MODEL_ID",
        "EMBEDDING_BASE_URL",
        "EMBEDDING_API_KEY",
        "GENERATION_MODEL_ID",
        "GENERATION_BASE_URL",
        "GENERATION_API_KEY",
        "RAG_EMBED_BACKEND",
    ):
        monkeypatch.delenv(name, raising=False)


def test_embed_ignores_fourgeeks_api_token(monkeypatch):
    _clear(monkeypatch)
    monkeypatch.setenv("FOURGEEKS_API_TOKEN", "do-not-use")
    try:
        embed("Nexova headhunting fee")
    except EmbeddingNotConfigured as exc:
        assert "do-not-use" not in str(exc)
    else:
        raise AssertionError("embed() ran without the embeddings configuration")


def test_same_model_id_is_rejected(monkeypatch):
    _clear(monkeypatch)
    monkeypatch.setenv("EMBEDDING_MODEL_ID", "same-model")
    monkeypatch.setenv("GENERATION_MODEL_ID", "same-model")
    monkeypatch.setenv("EMBEDDING_BASE_URL", "https://example.invalid/v1")
    monkeypatch.setenv("EMBEDDING_API_KEY", "test-key")
    try:
        embed("Nexova")
    except ModelIdConflict:
        return
    raise AssertionError("identical model IDs were accepted")


def test_remote_embed_uses_the_embeddings_model_id(monkeypatch):
    _clear(monkeypatch)
    monkeypatch.setenv("EMBEDDING_MODEL_ID", "embed-model")
    monkeypatch.setenv("GENERATION_MODEL_ID", "gen-model")
    monkeypatch.setenv("EMBEDDING_BASE_URL", "https://example.invalid/v1")
    monkeypatch.setenv("EMBEDDING_API_KEY", "embed-key")
    holder = {}

    class Embeddings:
        def create(self, **kwargs):
            holder["kwargs"] = kwargs
            data = type("Data", (), {"embedding": [3.0, 4.0]})()
            return type("Response", (), {"data": [data]})()

    class Client:
        def __init__(self, **kwargs):
            holder["init"] = kwargs
            self.embeddings = Embeddings()

    monkeypatch.setattr("openai.OpenAI", Client)
    vector = embed("Nexova")
    assert holder["init"]["api_key"] == "embed-key"
    assert holder["init"]["base_url"] == "https://example.invalid/v1"
    assert holder["kwargs"]["model"] == "embed-model"
    assert holder["kwargs"]["model"] != "gen-model"
    assert abs(vector[0] - 0.6) < 1e-9
    assert abs(vector[1] - 0.8) < 1e-9
