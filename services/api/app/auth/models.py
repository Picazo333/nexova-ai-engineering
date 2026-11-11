"""Request and response models for credentials and profiles.

`User` stores credentials only. Display name and contact data belong to `Profile`.
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, ValidationError, field_validator


class Role(str, Enum):
    admin = "admin"
    manager = "manager"
    user = "user"


ROLE_MESSAGE = "El rol solo puede ser admin, manager o user."


def normalize_email(value: Any) -> str:
    if not isinstance(value, str):
        raise ValueError("El correo no tiene un formato válido.")
    text = value.strip().lower()
    if " " in text or text.count("@") != 1:
        raise ValueError("El correo no tiene un formato válido.")
    local, domain = text.split("@")
    if not local or "." not in domain or domain.startswith(".") or domain.endswith("."):
        raise ValueError("El correo no tiene un formato válido.")
    return text


def require_password(value: Any) -> str:
    if not isinstance(value, str) or value != value.strip() or len(value) < 8:
        raise ValueError("La contraseña tiene que tener al menos 8 caracteres, sin espacios al borde.")
    if len(value.encode("utf-8")) > 72:
        raise ValueError("La contraseña no puede superar 72 bytes.")
    return value


def optional_text(value: Any, *, limit: int, label: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"{label} tiene que ser texto.")
    text = value.strip()
    if not text:
        return None
    if len(text) > limit:
        raise ValueError(f"{label} supera los {limit} caracteres.")
    return text


class UserCreate(BaseModel):
    """Public registration. Role is not accepted: the service stores `user`."""

    model_config = ConfigDict(extra="forbid")

    email: str
    password: str
    name: str | None = None
    phone: str | None = None
    address: str | None = None

    @field_validator("email", mode="before")
    @classmethod
    def email_ok(cls, value: Any) -> str:
        return normalize_email(value)

    @field_validator("password", mode="before")
    @classmethod
    def password_ok(cls, value: Any) -> str:
        return require_password(value)

    @field_validator("name", mode="before")
    @classmethod
    def name_ok(cls, value: Any) -> str | None:
        return optional_text(value, limit=200, label="El nombre")

    @field_validator("phone", mode="before")
    @classmethod
    def phone_ok(cls, value: Any) -> str | None:
        return optional_text(value, limit=40, label="El teléfono")

    @field_validator("address", mode="before")
    @classmethod
    def address_ok(cls, value: Any) -> str | None:
        return optional_text(value, limit=400, label="La dirección")


class UserUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: str | None = None
    password: str | None = None
    role: Role | None = None
    is_active: bool | None = None

    @field_validator("email", mode="before")
    @classmethod
    def email_ok(cls, value: Any) -> str | None:
        if value is None:
            return None
        return normalize_email(value)

    @field_validator("password", mode="before")
    @classmethod
    def password_ok(cls, value: Any) -> str | None:
        if value is None:
            return None
        return require_password(value)

    @field_validator("role", mode="before")
    @classmethod
    def role_ok(cls, value: Any) -> Any:
        if value is None:
            return None
        if isinstance(value, Role):
            return value
        if not isinstance(value, str) or value not in {item.value for item in Role}:
            raise ValueError(ROLE_MESSAGE)
        return value


class ProfileUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = None
    phone: str | None = None
    address: str | None = None

    @field_validator("name", mode="before")
    @classmethod
    def name_ok(cls, value: Any) -> str | None:
        return optional_text(value, limit=200, label="El nombre")

    @field_validator("phone", mode="before")
    @classmethod
    def phone_ok(cls, value: Any) -> str | None:
        return optional_text(value, limit=40, label="El teléfono")

    @field_validator("address", mode="before")
    @classmethod
    def address_ok(cls, value: Any) -> str | None:
        return optional_text(value, limit=400, label="La dirección")


class LoginBody(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: str
    password: str

    @field_validator("email", mode="before")
    @classmethod
    def email_ok(cls, value: Any) -> str:
        return normalize_email(value)

    @field_validator("password", mode="before")
    @classmethod
    def password_present(cls, value: Any) -> str:
        if not isinstance(value, str) or not value:
            raise ValueError("La contraseña es obligatoria.")
        return value


class ProfilePublic(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    user_id: str
    name: str | None = None
    phone: str | None = None
    address: str | None = None


class UserPublic(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    email: str
    is_active: bool
    role: Role
    created_at: str


class UserWithProfile(UserPublic):
    profile: ProfilePublic


class AuthMe(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    email: str
    role: Role
    profile: ProfilePublic


class TokenResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    access_token: str
    token_type: str
    expires_in: int
    user_uuid: str


def validation_message(exc: ValidationError) -> str:
    parts: list[str] = []
    for err in exc.errors():
        msg = str(err.get("msg", "Dato no válido."))
        prefix = "Value error, "
        if msg.startswith(prefix):
            msg = msg[len(prefix) :]
        parts.append(msg)
    return " ".join(parts) or "La entrada no es válida."
