# NEXOVA — Delivery Visual Lock

**Status:** LOCKED  
**Date:** 2026-09-24  
**Purpose:** canonical website visual/source lock for the 4Geeks activity delivery.

## Human approval

The user explicitly approved the v0 sandbox preview as the website direction to use for the activity delivery.

Source chat:
https://v0.app/mbpicazo33-1986/chat/nexova-visual-sandbox-n0o4weQLsCq

## Immutable source fingerprint

Exported source ZIP:
`nexova-visual-sandbox.zip`

SHA-256:
`211874809bebc6dcb71eaeaf804b4a86b92a443f37d9b7dfb672319d44a4b329`

Persistent artifact:
`/NEXOVA/locks/NEXOVA_V0_DELIVERY_VISUAL_LOCK_2026-09-24.zip`

Library file id:
`libfile_563038655944819182ceebf97366b1cb`

Any source claiming to be this lock must reproduce the exact ZIP SHA-256 above.

## Approved implementation stack

- Next.js 16.3.3
- React 19
- Tailwind CSS 4.3.3
- GSAP 3.15.0
- next/font:
  - Instrument Serif
  - Inter
  - IBM Plex Mono

## Canonical image set

1. `A1_HERO_ABYSSAL_PRESENCE.png`
2. `A2_FIBROUS_CRIMSON_MATERIAL.png`
3. `A3_EDITORIAL_MID_PAGE.png`
4. `A4_EVIDENCE_PRECISION.png`
5. `A5_FINAL_DECLARATION.png`

The approved source assigns these semantic roles:
- A1: hero / emotional anchor
- A2: Hero→Manifesto transition material
- A3: signature mid-page composition
- A4: evidence / precision
- A5: final declaration

## Approved page sequence

1. Header
2. Hero / REST
3. Hero→Manifesto scrollytelling
4. Manifesto / Operating Philosophy
5. Signature Mid-Page
6. Evidence / Precision
7. Final Declaration
8. Minimal Footer

## Motion lock

Signature sequence:
`REST → SEPARATE → YIELD → RELEASE`

Implementation:
- GSAP + ScrollTrigger
- one bounded pinned Hero→Manifesto story on supported desktop
- native scroll authoritative
- no wheel hijacking
- no full-page snapping
- reduced-motion path without pinned scrub

## No-regression rule

The monorepo port must preserve:
- composition;
- typography;
- asset choice and semantic role;
- section order;
- visual hierarchy;
- color/material system;
- motion narrative and timing character;
- desktop/mobile visual intent.

### Allowed after lock
Only:
- monorepo integration;
- dependency/build compatibility;
- factual/rubric-required copy corrections;
- accessibility fixes;
- responsive bug fixes;
- performance fixes;
- deployment fixes.

### Forbidden after lock
Without new explicit human approval:
- redesign;
- new visual route;
- substituting A1–A5;
- changing fonts;
- changing section composition;
- converting A2 into ordinary content imagery;
- changing the signature motion concept;
- genericizing the page to fit the existing Vite implementation.

## Integration policy

The target required by the assignment remains:
`/uis/website`

The approved source currently exists as a standalone Next.js export. The engineering task is therefore to port/integrate this exact source into the Nexova monorepo while preserving the visual lock.

If maintaining the exact Next.js implementation inside `/uis/website` is lower-risk than translating it into Vite, prefer the Next.js implementation. Architecture must serve no-regression, not force a rewrite.

## Academic delivery

After the port:
1. run the repository's real install/typecheck/build/runtime workflow;
2. capture updated website + backoffice evidence;
3. rerun R01–R22;
4. final assignment head must be on `feature/agent-memory-bank`;
5. update existing PR #1; do not replace it;
6. user submits the exact PR URL to Campus.

## Current gate

`PORT_APPROVED_SOURCE_TO_UIS_WEBSITE_AND_VERIFY_NO_REGRESSION`
