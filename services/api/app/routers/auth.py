"""Login and the caller's identity. Stateless JWT, no session cookie."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import ValidationError

from app.auth.deps import get_current_user
from app.auth.models import AuthMe, LoginBody, TokenResponse, validation_message
from app.auth.security import AuthConfigError, create_access_token, expire_minutes
from app.auth.service import ServiceError, authenticate, get_profile_by_user_id, public_profile

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
        except Exception as exc:
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
        minutes = expire_minutes()
        token = create_access_token(record["id"])
    except ServiceError as exc:
        raise _fail(exc) from exc
    except AuthConfigError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
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
