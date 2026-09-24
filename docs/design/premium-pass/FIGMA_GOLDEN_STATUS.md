# Nexova Premium Website — Figma Golden Status

**Status:** H2 V1 HISTORICAL APPROVAL / CURRENT VISUAL AUTHORITY REOPENED  
**Date:** 2026-09-24  
**Canonical Figma file:** https://www.figma.com/design/fbDnWF59yCqfEEq5Sf8wFf  
**File key:** `fbDnWF59yCqfEEq5Sf8wFf`

## Current adjudication

The 2026-09-23 H2 approval remains valid as a **historical approval snapshot**, but H2 V1 is no longer sufficient as current production visual authority.

New material evidence from deployed H3 review showed:
- technically green runtime was visually far below the intended brand impact;
- static Golden composition left too much art-direction ambiguity;
- embedded A1/A2 images are only layout proxies;
- runtime mechanics alone did not recover the intended identity.

Therefore the visual track is reopened at:
`VISUAL_RECOVERY_PLAN_V2.md`.

This does **not** reopen the Identity Base Lock, Direction Contract, Product Truth or technical architecture.

## H2 V1 recovered facts

### Typography
- Instrument Serif / Regular
- Inter / Regular + Medium
- IBM Plex Mono / Regular

### Layout history
- complete 1440 desktop composition
- complete 390 mobile composition

### Motion history
- REST
- SEPARATE
- YIELD
- RELEASE
- one GSAP + ScrollTrigger Hero→Manifesto sequence
- native scroll
- reduced-motion without pin/scrub

### Embedded-image limitation
Figma source inspection:
- A1 imageHash original size: **172×180**
- A2 imageHash original size: **92×72**

These are proxies, not production masters.

## Current state

```yaml
H1_HISTORICAL_APPROVAL: true
H2_V1_HISTORICAL_APPROVAL: true
H2_V1_CURRENT_VISUAL_AUTHORITY: false
FIGMA_GOLDEN_LOCK: false
VISUAL_RECOVERY_V2_ACTIVE: true
R0_VISUAL_CANON_RECOVERY: active
A1_CANONICAL_MASTER: unrecovered
A2_ROLE_CONTRACT: recovered
TYPOGRAPHY_CONTRACT: recovered
MOTION_CONTRACT: recovered
V0_NEW_PASS_ALLOWED_BEFORE_H1_5: false
H3_APPROVED: false
```

## Next state

```text
R0 A1 CANONICAL RECOVERY
↓
R1 FIVE HIGH-FIDELITY FRAMES
↓
H1.5 HUMAN VISUAL GATE
↓
R2 v0 RUNTIME DESIGN PROTOTYPE
↓
R3 FIGMA GOLDEN V2
↓
H2 V2 HUMAN GOLDEN GATE
```

## Historical snapshot

On 2026-09-23 the user explicitly approved H2 V1 and authorized the original v0 challenger. That decision is preserved as history and must not be erased. It was later superseded for current visual authority by material runtime evidence and explicit human rejection.
