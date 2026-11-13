# DESIGN-QA — 025

No hay UI nueva. El entregable es el plan, el esquema y el validador de línea de comandos. Las comprobaciones de pantalla quedan en NO APLICA, con la razón al lado.

| Comprobación | Resultado |
| --- | --- |
| 390 / 768 / 1280 | NO APLICA. No hay vista nueva. |
| Carga, vacío y error de una pantalla | NO APLICA. El plan describe esos estados como eventos (`page_load_recorded`, `flow_abandoned`, `frontend_exception_recorded`, `api_response_failed`) y no los pinta. |
| `prefers-reduced-motion` | NO APLICA. No hay motion nueva. Playwright del portal sigue cubriendo el indicador de carga quieto: 14 passed, incluido ese caso. |
| Lockup | NO APLICA. No hay footer nuevo. |
| Vídeo | NO APLICA. No hay recorrido visual. |
| axe | NO APLICA. No hay DOM nuevo. No se certifica WCAG. |
| Tipografía y color de una pantalla | NO APLICA. El diagrama es Mermaid dentro del Markdown. |
| SEO | NO APLICA. No hay ruta pública nueva. El backoffice y el portal siguen como estaban. |
| Validador | `python3 docs/telemetry/validate_event_schemas.py`. 287 PASS, 0 FAIL. Log en `evidence/validate-schemas.txt`. |
| Ejemplos rechazados | Clave de más, programa ausente, fecha `12/11/2026`, `event_type` desconocido, correo en `login_failed`, nombre en la salida, EUR/USD cruzado con la oficina, `assignee_ref` junto a `assignee_redacted`. |
| Suites | API 179 passed con `postgresql:///nexova_audit`. Jest portal 23. Jest backoffice 20. Playwright portal 14 passed. |

No hay hero, ni métricas de negocio inventadas, ni testimonios. Los números del plan que vienen de la semilla (stock 12, 6, 20, 0, 18, 15) están en `services/api/app/inventory/seed.py`. El 10 del umbral está en `uis/backoffice/lib/stock.ts`. El 110 ms citado es la mediana ya medida en el proyecto de caché, no una medida nueva.
