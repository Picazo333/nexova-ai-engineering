# Revisión de excelencia — 025

Estado de esta revisión: no sustituye la del orquestador.

## Qué queda sólido

Las cinco métricas salen del briefing leído en el syllabus `fd2da034`, no de una lista inventada. El plan nombra el archivo y la función donde cada evento se engancha mañana: `create_entry`, `create_exit`, `invalid_request`, `login`, `get_current_user`, el middleware de timing, `apiFetch` y `error.tsx`.

El validador ata el Markdown al JSON Schema: mismas claves, misma obligatoriedad, mismos orígenes. Ocho ejemplos inválidos cubren clave de más, programa ausente, fecha mal formada, tipo desconocido, correo en el login, nombre en la salida, moneda cruzada con la oficina, y un id de empleado junto a la marca de redacción.

Las suites que ya existían siguen en el mismo resultado que la rama base: API 179 con Postgres, Jest 23 y 20, Playwright 14.

## Límites

- `proposed-2026-11-12` traduce `hardware` y `peripherals` a `onboarding_equipment` porque el briefing llama así a los portátiles de incorporación y la semilla hardware es ese portátil. Elena no ha confirmado la tabla. La versión va en el evento para poder filtrarla después.
- `programme_id = unassigned` es un cubo de calidad. No es un programa del briefing. Sin esa marca, las cinco métricas no podrían cumplirse con el `Asset` actual, que no tiene columna de programa.
- `kit_cost_variance_detected` está diseñado y no puede dispararse: `AssetEntry` no guarda costo. No se fabricó un importe.
- `NXV-OFF-001` (papel, `office_supplies`) no entra en las cinco métricas. Un intento de escribir su stock a mano tampoco. El 422 sigue existiendo; la métrica de Patricia, para el papel, no.
- El cliente llama `expired` a cualquier 401. El plan prohíbe usar ese query como fuente de `session_expired`. Quien instrumente y se salte esa regla inflará las caducidades.
- `decode_access_token` hoy mete caducidad y firma mala en el mismo mensaje. El plan describe el corte con `ExpiredSignatureError`. Ese corte no está escrito en código, a propósito.
- Los topes de 30 y de 60 son por proceso. Esta API arranca en un solo proceso.
- No se midió de nuevo la latencia. La frase de los 110 ms cita la mediana ya publicada en el proyecto de caché. El ejemplo de 1105 ms es un caso que cruzaría el umbral de 1 s, no una medida de esta rama.
- No hay pipeline, almacén ni proveedor. N05 es NO APLICA. Un mock de envío no se presenta como captura.

## Extra visible y extra técnico

Visible: la figura de la sección 8, con lo que se mira en el momento, cada hora y cada noche.

Técnico: `validate_event_schemas.py`, draft-07, ejemplos y fichas.

## Lockup

No hay UI. El lockup de SIGNAL no se copia. La regla está en el brief: en proyectos sin frontend el lockup no aplica.

## Autoría

No se añaden colaboradores ni firmas. Las copias de enunciado y briefing conservan el texto del syllabus. El SHA256 está en `process/SOURCE.md`.
