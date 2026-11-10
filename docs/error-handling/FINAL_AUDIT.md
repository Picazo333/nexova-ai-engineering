# Auditoría final — 017

Estado: **PENDIENTE_AUDITORIA_INDEPENDIENTE**. Las cifras de abajo salen de una re-ejecución real del 10-nov-2026 (CDMX), con logs versionados en `docs/error-handling/evidence/rerun-2026-11-10/`. Esta nota no es la auditoría independiente. No hay merge. No hay envío al LMS.

Commit de la rama sin el parche: `97e7bb36c5abec60f8c81202fd67e6063c853c3f` (punta de PR #19; la versión anterior de este documento citaba `2bbaf91`, que es su padre).  
Commit con el parche: lo fija el `git am` que lo aplique. El parche añade `.finally` al JS del backoffice, `services/api/tests/test_backoffice_finally.py` y `uis/portal/e2e/backoffice-finally.spec.ts`.  
Rama: `feature/error-handling-audit`  
PR: https://github.com/Picazo333/nexova-ai-engineering/pull/19  
Base: `feature/centralized-incident-manager` (PR #17)

## Resultado

Autoevaluación del productor, no auditoría independiente. Criterios required R01–R21 (21), E01–E02 (2) y S01–S06 (6): **29/29 PASS** (antes se citaba 28 por error de suma de rangos).  
FAIL: ninguno.  
BLOCKED: ninguno.  
HITL_ENVIO_MIGUEL (fuera del porcentaje): H01.

## Checklist de entrega para Miguel

1. Revisar el PR de `feature/error-handling-audit` contra `feature/centralized-incident-manager`.
2. Decidir el orden con #16 si hace falta.
3. H01: compartir la URL del PR con el instructor o el LMS. Este paso no lo hace esta ejecución.
4. Merge solo después de la revisión. Esta ejecución no mergea.

## Suites

Re-ejecución del 10-nov-2026 (Python 3.13.5, uv 0.13.7, Node 24.22.1, Playwright 1.56.1 con Google Chrome del sistema). Los logs que citaba la versión anterior (`logs/pytest.txt`, `logs/jest.txt`, `logs/playwright.txt`) no existían en el árbol. Los sustituyen estos:

| Suite | SHA | Resultado | Log |
| --- | --- | --- | --- |
| `cd services/api && uv run pytest` | `97e7bb3` | 115 passed | `evidence/rerun-2026-11-10/02-pytest.txt` |
| `cd services/api && uv run pytest --cov` | `97e7bb3` | 115 passed, `app.auth` 95.19% (umbral 70%) | `03-pytest-cov.txt` |
| `cd uis/portal && npx jest --coverage` | `97e7bb3` | 19 passed (5 suites) | `11-jest.txt` |
| `cd uis/portal && npx playwright test` | `97e7bb3` | 10 passed | `13-playwright.txt` |
| `pytest tests/test_backoffice_finally.py` sin el JS del parche | `97e7bb3` | 6 failed (esperado) | `40-patch-test-WITHOUT-js-patch.txt` |
| `pytest tests/test_backoffice_finally.py` con el parche | `97e7bb3` + parche | 6 passed | `41-patch-test-WITH-patch.txt` |
| `pytest` completo con el parche | `97e7bb3` + parche | 121 passed | `42-patched-pytest-full.txt` |
| `npx playwright test` completo con el parche | `97e7bb3` + parche | 11 passed | `43-patched-playwright-full.txt` |
| `gitleaks dir` del árbol | `97e7bb3` | 3 hallazgos: 2 son hashes de assets en `test_assets.py` (falso positivo) y 1 es un JWT caducado de la transcripción de 012 | `30-gitleaks.txt` |

Los hashes de los logs están en `evidence/rerun-2026-11-10/SHA256SUMS.txt`.

## Integridad

El enunciado no prohíbe la IA. La línea 60 pide el coding agent. El escaneo se repitió y está citado en R02. No hay autoría inventada ni colaboradores añadidos.

## Límites

- No hay llamada real a un proveedor externo: la API no tiene uno.
- INP de laboratorio es null. Se informa TBT.
- El lockup no se ha añadido al sitio público. Motivo en EXCELLENCE_REVIEW.
- La revisión de este ejecutor no es la aprobación visual del dueño del repo.
