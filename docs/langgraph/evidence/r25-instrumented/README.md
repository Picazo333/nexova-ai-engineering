# R25 — real instrumented LangGraph run

Date: 2026-11-06 12:09 CST (America/Mexico_City, UTC-6).
Head: `c63c26f08cac9330263f4fdbb1c1f31a3f7e36bb` (PR #18).

Command (keys are sourced, never displayed):
```bash
source /workspace/llm-run/env038.sh
PYTHONDONTWRITEBYTECODE=1 /workspace/llm-run/wt-c63c26f/.venv/bin/python /workspace/ejecucion/039-ai-eng-langgraph-agent-base/evidence/r25-instrumented/run_trace.py
```

The external harness uses the repository's `compile_agent`, default retrieval and generation functions, real local Qdrant corpus, live remote embeddings and generation, and a fresh InMemorySaver per question. No fake functions, model responses, or status-inferred nodes. A UUID is passed as `config.run_id`, with a separate `configurable.thread_id`. The original questions come directly from `02-run-agent-live.json`.

`graph.stream(..., stream_mode=["updates", "debug"])` records actual task and task_result events, update payloads, state keys written and actually changed, retrieved context/source payloads, and final answers. Node timing uses debug timestamps and monotonic time between observed events: real observer-measured latency, not provider-only compute time. Raw framework debug timestamps retain their UTC offsets; run timestamps use America/Mexico_City. Real checkpoint IDs and metadata are read from `get_state_history(config)`, not invented. The checkpoints are in-memory snapshots exported to JSON, not durable database checkpoints.

A transparent observer around OpenAI Completions.create captures the real returned model and usage without changing the request or response. Generation model: `online/openrouter/deepseek/deepseek-v4-flash`; embedding model: `online/openrouter/perplexity/pplx-embed-v1-0.6b`; generation base URL: `https://llm.4geeks.ai/v1`.

## Results

- Fee run `8d1bc6df-340e-4f11-920e-dc8ff9d109c4`: receive_question → retrieve_context → generate_answer; 5 checkpoints; 4.513577 s overall. Node durations 0.000908 / 2.186414 / 2.323282 s. Correct: 22% fee, discount requires Marcos Ibáñez's approval. Actual provider generation usage: prompt 661, completion 293, total 954 (170 reasoning tokens included).
- Outside-corpus run `58100d65-a9a4-46e9-9adf-bfbe3deebc7f`: receive_question → retrieve_context → insufficient_context; 5 checkpoints; 0.578928 s overall. Node durations 0.000376 / 0.574653 / 0.002058 s. Honest Spanish refusal; generation model and usage null because generation was not called. Embedding usage is not collected by this harness; generation usage is not a whole-pipeline token total.

Provider optional token breakdown fields can be null when absent from response metadata. No estimates replace missing data. Run errors are empty. Process exited 0; Qdrant emitted a Python-shutdown destructor warning (`ImportError: sys.meta_path is None, Python is likely shutting down`) after successful export; it did not interrupt either graph run.

## Files

- `run_trace.py`: reproducible external harness.
- `trace-instrumented.json`: full observed debug/update events, node details and checkpoints.
- `trace-full-run.instrumented.json`: original export's envelope/run shape with measured fields, real IDs/checkpoints and additional instrumentation.
- `run.log`: sanitized structured execution summary.
- `secret-scan.json`: exact sensitive-environment-value and credential-pattern scan, PASS.

Outputs are sanitized against sensitive environment values before writing. No keys, authorization headers, or environment dumps are recorded. Repo was not edited; nothing was pushed, merged, deployed or sent to LMS.
