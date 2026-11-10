"""HTTP status to a human sentence.

Routers keep their own 4xx copy (a duplicate email, an empty password, an
empty update). This module is the fallback, and it is what a 5xx is allowed
to say. Nothing here copies a traceback, a filesystem path, or a secret.
"""

from __future__ import annotations

import re

CATALOG: dict[int, str] = {
    400: "La solicitud no se puede procesar. Revisa los datos e inténtalo de nuevo.",
    401: "Falta un token válido.",
    403: "No tienes permiso para ese recurso.",
    404: "No encontrado.",
    405: "Ese método no está admitido en esta ruta.",
    409: "Esa operación entra en conflicto con un dato que ya existe.",
    413: "El fichero supera el tamaño permitido.",
    422: "Hay datos que no se pueden aceptar. Revisa el formulario.",
    500: "No se pudo completar la operación. Inténtalo de nuevo.",
}

GENERIC = "No se pudo completar la solicitud."

# Starlette writes these English strings. They are not a decision of this API.
FRAMEWORK_DETAIL = {
    "Not Found",
    "Method Not Allowed",
    "Not authenticated",
    "Unauthorized",
    "Forbidden",
}

_LEAK = re.compile(
    r"traceback|file \"|jwt_secret|hashed_password|"
    r"sqlite://|postgres(?:ql)?://|mongodb(?:\+srv)?://|mysql://|"
    r"unexpected token|syntaxerror|\.env\b|/workspace/|"
    r"secret-sentinel|bearer [a-z0-9._\-]{12,}",
    re.IGNORECASE,
)


def catalog_message(status: int) -> str:
    if status >= 500:
        return CATALOG[500]
    return CATALOG.get(status, GENERIC)


def safe_detail(status: int, detail: str) -> str | None:
    """A router sentence the client may read, or None when it must be replaced."""
    if status >= 500:
        return None
    text = detail.strip()
    if not text or text in FRAMEWORK_DETAIL or len(text) > 400:
        return None
    if _LEAK.search(text):
        return None
    return text


_PYDANTIC_ENGLISH = {
    "Field required": "Falta un dato obligatorio.",
    "Extra inputs are not permitted": "Hay un campo que no se acepta.",
    "Input should be a valid string": "El dato tiene que ser texto.",
    "Input should be a valid integer": "El dato tiene que ser un número entero.",
    "Input should be a valid number": "El dato tiene que ser un número.",
    "Input should be a valid list": "El dato tiene que ser una lista.",
}


def message_from_validation(errors: object) -> str:
    """Spanish sentences from a validation error, without the submitted input."""
    if not isinstance(errors, list):
        return catalog_message(422)
    parts: list[str] = []
    for item in errors:
        if not isinstance(item, dict):
            continue
        raw = item.get("msg", "Dato no válido.")
        text = str(raw)
        prefix = "Value error, "
        if text.startswith(prefix):
            text = text[len(prefix) :]
        text = text.strip()
        text = _PYDANTIC_ENGLISH.get(text, text)
        if not text or _LEAK.search(text):
            text = "Dato no válido."
        parts.append(text)
    return " ".join(parts) or catalog_message(422)


def public_body(status: int, detail: object) -> dict:
    """JSON body for an HTTPException. A 5xx never repeats ``detail``."""
    if status >= 500 or not _detail_is_public(status, detail):
        code = "http_error"
        return {"error": code, "message": catalog_message(status)}
    if isinstance(detail, dict):
        return _public_dict(status, detail)
    assert isinstance(detail, str)
    kept = safe_detail(status, detail)
    assert kept is not None
    if status == 401:
        code = "unauthorized"
    elif status == 403:
        code = "forbidden"
    else:
        code = "http_error"
    return {"error": code, "message": kept, "detail": kept}


def _detail_is_public(status: int, detail: object) -> bool:
    if isinstance(detail, str):
        return safe_detail(status, detail) is not None
    if isinstance(detail, dict):
        message = detail.get("message")
        if isinstance(message, str) and safe_detail(status, message) is None:
            return False
        extra = detail.get("detail")
        if isinstance(extra, str) and safe_detail(status, extra) is None:
            return False
        return True
    return False


def _public_dict(status: int, detail: dict) -> dict:
    cloned = dict(detail)
    message = cloned.get("message")
    if isinstance(message, str):
        kept = safe_detail(status, message)
        cloned["message"] = kept if kept is not None else catalog_message(status)
    extra = cloned.get("detail")
    if isinstance(extra, str):
        kept = safe_detail(status, extra)
        cloned["detail"] = kept if kept is not None else cloned.get("message", catalog_message(status))
    return cloned
