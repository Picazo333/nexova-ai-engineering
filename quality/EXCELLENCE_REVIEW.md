# Revisión de excelencia — 040

Los extras no cambian el enunciado. Los dos pedidos en el lanzamiento están implementados. Un tercero se rechazó.

## Visible — trazas lado a lado

Decisión: IMPLEMENT.

`/agente` pone la ruta RAG y la ruta de tickets en dos columnas. Cada una muestra la respuesta y la traza (`route`, `sources`, nodos en orden). La pregunta de la tarifa, sin embeddings de 4Geeks, enseña el error real de configuración. La pregunta con un id creado por `POST /api/incidents` enseña el estado `in_progress` leído del gestor. El ticket 482 enseña el fallback, sin un estado inventado.

Evidencia: `evidence/agente-lado-a-lado-1280.png`, `evidence/agente-lado-a-lado-390.png`, `evidence/agente-ticket-vacio-768.png`, `docs/langgraph/traces-side-by-side.json`.

## Técnico — timeout, fallback y enrutamiento

Decisión: IMPLEMENT.

El enunciado ya pide timeout, fallback y dos evals. Lo que queda por encima del mínimo:

- El timeout de producción es 4,0 s y el test de comportamiento corta a los 0,2 s un lector que dormiría 2 s y devolvería `resolved`. La respuesta no contiene ese estado. Tiempo medido por debajo de 1 s.
- El fallback cubre id ausente, timeout, token ausente y la frase en español.
- Hay siete evals de ruta en `tests/pipelines/test_agent_routing.py`, no dos: tool, RAG, ausente, timeout, español, mixta y filtro `open` contra el almacén real.
- El cliente HTTP de prueba solo registra `GET`, con el timeout 4 y el header `Authorization`.

Evidencia: `tests/pipelines/test_agent_routing.py`, `services/api/tests/test_ticket_tool.py`, `evidence/pytest-root.txt`, `evidence/pytest-api.txt`.

## Router con modelo

Decisión: REJECT.

Un router que llamara al modelo de 4Geeks no se puede verificar: las keys no están. Marcarlo PASS con un doble contradice la regla de que un mock no cierra la integración real. El router determinista sí se verifica con las evals y no inventa estados.

## Inventario

No es un extra. Es R09, NO_APLICA, porque el gestor del proyecto 021 no está en el monorepo.
