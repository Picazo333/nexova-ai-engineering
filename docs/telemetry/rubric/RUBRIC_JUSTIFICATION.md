# Justificación — 025

| ID | Estado | Cómo se cumple | Evidencia |
| --- | --- | --- | --- |
| R01 | PASS | `inbound_order_created`, `outbound_order_created`, `stock_threshold_triggered`, `direct_stock_edit_rejected`, `kit_cost_variance_detected`, marcados obligatorio. | `telemetry-plan.md` sección 1 y catálogo. `source/nexova-BRIEFING.md` sección 3. |
| R02 | PASS | `office` `valencia`/`miami`, categorías `training_kit`/`certification`/`onboarding_equipment`, moneda EUR/USD sin conversión, sin nombres de personas. El slug de programa no se inventa: los ejemplos inglés y español no coinciden. | `telemetry-plan.md` secciones 1, 2 y 4. Esquema, definiciones de esas claves. |
| R03 | PASS | Del `POST /auth/login` al 201 de entrada o de salida, con las pantallas del backoffice. | `telemetry-plan.md` sección 6. |
| R04 | PASS | Siete puntos numerados en ese recorrido. | `telemetry-plan.md` sección 6. |
| R05 | PASS | Punto 4 `direct_stock_edit_rejected` (el 422 de `current_stock`). Punto 3 `order_validation_failed`. Punto 6 `stock_threshold_triggered` con el `available` de `create_exit` y el 10 de `LOW_STOCK_BELOW`. | `telemetry-plan.md` sección 6. `uis/backoffice/lib/stock.ts`. `tests/test_inventory.py`. |
| R06 | PASS | `login_failed`, `login_succeeded`, `session_expired`, `credential_rejected`. El query `reason=expired` no cuenta como caducidad. | Fichas de autenticación. `app/auth/deps.py`, `uis/backoffice/lib/http.ts`, `uis/portal/lib/api.ts`. |
| R07 | PASS | `api_latency_recorded` desde el middleware de timing, a partir de 1 s o de un 5xx. `page_load_recorded` con `PerformanceNavigationTiming`, una vez por documento. | Fichas de rendimiento. `app/main.py` `timing_middleware`. |
| R08 | PASS | `frontend_exception_recorded` en `app/error.tsx` del backoffice, que hoy ignora `error`, y en el listener del portal, que no tiene `error.tsx`. El mensaje va hasheado. | Ficha del evento. |
| R09 | PASS | `section_viewed` con la tabla de rutas reales. `flow_abandoned` en entrada, salida, login, registro, reset, contraseña e incidencia. | Fichas de navegación. `lib/paths.ts`, `AppHeader.tsx`. |
| R10 | PASS | 14 eventos identificados además de los 5. Negocio, autenticación, rendimiento, errores y navegación. | Catálogo de `telemetry-plan.md`. |
| R11 | PASS | Cada ficha abre con «Capturamos … porque necesitamos saber … decisión …». El validador lo comprueba. | `evidence/validate-schemas.txt`. |
| R12 | PASS | Columna Clase del catálogo, y `origin` en el comentario de cada ficha y en `x-nexova`. | Catálogo. `event-schemas.json`. |
| R13 | PASS | El sobre exige los ocho campos. `timestamp` lleva patrón ISO 8601 porque el checker `date-time` no está instalado. | `event-schemas.json` `required`. Validador. |
| R14 | PASS | Verbos `created`, `triggered`, `rejected`, `detected`, `failed`, `succeeded`, `expired`, `requested`, `recorded`, `viewed`, `abandoned`. | Enum `event_type`. |
| R15 | PASS | Las cinco definiciones incluyen el piso del briefing. El validador falla si falta una clave. | `evidence/validate-schemas.txt`. |
| R16 | PASS | 14 identificados. | Catálogo. |
| R17 | PASS | Los 14 cubren negocio, autenticación, rendimiento, errores y navegación. | Validador: «cubren authentication, business, errors, navigation, performance». |
| R18 | PASS | `additionalProperties: false` en el sobre y en cada definición. | Esquema. Ejemplos `examples/invalid/extra-property.json` y `outbound-with-name.json`. |
| R19 | PASS | Tabla Propiedad / Tipo / Obligatorio / Descripción en cada ficha. El validador compara las filas con el esquema. | Fichas. `validate-schemas.txt`. |
| R20 | PASS | Correo, contraseña, token, IP, nombres y `assigned_to` libre quedan fuera o se reducen a `NXV-EMP-` / `assignee_redacted`. El reset no revela si la cuenta existe. El error de pantalla se hashea tras quitar correos y números. | `telemetry-plan.md` sección 4 y exclusiones. |
| R21 | PASS | Draft-07. `Draft7Validator.check_schema` pasa. 20 ejemplos válidos. 8 inválidos se rechazan. | `evidence/validate-schemas.txt` EXIT 0. |
| R22 | PASS | Allowlist, obligatorias, origen, categoría y entrega coinciden. 287 comprobaciones, 0 fallos. | `docs/telemetry/validate_event_schemas.py`. |
| R23 | PASS | Cada ficha dice stream o batch, y el comentario de máquina también. | Catálogo. |
| R24 | PASS | La justificación nombra la decisión y el plazo (el mismo día, la hora, la noche). La figura de la sección 8 lo resume para Elena y Laura. | Sección 8 y cada ficha. |
| R25 | PASS | Umbral por cruce, latencia desde 1 s con tope 30/min, carga una vez, sección a 30 s, errores de pantalla a 5/min, abandono uno por flujo, `missing_token` a 60/min. Login fallido y edición directa de stock no se descartan. | Sección 9. |
| R26 | PASS | Pregunta de conocimiento, texto de incidencia, tarifa de proveedor, acierto de caché, health, clics, semilla rejugada, 405 sin número. | Sección 10. |
| R27 | PASS | Correo, token, IP, nombres, papel de oficina fuera de las cinco métricas, histograma de latencia sana. | Sección 10. |
| R28 | PASS | Cada ficha nombra archivo y función (`create_entry`, `create_exit`, `invalid_request`, `login`, `get_current_user`, `timing_middleware`, `apiFetch`, `error.tsx`). La sección 11 es la lista de trabajo. | Secciones 7 y 11. |
| R29 | PASS | El diff de la rama no toca `services/` ni `uis/`. El script solo lee el esquema, el plan y los ejemplos. | `git diff --stat` contra `3be83a0`. |
| R30 | PASS | `docs/telemetry/telemetry-plan.md` y `docs/telemetry/event-schemas.json`. | Esos dos paths. |
| R31 | PASS | Título `docs: telemetry design plan`. El cuerpo lleva 19 eventos, 5 obligatorios, 14 identificados, las cinco categorías y la decisión de la tabla `proposed-2026-11-12` frente a `unassigned`. La base es `feature/caching-optimisation`, no `main`: lo pide esta ejecución. | Cuerpo del PR. Sección 12 del plan. |
| R32 | PASS | API 179 passed con Postgres. Jest portal 23. Jest backoffice 20. Playwright portal 14 passed. | `evidence/pytest-api.txt`, `jest-portal.txt`, `jest-backoffice.txt`, `playwright-portal.txt`. |
| X01 | PASS | Figura mermaid «En el momento / Cada hora / Cada noche» y la tabla que la une a los `event_type`. | `telemetry-plan.md` sección 8. |
| X02 | PASS | `validate_event_schemas.py` contra ejemplos válidos, inválidos y fichas. | `evidence/validate-schemas.txt`. |
| N01 | NO APLICA | No hay pantalla nueva. Las capturas de anchos no aplican. | `quality/DESIGN-QA.md`. |
| N02 | NO APLICA | El lockup es de UI. Esta entrega no tiene UI. | `quality/EXCELLENCE_REVIEW.md`. |
| N03 | NO APLICA | No hay recorrido visual. | `quality/DESIGN-QA.md`. |
| N04 | NO APLICA | No hay DOM nuevo que pasar por axe. | `quality/DESIGN-QA.md`. |
| N05 | NO APLICA | No se despliega un pipeline. No hay mock presentado como captura real. | Sección 11 del plan. |
| H01 | HITL_ENVIO_MIGUEL | El PR queda abierto. Compartirlo con el instructor o enviarlo al LMS es de Miguel. | `quality/FINAL_AUDIT.md`. |
