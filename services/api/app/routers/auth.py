"""Login and the caller's identity. Stateless JWT, no session cookie."""

from __future__ import annotations

import json
import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import ValidationError

from app.auth.deps import get_current_user
from app.auth.models import (
    AuthMe,
    ChangePasswordBody,
    ForgotPasswordBody,
    LoginBody,
    MessageResponse,
    ResetPasswordBody,
    TokenResponse,
    validation_message,
)
from app.auth.recovery import (
    FORGOT_MESSAGE,
    RecoveryError,
    change_password,
    request_password_reset,
    reset_password,
)
from app.auth.security import AuthConfigError, create_access_token, expire_minutes
from app.auth.service import ServiceError, authenticate, get_profile_by_user_id, public_profile
from app.http_catalog import catalog_message

logger = logging.getLogger("nexova.api")

router = APIRouter(prefix="/auth", tags=["auth"])

LOGIN_OPENAPI = {
    "requestBody": {
        "required": True,
        "content": {
            "application/json": {
                "schema": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["email", "password"],
                    "properties": {
                        "email": {"type": "string", "example": "ana@nexova.test"},
                        "password": {"type": "string", "example": "clave-segura-1"},
                    },
                }
            },
            "application/x-www-form-urlencoded": {
                "schema": {
                    "type": "object",
                    "required": ["username", "password"],
                    "properties": {
                        "username": {
                            "type": "string",
                            "description": "Correo. Lo usa el botón Authorize de Swagger.",
                            "example": "ana@nexova.test",
                        },
                        "password": {"type": "string", "example": "clave-segura-1"},
                        "email": {"type": "string", "description": "Alternativa a username."},
                    },
                }
            },
        },
    }
}


def _fail(exc: ServiceError) -> HTTPException:
    headers = {"WWW-Authenticate": "Bearer"} if exc.status_code == 401 else None
    return HTTPException(status_code=exc.status_code, detail=exc.message, headers=headers)


async def _credentials(request: Request) -> LoginBody:
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        try:
            payload = await request.json()
        except (json.JSONDecodeError, UnicodeDecodeError, ValueError) as exc:
            raise HTTPException(status_code=422, detail="El cuerpo tiene que ser un objeto JSON.") from exc
        if not isinstance(payload, dict):
            raise HTTPException(status_code=422, detail="El cuerpo tiene que ser un objeto JSON.")
    else:
        form = await request.form()
        email = form.get("email") or form.get("username")
        password = form.get("password")
        payload = {"email": email, "password": password}
    try:
        return LoginBody.model_validate(payload)
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=validation_message(exc)) from exc


@router.post(
    "/login",
    summary="Paso 2 — Iniciar sesión",
    response_model=TokenResponse,
    openapi_extra=LOGIN_OPENAPI,
)
async def login(request: Request) -> dict:
    """Valida correo y contraseña y devuelve un JWT firmado."""
    body = await _credentials(request)
    try:
        record = authenticate(body.email, body.password)
    except ServiceError as exc:
        raise _fail(exc) from exc
    try:
        minutes = expire_minutes()
        token = create_access_token(record["id"])
    except AuthConfigError:
        logger.error("auth config unavailable during login")
        raise HTTPException(status_code=500, detail=catalog_message(500)) from None
    payload = {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": minutes * 60,
        "user_uuid": record["id"],
    }
    TokenResponse.model_validate(payload)
    return payload


@router.get("/me", summary="Paso 3 — Quién soy", response_model=AuthMe)
def who_am_i(actor: dict = Depends(get_current_user)) -> dict:
    profile = get_profile_by_user_id(actor["id"])
    if profile is None:
        raise HTTPException(status_code=404, detail="Este usuario no tiene perfil.")
    body = {
        "id": actor["id"],
        "email": actor["email"],
        "role": actor["role"],
        "profile": public_profile(profile),
    }
    AuthMe.model_validate(body)
    return body


def _client_ip(request: Request) -> str:
    if request.client is None:
        return ""
    host = request.client.host or ""
    cleaned = "".join(ch for ch in host if ch.isprintable())
    return cleaned[:64]


def _recovery_error(exc: RecoveryError) -> HTTPException:
    return HTTPException(
        status_code=exc.status,
        detail={
            "error": "unauthorized" if exc.status == 401 else "http_error",
            "message": exc.message,
            "detail": exc.message,
            "code": exc.code,
        },
    )


@router.post(
    "/forgot-password",
    summary="Pedir un enlace para restablecer la contraseña",
    response_model=MessageResponse,
)
def forgot_password(body: ForgotPasswordBody, request: Request) -> dict:
    """Siempre responde 200. No indica si el correo tiene cuenta."""
    request_password_reset(body.email, _client_ip(request))
    return {"message": FORGOT_MESSAGE}


@router.post(
    "/reset-password",
    summary="Elegir una contraseña con el enlace de un solo uso",
    response_model=MessageResponse,
)
def reset_password_route(body: ResetPasswordBody) -> dict:
    """Valida firma, caducidad y que el enlace no se haya usado."""
    try:
        reset_password(body.token, body.new_password)
    except RecoveryError as exc:
        raise _recovery_error(exc) from exc
    return {"message": "La contraseña se ha actualizado. Ya puedes entrar."}


@router.post(
    "/change-password",
    summary="Cambiar la contraseña de la sesión actual",
    response_model=MessageResponse,
)
def change_password_route(
    body: ChangePasswordBody,
    actor: dict = Depends(get_current_user),
) -> dict:
    """Comprueba la contraseña actual y guarda un hash nuevo."""
    try:
        change_password(actor["id"], body.current_password, body.new_password)
    except RecoveryError as exc:
        raise _recovery_error(exc) from exc
    return {"message": "La contraseña se ha actualizado."}
