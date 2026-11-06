# 038 — corrida live con el LLM de 4Geeks (local, sin publicar)

Fecha: 2026-11-06, 11:31–11:43 CST. Head verificado: `eafe56e` (PR #16, `feature/rag-knowledge-base`), clon de lectura en la caja.
Base URL: `https://llm.4geeks.ai/v1` (OpenAI-compatible). La key se pasó solo por env del proceso; no está en ningún archivo.
Embeddings: `online/openrouter/perplexity/pplx-embed-v1-0.6b` (1024 dim). Generación: `online/openrouter/deepseek/deepseek-v4-flash`.
Qdrant: motor embebido del SDK (`QDRANT_PATH` local), el modo que el README documenta cuando `QDRANT_URL` está vacío.

| Criterio | Antes | Ahora | Evidencia |
|---|---|---|---|
| R11 llamada real a embeddings 4Geeks | BLOCKED_HITL | PASS | `01-setup-embed.txt`: 32 chunks, vector_size 1024 |
| R20 sin contexto, dice que no hay información y no inventa | BLOCKED_HITL | PASS | `03-generation-live.json`, caso fuera del corpus: 0 chunks sobre el umbral; el modelo dice que no tiene la información |
| R22 llamada real a generación 4Geeks | BLOCKED_HITL | PASS | `03-generation-live.json` (respuesta con fuente citada) y `05-api-knowledge-query.txt` (`POST /knowledge/query` HTTP 200) |
| R35 Recall@3 ≥ 80% en el espacio de embeddings exigido | BLOCKED_HITL | PASS | `02-recall-at-3.txt` y `02-recall-report.json`: 24/24 = 1.00, `official_4geeks_criterion: measured` |

Tests: `tests/pipelines/test_rag.py` dio 7 passed (`04-pytest-rag.txt`).

## Hallazgo para REPAIR (no bloquea)
El primer `POST /knowledge/query` devolvió HTTP 200 con `{"answer":"Gra"}`: el proxy entregó una respuesta truncada y `complete_chat()` la aceptó porque no estaba vacía. Los dos reintentos y dos llamadas directas salieron completos (`finish_reason=stop`). Reparación propuesta: rechazar `finish_reason != "stop"` y respuestas por debajo de una longitud mínima con `GenerationCallFailed`, con un test.

## Tokens
Llamada diagnóstica: prompt 935 / completion 371 y prompt 856 / completion 504. No hay conteo agregado de toda la corrida.

Nada de esto está publicado: espera la confirmación directa de Miguel.
