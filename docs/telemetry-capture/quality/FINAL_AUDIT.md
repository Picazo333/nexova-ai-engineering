# FINAL AUDIT — 026 captura de telemetría

Estado: `PENDIENTE_REVISION_ORQUESTADOR`.

No es `READY_TO_SUBMIT`. No hubo merge ni envío al LMS.

## Base

- Rama: `feature/telemetry-capture`
- Parte de: `feature/telemetry-plan` @ `da3525b9cf1e6fedfd158f2200eb1371227261e1` (PR #29)
- PR contra: `feature/telemetry-plan`
- Título: `feat: telemetry event capture`
- Head anterior a R22: `76e70b159b49783f2114b84a2b72d611bb14df4d`
- Head de R22: se anota en el commit que cierra esta auditoría.

## Conteo

| Estado | Filas |
| --- | --- |
| PASS | 37 |
| FAIL | 0 |
| HITL | 1 (H01, fuera del porcentaje) |
| NO APLICA | 2 (N01, N02) |

Required que cuentan: 37. 37/37.

## Suites

| Suite | Resultado |
| --- | --- |
| `services/api` pytest con `NEXOVA_TEST_DATABASE_URL` | 171 passed |
| pytest de la raíz (`tests/`) | 47 passed, 1 skipped |
| Jest portal | 23 passed |
| Jest backoffice | 29 passed |
| `next build` backoffice | EXIT 0 |
| `next build` portal | EXIT 0 |
| Playwright portal | 14 passed |

El check de CI `rag-tests.yml` no se toca. Ya falla en las ramas base por una ruta `tests/api` que no existe.

## Límites que el orquestador debe ver

1. No hay una captura del panel Network de Chrome. El 200 del stub sigue siendo la petición real del navegador de la pasada anterior.
2. `outbound_order_created`, `stock_threshold_triggered` y `direct_stock_edit_rejected` están instrumentados y validados contra el esquema. No salieron en el lote fotografiado.
3. El vacío y el error de la lista se forzaron en el navegador. No se usan como PASS de la integración.
4. Supabase no persiste eventos. El stub no escribe.
5. El portal no emite telemetría. `web_vital_recorded` sale del backoffice. `app` admite `portal` para cuando esa captura exista.
6. El check `pytest` de CI que invoca `tests/api` sigue fuera de este PR. Esa ruta no existe y el arreglo es otro cambio.

## Autoría

No se añaden nombres de colaboradores. Los ficheros de origen conservan el texto de 4Geeks. El crédito visual del lockup ya estaba y no se presenta como una asociación oficial.
