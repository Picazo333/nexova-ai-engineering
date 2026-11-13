# Checkpoint de auditoría — actividad 33 de la plataforma

**Para:** Auditor — Rodrigo Salcedo (independiente; nunca es el autor de este trabajo).
**Fecha de este checkpoint:** 13 nov 2026, 10:35 (hora de CDMX).
**Regla de veredicto:** si el trabajo **pasa la rúbrica oficial**, se da por bueno aunque haya hallazgos menores o irrelevantes. Solo un hallazgo **GRAVE** bloquea. GRAVE = rompe un criterio de la rúbrica o la seguridad (secretos, auth, inyección, pérdida de datos). MENOR se reporta y no bloquea. IRRELEVANTE se anota y no retrasa.

## Actividad

| Campo | Valor |
|---|---|
| Número de la plataforma | 33 |
| Título | Company Monorepo Containerization |
| Slug | `ai-eng-company-monorepo-container` |
| Tarea LMS | 1022000 |
| Enlace LMS | https://learn.4geeks.com/main-cohort/latam-aie-pt-6/syllabus/latam-container-applications-with-docker/project/ai-eng-company-monorepo-container?moduleId=1 |
| Repositorio | `Picazo333/nexova-ai-engineering` (Nexova original) |
| PR | https://github.com/Picazo333/nexova-ai-engineering/pull/22 |
| Rama | `feature/company-monorepo-container` |
| Head al emitir este archivo | `b88de1b4a1` — [árbol](https://github.com/Picazo333/nexova-ai-engineering/tree/feature/company-monorepo-container) |
| Estado LMS (13 nov 2026, API viva) | No |

## Rúbrica de referencia

Enunciado oficial: /workspace/ejecucion/015-ai-eng-company-monorepo-container/source/ (OFFICIAL_README). Rúbrica del autor en el PR. No hay recibo de Rodrigo a esta fecha. El auditor evalúa contra el enunciado oficial.

El auditor no usa como única fuente la autoevaluación del autor. Contrasta con el enunciado oficial. No reescribe el código, no hace merge, no envía al LMS y un autor nunca audita su propio trabajo.

## Qué intentar romper (de todas las formas razonables)

1. **Tests:** correr las suites documentadas en un entorno limpio. Registrar comando, salida y fallos. Distinguir fallos nuevos de los heredados de la base (por ejemplo `tests/api` / `rag-tests`).
2. **Entradas inválidas:** vacíos, tipos incorrectos, tamaños extremos, Unicode, IDs inexistentes, tokens caducados o reutilizados, dobles envíos.
3. **Seguridad:** authz (datos de otro usuario), inyección, CSRF donde aplique, límites de tasa. **Nunca imprimas, copies ni subas secretos reales.**
4. **Secretos:** buscar claves, tokens, contraseñas o URIs con password en el árbol, en la evidencia y en el historial del PR. Un secreto en el repo es GRAVE.
5. **UI** (si hay interfaz): responsiva (aprox. 390 / 768 / 1280), teclado, foco, contraste, textos alternativos, estados de error y vacío. Si declara SIGNAL, comprobar tokens; no imponer SIGNAL contra la rúbrica.
6. **Rendimiento** (si la rúbrica lo pide): mediciones en producción (build + start), nunca en modo dev.
7. **Reproducibilidad desde cero:** seguir el README de un clone limpio. Lo que la rúbrica deja en HITL humano no se convierte en FAIL.
8. **Cumplimiento literal del enunciado** y de las prohibiciones (no usar IA, no copiar la solución oficial, etc.), con evidencia.
9. **Integridad:** no fabricar evidencia, no contar mocks como integración real, no inflar PASS, no inventar autoría.

## Tabla de hallazgos (a llenar por el auditor)

| ID | Severidad (GRAVE / MENOR / IRRELEVANTE) | Dónde (archivo, línea, SHA, comando) | Qué se observó | Criterio de rúbrica afectado | ¿Bloquea? |
|---|---|---|---|---|---|
| H1 | MENOR | README raíz documenta `make up` (llena `.env` gitignorado y lanza Compose). `docker compose.yml` declara `env_file` con `required: false`. `jwt_secret()` en `services/api/app/auth/security.py` L50–54 lanza `AuthConfigError` si `JWT_SECRET` falta o es corto. | Enunciado: «`docker compose up` desde la raíz arranca la plataforma sin pasos extra». Sin `make up`, el login fallaría por secreto vacío; salud y contenedores pueden arrancar. El atajo documentado cubre el caso. | No |
| H2 | MENOR | PR #22, `mergeable=false`, `mergeable_state=dirty`. La base `feature/user-authentication-restore` se movió de `d69a3b954c` a `639bc6fcb2` (checkpoint + ESTADO, 13 nov 10:40–10:42 CST). | No es un criterio de la rúbrica oficial. Afecta al merge (HITL). | No |
| H3 | IRRELEVANTE | En este sandbox no hay CLI de Docker. `tests/infra/test_compose_contract.py::test_rendered_compose_keeps_qdrant_off_public_interfaces` se salta (diseñado así). `test_env_is_gitignored_and_absent_from_history` falló aquí con `git log --all` exit 128 por un objeto ausente del clone parcial (`97e7bb36`); la API de GitHub devuelve 0 commits para `.env` y variantes. `.env` está en `.gitignore` L14 y no está en el índice. | El criterio «`.env` en `.gitignore` y ausente del historial» se verifica por esas otras vías, no por el fallo local. | No |

No hay hallazgos GRAVE. Los criterios oficiales no-HITL pasan. El criterio de evaluación «contenedores desplegados y en producción en el VPS» queda en **HITL** (acceso SSH y autorización de Miguel; runbook en `docs/container/RUNBOOK.md`, estado BLOCKED_HITL, sin URL inventada). No es GRAVE y no bloquea.

HITL abiertos, no bloquean: VPS; envío al LMS (tarea 1022000, GET 13 nov 2026: `PENDING`, `github_url` vacío); merge.

## Veredicto

- **READY** — pasa la rúbrica oficial. Los MENOR e IRRELEVANTE no lo impiden.
- **NO READY** — hay al menos un GRAVE, o un criterio obligatorio en FAIL / UNVERIFIED que no sea HITL explícito de Miguel.
- Los HITL de Miguel (merge, envío al LMS, VPS, key de LLM, prueba en dispositivo, video) no restan del porcentaje de la rúbrica y no los cierra el auditor.

## Veredicto del auditor (13 nov 2026)

- **READY / PASA.** Criterios oficiales no-HITL en PASS. VPS en HITL. 0 GRAVE.
- Conteos: GRAVE 0, MENOR 2, IRRELEVANTE 1.
- Informe: `audit/AUDIT_REPORT_33_ai-eng-company-monorepo-container.md`.

## Dónde dejar el reporte

1. En esta misma rama, en `audit/AUDIT_REPORT_33_ai-eng-company-monorepo-container.md` (no en `main`; no se hace merge).
2. Una copia en `/workspace/intake/zip_1112/runtime-private/academic/` con un nombre que no pise un recibo anterior.
3. Avisa al Orquestador. No comentes en el LMS ni pidas tú más datos a los profesores.

## Estado portable de la cohorte

Las 83 actividades, en el orden de la plataforma, están en `Picazo333/4geeks-control-tower`, carpeta `estado/`, rama `estado-cohorte-2026-11-13`, PR https://github.com/Picazo333/4geeks-control-tower/pull/32 (sin merge). En esta caja: `/workspace/ESTADO/`.
