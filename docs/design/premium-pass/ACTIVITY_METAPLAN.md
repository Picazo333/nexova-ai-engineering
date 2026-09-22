# 4g-006 / Nexova Premium Extension Metaplan

**Status:** APPROVED  
**Academic status at approval:** 22/22 blocking criteria PASS, READY_TO_SUBMIT, not submitted.  
**Existing academic PR:** #1, `feature/agent-memory-bank -> main`.

## Macro state machine

```
S0 ACADEMIC_BASELINE_PASS
 ↓
S1 WEBSITE_PREMIUM_PASS
 ↓
S2 BACKOFFICE_PREMIUM_PASS
 ↓
S3 NEXOVA_FOUNDATION_PASS
 ↓
S4 INTEGRATED_QA_PASS
 ↓
S5 RUBRIC_REFRESH_PASS
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

## S0 — Preserve academic state

Current academic state is not considered visually final, but it remains the recovery path.

No academic evidence is invalidated until premium changes are reintegrated into the required assignment branch.

## S1 — Website Premium Pass

Execute the approved `PREMIUM_WEBSITE_EXECUTION_PLAN.md`.

Output:
`WEBSITE_PREMIUM_PASS`.

## S2 — Backoffice Premium Translation

Translate the final website visual language into an Operate surface.

Reuse:
- color;
- typography;
- line/border language;
- tokens;
- interaction grammar.

Reduce:
- artwork;
- ornament;
- motion;
- narrative scrolling;
- atmospheric effects.

Increase:
- density;
- scanability;
- consistency;
- data hierarchy.

Use Mobbin as the dominant reference source.

Canonical surfaces:
1. Overview
2. Table/Data
3. Form/Detail

No GSAP/Spline in backoffice by default.

Output:
`BACKOFFICE_PREMIUM_PASS`.

## S3 — Nexova Foundation Consolidation

Only after two real surfaces exist, extract shared architecture.

A primitive/component is shared only if:
- actual reuse exists across >=2 relevant consumers, or
- it is a stable canonical token/foundation.

Website-specific hero/motion remains local.

Activate Storybook only if >=5 genuinely reused components with meaningful states make isolated documentation/testing worthwhile.

Output:
`NEXOVA_FOUNDATION_PASS`.

## S4 — Integrated QA

Run monorepo-wide:
- structural checks;
- install;
- typecheck;
- website build;
- backoffice build;
- both runtimes;
- browser QA;
- axe;
- keyboard/focus;
- reduced motion;
- performance;
- content provenance;
- dependency audit.

Output:
`INTEGRATED_QA_PASS`.

## S5 — Rubric refresh

Fresh evidence is mandatory for any criterion affected by frontend/architecture changes.

Expected fresh verification:
- R12–R17
- R19
- R21

All R01–R22 are nevertheless reviewed as a grader.

Target:
`22/22 blocking PASS` on the final implementation commit.

Control Tower receives new commit/evidence/state; it does not become visual authority.

Output:
`RUBRIC_REFRESH_PASS`.

## S6 — Update existing PR #1

Do not open a second academic PR.

Update the existing required PR with:
- current website screenshot;
- current backoffice screenshot;
- AGENTS.md link;
- final validation evidence.

PR CI must pass on the exact final head.

Output:
`FINAL_PR_READY`.

## S7 — Final visible audit

Show user:
- desktop website;
- mobile website;
- backoffice;
- signature motion;
- accessibility/performance summary;
- red-team summary;
- dependency audit;
- fresh 22/22 rubric;
- exact PR URL.

Output:
`USER_APPROVED`.

## S8 — Submission

Only user performs the external Campus submission.

Do not mark submitted until user confirms.

## S9 — Didactic protocol

After submission produce:
- MASTER_STUDY.md
- DEFENSE_QA.md
- CHEAT_SHEET.md
- TROUBLESHOOTING.md
- NotebookLM prompts
- presentation if requested

Output:
`DIDACTIC_PASS`.

## S10 — Harvest

Only after delivery/learning.

Classify each lesson:
- LOCAL_NEXOVA
- CONTROL_TOWER
- NOEMA_CANDIDATE
- SKILL_FOUNDRY_CANDIDATE
- PROTOCOL_UPDATE
- NO_ACTION

Never export Oni Nocturne, company-specific copy/assets, or project-specific implementation as generic capability.

No Noema/Skill Foundry feature is implemented during the academic execution merely because a candidate was discovered.

Output:
`HARVEST_COMPLETE`.
