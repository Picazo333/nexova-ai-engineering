# Auditoría final — 022 inventario en el backoffice

Estado: **PENDIENTE_REVISION_ORQUESTADOR**. No es READY_TO_SUBMIT. No hubo merge. No se envió nada al LMS.

PR: https://github.com/Picazo333/nexova-ai-engineering/pull/24 contra `feature/milestone-backend-development` (`106083a`).

Implementación: `b9c199566576ca2613233ef049eb66397e0846ea`.

## Resultado

38/38 criterios que cuentan: PASS (R01–R25, S01–S11, E01–E02).

No cuentan:

| ID | Estado | Qué falta |
| --- | --- | --- |
| D01 | HITL_ENVIO_MIGUEL | Subir la URL del fork o del PR a la plataforma del estudiante. |
| D02 | HITL_MIGUEL | Revisar este PR y decidir el merge. |
| B01 | BLOCKED_HITL | URI de Supabase. PostgreSQL 16.15 local no lo sustituye. |

## Qué se ejecutó

- `cd services/api && uv run pytest` con `NEXOVA_TEST_DATABASE_URL` → 169 passed.
- La misma suite con `--cov` → 169 passed, `app.auth` 91,60 % (mínimo 70).
- Desde la raíz, `uv run python -m pytest tests packages/incident_analysis/tests` → 64 passed, 1 skipped.
- `cd uis/portal && npx jest --coverage` → 20 passed.
- `cd uis/portal && npx playwright test` → 14 passed.
- `cd uis/backoffice && npx jest --coverage` → 14 passed. `npx tsc --noEmit` sin errores. `npm run build` correcto.
- API en `127.0.0.1:8000` contra PostgreSQL local: NXV-IT-001 = 12, 400 de stock, entrada real que deja el stock en 13.
- axe sin serious ni critical.
- Lighthouse de producción en `127.0.0.1:3010`, tres corridas. Ver `evidence/lighthouse-summary.json`.

## Checklist de Miguel

1. Revisar https://github.com/Picazo333/nexova-ai-engineering/pull/24 contra `feature/milestone-backend-development`. No hay merge automático.
2. Para probar: API con `DATABASE_URL` de PostgreSQL y `INVENTORY_AUTOSEED=1`, y `cd uis/backoffice && npm run dev`. Entrar en `/login`. La clave del token es `nexova-access-token` en este origen.
3. Entregar al instructor o al LMS, si toca. D01.
4. Merge solo después de aprobar. D02.
5. Supabase sigue en el runbook del hito 021. B01.

## Límites

- El portal (puerto 3000) y este backoffice (puerto 3001) no comparten `localStorage`. Hay que entrar en cada origen.
- `GET /inventory/products` y `GET /inventory/orders` son públicos en la API. La UI igual exige sesión y manda el Bearer.
- La entrada de evidencia sumó 1 a NXV-IT-001 en la base local de esta VM. No está en el repositorio.
- El umbral de stock (10) es de esta pantalla. La API no lo define.
- INP de campo no se midió. TBT de laboratorio sí.
