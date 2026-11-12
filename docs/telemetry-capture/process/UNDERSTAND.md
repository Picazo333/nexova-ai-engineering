# UNDERSTAND — 026 captura de telemetría

El plan de 025 describe 19 eventos y el sobre. Esta entrega construye el receptor mínimo y el emisor del backoffice. El orden del enunciado es stub, luego servicio, luego instrumentación.

## Qué se construye

1. `POST /telemetry/events` en `services/api/app/telemetry/`. Valida el sobre con `TelemetryEvent`, escribe en el log cuántos eventos llegaron y el `event_type` de cada uno, y responde `{ "received": N }`. No escribe en base de datos. `TELEMETRY_ENDPOINT` se lee y no se usa para redirigir.
2. `uis/backoffice/lib/telemetry.ts`. La única función pública de envío es `track(eventType, properties)`. La cola sale cada 10 segundos o al llegar a 20 eventos. `visibilitychange` oculto usa `navigator.sendBeacon`. Un fallo de red reintenta tres veces con espera 200 ms, 400 ms y se descarta. Un 4xx no se reintenta: el mismo cuerpo inválido no se vuelve válido. El componente no pasa `eventId`, `sessionId`, `userId`, `timestamp`, `schemaVersion` ni `requestId`.
3. La instrumentación vive en el backoffice y llama a `track()`. Las propiedades salen de la allowlist. Si falta una clave obligatoria, ese evento no se emite.

## Decisiones

| Tema | Decisión |
| --- | --- |
| Dónde se emite | En el backoffice, en el momento en que la pantalla ya tiene la respuesta. El plan nombra funciones de la API como enganche de un emisor futuro. Este enunciado pide un solo `track()` en el cliente. |
| `unit_cost_minor` | El plan dice añadirlo en la captura, no en la semilla. La columna es nullable. El primer costo de un activo, proveedor y oficina no tiene histórico y no emite `kit_cost_variance_detected`. El segundo, si se separa más del 10 %, sí. |
| Papel (`office_supplies`) | Sigue fuera de las cinco métricas. |
| `programme_id` | `unassigned`. Al lado va `catalogue_gap_recorded` con `gap = missing_programme`. |
| Web Vitals | No hay `event_type` en el esquema. No se inventa. La carga del documento es `page_load_recorded`. |
| Login fallido | `failure_code` solo puede ser `invalid_credentials`. La caducidad es `session_expired`. La red es `api_response_failed`. Meter los tres en `login_failed` rompería el esquema. |
| Portal | El enunciado sitúa el servicio en `uis/backoffice`. Las pantallas del portal no se instrumentan en esta rama. |
| `asset_created` y `password_reset_requested` | No hay alta de producto ni restablecimiento en el backoffice. No se añade una pantalla para forzar el evento. |
| Credenciales que exigen el secreto JWT | El navegador no clasifica `bad_signature`. Sí emite `missing_token` cuando una ruta protegida no tiene token, y `session_expired` cuando el `exp` del token que ya tenía ya pasó. No usa el query `reason=expired` como fuente. |

## Qué no es un mock

El lote que el navegador envía llega a uvicorn y responde 200. El costo que dispara `kit_cost_variance_detected` es el que el operador escribe; la mediana sale de filas ya guardadas en PostgreSQL. El estado vacío y el de error de la lista se forzaron en el navegador para la captura de UI. Eso no se usa como prueba del stub.
