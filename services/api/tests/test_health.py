"""GET /health is the Compose probe. It does not require a session."""

from fastapi.testclient import TestClient


def test_health_is_ok_without_a_token(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert "localhost" not in response.text
