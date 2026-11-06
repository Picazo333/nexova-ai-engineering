# Support agent

Sales-support graph for an SDR. It answers one question from the Nexova knowledge base.

The graph, the checkpoints, and the trace writer are `services/api/app/agent/`. The HTTP entry is `POST /agent/query` on the existing FastAPI app (`services/api/app/main.py`). `GET /agent/runs/{run_id}` returns the stored trace.

Nodes:

1. `receive_question` — keeps the question and rejects an empty or oversized one.
2. `retrieve_context` — calls `retrieve()` in `data/pipelines/rag.py`.
3. `generate_answer` — calls `generate_answer(question, context)` with the chunks from step 2.

Conditional edges:

- Empty or invalid question → `refuse_empty`. Retrieval does not run.
- No chunk above the threshold → `insufficient_context`. Generation does not run.
- Otherwise → `generate_answer`.

`query()` is not a node. The state is `question`, `context`, `answer`, `error`, and `status`. There is no conversation history.

```bash
uv run python -m pytest tests/pipelines/test_agent_graph.py
PYTHONPATH=services/api uv run python -m app.agent.export_trace
```

The published trace is derived from the instrumented run in `docs/langgraph/evidence/r25-instrumented/`. Generation model: `online/openrouter/deepseek/deepseek-v4-flash` at `https://llm.4geeks.ai/v1`. Fee run `8d1bc6df-340e-4f11-920e-dc8ff9d109c4` keeps 22% and names Marcos Ibáñez (661+293=954 generation tokens, 5 checkpoints). Rebuild with `PYTHONPATH=services/api uv run python -m app.agent.export_trace`. Routing tests may stub the two pipeline functions. Those stubs are not the published trace.

> _Spanish version: [README.es.md](./README.es.md)._
