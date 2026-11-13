"""Password reset and change.

The reset token is a signed JWT (purpose, subject, expiry) and its SHA-256
is stored in TinyDB. A valid signature is not enough: the row has to exist,
be unused, and be inside the stored expiry. The raw token is never written
to the database. JWT `exp` alone cannot cancel a token that was already used.
"""

from __future__ import annotations

import hashlib
import logging
import os
import uuid
from datetime import datetime, timedelta, timezone
from urllib.parse import quote, urlsplit

from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError
from tinydb import Query

from app.auth.mailer import EmailMessage, MailerError, deliver, mailer_ready, render_reset_message
from app.auth.security import ALGORITHM, AuthConfigError, hash_password, jwt_secret, verify_password
from app.auth.store import auth_lock, reset_attempts_table, reset_tokens_table, users_table

logger = logging.getLogger("nexova.api")

FORGOT_MESSAGE = "Si esa dirección está registrada, recibirás un enlace en breve."
WINDOW = timedelta(hours=1)

_MESSAGES = {
    "expired": "El enlace ha caducado. Pide otro.",
    "used": "Este enlace ya se usó. Pide otro.",
    "invalid": "El enlace no es válido. Pide otro.",
    "current_password": "La contraseña actual no es correcta.",
    "same_password": "La nueva contraseña tiene que ser distinta de la actual.",
    "session": "El token no es válido o ha caducado.",
}


class RecoveryError(Exception):
    def __init__(self, code: str, status: int = 400) -> None:
        self.code = code
        self.status = status
        self.message = _MESSAGES[code]
        super().__init__(self.message)


def hash_reset_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def reset_expire_minutes() -> int:
    raw = os.environ.get("PASSWORD_RESET_EXPIRE_MINUTES", "30").strip() or "30"
    try:
        minutes = int(raw)
    except ValueError as exc:
        raise AuthConfigError("PASSWORD_RESET_EXPIRE_MINUTES tiene que ser un entero.") from exc
    if minutes < 15 or minutes > 60:
        raise AuthConfigError("PASSWORD_RESET_EXPIRE_MINUTES tiene que estar entre 15 y 60.")
    return minutes


def reset_max_per_hour() -> int:
    raw = os.environ.get("PASSWORD_RESET_MAX_PER_HOUR", "5").strip() or "5"
    try:
        limit = int(raw)
    except ValueError as exc:
        raise AuthConfigError("PASSWORD_RESET_MAX_PER_HOUR tiene que ser un entero.") from exc
    if limit < 1 or limit > 20:
        raise AuthConfigError("PASSWORD_RESET_MAX_PER_HOUR tiene que estar entre 1 y 20.")
    return limit


def public_app_url() -> str:
    raw = os.environ.get("PUBLIC_APP_URL", "http://127.0.0.1:3000").strip() or "http://127.0.0.1:3000"
    parts = urlsplit(raw)
    if parts.scheme not in {"http", "https"} or not parts.netloc:
        raise AuthConfigError("PUBLIC_APP_URL tiene que ser una URL http o https.")
    return raw.rstrip("/")


def build_reset_link(token: str) -> str:
    return f"{public_app_url()}/reset-password?token={quote(token, safe='')}"


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def _iso(value: datetime) -> str:
    return value.isoformat()


def _new_id() -> str:
    return str(uuid.uuid4())


def _purge_attempts(now: datetime) -> None:
    cutoff = _iso(now - WINDOW)
    reset_attempts_table().remove(Query().created_at < cutoff)


def _attempt_count(email: str) -> int:
    return len(reset_attempts_table().search(Query().email == email))


def _revoke_unlocked(user_id: str, now_iso: str) -> None:
    table = reset_tokens_table()
    for row in table.search(Query().user_id == user_id):
        if not row.get("used_at"):
            table.update({"used_at": now_iso}, Query().id == row["id"])


def _mark_used_unlocked(token_hash: str, now_iso: str) -> None:
    reset_tokens_table().update({"used_at": now_iso}, Query().token_hash == token_hash)


def revoke_reset_tokens(user_id: str) -> None:
    """Cancel outstanding reset links after a password change or a deletion."""
    with auth_lock():
        _revoke_unlocked(user_id, _iso(_now()))


def _sign(user_id: str, now: datetime, minutes: int) -> str:
    payload = {
        "sub": user_id,
        "purpose": "password_reset",
        "jti": _new_id(),
        "iat": int(now.timestamp()),
        "exp": now + timedelta(minutes=minutes),
    }
    return jwt.encode(payload, jwt_secret(), algorithm=ALGORITHM)


