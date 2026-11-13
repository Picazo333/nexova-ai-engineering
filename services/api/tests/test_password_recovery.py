"""Forgot, reset, and change password. The mail transport in these tests is mock.

A mocked HTTP call is not a real delivery. The Resend and SendGrid tests patch
httpx and use a local stand-in key that is not a provider credential.
"""

from __future__ import annotations

import threading
from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qs, urlsplit

import pytest
from fastapi.testclient import TestClient
from jose import jwt
from tinydb import Query

from app.auth.mailer import mock_outbox
from app.auth.recovery import hash_reset_token, reset_password
from app.auth.security import ALGORITHM
from app.auth.service import ServiceError, authenticate
from app.auth.store import auth_lock, db_file, reset_tokens_table
from tests.auth_support import PASSWORD, bearer, login, register, token_for

FORGOT = "Si esa dirección está registrada, recibirás un enlace en breve."
NEW_PASSWORD = "nueva-clave-9"
OTHER_PASSWORD = "otra-clave-99"


def _token_from_link(link: str) -> str:
    return parse_qs(urlsplit(link).query)["token"][0]


def _link_from_outbox(index: int = -1) -> str:
    text = mock_outbox()[index]["text"]
    for line in text.splitlines():
        if "/reset-password?token=" in line:
            return line.strip()
    raise AssertionError("el mensaje mock no trae el enlace")


def _issue(client: TestClient, email: str = "ana@nexova.test") -> str:
    response = client.post("/auth/forgot-password", json={"email": email})
    assert response.status_code == 200
    assert response.json() == {"message": FORGOT}
    return _token_from_link(_link_from_outbox())


def test_unknown_and_known_emails_share_the_same_200_body(client: TestClient) -> None:
    register(client, "ana@nexova.test")
    known = client.post("/auth/forgot-password", json={"email": "Ana@Nexova.test"})
    missing = client.post("/auth/forgot-password", json={"email": "nadie@nexova.test"})
    assert known.status_code == 200
    assert missing.status_code == 200
    assert known.content == missing.content
    assert known.json() == {"message": FORGOT}
    assert "ana@nexova.test" not in known.text
    assert len(mock_outbox()) == 1
    assert mock_outbox()[0]["to"] == "ana@nexova.test"


def test_inactive_account_gets_the_same_body_and_no_message(client: TestClient) -> None:
    from app.auth.service import create_user, update_user

    record = create_user(email="inactiva@nexova.test", password=PASSWORD, name="Inactiva")
    update_user(record["id"], {"is_active": False})
    response = client.post("/auth/forgot-password", json={"email": "inactiva@nexova.test"})
    known = client.post("/auth/forgot-password", json={"email": "nadie-2@nexova.test"})
    assert response.status_code == 200
    assert response.content == known.content
    assert mock_outbox() == []


def test_reset_link_is_signed_hashed_and_absent_from_the_database(client: TestClient) -> None:
    register(client, "ana@nexova.test")
    token = _issue(client)
    payload = jwt.decode(token, "test-jwt-secret-local-only", algorithms=[ALGORITHM])
    assert payload["purpose"] == "password_reset"
    assert payload["exp"] - payload["iat"] == 30 * 60
    stored = db_file().read_text(encoding="utf-8")
    assert token not in stored
    assert hash_reset_token(token) in stored
    message = mock_outbox()[0]
    assert message["subject"] == "Restablece tu contraseña de Nexova"
    assert token in message["text"]
    assert "viewport" in message["html"]
    assert "font-size:16px" in message["html"]
    assert "max-width:480px" in message["html"]
    assert token in message["html"]
    with auth_lock():
        row = reset_tokens_table().get(Query().token_hash == hash_reset_token(token))
    assert row is not None
    assert row["remote_addr"] == "testclient"
    assert row["used_at"] is None
    assert "testclient" not in client.post(
        "/auth/forgot-password", json={"email": "nadie@nexova.test"}
    ).text


