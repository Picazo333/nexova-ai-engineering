# Justificación — 026 captura de telemetría

| ID | Estado | Evidencia |
| --- | --- | --- |
| R01 | PASS | `services/api/app/telemetry/router.py`. `tests/test_telemetry.py` `test_stub_accepts_a_batch_and_returns_the_count`. |
| R02 | PASS | El mismo test lee el log `received=2` y `login_succeeded`. En el navegador, `evidence/stub-log.txt`. |
| R03 | PASS | El test exige `{ "received": 2 }`. El lote del navegador respondió `{ "received": 6 }` (`evidence/telemetry-batches.json` guarda otro lote real de 2, también 200). |
| R04 | PASS | `services/api/app/telemetry/schemas.py` `TelemetryEvent`. Un sobre incompleto responde 422. |
| R05 | PASS | `app/config.py` `telemetry_endpoint()`. `test_telemetry_endpoint_is_read_from_the_environment`. El log dice `endpoint_set=True`. |
| R06 | PASS | `uis/backoffice/lib/telemetry.ts` cola `queue`. `pendingEvents()` en Jest. |
| R07 | PASS | `__tests__/telemetry.test.ts`: 19 eventos no llaman a `fetch`; el 20 sí; uno suelto espera 10 s. |
| R08 | PASS | El mismo fichero, «al ocultar la pestaña el lote sale con sendBeacon». El cuerpo es `text/plain` y el stub lo acepta (`test_stub_accepts_text_plain_beacon_body`). |
| R09 | PASS | El test de red falla tres veces y la cola queda vacía. Las esperas son 200 ms y 400 ms. |
| R10 | PASS | `seal()` en `telemetry.ts`. El test de `login_failed` comprueba que el componente no puso el sobre. `sessionId` antes del login es `missing` y `userId` es `anonymous`, como el esquema. |
| R11 | PASS | Los componentes importan `track` o funciones que solo llaman a `track`. No hay otro envío. |
| R12 | PASS | `endpointUrl()` lee `process.env.NEXT_PUBLIC_TELEMETRY_ENDPOINT`. `uis/backoffice/.env.example` documenta `http://localhost:8000/telemetry/events`. |
| R13 | PASS | Las cinco obligatorias tienen llamada a `track()` y un evento de Jest contra `event-schemas.json`. El navegador registró `inbound_order_created`, `kit_cost_variance_detected`, y después una salida real de NXV-IT-001 (stock 14, cantidad 5) que emitió `outbound_order_created` y `stock_threshold_triggered` (`evidence/telemetry-batch-outbound.json`). `direct_stock_edit_rejected` no tiene pantalla: el panel no envía `current_stock`. |
| R14 | PASS | `installTelemetryRuntime` escucha `error` y `unhandledrejection`. `app/error.tsx` llama a `recordException`. El hash del ejemplo del plan coincide: `b7b32534990c138f77d0b6a7d0d9d0d58ad07faca7c6d5ab1d69c54bcc459036`. |
| R15 | PASS | `page_load_recorded` en el arranque del documento y `api_latency_recorded` en `apiFetch` desde 1000 ms o con estado ≥ 500. El lote guardado trae `page_load_recorded` de `/login`. |
| R16 | PASS | `SiteHeader` llama a `trackSection` al cambiar `pathname`. El lote trae `section_viewed` / `backoffice_login`. |
| R17 | PASS | `lib/telemetry-catalog.ts` solo escribe claves de la allowlist. El test recorre los eventos de material y `expectValid` usa Ajv sobre `event-schemas.json`. `office_supplies` no emite. |
| R18 | PASS | `propertiesAreSafe` tira el evento si hay correo, contraseña, nombre o token. El test «no encola un evento con correo» lo comprueba. El JSON guardado no contiene `@`. |
| R19 | PASS | Chrome, vía Playwright, hizo `POST /telemetry/events`. uvicorn respondió 200. `evidence/stub-log.txt` y `evidence/telemetry-batches.json`. No es un mock del stub. No hay una foto del panel Network de Chrome; la petición y la respuesta son las de ese Chrome. |
| R20 | PASS | El test recorre `uis/backoffice` y solo `lib/telemetry.ts` contiene `/telemetry/events`. No hay axios. |
| R21 | PASS | El enum del modelo y el de `event-schemas.json` son los 20 del plan en 1.1.0. `test_stub_rejects_an_unknown_event_type` rechaza `page_view`. |
| R22 | PASS | `web_vital_recorded` entra en `event-schemas.json` como 1.1.0, sin cambiar los eventos de 1.0.0. `WebVitalsReporter` usa `useReportWebVitals` y llama a `track()`. `lib/web-vitals.ts` pone `metric_name`, `value`, `rating`, `path_template` y `app`. El validador termina en 300 PASS y 0 FAIL (`evidence/validate-schemas.txt`). La API acepta el ejemplo con 200 y rechaza con 422 la versión 1.0.0, `FID` y un correo. El test de Jest cubre los cortes. |
| R23 | PASS | `LoginScreen` emite `login_failed` con `invalid_credentials` en el 401 y `login_succeeded` con `expires_in_seconds` tras guardar el token. `apiFetch` emite `session_expired` solo si el `exp` del token ya pasó, y `credential_rejected` / `missing_token` si la ruta protegida no tiene token. El valor del correo y de la contraseña no entra en `properties`. `session_expired` y el fallo de red no caben dentro de `login_failed`: el esquema fija `failure_code` en `invalid_credentials` y reparte la caducidad y la red en otros dos eventos. |
| R24 | PASS | Título del PR: `feat: telemetry event capture`. |
| R25 | PASS | El cuerpo del PR lleva la tabla de eventos de esta justificación. |
| R26 | PASS | Rama `feature/telemetry-capture` desde `da3525b`. Base del PR: `feature/telemetry-plan`. Sin merge, sin force-push, sin LMS. El enunciado pedía `main` y merge; manda el encargo. |
| R27 | PASS | pytest de `services/api` con PostgreSQL: 171 passed. pytest de la raíz: 47 passed, 1 skipped. Jest del portal: 23 passed. Jest del backoffice: 29 passed. Playwright del portal: 14 passed. Logs en `evidence/`. |
| R28 | PASS | Obligatorios: los cinco del plan. `programme_id` es `unassigned`. No se asigna `b2b-sales` ni `liderazgo-basico`. El papel no entra en las cinco métricas. El costo de la semilla no se inventa. |
| R29 | PASS | `JWT_SECRET` y la contraseña del usuario de prueba viven en `/tmp` y en la sesión del navegador. No están en el diff. `TELEMETRY_ENDPOINT` es una URL local. |
| R30 | PASS | No se añaden colaboradores ni firmas. Los README de origen se copian con su texto. El lockup no se reinterpreta como una asociación. |
| U01 | PASS | `evidence/login-390.png`, `login-768.png`, `login-1280.png`, `inbound-sent-390.png`, `inbound-sent-768.png`, `inbound-sent-1280.png`. |
| U02 | PASS | `evidence/recorrido-entrada.webm`, duración 9,0 s. |
| U03 | PASS | `products-loading-390.png`, `products-empty-768.png`, `products-error-1280.png`. El vacío y el error se forzaron en el navegador. El 200 del stub no usa ese force. |
| U04 | PASS | Pares medidos en `quality/DESIGN-QA.md`. El indicador usa `--color-muted` sobre superficie blanca: 6,61:1. |
| U05 | PASS | `products-reduced-1280.png`. Sin animación nueva. |
| U06 | PASS | `axe-login.json` y `axe-products.json`: 0 violaciones. No es una certificación WCAG. |
| U07 | PASS | A 390 se ve el lockup apilado (`login-390.png`). A 768 y 1280, el horizontal. Los bytes siguen en `uis/backoffice/brand/`. |
| X01 | PASS | `components/TelemetryStatus.tsx`. Visible en las capturas de `next dev`. `next build` lo elimina porque `NODE_ENV` no es `development`. |
| X02 | PASS | Jest con Ajv contra `event-schemas.json`. pytest del stub y de la mediana de costo. |
| N01 | NO APLICA | El stub no persiste. La fase 3 es la base. |
| N02 | NO APLICA | El servicio pedido está en el backoffice. |
| H01 | HITL | No se comparte con el instructor y no se envía al LMS. No entra en el porcentaje. |

