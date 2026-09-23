# Nexova Premium Website — v0 Challenger Review

**Date:** 2026-09-23  
**Status:** COMPLETE  
**Source branch:** `v0/premium-challenger`  
**Source commit:** `f6149a1093e700bd12f85762c184f0aef5c07747`  
**Decision:** DO NOT MERGE WHOLESALE

## Executive decision

The v0 challenger produced useful implementation mechanics, but it is not the canonical implementation.

The approved Figma Golden remains the visual authority. Selected mechanics may be adapted into the production implementation; the v0 branch must not be merged as-is.

## Cost gate

v0 usage is now frozen for this activity.

No further v0 calls are authorized unless:
1. a material visual implementation problem remains after Codex implementation;
2. the issue cannot be resolved from the Figma Golden + existing contracts;
3. the expected visual value justifies a new variable-cost generation.

Build debugging, Git inspection, CI diagnosis, asset optimization, accessibility checks, responsive fixes and mechanical code corrections must be handled with GitHub/Codex/CI/Vercel tooling instead of v0.

## Challenger classifications

### V0-A — Hero
**Classification:** ADAPT

KEEP:
- semantic `<picture>` structure;
- separate desktop/mobile A1 sources;
- explicit width/height;
- `fetchPriority="high"` for hero/LCP;
- left copy / right visual counter-mass;
- no scroll hijacking;
- readable static composition.

ADAPT:
- crop/placement must be brought back to the H2 Figma Golden;
- type scale, spacing and responsive behavior must be validated against 1440/1024/768/430/390;
- use optimized runtime derivatives of the A1 master, not raw master PNGs.

REJECT:
- any visual deviation that weakens the approved H2 composition;
- any fallback to the old Oni mask / pseudo-Japanese decoration.

### V0-B — Operating Philosophy
**Classification:** ADAPT

KEEP:
- inverse bone field;
- asymmetric material/copy split;
- A2 used as compositional material rather than wallpaper;
- semantic section structure;
- mobile crop differing from desktop.

ADAPT:
- spacing/type/crop against H2 Figma Golden;
- production image delivery via optimized responsive formats.

### V0-C — Mobile
**Classification:** ADAPT

KEEP:
- mobile-specific crop;
- reduced ornament density;
- no horizontal-scroll behavior;
- no scroll snapping;
- compact header approach;
- preserved content hierarchy.

ADAPT:
- exact 390 Golden proportions;
- verify 430 and 768 intermediate states;
- touch targets and menu behavior in runtime.

## Motion decision

**Current v0 reveal implementation:** REJECT AS SIGNATURE MOTION

The v0 branch uses IntersectionObserver + CSS reveal transitions. This is technically sound progressive enhancement, but it does not implement the approved H2 Hero → Manifesto signature sequence.

KEEP:
- the reduced-motion / no-JS progressive-enhancement principle;
- final-readable-state behavior.

REPLACE:
- generic reveal choreography with the single approved GSAP + ScrollTrigger Hero → Manifesto sequence;
- no pin/scrub on reduced-motion path;
- native scroll remains authoritative.

## Full-page consistency issue

The v0 challenger intentionally did not redesign unrelated surfaces. Therefore the branch still contains legacy patterns that must NOT survive into the final production pass when they conflict with H2, including:
- generic three-card service layout;
- legacy peony decorative treatment;
- legacy sections that do not match the Figma Golden editorial structure.

Codex production implementation must follow the **full H2 Figma Golden**, not simply patch the v0 diff into the pre-H2 page.

## Asset note

A1/A2 masters are valid source assets but too large for direct runtime delivery.

Before H3:
- generate AVIF/WebP derivatives;
- retain master PNGs only as source assets;
- responsive sizes/srcset;
- explicit dimensions/aspect ratio;
- lazy-load non-LCP assets;
- verify LCP impact.

## Definition of done for v0 phase

- [x] isolated branch created;
- [x] Hero challenger produced;
- [x] Philosophy challenger produced;
- [x] Mobile challenger produced;
- [x] no framework migration;
- [x] no dependency additions;
- [x] no automatic merge;
- [x] mechanics classified;
- [x] cost gate applied;
- [x] selected lessons ready for Codex handoff.

**v0 phase: CLOSED.**
