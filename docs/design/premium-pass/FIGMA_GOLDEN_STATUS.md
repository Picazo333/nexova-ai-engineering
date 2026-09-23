# Nexova Premium Website — Figma Golden Status

**Status:** H2_APPROVED / FIGMA_GOLDEN_LOCK  
**Date:** 2026-09-23  
**Canonical Figma file:** https://www.figma.com/design/fbDnWF59yCqfEEq5Sf8wFf  
**File key:** `fbDnWF59yCqfEEq5Sf8wFf`

## Authority

After H2 approval, this Figma file becomes the canonical visual source of truth for the premium website implementation.

Until H2 is explicitly approved, its current state is a review candidate.

## Completed

### Foundations
- Primitive + semantic color variables
- Spacing/radius variables
- Motion timing/easing variables
- Typography styles
- Foundations reference page

### Desktop Golden — 1440
Complete page structure:
1. Hero
2. Hero → Manifesto transition
3. Capability field
4. Evidence
5. Operating philosophy
6. Presence
7. Closing
8. Footer

The current company facts and service copy are source-backed from `CONTEXT.md` / `PRODUCT_TRUTH.md`.

### Mobile Golden — 390
The full site has an independently art-directed mobile composition:
- reduced ornamental density;
- mobile-specific hero crop;
- mobile-specific type scale;
- reduced motion assumptions;
- full content hierarchy preserved.

### Approved production material
- A1 abstract abyssal hero is embedded as the Figma crop/layout reference.
- A2 crimson-soaked fibrous material is embedded for transition/closing material fields.
- The original high-resolution masters remain the production image sources; embedded Figma references are layout/crop proxies and must not be exported as final production assets.

### Motion
The Motion Spec contains a four-frame storyboard:
- REST
- SEPARATE
- YIELD
- RELEASE

Contract:
- one GSAP + ScrollTrigger signature sequence for Hero → Manifesto;
- native scroll remains authoritative;
- reduced-motion path removes pin/scrub and resolves to the final readable state.

## H2 review contract

H2 may be approved only if the user accepts:

1. full desktop information hierarchy;
2. mobile translation;
3. visual system and type direction;
4. placement/use of A1/A2 material assets;
5. Hero → Manifesto motion concept;
6. overall balance between brutalist structure, organic materiality, and corporate clarity.

## Current state

```yaml
H1_APPROVED: true
FIGMA_FOUNDATIONS_PASS: true
DESKTOP_GOLDEN_READY: true
MOBILE_GOLDEN_READY: true
MOTION_STORYBOARD_READY: true
H2_READY: true
H2_APPROVED: true
FIGMA_GOLDEN_LOCK: true
V0_CHALLENGER_ALLOWED: true
```

## Next state

On explicit H2 approval:

```
FIGMA_GOLDEN_LOCK = TRUE
↓
V0 CHALLENGER
↓
V0-A Hero implementation
V0-B Editorial section
V0-C Mobile translation
```


## H2 approval

**Approved by user:** 2026-09-23

The Golden candidate is now locked as the canonical visual baseline for the premium website.

```yaml
FIGMA_GOLDEN_LOCK: true
H2_APPROVED: true
V0_CHALLENGER_ALLOWED: true
```

The next gate is the v0 Challenger. v0 may challenge implementation choices, but it may not silently replace the approved identity, information hierarchy, mobile intent, or Hero → Manifesto narrative contract.
