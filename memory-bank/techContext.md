# Technical Context

## Repository model
This is a cumulative company monorepo created from the official 4Geeks AI Engineering company-project template.

Top-level placement follows the template:
- `uis/` — user interfaces;
- `services/` — centralized backend/API when required;
- `data/` — raw/process/pipelines/eval;
- `agents/` — Nexova product agents;
- `skills/` — Nexova product/runtime capabilities;
- `mcps/` — MCP servers;
- `workflows/` — orchestration;
- `packages/` / `shared/` — reusable code/assets;
- `infra/`, `scripts/`, `internal/` — operational/developer tooling.

Coding-agent configuration is deliberately separate under `.agents/`.

## Current milestone baseline
- Baseline commit: `3837eb3b943655d8cfb3131e43258cada0fd8871`
- Working branch: `feature/agent-memory-bank`
- Root company briefing already contains Nexova context.
- No application runtime existed at baseline.
- `packages/shared/package.json` exists, but no root workspace runner existed at baseline.

## Current architectural decisions
- One root Noema manifest; no nested project manifests.
- Progressive context loading; `AGENTS.md` routes, it does not duplicate all context.
- No backend is created until a real current requirement justifies it.
- No RAG/vector DB, event bus, persistent agent runtime, knowledge graph or advanced observability stack without an activation trigger.
- A root JavaScript workspace is a candidate because the current milestone requires two UIs; exact stack remains pending the workspace/frontend gate.
- Shared visual/code abstractions are extracted only after actual reuse between website/backoffice is observed.

## Quality baseline
Applicable changes should be validated across:
1. structure/paths;
2. syntax/types/lint;
3. tests;
4. production build;
5. runtime smoke;
6. accessibility/responsive/visual checks when UI is affected;
7. rubric evidence;
8. remote branch/PR state before submission.

## Known constraints
- 4Geeks rubric is the primary delivery constraint.
- Historical Nexova architecture ideas are inputs, not binding implementation decisions.
- The Sales-leader source conflict remains unresolved.
- Current Control Tower GitHub Actions have an external no-step runner failure; this does not change Nexova source/runtime validity.
