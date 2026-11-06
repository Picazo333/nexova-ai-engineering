"""API-042 — supplier directory decisions. Not the auth module."""

from __future__ import annotations

from fastapi.testclient import TestClient

import directory
from tests.http_auth import attach_operator


def _contract(**overrides: object) -> dict:
    body = {
        "name": "Portal nuevo",
        "country": "Spain",
        "categories": ["job_boards"],
        "monthly_rate": 10,
        "currency": "EUR",
        "status": "active",
    }
    body.update(overrides)
    return body


def test_happy_path_a_spain_contract_is_stored_in_eur(client: TestClient) -> None:
    attach_operator(client)
    created = client.post("/suppliers", json=_contract())
    assert created.status_code == 201
    body = created.json()
    assert body["country"] == "Spain"
    assert body["currency"] == "EUR"
    assert body["monthly_rate"] == 10
    assert body["id"]
    stored = directory.get_supplier(body["id"])
    assert stored is not None
    assert stored["name"] == "Portal nuevo"
    assert stored["updated_at"]


def test_edge_a_category_filter_keeps_only_matching_contracts(client: TestClient) -> None:
    attach_operator(client)
    client.post("/suppliers", json=_contract(name="Bolsas", categories=["job_boards"]))
    client.post(
        "/suppliers",
        json=_contract(
            name="Nomina",
            categories=["payroll_and_hr_software"],
            country="USA",
            currency="USD",
        ),
    )
    listed = client.get("/suppliers", params={"category": "job_boards"})
    assert listed.status_code == 200
    names = [row["name"] for row in listed.json()]
    assert names == ["Bolsas"]
    # The smallest positive rate is still a rate. Zero is not.
    tiny = client.post("/suppliers", json=_contract(name="Casi cero", monthly_rate=0.01))
    assert tiny.status_code == 201
    assert tiny.json()["monthly_rate"] == 0.01
    zero = client.post("/suppliers", json=_contract(name="Gratis", monthly_rate=0))
    assert zero.status_code == 422
    assert directory.get_supplier(tiny.json()["id"])["monthly_rate"] == 0.01


def test_failure_unknown_id_and_a_currency_mismatch_do_not_change_the_directory(
    client: TestClient,
) -> None:
    attach_operator(client)
    before = directory.count_suppliers()
    missing = client.get("/suppliers/999999")
    assert missing.status_code == 404
    assert missing.json()["message"] == "No existe un proveedor con ese id."
    mismatch = client.post(
        "/suppliers",
        json=_contract(name="Moneda mal", country="Spain", currency="USD"),
    )
    assert mismatch.status_code == 422
    assert "EUR" in mismatch.text
    removed = client.delete("/suppliers/999999")
    assert removed.status_code == 404
    assert directory.count_suppliers() == before
    assert directory.get_supplier(999999) is None
