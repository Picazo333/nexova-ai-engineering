"""GET /api/incidents/summary on an empty database.

Rubric 016 (ai-eng-centralized-incident-manager): "El endpoint `/summary`
devuelve métricas correctas aunque no haya incidencias." and "Los endpoints de
lectura no fallan si la base de datos está vacía: devuelven lista vacía o
métricas en cero."
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from nexova_incidents.model import BRANCHES, CATEGORIES, ORIGINS, STATUSES
from tests.http_auth import attach_operator


def test_summary_is_all_zeros_with_every_briefing_key_when_there_are_no_incidents(client: TestClient) -> None:
    attach_operator(client)
    assert client.get("/api/incidents").json() == []  # the store really is empty

    response = client.get("/api/incidents/summary")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 0
    # Every bucket lists every allowed code, so the panel can render zeros
    # instead of an empty table.
    for bucket, codes in (
        ("by_status", STATUSES),
        ("by_category", CATEGORIES),
        ("by_origin", ORIGINS),
        ("by_branch", BRANCHES),
    ):
        assert body[bucket] == {code: 0 for code, _label in codes}, bucket


def test_empty_summary_still_requires_a_token(client: TestClient) -> None:
    # Empty data must not turn the route public.
    assert client.get("/api/incidents/summary").status_code == 401
