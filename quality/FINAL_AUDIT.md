# Auditoría final — 040 ai-eng-langgraph-agent-tools

Estado: PENDIENTE_REVISION_ORQUESTADOR. No está READY_TO_SUBMIT.

## Cierre

22/22 criterios que se pueden implementar en esta VM están en PASS. La rúbrica tiene 27 filas. Las otras cinco no son un fallo de implementación:

| ID | Estado | Motivo |
| --- | --- | --- |
| R09 | NO_APLICA | No hay gestor de inventario (021). No se inventó stock. |
| L01 | BLOCKED_HITL | Faltan `GENERATION_*`. Un doble no es PASS. |
| L02 | BLOCKED_HITL | Faltan `EMBEDDING_*`. fastembed no sustituye el criterio. |
| D01 | HITL_ENVIO_MIGUEL | Envío al LMS y enlace al instructor. |
| D02 | HITL_MIGUEL | Merge a `main` cuando el PR esté aprobado. |

## Checklist de Miguel

1. Revisar el PR de `feature/langgraph-external-tools` contra `feature/langgraph-agent-base`. No está mergeado.
2. Decidir el merge a `main` (D02).
3. Enviar al LMS o compartir el enlace (D01).
4. Cuando existan las keys, volver a correr `test_eval_live_answer_is_grounded_in_the_briefing` y una recuperación con `EMBEDDING_*`. Hasta entonces L01 y L02 siguen en BLOCKED_HITL.
5. La etiqueta `langgraph-external-tools` del enunciado, si el repositorio no la tiene creada, la pone Miguel.

## Qué no se rompió

`cd services/api && uv run pytest`: 138 passed. La base citada era 131. Las siete pruebas nuevas están en `services/api/tests/test_ticket_tool.py`. El resto de 017, 038 y 039 sigue en verde, incluida la suite de la raíz: 25 passed y 1 skipped (el skip es L01).

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
