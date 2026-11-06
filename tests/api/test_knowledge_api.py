"""The HTTP endpoint returns the model string and nothing from Qdrant."""

from fastapi.testclient import TestClient

from data.rag_errors import GenerationNotConfigured
from services.api.app import create_app


def test_json_endpoint_returns_only_the_answer(monkeypatch):
    monkeypatch.setattr("data.pipelines.rag.query", lambda question: "Respuesta del modelo.")
    client = TestClient(create_app())
    response = client.post(
        "/knowledge/query",
        json={"question": "¿Cuánto cuesta un programa de formación de 8 semanas?"},
    )
    assert response.status_code == 200
    assert response.json() == {"answer": "Respuesta del modelo."}
    assert "score" not in response.text
    assert "source_document" not in response.text


def test_unconfigured_generation_is_an_error_not_an_empty_answer(monkeypatch):
    def boom(question):
        raise GenerationNotConfigured()

    monkeypatch.setattr("data.pipelines.rag.query", boom)
    client = TestClient(create_app())
    response = client.post("/knowledge/query", json={"question": "¿Cuál es la tarifa?"})
    assert response.status_code == 503
    body = response.json()
    assert "answer" not in body
    assert "detail" in body
    assert body["detail"]


def test_blank_question_is_rejected(monkeypatch):
    monkeypatch.setattr(
        "data.pipelines.rag.query",
        lambda question: (_ for _ in ()).throw(AssertionError("query should not run")),
    )
    client = TestClient(create_app())
    response = client.post("/knowledge/query", json={"question": "   "})
    assert response.status_code == 422
    assert "answer" not in response.json()


def test_form_post_renders_the_model_answer(monkeypatch):
    monkeypatch.setattr("data.pipelines.rag.query", lambda question: "Sources: pricing-model — Formación corporativa")
    client = TestClient(create_app())
    response = client.post(
        "/knowledge/query",
        data={"question": "¿Cuánto cuesta un programa de formación de 8 semanas?"},
        headers={"Accept": "text/html"},
    )
    assert response.status_code == 200
    assert "Fuentes citadas" in response.text
    assert "pricing-model" in response.text
    assert "score" not in response.text


def test_catalog_lists_eight_official_documents():
    client = TestClient(create_app())
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


def test_unknown_html_route_is_a_real_404():
    client = TestClient(create_app())
    response = client.get("/no-existe", headers={"Accept": "text/html"})
    assert response.status_code == 404
    assert "Esa ruta no existe" in response.text
