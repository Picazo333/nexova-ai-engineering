# FINAL AUDIT — 027 almacenamiento de telemetría

Estado: `PENDIENTE_REVISION_ORQUESTADOR`.

No es `READY_TO_SUBMIT`. No hubo merge a `main` ni envío al LMS.

## Base

- Rama: `feature/telemetry-storage`
- Parte de: `feature/telemetry-capture` @ `631e01a1fb640f7c0e2a894c2d4ee70f9e03cb8f` (PR #30)
- La base avanzó a `6cc066f7bf61f42dbb7b32941aa166799f29e770` (plan y `$id` en 1.1.0)
- Merge normal: `e6fb02fd43eb3723423063956979cfc13888c0d8`
- PR contra: `feature/telemetry-capture`
- Título: `feat: telemetry event storage`
- Código de almacenamiento: `8ea4431` más el merge. Las suites de esta auditoría corrieron después del merge, sobre ese árbol.

## Conteo

| Estado | Filas |
| --- | --- |
| PASS | 24 (R01–R22, X01, X02) |
| FAIL | 0 |
| HITL | 5 (H01, H02, H03, H05 = HITL_MIGUEL; H04 = HITL_ENVIO_MIGUEL) |
| NO APLICA | 2 (N01, N02) |

Required que cuentan: 22. 22/22. HITL no entra en el porcentaje.

## Suites

Corridas después del merge `e6fb02f`.

| Suite | Resultado |
| --- | --- |
| `services/api` `uv run pytest` con `NEXOVA_TEST_DATABASE_URL` | 196 passed |
| `services/api` `uv run pytest tests` | 179 passed (la base 026 era 171 en este directorio) |
| pytest de la raíz (`tests/`) | 47 passed, 1 skipped |
| Validador de `event-schemas.json` | 300 pass, 0 fail |
| Jest portal | 23 passed |
| Jest backoffice | 29 passed |
| Playwright portal | 14 passed |

`uis/` no cambia respecto de `6cc066f`.

El check de CI `rag-tests.yml` no se toca. Ya falla en las ramas base por una ruta `tests/api` que no existe.

## Límites que el orquestador debe ver

1. Supabase no tiene la tabla. H01, H02 y H03 quedan en HITL_MIGUEL. Los pasos están en `rubric/RUBRIC_JUSTIFICATION.md`. Postgres local demuestra el SQL, el bulk insert y el rechazo parcial. No demuestra Supabase.
2. No hay captura del editor de Supabase ni órdenes hechas desde el backoffice desplegado.
3. El `$id` del esquema es `event-envelope-1.1.0.json`. El loader no abre ese nombre. Abre `docs/telemetry/event-schemas.json`.
4. `level` es NOT NULL. `tags` incluye los cinco campos del sobre además de la allowlist. Las dos decisiones están en la sección 13 del plan.
5. El enunciado pide PR contra `main` y merge. El encargo pide PR contra `feature/telemetry-capture` y prohíbe el merge. Se sigue el encargo.
6. El check `pytest` de CI que invoca `tests/api` sigue fuera de este PR.

## Autoría

No se añaden nombres de colaboradores. Los ficheros de origen conservan el texto de 4Geeks. Los commits de esta rama los firma el agente de la sesión.
