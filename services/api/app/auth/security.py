"""Password hashing and JWT signing.

The signing secret and the token lifetime come from the environment. Nothing
in this module falls back to a built-in secret.
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.hash import bcrypt

ALGORITHM = "HS256"
PLACEHOLDER_SECRETS = {
    "",
    "change-me",
    "changeme",
    "replace-with-a-long-local-secret",
}


class AuthConfigError(RuntimeError):
    """A required auth setting is missing or unusable."""


class TokenError(Exception):
    """The bearer token cannot be trusted."""


def load_local_env() -> None:
    """Read services/api/.env. Variables already set in the process win."""
    from app.config import API_DIR

    env_path = API_DIR / ".env"
    if not env_path.is_file():
        return
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            os.environ.setdefault(key, value)


def jwt_secret() -> str:
    secret = os.environ.get("JWT_SECRET", "").strip()
    if secret in PLACEHOLDER_SECRETS or len(secret) < 16:
        raise AuthConfigError(
            "JWT_SECRET no está definido o es demasiado corto. "
            "Créalo en services/api/.env; el código no trae un secreto propio."
        )
    return secret


def expire_minutes() -> int:
    raw = os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "").strip()
    if not raw:
        raise AuthConfigError(
            "ACCESS_TOKEN_EXPIRE_MINUTES no está definido. "
            "Añádelo en services/api/.env."
        )
    try:
        return int(raw)
    except ValueError as exc:
        raise AuthConfigError("ACCESS_TOKEN_EXPIRE_MINUTES tiene que ser un entero.") from exc


def bcrypt_rounds() -> int:
    raw = os.environ.get("AUTH_BCRYPT_ROUNDS", "12").strip() or "12"
    try:
        rounds = int(raw)
    except ValueError as exc:
        raise AuthConfigError("AUTH_BCRYPT_ROUNDS tiene que ser un entero.") from exc
    if rounds < 4 or rounds > 20:
        raise AuthConfigError("AUTH_BCRYPT_ROUNDS tiene que estar entre 4 y 20.")
    return rounds


def hash_password(password: str) -> str:
    return bcrypt.using(rounds=bcrypt_rounds()).hash(password)


def verify_password(password: str, hashed: str) -> bool:
    try:
        return bool(bcrypt.verify(password, hashed))
    except (ValueError, TypeError):
        return False


def create_access_token(user_id: str) -> str:
    """Sign a token whose subject is the TinyDB user id (also `user_uuid`)."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "user_uuid": user_id,
        "iat": int(now.timestamp()),
        "exp": now + timedelta(minutes=expire_minutes()),
    }
    return jwt.encode(payload, jwt_secret(), algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, jwt_secret(), algorithms=[ALGORITHM])
    except JWTError as exc:
        raise TokenError("El token no es válido o ha caducado.") from exc
    if not isinstance(payload, dict):
        raise TokenError("El token no es válido o ha caducado.")
    subject = payload.get("sub")
    if not isinstance(subject, str) or not subject:
        raise TokenError("El token no identifica a un usuario.")
    user_uuid = payload.get("user_uuid")
    if user_uuid is not None and user_uuid != subject:
        raise TokenError("El token no identifica a un usuario.")
    return payload