## Eventos instrumentados

| `event_type` | Clase | Dónde |
| --- | --- | --- |
| `inbound_order_created` | obligatorio | `EntryForm` tras el 201 |
| `outbound_order_created` | obligatorio | `ExitForm` tras el 201 |
| `stock_threshold_triggered` | obligatorio | `ExitForm` si el stock cruza 10 hacia abajo |
| `direct_stock_edit_rejected` | obligatorio | `apiFetch` si inventario responde 422 con `current_stock`, o 405 con un entero |
| `kit_cost_variance_detected` | obligatorio | `EntryForm` cuando la API devuelve `variance_ratio` mayor que 0,1 |
| `catalogue_gap_recorded` | identificada | Junto a cada evento de material con `programme_id` `unassigned` |
| `order_validation_failed` | identificada | `EntryForm` y `ExitForm` en el error de la API |
| `login_failed` | identificada | `LoginScreen` en el 401 |
| `login_succeeded` | identificada | `LoginScreen` tras guardar el token |
| `session_expired` | identificada | `apiFetch` si el `exp` del token ya pasó |
| `credential_rejected` | identificada | `apiFetch` sin token en una ruta protegida (`missing_token`) |
| `api_latency_recorded` | identificada | `apiFetch` desde 1000 ms o con estado ≥ 500 |
| `page_load_recorded` | identificada | `installTelemetryRuntime` |
| `frontend_exception_recorded` | identificada | `app/error.tsx`, `window` `error` y `unhandledrejection` |
| `api_response_failed` | identificada | `apiFetch` si no hay red o el estado es 5xx |
| `section_viewed` | identificada | `SiteHeader` |
| `flow_abandoned` | identificada | `useFlowAbandon` en login, entrada y salida |

No instrumentados, y no se finge que lo estén: `asset_created`, `password_reset_requested`, y los `credential_rejected` que el navegador no puede distinguir sin el secreto.

## Conteo

Required con estado: 37 filas R y U. PASS 37. FAIL 0. HITL 1, fuera del porcentaje. 37/37.
