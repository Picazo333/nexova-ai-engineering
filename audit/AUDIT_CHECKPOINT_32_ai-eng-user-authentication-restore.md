# Checkpoint de auditoría — actividad 32 de la plataforma

**Para:** Auditor — Rodrigo Salcedo (independiente; nunca es el autor de este trabajo).
**Fecha de este checkpoint:** 13 nov 2026, 10:35 (hora de CDMX).
**Regla de veredicto:** si el trabajo **pasa la rúbrica oficial**, se da por bueno aunque haya hallazgos menores o irrelevantes. Solo un hallazgo **GRAVE** bloquea. GRAVE = rompe un criterio de la rúbrica o la seguridad (secretos, auth, inyección, pérdida de datos). MENOR se reporta y no bloquea. IRRELEVANTE se anota y no retrasa.

## Actividad

| Campo | Valor |
|---|---|
| Número de la plataforma | 32 |
| Título | The Missing Piece: Password Reset Flow |
| Slug | `ai-eng-user-authentication-restore` |
| Tarea LMS | 1022070 |
| Enlace LMS | https://learn.4geeks.com/main-cohort/latam-aie-pt-6/syllabus/authentication-web-applications/project/ai-eng-user-authentication-restore?moduleId=2 |
| Repositorio | `Picazo333/nexova-ai-engineering` (Nexova original) |
| PR | https://github.com/Picazo333/nexova-ai-engineering/pull/21 |
| Rama | `feature/user-authentication-restore` |
| Head al emitir este archivo | `83209062d0` — [árbol](https://github.com/Picazo333/nexova-ai-engineering/tree/feature/user-authentication-restore) |
| Estado LMS (13 nov 2026, API viva) | No |

## Rúbrica de referencia

Enunciado oficial: /workspace/ejecucion/014-ai-eng-user-authentication-restore/source/OFFICIAL_README.md (L118–L129). Rúbrica del autor en el head: rubric/RUBRIC.md o docs/user-authentication-restore/rubric/RUBRIC.md. El auditor evalúa contra el enunciado oficial.

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
| H1 | MENOR | PR #21, base `feature/langgraph-external-tools` @ `341ba45c0f` (API `mergeable=true`, `mergeable_state=unstable`). Head `639bc6fcb248b148785acd77946c911731fd9890`. | El enunciado (L135) pide abrir el PR contra `main`. La cola serial del monorepo usa la rama padre, igual que 024–027. | No |
| H2 | IRRELEVANTE | CI `rag-tests.yml` en la rama (y en la base): fallo heredado de `tests/api`, código de salida 4. | No es un criterio de esta actividad. | No |

No hay hallazgos GRAVE. El trabajo pasa los 12 criterios oficiales de evaluación (OFFICIAL_README.md L118–L129).

HITL abiertos, no bloquean: envío al LMS (tarea 1022070, GET 13 nov 2026: `task_status=PENDING`, `github_url` vacío); merge (decisión de Miguel). No se reenvió correo real (gasto de créditos): la evidencia `evidence/resend-live/send-result.json` del 12 nov 2026, 15:51 CST, registra HTTP 200 de Resend y de la app, `resend_calls=1`, sin clave en el fichero.

## Veredicto

- **READY** — pasa la rúbrica oficial. Los MENOR e IRRELEVANTE no lo impiden.
- **NO READY** — hay al menos un GRAVE, o un criterio obligatorio en FAIL / UNVERIFIED que no sea HITL explícito de Miguel.
- Los HITL de Miguel (merge, envío al LMS, VPS, key de LLM, prueba en dispositivo, video) no restan del porcentaje de la rúbrica y no los cierra el auditor.

## Veredicto del auditor (13 nov 2026)

- **READY / PASA.** 12/12 criterios oficiales PASS. 0 GRAVE.
- Conteos: GRAVE 0, MENOR 1, IRRELEVANTE 1.
- Informe: `audit/AUDIT_REPORT_32_ai-eng-user-authentication-restore.md`.

## Dónde dejar el reporte

1. En esta misma rama, en `audit/AUDIT_REPORT_32_ai-eng-user-authentication-restore.md` (no en `main`; no se hace merge).
2. Una copia en `/workspace/intake/zip_1112/runtime-private/academic/` con un nombre que no pise un recibo anterior.
3. Avisa al Orquestador. No comentes en el LMS ni pidas tú más datos a los profesores.

## Estado portable de la cohorte

Las 83 actividades, en el orden de la plataforma, están en `Picazo333/4geeks-control-tower`, carpeta `estado/`, rama `estado-cohorte-2026-11-13`, PR https://github.com/Picazo333/4geeks-control-tower/pull/32 (sin merge). En esta caja: `/workspace/ESTADO/`.
