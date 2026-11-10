"""Supplier directory contract: briefing data, validation before TinyDB, and the page."""

from __future__ import annotations

import ast
import re
from datetime import date, timedelta
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

ROOT = Path(__file__).resolve().parents[3]


def _briefing(name: str) -> list[dict]:
    text = (ROOT / "scripts" / name).read_text(encoding="utf-8")
    match = re.search(r"```python\nSUPPLIERS_SEED = (\[.*?\])\n```", text, re.S)
    assert match, name
    return ast.literal_eval(match.group(1))


def _payload(**overrides: object) -> dict:
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


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("SUPPLIERS_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("SUPPLIERS_AUTOSEED", "1")
    monkeypatch.setenv("INCIDENTS_DATA_DIR", str(tmp_path / "incidents"))
    from database import reset_db
    from app.main import create_app

    reset_db()
    application = create_app()
    with TestClient(application) as test_client:
        from tests.http_auth import attach_operator

        attach_operator(test_client)
        yield test_client
    reset_db()


def test_seed_data_matches_nexova_briefings() -> None:
    from seed_data import SUPPLIERS_SEED

    spanish = _briefing("nexova-supplier-BRIEFING.es.md")
    english = _briefing("nexova-supplier-BRIEFING.en.md")
    assert SUPPLIERS_SEED == spanish
    assert len(spanish) == len(english) == 15
    for left, right in zip(spanish, english):
        assert set(left) == set(right)
        for key, value in left.items():
            if key == "notes":
                assert value != right[key]
            else:
                assert value == right[key]


def test_seed_is_idempotent_and_prints_the_inserted_count(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setenv("SUPPLIERS_DATA_DIR", str(tmp_path))
    from database import reset_db
    from directory import count_suppliers
    import seed

    reset_db()
    seed.main()
    first = capsys.readouterr().out
    assert "Se insertaron 15 registros." in first
    assert count_suppliers() == 15
    workable = next(item for item in seed.SUPPLIERS_SEED if item["name"] == "Workable")
    from directory import list_suppliers, update_rate

    stored = next(row for row in list_suppliers() if row["name"] == "Workable")
    update_rate(stored["id"], 111.0)
    seed.main()
    second = capsys.readouterr().out
    assert "Se insertaron 0 registros." in second
    assert "Se omitieron 15 registros ya presentes." in second
    assert count_suppliers() == 15
    again = next(row for row in list_suppliers() if row["name"] == "Workable")
    assert again["monthly_rate"] == 111.0
    assert again["monthly_rate"] != workable["monthly_rate"]
    reset_db()


def test_seed_validates_the_batch_before_any_insert(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SUPPLIERS_DATA_DIR", str(tmp_path))
    from database import reset_db
    from directory import count_suppliers
    from seed import seed_suppliers
    from seed_data import SUPPLIERS_SEED
    import seed

    reset_db()
    called = False

    def boom(_models: list) -> tuple[int, int]:
        nonlocal called
        called = True
        return (0, 0)

    monkeypatch.setattr(seed, "insert_missing", boom)
    bad = dict(SUPPLIERS_SEED[0])
    bad["monthly_rate"] = 0
    with pytest.raises(ValidationError):
        seed_suppliers([bad])
    bad_status = dict(SUPPLIERS_SEED[0])
    bad_status["status"] = "paused"
    with pytest.raises(ValidationError):
        seed_suppliers([bad_status])
    assert called is False
    assert count_suppliers() == 0
    reset_db()


def test_list_filters_and_unknown_id(client: TestClient) -> None:
    from seed_data import SUPPLIERS_SEED

    listing = client.get("/suppliers")
    assert listing.status_code == 200
    body = listing.json()
    assert [row["name"] for row in body] == [item["name"] for item in SUPPLIERS_SEED]
    by_name = {row["name"]: row for row in body}
    for item in SUPPLIERS_SEED:
        stored = by_name[item["name"]]
        assert stored["country"] == item["country"]
        assert stored["categories"] == item["categories"]
        assert stored["monthly_rate"] == item["monthly_rate"]
        assert stored["currency"] == item["currency"]
        assert stored["status"] == item["status"]
        assert stored["contact_email"] == item.get("contact_email")
        assert stored["notes"] == item.get("notes")
        assert stored["contract_renewal_date"] == item.get("contract_renewal_date")
        assert stored["id"]
        assert stored["updated_at"]

    spain = client.get("/suppliers", params={"country": "Spain"})
    assert spain.status_code == 200
    assert {row["country"] for row in spain.json()} == {"Spain"}
    assert len(spain.json()) == sum(1 for item in SUPPLIERS_SEED if item["country"] == "Spain")

    category = client.get("/suppliers", params={"category": "ats_software"})
    assert {row["name"] for row in category.json()} == {"Workable", "Greenhouse"}

    both = client.get("/suppliers", params={"country": "Spain", "category": "job_boards"})
    assert {row["name"] for row in both.json()} == {"LinkedIn Talent Solutions", "InfoJobs Premium"}

    assert client.get("/suppliers/999999").status_code == 404
    assert client.delete("/suppliers/999999").status_code == 404
    assert client.get("/suppliers", params={"category": "nope"}).status_code == 422
    assert client.get("/suppliers", params={"country": "France"}).status_code == 422
    assert client.get("/suppliers", params={"status": "archived"}).status_code == 422


def test_post_rejects_invalid_input_before_insert(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    import directory

    before = [row["id"] for row in client.get("/suppliers").json()]

    def boom(*_args: object, **_kwargs: object) -> dict:
        raise AssertionError("TinyDB no debía recibir un alta inválida")

    monkeypatch.setattr(directory, "create_supplier", boom)
    cases = [
        _payload(status="paused"),
        _payload(monthly_rate=0),
        _payload(monthly_rate=-4),
        _payload(currency="USD"),
        {key: value for key, value in _payload().items() if key != "country"},
        _payload(updated_at="2020-01-01T00:00:00+00:00"),
        _payload(categories=[]),
        _payload(categories=["unknown"]),
    ]
    for body in cases:
        response = client.post("/suppliers", json=body)
        assert response.status_code == 422, body
        assert response.json()["message"]
    assert [row["id"] for row in client.get("/suppliers").json()] == before


def test_post_returns_the_created_supplier(client: TestClient) -> None:
    created = client.post("/suppliers", json=_payload(notes="Alta de prueba"))
    assert created.status_code == 201
    body = created.json()
    assert isinstance(body["id"], int)
    assert body["name"] == "Portal nuevo"
    assert body["monthly_rate"] == 10
    assert body["updated_at"]
    fetched = client.get(f"/suppliers/{body['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["notes"] == "Alta de prueba"


def test_rate_status_and_delete(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    import directory

    supplier = next(row for row in client.get("/suppliers").json() if row["name"] == "Workable")

    def boom(*_args: object, **_kwargs: object) -> dict:
        raise AssertionError("TinyDB no debía guardar una tarifa o un estado inválidos")

    original_rate = directory.update_rate
    original_status = directory.update_status
    monkeypatch.setattr(directory, "update_rate", boom)
    monkeypatch.setattr(directory, "update_status", boom)
    assert client.patch(f"/suppliers/{supplier['id']}/rate", json={"monthly_rate": 0}).status_code == 422
    assert client.patch(f"/suppliers/{supplier['id']}/rate", json={"monthly_rate": -1}).status_code == 422
    assert client.patch(f"/suppliers/{supplier['id']}/status", json={"status": "closed"}).status_code == 422
    monkeypatch.setattr(directory, "update_rate", original_rate)
    monkeypatch.setattr(directory, "update_status", original_status)

    unchanged = next(row for row in client.get("/suppliers").json() if row["id"] == supplier["id"])
    assert unchanged["monthly_rate"] == supplier["monthly_rate"]
    assert unchanged["status"] == supplier["status"]
    assert unchanged["updated_at"] == supplier["updated_at"]

    updated = client.patch(f"/suppliers/{supplier['id']}/rate", json={"monthly_rate": 333})
    assert updated.status_code == 200
    assert updated.json()["monthly_rate"] == 333
    assert updated.json()["updated_at"] != supplier["updated_at"]

    suspended = client.patch(f"/suppliers/{supplier['id']}/status", json={"status": "suspended"})
    assert suspended.status_code == 200
    assert suspended.json()["status"] == "suspended"
    assert suspended.json()["updated_at"] == updated.json()["updated_at"]
    assert suspended.json()["monthly_rate"] == 333

    assert client.patch("/suppliers/999999/rate", json={"monthly_rate": 12}).status_code == 404
    assert client.patch("/suppliers/999999/status", json={"status": "active"}).status_code == 404

    removed = client.delete(f"/suppliers/{supplier['id']}")
    assert removed.status_code == 200
    assert removed.json()["name"] == "Workable"
    assert client.get(f"/suppliers/{supplier['id']}").status_code == 404
    assert client.delete(f"/suppliers/{supplier['id']}").status_code == 404


def test_directory_page_filters_badges_and_keeps_incidents(client: TestClient) -> None:
    page = client.get("/proveedores")
    assert page.status_code == 200
    assert "<h1>Directorio de proveedores</h1>" in page.text
    assert "LinkedIn Talent Solutions" in page.text
    assert "Activo (active)" in page.text
    assert "Suspendido (suspended)" in page.text
    assert "Renovación vencida" in page.text
    assert "signal-horizontal.svg" in page.text
    assert 'src="/js/suppliers.js"' in page.text
    filtered = client.get("/proveedores", params={"category": "ats_software"})
    assert "Workable" in filtered.text
    assert "Greenhouse" in filtered.text
    assert "LinkedIn Talent Solutions" not in filtered.text
    empty = client.get("/proveedores", params={"country": "USA", "category": "assessment_tools"})
    assert empty.status_code == 200
    assert "Ningún proveedor coincide" in empty.text
    fragment = client.get(
        "/proveedores",
        params={"country": "Spain"},
        headers={"X-Directory-Fragment": "1"},
    )
    assert fragment.status_code == 200
    assert "<html" not in fragment.text.lower()
    assert "WeWork Miami" not in fragment.text
    assert "InfoJobs Premium" in fragment.text
    hostile = client.get("/proveedores", params={"country": "<script>"})
    assert hostile.status_code == 422
    assert "<script>" not in hostile.text
    home = client.get("/")
    assert home.status_code == 200
    assert "Analizar fichero" in home.text
    assert 'href="/proveedores"' in home.text
    assert "account@linkedin.com" not in home.text


def test_upcoming_renewal_is_marked(client: TestClient) -> None:
    renewal = (date.today() + timedelta(days=10)).isoformat()
    created = client.post(
        "/suppliers",
        json=_payload(name="Renovación cercana", contract_renewal_date=renewal),
    )
    assert created.status_code == 201
    page = client.get("/proveedores", params={"country": "Spain", "category": "job_boards"})
    assert "Renovación en 10 días" in page.text
    assert "Renovación cercana" in page.text


def test_html_form_shows_the_api_error(client: TestClient) -> None:
    response = client.post(
        "/suppliers",
        data={
            "name": "Moneda cruzada",
            "country": "Spain",
            "categories": "job_boards",
            "monthly_rate": "15",
            "currency": "USD",
            "status": "active",
        },
        headers={"Accept": "text/html"},
    )
    assert response.status_code == 422
    assert "tiene que usar EUR" in response.text
    assert "Moneda cruzada" in response.text
    assert all(row["name"] != "Moneda cruzada" for row in client.get("/suppliers").json())


def test_records_survive_a_new_process(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SUPPLIERS_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("SUPPLIERS_AUTOSEED", "0")
    monkeypatch.setenv("INCIDENTS_DATA_DIR", str(tmp_path / "incidents"))
    from database import reset_db
    from app.main import create_app

    reset_db()
    from tests.http_auth import attach_operator

    with TestClient(create_app()) as first:
        attach_operator(first)
        empty = first.get("/proveedores")
        assert "El directorio está vacío" in empty.text
        created = first.post("/suppliers", json=_payload(name="Persistente"))
        assert created.status_code == 201
        supplier_id = created.json()["id"]
    reset_db()
    with TestClient(create_app()) as second:
        attach_operator(second)
        again = second.get(f"/suppliers/{supplier_id}")
        assert again.status_code == 200
        assert again.json()["name"] == "Persistente"
        page = second.get("/proveedores")
        assert "Persistente" in page.text
    assert (tmp_path / "suppliers.json").is_file()
    reset_db()
