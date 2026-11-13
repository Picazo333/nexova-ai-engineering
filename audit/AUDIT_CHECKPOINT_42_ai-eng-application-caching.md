# Checkpoint de auditoría — actividad 42 de la plataforma

**Para:** Auditor — Rodrigo Salcedo (independiente; nunca es el autor de este trabajo).
**Fecha de este checkpoint:** 13 nov 2026, 10:35 (hora de CDMX).
**Regla de veredicto:** si el trabajo **pasa la rúbrica oficial**, se da por bueno aunque haya hallazgos menores o irrelevantes. Solo un hallazgo **GRAVE** bloquea. GRAVE = rompe un criterio de la rúbrica o la seguridad (secretos, auth, inyección, pérdida de datos). MENOR se reporta y no bloquea. IRRELEVANTE se anota y no retrasa.

## Actividad

| Campo | Valor |
|---|---|
| Número de la plataforma | 42 |
| Título | Performance Optimisation: Caching |
| Slug | `ai-eng-application-caching` |
| Tarea LMS | 1022086 |
| Enlace LMS | https://learn.4geeks.com/main-cohort/latam-aie-pt-6/syllabus/latam-architecture-optimization/project/ai-eng-application-caching?moduleId=3 |
| Repositorio | `Picazo333/nexova-ai-engineering` (Nexova original) |
| PR | https://github.com/Picazo333/nexova-ai-engineering/pull/26 |
| Rama | `feature/caching-optimisation` |
| Head auditado (esta pasada) | `a600dd4a9b3aeda123f5aef2687269877cedacd3` |
| Estado LMS (13 nov 2026, API viva, GET) | PENDING / PENDING, `github_url` vacío (tarea 1022086) |

## Rúbrica de referencia

Enunciado oficial: /workspace/ejecucion/024-ai-eng-application-caching/source/. Rúbrica: docs/caching-optimisation/rubric/RUBRIC.md. Justificación y FINAL_AUDIT en la misma carpeta.

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
| H1 | MENOR | PR #26, base distinta de `main`. Head `a600dd4a9b3aeda123f5aef2687269877cedacd3`. | Cola serial del monorepo. Igual que en el recibo del 12 nov. | Proceso, no L157–L164. | No |
| H2 | IRRELEVANTE | CI `rag-tests.yml` en la rama (y en la base): fallo heredado de `tests/api`. | No es un criterio de esta actividad. El código de caché no cambió desde `3be83a02`. | No | No |

No hay hallazgos GRAVE. Se mantiene el 18/18 del recibo `024_INDEPENDENT_REVIEW.md` (SHA `3be83a02252f2de46e57e67b52194bd70eff9d7d`). El único delta posterior es documentación (ESTADO + este checkpoint).

HITL abiertos, no bloquean: envío al LMS (tarea 1022086, PENDING); merge.

## Veredicto

- **READY** — pasa la rúbrica oficial. Los MENOR e IRRELEVANTE no lo impiden.
- **NO READY** — hay al menos un GRAVE, o un criterio obligatorio en FAIL / UNVERIFIED que no sea HITL explícito de Miguel.
- Los HITL de Miguel (merge, envío al LMS, VPS, key de LLM, prueba en dispositivo, video) no restan del porcentaje de la rúbrica y no los cierra el auditor.

## Veredicto del auditor (13 nov 2026)

- **READY / PASA.** 18/18 vigentes. 0 GRAVE. Delta posterior al recibo: solo docs.
- Conteos: GRAVE 0, MENOR 1, IRRELEVANTE 1.
- Informe: `audit/AUDIT_REPORT_42_ai-eng-application-caching.md`.

## Dónde dejar el reporte

1. En esta misma rama, en `audit/AUDIT_REPORT_42_ai-eng-application-caching.md` (no en `main`; no se hace merge).
2. Una copia en `/workspace/intake/zip_1112/runtime-private/academic/` con un nombre que no pise un recibo anterior.
3. Avisa al Orquestador. No comentes en el LMS ni pidas tú más datos a los profesores.

## Estado portable de la cohorte

Las 83 actividades, en el orden de la plataforma, están en `Picazo333/4geeks-control-tower`, carpeta `estado/`, rama `estado-cohorte-2026-11-13`, PR https://github.com/Picazo333/4geeks-control-tower/pull/32 (sin merge). En esta caja: `/workspace/ESTADO/`.