def test_reset_updates_the_password_and_a_replay_does_not(client: TestClient) -> None:
    register(client, "ana@nexova.test")
    token = _issue(client)
    first = client.post(
        "/auth/reset-password",
        json={"token": token, "new_password": NEW_PASSWORD},
    )
    assert first.status_code == 200
    assert first.json()["message"] == "La contraseña se ha actualizado. Ya puedes entrar."
    replay = client.post(
        "/auth/reset-password",
        json={"token": token, "new_password": OTHER_PASSWORD},
    )
    assert replay.status_code == 400
    assert replay.json()["code"] == "used"
    assert replay.json()["message"] == "Este enlace ya se usó. Pide otro."
    assert client.post(
        "/auth/login", json={"email": "ana@nexova.test", "password": PASSWORD}
    ).status_code == 401
    assert client.post(
        "/auth/login", json={"email": "ana@nexova.test", "password": OTHER_PASSWORD}
    ).status_code == 401
    assert client.post(
        "/auth/login", json={"email": "ana@nexova.test", "password": NEW_PASSWORD}
    ).status_code == 200


def test_expired_database_row_is_rejected_while_the_signature_is_still_valid(
    client: TestClient,
) -> None:
    register(client, "ana@nexova.test")
    token = _issue(client)
    with auth_lock():
        updated = reset_tokens_table().update(
            {"expires_at": "2000-01-01T00:00:00+00:00"},
            Query().token_hash == hash_reset_token(token),
        )
    assert updated
    response = client.post(
        "/auth/reset-password",
        json={"token": token, "new_password": NEW_PASSWORD},
    )
    assert response.status_code == 400
    assert response.json()["code"] == "expired"
    assert client.post(
        "/auth/login", json={"email": "ana@nexova.test", "password": PASSWORD}
    ).status_code == 200


def test_expired_signature_is_400_even_if_the_row_has_not_reached_its_window(
    client: TestClient,
) -> None:
    created = register(client, "ana@nexova.test")
    now = datetime.now(timezone.utc) - timedelta(minutes=5)
    token = jwt.encode(
        {
            "sub": created["id"],
            "purpose": "password_reset",
            "iat": int(now.timestamp()),
            "exp": now + timedelta(minutes=1),
        },
        "test-jwt-secret-local-only",
        algorithm=ALGORITHM,
    )
    with auth_lock():
        reset_tokens_table().insert(
            {
                "id": "row-expired-signature",
                "user_id": created["id"],
                "token_hash": hash_reset_token(token),
                "expires_at": "2099-01-01T00:00:00+00:00",
                "used_at": None,
                "created_at": "2098-01-01T00:00:00+00:00",
                "remote_addr": "",
            }
        )
    response = client.post(
        "/auth/reset-password",
        json={"token": token, "new_password": NEW_PASSWORD},
    )
    assert response.status_code == 400
    assert response.json()["code"] == "expired"


def test_tampered_token_access_token_and_unknown_token_are_invalid(client: TestClient) -> None:
    register(client, "ana@nexova.test")
    token = _issue(client)
    access = token_for(client, "ana@nexova.test")
    tampered = token[:-1] + ("a" if token[-1] != "a" else "b")
    for bad in (tampered, access, "esto-no-es-un-jwt"):
        response = client.post(
            "/auth/reset-password",
            json={"token": bad, "new_password": NEW_PASSWORD},
        )
        assert response.status_code == 400
        assert response.json()["code"] == "invalid"
    assert client.post(
        "/auth/login", json={"email": "ana@nexova.test", "password": PASSWORD}
    ).status_code == 200


def test_a_newer_link_invalidates_the_previous_one(client: TestClient) -> None:
    register(client, "ana@nexova.test")
    first = _issue(client)
    second = _issue(client)
    assert first != second
    stale = client.post(
        "/auth/reset-password",
        json={"token": first, "new_password": NEW_PASSWORD},
    )
    assert stale.status_code == 400
    assert stale.json()["code"] == "used"
    fresh = client.post(
        "/auth/reset-password",
        json={"token": second, "new_password": NEW_PASSWORD},
    )
    assert fresh.status_code == 200


