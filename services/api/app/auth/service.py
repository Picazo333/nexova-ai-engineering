"""User and profile services backed by TinyDB.

HTTP authorization lives with these functions so a router cannot update
another person's credentials without passing through the same checks.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from tinydb import Query

from app.auth.models import Role
from app.auth.security import hash_password, verify_password
from app.auth.store import auth_lock, profiles_table, users_table

USER_FIELDS = ("id", "email", "hashed_password", "is_active", "role", "created_at")
PROFILE_FIELDS = ("id", "user_id", "name", "phone", "address")
_DUMMY_HASH: str | None = None


class ServiceError(Exception):
    def __init__(self, status_code: int, message: str) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.message = message


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _new_id() -> str:
    return str(uuid.uuid4())


def _dummy_hash() -> str:
    global _DUMMY_HASH
    if _DUMMY_HASH is None:
        _DUMMY_HASH = hash_password("dummy-password-not-a-user")
    return _DUMMY_HASH


def public_user(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": record["id"],
        "email": record["email"],
        "is_active": bool(record["is_active"]),
        "role": record["role"],
        "created_at": record["created_at"],
    }


def public_profile(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": record["id"],
        "user_id": record["user_id"],
        "name": record.get("name"),
        "phone": record.get("phone"),
        "address": record.get("address"),
    }


def get_user_by_id(user_id: str) -> dict[str, Any] | None:
    with auth_lock():
        found = users_table().get(Query().id == user_id)
    if found is None:
        return None
    return dict(found)


def get_user_by_email(email: str) -> dict[str, Any] | None:
    with auth_lock():
        found = users_table().get(Query().email == email)
    if found is None:
        return None
    return dict(found)


def get_profile_by_user_id(user_id: str) -> dict[str, Any] | None:
    with auth_lock():
        found = profiles_table().get(Query().user_id == user_id)
    if found is None:
        return None
    return dict(found)


def list_users() -> list[dict[str, Any]]:
    with auth_lock():
        rows = users_table().all()
    public = [public_user(dict(row)) for row in rows]
    return sorted(public, key=lambda item: item["created_at"])


def create_user(
    *,
    email: str,
    password: str,
    name: str | None = None,
    phone: str | None = None,
    address: str | None = None,
    role: str = Role.user.value,
    is_active: bool = True,
) -> dict[str, Any]:
    """Create a user and the linked profile. Returns the stored user record."""
    if role not in {item.value for item in Role}:
        raise ServiceError(422, "El rol solo puede ser admin, manager o user.")
    with auth_lock():
        if users_table().get(Query().email == email) is not None:
            raise ServiceError(409, "Ya existe una cuenta con ese correo.")
        user = {
            "id": _new_id(),
            "email": email,
            "hashed_password": hash_password(password),
            "is_active": bool(is_active),
            "role": role,
            "created_at": _now(),
        }
        if set(user) != set(USER_FIELDS):
            raise RuntimeError("el documento User tiene campos que no son credenciales")
        profile = {
            "id": _new_id(),
            "user_id": user["id"],
            "name": name,
            "phone": phone,
            "address": address,
        }
        users_table().insert(user)
        profiles_table().insert(profile)
    return user


def update_user(user_id: str, changes: dict[str, Any]) -> dict[str, Any]:
    """Update credential fields. `changes` uses plaintext `password` if present."""
    with auth_lock():
        table = users_table()
        current = table.get(Query().id == user_id)
        if current is None:
            raise ServiceError(404, "No existe un usuario con ese id.")
        stored = dict(current)
        if "email" in changes and changes["email"] != stored["email"]:
            taken = table.get(Query().email == changes["email"])
            if taken is not None and taken["id"] != user_id:
                raise ServiceError(409, "Ya existe una cuenta con ese correo.")
            stored["email"] = changes["email"]
        if "password" in changes:
            stored["hashed_password"] = hash_password(changes["password"])
        if "role" in changes:
            role = changes["role"]
            stored["role"] = role.value if isinstance(role, Role) else role
        if "is_active" in changes:
            stored["is_active"] = bool(changes["is_active"])
        for field in ("name", "phone", "address", "password"):
            stored.pop(field, None)
        password_changed = "password" in changes
        table.update(stored, Query().id == user_id)
    if password_changed:
        from app.auth.recovery import revoke_reset_tokens

        revoke_reset_tokens(user_id)
    updated = get_user_by_id(user_id)
    if updated is None:
        raise ServiceError(404, "No existe un usuario con ese id.")
    return updated


def delete_user(user_id: str) -> dict[str, Any]:
    """Delete the user and the linked profile. Returns the stored user."""
    with auth_lock():
        table = users_table()
        current = table.get(Query().id == user_id)
        if current is None:
            raise ServiceError(404, "No existe un usuario con ese id.")
        stored = dict(current)
        table.remove(Query().id == user_id)
        profiles_table().remove(Query().user_id == user_id)
    from app.auth.recovery import revoke_reset_tokens

    revoke_reset_tokens(user_id)
    return stored


def update_profile(user_id: str, changes: dict[str, Any]) -> dict[str, Any]:
    with auth_lock():
        table = profiles_table()
        current = table.get(Query().user_id == user_id)
        if current is None:
            raise ServiceError(404, "Este usuario no tiene perfil.")
        if current["user_id"] != user_id:
            raise ServiceError(403, "Solo puedes modificar tu propio perfil.")
        stored = dict(current)
        for key in ("name", "phone", "address"):
            if key in changes:
                stored[key] = changes[key]
        table.update(
            {"name": stored.get("name"), "phone": stored.get("phone"), "address": stored.get("address")},
            Query().user_id == user_id,
        )
        refreshed = table.get(Query().user_id == user_id)
    if refreshed is None:
        raise ServiceError(404, "Este usuario no tiene perfil.")
    return dict(refreshed)


def authenticate(email: str, password: str) -> dict[str, Any]:
    """Validate credentials. The error is the same for unknown and wrong passwords."""
    record = get_user_by_email(email)
    hashed = record["hashed_password"] if record else _dummy_hash()
    valid = verify_password(password, hashed)
    if record is None or not valid or not record.get("is_active", False):
        raise ServiceError(401, "El correo o la contraseña no son válidos.")
    return record


def assert_can_manage_user(actor: dict[str, Any], target_id: str) -> dict[str, Any]:
    target = get_user_by_id(target_id)
    if target is None:
        raise ServiceError(404, "No existe un usuario con ese id.")
    if actor["id"] != target["id"] and actor["role"] != Role.admin.value:
        raise ServiceError(403, "No puedes consultar ni modificar las credenciales de otro usuario.")
    return target


def assert_can_assign(actor: dict[str, Any], target: dict[str, Any], changes: dict[str, Any]) -> None:
    if "role" in changes and changes["role"] != target["role"] and actor["role"] != Role.admin.value:
        raise ServiceError(403, "Solo un admin puede cambiar el rol.")
    if "is_active" in changes and bool(changes["is_active"]) != bool(target["is_active"]):
        if actor["role"] != Role.admin.value:
            raise ServiceError(403, "Solo un admin puede activar o desactivar una cuenta.")
