# 039 — corrida live con el LLM de 4Geeks (local, sin publicar)

Fecha: 2026-11-06, 11:43–11:45 CST. Head verificado: `8858642` (PR #18, `feature/langgraph-agent-base`), clon de lectura en la caja.
Base URL `https://llm.4geeks.ai/v1`. La key se pasó solo por env del proceso. Embeddings `online/openrouter/perplexity/pplx-embed-v1-0.6b` (1024 dim); generación `online/openrouter/deepseek/deepseek-v4-flash`. Qdrant embebido con el índice que 038 construyó con esos embeddings en esta misma corrida.

| Criterio | Antes | Ahora | Evidencia |
|---|---|---|---|
| R16 respuesta live anclada en el briefing | BLOCKED_HITL | PASS | `01-pytest-live.txt`: `test_eval_live_answer_is_grounded_in_the_briefing` PASSED sin dobles. `02-run-agent-live.json`: el agente mantiene el 22%, nombra a Marcos Ibáñez para aprobar el descuento y cita pricing-model |

Además, en `02-run-agent-live.json` la pregunta fuera del corpus termina en `insufficient_context` y no inventa nada. `03-pytest-agent-graph-full.txt`: 13 passed (antes era 12 + 1 skipped).

Nota sobre R25: sigue PASS. El export de traza que dice `live_generation: BLOCKED_HITL` es el artefacto de los tests con stand-in. Si Miguel autoriza publicar, conviene regenerar el export o ajustar ese texto.

Nada de esto está publicado: espera la confirmación directa de Miguel.
