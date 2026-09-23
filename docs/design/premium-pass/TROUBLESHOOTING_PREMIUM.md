# Nexova Premium Extension — Troubleshooting & Process Errors

**Status:** ACTIVE CASE LOG  
**Date:** 2026-09-23  
**Scope:** Premium website workflow only  
**Purpose:** Preserve meaningful failures, their causes, fixes, prevention rules, and reusable lessons.

This log follows the canonical 4Geeks troubleshooting schema:

```
SYMPTOM
CAUSE
FIX
LESSON
PREVENTION
```

---

## E01 — Moodboards lost the approved visual universe

**SYMPTOM**  
Several generated rounds stopped behaving like a moodboard/universe and collapsed into a single illustration, collage, literal demon/tattoo image, or aggressive fantasy composition.

**CAUSE**  
The generation request was carrying too much aesthetic intent but not enough rigid artifact-role constraints. “Japanese + demon + skin + brutalism” was repeatedly interpreted as subject matter instead of a system of typography, materials, palette, composition, imagery and texture references.

**FIX**  
Create and lock a stricter visual contract:
- moodboard ≠ hero art;
- demon is only a partially legible motif;
- skin is substrate/texture, not depicted anatomy;
- wet crimson cotton is a material family;
- black/bone/skin/crimson/ochre palette;
- brutalism is structural;
- traditional Japanese influence is compositional/material, not cliché iconography.

**LESSON**  
Visual intent must be represented as an artifact contract, not only as descriptive prompting.

**PREVENTION**  
Before any high-variance image generation, define:
- artifact type;
- compositional job;
- allowed motifs;
- forbidden readings;
- palette;
- material behavior;
- safe zones/crops;
- candidate budget;
- explicit rejection tests.

---

## E02 — Asset generation was not sufficiently independent

**SYMPTOM**  
Some rounds drifted by deriving one candidate from the previous visual direction rather than producing independent alternatives.

**CAUSE**  
Candidate independence was not explicit enough in the generation contract.

**FIX**  
Require candidates to be independent explorations under the same locked identity, not revisions of each other unless the step is explicitly a repair round.

**LESSON**  
“More candidates” does not equal exploration if they share the same local optimum.

**PREVENTION**  
Separate:
- exploration round = independent candidates;
- selection;
- repair round = only selected winner.

---

## E03 — Generated demon read as aggressive “evil smoke”

**SYMPTOM**  
A later hero direction became too literal/aggressive and read as a malicious entity emerging from smoke.

**CAUSE**  
The recognizable character signal was too strong: full face/eyes/mouth and foreground agency overwhelmed the intended premium ambiguity.

**FIX**  
Lock demon visibility to approximately 20–30%, dissolve anatomy into the abyssal field, forbid full eye pair/full mouth/full face, increase material/negative-space dominance.

**LESSON**  
For premium abstract identities, motif legibility is a controllable dial. More recognizability can reduce sophistication.

**PREVENTION**  
Use a motif-legibility threshold and rejection rule:
“If the subject can be identified immediately as a literal demon emerging from smoke, it is too explicit.”

---

## E04 — Figma state was correct, but some repository documents became stale

**SYMPTOM**  
Later inspection found old state flags such as `FIGMA_GOLDEN_LOCK: false` / `H1_APPROVED: false` in documents whose narrative had already been superseded.

**CAUSE**  
Milestone approvals were appended to some state files without reconciling all prior embedded state blocks.

**FIX**  
Add a state-reconciliation preflight before every agent handoff.

**LESSON**  
Append-only documentation can create contradictory authority for coding agents.

**PREVENTION**  
Before handoff:
1. identify canonical state fields;
2. search for stale duplicates;
3. reconcile status blocks;
4. ensure one current “next action.”

---

## E05 — v0 import initially produced an empty workspace

**SYMPTOM**  
v0 reported:
- `/vercel/share/v0-project` was not a Git repository;
- no `.git`;
- no `package.json`;
- no `docs/`;
- Preview could not start.

**CAUSE**  
The first import attached to the wrong Vercel/Git context and effectively referenced `main` without materializing the repository into the v0 workspace.

**FIX**  
Re-import as a new Vercel project using:
- repository: `Picazo333/nexova-ai-engineering`;
- base branch: `design/oni-nocturne-premium-pass`;
- root: repository root;
- verify governing files before generation.

**LESSON**  
A paid code-generation tool must pass a zero/low-cost repository preflight before any generation request.

