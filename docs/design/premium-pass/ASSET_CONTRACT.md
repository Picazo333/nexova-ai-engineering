# Nexova Premium Website — Asset Contract

**Status:** READY FOR PRODUCTION — REFRESHED AFTER IDENTITY BASE APPROVAL  
**Authority:** Direction Contract + Oni Nocturne Visual Lock  
**Purpose:** Generate only assets that have a defined compositional job.

## General rules

1. Assets are production inputs, not standalone poster art.
2. No generated text, pseudo-kanji, logos or UI inside raster artwork.
3. Every primary asset needs a usable safe zone for interface/copy.
4. Desktop and mobile crop viability must be tested before approval.
5. One dominant motif per composition.
6. Keep masters high-resolution; optimize only selected winners.
7. If CSS/SVG can create the material more cleanly, do not rasterize it.

## A1 — Abyssal Demon / Oni Hero

**Priority:** CRITICAL  
**Role:** primary brand anchor / dominant visual mass.

### Visual intent
- traditional-Japanese-informed demon/oni, treated graphically rather than cinematically;
- abstract, fragmented and partially dissolved into an abyssal dark field;
- severe, controlled and intelligent;
- dark material depth with bone/ivory fragments and selective oxblood/crimson;
- skin-like organic substrate may appear as material texture only;
- crimson-soaked wet cotton may appear as a fibrous material/transition layer;
- no full fantasy-character reading;
- no anime;
- no tattoo-shop poster;
- no movie-poster lighting;
- no gore.

### Composition
Desktop master:
- landscape or flexible 4:3-ish master;
- face/head/upper-body focal mass biased toward right or center-right;
- left or left-center safe negative space for headline;
- meaningful dark edges for responsive crop.

Mobile:
- crop must preserve face/eyes/mask character;
- must permit headline overlay or separation;
- no essential information in far edges.

### Reject
- centered poster;
- full symmetrical mask filling frame;
- oversaturated red;
- glowing eyes;
- horns treated as gaming/fantasy;
- random Japanese lettering;
- melting ornamental anatomy;
- excessively busy background.

### Candidate budget
3 independent candidates.
1 repair maximum after winner selection.

## A2 — Crimson Fibrous / Organic Counter-Material

**Priority:** HIGH  
**Role:** foreground framing / depth / transition support; wet cotton saturated by crimson liquid is the primary approved material direction.

### Visual intent
- fibrous cotton-like softness with visible absorption behavior;
- crimson/oxblood liquid soaking into warm organic fibers;
- tactile but refined;
- large compositional masses, not macro-gore;
- edge-friendly for clipping, masking and motion;
- can coexist with restrained botanical/ink fragments only if needed.

### Composition
- transparent or clean dark background preferred;
- can be cropped aggressively;
- should work as left/right foreground framing.

### Reject
- gore or blood-horror reading;
- medical imagery;
- glossy wet-flesh appearance;
- neon red;
- decorative wallpaper;
- random floral filler.

### Candidate budget
3.

## A3 — Sumi Atmosphere

**Priority:** HIGH  
**Role:** atmospheric depth and transition separation.

### Visual intent
- ink/smoke behavior;
- directional;
- transparent/black-friendly;
- broad shapes rather than noisy fog.

### Requirements
- must support compositing;
- should not contain focal objects;
- must not reduce text contrast when used within specified opacity.

### Implementation note
If a CSS/SVG/noise solution performs better, generated raster may be rejected entirely.

## A4 — Signature Background / Landscape

**Priority:** HIGH  
**Role:** secondary atmosphere for philosophy/closing; not repeated background wallpaper.

### Visual intent
- nocturnal Japanese landscape / architectural suggestion;
- deep black field;
- restrained moon/torii if composition requires;
- large quiet zones;
- cinematic but minimal.

### Reject
- scenic wallpaper;
- tourist/Japan cliché;
- obvious red sun centered behind torii;
- fantasy matte painting.

## B1 — Blood Moon

Conditional.
Prefer CSS/vector/photographic treatment if sufficient.

## B2 — Secondary Oni Detail

Conditional.
Close crop/detail only if a later section genuinely needs a second art anchor.

## B3 — Ritual Ornament

Conditional.
Prefer vector/line construction.

## C — Code-native materials

Default to CSS/SVG:
- grain;
- lacquer sheen;
- paper noise;
- fine rules;
- frame lines;
- subtle gold/metal highlights.

## Asset approval schema

```yaml
id:
role:
candidate:
status: APPROVE | REPAIR | REJECT
identity_match:
composition_usefulness:
safe_zone:
desktop_crop:
mobile_crop:
artifact_cleanliness:
visual_uniqueness:
performance_risk:
notes:
```

## Production sequence

1. Generate A1 Hero Oni candidates.
2. Select/repair A1.
3. Generate A2 Peony against selected A1 visual grammar.
4. Generate/test A3 only if code-native atmosphere is insufficient.
5. Generate A4 after full-page composition establishes its required shape.
6. Do not generate Tier B until a Figma composition calls for it.

## Current state

```yaml
A1_HERO_ONI: approved
A2_CRIMSON_FIBROUS_MATERIAL: approved
A3_SUMI: blocked_by_composition_test
A4_LANDSCAPE: blocked_by_page_composition
TIER_B: deferred
```


## Approved production direction — 2026-09-22

### A1 — Abstract abyssal hero
**Status:** APPROVED

The approved hero direction is an abstract composition where the demon/oni is only partially legible and largely dissolved into a black abyssal field. Recognizable anatomy is subordinate to material flow, negative space and editorial composition.

Approved characteristics:
- demon visibility approximately 20–30%;
- no complete face;
- no full eye pair;
- no full mouth;
- horns only as partial fragments;
- black void dominant;
- wet crimson cotton/fibrous material integrated into the composition;
- skin-like materiality remains subtle;
- ochre/gold is restrained;
- aggression low;
- mystery/elegance high.

### A2 — Crimson fibrous material
**Status:** APPROVED

The cotton/fiber material soaked with crimson liquid is approved as a recurring organic counter-material. It may be used as:
- transition layer;
- foreground framing;
- mask/reveal material;
- section divider;
- motion source.

It must not read as gore.

### Next gate
Build the Composition Proof for:
- Navigation
- Hero
- Hero → Manifesto transition
- First capability section

This Composition Proof is the artifact for H1 approval. Figma production begins only after H1.
