"""Pydantic models for the Nexova supplier directory.

Field names, categories, and statuses match the company briefing. `updated_at`
is not part of the input models: the service sets it when a rate is stored.
"""

from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, ValidationError, field_validator, model_validator


class SupplierStatus(str, Enum):
    active = "active"
    suspended = "suspended"


class SupplierCountry(str, Enum):
    spain = "Spain"
    usa = "USA"


class SupplierCurrency(str, Enum):
    eur = "EUR"
    usd = "USD"


class ProductCategory(str, Enum):
    job_boards = "job_boards"
    ats_software = "ats_software"
    assessment_tools = "assessment_tools"
    training_platforms = "training_platforms"
    payroll_and_hr_software = "payroll_and_hr_software"
    video_interview = "video_interview"
    background_check = "background_check"
    office_and_facilities = "office_and_facilities"
    it_and_software_licenses = "it_and_software_licenses"


VALID_CATEGORIES = [item.value for item in ProductCategory]
VALID_STATUSES = [item.value for item in SupplierStatus]
CURRENCY_BY_COUNTRY = {
    SupplierCountry.spain.value: SupplierCurrency.eur.value,
    SupplierCountry.usa.value: SupplierCurrency.usd.value,
}

FIELD_LABELS = {
    "name": "Nombre",
    "country": "País",
    "categories": "Categorías",
    "monthly_rate": "Tarifa mensual",
    "currency": "Moneda",
    "status": "Estado",
    "contract_renewal_date": "Fecha de renovación",
    "contact_email": "Correo de contacto",
    "notes": "Notas",
    "updated_at": "Actualización de tarifa",
}


def _positive_rate(value: Any) -> float:
    if isinstance(value, bool) or value is None:
        raise ValueError("La tarifa mensual tiene que ser un número mayor que cero.")
    if isinstance(value, str):
        text = value.strip()
        if not text:
            raise ValueError("La tarifa mensual tiene que ser un número mayor que cero.")
        try:
            value = float(text)
        except ValueError as exc:
            raise ValueError("La tarifa mensual tiene que ser un número mayor que cero.") from exc
    if not isinstance(value, (int, float)):
        raise ValueError("La tarifa mensual tiene que ser un número mayor que cero.")
    number = float(value)
    if number <= 0:
        raise ValueError("La tarifa mensual tiene que ser un número mayor que cero.")
    return number


def _one_of(value: Any, allowed: set[str], message: str) -> str:
    if isinstance(value, Enum):
        value = value.value
    if not isinstance(value, str) or value not in allowed:
        raise ValueError(message)
    return value


