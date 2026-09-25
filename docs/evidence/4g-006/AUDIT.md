# 4g-006 — Final Delivery Audit Evidence

**Assignment:** AI-driven Engineering  
**Repository:** `Picazo333/nexova-ai-engineering`  
**Branch:** `feature/agent-memory-bank`  
**PR:** https://github.com/Picazo333/nexova-ai-engineering/pull/1  
**Pre-milestone baseline:** `3837eb3b943655d8cfb3131e43258cada0fd8871`

## Human visual lock
The user explicitly selected the v0 visual-sandbox website for final 4g-006 delivery.

Evidence:
- `WEBSITE_DELIVERY_VISUAL_LOCK.md`
- `V0_APPROVED_SOURCE_MANIFEST.json`
- source ZIP SHA-256: `211874809bebc6dcb71eaeaf804b4a86b92a443f37d9b7dfb672319d44a4b329`

The five website visual assets committed under `uis/website/public/nexova/` are byte-identical to the approved ZIP.

## Validated implementation
Application implementation commit:
`514ab22f20a315e5759e23097bfaa38aa97cef2a`

### Push validation
GitHub Actions run:
https://github.com/Picazo333/nexova-ai-engineering/actions/runs/36085463496

Result: **SUCCESS**

### PR validation
GitHub Actions run:
https://github.com/Picazo333/nexova-ai-engineering/actions/runs/36085466018

Result: **SUCCESS**

### Noema conformance
GitHub Actions run:
https://github.com/Picazo333/nexova-ai-engineering/actions/runs/36085466652

Result: **SUCCESS**

## Deterministic checks passed
1. dependency installation;
2. TypeScript typecheck;
3. production build for workspaces;
4. website dev runtime;
5. backoffice dev runtime;
6. website DOM assertions against approved delivery copy;
7. backoffice company-data assertions;
8. browser rendering;
9. complete website screenshot capture;
10. backoffice screenshot capture;
11. evidence artifact upload;
12. Noema conformance.

## Website assertions
Current runtime evidence verifies:
- `CRITERIO HUMANO`;
- `EL CRITERIO`;
- `LA ESTRUCTURA`;
- `VALENCIA`;
- `MIAMI`.

## Backoffice assertions
Current runtime evidence verifies:
- `Contexto operativo`;
- `48 h`;
- `SLA 24 h`;
- `40%`;
- `30–80`.

## Rendered evidence
- `docs/evidence/4g-006/website.png`
- `docs/evidence/4g-006/backoffice.png`

These are browser-generated from the integrated feature branch, not design mockups.

## Delivery integrity
- existing monorepo retained;
- website remains under `/uis/website`;
- backoffice remains under `/uis/backoffice`;
- required academic branch retained;
- existing PR #1 retained;
- no replacement assignment repository or PR created;
- visual source is locked against unapproved redesign.

## Known external limitation
The historical Vercel project `nexova-premium-v0-challenger` currently fails its automatic GitHub deployment because its project configuration is stale relative to the monorepo. This is a deployment-integration issue, not a website build/runtime failure: GitHub Actions independently proves the website and backoffice build and render successfully.

Vercel publishing is therefore **not used as academic PASS evidence**.

## Final audit rule
Do not declare Campus submission complete until:
- final reconciled branch validation is green;
- PR #1 remains open and valid;
- PR body contains current website screenshot, backoffice screenshot and AGENTS.md link;
- user submits the exact PR #1 URL.
