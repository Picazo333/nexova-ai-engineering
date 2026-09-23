# Nexova Premium Website — Codex Production Handoff

**Date:** 2026-09-23  
**Status:** READY  
**Base branch:** `design/oni-nocturne-premium-pass`  
**Reference challenger:** `v0/premium-challenger` @ `f6149a1093e700bd12f85762c184f0aef5c07747`  
**Canonical visual authority:** Figma H2 Golden, file key `fbDnWF59yCqfEEq5Sf8wFf`

## Mission

Implement the approved premium Nexova website in the existing React + Vite + TypeScript monorepo with high visual fidelity, restrained complexity and production-grade responsive/accessibility/performance behavior.

Do not merge the v0 challenger wholesale. Use only the KEEP/ADAPT mechanics recorded in `V0_CHALLENGER_REVIEW.md`.

## Authority order

1. 4Geeks rubric / delivery constraints
2. Product truth
3. Identity Base Lock
4. Direction Contract
5. Figma H2 Golden Lock
6. v0 Challenger Review
7. Existing repository architecture
8. Runtime evidence

## Architecture lock

Preserve:
- React;
- Vite;
- TypeScript;
- npm workspaces;
- `uis/website`;
- `packages/design-system`.

Do not add:
- Next.js;
- Tailwind;
- shadcn;
- a replacement design system;
- backend/services;
- dependencies without a specific implementation need.

## Production sequence

### P0 — Branch + baseline
Create an isolated Codex implementation branch from `design/oni-nocturne-premium-pass`.

Run:
- typecheck;
- website build;
- existing tests/checks;
- record baseline failures before editing.

### P1 — Static H2 fidelity
Implement the full desktop 1440 Golden first with no signature motion dependency on correctness.

Required sections:
1. Header
2. Hero
3. Hero → Manifesto visual handoff
4. Capability editorial section
5. Evidence
6. Operating Philosophy
7. Presence
8. Closing
9. Footer

Important:
- replace legacy three-card service UI with the H2 editorial capability treatment;
- remove visual elements that conflict with the approved identity;
- A1 and A2 are material/image sources, not generic backgrounds.

**DoD**
- layout matches H2 hierarchy;
- copy remains product-truth compliant;
- no unnecessary new dependency;
- no horizontal overflow at 1440/1024.

### P2 — Responsive translation
Implement the mobile 390 Golden as its own art direction.

Validate:
- 390
- 430
- 768
- 1024
- 1440

**DoD**
- no horizontal overflow;
- mobile A1 crop is intentional;
- type scale remains dramatic but readable;
- essential content never hidden;
- touch targets practical;
- menu predictable.

### P3 — Asset delivery
Keep high-resolution masters as source assets.

Create runtime derivatives:
- AVIF preferred;
- WebP fallback;
- responsive widths;
- desktop/mobile crops where materially useful.

Use:
- `picture`;
- `srcset`;
- `sizes`;
- width/height;
- high priority only for LCP A1;
- lazy loading for A2 and later imagery.

**DoD**
- no raw 1.5MB A2 delivered by default;
- no unnecessary duplicate downloads;
- LCP image strategy documented.

### P4 — Signature motion
Implement ONE authored sequence: Hero → Manifesto.

Preferred implementation:
- GSAP + ScrollTrigger only if it materially simplifies the approved choreography;
- if added, justify dependency and keep its scope local.

Contract:
- native scroll is authoritative;
- no wheel/touch interception;
- no full-page scroll hijack;
- reduced-motion/no-JS resolves to readable final states;
- motion must not be required to understand content.

**DoD**
- H2 REST → SEPARATE → YIELD → RELEASE concept is recognizable;
- no generic reveal soup;
- reduced-motion path tested.

### P5 — QA / H3
Run:
- typecheck;
- production build;
- visual checks at required widths;
- keyboard navigation;
- reduced motion;
- no-JS readable-state check;
- asset/network sanity;
- Lighthouse-style performance review where available.

Investigate Vercel failure through build configuration/logs without using v0.

## Cost-efficiency contract

Use the cheapest adequate tool for each job:

- Git/repo inspection → GitHub tooling
- implementation/refactor → Codex
- compile/type errors → Codex + local/CI
- visual authority → Figma
- runtime/deployment diagnosis → Vercel/CI logs
- variable-cost v0 → CLOSED unless a genuinely unresolved visual challenge remains

Do not spend premium visual-generation credits on:
- branch inspection;
- build diagnosis;
- lint/type fixes;
- asset conversion;
- test execution;
- deployment configuration.

## H3 gate

Do not call production complete until:
- static desktop fidelity passes;
- mobile fidelity passes;
- A1/A2 runtime assets are optimized;
- motion contract passes;
- reduced motion passes;
- build/typecheck pass;
- Vercel preview succeeds;
- rubric audit passes.

## Exit artifact

Return:
1. exact files changed;
2. dependency diff;
3. test/build evidence;
4. responsive evidence;
5. performance/asset evidence;
6. deviations from Figma, if any;
7. unresolved risks;
8. preview URL;
9. commit SHA.
