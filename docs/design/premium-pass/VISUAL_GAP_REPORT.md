# Nexova Premium Website — Visual Gap Report

**Audit target:** academically validated website implementation at `138ff88496b80ff220141df4a39f3cffb6b62b4a`  
**Visual target:** Oni Nocturne Oxblood lock (`VISUAL_LOCK.md`, boards 26–30)  
**Audit type:** source + implementation-contract audit. Fresh browser-level visual comparison will be added during runtime capture.

## Severity

- **P0** — identity/composition fundamentally wrong or broken.
- **P1** — material gap that substantially weakens the intended art direction.
- **P2** — quality gap that reduces craft/fidelity but does not destroy the concept.
- **P3** — optical polish.

## Findings

### VIS-001 — Primary artwork is an abstraction rather than production art
**Severity:** P1  
**Surface:** Hero  
**Expected:** A dominant, authored Oni image carrying material depth, facial detail, controlled menace and irezumi/Japanese-art specificity.  
**Actual:** The hero uses `oni-mask.svg` as a full-background lightweight SVG abstraction.  
**Root cause:** Production implementation substituted symbolic SVG artwork for the richer approved reference language.  
**Repair intent:** Produce a real hero artwork with explicit desktop/mobile crop contracts; use CSS only for atmosphere/overlay rather than for the main illustration.

### VIS-002 — Page rhythm falls back to conventional marketing blocks
**Severity:** P1  
**Surface:** Overall page structure  
**Expected:** Editorial/cinematic rhythm with differentiated visual modes and intentional tension/release.  
**Actual:** The implementation follows hero → fact band → three service cards → image/text belief block → two-column presence list → CTA.  
**Root cause:** Content architecture was implemented before a canonical page composition existed.  
**Repair intent:** Define section-level narrative roles and composition grammar before coding; avoid repeated generic marketing patterns.

### VIS-003 — Services use a default three-card grid
**Severity:** P1  
**Surface:** Services  
**Expected:** Capabilities expressed through a composition specific to Nexova's identity and narrative.  
**Actual:** `.services-grid { grid-template-columns: repeat(3,1fr) }` with three similar cards.  
**Root cause:** Component convenience overrode art direction.  
**Repair intent:** Replace equal-card presentation unless research shows a compelling reason; test editorial sequencing, staggered media/content, or a capability field.

### VIS-004 — Materiality is represented mainly by gradients/SVG texture references
**Severity:** P1  
**Surface:** Hero / belief / CTA  
**Expected:** Convincing lacquer, ink, paper, stone and atmospheric depth.  
**Actual:** Material cues are primarily gradients, SVG backgrounds and opacity.  
**Root cause:** No production asset bible existed.  
**Repair intent:** Split material into production artwork vs CSS-native surface treatment; reserve raster art for elements that genuinely need image-level detail.

### VIS-005 — Typography is technically coherent but not art-directed enough
**Severity:** P1  
**Surface:** Global  
**Expected:** A deliberate editorial type system that carries part of the identity.  
**Actual:** Display stack is system/editorial fallback (`Iowan Old Style`, Palatino, Book Antiqua, Baskerville, Georgia) and UI uses Inter/system sans.  
**Root cause:** Typography was selected pragmatically inside code rather than through a dedicated comparative type study.  
**Repair intent:** Evaluate up to three real typography systems using Typewolf/Fonts in Use references, licensing constraints and hero tests before Figma Golden.

### VIS-006 — Hero composition is code-led rather than art-led
**Severity:** P1  
**Surface:** Hero  
**Expected:** Integrated artwork/text relationship with deliberate image mass, asymmetry, depth and crop behavior.  
**Actual:** A conventional grid places copy and a secondary side block over a background image; visual hierarchy is generated primarily through type size and overlay gradients.  
**Root cause:** No approved high-fidelity composition proof preceded implementation.  
**Repair intent:** Create composition proof first; only then structure it in Figma and code.

