"""FastAPI dependencies that turn a bearer token into the current user."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from app.auth.security import AuthConfigError, TokenError, decode_access_token
from app.auth.service import get_user_by_id, public_user

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)

BEARER = {"WWW-Authenticate": "Bearer"}


def unauthorized(message: str) -> HTTPException:
    return HTTPException(status_code=401, detail=message, headers=BEARER)


def get_current_user(token: Annotated[str | None, Depends(oauth2_scheme)]) -> dict:
    """Decode the bearer token and load the TinyDB user it points at."""
    if not token:
        raise unauthorized("Falta el token de acceso.")
    try:
        payload = decode_access_token(token)
    except AuthConfigError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except TokenError as exc:
        raise unauthorized(str(exc)) from exc
    record = get_user_by_id(str(payload["sub"]))
    if record is None or not record.get("is_active", False):
        raise unauthorized("El token no es válido o ha caducado.")
    return public_user(record)


def get_optional_user(token: Annotated[str | None, Depends(oauth2_scheme)]) -> dict | None:
    """Return the user when the page request carries a valid token, else None."""
    if not token:
        return None
    try:
        return get_current_user(token)
    except HTTPException:
        return None
