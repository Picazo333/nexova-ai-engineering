# Auditoría final — 021 ai-eng-milestone-backend-development

Estado: **PENDIENTE_REVISION_ORQUESTADOR**. No es READY_TO_SUBMIT. No hubo merge. No se envió nada al LMS.

## Resultado

30/30 criterios que cuentan: PASS (R01–R30).

Extras E01 y E02: PASS.

No cuentan:

| ID | Estado | Qué falta |
| --- | --- | --- |
| S01 | BLOCKED_HITL | URI de Supabase, método Transaction pooler, tipo URI. No hay proyecto ni clave. |
| S02 | BLOCKED_HITL | Llamada real a ese proyecto. PostgreSQL 16.15 local no lo sustituye. |
| D01 | HITL_ENVIO_MIGUEL | Subir la URL del fork o del PR a la plataforma del estudiante. |
| D02 | HITL_MIGUEL | Pegar la URI en `.env`, revisar este PR y decidir el merge. |

## Qué se ejecutó

- `cd services/api && uv run pytest` sin `NEXOVA_TEST_DATABASE_URL` → 162 passed, 7 skipped. La base era 157. Las 5 pruebas nuevas que no abren Postgres pasan igual. Los 7 saltos son las de integración.
- La misma suite con `NEXOVA_TEST_DATABASE_URL` apuntando a PostgreSQL local → 169 passed.
- `uv run pytest --cov` → 169 passed, `app.auth` al 91.60% (mínimo 70).
- Desde la raíz, `uv run python -m pytest tests packages/incident_analysis/tests` → 64 passed, 1 skipped. El salto ya existía.
- Proceso en `127.0.0.1:8011` contra el esquema `evidence021`: alta, login, listado, 400 de stock, 422 si mandas `current_stock`, 401 sin token, entrada con el id de TinyDB.
- `psql`: versión 16.15, tablas `asset`, `assetentry`, `assetexit`, sin columna `current_stock`, dos FK a `asset`, cero tablas de usuario.

No se reinstaló `uis/`. Este hito no toca el frontend. Jest y Playwright del portal no se volvieron a lanzar porque no hay `node_modules` en la VM.

## Checklist de Miguel

1. Revisar el PR contra `feature/company-monorepo-container`. No hay merge automático.
2. Si quieres cerrar S01 y S02, sigue `RUNBOOK_SUPABASE.md` con tu URI de Transaction pooler. No la subas al repositorio.
3. Entregar al instructor o al LMS, si toca. D01.
4. Merge solo después de aprobar. D02.

## Límites

- No hay cuenta de Supabase ni URI de pooler.
- `create_all()` crea el esquema al arrancar. No es un historial de migraciones.
- El marcador `00000000-0000-4000-8000-000000000201` identifica la semilla. No inicia sesión. Las órdenes de la API guardan el id de TinyDB de quien llama.
- El stock no se parte por oficina dentro de un mismo activo. Cada SKU del briefing ya tiene una oficina.
- La contraseña del rol local de esta VM no está en el repo.
