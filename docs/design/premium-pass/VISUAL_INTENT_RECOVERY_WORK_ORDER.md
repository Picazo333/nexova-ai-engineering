# Nexova Premium Website — Visual Intent Recovery Work Order

**Status:** LOCKED EXECUTION ORDER  
**Date:** 2026-09-23  
**Owner:** Codex production implementation  
**Trigger:** H3 human runtime review exposed material loss of approved visual intent.  
**Scope:** Recover the already-approved premium direction. No new art direction, no scope expansion.

## Authority chain

1. 4Geeks academic requirements
2. Product Truth
3. `IDENTITY_BASE_LOCK.md`
4. `DIRECTION_CONTRACT.md`
5. `ASSET_CONTRACT.md`
6. H1 approved Composition Proof
7. H2 Figma Golden
8. `RUNTIME_ASSET_DELIVERY_CONTRACT.md`
9. H2 Motion Storyboard
10. this bounded recovery order

Where a static Figma proxy conflicts with an explicit production contract, the production contract wins:
- Figma image fills are crop/layout references;
- approved high-resolution masters are production sources;
- Figma's static frames do not replace the approved runtime motion contract.

## Observed H3 failure

The deployed page is technically functional but visually under-resolves the approved direction.

Material failures:
- A1 runtime source drifted between a low-resolution Figma proxy and an older literal Oni master.
- A2 fibrous material is presented as repeated static image furniture instead of transition/framing/motion material.
- typography does not reliably render the exact Golden families;
- the approved Hero→Manifesto scrollytelling is not implemented as the locked GSAP/ScrollTrigger signature sequence;
- the result reads as a structurally correct dark editorial site rather than the intended authored premium experience.

H3 remains OPEN.

## Non-negotiable recovery targets

### 1. Typography — exact H2 system

Use:
- **Instrument Serif / Regular** — display, wordmark, large editorial statements;
- **Inter / Regular + Medium** — body, navigation, actions;
- **IBM Plex Mono / Regular** — utility metadata/eyebrows.

Golden desktop reference:
- hero display: Instrument Serif 104 / 92, tracking -2.2 px;
- body: Inter 18 / 30;
- utility: IBM Plex Mono 11 / 16, tracking 1.6 px;
- navigation/action: Inter Medium 12 / 16, tracking 1.8 px.

Mobile reference:
- hero display: Instrument Serif 58 / 54;
- body remains restrained and readable.

No fallback stack may be accepted as the intended final type treatment when the approved web font is available.

### 2. A1 Hero — approved role, not substitute art

Contract:
- abstract abyssal demon;
- only 20–30% recognizability;
- no complete face;
- black void dominant;
- skin/fibrous crimson material integrated;
- aggression low, mystery/elegance high;
- desktop focal mass right/center-right;
- mobile independently art-directed.

Current repository problem:
- Figma A1 imageHash resolves to only **172×180 px**;
- therefore it is a proxy and cannot be used as production art;
- current repository high-resolution `a1-hero-desktop.png` is a materially more literal Oni and is not an automatic replacement for the approved abstract A1.

Required:
- recover the approved A1 high-resolution master from prior generation/output if available;
- if unrecoverable, regenerate/reconstruct **against the locked A1 contract and H2 crop**, not against a new direction;
- only one bounded recovery candidate is allowed before another human checkpoint.

### 3. A2 Crimson Fibrous material — material, not content block

Approved role:
- transition layer;
- foreground framing;
- mask/reveal material;
- section divider;
- motion source.

Forbidden:
- repeated static `<img>` blocks that read as ordinary section imagery;
- decorative wallpaper;
- use that competes with A1.

Implementation:
- Hero→Manifesto may use A2 as clipped/masked material participating in SEPARATE/YIELD;
- closing may echo the material only as an abstract lower-intensity field, never as an obvious repeated photograph;
- prefer compositing/masking/crop behavior over duplicated standalone figures.

### 4. Signature scrollytelling — exact H2 motion contract

Exactly one GSAP + ScrollTrigger sequence:

```
00 REST
→ 01 SEPARATE
→ 02 YIELD
→ 03 RELEASE
```

