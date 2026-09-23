# Nexova Premium Website — Reference Matrix

**Status:** RESEARCH LOCK v1  
**Scope:** Website only  
**Rule:** References contribute mechanisms, not identity. Oni Nocturne Oxblood remains the visual authority.

## Research conclusion

The useful pattern is not "dark website + red accent". That space is already crowded. Nexova needs a more specific grammar built from:

1. cinematic art direction without sacrificing corporate legibility;
2. editorial typography with strong serif/sans tension;
3. asymmetric composition and controlled negative space;
4. a hero that becomes the transition into the page rather than a static poster;
5. a restrained scroll signature instead of animation everywhere;
6. mobile behavior designed as a translation, not a collapse.

The references below were selected because each answers a specific production question.

---

## Lapa Ninja — marketing composition references

### REF-L01 — Flesh and Bones

**Source:** Lapa Ninja, 2026  
**Category:** Studio / Agency / Creative / Marketing  
**Observed metadata:** black/red, heavy/handwriting font collection, full-site recording available.

**Extract**
- willingness to let one visual language dominate the page;
- cinematic confidence and strong art-to-interface relationship;
- black/red can work when the visual system is materially specific rather than a generic luxury palette;
- section identity can be stronger than generic card modularity.

**Do not copy**
- chaotic creative-studio energy;
- handwriting;
- entertainment-industry posture;
- visual noise.

**Nexova application**
Use as evidence that dramatic art can coexist with navigation/content, but Nexova must be more controlled, legible and B2B.

### REF-L02 — darkroom.engineering

**Source:** Lapa Ninja, 2025  
**Category:** Studio / Creative  
**Observed metadata:** black/red, motion-rich digital work, WebGL positioning, heavy/condensed/mono typography.

**Extract**
- technical/motion capability can become part of brand expression;
- red/black mode can feel engineered rather than decorative;
- condensed/mono accents can create operational tension against a stronger display system;
- motion should communicate technical confidence.

**Do not copy**
- developer-studio identity;
- WebGL-for-WebGL's-sake;
- heavy technical typography as primary voice.

**Nexova application**
Use as motion/engineering reference, not brand reference.

### REF-L03 — SVZ

**Source:** Lapa Ninja, 2025  
**Category:** Studio / Agency / Creative  
**Observed metadata:** black/red, PP Editorial New + KMR Waldenburg.

**Extract**
- editorial serif can carry premium authority without looking heritage-only;
- red/black can remain sophisticated when typography and whitespace do most of the work;
- typography should carry visual identity before decoration.

**Do not copy**
- agency self-promotion structure;
- award-language framing;
- direct typographic imitation.

**Nexova application**
Strongest typography/composition reference among the Lapa set.

### REF-L04 — 27b

**Source:** Lapa Ninja, 2024  
**Category:** Studio / Creative / Agency  
**Observed metadata:** black/red, Neue Haas Unica, Framer.

**Extract**
- strict grotesk systems can keep expressive imagery under control;
- black/red does not require ornamental overload;
- a neutral type system can allow art direction to remain the dominant voice.

**Do not copy**
- studio portfolio structure;
- generic full-service agency language.

**Nexova application**
Useful counterweight if the serif-led direction becomes too theatrical.

---

## Mobbin web — UX behavior reference

### REF-M01 — Navigation / menu / flow behavior

**Source:** Mobbin web library  
**Use:** UX maturity, not art direction.

Mobbin's public library exposes shipped screens, UI elements and end-to-end flows, including categories such as Sidebar, Button, Dialog, Tabs and navigation-adjacent patterns. The website also provides flow playback/prototypes for studying interaction in context.

**Extract**
- navigation should use familiar interaction conventions even when art direction is unusual;
- mobile menu behavior must remain predictable;
- interaction states should be legible before they are branded;
- site-level navigation should not become experimental merely because the hero is cinematic.

**Do not copy**
- product-app visual language;
- dashboards or app chrome into the marketing site.

**Nexova application**
Use Mobbin manually during Figma/runtime QA to sanity-check:
- desktop nav hierarchy;
- mobile menu opening/closing;
- active/focus states;
- interaction target sizing;
- predictable dismissal and return paths.

**Note**
The free web surface is being used intentionally; no Mobbin MCP/Pro dependency is required for this track.

---

## Typography references

### REF-T01 — Editorial New + neutral grotesk

**Sources:** Typewolf + SVZ/Lapa  
**Observed pairing evidence:** Editorial New is commonly paired with modern sans/grotesk systems; Typewolf documents Editorial New with Space Grotesk and other contemporary pairings.

