# UNDERSTAND — 027 almacenamiento de telemetría

El stub de 026 acepta `{ "events": [...] }`, valida el lote entero con `TelemetryBatch` (`events: list[TelemetryEvent]`) y responde `{ "received": N }`. Un evento inválido devuelve 422 y no se guarda nada. El frontend solo mira el código HTTP: 2xx cuenta como enviado, 4xx se descarta, 5xx se reintenta.

El enunciado cambia el interior del mismo URL:

1. El sobre se acepta si es un objeto con un arreglo `events`. Cada elemento sigue siendo un dict.
2. `TelemetryEvent.model_validate` se aplica a cada dict. El modelo no se modifica. Sigue exigiendo el sobre y, en `web_vital_recorded`, las propiedades de 1.1.0.
3. El mismo dict se valida contra `docs/telemetry/event-schemas.json`. Ahí está la allowlist de cada `event_type`, incluida `web_vital_recorded`. El `$id` puede decir `event-envelope-1.1.0.json`; el archivo no se mueve.
4. Los válidos entran en un solo `INSERT` y una sola transacción. Los inválidos incrementan `rejected`. La respuesta es `{ "received", "stored", "rejected" }` con 200.
5. Si hay eventos válidos y no hay Postgres, la respuesta es 503. Un 200 con `stored: 0` haría que el navegador tirara el lote.
6. La tabla es de solo escritura. La migración crea las ocho columnas, tres índices y triggers que rechazan `UPDATE`, `DELETE` y `TRUNCATE`.

`tags` guarda las `properties` que pasaron el esquema y cinco campos del sobre (`eventId`, `sessionId`, `userId`, `schemaVersion`, `requestId`). El plan los usa para analizar y la tabla no tiene columna para ellos. La sección 13 de `telemetry-plan.md` fija el mapeo de `service`, `level`, `value` y `message`.

Supabase no está disponible. Crear la tabla allí, generar órdenes desde el backoffice desplegado y fotografiar esas filas queda en HITL. Postgres local no sustituye ese criterio. Sí sirve para el bulk insert, el rechazo parcial y la forma de la tabla.
