# FINAL AUDIT — 026 captura de telemetría

Estado: `PENDIENTE_REVISION_ORQUESTADOR`.

No es `READY_TO_SUBMIT`. No hubo merge ni envío al LMS.

## Base

- Rama: `feature/telemetry-capture`
- Parte de: `feature/telemetry-plan` @ `da3525b9cf1e6fedfd158f2200eb1371227261e1` (PR #29)
- PR contra: `feature/telemetry-plan`
- Título: `feat: telemetry event capture`

## Conteo

| Estado | Filas |
| --- | --- |
| PASS | 36 |
| FAIL | 1 (R22 Web Vitals: el esquema cerrado no tiene ese `event_type`) |
| HITL | 1 (H01, fuera del porcentaje) |
| NO APLICA | 2 (N01, N02) |

Required que cuentan: 37. 36/37.

## Suites

| Suite | Resultado |
| --- | --- |
| `services/api` pytest con `NEXOVA_TEST_DATABASE_URL` | 170 passed |
| pytest de la raíz (`tests/`) | 47 passed, 1 skipped |
| Jest portal | 23 passed |
| Jest backoffice | 28 passed |
| `next build` backoffice | EXIT 0 |
| `next build` portal | EXIT 0 |
| Playwright portal | 14 passed |

El check de CI `rag-tests.yml` no se toca. Ya falla en las ramas base por una ruta `tests/api` que no existe.

## Límites que el orquestador debe ver

1. R22 queda en FAIL. No es un olvido: emitir Web Vitals violaría `event-schemas.json`.
2. El 200 del stub está en el log y en la respuesta del navegador. No hay una captura del cromo de DevTools.
3. `outbound_order_created`, `stock_threshold_triggered` y `direct_stock_edit_rejected` están instrumentados y validados contra el esquema. El lote fotografiado trae `inbound_order_created` y `kit_cost_variance_detected`.
4. El vacío y el error de la lista se forzaron en el navegador. No se usan como PASS de la integración.
5. Supabase no persiste eventos. El stub no escribe.
6. El portal no emite telemetría en esta rama.

## Autoría

No se añaden nombres de colaboradores. Los ficheros de origen conservan el texto de 4Geeks. El crédito visual del lockup ya estaba y no se presenta como una asociación oficial.
