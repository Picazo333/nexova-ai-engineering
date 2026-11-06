# 040 — corrida live con el LLM de 4Geeks (local, sin publicar)

Fecha: 2026-11-06, 11:44–11:46 CST. Head verificado: `54b8621` (PR #20, `feature/langgraph-external-tools`), clon de lectura en la caja.
Base URL `https://llm.4geeks.ai/v1`. La key se pasó solo por env del proceso. Embeddings `online/openrouter/perplexity/pplx-embed-v1-0.6b` (1024 dim); generación `online/openrouter/deepseek/deepseek-v4-flash`. Qdrant embebido con el índice live de esta corrida. JWT_SECRET efímero, generado solo para el proceso.

| Criterio | Antes | Ahora | Evidencia |
|---|---|---|---|
| L01 respuesta live anclada en el briefing | BLOCKED_HITL | PASS | `01-pytest-agent-live.txt`: 22 passed y 0 skipped en test_agent_graph + test_agent_routing (antes, el anclaje live salía como skipped). `02-api-agent-query.txt`: mantiene el 22%, deriva a Marcos Ibáñez y cita pricing-model y objection-handling |
| L02 pregunta de tarifa contra el proceso real con embeddings 4Geeks | BLOCKED_HITL | PASS | `02-api-agent-query.txt`: `POST /agent/query` da HTTP 200, con traza receive_question → route_sources → retrieve_context → generate_answer (antes terminaba en 503 y en el nodo error) |

Observación: la pregunta de incidentes abiertos va a la herramienta (`lookup_ticket`) y responde con honestidad que el gestor pide un token válido. Es el comportamiento documentado de la herramienta y no forma parte de L01/L02.

Nada de esto está publicado: espera la confirmación directa de Miguel.
