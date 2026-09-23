---
status: independent_review_complete
owner: meta
created: 2026-09-23
authority: audit_only
execution_effect: none
source_branch: design/oni-nocturne-premium-pass
---
# Nexova Premium Website — Independent Process Audit

## Scope

Audit the workflow used to move an already-valid 4Geeks academic baseline toward a premium website. This document proposes process changes only. It does not implement code or mutate Figma.

## Executive diagnosis

The strongest part of Nexova is its authority chain:

`academic baseline -> Product Truth -> Direction/Asset Contracts -> H1 -> Figma H2 Golden -> production -> runtime evidence -> H3`

The main waste came from over-broad tool planning, variable-cost challenger usage and mutable state repeated inside narrative documents.

The current locked plan is already much better than the original 19-phase premium plan. Further improvement should compress governance and handoffs, not redesign the workflow again.

## KEEP

### Academic recovery baseline
Premium work is isolated and the validated delivery can be recovered without reconstruction.

### Product Truth
Prevents design/copy/code tools from presenting future-state concepts or fabricated proof as current facts.

### Direction + Asset Contracts
They were necessary because earlier visual generation changed artifact type, literalness and candidate independence.

### H1 / H2 / H3
The three human gates map to materially different subjective decisions:
- H1 direction;
- H2 canonical Figma Golden;
- H3 final runtime acceptance.

### Figma H2 Golden
After H2, Figma is visual normative authority. Implementation may reveal feasibility issues but does not silently redesign.

### Codex as production owner
The real repo, locked stack and deterministic test loop make Codex the correct default production executor.

### Runtime Asset Delivery Contract and H3 Evidence Matrix
Both create observable verification tied to a candidate implementation.

## REMOVE / DEFER

### v0 as a standard pipeline stage
The existing v0 spend produced useful mechanics, including responsive image delivery and progressive-enhancement principles, but these were not exclusive to v0. It also incurred environment/import friction, generic motion and legacy-section residue.

For the current activity: no more v0 calls.

For future work: v0 is optional only for one unresolved front-end question after an approved Figma and a baseline implementation exist.

### Spline / SuperDesign / additional visual tools by default
No demonstrated gap justifies them.

Tool inventory must not become execution plan.

## MODIFY — production execution

Do not treat static desktop, responsive translation, runtime assets and motion as four human-governed phases.

Use one Codex Production Work Order with internal checkpoints:

```text
CHECKPOINT 1 static fidelity
CHECKPOINT 2 responsive translation
CHECKPOINT 3 runtime assets
CHECKPOINT 4 signature motion
FINAL candidate for QA
```

The executor can continue between checkpoints while:
- scope remains stable;
- tests are interpretable;
- no visual-authority ambiguity appears;
- no new paid tool is required.

Escalate to the human only for material design deviation, scope change or unresolved authority conflict.

## MODIFY — H3 sequence

Current reduced plan places independent red team after H3.

Recommended:

`QA -> RED TEAM -> BOUNDED REPAIR -> H3`

H3 should approve the adversarially reviewed runtime, not a provisional candidate.

## MODIFY — P2 findings

H3 should require:
- P0 = 0;
- P1 = 0;
- P2 = 0 **or** each surviving P2 explicitly dispositioned as non-material by the human owner.

No silent P2 backlog at H3; no endless polishing loop either.

## State drift

Observed examples:
- `FIGMA_GOLDEN_STATUS.md` contains historical states where v0 is both disallowed/complete and later allowed.
- `V0_CHALLENGER_EVAL.md` remained ACTIVE while the review declares the phase CLOSED.
- `PROJECT_STATE.md` contains sequential status narratives understandable to a human but risky as current instructions for an agent.

Fix:
- one authoritative current cursor per scope;
- historical events/changelog separate from current flags;
- contracts must not act as mutable state logs.

## Authority model

Separate:
1. normative authority: rubric, Product Truth, identity/direction, Figma, architecture;
2. advisory evidence: challenger reviews;
3. validation evidence: runtime, CI, accessibility/performance.

A challenger does not outrank repository architecture merely because it appears earlier in a list.

## Cost-control model

Evaluate each nontrivial run using a vector, not a fake aggregate score:

- context/tokens;
- direct tool cost;
- human interventions;
- wall time;
- retries/rework;
- downstream reuse;
- uncertainty reduced.

Stop-loss:
- generative/variable-cost tool: one initial + one targeted repair;
- premium challenger: one bounded question + one optional repair;
- after two correctly executed failures: stop and classify the failure before changing tools.

## Optimized workflow

```text
ACADEMIC BASELINE
      ↓
PRODUCT / DIRECTION
      ↓
H1
      ↓
FIGMA GOLDEN
      ↓
H2
      ↓
G0 PRODUCTION PREFLIGHT
      ↓
CODEX PRODUCTION WORK ORDER
      ↓
DETERMINISTIC QA
      ↓
INDEPENDENT RED TEAM
      ↓
ONE BOUNDED REPAIR BATCH
      ↓
H3
      ↓
WEBSITE PREMIUM PASS
```

A second repair batch is allowed only for a remaining material failure.

## Reusable harvest

Strong cross-project candidates:
- capability authorization by active question;
- run economics/telemetry;
- scoped state authority;
- bounded agent work orders;
- challenger-as-advisory semantics;
- red team before final human acceptance.

Do not generalize Nexova-specific H1/H2/H3 naming, Oni visual rules, exact widths, or v0 as a standard tool.
