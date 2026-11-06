"""POST /agent/query on the shared FastAPI app. Retrieval and generation are doubles."""

import json

import pytest
from data.rag_errors import GenerationNotConfigured


@pytest.fixture(autouse=True)
def trace_dir(monkeypatch, tmp_path):
    monkeypatch.setenv("AGENT_TRACE_DIR", str(tmp_path))


def _chunk():
    return {
        "text": "Standard fee: 22% of the hired role's gross annual salary.",
        "source_document": "pricing-model",
        "section": "Executive headhunting",
        "language": "en",
    }


def test_endpoint_invokes_the_graph_and_stores_the_trace(client, monkeypatch):
    monkeypatch.setattr("data.pipelines.rag.retrieve", lambda question, **kwargs: [_chunk()])
    monkeypatch.setattr(
        "data.pipelines.rag.generate_answer",
        lambda question, context: "The standard fee is 22%.",
    )
    response = client.post(
        "/agent/query",
        json={"question": "What is the standard executive-search fee?"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["answer"] == "The standard fee is 22%."
    assert [item["node"] for item in body["trace"]["nodes"]] == [
        "receive_question",
        "retrieve_context",
        "generate_answer",
    ]
    assert body["trace"]["checkpoint_count"] >= 3
    stored = client.get(f"/agent/runs/{body['run_id']}")
    assert stored.status_code == 200
    assert stored.json()["run_id"] == body["run_id"]
    assert stored.json()["answer"] == body["answer"]


def test_endpoint_does_not_call_query(client, monkeypatch):
    def explode(question):
        raise AssertionError("query() must not run")

    monkeypatch.setattr("data.pipelines.rag.query", explode)
    monkeypatch.setattr("data.pipelines.rag.retrieve", lambda question, **kwargs: [_chunk()])
    monkeypatch.setattr(
        "data.pipelines.rag.generate_answer",
        lambda question, context: "The standard fee is 22%.",
    )
    response = client.post("/agent/query", json={"question": "What is the standard fee?"})
    assert response.status_code == 200


def test_blank_question_is_a_graph_decision(client, monkeypatch):
    def explode(*args, **kwargs):
        raise AssertionError("retrieve must not run")

    monkeypatch.setattr("data.pipelines.rag.retrieve", explode)
    response = client.post("/agent/query", json={"question": "   "})
    assert response.status_code == 422
    assert "consultar" in response.json()["detail"]
    assert "answer" not in response.json()
    assert response.json()["run_id"]


def test_empty_context_does_not_invent(client, monkeypatch):
    monkeypatch.setattr("data.pipelines.rag.retrieve", lambda question, **kwargs: [])

    def explode(*args, **kwargs):
        raise AssertionError("generate_answer must not run")

    monkeypatch.setattr("data.pipelines.rag.generate_answer", explode)
    response = client.post(
        "/agent/query",
        json={"question": "What is the office wifi password?"},
    )
    assert response.status_code == 200
    assert response.json()["answer"].startswith("I don't have information about that.")


def test_unconfigured_generation_has_no_stack(client, monkeypatch):
    monkeypatch.setattr("data.pipelines.rag.retrieve", lambda question, **kwargs: [_chunk()])

    def boom(question, context):
        raise GenerationNotConfigured()

    monkeypatch.setattr("data.pipelines.rag.generate_answer", boom)
    response = client.post("/agent/query", json={"question": "What is the standard fee?"})
    assert response.status_code == 503
    text = response.text
    assert "Traceback" not in text
    assert "answer" not in response.json()
    assert "not configured" in text.lower() or "configurado" in text.lower() or "configured" in text.lower()


def test_unexpected_failure_hides_internal_detail(client, monkeypatch):
    monkeypatch.setattr("data.pipelines.rag.retrieve", lambda question, **kwargs: [_chunk()])

    def boom(question, context):
        raise RuntimeError("SECRET_STACK /tmp/secret-trace")

    monkeypatch.setattr("data.pipelines.rag.generate_answer", boom)
    response = client.post("/agent/query", json={"question": "What is the standard fee?"})
    assert response.status_code == 502
    assert "SECRET_STACK" not in response.text
    assert "Traceback" not in response.text
    assert response.json()["detail"] == "El agente no pudo completar la respuesta."


def test_malformed_json_never_starts_the_graph(client, monkeypatch):
    def explode(*args, **kwargs):
        raise AssertionError("the graph must not start")

    monkeypatch.setattr("app.agent.graph.run_agent", explode)
    response = client.post(
        "/agent/query",
        content=b"{",
        headers={"content-type": "application/json"},
    )
    assert response.status_code == 422
    assert "JSON" in response.json()["detail"]


def test_unknown_run_is_a_clear_404(client):
    missing = client.get("/agent/runs/not-a-uuid")
    assert missing.status_code == 404
    assert "identificador" in missing.json()["detail"]
    random_id = "00000000-0000-4000-8000-000000000000"
    assert client.get(f"/agent/runs/{random_id}").status_code == 404


def test_trace_file_is_the_get_body(client, monkeypatch, tmp_path):
    monkeypatch.setattr("data.pipelines.rag.retrieve", lambda question, **kwargs: [_chunk()])
    monkeypatch.setattr(
        "data.pipelines.rag.generate_answer",
        lambda question, context: "The standard fee is 22%.",
    )
    response = client.post("/agent/query", json={"question": "fee"})
    run_id = response.json()["run_id"]
    on_disk = json.loads((tmp_path / f"{run_id}.json").read_text(encoding="utf-8"))
    assert on_disk["nodes"][0]["node"] == "receive_question"
    assert on_disk["checkpoint_count"] >= 3
