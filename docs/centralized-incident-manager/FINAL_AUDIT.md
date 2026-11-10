# Auditoría final — 016

Estado: **PENDIENTE_AUDITORIA_INDEPENDIENTE**. Esto no es la auditoría independiente. No hay merge. No hay envío al LMS.

Commit sin el parche: `6d0c5789b47fc28c5371970f0ccbed3b677b567a` (punta de PR #17). El parche añade estos documentos, las tres capturas y `services/api/tests/test_incident_summary_empty.py`.
Rama: `feature/centralized-incident-manager`. Base: `feature/building-bullet-proof-applications` (PR #15).

## Resultado (20 required)

PASS 15 · FAIL 0 · UNVERIFIED 5. Detalle en `RUBRIC_JUSTIFICATION.md`. Con UNVERIFIED en criterios required no está listo para auditoría.

## Suites (10-nov-2026; Python 3.13.5, uv 0.13.7, Node 24.22.1, Playwright 1.56.1 con Chrome del sistema)

| Suite | Resultado | Log |
| --- | --- | --- |
| `cd services/api && uv run pytest` | 107 passed | `evidence/rerun-2026-11-10/02-pytest.txt` |
| `uv run pytest --cov` | 107 passed, `app.auth` 95.38% | `03-pytest-cov.txt` |
| `npx jest --coverage` | 15 passed | `11-jest.txt` |
| `npx playwright test` | 10 passed | `13-playwright.txt` |
| Seed ×2 y `/api/incidents/summary` en localhost | 96 insertadas, 0 en la 2ª corrida, totales = BRIEFING | `20-seed2x-summary.txt` |
| Test nuevo de `/summary` con la base vacía | 2 passed | `40-patch-test-summary-empty.txt` |
| `pytest` completo con el parche | 109 passed | `42-patched-pytest-full.txt` |
| `playwright` completo con el parche | 10 passed | `43-patched-playwright-full.txt` |
| Test con fuga de orden (`test_incident_manager.py` antes del test nuevo) | 7 passed | `44-patched-pytest-full-random-order-check.txt` |

## Capturas que pide el PR

`evidence/form-error-1280.png`, `evidence/list-1280.png`, `evidence/summary-1280.png`. Se generan con `uis/portal/scripts/capture-incident-manager.mjs` contra la API local con el seed cargado. Para la foto, la cabecera sticky se deja en flujo normal.

## Pendiente

- UNVERIFIED: C14 (carga y botón deshabilitado), C15 (error de la API en lenguaje claro), C16 (estados cargando y vacío), C17 (reversión del estado), C20 (la UI está en `services/`; lo decide el auditor).
- Fuga entre tests: `test_internal_error_does_not_return_the_exception` asigna `records.list_incidents = boom` a nivel de módulo, sin `monkeypatch.setattr`. Cualquier test posterior que llame a `GET /api/incidents` recibe 500. El test nuevo lo evita; la corrección mínima (`monkeypatch.setattr(records, "list_incidents", boom)`) queda fuera del alcance de este parche.
- Detalle visto en la captura del listado: «Mostrando 96 incidencias con los filtros actuales.» aparece dos veces.
