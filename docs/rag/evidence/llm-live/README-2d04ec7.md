# Nexova 038 live verification
Date: 2026-11-06 12:23 CST (America/Mexico_City).
HEAD: 2d04ec709d53cb60dbe38410f2c96a1eb8ce5903, confirmed equal to origin/feature/rag-knowledge-base after git fetch origin.
Detached worktree: /workspace/llm-run/wt-2d04ec7.

## Commands and results
Environment sourced from /workspace/llm-run/env038.sh, unchanged EMBEDDING_*, GENERATION_* and QDRANT_PATH. Reused existing local Qdrant index; no reindex required. Existing 969556d virtual environments reused through temporary symlinks (removed after verification).
- `uv run python -m pytest tests -v`: 25 passed, matching claim. Unit tests are not proof of live inference.
- `cd services/api && uv run pytest`: 123 passed, matching claim.
- `uv run python -m data.eval.recall_at_3`: exit 0, remote embeddings, 26/27 (96.30%), 26 above configured min_score 0.4. Threshold 0.8 met, but NOT 27/27.
- Sole miss: es-compound-fee-and-discount. Top 3 sources: service-lines, objection-handling, service-lines; pricing-model missing. All other 26 IDs hit; JSON contains per-question outcomes and requires all expected needles for compound questions.
- API command and full sequential status/bodies: 04-knowledge-query-live.txt. PYTHONPATH=.:packages:services/api, ephemeral JWT_SECRET, ACCESS_TOKEN_EXPIRE_MINUTES=30, services/api/.venv/bin/uvicorn app.main:app --port 18038. Readiness: GET /conocimiento 200. API started only after eval exited, then stopped cleanly.

## Live query verdicts
1. Fee + discount: HTTP 502, FAIL. Initial APITimeoutError, then incomplete generation finish_reason=length chars=0; no answer, no 22%, Marcos Ibáñez or pricing-model citation. Incomplete-output guard works; required business answer does not pass.
2. Training price + contents: HTTP 200, PASS: from 6.200 USD, up to 15 participants, diagnosis/live sessions/certificate; cites pricing-model and service-lines.
3. Executive time + escalation: HTTP 200, PASS: average 8 weeks, 3 candidates; at 4 weeks without qualified candidate escalate to Javier Almeida and proactively notify client with action plan; cites hiring-process-sla.
4. World Cup 2098: HTTP 200, PASS honest abstention.
5. Canonical minimum team (English): HTTP 200, PASS 5 agents, service-lines citation.

## Safety and scope
Exact environment secret-value scan plus JWT and provider-key patterns: zero hits in diff origin/main...HEAD and new evidence. http-transcript.txt contains zero eyJ occurrences. Secret values are masked before evidence writes; no raw diff persisted. See 05-secret-scan.txt.
No source changes, push, merge or LMS actions. Eval generated its ignored recall-report.json in the worktree; masked report copied here. No claim that the compound-fee repair is complete: live retrieval still misses pricing-model and the endpoint failed this run.