def request_password_reset(email: str, remote_addr: str) -> None:
    """Create and send a link when the account is active. Never raises for a miss.

    The HTTP layer always answers 200. This function logs a delivery failure
    without the address, the token, or the provider key.
    """
    try:
        minutes = reset_expire_minutes()
        limit = reset_max_per_hour()
        public_app_url()
    except AuthConfigError:
        logger.error("password reset settings are unusable")
        return
    if not mailer_ready():
        logger.error("password reset mailer is not configured")
        return

    now = _now()
    issued: str | None = None
    with auth_lock():
        _purge_attempts(now)
        if _attempt_count(email) >= limit:
            return
        reset_attempts_table().insert(
            {"id": _new_id(), "email": email, "created_at": _iso(now)}
        )
        user = users_table().get(Query().email == email)
        if user is None or not bool(user.get("is_active")):
            return
        user_id = str(user["id"])
        _revoke_unlocked(user_id, _iso(now))
        try:
            token = _sign(user_id, now, minutes)
        except AuthConfigError:
            logger.error("password reset signer is not configured")
            return
        expires_at = now + timedelta(minutes=minutes)
        reset_tokens_table().insert(
            {
                "id": _new_id(),
                "user_id": user_id,
                "token_hash": hash_reset_token(token),
                "expires_at": _iso(expires_at),
                "used_at": None,
                "created_at": _iso(now),
                "remote_addr": remote_addr[:64],
            }
        )
        issued = token

    if issued is None:
        return
    subject, text, html = render_reset_message(build_reset_link(issued), minutes)
    try:
        deliver(EmailMessage(to=email, subject=subject, text=text, html=html))
    except MailerError:
        logger.error("password reset mail was not delivered")
        with auth_lock():
            _mark_used_unlocked(hash_reset_token(issued), _iso(_now()))


def _decode(token: str) -> dict:
    if not token or len(token) > 2000:
        raise RecoveryError("invalid")
    try:
        payload = jwt.decode(token, jwt_secret(), algorithms=[ALGORITHM])
    except ExpiredSignatureError as exc:
        raise RecoveryError("expired") from exc
    except (JWTError, AuthConfigError) as exc:
        raise RecoveryError("invalid") from exc
    if not isinstance(payload, dict):
        raise RecoveryError("invalid")
    if payload.get("purpose") != "password_reset":
        raise RecoveryError("invalid")
    subject = payload.get("sub")
    if not isinstance(subject, str) or not subject:
        raise RecoveryError("invalid")
    return payload


def reset_password(token: str, new_password: str) -> None:
    """Validate the signed token and the stored row, then rotate the password.

    The check and the write share one lock, so two callers cannot both commit.
    """
    payload = _decode(token)
    digest = hash_reset_token(token)
    new_hash = hash_password(new_password)
    now = _now()
    now_iso = _iso(now)
    with auth_lock():
        table = reset_tokens_table()
        row = table.get(Query().token_hash == digest)
        if row is None:
            raise RecoveryError("invalid")
        if row.get("used_at"):
            raise RecoveryError("used")
        expires_at = datetime.fromisoformat(str(row["expires_at"]))
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if expires_at <= now:
            raise RecoveryError("expired")
        user_id = str(row["user_id"])
        if user_id != payload["sub"]:
            raise RecoveryError("invalid")
        user = users_table().get(Query().id == user_id)
        if user is None or not bool(user.get("is_active")):
            _mark_used_unlocked(digest, now_iso)
            raise RecoveryError("invalid")
        table.update({"used_at": now_iso}, Query().id == row["id"])
        users_table().update({"hashed_password": new_hash}, Query().id == user_id)
        _revoke_unlocked(user_id, now_iso)


def change_password(user_id: str, current_password: str, new_password: str) -> None:
    """Verify the current password, store a new hash, and cancel reset links."""
    new_hash = hash_password(new_password)
    now_iso = _iso(_now())
    with auth_lock():
        user = users_table().get(Query().id == user_id)
        if user is None or not bool(user.get("is_active")):
            raise RecoveryError("session", status=401)
        stored = str(user["hashed_password"])
        if not verify_password(current_password, stored):
            raise RecoveryError("current_password")
        if verify_password(new_password, stored):
            raise RecoveryError("same_password")
        users_table().update({"hashed_password": new_hash}, Query().id == user_id)
        _revoke_unlocked(user_id, now_iso)
