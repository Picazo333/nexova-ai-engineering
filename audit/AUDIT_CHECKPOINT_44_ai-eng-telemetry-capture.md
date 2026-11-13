# Checkpoint de auditoría — actividad 44 de la plataforma

**Para:** Auditor — Rodrigo Salcedo (independiente; nunca es el autor de este trabajo).
**Fecha de este checkpoint:** 13 nov 2026, 10:35 (hora de CDMX).
**Regla de veredicto:** si el trabajo **pasa la rúbrica oficial**, se da por bueno aunque haya hallazgos menores o irrelevantes. Solo un hallazgo **GRAVE** bloquea. GRAVE = rompe un criterio de la rúbrica o la seguridad (secretos, auth, inyección, pérdida de datos). MENOR se reporta y no bloquea. IRRELEVANTE se anota y no retrasa.

## Actividad

| Campo | Valor |
|---|---|
| Número de la plataforma | 44 |
| Título | Company's Telemetry – Frontend capture |
| Slug | `ai-eng-telemetry-capture` |
| Tarea LMS | 1022091 |
| Enlace LMS | https://learn.4geeks.com/main-cohort/latam-aie-pt-6/syllabus/latam-application-telemetry/project/ai-eng-telemetry-capture?moduleId=2 |
| Repositorio | `Picazo333/nexova-ai-engineering` (Nexova original) |
| PR | https://github.com/Picazo333/nexova-ai-engineering/pull/30 |
| Rama | `feature/telemetry-capture` |
| Head auditado (esta pasada) | `5054f4b19b98944bc1195c462916d052d15476a5` |
| Estado LMS (13 nov 2026, API viva, GET) | PENDING / PENDING, `github_url` vacío (tarea 1022091) |

## Rúbrica de referencia

Enunciado oficial: /workspace/ejecucion/026-ai-eng-telemetry-capture/source/. El head se pulió después del recibo (631e01a → 6cc066f): conviene reconfirmar. Eventos forzados en el navegador no cuentan.

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
| H1 | MENOR | PR #30, base distinta de `main`. Head `5054f4b19b98944bc1195c462916d052d15476a5`. | Cola serial. | Proceso, no L111–L122. | No |
| H2 | IRRELEVANTE | CI `rag-tests.yml`, fallo heredado de `tests/api`. | El pulido 1.1.0 no toca el workflow. | No | No |

No hay hallazgos GRAVE. Se mantiene el 23/23 del recibo `026_INDEPENDENT_REVIEW.md` (SHA `631e01a1fb640f7c0e2a894c2d4ee70f9e03cb8f`). El delta `9a9e28e`/`6cc066f` alinea plan y `$id` a 1.1.0 y aporta evidencia del validador (300 PASS); no cambia el código de captura.

HITL abiertos, no bloquean: envío al LMS (tarea 1022091, PENDING); merge.

## Veredicto

- **READY** — pasa la rúbrica oficial. Los MENOR e IRRELEVANTE no lo impiden.
- **NO READY** — hay al menos un GRAVE, o un criterio obligatorio en FAIL / UNVERIFIED que no sea HITL explícito de Miguel.
- Los HITL de Miguel (merge, envío al LMS, VPS, key de LLM, prueba en dispositivo, video) no restan del porcentaje de la rúbrica y no los cierra el auditor.

## Veredicto del auditor (13 nov 2026)

- **READY / PASA.** 23/23 vigentes. 0 GRAVE. Pulido 1.1.0 documental; código de captura intacto.
- Conteos: GRAVE 0, MENOR 1, IRRELEVANTE 1.
- Informe: `audit/AUDIT_REPORT_44_ai-eng-telemetry-capture.md`.

## Dónde dejar el reporte

1. En esta misma rama, en `audit/AUDIT_REPORT_44_ai-eng-telemetry-capture.md` (no en `main`; no se hace merge).
2. Una copia en `/workspace/intake/zip_1112/runtime-private/academic/` con un nombre que no pise un recibo anterior.
3. Avisa al Orquestador. No comentes en el LMS ni pidas tú más datos a los profesores.

## Estado portable de la cohorte

Las 83 actividades, en el orden de la plataforma, están en `Picazo333/4geeks-control-tower`, carpeta `estado/`, rama `estado-cohorte-2026-11-13`, PR https://github.com/Picazo333/4geeks-control-tower/pull/32 (sin merge). En esta caja: `/workspace/ESTADO/`.
