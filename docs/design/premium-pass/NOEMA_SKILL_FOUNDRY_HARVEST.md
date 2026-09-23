# Nexova Premium Extension — Noema / Skill Foundry Harvest Candidates

**Status:** CANDIDATE ONLY  
**Date:** 2026-09-23  
**Rule:** Nothing in this document is automatically canonized or implemented in Noema/Skill Foundry during the 4Geeks activity.

## Classification model

- **LOCAL_NEXOVA** — useful only for this project.
- **NOEMA_CANDIDATE** — orchestration/governance capability.
- **SKILL_FOUNDRY_CANDIDATE** — reusable bounded capability suitable for a skill.
- **PROTOCOL_UPDATE** — generic operating rule for 4Geeks/project delivery.
- **NO_ACTION** — lesson is real but not reusable enough.

---

## H01 — Premium Tool Cost Gate

**Classification:** NOEMA_CANDIDATE + SKILL_FOUNDRY_CANDIDATE + PROTOCOL_UPDATE

### Problem
A capable premium tool can be economically wrong for inspection/debugging work.

### Candidate contract
Inputs:
- task;
- candidate tool;
- expected unique value;
- cheaper alternatives;
- variable cost model;
- max calls/iterations;
- stop-loss threshold.

Output:
- USE;
- USE_BOUNDED;
- DEFER;
- REJECT;
- route to cheaper tool.

### Noema value
Add spend-aware routing and stop-loss policy to orchestration.

### Skill Foundry candidate
`premium-tool-gate`
Evaluates whether a paid/variable-cost tool call is justified before execution.

---

## H02 — External Generator Repository Preflight

**Classification:** SKILL_FOUNDRY_CANDIDATE + PROTOCOL_UPDATE

### Problem
v0 initially started from an unusable/empty workspace.

### Candidate contract
Verify before generation:
- repository;
- exact base branch;
- current branch;
- remote;
- root directory;
- package manifest;
- target workspace;
- governing instruction files;
- clean/expected state.

### Output
`PASS | FAIL | UNVERIFIED` with exact blocker.

### Skill candidate
`external-codegen-repo-preflight`

Applicable to:
- v0;
- Replit Agent;
- cloud IDE agents;
- hosted coding generators.

---

## H03 — Authority Graph / State Reconciliation

**Classification:** NOEMA_CANDIDATE + SKILL_FOUNDRY_CANDIDATE

### Problem
Old state blocks can contradict later approvals.

### Candidate contract
Input:
- authority documents;
- state files;
- milestone locks.

Detect:
- stale booleans;
- duplicate “next state” declarations;
- conflicting authorities;
- superseded gates.

Output:
- canonical current state;
- contradictions;
- safe repair patch.

### Noema value
A canonical state graph should be queryable before delegation.

### Skill candidate
`project-state-reconciler`

---

## H04 — Visual Artifact Contract Compiler

**Classification:** SKILL_FOUNDRY_CANDIDATE

### Problem
Image generation drifted when aesthetic prose was not translated into a strict artifact contract.

### Candidate contract
Translate creative direction into:
- artifact type;
- role;
- composition;
- safe zones;
- motif-legibility range;
- palette;
- materiality;
- forbidden readings;
- crop requirements;
- candidate budget;
- repair budget;
- rejection tests.

### Skill candidate
`visual-artifact-contract`

This should remain generator-agnostic.

---

## H05 — Independent Candidate / Repair Controller

**Classification:** SKILL_FOUNDRY_CANDIDATE

### Problem
Multiple generations can become minor variants rather than independent exploration.

### Candidate behavior
Modes:
- `EXPLORE`: candidates must be independent;
- `SELECT`: no generation;
- `REPAIR`: modify selected winner only.

### Skill candidate
`creative-candidate-controller`

---

## H06 — Challenger Diff Evaluator

**Classification:** SKILL_FOUNDRY_CANDIDATE + NOEMA_CANDIDATE

### Problem
A challenger can provide useful mechanics while being unsafe to merge wholesale.

### Candidate contract
Compare:
- canonical authority;
- challenger diff;
- architecture lock;
- product truth;
- QA rules.

Classify each change:
- KEEP;
- ADAPT;
- REJECT.

Produce:
- extraction map;
- forbidden merge warning;
- production handoff.

### Skill candidate
`challenger-diff-evaluator`

### Noema value
Formal challenger → production transition state.

---

## H07 — Master-to-Runtime Asset Delivery

**Classification:** SKILL_FOUNDRY_CANDIDATE

### Problem
Approved high-resolution masters are not automatically valid web-delivery assets.

### Candidate contract
Input:
- master;
- focal point;
- crop policy;
- LCP role;
- target widths.

Output:
- optimized AVIF/WebP derivatives;
- `picture/srcset/sizes` plan;
- loading priority;
- measured byte sizes;
- fallback.

### Skill candidate
`responsive-image-delivery`

---

## H08 — Design-to-Code Fidelity Evidence Gate

**Classification:** SKILL_FOUNDRY_CANDIDATE + NOEMA_CANDIDATE

### Problem
“Looks like Figma” is too subjective for a production gate.

### Candidate contract
At canonical widths:
- capture deterministic runtime screenshot;
- pair with canonical design reference;
- evaluate hierarchy/crop/type/spacing/overflow;
- log P0/P1/P2/P3 findings.

Output:
- evidence matrix;
- repair queue;
- PASS when P0/P1/P2 = 0.

### Skill candidate
`design-runtime-fidelity-audit`

---

## H09 — Motion Contract Auditor

**Classification:** SKILL_FOUNDRY_CANDIDATE

### Problem
Generic reveal animation can be technically safe but narratively wrong.

### Candidate contract
Compare implementation to:
- motion storyboard;
- reduced-motion rule;
- native-scroll rule;
- no-JS readable-state rule.

### Skill candidate
`motion-contract-auditor`

---

## H10 — Evidence Matrix Builder

**Classification:** SKILL_FOUNDRY_CANDIDATE + PROTOCOL_UPDATE

### Problem
DoD statements can remain qualitative unless mapped to evidence.

### Candidate contract
For every requirement:
- verification method;
- evidence artifact;
- status;
- exact commit/run.

### Skill candidate
`definition-of-done-evidence-matrix`

---

## H11 — Run-level spend telemetry

**Classification:** NOEMA_CANDIDATE

Noema should be able to record per workflow step:
- tool;
- model/mode;
- paid/free/fixed/variable;
- estimated or observed spend;
- iteration count;
- purpose;
- outcome;
- value classification.

This enables:
- cost retrospectives;
- stop-loss enforcement;
- tool substitution;
- cost-per-approved-artifact analysis.

---

## H12 — Tool trigger registry

**Classification:** NOEMA_CANDIDATE

Optional tools should not appear merely because they are available.

Registry fields:
```yaml
tool:
purpose:
trigger:
forbidden_uses:
max_iterations:
budget:
exit_condition:
fallback:
authority_level:
```

Examples from this case:
- v0 → only bounded frontend challenger;
- GSAP → only signature narrative motion;
- Mobbin → interaction sanity/reference;
- Spline → only if 3D yields material gain;
- Figma → canonical design, not debugging.

---

## Local-only findings

The following should NOT be generalized:
- Oni Nocturne aesthetic;
- demon visibility 20–30%;
- wet crimson cotton motif;
- Nexova company copy/facts;
- specific H1/H2 layouts.

These remain **LOCAL_NEXOVA**.
