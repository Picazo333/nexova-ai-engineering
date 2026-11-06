# Nexova 038 live verification
Date: 2026-11-06 12:35 CST (America/Mexico_City).
HEAD: 70dd6b4c8154ef532d958052064fe0913f64d829, confirmed equal to origin/feature/rag-knowledge-base after git fetch origin.
Detached worktree: /workspace/llm-run/wt-70dd6b4.

## Commands and results
Environment: source /workspace/llm-run/env038.sh. No key values printed or persisted. Same existing Qdrant index and unchanged live configuration as 2d04ec7; no reindex required. Temporary venv symlinks reused from wt-969556d and removed after verification. Eval, API, and extra retrieval diagnostic ran sequentially, with no Qdrant lock contention.
- `uv run python -m pytest tests -v`: 28 passed, matching claim. Unit tests are not proof of live inference.
- `cd services/api && uv run pytest`: 123 passed, matching claim.
- `uv run python -m data.eval.recall_at_3`: exit 0, remote embeddings, 27/27 (100%), no misses; all 27 also covered at configured min_score 0.4. Full per-question report in recall-report.json.
- API: `PYTHONPATH=.:packages:services/api JWT_SECRET=<ephemeral> ACCESS_TOKEN_EXPIRE_MINUTES=30 services/api/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 18038`. Readiness GET /conocimiento. Same five sequential POST /knowledge/query questions as prior run. Full status, answers and logs in 04-knowledge-query-live.txt.

## Live query verdicts
All five returned HTTP 200 on attempt 1; no retries needed.
1. Fee and discount: PASS; 22%, Marcos Ibáñez approval, explicit pricing-model and objection-handling citations.
2. Training price and contents: PASS; from 6.200 USD, up to 15 people, diagnosis, live sessions, certificate; pricing-model and service-lines citations.
3. Executive timing and escalation: PASS; average 8 weeks, 3 candidates; at 4 weeks without qualified candidate escalate to Javier Almeida and proactively notify client with action plan; hiring-process-sla citations.
4. World Cup 2098: PASS honest abstention. Additional live retrieve diagnostic after API shutdown returned zero chunks using configured top_k/min_score; no irrelevant chunks promoted. Exact diagnostic command appended to 04.
5. Minimum support team: PASS; five agents, service-lines and pricing-model citations.

## Safety and discrepancies
Secret scan covers diff origin/main...HEAD and every new evidence file including this README, exact environment secret values plus JWT/provider-key patterns. http-transcript.txt has zero eyJ occurrences. See 05-secret-scan.txt. No source edits, push, merge or LMS.
The recall evaluation generated its ignored recall-report.json in the worktree, copied here masked. The only operational deviations were using python3 for the external orchestration runner (python is not on box PATH), the optional fee retries (not needed), and the extra requested World Cup retrieval check. Same test commands and evidence layout as prior verification.
Non-failing diagnostic: QdrantClient destructor emits ImportError: sys.meta_path is None at Python shutdown in eval and standalone diagnostic; both exit 0. No test-count discrepancies or live correctness failures.