**PREVENTION**  
Mandatory external-generator preflight:
- repo exists;
- expected branch;
- `package.json`;
- target workspace package;
- governing contracts;
- working directory;
- Git remote/base;
- no generation until PASS.

---

## E06 — v0 was used for tasks that did not justify variable-cost inference

**SYMPTOM**  
Approximately US$5 of v0 usage accumulated before the challenger provided proportional incremental value.

**CAUSE**  
The workflow allowed v0 to participate in inspection, environment verification and potential build diagnosis instead of limiting it to the one task where its visual/frontend generation could add differentiated value.

**FIX**  
Close v0 after one bounded challenger output. Route:
- Git/repo inspection → GitHub;
- build/type/debug → Codex + CI;
- deployment → Vercel;
- visual authority → Figma;
- v0 → optional bounded challenger only.

**LESSON**  
Tool capability is not the same as tool-economic suitability.

**PREVENTION**  
Add a Premium Tool Cost Gate:
- purpose;
- expected unique value;
- cheaper adequate alternative;
- maximum calls/iterations;
- stop-loss budget;
- explicit exit condition.

---

## E07 — v0 challenger output was useful but not a safe production merge

**SYMPTOM**  
The challenger implemented Hero/Philosophy/Mobile mechanics, but the branch still contained legacy page patterns such as the three-card services layout and other pre-H2 structures.

**CAUSE**  
The challenger scope was intentionally bounded and therefore did not rebuild the entire site from the H2 Golden.

**FIX**  
Classify v0 output as `KEEP / ADAPT / REJECT`; do not merge wholesale. Production starts from the approved premium base and ports only selected mechanics.

**LESSON**  
A challenger branch is evidence/reference, not automatically an implementation branch.

**PREVENTION**  
Every challenger must declare:
- authority level;
- allowed surfaces;
- merge policy;
- extraction policy;
- evaluation rubric.

---

## E08 — v0 motion was technically valid but violated the signature-motion contract

**SYMPTOM**  
v0 used IntersectionObserver + CSS reveal transitions.

**CAUSE**  
It optimized for a safe generic implementation rather than the approved REST → SEPARATE → YIELD → RELEASE narrative.

**FIX**  
Keep only the progressive-enhancement/reduced-motion principle. Replace generic reveals with the single locked Hero → Manifesto choreography during production.

**LESSON**  
Technical correctness does not imply design fidelity.

**PREVENTION**  
Motion must be tested against a named narrative contract, not only against “animation exists.”

---

## E09 — High-resolution master assets are too heavy for direct runtime delivery

**SYMPTOM**  
A1/A2 production masters are materially heavier than desirable runtime assets; A2 is approximately 1.5MB and A1 approximately 0.5MB per master.

**CAUSE**  
Correctly preserved high-resolution source assets were imported directly during prototyping.

**FIX**  
Before H3:
- keep masters as source;
- generate AVIF/WebP runtime derivatives;
- responsive `srcset`/`sizes`;
- explicit dimensions;
- priority only for LCP image;
- lazy load later imagery.

**LESSON**  
Source-asset quality and runtime-delivery quality are separate contracts.

**PREVENTION**  
Every approved raster asset gets both:
- MASTER contract;
- DELIVERY contract.

---

## E10 — Toolchain planning was broader than the value ultimately required

**SYMPTOM**  
The premium plan considered SuperDesign, Spline, Motion, GSAP, Mobbin, v0, Figma, Codex and multiple QA layers. Not all were needed to reach the current approved direction.

**CAUSE**  
The initial plan intentionally explored an industry-grade toolchain before enough evidence existed to know which tools would materially improve this specific site.

**FIX**  
Move optional tools behind evidence-triggered gates:
- Spline: skipped unless a proven spatial problem appears;
- SuperDesign: skipped after H1 direction was resolved without it;
- Motion package: add only if recurring local motion justifies it;
- GSAP: reserved for the one locked signature sequence;
- Mobbin: UX sanity reference, not visual authority;
- v0: challenger complete/closed.

**LESSON**  
A professional workflow is defined by correct tool selection, not by maximizing tool count.

**PREVENTION**  
Every optional tool requires a trigger and a stop condition.

---

## Current prevention rules

1. No paid/variable-cost generator without a preflight and budget.
2. One canonical authority chain must be machine-readable.
3. State reconciliation happens before every handoff.
4. Visual generators receive artifact contracts, not only aesthetic prose.
5. Challengers never merge automatically.
6. Masters and runtime derivatives are separate.
7. Optional tools are trigger-based, not mandatory-by-plan.
8. H3 evidence is generated from runtime, not inferred from source.
