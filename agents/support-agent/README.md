# Support agent

Sales-support graph for one question. It answers from the Nexova knowledge base or from the incident manager, and it chooses which one from the question text.

The graph, the checkpoints, and the trace writer are `services/api/app/agent/`. The HTTP entry is `POST /agent/query` on the existing FastAPI app (`services/api/app/main.py`). `GET /agent/runs/{run_id}` returns the stored trace. `/agente` shows a RAG trace and a ticket trace side by side.

Nodes:

1. `receive_question` — keeps the question and rejects an empty or oversized one.
2. `route_sources` — sets `rag`, `ticket`, or `both`.
3. `retrieve_context` — calls `retrieve()` in `data/pipelines/rag.py`.
4. `lookup_ticket` — calls the read-only ticket tool.
5. `generate_answer` — calls `generate_answer(question, context)` with the chunks from step 3.
6. `report_ticket` / `compose_sources` — write the answer from the tool payload, and from the RAG answer when both sources ran.

Conditional edges:

- Empty or invalid question → `refuse_empty`. Retrieval and the tool do not run.
- Ticket wording, and no policy wording → `lookup_ticket` only.
- Policy wording, and no ticket wording → `retrieve_context` only.
- Both signals → `lookup_ticket`, then `retrieve_context`.
- No chunk above the threshold → `insufficient_context`. Generation does not run.
- Tool timeout, error, missing token, or unknown id → an honest sentence. No status is invented.

`query()` is not a node. The state is `question`, `context`, `answer`, `error`, `status`, `route`, `sources`, and `ticket`. There is no conversation history.

The ticket tool lives in `services/api/app/agent/tools/tickets.py`. See `agents/tools/README.md`.

```bash
uv run python -m pytest tests/pipelines/test_agent_graph.py tests/pipelines/test_agent_routing.py
PYTHONPATH=services/api:. uv run python -m app.agent.export_trace
PYTHONPATH=services/api:. uv run python -m app.agent.export_compare
```

Live generation needs `GENERATION_MODEL_ID`, `GENERATION_BASE_URL`, and `GENERATION_API_KEY`, and retrieval against the remote embedder needs `EMBEDDING_*`. The recorded live run is `evidence/llm-live/`: 22 passed, 0 skipped, and `POST /agent/query` returned HTTP 200 with `receive_question` → `route_sources` → `retrieve_context` → `generate_answer`. That trace is the first run of `docs/langgraph/trace-full-run.json`. This checkout still skips the live eval when those variables are empty. A stand-in does not pass that criterion. The ticket column reads an incident the manager stored.

> _Spanish version: [README.es.md](./README.es.md)._
