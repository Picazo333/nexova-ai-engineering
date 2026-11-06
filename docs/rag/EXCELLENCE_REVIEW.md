# Revisión de excelencia — caso 038

Los extras no sustituyen requisitos. Ninguno contradice el enunciado.

Conteo alineado con la rúbrica: **40 PASS**, **0 FAIL**, **4 BLOCKED_HITL** (R11, R20, R22, R35) por las keys de 4Geeks. R29 no aplica.

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

## Diferido

Llamadas reales a los modelos de 4Geeks y el Recall@3 en ese espacio. Siguen BLOCKED_HITL.