class SupplierCreate(BaseModel):
    """Payload accepted from a client. It has no id and no updated_at."""

    model_config = ConfigDict(extra="forbid")

    name: str
    country: SupplierCountry
    categories: list[ProductCategory]
    monthly_rate: float
    currency: SupplierCurrency
    status: SupplierStatus
    contract_renewal_date: date | None = None
    contact_email: str | None = None
    notes: str | None = None

    @field_validator("name")
    @classmethod
    def name_required(cls, value: str) -> str:
        text = value.strip()
        if not text:
            raise ValueError("El nombre es obligatorio.")
        return text

    @field_validator("country", mode="before")
    @classmethod
    def country_allowed(cls, value: Any) -> Any:
        return _one_of(
            value,
            {item.value for item in SupplierCountry},
            "El país del contrato solo puede ser Spain o USA.",
        )

    @field_validator("currency", mode="before")
    @classmethod
    def currency_allowed(cls, value: Any) -> Any:
        return _one_of(
            value,
            {item.value for item in SupplierCurrency},
            "La moneda solo puede ser EUR o USD.",
        )

    @field_validator("status", mode="before")
    @classmethod
    def status_allowed(cls, value: Any) -> Any:
        return _one_of(
            value,
            {item.value for item in SupplierStatus},
            "El estado solo puede ser active o suspended.",
        )

    @field_validator("categories", mode="before")
    @classmethod
    def categories_allowed(cls, value: Any) -> list[str]:
        if isinstance(value, str):
            value = [value]
        if not isinstance(value, list):
            raise ValueError("Elige al menos una categoría.")
        allowed = {item.value for item in ProductCategory}
        cleaned: list[str] = []
        for item in value:
            raw = item.value if isinstance(item, Enum) else item
            if not isinstance(raw, str) or raw not in allowed:
                raise ValueError("Hay una categoría que no está en el directorio de Nexova.")
            if raw not in cleaned:
                cleaned.append(raw)
        if not cleaned:
            raise ValueError("Elige al menos una categoría.")
        return cleaned

    @field_validator("monthly_rate", mode="before")
    @classmethod
    def rate_positive(cls, value: Any) -> float:
        return _positive_rate(value)

    @field_validator("contract_renewal_date", mode="before")
    @classmethod
    def empty_date(cls, value: Any) -> Any:
        if value is None or value == "":
            return None
        if isinstance(value, str):
            text = value.strip()
            if not text:
                return None
            return text
        return value

    @field_validator("contact_email", mode="before")
    @classmethod
    def email_format(cls, value: Any) -> str | None:
        if value is None:
            return None
        if not isinstance(value, str):
            raise ValueError("El correo de contacto no tiene un formato válido.")
        text = value.strip()
        if not text:
            return None
        if " " in text or text.count("@") != 1:
            raise ValueError("El correo de contacto no tiene un formato válido.")
        local, domain = text.split("@")
        if not local or "." not in domain or domain.startswith(".") or domain.endswith("."):
            raise ValueError("El correo de contacto no tiene un formato válido.")
        return text

    @field_validator("notes", mode="before")
    @classmethod
    def empty_notes(cls, value: Any) -> str | None:
        if value is None:
            return None
        if not isinstance(value, str):
            raise ValueError("Las notas tienen que ser texto.")
        text = value.strip()
        return text or None

    @model_validator(mode="after")
    def currency_matches_country(self) -> SupplierCreate:
        expected = CURRENCY_BY_COUNTRY[self.country.value]
        if self.currency.value != expected:
            raise ValueError(f"Un proveedor de {self.country.value} tiene que usar {expected}.")
        return self


class RateUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    monthly_rate: float

    @field_validator("monthly_rate", mode="before")
    @classmethod
    def rate_positive(cls, value: Any) -> float:
        return _positive_rate(value)


class StatusUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: SupplierStatus

    @field_validator("status", mode="before")
    @classmethod
    def status_allowed(cls, value: Any) -> Any:
        return _one_of(
            value,
            {item.value for item in SupplierStatus},
            "El estado solo puede ser active o suspended.",
        )


class SupplierQuery(BaseModel):
    model_config = ConfigDict(extra="forbid")

    country: SupplierCountry | None = None
    category: ProductCategory | None = None
    status: SupplierStatus | None = None

    @field_validator("country", mode="before")
    @classmethod
    def country_allowed(cls, value: Any) -> Any:
        if value is None or value == "":
            return None
        return _one_of(
            value,
            {item.value for item in SupplierCountry},
            "El país del contrato solo puede ser Spain o USA.",
        )

    @field_validator("category", mode="before")
    @classmethod
    def category_allowed(cls, value: Any) -> Any:
        if value is None or value == "":
            return None
        return _one_of(
            value,
            {item.value for item in ProductCategory},
            "Esa categoría no está en el directorio de Nexova.",
        )

    @field_validator("status", mode="before")
    @classmethod
    def status_allowed(cls, value: Any) -> Any:
        if value is None or value == "":
            return None
        return _one_of(
            value,
            {item.value for item in SupplierStatus},
            "El estado solo puede ser active o suspended.",
        )


class SupplierPublic(BaseModel):
    """Supplier returned by the API, including the TinyDB id and updated_at."""

    model_config = ConfigDict(extra="forbid")

    id: int
    name: str
    country: SupplierCountry
    categories: list[ProductCategory]
    monthly_rate: float
    currency: SupplierCurrency
    updated_at: datetime
    status: SupplierStatus
    contract_renewal_date: date | None = None
    contact_email: str | None = None
    notes: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return self.model_dump(mode="json")


def validation_message(exc: ValidationError) -> str:
    parts: list[str] = []
    for err in exc.errors():
        loc = [str(item) for item in err.get("loc", ()) if item != "body"]
        msg = str(err.get("msg", "Dato no válido."))
        prefix = "Value error, "
        if msg.startswith(prefix):
            msg = msg[len(prefix) :]
        if loc:
            label = FIELD_LABELS.get(loc[0], loc[0])
            parts.append(f"{label}: {msg}")
        else:
            parts.append(msg)
    return " ".join(parts) or "La entrada no es válida."
