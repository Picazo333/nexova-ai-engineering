# Nexova Project State

**Status:** DELIVERY LOCK ACTIVE  
**Updated:** 2026-09-24  
**Current milestone:** 4g-006 — AI-driven Engineering  
**Working branch:** `feature/agent-memory-bank`  
**Pre-milestone baseline:** `3837eb3b943655d8cfb3131e43258cada0fd8871`

## Current objective
Deliver the 4Geeks AI-driven Engineering milestone with the human-approved Nexova website, the validated backoffice, the required agent-development infrastructure, and evidence-backed delivery state.

## Current phase
**FINAL DELIVERY VALIDATION / PR #1**

## Locked website delivery
The website selected by the user for the activity is the v0 visual-sandbox implementation now integrated under `/uis/website`.

Authoritative lock:
- `docs/evidence/4g-006/WEBSITE_DELIVERY_VISUAL_LOCK.md`
- `docs/evidence/4g-006/V0_APPROVED_SOURCE_MANIFEST.json`

Approved source:
- v0 chat: https://v0.app/mbpicazo33-1986/chat/nexova-visual-sandbox-n0o4weQLsCq
- source ZIP SHA-256: `211874809bebc6dcb71eaeaf804b4a86b92a443f37d9b7dfb672319d44a4b329`

The five committed visual assets are byte-identical to the approved source ZIP.

### No-regression rule
No visual redesign, asset substitution, typography reinterpretation, composition change, or motion redesign is permitted without explicit human reapproval.

Only bounded fixes for factual correctness, rubric compliance, accessibility, responsive defects, performance, build/runtime, or deployment are allowed.

## Current implementation
- website: Next.js 16 + React 19 + Tailwind 4 + GSAP/ScrollTrigger under `uis/website`;
- backoffice: independent app under `uis/backoffice`;
- root npm workspace preserved;
- Noema RC0 bridge integrated without taking ownership of Nexova domain/runtime state;
- existing PR #1 remains the only academic delivery PR.

## Current validation
Validated website/backoffice implementation commit:
`514ab22f20a315e5759e23097bfaa38aa97cef2a`

Successful GitHub Actions:
- push validation: `36085463496`;
- PR validation: `36085466018`;
- Noema conformance: `36085466652`.

Validated:
- dependency installation;
- TypeScript typecheck;
- production builds;
- website and backoffice runtime smoke;
- browser DOM assertions;
- complete rendered screenshots;
- evidence upload;
- Noema structural conformance.

The current branch head may include a subsequent bot evidence commit produced by the successful workflow; such an evidence-only commit does not change application code.

## Academic delivery state
- R01–R22 baseline contract exists in Control Tower.
- Required branch: `feature/agent-memory-bank`.
- Required PR: https://github.com/Picazo333/nexova-ai-engineering/pull/1
- PR base: `main`.
- Final campus artifact is PR #1.
- Campus submission remains a user action.

## Source issue
The historical source set contains a conflict over the Sales department leader (Megan Clarke vs Marcos Ibáñez). Treat the contested identity as unresolved until a governing source settles it.

## Remaining gates
1. run final CI on this reconciled delivery state;
2. confirm PR #1 contains current website/backoffice evidence and AGENTS link;
3. perform final visible rubric/delivery audit;
4. user submits PR #1 URL in Campus.

## Not required for academic lock
The historical Vercel project `nexova-premium-v0-challenger` is misconfigured for this monorepo and currently reports failed deployments. This does not invalidate the 4Geeks runtime evidence because GitHub Actions independently builds and renders both apps successfully. Public production publishing can be repaired separately without changing the locked website design.
