# Nexova Agent Entry Point

This repository is the cumulative Nexova Solutions company monorepo used across 4Geeks milestones.

## Session startup — required
At the start of every coding session:
1. Read `memory-bank/projectbrief.md`.
2. Read `memory-bank/techContext.md`.
3. Read `memory-bank/progress.md`.
4. Read `noema.project.yaml` and classify the task as `patch | build | audit | research | architect | recover`.
5. Load only the additional required context for that mode plus the files directly affected by the task.

`AGENTS.md` is an entry map. Exact project context routing lives in `noema.project.yaml`.
For the current 4g-006 RC0 bridge, read `docs/noema/c05-work-order.yaml` and `docs/noema/c05-handoff.yaml`; the academic review stays with Nexova and Control Tower.

## Namespace boundary
- `.agents/` = instructions/rules/skills for coding agents working **on this repository**.
- `agents/` = Nexova product/business agents.
- `skills/` = Nexova product/runtime reusable capabilities.
Do not move content across these namespaces merely because names are similar.

## Mandatory workflow before every commit
1. **Scope check** — confirm changed files are inside the approved task and inspect the diff for unrelated edits.
2. **Context check** — confirm the implementation still agrees with `CONTEXT.md`, current Memory Bank state, relevant README conventions, and any applicable ADR/source record.
3. **Validation check** — run every applicable structural, type/lint, test, build and runtime check for the affected surface; do not infer PASS from unexecuted checks.
4. **Evidence check** — record the commands/results or other evidence needed to support the task/rubric claims and identify any stale evidence caused by the change.
5. **Delivery check** — verify branch, changed paths and required artifacts; update `memory-bank/progress.md` when the commit changes meaningful project state.

A commit is not ready if a required check is `FAIL` or `UNVERIFIED`.

## Protected paths / changes
Coding agents must obtain explicit developer confirmation before:
- modifying `CONTEXT.md` company facts;
- changing `docs/00-meta/PROJECT_PRINCIPLES.md` locked principles;
- changing authority boundaries in `noema.project.yaml`;
- resolving an open source conflict in `docs/domain/SOURCE_MANIFEST.yaml`;
- deleting or renaming top-level template folders;
- introducing a database, queue/event bus, persistent agent runtime, vector database/RAG layer, knowledge graph, microservice split, or other material architecture expansion;
- changing secrets, credentials, deployment ownership, destructive migrations, or irreversible external effects.

## Core development rules
- Read the README in any top-level folder before creating implementation inside it.
- Preserve 4Geeks rubric requirements exactly before adding optional extensions.
- Prefer deterministic logic for deterministic business rules.
- Do not present historical strategy/blueprints as current product roadmap.
- Do not claim live data when the UI is showing source baselines, policies, or demonstration data.
- Reuse shared code only after real duplication/reuse appears; do not create speculative abstractions.
- Noema conformance is structural evidence, not product/rubric quality evidence.
- Keep durable coordination in repository artifacts, not only in chat.
