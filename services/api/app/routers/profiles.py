"""The authenticated user's profile. There is no route to edit someone else's."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.auth.deps import get_current_user
from app.auth.models import ProfilePublic, ProfileUpdate
from app.auth.service import ServiceError, get_profile_by_user_id, public_profile, update_profile

router = APIRouter(prefix="/profiles", tags=["profiles"])


def _own(user_id: str) -> dict:
    record = get_profile_by_user_id(user_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Este usuario no tiene perfil.")
    if record["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Solo puedes consultar tu propio perfil.")
    body = public_profile(record)
    ProfilePublic.model_validate(body)
    return body


@router.get("/me", summary="Paso 3 — Ver mi perfil")
def read_my_profile(actor: dict = Depends(get_current_user)) -> dict:
    return _own(actor["id"])


@router.put("/me", summary="Paso 3 — Actualizar mi perfil")
def put_my_profile(payload: ProfileUpdate, actor: dict = Depends(get_current_user)) -> dict:
    changes = payload.model_dump(exclude_unset=True)
    if not changes:
        raise HTTPException(status_code=422, detail="No hay cambios.")
    try:
        updated = update_profile(actor["id"], changes)
    except ServiceError as exc:
        headers = {"WWW-Authenticate": "Bearer"} if exc.status_code == 401 else None
        raise HTTPException(status_code=exc.status_code, detail=exc.message, headers=headers) from exc
    if updated["user_id"] != actor["id"]:
        raise HTTPException(status_code=403, detail="Solo puedes modificar tu propio perfil.")
    body = public_profile(updated)
    ProfilePublic.model_validate(body)
    return body
