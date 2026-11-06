# Auditoría final — 014 ai-eng-user-authentication-restore

Estado: **PENDIENTE_REVISION_ORQUESTADOR**. No es READY_TO_SUBMIT. No hubo merge.

## Resultado

22/22 criterios que cuentan: PASS.

No cuentan y quedan pendientes:

| ID | Estado | Qué falta |
| --- | --- | --- |
| V01 | BLOCKED_HITL | Un correo real de Resend o SendGrid. El mock no vale como PASS. |
| D01 | HITL_ENVIO_MIGUEL | Entrega al instructor o al LMS. |
| D02 | HITL_MIGUEL | Merge a `main` cuando el PR esté aprobado. |
| H01 | HITL_MIGUEL | Crear la cuenta del proveedor y definir `RESEND_API_KEY` (o `SENDGRID_API_KEY` si se cambia el transporte). |
| U09 | NO_APLICA | SEO de landing pública. El portal es interno. |

Extras X01 y X02: PASS. Están en `quality/EXCELLENCE_REVIEW.md`.

## Checklist de Miguel

1. Revisar el PR contra `feature/langgraph-external-tools`. No merge automático.
2. Si el envío real debe demostrarse: crear la cuenta en Resend o SendGrid, poner la clave solo en el entorno del servidor, pedir un enlace a un buzón autorizado y guardar esa evidencia. Hasta entonces V01 sigue BLOCKED_HITL.
3. Entregar al instructor o al LMS, si toca. D01.
4. Merge a `main` solo después de aprobar. D02.

## Qué se volvió a ejecutar

- `services/api`: `uv run pytest` → 156 passed. La línea de partida de esta cadena era 138. Las 18 pruebas nuevas están en `tests/test_password_recovery.py`.
- Raíz: `uv run python -m pytest tests packages/incident_analysis/tests` → 57 passed, 1 skipped. El skip ya existía (generación en vivo bloqueada).
- Portal: `tsc --noEmit`, Jest 20 passed, Playwright 14 passed (las 10 anteriores y 4 de contraseña).
- Capturas y axe con el portal en producción y la API en `EMAIL_TRANSPORT=mock`.
- Lighthouse 18 corridas. `configSettings` comprobado.

## Límites

- No se envió ningún correo fuera de la máquina. No se creó cuenta de proveedor.
- El mock escribe el enlace en `PASSWORD_RESET_CAPTURE_FILE` solo si esa variable está puesta y el transporte es `mock`. Las pruebas del portal la usan en `/tmp`. No es un buzón.
- Con Resend de verdad, el tiempo de respuesta puede diferir entre un correo que existe y uno que no, porque la llamada solo se hace si hay cuenta activa. El cuerpo HTTP no cambia. Queda anotado en la revisión de excelencia.
- El JWT de sesión no se anula al cambiar la contraseña. Los enlaces de restablecimiento sí.

## Reparaciones de esta pasada

1. Dos enlaces pedidos en el mismo segundo salían iguales. Se añadió `jti`.
2. La captura de la carga cumplía la ruta dos veces y Playwright abortaba. La espera termina cuando el `fulfill` acaba.
3. El vídeo pedía ffmpeg de Playwright. Se instaló y la toma quedó en 5,52 s.
4. La captura del enlace caducado repetía el título en el párrafo. El párrafo usa la frase de la API.
