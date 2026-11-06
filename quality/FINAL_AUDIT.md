# Auditoría final — 040 ai-eng-langgraph-agent-tools

Estado: PENDIENTE_REVISION_ORQUESTADOR. No está READY_TO_SUBMIT.

## Cierre

24/27 filas en PASS (R01–R08, R10–R14, L01, L02, D03, U01–U08). Las otras tres no son un fallo de implementación:

| ID | Estado | Motivo |
| --- | --- | --- |
| R09 | NO_APLICA | El enunciado lo deja opcional y prohibe simular el inventario. Citas en `rubric/RUBRIC_JUSTIFICATION.md`: `OFFICIAL_README.es.md` L29, L33, L65, L78 y L92. |
| D01 | HITL_ENVIO_MIGUEL | Envío al LMS y enlace al instructor. Sigue siendo de Miguel. |
| D02 | HITL_MIGUEL | Merge a `main` cuando el PR esté aprobado. Sigue siendo de Miguel. No hay merge. |

## Pull request

https://github.com/Picazo333/nexova-ai-engineering/pull/20

Base: `feature/langgraph-agent-base` (`8858642`). La tool está en `3e9ac08`. Esta reparación publica `evidence/llm-live/` y deja L01 y L02 en PASS. El head es el de la rama después de este commit.

## Checklist de Miguel

1. Revisar el PR https://github.com/Picazo333/nexova-ai-engineering/pull/20 contra `feature/langgraph-agent-base`. No está mergeado.
2. Decidir el merge a `main` (D02).
3. Enviar al LMS o compartir el enlace (D01).
4. L01 y L02 están en PASS con `evidence/llm-live/` (22 passed, 0 skipped; HTTP 200 y la traza `receive_question` → `route_sources` → `retrieve_context` → `generate_answer`). D01 y D02 no cambian.
5. La etiqueta `langgraph-external-tools` ya está en el PR.

## Qué no se rompió

Re-corrida en esta VM el 2026-11-06 17:58 UTC: `cd services/api && uv run pytest` 138 passed. Raíz (`test_agent_graph`, `test_agent_routing`, `test_project_constraints`): 25 passed, 1 skipped. El skip es el eval en vivo porque esta VM no tiene las keys. La corrida que cierra L01 y L02 es `evidence/llm-live/01-pytest-agent-live.txt`: 22 passed, 0 skipped. La base citada de la API era 131.

## Límites

- La tool no escribe en el gestor. Sin token no lee.
- El router no es un modelo. Está documentado en `quality/EXCELLENCE_REVIEW.md`.
- La pantalla `/agente` necesita JavaScript para mantener las dos columnas a la vez. Sin JavaScript cada formulario hace POST y la página vuelve con esa columna rellena.
- El lockup es el crédito visual aceptado por Miguel. No añade autores ni una relación comercial.

## Reparaciones durante EVAL

1. Los evals de la raíz no veían TinyDB. Se declaró `tinydb==4.8.2` en el grupo dev de la raíz, la misma versión que ya usa la API.
2. `docs/langgraph/trace-full-run.json` se regeneró para incluir el nodo `route_sources`.
3. El export lado a lado añade `packages/shared` al path antes de `create_incident`.
4. La aserción del HTML buscaba un apóstrofo sin escapar. El texto real es `I don&#x27;t have`.
5. `test_internal_error_does_not_return_the_exception` dejaba `list_incidents` parcheado. Ahora restaura la función. Sin eso, la prueba nueva de lectura veía el centinela.
6. Un 503 no devolvía la traza. Ahora el cuerpo lleva `trace` además de `detail` y `run_id`, sin el campo `answer`.
7. El vídeo salió en 1,96 s y luego en 4,44 s. La toma final dura 5,80 s.
8. Lighthouse se quedó en el prompt de telemetría. Se relanzó con `CI=1`.
9. L01 y L02 estaban en BLOCKED_HITL y el export decía `explicit_stand_in`. La corrida live se copió a `evidence/llm-live/` y sustituyó esa traza. D01 y D02 no se tocaron.
