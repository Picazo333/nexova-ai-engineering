# Nexova / 4Geeks 4g-006 — Locked Execution Plan From H2

**Status:** EXECUTION LOCK  
**Date:** 2026-09-23  
**Change policy:** No phase/tool is added unless a current gate cannot be satisfied with the approved toolchain.

## Position in the global activity

```
S0 ACADEMIC_BASELINE_PASS          ✅
 ↓
S1 WEBSITE_PREMIUM_PASS           ← CURRENT
    H1                            ✅
    H2                            ✅
    v0 Challenger                 ✅ CLOSED
    G0 Production Preflight       ← NEXT
    Codex Production
    H3 Runtime Approval
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

The activity is **not** at final submission. It is inside S1, after design approval and challenger review, immediately before production implementation.

---

# G0 — Production Preflight

Owner: ChatGPT/GitHub/Codex tooling  
Paid visual generator: NO

Tasks:
1. reconcile stale project/document state;
2. create H3 Evidence Matrix;
3. classify current Vercel failure/config before relying on preview;
4. lock runtime asset-delivery schema;
5. confirm Codex branch from H2 base;
6. baseline typecheck/build/tests.

DoD:
- one canonical current state;
- no contradictory H1/H2/v0 flags;
- evidence matrix exists;
- baseline failures recorded;
- asset-delivery contract exists;
- production branch is isolated.

---

# P1 — Codex Static Desktop Implementation

Owner: Codex  
Authority: Figma H2 Golden

Implement:
- Header;
- Hero;
- Hero → Manifesto static final state;
- Capability editorial field;
- Evidence;
- Operating Philosophy;
- Presence;
- Closing;
- Footer.

v0 use:
- reference only;
- port KEEP/ADAPT mechanics explicitly;
- never merge wholesale.

DoD:
- 1440 matches H2 hierarchy/composition;
- 1024 does not break;
- legacy three-card/peony structures conflicting with H2 removed;
- factual copy remains source-backed;
- no unjustified dependency;
- build/typecheck remain green or known baseline issue is documented.

---

# P2 — Responsive Translation

Owner: Codex  
Reference sanity: Mobbin may be consulted only for interaction conventions.

Canonical width:
- 390

Verification:
- 430;
- 768;
- 1024;
- 1440.

DoD:
- no horizontal overflow;
- A1 crop intentional at mobile;
- type scale readable;
- navigation predictable;
- practical touch targets;
- essential content preserved;
- mobile is not desktop stacking.

---

# P3 — Runtime Asset Delivery

Owner: Codex/tooling

Masters remain untouched.

Create only necessary runtime variants:
- A1 desktop;
- A1 mobile;
- A2 responsive;
- AVIF preferred;
- WebP fallback where needed.

Use:
- `picture`;
- `srcset`;
- `sizes`;
- explicit dimensions;
- hero priority;
- non-LCP lazy loading.

DoD:
- raw heavy masters are not default delivery;
- no duplicate unnecessary downloads;
- byte sizes recorded;
- visual crop still matches H2.

---

# P4 — Signature Motion

Owner: Codex  
Tool: GSAP + ScrollTrigger if required to reproduce H2 storyboard.

Exactly one authored sequence:
`REST → SEPARATE → YIELD → RELEASE`.

Rules:
- native scroll authoritative;
- no wheel/touch interception;
- no site-wide scroll hijack;
- no generic reveal soup;
- no-JS final state readable;
- reduced-motion final state readable;
- local hover/focus stays CSS.

DoD:
- sequence recognizably matches storyboard;
- only required GSAP code ships;
- reduced-motion test passes;
- content comprehension never depends on animation.

---

# P5 — Runtime QA / H3 Evidence

Owner: Codex + Playwright/browser + axe + Lighthouse + GitHub Actions + Vercel

Evidence Matrix columns:
`requirement | verification | evidence | commit/run | status`

Required checks:
- 1440;
- 1024;
- 768;
- 430;
- 390;
- typecheck;
- production build;
- runtime;
- console errors;
- keyboard;
- focus;
- reduced motion;
- no-JS readable state;
- axe critical/serious;
- CLS;
- LCP;
- INP where measurable;
- asset/network sanity.

Visual finding severities:
- P0 blocker;
- P1 material;
- P2 quality;
- P3 polish.

H3 eligibility:
- P0 = 0;
- P1 = 0;
- P2 = 0;
- required technical gates PASS;
- Vercel preview works;
- evidence tied to exact commit.

---

# H3 — Human Runtime Approval

Present:
- desktop runtime;
- mobile runtime;
- signature motion;
- Figma↔runtime comparison;
- QA summary;
- accessibility/performance summary;
- dependency diff;
- unresolved P3 only;
- preview URL;
- commit SHA.

User approves or returns material findings.

No new design exploration begins at H3.

---

# After H3 — Finish S1

1. independent red team if not already satisfied by H3 evidence;
2. one bounded P0–P2 repair batch;
3. recapture once;
4. second repair only for remaining material failure;
5. declare `WEBSITE_PREMIUM_PASS`.

Then move to S2 Backoffice Premium Pass.

---

# v0 Integration Map

v0 prototype exists at:

```
branch: v0/premium-challenger
commit: f6149a1093e700bd12f85762c184f0aef5c07747
```

It is **not** a deployable authority and will not be merged whole.

## When it appears

It appears during **P1–P2 as a reference implementation**, after G0 and while Codex is implementing against Figma.

It does not appear as a separate final site.

## What is extracted

### KEEP / port
- semantic `picture` structure;
- desktop/mobile A1 source separation;
- width/height and hero loading priority;
- mobile-specific crop concept;
- inverse Philosophy field mechanics;
- A2 as compositional image, not wallpaper;
- native-scroll discipline;
- progressive-enhancement principle;
- reduced-motion/no-JS final-readable-state principle.

### ADAPT
- exact CSS geometry;
- type sizes;
- spacing;
- image positions;
- responsive breakpoints;
- section proportions.

These must be corrected against Figma H2.

### REJECT
- wholesale merge;
- legacy page sections left unchanged by the challenger;
- generic IntersectionObserver reveal as the signature Hero → Manifesto motion;
- any pseudo-Japanese decoration that is not required by the H2 identity.

## Optimal incorporation mechanism

Codex starts from:
`design/oni-nocturne-premium-pass`

Then:
1. inspect v0 diff;
2. port selected mechanics manually/semantically;
3. implement the rest directly from Figma H2;
4. never cherry-pick the full v0 commit;
5. validate runtime against Figma.

This preserves the value already purchased from v0 without allowing the challenger to become architecture or visual authority.

---

# Cost lock

For the remainder of S1:
- v0 calls: 0 by default;
- Figma mutations: only if H2 contains an actual ambiguity;
- image generation: 0 by default;
- Spline: SKIP;
- SuperDesign: SKIP;
- Motion package: only if repeated local motion creates a real need;
- GSAP: P4 signature sequence only;
- Codex/GitHub/CI/Vercel handle implementation and verification.

Any new variable-cost tool use requires:
- unresolved gate;
- unique expected value;
- cheaper alternatives ruled out;
- explicit bounded budget;
- stop condition.
