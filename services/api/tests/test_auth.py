"""JWT auth: TinyDB users, ownership, expiry, and the routes inherited from 009 and 011."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from jose import jwt

ROOT = Path(__file__).resolve().parents[3]
API_ROOT = ROOT / "services" / "api"
PASSWORD = "clave-segura-1"

EXISTING_PROTECTED = (
    ("GET", "/suppliers"),
    ("GET", "/suppliers/999999"),
    ("POST", "/suppliers"),
    ("PATCH", "/suppliers/999999/rate"),
    ("POST", "/suppliers/999999/rate"),
    ("PATCH", "/suppliers/999999/status"),
    ("POST", "/suppliers/999999/status"),
    ("DELETE", "/suppliers/999999"),
    ("POST", "/api/incidents/analyze"),
    ("GET", "/api/incidents/results/export"),
)


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("SUPPLIERS_DATA_DIR", str(tmp_path / "suppliers"))
    monkeypatch.setenv("SUPPLIERS_AUTOSEED", "0")
    monkeypatch.setenv("INCIDENTS_DATA_DIR", str(tmp_path / "incidents"))
    from app.auth.store import reset_auth_db
    from app.infrastructure.analysis_store import reset_store
    from app.main import create_app
    from database import reset_db

    reset_db()
    reset_auth_db()
    reset_store(tmp_path / "incidents")
    with TestClient(create_app()) as test_client:
        yield test_client
    reset_db()
    reset_auth_db()


def _register(client: TestClient, email: str, name: str, **extra: object) -> dict:
    body = {"email": email, "password": PASSWORD, "name": name}
    body.update(extra)
    response = client.post("/users", json=body)
    assert response.status_code == 201, response.text
    return response.json()


def _login(client: TestClient, email: str, password: str = PASSWORD) -> str:
    response = client.post("/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_register_hashes_the_password_and_stores_contact_on_the_profile(client: TestClient) -> None:
    created = _register(
        client,
        "ana@nexova.test",
        "Ana Soler",
        phone="+34 600 000 000",
        address="Calle Mayor 1",
    )
    assert created["role"] == "user"
    assert created["is_active"] is True
    assert created["profile"]["name"] == "Ana Soler"
    assert created["profile"]["user_id"] == created["id"]
    assert "hashed_password" not in created
    assert PASSWORD not in str(created)
    assert "hashed_password" not in str(created)

    from app.auth.service import get_profile_by_user_id, get_user_by_email

    stored = get_user_by_email("ana@nexova.test")
    assert stored is not None
    assert set(stored) == {"id", "email", "hashed_password", "is_active", "role", "created_at"}
    assert stored["hashed_password"] != PASSWORD
    assert stored["hashed_password"].startswith("$2")
    assert "name" not in stored
    profile = get_profile_by_user_id(stored["id"])
    assert profile is not None
    assert profile["user_id"] == stored["id"]
    assert profile["phone"] == "+34 600 000 000"
    assert profile["address"] == "Calle Mayor 1"


def test_role_is_constrained_and_registration_cannot_choose_it(client: TestClient) -> None:
    rejected = client.post(
        "/users",
        json={"email": "admin-hope@nexova.test", "password": PASSWORD, "role": "admin"},
    )
    assert rejected.status_code == 422
    from app.auth.service import ServiceError, create_user

    with pytest.raises(ServiceError) as caught:
        create_user(email="owner@nexova.test", password=PASSWORD, role="owner")
    assert caught.value.status_code == 422
    created = _register(client, "ana@nexova.test", "Ana")
    assert created["role"] == "user"
    token = _login(client, "ana@nexova.test")
    bad = client.put(
        f"/users/{created['id']}",
        json={"role": "superuser"},
        headers=_auth(token),
    )
    assert bad.status_code == 422


def test_login_returns_a_signed_token_with_the_tinydb_id(client: TestClient) -> None:
    created = _register(client, "ana@nexova.test", "Ana")
    logged = client.post(
        "/auth/login",
        data={"username": "Ana@Nexova.test", "password": PASSWORD},
    )
    assert logged.status_code == 200
    assert "set-cookie" not in {key.lower() for key in logged.headers}
    body = logged.json()
    assert body["token_type"] == "bearer"
    assert body["user_uuid"] == created["id"]
    assert body["expires_in"] == 30 * 60
    payload = jwt.decode(body["access_token"], "test-jwt-secret-local-only", algorithms=["HS256"])
    assert payload["sub"] == created["id"]
    assert payload["user_uuid"] == created["id"]
    me = client.get("/auth/me", headers=_auth(body["access_token"]))
    assert me.status_code == 200
    assert me.json()["email"] == "ana@nexova.test"
    assert me.json()["role"] == "user"
    assert me.json()["profile"]["name"] == "Ana"
    wrong = client.post("/auth/login", json={"email": "ana@nexova.test", "password": "clave-erronea"})
    assert wrong.status_code == 401
    assert wrong.json()["message"] == "El correo o la contraseña no son válidos."


def test_missing_malformed_and_expired_tokens_are_401(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    created = _register(client, "ana@nexova.test", "Ana")
    missing = client.get("/profiles/me")
    assert missing.status_code == 401
    assert missing.json()["error"] == "unauthorized"
    malformed = client.get("/users", headers={"Authorization": "Bearer esto-no-es-un-jwt"})
    assert malformed.status_code == 401
    other = jwt.encode({"sub": created["id"], "user_uuid": created["id"]}, "otro-secreto-distinto", algorithm="HS256")
    forged = client.get("/auth/me", headers=_auth(other))
    assert forged.status_code == 401
    fresh = _login(client, "ana@nexova.test")
    monkeypatch.setenv("ACCESS_TOKEN_EXPIRE_MINUTES", "-1")
    logged = client.post("/auth/login", json={"email": "ana@nexova.test", "password": PASSWORD})
    assert logged.status_code == 200
    expired = client.get("/suppliers", headers=_auth(logged.json()["access_token"]))
    assert expired.status_code == 401
    assert expired.json()["message"]
    still_valid = client.get("/auth/me", headers=_auth(fresh))
    assert still_valid.status_code == 200


def test_other_users_credentials_return_403_and_profile_stays_private(client: TestClient) -> None:
    ana = _register(client, "ana@nexova.test", "Ana")
    luis = _register(client, "luis@nexova.test", "Luis", phone="600111111")
    ana_token = _login(client, "ana@nexova.test")
    headers = _auth(ana_token)
    assert client.get(f"/users/{luis['id']}", headers=headers).status_code == 403
    renamed = client.put(
        f"/users/{luis['id']}",
        json={"email": "otro@nexova.test"},
        headers=headers,
    )
    assert renamed.status_code == 403
    assert client.delete(f"/users/{luis['id']}", headers=headers).status_code == 403
    role = client.put(f"/users/{ana['id']}", json={"role": "manager"}, headers=headers)
    assert role.status_code == 403
    own = client.put("/profiles/me", json={"name": "Ana Soler", "address": "Gran Vía 2"}, headers=headers)
    assert own.status_code == 200
    assert own.json()["user_id"] == ana["id"]
    assert own.json()["name"] == "Ana Soler"
    luis_me = client.get("/auth/me", headers=_auth(_login(client, "luis@nexova.test")))
    assert luis_me.status_code == 200
    assert luis_me.json()["profile"]["name"] == "Luis"
    assert luis_me.json()["profile"]["phone"] == "600111111"
    assert luis_me.json()["profile"]["address"] is None

    from app.auth.service import create_user

    create_user(email="admin@nexova.test", password="clave-admin-1", role="admin")
    admin = _auth(_login(client, "admin@nexova.test", "clave-admin-1"))
    promoted = client.put(f"/users/{luis['id']}", json={"role": "manager"}, headers=admin)
    assert promoted.status_code == 200
    assert promoted.json()["role"] == "manager"
    assert promoted.json()["profile"]["name"] == "Luis"
    own_email = client.put(
        f"/users/{ana['id']}",
        json={"email": "ana.soler@nexova.test"},
        headers=headers,
    )
    assert own_email.status_code == 200
    assert own_email.json()["email"] == "ana.soler@nexova.test"
    removed = client.delete(f"/users/{ana['id']}", headers=headers)
    assert removed.status_code == 200
    assert "hashed_password" not in removed.json()
    from app.auth.service import get_profile_by_user_id

    assert get_profile_by_user_id(ana["id"]) is None
    assert client.post(
        "/auth/login",
        json={"email": "ana.soler@nexova.test", "password": PASSWORD},
    ).status_code == 401


def test_duplicate_email_and_inactive_user(client: TestClient) -> None:
    _register(client, "ana@nexova.test", "Ana")
    again = client.post("/users", json={"email": "Ana@nexova.test", "password": PASSWORD})
    assert again.status_code == 409
    from app.auth.service import create_user, update_user

    record = create_user(email="baja@nexova.test", password=PASSWORD, name="Baja")
    update_user(record["id"], {"is_active": False})
    refused = client.post("/auth/login", json={"email": "baja@nexova.test", "password": PASSWORD})
    assert refused.status_code == 401


def test_secret_and_lifetime_come_from_the_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    from app.auth.security import AuthConfigError, expire_minutes, jwt_secret

    assert jwt_secret() == "test-jwt-secret-local-only"
    assert expire_minutes() == 30
    monkeypatch.delenv("JWT_SECRET")
    with pytest.raises(AuthConfigError):
        jwt_secret()
    monkeypatch.setenv("JWT_SECRET", "change-me")
    with pytest.raises(AuthConfigError):
        jwt_secret()
    monkeypatch.setenv("JWT_SECRET", "test-jwt-secret-local-only")
    monkeypatch.delenv("ACCESS_TOKEN_EXPIRE_MINUTES")
    with pytest.raises(AuthConfigError):
        expire_minutes()
    source = (API_ROOT / "app" / "auth" / "security.py").read_text(encoding="utf-8")
    assert "from passlib.hash import bcrypt" in source
    assert "JWT_SECRET" in source
    project = (API_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert 'libpass[bcrypt]' in project
    assert "passlib[" not in project
    sources = [
        path
        for path in API_ROOT.rglob("*.py")
        if "tests" not in path.parts and ".venv" not in path.parts
    ]
    tree = "\n".join(path.read_text(encoding="utf-8") for path in sources)
    assert "import sqlmodel" not in tree.lower()
    assert "import supabase" not in tree.lower()


def test_existing_monorepo_routes_require_a_token_and_still_run(client: TestClient) -> None:
    assert len(EXISTING_PROTECTED) >= 5
    for method, path in EXISTING_PROTECTED:
        assert not path.startswith("/users")
        assert not path.startswith("/auth")
        blocked = client.request(method, path)
        assert blocked.status_code == 401, (method, path, blocked.status_code, blocked.text)

    from tests.http_auth import attach_operator

    attach_operator(client)
    opened = client.get("/suppliers")
    assert opened.status_code == 200
    assert opened.json() == []
    missing = client.get("/suppliers/999999")
    assert missing.status_code == 404
    invalid = client.post("/suppliers", json={})
    assert invalid.status_code == 422
    rate = client.patch("/suppliers/999999/rate", json={"monthly_rate": 0})
    assert rate.status_code == 422
    status = client.patch("/suppliers/999999/status", json={"status": "closed"})
    assert status.status_code == 422
    absent_rate = client.patch("/suppliers/999999/rate", json={"monthly_rate": 12})
    assert absent_rate.status_code == 404
    absent_status = client.patch("/suppliers/999999/status", json={"status": "active"})
    assert absent_status.status_code == 404
    removed = client.delete("/suppliers/999999")
    assert removed.status_code == 404
    form_rate = client.post("/suppliers/999999/rate", json={"monthly_rate": 12})
    assert form_rate.status_code == 404
    form_status = client.post("/suppliers/999999/status", json={"status": "active"})
    assert form_status.status_code == 404
    analyze = client.post("/api/incidents/analyze")
    assert analyze.status_code == 400
    assert analyze.json()["error"] == "missing_file"
    export = client.get("/api/incidents/results/export")
    assert export.status_code == 404
    assert export.json()["error"] == "no_analysis"
    listing = client.get("/users")
    assert listing.status_code == 200
    assert listing.json()
    assert "hashed_password" not in listing.text


def test_directory_page_omits_supplier_rows_without_a_token(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SUPPLIERS_DATA_DIR", str(tmp_path / "suppliers"))
    monkeypatch.setenv("SUPPLIERS_AUTOSEED", "1")
    monkeypatch.setenv("INCIDENTS_DATA_DIR", str(tmp_path / "incidents"))
    from app.auth.store import reset_auth_db
    from app.main import create_app
    from database import reset_db

    reset_db()
    reset_auth_db()
    with TestClient(create_app()) as bare:
        page = bare.get("/proveedores")
        assert page.status_code == 200
        assert "Hace falta una sesión" in page.text
        assert "LinkedIn Talent Solutions" not in page.text
        assert "Entrar" in page.text
        assert "@" not in page.text
        fragment = bare.get("/proveedores", headers={"X-Directory-Fragment": "1"})
        assert fragment.status_code == 401
        from tests.http_auth import attach_operator

        attach_operator(bare)
        opened = bare.get("/proveedores")
        assert opened.status_code == 200
        assert "LinkedIn Talent Solutions" in opened.text
        assert "Hace falta una sesión" not in opened.text
    reset_db()
    reset_auth_db()


def test_protected_routes_are_the_ones_declared_in_the_source() -> None:
    """The five-route minimum is met by routes that already existed, not by new stubs."""
    suppliers = (API_ROOT / "routes" / "suppliers.py").read_text(encoding="utf-8")
    incidents = (API_ROOT / "app" / "routers" / "incidents.py").read_text(encoding="utf-8")
    assert "dependencies=[Depends(get_current_user)]" in suppliers
    assert "dependencies=[Depends(get_current_user)]" in incidents
    tree = ast.parse(suppliers)
    routes = [
        decorator
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        for decorator in node.decorator_list
        if isinstance(decorator, ast.Call)
        and isinstance(decorator.func, ast.Attribute)
        and decorator.func.attr in {"get", "post", "patch", "delete", "put"}
    ]
    assert len(routes) >= 8
