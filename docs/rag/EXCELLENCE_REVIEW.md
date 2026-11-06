# Revisión de excelencia — caso 038

Los extras no sustituyen requisitos. Ninguno contradice el enunciado.

Conteo alineado con la rúbrica: **44 PASS**, **0 FAIL**, **0 BLOCKED_HITL**. R11, R20, R22 y R35 pasan con la corrida live en `docs/rag/evidence/llm-live/` (Recall@3 24/24, generación con fuente, rechazo fuera del corpus, POST HTTP 200). R29 no aplica.

## S06 — PASS

El footer de `uis/knowledge-query/` usa el lockup oficial, copiado sin editarlo:

`uis/knowledge-query/brand/signal-horizontal.svg`

sha256 `85459232bf51e7bf7c94225fd4f2cd6b71a681b6d701cb4ffd6d2a142cf57a81`

En 768 y 1280 se pinta a 400×64 px. En 390 no cabe a 400 px, así que se muestra `signal-stacked.svg` del mismo ZIP a 280×140 px. El fondo es claro, así que no se usa `signal-reverse.svg`.

## Cláusula de la línea 33

Pendiente de que Miguel la confirme. Texto del enunciado:

> For this milestone you'll work directly with the Qdrant SDK and FastAPI — no orchestration frameworks (LangChain, LlamaIndex, etc.). That means you write the four minimum functions (`setup`, `embed`, `retrieve`, `query`) yourself, which forces you to understand what each piece does instead of delegating it to an abstraction.

La lectura aplicada es que va contra LangChain y LlamaIndex. `setup`, `embed`, `retrieve`, `query` y `generate_answer` están escritos con el SDK de Qdrant y FastAPI.

## Visible — implementado

La pantalla `/conocimiento` enseña los ocho documentos oficiales y el conteo de `nexova_knowledge` antes de preguntar. Las preguntas de ejemplo salen del briefing y del archivo de objeciones; solo rellenan el campo.

Si la respuesta trae `Sources:` o `Fuentes:`, la UI las separa y ofrece copiarlas. El POST de formulario lo cubre `services/api/tests/test_knowledge.py`. Sin modelo, la pantalla muestra el 503 y no inventa una cita.

## Técnico — implementado

- `setup()` idempotente contra el cliente real de Qdrant en memoria, con UUID5 estables: `tests/process/test_setup.py`.
- Recall@3 y sondas de umbral: `data/eval/recall_at_3.py`. El 23/24 del modelo local no es PASS de R35.
- IDs de modelo distintos. El código no lee `FOURGEEKS_API_TOKEN`.
- El router vive en la app de `services/api`, no en un segundo proceso.

## Rechazado

Inventar una respuesta comercial para la captura o el PR. Un mock no cuenta como PASS de R11, R20, R22 ni R35.

## Reparación posterior a la corrida live

El primer `POST /knowledge/query` de esa evidencia devolvió HTTP 200 con `{"answer":"Gra"}`. `complete_chat` lo aceptaba porque el texto no estaba vacío. Ahora solo acepta `finish_reason == "stop"` y al menos 20 caracteres. Hay dos intentos. Si los dos fallan, lanza `GenerationCallFailed` y el endpoint responde 502, sin devolver el recorte.

Tests: `test_complete_chat_retries_truncated_gra_and_does_not_return_it`, `test_complete_chat_rejects_finish_reason_length`, `test_complete_chat_does_not_accept_gra_after_the_bounded_retry`, `test_truncated_gra_is_not_a_200_answer`.
