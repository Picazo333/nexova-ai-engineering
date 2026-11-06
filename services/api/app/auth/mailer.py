"""Transactional email for the password reset link.

Resend is the provider this delivery uses. SendGrid is the other provider the
brief allows and is selected with EMAIL_TRANSPORT=sendgrid. Both read the API
key from the environment on the server. EMAIL_TRANSPORT=mock keeps the message
in memory for tests and does not open a connection.

Nothing in this module prints the key or the reset token.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from html import escape
from pathlib import Path

import httpx

logger = logging.getLogger("nexova.api")

RESEND_URL = "https://api.resend.com/emails"
SENDGRID_URL = "https://api.sendgrid.com/v3/mail/send"
DEFAULT_FROM = "Nexova <onboarding@resend.dev>"
PLACEHOLDER_KEYS = {"", "change-me", "changeme", "replace-me"}

_outbox: list[dict[str, str]] = []


class MailerError(Exception):
    """The message was not handed to a transport."""


class MailerNotConfigured(MailerError):
    """The selected provider has no API key in the environment."""


class MailerDeliveryError(MailerError):
    """The provider rejected the message. The status is not a secret."""

    def __init__(self, status_code: int) -> None:
        super().__init__(f"email provider status {status_code}")
        self.status_code = status_code


@dataclass(frozen=True)
class EmailMessage:
    to: str
    subject: str
    text: str
    html: str


def transport_name() -> str:
    raw = os.environ.get("EMAIL_TRANSPORT", "").strip().lower()
    if raw in {"", "resend"}:
        return "resend"
    if raw == "sendgrid":
        return "sendgrid"
    if raw == "mock":
        return "mock"
    raise MailerNotConfigured("EMAIL_TRANSPORT")


def _key(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if value in PLACEHOLDER_KEYS:
        return ""
    return value


def mailer_ready() -> bool:
    """True when a send can be attempted without inventing a credential."""
    try:
        mode = transport_name()
    except MailerNotConfigured:
        return False
    if mode == "mock":
        return True
    if mode == "resend":
        return bool(_key("RESEND_API_KEY"))
    return bool(_key("SENDGRID_API_KEY"))


def from_header() -> str:
    raw = os.environ.get("EMAIL_FROM", "").strip()
    return raw or DEFAULT_FROM


def parse_from(raw: str) -> tuple[str, str]:
    text = raw.strip()
    if text.endswith(">") and "<" in text:
        name, _, rest = text.partition("<")
        email = rest[:-1].strip()
        label = name.strip() or "Nexova"
        return email, label
    return text, "Nexova"


def render_reset_message(link: str, minutes: int) -> tuple[str, str, str]:
    """Plain text and a single-column HTML body. The link is the only URL."""
    subject = "Restablece tu contraseña de Nexova"
    text = (
        "Alguien pidió restablecer la contraseña de esta cuenta de Nexova.\n\n"
        f"El enlace caduca en {minutes} minutos y solo se puede usar una vez:\n"
        f"{link}\n\n"
        "Si no fuiste tú, ignora este mensaje. La contraseña no cambia hasta que se use el enlace.\n"
    )
    safe = escape(link, quote=True)
    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(subject)}</title>
</head>
<body style="margin:0;padding:0;background:#F7F8FA;color:#18202B;font-family:Arial,Helvetica,sans-serif;font-size:16px;line-height:24px;">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#F7F8FA;">
    <tr>
      <td align="center" style="padding:24px 16px;">
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="max-width:480px;background:#FFFFFF;border:1px solid #788598;border-radius:8px;">
          <tr>
            <td style="padding:24px;">
              <h1 style="margin:0 0 12px;font-size:24px;line-height:30px;font-weight:700;">Restablece tu contraseña</h1>
              <p style="margin:0 0 16px;">Alguien pidió restablecer la contraseña de esta cuenta de Nexova. El enlace caduca en {minutes} minutos y solo se puede usar una vez.</p>
              <p style="margin:0 0 16px;">
                <a href="{safe}" style="display:inline-block;background:#B53A17;color:#FFFFFF;text-decoration:none;font-weight:700;padding:12px 16px;border-radius:8px;">Elegir una contraseña nueva</a>
              </p>
              <p style="margin:0 0 16px;word-break:break-all;">Si el botón no abre, copia este enlace:<br><a href="{safe}">{safe}</a></p>
              <p style="margin:0;color:#505E70;">Si no fuiste tú, ignora este mensaje. La contraseña no cambia hasta que se use el enlace.</p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""
    return subject, text, html


def clear_mock_outbox() -> None:
    _outbox.clear()


def mock_outbox() -> list[dict[str, str]]:
    return [dict(item) for item in _outbox]


def _capture_mock_link(link: str) -> None:
    """Write the link only for the mock transport, and only when asked."""
    raw = os.environ.get("PASSWORD_RESET_CAPTURE_FILE", "").strip()
    if not raw:
        return
    target = Path(raw)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(link + "\n", encoding="utf-8")
    os.chmod(target, 0o600)


def _mock_send(message: EmailMessage) -> None:
    _outbox.append(
        {
            "to": message.to,
            "subject": message.subject,
            "text": message.text,
            "html": message.html,
        }
    )
    for line in message.text.splitlines():
        if "/reset-password?token=" in line:
            _capture_mock_link(line.strip())
            break


def _resend_send(message: EmailMessage) -> None:
    key = _key("RESEND_API_KEY")
    if not key:
        raise MailerNotConfigured("RESEND_API_KEY")
    response = httpx.post(
        RESEND_URL,
        headers={
            "Authorization": f"Bearer {key}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        json={
            "from": from_header(),
            "to": [message.to],
            "subject": message.subject,
            "text": message.text,
            "html": message.html,
        },
        timeout=10.0,
    )
    if response.status_code >= 400:
        logger.error("resend rejected a message status=%s", response.status_code)
        raise MailerDeliveryError(response.status_code)


def _sendgrid_send(message: EmailMessage) -> None:
    key = _key("SENDGRID_API_KEY")
    if not key:
        raise MailerNotConfigured("SENDGRID_API_KEY")
    email, name = parse_from(from_header())
    response = httpx.post(
        SENDGRID_URL,
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
        json={
            "personalizations": [{"to": [{"email": message.to}]}],
            "from": {"email": email, "name": name},
            "subject": message.subject,
            "content": [
                {"type": "text/plain", "value": message.text},
                {"type": "text/html", "value": message.html},
            ],
        },
        timeout=10.0,
    )
    if response.status_code >= 400:
        logger.error("sendgrid rejected a message status=%s", response.status_code)
        raise MailerDeliveryError(response.status_code)


def deliver(message: EmailMessage) -> None:
    mode = transport_name()
    if mode == "mock":
        _mock_send(message)
        return
    if mode == "resend":
        _resend_send(message)
        return
    _sendgrid_send(message)