**Strength**
- narrow editorial authority;
- dramatic at large sizes;
- strong contrast against a neutral sans;
- compatible with Oni's ceremonial/editorial identity.

**Risk**
- can become predictable "premium agency" typography if overused;
- license cost may be undesirable.

**Use**
Reference direction, not committed font.

### REF-T02 — Calligraphic serif + mono/grotesk contrast

**Source:** Typewolf example: GT Sectra + GT Pressura Mono.

**Strength**
- human/calligraphic form against system/technical voice;
- mirrors Nexova's human judgment × operational intelligence tension;
- could give utility text a distinct system voice.

**Risk**
- too stylized if both faces compete;
- licensing.

**Use**
Conceptual pairing model.

### REF-T03 — Same-skeleton serif/sans family logic

**Source:** Typewolf example: Freight Big + Freight Sans.

**Strength**
- editorial warmth and interface clarity with structural coherence;
- lower risk of visual fragmentation;
- good for a corporate site that still needs drama.

**Risk**
- can become too conventional if composition is weak.

**Use**
Fallback direction if the more expressive pairing becomes theatrical.

### Typography decision rule

Figma hero test will compare no more than three systems:

1. **Editorial tension** — expressive serif + restrained grotesk.
2. **Human/system tension** — calligraphic/editorial serif + mono/grotesk utility layer.
3. **Coherent family** — related serif/sans skeleton.

No font is purchased before a clear winner exists. A free/licensed-safe substitute may be used if visual loss is small.

---

## 21st.dev — mechanism references

### REF-21-01 — Scroll media expansion hero

**Category:** hero / scroll-driven transition

**Extract**
The hero can become the transition into the page rather than a static block followed by another block.

**Nexova use**
Potential foundation for the signature GSAP sequence:
- Oni begins dominant;
- first scroll changes framing/depth;
- the composition yields into manifesto/capability content.

**Constraint**
No scroll hijacking. Native scroll remains authoritative.

### REF-21-02 — Smooth Scroll Hero / restrained parallax

**Category:** hero depth

**Extract**
Subtle multi-layer movement can produce depth without resizing everything.

**Nexova use**
Candidate fallback if the more structural media-expansion concept is too expensive or distracting.

### REF-21-03 — Sticky / pinned narrative reveal

**Category:** scroll choreography

**Extract**
Pinning is effective only when the viewport hold has a meaningful narrative payoff.

**Nexova use**
A single bounded pinned sequence may work for Hero → Manifesto, but the page should not repeatedly trap scroll.

### REF-21-04 — Text reveal

**Category:** motion typography

**Extract**
Mask/reveal patterns can add ceremony without turning copy into a gimmick.

**Nexova use**
Use for section-entry emphasis, never for core reading text that must wait for animation.

### REF-21-05 — Parallax layering

**Category:** depth

**Extract**
Transform-based parallax can separate foreground smoke, artwork and typography while staying compositor-friendly.

**Nexova use**
Potentially use subtle parallax for smoke/peony/oni planes.

### REF-21-06 — IntersectionObserver / CSS-scroll-driven reveals

**Category:** performance mechanism

**Extract**
Entry reveals should prefer observer/CSS-native mechanisms where possible instead of continuous JS scroll listeners.

**Nexova use**
Keep GSAP focused on the one signature sequence; simpler reveals should remain cheaper.

---

# Surviving high-signal ideas

The research pool is reduced to **7 concepts**:

1. **Hero-as-transition**, not hero-as-static-poster.
2. **One dominant visual mass** with controlled supporting layers.
3. **Editorial serif / restrained system voice tension**.
4. **Asymmetry + negative space** instead of generic centered SaaS composition.
5. **Single signature pinned/scroll sequence**, no repeated scroll theater.
6. **Familiar navigation behavior beneath unusual art direction**.
7. **Transform/observer/CSS-first motion for non-signature effects**.

Everything else is reference noise.

# Explicit rejections

Do not import:
- generic red/black agency templates;
- portfolio-site work grids;
- WebGL as a status symbol;
- smooth-scroll libraries that replace native scroll by default;
- typography chosen solely because a reference uses it;
- Tailwind/shadcn dependency assumptions from 21st examples;
- Mobbin product UI chrome into the marketing site.

# Research gate

**REFERENCE_INTELLIGENCE_PASS = TRUE**

Next artifact:
`DIRECTION_CONTRACT.md`.
