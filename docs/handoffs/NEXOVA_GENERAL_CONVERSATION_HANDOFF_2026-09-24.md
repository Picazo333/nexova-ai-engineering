# Nexova — General Conversation Handoff

**Date:** 2026-09-24  
**Purpose:** start a new conversation that manages the overall Nexova / 4Geeks program without absorbing the website art-direction workstream.

## Read first

1. `CURRENT_EXECUTION_STATE.yaml`
2. `PROJECT_STATE.md`
3. `docs/design/premium-pass/ACTIVITY_METAPLAN.md`
4. Control Tower branch `assignment/4g-006-ai-driven-engineering` when rubric evidence is needed
5. Existing PR #1: https://github.com/Picazo333/nexova-ai-engineering/pull/1

## Scope of this conversation

Own:
- overall 4g-006 state machine;
- academic/rubric integrity;
- website/backoffice/foundation/integrated-QA sequencing;
- PR/submission state;
- cross-workstream dependencies;
- coordination with the forthcoming transversal Noema version.

Do **not** own:
- website art direction;
- A1/A2 visual decisions;
- composition frames;
- v0 runtime visual prototype;
- Figma H2 V2 decisions.

Those belong to the dedicated Website Visual Recovery conversation.

## Current macro state

```text
S0 ACADEMIC_BASELINE_PASS      ✅
S1 WEBSITE_PREMIUM_PASS       ← ACTIVE / delegated visual workstream
S2 BACKOFFICE_PREMIUM_PASS    not started
S3 NEXOVA_FOUNDATION_PASS     not started
S4 INTEGRATED_QA_PASS         not started
S5 RUBRIC_REFRESH_PASS        not started
S6 FINAL_PR_READY             not started
S7 USER_APPROVED              not started
S8 SUBMITTED                  not submitted
S9 DIDACTIC_PASS              not started
S10 HARVEST_COMPLETE          not started
```

Academic baseline:
- Control Tower recorded 22/22 blocking PASS on the academic baseline;
- required branch: `feature/agent-memory-bank`;
- required PR #1 is open against `main`;
- final 22/22 must be rerun at S5 after website + backoffice + integrated QA;
- do not create a replacement academic PR.

## Current dependency

General Nexova execution is intentionally waiting on:
`WEBSITE_PREMIUM_PASS`.

Do not begin S2 merely because the technical website baseline builds.  
The website visual workstream must first close H3.

## Noema boundary

A new transversal Noema version is about to be incorporated.

Rules:
- Noema may consume this checkpoint and coordinate workflow/conformance;
- Nexova repo state remains domain authority;
- Noema must not reconstruct locks from chat history;
- Noema must not reopen approved product/academic decisions without current evidence;
- always verify live repo state before mutating strategy.

## Next general action

Wait for the visual conversation to set:
`WEBSITE_PREMIUM_PASS = true`.

Then execute:
S2 Backoffice → S3 Foundation → S4 Integrated QA → S5 final R01–R22 → update PR #1 → visible audit → user Campus submission → didactic/harvest.

## Start prompt for the new conversation

> Continue Nexova general orchestration from repository `Picazo333/nexova-ai-engineering`. Do not reconstruct state from chat memory. Read `CURRENT_EXECUTION_STATE.yaml`, `PROJECT_STATE.md`, and `docs/design/premium-pass/ACTIVITY_METAPLAN.md` first. Treat the dedicated website visual-recovery workstream as separate authority for S1 visual execution. Current macro gate is S1 WEBSITE_PREMIUM_PASS; academic baseline remains 22/22 on `feature/agent-memory-bank` with PR #1 open, but final rubric refresh is S5. A new transversal Noema version may coordinate but must not override current Nexova repo state.
