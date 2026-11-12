# 014 V01 — un correo real por Resend

Enviado el 2026-11-12 15:51:17 CST (America/Mexico_City), con autorización literal de Miguel (12 nov 2026 15:46 CST) a `m***@gmail.com`. Exactamente un envío. No se reintentó.

- **Ruta de código:** `POST /auth/forgot-password` del router real `app.routers.auth` (TestClient de FastAPI) → `request_password_reset` (`app.auth.recovery`) → `mailer._resend_send` (`app.auth.mailer`). SHA de la app: `3b156de` (`origin/feature/user-authentication-restore`, PR #21).
- **Transporte:** `EMAIL_TRANSPORT=resend`. Remitente por defecto de la app: `Nexova <onboarding@resend.dev>`. `POST https://api.resend.com/emails`.
- **Base:** TinyDB local en un directorio temporal aislado (`AUTH_DATA_DIR`), con una cuenta activa registrada a esa dirección. El directorio se borró después. No se usó Supabase ni se modificó el worktree.
- **Resultado:** HTTP de la app 200 (mismo cuerpo anti-enumeración). HTTP de Resend 200. `resend_message_id`: `01a1d1be-6006-77ab-ad3c-26f86f632b58`. Una sola llamada HTTP a Resend.
- **Redacción:** no está la clave `RESEND_API_KEY` ni el token/enlace de restablecimiento. El destinatario aparece como `m***@gmail.com`. Detalle en `send-result.json`.
- Sin reintentos, sin merge, sin LMS, sin push.
