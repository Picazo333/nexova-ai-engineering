# Nexova Premium Website — v0 Challenger Brief

**Status:** READY_TO_RUN  
**Date:** 2026-09-23  
**Authority:** Challenger only; below Figma Golden Lock.  
**Canonical Figma:** https://www.figma.com/design/fbDnWF59yCqfEEq5Sf8wFf  
**Target repo:** `Picazo333/nexova-ai-engineering`  
**Target branch:** `design/oni-nocturne-premium-pass`

## 0. Locked inputs

The following are already approved and MUST NOT be silently redesigned:

- H1 visual direction;
- H2 desktop 1440 Golden;
- H2 mobile 390 Golden;
- Figma foundations/tokens;
- A1 abstract abyssal hero artwork;
- A2 crimson-soaked fibrous material;
- Hero → Manifesto narrative/motion concept;
- factual company content;
- existing React + Vite + TypeScript architecture.

Authority order:

1. 4Geeks rubric / assignment constraints
2. Product truth
3. Identity Base Lock
4. Direction Contract
5. Figma Golden Lock
6. Existing repository architecture
7. Runtime evidence
8. v0 output

v0 is allowed to challenge **implementation mechanics**, not the approved product truth or visual authority.

## 1. Hard technical constraints

Preserve:
- React;
- Vite;
- TypeScript;
- npm workspace;
- `uis/website`;
- `packages/design-system`.

Do NOT introduce merely for generator convenience:
- Next.js;
- Tailwind;
- shadcn;
- a new UI kit;
- a framework migration;
- a new design system;
- backend/services.

Existing CSS/custom primitives are valid and preferred when they solve the problem cleanly.

Dependencies must be justified individually. If a dependency is not materially better than native CSS/React, do not add it.

## 2. Visual constraints

Target identity:

> brutalist editorial structure × traditional Japanese graphic language × abyssal abstract demon × organic skin substrate × crimson-soaked wet cotton materiality.

Must feel:
- editorial;
- dark;
- tactile;
- disciplined;
- premium;
- severe but commercially legible;
- human/B2B rather than AI-startup-like.

Reject:
- centered SaaS hero;
- generic 3-card feature grid;
- bento-by-default;
- glassmorphism;
- cyan/neon;
- purple AI gradients;
- chromatic glow;
- cyberpunk;
- gaming UI;
- anime/fantasy poster treatment;
- tattoo-shop aesthetic;
- decorative pseudo-Japanese iconography;
- generic luxury template;
- fake testimonials or fake proof.

Typography is a primary identity carrier. Ornament is secondary.

## 3. Product truth

Publishable facts only:
- Nexova Solutions;
- founded 2011;
- Valencia headquarters;
- Miami expansion office;
- 120 employees;
- recruitment/headhunting;
- outsourced customer-support teams;
- leadership and soft-skills corporate training;
- frequent sectors: technology, retail, financial services;
- company is modernizing fragmented/manual infrastructure.

Do not invent:
- customer logos;
- testimonials;
- awards;
- metrics;
- conversion gains;
- case studies;
- AI product adoption.

## 4. Challenge protocol

Run **three independent challenges**.

For each challenge:
- one initial generation;
- at most one material revision;
- no automatic merge;
- no hidden changes outside the requested surface;
- report any dependency added;
- explain any deviation from Figma.

The output is reviewed as:
- KEEP
- ADAPT
- REJECT

### V0-A — Hero implementation challenger

**Question:** Can you implement the locked desktop Hero more effectively than the current code without changing the approved composition?

Target:
- desktop 1440 Hero;
- persistent conventional header;
- copy counter-mass on the left;
- A1 image mass on the right;
- one primary CTA + one secondary text action;
- strong negative space;
- editorial type;
- readable before animation.

Implementation requirements:
- React + TypeScript + CSS;
- preserve current token vocabulary where practical;
- use the production A1 master asset, not a low-resolution Figma proxy;
- no decorative Japanese text required for identity;
- no scroll hijacking;
- hero must remain fully legible with JS disabled;
- reserve GSAP choreography for Hero → Manifesto rather than filling the Hero with independent animation.

Deliver:
1. exact files you would change;
2. complete proposed implementation;
3. dependency diff;
4. responsive behavior at 1440 / 1024 / 768 / 390;
5. accessibility notes;
6. performance/LCP risks;
7. a concise explanation of what your implementation improves mechanically.

### V0-B — Complex editorial section challenger

**Question:** What is the cleanest implementation of the locked Operating Philosophy section while preserving its inverse field, materiality and editorial hierarchy?

Target:
- light bone field interrupting the black site rhythm;
- organic material crop;
- large editorial statement;
- restrained body copy;
- asymmetric image/text relationship;
- no card container aesthetic.

Implementation requirements:
- semantic section markup;
- CSS layout first;
- no unnecessary JS;
- no decorative effect that weakens copy contrast;
- no generic split-screen template feel;
- material asset is compositional, not wallpaper.

Deliver:
1. exact files you would change;
2. implementation;
3. breakpoint behavior;
4. how the image crop changes between desktop/mobile;
5. accessibility/contrast notes;
6. what should remain local to the section instead of becoming a shared abstraction.

### V0-C — Mobile translation challenger

**Question:** Can you translate the H2 mobile Golden into a robust 390px implementation without simply stacking desktop blocks?

Target:
- mobile 390;
- independently art-directed A1 crop;
- reduced ornament density;
- reduced type scale without losing drama;
- compact navigation;
- Hero → Manifesto continuity;
- native scroll;
- reduced-motion path.

Implementation requirements:
- preserve information hierarchy;
- avoid horizontal overflow;
- minimum practical touch targets;
- do not hide essential content;
- no scroll snapping;
- no wheel/touch interception;
- motion amplitude reduced relative to desktop.

Deliver:
1. implementation changes;
2. rules that make the mobile composition intentionally different from desktop;
3. 390 / 430 / 768 behavior;
4. reduced-motion implementation;
5. any layout edge cases.

## 5. Mandatory final response format from v0

Return:

### Files changed
- path
- purpose

### Dependencies
- added
- removed
- unchanged
- justification

### Implementation notes
- A
- B
- C

### Deviations from Figma
For every deviation:
- exact deviation;
- reason;
- whether it is required by implementation/accessibility/performance.

### Risks
- visual fidelity;
- responsive;
- accessibility;
- performance;
- maintainability.

### Recommended extraction
Only identify reusable primitives proven by repetition.

### Do not do
Do not merge, deploy production, rewrite unrelated sections, or alter factual copy.

## 6. Stop condition

Stop after the three challengers and their requested evidence.

Do not continue into full-site implementation.

Production implementation belongs to Codex after challenger review.