Storyboard text:
> One pinned GSAP/ScrollTrigger sequence. Native scroll remains authoritative. The artwork shifts, fibers separate, copy yields, manifesto appears, then the page releases.

Required behavior:
- one bounded pin only across Hero→Manifesto;
- native scroll remains authoritative;
- no wheel interception;
- no full-page snap;
- A1 remains readable before movement;
- A2 separates as transition material;
- hero copy yields visual territory;
- manifesto enters;
- sequence releases into normal document flow.

Reduced motion:
- no pin;
- no scrub;
- final readable Hero state;
- simple opacity/translate reveal for Manifesto.

### 5. Composition fidelity

Preserve H2 Golden:
- page hierarchy;
- asymmetry;
- hero 1440 composition;
- independent 390 translation;
- capability field;
- evidence;
- operating philosophy;
- presence;
- closing;
- footer.

Do not decorate the page to compensate for missing art/motion.
Do not add new sections.
Do not convert the page into cards/bento/dashboard patterns.

## Tooling lock

Use the smallest approved toolchain:
- **Figma H2 Golden** — visual geometry/reference authority;
- **GitHub/Codex production branch** — implementation owner;
- **GSAP + ScrollTrigger** — only signature scroll narrative;
- CSS — microstates, layout, masking, restrained surface treatment;
- deterministic QA — responsive/overflow/console/keyboard/reduced motion;
- axe + Lighthouse — accessibility/performance;
- Vercel — deployed runtime evidence.

Not authorized for this recovery unless a specific unresolved gate proves need:
- v0;
- Spline;
- SuperDesign;
- new moodboards;
- new visual route exploration;
- unrelated image-generation experiments.

## Execution order

### VIR-0 — State and source integrity
- mark current runtime as technical baseline / visual not approved;
- prohibit `*-golden-*.png` Figma proxies as runtime sources;
- identify/recover correct A1 production master;
- verify A2 source.

### VIR-1 — Typography recovery
- load exact approved families;
- match H2 scale/line-height/tracking at desktop/mobile;
- verify fallback does not silently replace primary family.

### VIR-2 — Asset-role recovery
- A1 returns to dominant hero role;
- A2 removed from ordinary static-image role;
- A2 becomes transition/framing material;
- preserve H2 crop intent.

### VIR-3 — Signature scrollytelling
- implement GSAP + ScrollTrigger;
- REST → SEPARATE → YIELD → RELEASE;
- reduced-motion alternate state.

### VIR-4 — Premium composition polish
Only after VIR-1..3:
- optical spacing;
- crop calibration;
- negative-space balance;
- line/stroke/material restraint;
- no new design language.

### VIR-5 — Runtime QA
Required:
- 1440 / 1024 / 768 / 430 / 390;
- no horizontal overflow;
- no console/runtime errors;
- keyboard/focus/mobile nav;
- reduced motion;
- no-JS readable state;
- axe 0 serious/critical;
- Lighthouse;
- perceptual visual review against H2 + Direction Contract;
- asset-source integrity check.

### VIR-6 — Human H3
Present deployed runtime only after VIR-5 passes.
H3 closes only with explicit human approval.

## Stop conditions

STOP and escalate only if:
- the approved A1 high-resolution master cannot be recovered and one bounded reconstruction must be generated;
- implementation reveals a genuine contradiction between H2 Golden and a higher-authority contract;
- a new paid/variable-cost tool becomes materially necessary;
- H3 human review identifies a new material failure.

Otherwise continue autonomously.

## Definition of Done

```yaml
TECHNICAL_BASELINE: PASS
VISUAL_INTENT_RECOVERED: PASS
A1_SOURCE_INTEGRITY: PASS
A2_ROLE_INTEGRITY: PASS
TYPOGRAPHY_H2_EXACT: PASS
SCROLLYTELLING_CONTRACT: PASS
RESPONSIVE_GOLDEN: PASS
ACCESSIBILITY: PASS
PERFORMANCE: PASS
DEPLOYED_PREVIEW: PASS
HUMAN_H3_APPROVAL: PASS
```

Anything less is not H3.
