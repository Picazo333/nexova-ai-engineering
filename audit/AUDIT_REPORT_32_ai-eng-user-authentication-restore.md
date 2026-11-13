# Informe de auditoría adversaria — actividad 32

- **Auditor:** Rodrigo Salcedo (independiente; no es el autor)
- **Fecha:** 13 de noviembre de 2026, 10:52 CST (America/Mexico_City, UTC-6)
- **Slug:** `ai-eng-user-authentication-restore`
- **Tarea LMS:** 1022070 (GET 13 nov 2026: `task_status=PENDING`, `revision_status=PENDING`, `github_url` vacío)
- **Repo / PR:** [Picazo333/nexova-ai-engineering#21](https://github.com/Picazo333/nexova-ai-engineering/pull/21)
- **Rama:** `feature/user-authentication-restore`
- **Head auditado:** `639bc6fcb248b148785acd77946c911731fd9890` (13 nov 2026, 10:42:02 CST; solo documentación de ESTADO sobre el padre `07522b5`, que añade este checkpoint)
- **Fuente de criterios:** enunciado oficial `/workspace/ejecucion/014-ai-eng-user-authentication-restore/source/OFFICIAL_README.md` @ syllabus `fd2da034`, casillas L118–L129. No se usó la rúbrica ampliada del autor como fuente de verdad.
- **Alcance:** tests en entorno limpio, entradas inválidas, secretos e historial, adhesión literal, reproducibilidad según el README. Sin merge, sin comentarios en el PR, sin escrituras al LMS, sin créditos de pago (no se reenvió correo Resend).

## Veredicto

**PASA** (READY). 12/12 criterios oficiales PASS. 0 GRAVE. Solo GRAVE bloquea.

HITL abiertos, no restan: envío al LMS, merge, y no repetir el envío real de correo (evidencia ya existente; se evitó gastar créditos).

## Criterios oficiales (L118–L129)

| Línea | Criterio | Dictamen | Evidencia de esta pasada |
|---|---|---|---|
| L118 | `POST /auth/forgot-password` envía un correo real con el enlace a una dirección registrada. | **PASS** (no se relanzó en vivo) | Código: `app/auth/mailer.py` `_resend_send`, clave solo de `RESEND_API_KEY`. Evidencia `evidence/resend-live/send-result.json`: 12 nov 2026 15:51 CST, `transport=resend`, HTTP app 200, HTTP Resend 200, `resend_calls=1`, `resend_message_id` presente, sin clave ni cuerpo del enlace. |
| L119 | El mismo endpoint responde 200 aunque la dirección no esté registrada; no filtra información. | **PASS** | `uv run pytest tests/test_password_recovery.py`: 28 passed. `test_unknown_and_known_emails_share_the_same_200_body`. Extra adversarial: mismos cuerpos, sin «not found» / token en la respuesta HTTP. |
| L120 | El token caduca y no sirve después. | **PASS** | Tests de fila caducada y de firma caducada en `test_password_recovery.py`. Persistencia: hash SHA-256 del token, `used_at`, `expires_at` (`app/auth/recovery.py`). |
| L121 | `POST /auth/reset-password` actualiza la contraseña e invalida el token. | **PASS** | `test_reset_updates_the_password_and_a_replay_does_not`. Login con la anterior falla; el replay es 400. |
| L122 | Ese endpoint responde 400 ante token caducado o ya usado. | **PASS** | Mismos tests; también token de acceso, token manipulado y desconocido → 400 `code=invalid`. |
| L123 | `/forgot-password` muestra confirmación tras enviar, con independencia del resultado. | **PASS** | `ForgotPasswordScreen.tsx`: mensaje «Si esa dirección está registrada, recibirás un enlace en breve.» (equivalente oficial en español). `fieldset disabled={done || pending}`. |
| L124 | `/reset-password` lee el `token` de la query, envía y redirige a `/login` si va bien. | **PASS** | `app/reset-password/page.tsx` lee `searchParams.token`. `ResetPasswordScreen.tsx` hace `router.push("/login?notice=password-updated")`. |
| L125 | Ante token inválido o caducado, error claro y enlace a `/forgot-password`. | **PASS** | Textos «El enlace ha caducado» / «ya se usó» / «no es válido»; enlaces «Pedir un enlace» / «Pedir otro enlace» a `/forgot-password`. |
| L126 | En `/login` hay un enlace visible «Forgot your password?». | **PASS** | `LoginScreen.tsx` L150: «¿Olvidaste tu contraseña?» → `/forgot-password`. |
| L127 | `/account/change-password` valida que coincidan, llama a la API y da feedback. | **PASS** | `ChangePasswordScreen.tsx` usa `passwordConfirmError` antes de llamar; muestra éxito o error. |
| L128 | `POST /auth/change-password` rechaza la contraseña actual incorrecta con 400. | **PASS** | `test_change_password_rejects_a_wrong_current_password_and_keeps_the_old_one`. Sin Authorization: 401. |
| L129 | Ninguna API key va en el código; todo sale de variables de entorno. | **PASS** | Escaneo del árbol y de la API de GitHub (`path=.env`: 0 commits). `.env.example` deja `RESEND_API_KEY` y `SENDGRID_API_KEY` vacías. Fixtures de tests (`test-jwt-secret-local-only`) no son credenciales vivas. |

## Pruebas corridas (esta pasada)

Desde un worktree limpio en `/tmp/r032`, `UV_PROJECT_ENVIRONMENT=/tmp/venv-r032`, `cd services/api && uv sync --group dev`:

- `uv run pytest tests/test_password_recovery.py tests/test_auth.py`: **28 passed** en 1,79 s.
- `uv run pytest` (batería completa de `services/api`): **156 passed** en 7,10 s.
- `cd uis/portal && npm install && npx jest --coverage`: **20 passed**, 5 suites, cobertura 100 % de los módulos medidos.
- Casos adversarial extras (vacíos, tipos incorrectos, Unicode, inyección en el correo, token basura, cambio sin sesión, replay, el HTTP no devuelve el token): **25 passed**. Dos fallos fueron del arnés del auditor (se pasó el dict de `login()` en lugar de `token_for()`); los tests oficiales equivalentes ya cubren esos casos en verde. El fichero temporal se eliminó; no se commitea.

No se ejecutó Playwright en esta pasada (no era casilla oficial). Hay suite `e2e/password.spec.ts` y capturas en `evidence/`.

## Seguridad y secretos

Sin `.env` en el índice ni en el historial público (API GitHub: 0 commits). Sin claves de Resend/SendGrid, JWT reales ni URI con contraseña en el árbol. El mailer solo lee el entorno. Los tokens de reset se guardan hasheados y se invalidan al usarse, al emitir uno nuevo y al cambiar la contraseña con sesión. Sin créditos de pago gastados.

## Hallazgos

Véase la tabla del checkpoint. GRAVE 0, MENOR 1 (base distinta de `main`, cola serial), IRRELEVANTE 1 (CI `rag-tests` heredado).

## Reproducibilidad

El README de la API (`cd services/api && uv sync --group dev && uv run pytest`) se siguió al pie de la letra y terminó en verde. El envío real de correo exige `RESEND_API_KEY` de Miguel: HITL, no FAIL.
