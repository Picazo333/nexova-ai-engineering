# Rúbrica — 027 almacenamiento de telemetría

Required = sí cuenta para el cierre. HITL no resta. Un mock no es PASS de una integración real. Postgres local no es PASS de un criterio que nombra Supabase.

Cada fila sale de un criterio del enunciado (fases, evaluación o entrega) o de una restricción explícita de esta ejecución. El texto oficial está en `source/OFFICIAL_README.md`.

| ID | Required | Criterio |
| --- | --- | --- |
| R01 | sí | La migración crea `telemetry_events` con las ocho columnas y los tipos del enunciado. |
| R02 | sí | Cada fila mapea `timestamp`, `service`, `event_type`, `level`, `value`, `message` y `tags` como el contrato. |
| R03 | sí | `eventId`, `sessionId`, `userId`, `schemaVersion` y `requestId` se guardan en `tags`. El mapeo está en `telemetry-plan.md`. |
| R04 | sí | Hay índice en `timestamp`, índice en `event_type` y un GIN en `tags`. |
| R05 | sí | No hay UPDATE ni DELETE de aplicación. La tabla rechaza esas sentencias. |
| R06 | sí | `POST /telemetry/events` sustituye al stub, acepta `{ "events": [...] }` y sigue aceptando el cuerpo `text/plain` del beacon. |
| R07 | sí | El body no está tipado como `list[TelemetryEvent]`. Cada evento pasa por `TelemetryEvent.model_validate`. |
| R08 | sí | Un evento inválido no cancela el lote. Los válidos se persisten. La respuesta 200 trae `received`, `stored` y `rejected`. |
| R09 | sí | Los válidos de un lote entran en un solo INSERT y una sola transacción. |
| R10 | sí | El modelo `TelemetryEvent` no se modificó respecto del proyecto anterior. |
| R11 | sí | El frontend no cambia ni una línea. La URL del endpoint sigue igual. |
| R12 | sí | En Postgres local hay eventos de negocio y técnicos con `event_type`, `timestamp` y `tags`. |
| R13 | sí | `tags` conserva la allowlist y las dimensiones del briefing documentadas en el plan. |
| R14 | sí | La validación usa `docs/telemetry/event-schemas.json` (catálogo 1.1.0, con `web_vital_recorded`) y no abre el `$id` como archivo. |
| R15 | sí | Un curl de un lote mixto devuelve `stored` y `rejected` exactos. |
| R16 | sí | Sin base de datos, un lote con eventos válidos responde 503 y no afirma `stored`. |
| R17 | sí | `TELEMETRY_ENDPOINT` se lee. El lote no se reenvía. |
| R18 | sí | El PR se titula `feat: telemetry event storage`. La rama es `feature/telemetry-storage` contra `feature/telemetry-capture`. |
| R19 | sí | La descripción del PR incluye el JSON del lote mixto y dice que el frontend no cambió. |
| R20 | sí | Siguen verdes pytest de `services/api`, pytest de la raíz, Jest del portal, Jest del backoffice y Playwright del portal. |
| R21 | sí | No se imprimen ni se commitean secretos. No se inventa autoría. Se conservan licencias y procedencia. No se toca `.github/workflows`. |
| R22 | sí | No hay merge a `main`, ni force-push, ni envío al LMS, ni deploy a producción. |
| H01 | HITL | La tabla `telemetry_events` existe en Supabase con las ocho columnas, los tres índices y sin UPDATE/DELETE. |
| H02 | HITL | El backoffice desplegado genera al menos una entrada, una salida y un evento técnico, y esas filas se leen en Supabase. |
| H03 | HITL | El PR lleva una captura de Supabase con al menos 5 filas reales, una técnica y una de negocio. |
| H04 | HITL | Entrega al instructor o al LMS. |
| H05 | HITL | Merge a `main` después de que el PR se apruebe. Este encargo lo prohíbe. |
| N01 | no | Lockup. No hay UI en esta entrega y el enunciado prohíbe tocar el frontend. |
| N02 | no | Capturas 390/768/1280, vídeo, axe y reduced-motion. No hay cambio de UI. |
| X01 | extra | Log con filas insertadas, rechazadas y el motivo del rechazo, sin el cuerpo del evento. |
| X02 | extra | Test de rechazo parcial y de un solo INSERT contra Postgres. |
