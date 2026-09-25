# 4g-006 — Final Delivery Check

**Branch:** `feature/agent-memory-bank`  
**PR:** https://github.com/Picazo333/nexova-ai-engineering/pull/1  
**Locked website source:** v0 visual sandbox  
**Source ZIP SHA-256:** `211874809bebc6dcb71eaeaf804b4a86b92a443f37d9b7dfb672319d44a4b329`

This file records the mandatory AGENTS.md scope/context/validation/evidence/delivery workflow for the final locked website implementation.

## 1. Scope check
PASS.
- Work remains inside 4g-006 scope.
- Existing Nexova monorepo is preserved.
- Website remains under `/uis/website`.
- Backoffice remains under `/uis/backoffice`.
- No speculative backend/database/RAG/runtime infrastructure was introduced.
- Noema RC0 remains a coordination/conformance layer, not product authority.

## 2. Context check
PASS.
- Website remains grounded in approved Nexova context.
- Unsupported trademark glyph, stale copyright year and unsupported location copy from the raw v0 export were removed/corrected as bounded factual adaptations.
- The unresolved Sales-leader identity is not published as uncontested fact.
- Human-approved visual composition is locked against redesign.

## 3. Validation check
PASS for implementation commit `514ab22f20a315e5759e23097bfaa38aa97cef2a`.

- push run `36085463496`: SUCCESS;
- PR run `36085466018`: SUCCESS;
- Noema conformance run `36085466652`: SUCCESS.

Checks passed:
- install;
- typecheck;
- build;
- website runtime;
- backoffice runtime;
- DOM assertions;
- browser evidence;
- evidence upload.

## 4. Evidence check
PASS.
- `docs/evidence/4g-006/website.png`
- `docs/evidence/4g-006/backoffice.png`
- `docs/evidence/4g-006/AUDIT.md`
- `docs/evidence/4g-006/WEBSITE_DELIVERY_VISUAL_LOCK.md`
- `docs/evidence/4g-006/V0_APPROVED_SOURCE_MANIFEST.json`

## 5. Delivery check
PASS subject to final reconciled CI.
- required branch: `feature/agent-memory-bank`;
- target: `main`;
- required PR: #1;
- PR must contain website screenshot, backoffice screenshot and direct `AGENTS.md` link;
- exact PR #1 URL is the Campus submission artifact.

## Visual lock
Any post-lock visual redesign, asset substitution, typography reinterpretation, composition change or motion redesign requires explicit human reapproval.

**Delivery readiness:** run final reconciled CI, then final visible audit. Campus submission remains user-controlled.
