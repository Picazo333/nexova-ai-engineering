# Rúbrica — 026 captura de telemetría

Required = sí cuenta para el cierre. HITL no resta. Un mock no es PASS de una integración real.

Cada fila sale de un criterio del enunciado (fases, evaluación, actividad adicional o entrega) o de una restricción explícita de esta ejecución. El texto oficial está en `source/OFFICIAL_README.md`.

| ID | Required | Criterio |
| --- | --- | --- |
| R01 | sí | Existe `POST /telemetry/events` y acepta `{ "events": [...] }`. |
| R02 | sí | El stub escribe en el log cuántos eventos llegaron y el `event_type` de cada uno. |
| R03 | sí | Responde 200 con `{ "received": N }`. |
| R04 | sí | El modelo `TelemetryEvent` tiene `eventId`, `timestamp`, `sessionId`, `userId`, `event_type`, `schemaVersion`, `requestId` y `properties`. |
| R05 | sí | El backend lee `TELEMETRY_ENDPOINT` aunque el stub no redirija. |
| R06 | sí | `TelemetryService` acumula una cola en memoria. |
| R07 | sí | Envía la cola cada 10 segundos o al llegar a 20 eventos. |
| R08 | sí | `visibilitychange` oculto vacía la cola con `navigator.sendBeacon`. |
| R09 | sí | Si la red falla, reintenta hasta 3 veces con espera creciente y luego descarta el lote. |
| R10 | sí | El servicio genera `eventId`, `sessionId`, `userId`, `timestamp`, `schemaVersion` y `requestId`. Quien llama a `track()` no los pasa. |
| R11 | sí | La única función pública de envío es `track(eventType, properties)`. |
| R12 | sí | El navegador lee `NEXT_PUBLIC_TELEMETRY_ENDPOINT`. La URL no está escrita en el código de envío. |
| R13 | sí | Las cinco métricas obligatorias del briefing, vía el plan, están instrumentadas. |
| R14 | sí | Hay errores de frontend no capturados (`window` y el error boundary). |
| R15 | sí | Hay al menos una métrica de rendimiento: carga de documento o latencia de API. |
| R16 | sí | Hay vista de sección en las pantallas principales del backoffice. |
| R17 | sí | Los eventos priorizados usan la allowlist del plan. No se añaden claves de más. |
| R18 | sí | Ningún evento lleva correo, nombre, contraseña ni token. |
| R19 | sí | Un lote real del navegador llega al stub y la respuesta es 200. |
| R20 | sí | No hay `fetch` ni `axios` de telemetría fuera de `lib/telemetry.ts`. |
| R21 | sí | Los `event_type` son los del plan, no etiquetas genéricas del README. |
| R22 | sí | Actividad adicional: Web Vitals como eventos, con la ruta en `properties`. |
| R23 | sí | Los eventos de autenticación del plan se capturan en el login o en `apiFetch`, sin correo ni contraseña. |
| R24 | sí | El PR se titula `feat: telemetry event capture`. |
| R25 | sí | El cuerpo del PR lista los eventos, marca obligatorios e identificados, y dice qué componente o hook captura cada uno. |
| R26 | sí | La rama es `feature/telemetry-capture` contra `feature/telemetry-plan`. Sin merge, sin force-push y sin LMS. |
| R27 | sí | Siguen verdes pytest de `services/api`, Jest del portal, Jest del backoffice y Playwright del portal. |
| R28 | sí | No se inventan métricas ni programas. El vocabulario es el del plan y del briefing. |
| R29 | sí | No se imprimen ni se commitean secretos. |
| R30 | sí | No se inventan colaboradores ni firmas. Se conservan licencias y procedencia. |
| U01 | sí | Capturas reales a 390, 768 y 1280 de pantallas instrumentadas. |
| U02 | sí | Vídeo real de unos 5–10 segundos del recorrido. |
| U03 | sí | Estados de carga, vacío y error en una pantalla instrumentada. |
| U04 | sí | Contraste de texto al menos 4,5:1 en lo que esta entrega pinta. |
| U05 | sí | `prefers-reduced-motion` deja la pantalla en el estado final. |
| U06 | sí | axe en las pantallas instrumentadas sin violaciones serious o critical. No certifica WCAG. |
| U07 | sí | El lockup ya presente se conserva: apilado en 390, horizontal desde 640. |
| X01 | extra | Indicador discreto, solo en desarrollo, de eventos en cola y enviados. |
| X02 | extra | Tests que validan eventos contra `event-schemas.json`, y la cola con reintento. |
| N01 | no | Persistencia en Supabase. El enunciado la deja para la fase siguiente. |
| N02 | no | Instrumentar el portal. El enunciado sitúa el servicio en el backoffice. |
| H01 | HITL | Compartir el PR con el instructor o enviarlo al LMS. |
