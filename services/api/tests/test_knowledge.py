"""Knowledge routes on the shared FastAPI app. Qdrant and the LLM stay mocked."""

from data.rag_errors import GenerationNotConfigured


def test_json_endpoint_returns_only_the_answer(client, monkeypatch):
    monkeypatch.setattr("data.pipelines.rag.query", lambda question: "Respuesta del modelo.")
    response = client.post(
        "/knowledge/query",
        json={"question": "¿Cuánto cuesta un programa de formación de 8 semanas?"},
    )
    assert response.status_code == 200
    assert response.json() == {"answer": "Respuesta del modelo."}
    assert "score" not in response.text
    assert "source_document" not in response.text


def test_unconfigured_generation_is_an_error_not_an_empty_answer(client, monkeypatch):
    def boom(question):
        raise GenerationNotConfigured()

    monkeypatch.setattr("data.pipelines.rag.query", boom)
    response = client.post("/knowledge/query", json={"question": "¿Cuál es la tarifa?"})
    assert response.status_code == 503
    body = response.json()
    assert "answer" not in body
    assert body["detail"]
    assert "inventó" in body["detail"]


def test_blank_question_is_rejected(client, monkeypatch):
    monkeypatch.setattr(
        "data.pipelines.rag.query",
        lambda question: (_ for _ in ()).throw(AssertionError("query should not run")),
    )
    response = client.post("/knowledge/query", json={"question": "   "})
    assert response.status_code == 422
    assert "answer" not in response.json()


def test_form_post_renders_the_model_answer(client, monkeypatch):
    monkeypatch.setattr("data.pipelines.rag.query", lambda question: "Sources: pricing-model — Formación corporativa")
    response = client.post(
        "/knowledge/query",
        data={"question": "¿Cuánto cuesta un programa de formación de 8 semanas?"},
        headers={"Accept": "text/html"},
    )
    assert response.status_code == 200
    assert "Fuentes citadas" in response.text
    assert "pricing-model" in response.text
    assert "score" not in response.text
    assert "signal-horizontal.svg" in response.text


def test_catalog_lists_eight_official_documents(client):
    response = client.get("/knowledge/catalog")
    assert response.status_code == 200
    documents = response.json()["documents"]
    assert len(documents) == 8
    assert {item["source_document"] for item in documents} == {
        "service-lines",
        "pricing-model",
        "hiring-process-sla",
        "objection-handling",
    }


def test_knowledge_page_uses_the_official_lockup(client):
    response = client.get("/conocimiento")
    assert response.status_code == 200
    assert "Pregunta de un prospecto" in response.text
    assert "/ui/brand/signal-horizontal.svg" in response.text


def test_truncated_gra_is_not_a_200_answer(client, monkeypatch):
    monkeypatch.setenv("GENERATION_MODEL_ID", "gen-model")
    monkeypatch.setenv("GENERATION_BASE_URL", "https://example.invalid/v1")
    monkeypatch.setenv("GENERATION_API_KEY", "test-key")
    monkeypatch.setenv("EMBEDDING_MODEL_ID", "embed-model")
    monkeypatch.setattr(
        "data.pipelines.rag.retrieve",
        lambda question, **kwargs: [
            {
                "text": "Tiempo promedio de entrega: 6 a 8 semanas.",
                "source_document": "service-lines",
                "section": "Headhunting ejecutivo y de mandos medios",
                "language": "es",
            }
        ],
    )
    calls = {"n": 0}

    class _Completions:
        def create(self, **kwargs):
            calls["n"] += 1
            message = type("Message", (), {"content": "Gra"})()
            choice = type("Choice", (), {"message": message, "finish_reason": "length"})()
            return type("Response", (), {"choices": [choice]})()

    class _Client:
        def __init__(self, **kwargs):
            self.chat = type("Chat", (), {"completions": _Completions()})()

    monkeypatch.setattr("openai.OpenAI", _Client)
    response = client.post(
        "/knowledge/query",
        json={"question": "¿Cuánto tarda una búsqueda ejecutiva?"},
    )
    assert response.status_code == 502
    body = response.json()
    assert "answer" not in body
    assert "Gra" not in response.text
    assert calls["n"] == 2


def test_unknown_html_route_stays_the_backoffice_404(client):
    response = client.get("/no-existe", headers={"Accept": "text/html"})
    assert response.status_code == 404
    assert "No encontramos esa ruta" in response.text
