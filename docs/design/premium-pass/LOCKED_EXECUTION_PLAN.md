# Nexova / 4Geeks 4g-006 — Locked Execution Plan

**Status:** EXECUTION LOCK / AUDIT RECONCILED  
**Date:** 2026-09-23  
**Current cursor:** S1 Website Premium Pass → Visual Intent Recovery Work Order  
**Change policy:** No phase/tool is added unless a current gate cannot be satisfied with the approved toolchain.  
**Independent audit:** `docs/design/premium-pass/reviews/INDEPENDENT_PROCESS_AUDIT_2026-09-23.md`

## Authority and state model

Normative authority:
1. 4Geeks rubric / assignment contract;
2. Product Truth;
3. identity + direction + asset contracts;
4. Figma H2 Golden;
5. repository architecture;
6. this locked execution plan.

Advisory evidence:
- v0 Challenger Review;
- Independent Process Audit.

Validation evidence:
- GitHub Actions;
- deterministic browser QA;
- axe;
- Lighthouse;
- Vercel deployment/runtime evidence.

**Current-state authority:** `PROJECT_STATE.md` + `H3_EVIDENCE_MATRIX.md`.  
Historical narrative documents are not executable current-state instructions.

## Position in the global activity

```text
S0 ACADEMIC_BASELINE_PASS          ✅
 ↓
S1 WEBSITE_PREMIUM_PASS           ← CURRENT
    H1 Direction Approval         ✅
    H2 Figma Golden Lock          ✅
    v0 Challenger                 ✅ CLOSED
    G0 Production Preflight       ✅
    Codex Production Work Order   ✅
    Deterministic QA              ✅
    Independent Red Team          ✅
    Bounded Repair                ✅
    H3 Runtime Approval           ⏳ VERCEL + HUMAN APPROVAL
 ↓
S2 BACKOFFICE_PREMIUM_PASS
 ↓
S3 NEXOVA_FOUNDATION_PASS
 ↓
S4 INTEGRATED_QA_PASS
 ↓
S5 RUBRIC_REFRESH_PASS (22/22)
 ↓
S6 FINAL_PR_READY
 ↓
S7 USER_APPROVED
 ↓
S8 SUBMITTED
 ↓
S9 DIDACTIC_PASS
 ↓
S10 HARVEST_COMPLETE
```

## Audit reconciliation lock

The independent process audit is **advisory**, not a replacement authority. The following recommendations are accepted and locked because they improve the existing plan without changing H1/H2/Product Truth or repository architecture:

1. **Codex remains production owner.**
2. Static fidelity, responsive translation, runtime assets and signature motion are treated as **one Codex Production Work Order with internal checkpoints**, not four user-governed phases.
3. Final sequence is:
   `DETERMINISTIC QA → INDEPENDENT RED TEAM → ONE BOUNDED REPAIR → H3`.
4. A second repair batch is allowed only for a remaining material failure.
5. H3 requires:
   - P0 = 0;
   - P1 = 0;
   - P2 = 0, or any surviving P2 explicitly dispositioned by the human owner as non-material.
6. v0 is closed by default and remains advisory only.
7. State drift is prohibited: one authoritative cursor per scope; changelog/history cannot override current flags.
8. New variable-cost tools require a live unresolved gate, unique expected value, bounded budget and stop condition.

## Completed production work order

### Checkpoint 1 — Static fidelity
PASS.

### Checkpoint 2 — Responsive translation
PASS at 1440 / 1024 / 768 / 430 / 390.

### Checkpoint 3 — Runtime assets
PASS. Heavy A1/A2 masters are not the default runtime payload.

### Checkpoint 4 — Signature motion
PASS against the approved REST → SEPARATE → YIELD → RELEASE narrative with readable reduced-motion/no-JS states.

### Deterministic QA + Red Team + bounded repair
PASS internally on candidate `f10cd71572ea3b5883b9bf746f48d4cb04afbc36`.

Evidence:
- GitHub Actions run `35929968292`: PASS;
- horizontal overflow: 0 at required widths;
- console/runtime errors: 0;
- keyboard/focus/mobile navigation: PASS;
- no-JS: PASS;
- reduced motion: PASS;
- axe: 0 critical / 0 serious / 0 total violations;
- Lighthouse: performance 0.96, accessibility 1.00, LCP 2.5 s, CLS 0.061, TBT 0 ms;
- open P0/P1/P2 internal findings: 0.

## Current H3 gate

H3 is **not yet approved**.

Remaining requirements:
1. produce a reachable Vercel preview for the exact production candidate;
2. verify the deployed runtime;
3. present desktop/mobile/runtime evidence and QA summary to the user;
4. receive explicit human H3 approval.

Current external blocker:
- GitHub Vercel integration is deploying through historical project `nexova-premium-v0-challenger`;
- Vercel authorization/team scope must be corrected before deployment evidence can pass.

No new design exploration, v0 generation, Spline, SuperDesign or image generation is authorized for this blocker.

## After H3

1. declare `WEBSITE_PREMIUM_PASS`;
2. move to S2 Backoffice Premium Pass;
3. translate the locked website visual language into the Operate surface;
4. S3 consolidate only evidence-backed shared primitives;
5. S4 run integrated QA across website + backoffice;
6. S5 rerun the authoritative Control Tower rubric R01–R22 against the final assignment implementation;
7. update existing PR #1 from `feature/agent-memory-bank` to `main`;
8. final visible audit;
9. user performs Campus submission;
10. didactic packaging and harvest.

## 4Geeks rubric sequencing lock

The academic baseline already has a recorded 22/22 PASS, but the **final premium implementation refresh** belongs to S5.

Do not claim final 22/22 at website-only H3 because:
- R18 requires final assignment work on `feature/agent-memory-bank`;
- R20 requires PR #1 from that branch to `main`;
- R21 requires final website + backoffice screenshots in the PR.

The website H3 validates website-impacting criteria only; final academic closure happens after S2–S4.

## Cost lock

For the remainder of S1:
- v0 calls: 0 by default;
- Figma mutations: only for a genuine H2 ambiguity;
- image generation: 0 by default;
- Spline: SKIP;
- SuperDesign: SKIP;
- GSAP: only the approved signature sequence;
- Codex/GitHub/CI/Vercel handle implementation and verification.

Any new variable-cost tool requires:
- unresolved gate;
- unique expected value;
- cheaper alternatives ruled out;
- explicit bounded budget;
- stop condition.


## Visual Intent Recovery incorporation — 2026-09-23

H3 human review supplied new material evidence: the deployed runtime does not yet carry the approved visual intent.

Execution is now governed by:
`docs/design/premium-pass/VISUAL_INTENT_RECOVERY_WORK_ORDER.md`

This is a bounded recovery of the existing lock, not a redesign.


## VIR internal candidate validated — 2026-09-24

Candidate `f4f7a083ef0907e69eca3a9f53ac8c220a94327d` passes all deterministic recovery gates and Vercel deployment.

The remaining gate is deliberately human:
- judge whether the bounded A1 reconstruction and runtime motion recover the approved visual impact;
- if accepted, close H3 and proceed to S2;
- if rejected, repair only the identified material visual failure. No new visual route is unlocked.
