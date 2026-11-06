"""Credential CRUD under /users. Profile fields are accepted only on create."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

from app.auth.deps import get_current_user
from app.auth.models import UserCreate, UserUpdate, UserWithProfile
from app.auth.service import (
    ServiceError,
    assert_can_assign,
    assert_can_manage_user,
    create_user,
    delete_user,
    get_profile_by_user_id,
    list_users,
    public_profile,
    public_user,
    update_user,
)
router = APIRouter(prefix="/users", tags=["users"])


def _fail(exc: ServiceError) -> HTTPException:
    headers = {"WWW-Authenticate": "Bearer"} if exc.status_code == 401 else None
    return HTTPException(status_code=exc.status_code, detail=exc.message, headers=headers)


def _with_profile(record: dict) -> dict:
    profile = get_profile_by_user_id(record["id"])
    if profile is None:
        raise HTTPException(status_code=500, detail="El usuario no tiene perfil vinculado.")
    body = public_user(record)
    body["profile"] = public_profile(profile)
    UserWithProfile.model_validate(body)
    return body


@router.post("", status_code=201, summary="Paso 1 — Registrar usuario")
def register_user(payload: UserCreate) -> JSONResponse:
    """Crea la cuenta con rol `user` y el perfil en la misma operación."""
    try:
        record = create_user(
            email=payload.email,
            password=payload.password,
            name=payload.name,
            phone=payload.phone,
            address=payload.address,
        )
    except ServiceError as exc:
        raise _fail(exc) from exc
    return JSONResponse(status_code=201, content=_with_profile(record))


@router.get("", summary="Listar usuarios")
def read_users(_: dict = Depends(get_current_user)) -> list[dict]:
    return list_users()


@router.get("/{user_id}", summary="Paso 5 — Ver credenciales (403 si son de otro)")
def read_user(user_id: str, actor: dict = Depends(get_current_user)) -> dict:
    try:
        record = assert_can_manage_user(actor, user_id)
    except ServiceError as exc:
        raise _fail(exc) from exc
    return _with_profile(record)


@router.put("/{user_id}", summary="Paso 5 — Actualizar credenciales (403 si son de otro)")
def put_user(user_id: str, payload: UserUpdate, actor: dict = Depends(get_current_user)) -> dict:
    changes = payload.model_dump(exclude_unset=True)
    if "role" in changes and changes["role"] is not None:
        changes["role"] = changes["role"].value if hasattr(changes["role"], "value") else changes["role"]
    if not changes:
        raise HTTPException(status_code=422, detail="No hay cambios.")
    try:
        target = assert_can_manage_user(actor, user_id)
        assert_can_assign(actor, target, changes)
        updated = update_user(user_id, changes)
    except ServiceError as exc:
        raise _fail(exc) from exc
    return _with_profile(updated)


@router.delete("/{user_id}", summary="Eliminar usuario y su perfil")
def remove_user(user_id: str, actor: dict = Depends(get_current_user)) -> dict:
    try:
        assert_can_manage_user(actor, user_id)
        removed = delete_user(user_id)
    except ServiceError as exc:
        raise _fail(exc) from exc
    return public_user(removed)