### VIS-007 — Japanese influence risks becoming decorative annotation
**Severity:** P2  
**Surface:** Hero / decorative grammar  
**Expected:** Japanese influence embedded in composition, image treatment, materiality and restraint.  
**Actual:** Japanese vertical text/seal motifs are explicit surface decorations while the larger composition remains conventional.  
**Root cause:** Motifs were easier to transfer than the deeper compositional language of the references.  
**Repair intent:** Reduce decorative signifiers and increase structural influence: crop, asymmetry, negative space, rhythm, image framing and material behavior.

### VIS-008 — Negative space is present but not used as a dramatic system
**Severity:** P2  
**Surface:** Global  
**Expected:** Controlled voids that create tension, hierarchy and ceremonial pacing.  
**Actual:** Spacing is generous but regularized through conventional grids and section padding.  
**Root cause:** Spacing tokens were used without a specific negative-space composition contract.  
**Repair intent:** Define visual silence as part of each section role, not as generic padding.

### VIS-009 — Motion language is effectively absent
**Severity:** P1  
**Surface:** Global  
**Expected:** Restrained but intentional ceremonial motion with one signature sequence.  
**Actual:** Interactions are limited to short CSS transitions; no narrative motion architecture exists.  
**Root cause:** Motion was not designed before implementation.  
**Repair intent:** Author a Motion Spec after Figma direction lock; CSS for microstates, Motion for local interactions, GSAP/ScrollTrigger for one signature sequence.

### VIS-010 — Mobile behavior is adaptation, not a dedicated visual translation
**Severity:** P1  
**Surface:** Responsive  
**Expected:** Mobile preserves focal art, hierarchy and brand character while reducing ornament/motion appropriately.  
**Actual:** CSS primarily collapses grids, hides the hero side element, shifts the background position and stacks content.  
**Root cause:** Mobile was solved in CSS after desktop structure existed.  
**Repair intent:** Canonical 390px Figma design with specific crop, type wrapping, ornament-density and motion decisions before implementation.

### VIS-011 — Existing shared design tokens should be preserved selectively, not treated as final
**Severity:** P2  
**Surface:** Design system  
**Expected:** Evidence-backed semantic foundations derived from the Golden design.  
**Actual:** The current token layer is a sound academic substrate but includes choices made before premium art direction was fully translated.  
**Root cause:** Tokens were created to support the first implementation.  
**Repair intent:** Keep stable primitives where they survive the Golden design; revise only values/roles invalidated by approved visual work.

### VIS-012 — Current site can still read as "dark premium agency" without Nexova-specific art
**Severity:** P1  
**Surface:** Brand distinctiveness  
**Expected:** The identity remains recognizable even if the wordmark is temporarily hidden.  
**Actual:** Much of the uniqueness currently depends on black/oxblood/gold, serif scale and Japanese decorative cues—patterns that can appear in many dark-premium generated sites.  
**Root cause:** Identity was distilled into motifs/colors more successfully than into a unique compositional system.  
**Repair intent:** Make authorship come from the interaction of hero artwork, typography, asymmetric composition, section rhythm and signature motion rather than from palette/ornament alone.

## Existing strengths to preserve

The current implementation already provides:
- valid React/Vite/TypeScript architecture;
- semantic sections/navigation;
- accessible focus baseline;
- reduced-motion baseline;
- responsive breakpoints;
- source-backed corporate copy;
- a coherent shared color/token substrate;
- clean separation between website and backoffice;
- a recoverable academic implementation.

The premium pass must not throw away these strengths merely to achieve visual novelty.

## Audit conclusion

The first implementation is not failing because it lacks enough CSS. It is failing because the workflow compressed a high-fidelity visual identity directly into symbolic assets and conventional frontend structures without an intermediate canonical design.

The repair path is therefore:

```
approved identity
→ reference intelligence
→ direction contract
→ production asset bible
→ high-fidelity composition proof
→ Figma Golden
→ code
→ runtime visual audit
```

Do not attempt to fix the current page by incrementally decorating the existing layout.