def test_concurrent_reset_commits_only_one_password(client: TestClient) -> None:
    register(client, "ana@nexova.test")
    token = _issue(client)
    barrier = threading.Barrier(2)
    results: list[tuple[str, str]] = []

    def run(password: str) -> None:
        barrier.wait()
        try:
            reset_password(token, password)
        except Exception as exc:
            code = getattr(exc, "code", type(exc).__name__)
            results.append((str(code), password))
            return
        results.append(("ok", password))

    threads = [
        threading.Thread(target=run, args=(NEW_PASSWORD,)),
        threading.Thread(target=run, args=(OTHER_PASSWORD,)),
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    winners = [item for item in results if item[0] == "ok"]
    assert len(results) == 2
    assert len(winners) == 1
    assert any(item[0] == "used" for item in results)
    winner = winners[0][1]
    loser = OTHER_PASSWORD if winner == NEW_PASSWORD else NEW_PASSWORD
    authenticate("ana@nexova.test", winner)
    with pytest.raises(ServiceError):
        authenticate("ana@nexova.test", loser)


def test_rate_limit_keeps_the_same_body_and_stops_sending(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("PASSWORD_RESET_MAX_PER_HOUR", "2")
    register(client, "ana@nexova.test")
    first = client.post("/auth/forgot-password", json={"email": "ana@nexova.test"})
    second = client.post("/auth/forgot-password", json={"email": "ana@nexova.test"})
    third = client.post("/auth/forgot-password", json={"email": "ana@nexova.test"})
    missing = client.post("/auth/forgot-password", json={"email": "nadie@nexova.test"})
    assert first.content == second.content == third.content == missing.content
    assert len(mock_outbox()) == 2


def test_short_and_unknown_fields_do_not_echo_the_password(client: TestClient) -> None:
    response = client.post(
        "/auth/reset-password",
        json={"token": "x", "new_password": "corta", "extra": "no"},
    )
    assert response.status_code == 422
    assert "corta" not in response.text
    forgot = client.post(
        "/auth/forgot-password",
        json={"email": "ana@nexova.test", "password": "clave-segura-1"},
    )
    assert forgot.status_code == 422
    assert "clave-segura-1" not in forgot.text


def test_change_password_rejects_a_wrong_current_password_and_keeps_the_old_one(
    client: TestClient,
) -> None:
    register(client, "ana@nexova.test")
    missing = client.post(
        "/auth/change-password",
        json={"current_password": PASSWORD, "new_password": NEW_PASSWORD},
    )
    assert missing.status_code == 401
    token = token_for(client, "ana@nexova.test")
    wrong = client.post(
        "/auth/change-password",
        headers=bearer(token),
        json={"current_password": "clave-erronea", "new_password": NEW_PASSWORD},
    )
    assert wrong.status_code == 400
    assert wrong.json()["code"] == "current_password"
    same = client.post(
        "/auth/change-password",
        headers=bearer(token),
        json={"current_password": PASSWORD, "new_password": PASSWORD},
    )
    assert same.status_code == 400
    assert same.json()["code"] == "same_password"
    login(client, "ana@nexova.test", PASSWORD)


def test_change_password_rotates_the_hash_and_cancels_reset_links(client: TestClient) -> None:
    register(client, "ana@nexova.test")
    reset_token = _issue(client)
    access = token_for(client, "ana@nexova.test")
    changed = client.post(
        "/auth/change-password",
        headers=bearer(access),
        json={"current_password": PASSWORD, "new_password": NEW_PASSWORD},
    )
    assert changed.status_code == 200
    stale = client.post(
        "/auth/reset-password",
        json={"token": reset_token, "new_password": OTHER_PASSWORD},
    )
    assert stale.status_code == 400
    assert stale.json()["code"] == "used"
    assert client.post(
        "/auth/login", json={"email": "ana@nexova.test", "password": PASSWORD}
    ).status_code == 401
    login(client, "ana@nexova.test", NEW_PASSWORD)


def test_openapi_lists_the_three_routes_and_the_example_keys_are_empty() -> None:
    from pathlib import Path

    example = Path(__file__).resolve().parents[1] / ".env.example"
    text = example.read_text(encoding="utf-8")
    for name in ("RESEND_API_KEY", "SENDGRID_API_KEY"):
        line = next(item for item in text.splitlines() if item.startswith(f"{name}="))
        assert line == f"{name}="
    source = Path(__file__).resolve().parents[1].joinpath("app", "auth", "mailer.py").read_text(
        encoding="utf-8"
    )
    assert "RESEND_API_KEY" in source
    assert "local-test-resend-key" not in source
    assert "SG." not in source


def test_openapi_paths(client: TestClient) -> None:
    spec = client.get("/api/openapi.json")
    assert spec.status_code == 200
    paths = spec.json()["paths"]
    assert "/auth/forgot-password" in paths
    assert "/auth/reset-password" in paths
    assert "/auth/change-password" in paths


def test_mock_transport_does_not_call_httpx(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    def blocked(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("el transporte mock no puede abrir una conexión")

    monkeypatch.setattr("app.auth.mailer.httpx.post", blocked)
    register(client, "ana@nexova.test")
    response = client.post("/auth/forgot-password", json={"email": "ana@nexova.test"})
    assert response.status_code == 200
    assert len(mock_outbox()) == 1


def test_resend_builder_posts_the_link_and_a_missing_key_does_not(
    client: TestClient, monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    calls: list[dict[str, object]] = []

    def fake_post(url: str, **kwargs: object) -> object:
        calls.append({"url": url, "headers": kwargs.get("headers"), "json": kwargs.get("json")})

        class Response:
            status_code = 200

        return Response()

    monkeypatch.setattr("app.auth.mailer.httpx.post", fake_post)
    monkeypatch.setenv("EMAIL_TRANSPORT", "resend")
    monkeypatch.setenv("RESEND_API_KEY", "local-test-resend-key")
    monkeypatch.setenv("PASSWORD_RESET_CAPTURE_FILE", str(tmp_path / "must-not-exist.txt"))
    register(client, "ana@nexova.test")
    response = client.post("/auth/forgot-password", json={"email": "ana@nexova.test"})
    assert response.status_code == 200
    assert response.json() == {"message": FORGOT}
    assert "local-test-resend-key" not in response.text
    assert mock_outbox() == []
    assert not (tmp_path / "must-not-exist.txt").exists()
    assert len(calls) == 1
    assert calls[0]["url"] == "https://api.resend.com/emails"
    headers = calls[0]["headers"]
    assert isinstance(headers, dict)
    assert headers["Authorization"] == "Bearer local-test-resend-key"
    body = calls[0]["json"]
    assert isinstance(body, dict)
    assert body["to"] == ["ana@nexova.test"]
    assert "/reset-password?token=" in str(body["text"])
    assert "font-size:16px" in str(body["html"])
    link = next(line for line in str(body["text"]).splitlines() if "/reset-password?token=" in line)
    token = _token_from_link(link.strip())
    assert token not in db_file().read_text(encoding="utf-8")
    reset = client.post(
        "/auth/reset-password",
        json={"token": token, "new_password": NEW_PASSWORD},
    )
    assert reset.status_code == 200

    calls.clear()
    monkeypatch.delenv("RESEND_API_KEY", raising=False)
    refused = client.post("/auth/forgot-password", json={"email": "ana@nexova.test"})
    assert refused.status_code == 200
    assert refused.content == response.content
    assert calls == []


def test_sendgrid_builder_posts_without_a_network_socket(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.auth.mailer import EmailMessage, MailerDeliveryError, MailerNotConfigured, deliver

    seen: dict[str, object] = {}

    def fake_post(url: str, **kwargs: object) -> object:
        seen["url"] = url
        seen["headers"] = kwargs.get("headers")
        seen["json"] = kwargs.get("json")

        class Response:
            status_code = 202

        return Response()

    monkeypatch.setattr("app.auth.mailer.httpx.post", fake_post)
    monkeypatch.setenv("EMAIL_TRANSPORT", "sendgrid")
    monkeypatch.setenv("SENDGRID_API_KEY", "local-test-sendgrid-key")
    monkeypatch.setenv("EMAIL_FROM", "Nexova <onboarding@resend.dev>")
    deliver(
        EmailMessage(
            to="ana@nexova.test",
            subject="Restablece tu contraseña de Nexova",
            text="https://portal.example/reset-password?token=abc",
            html="<p>https://portal.example/reset-password?token=abc</p>",
        )
    )
    assert seen["url"] == "https://api.sendgrid.com/v3/mail/send"
    headers = seen["headers"]
    assert isinstance(headers, dict)
    assert headers["Authorization"] == "Bearer local-test-sendgrid-key"
    payload = seen["json"]
    assert isinstance(payload, dict)
    assert payload["from"] == {"email": "onboarding@resend.dev", "name": "Nexova"}
    assert "local-test-sendgrid-key" not in str(payload)

    def rejected(url: str, **kwargs: object) -> object:
        class Response:
            status_code = 403

        return Response()

    monkeypatch.setattr("app.auth.mailer.httpx.post", rejected)
    with pytest.raises(MailerDeliveryError) as caught:
        deliver(
            EmailMessage(
                to="ana@nexova.test",
                subject="Restablece tu contraseña de Nexova",
                text="enlace",
                html="<p>enlace</p>",
            )
        )
    assert "local-test-sendgrid-key" not in str(caught.value)

    monkeypatch.delenv("SENDGRID_API_KEY", raising=False)
    with pytest.raises(MailerNotConfigured):
        deliver(
            EmailMessage(
                to="ana@nexova.test",
                subject="Restablece tu contraseña de Nexova",
                text="enlace",
                html="<p>enlace</p>",
            )
        )
