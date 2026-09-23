# Independent Review Brief — Nexova / 4Geeks Premium Website Workflow

## Purpose

Audit the workflow used to take an academically valid Nexova website toward a professional premium implementation.

Do **not** assume the current workflow is correct merely because it is documented. The goal is to identify:
- unnecessary complexity;
- missing controls;
- wasted paid-tool usage;
- weak handoffs;
- places where quality could improve;
- places where the workflow should become simpler.

Return a proposed improved workflow, not implementation.

## Project context

- Course/project: 4Geeks, Nexova, milestone 4g-006 AI-driven Engineering.
- Academic baseline already reached 22/22 blocking rubric criteria before the premium extension.
- The premium extension is optional quality work and must never endanger the academic baseline.
- Stack is locked to React + Vite + TypeScript + npm workspaces.
- Website visual identity evolved into a dark editorial direction combining brutalist structure, traditional-Japanese-informed composition, abyssal abstraction, organic skin-like substrate and crimson-soaked fibrous material.
- Figma H2 Golden is approved and locked.
- Production implementation has not yet been accepted at H3.
- v0 has been used once as a bounded implementation challenger and is now closed for cost reasons.
- Codex is intended to own production implementation.
- GitHub/CI/Vercel are intended to own repository/build/deployment verification.

## What went well

1. Academic baseline was preserved with a recovery branch.
2. Premium work was isolated on `design/oni-nocturne-premium-pass`.
3. Product truth and visual authority were explicitly separated.
4. A strict Direction Contract and Asset Contract were eventually created.
5. H1 and H2 human gates prevented implementation from silently redefining the visual direction.
6. Figma became the canonical visual source of truth.
7. The original React/Vite/TypeScript architecture was protected from generator-driven framework migration.
8. v0 worked on an isolated branch and was not auto-merged.
9. v0 output was classified KEEP/ADAPT/REJECT instead of treated as authority.
10. Reduced-motion/no-JS readability became an explicit contract.
11. A cost-efficiency rule was added after observed v0 overspend.
12. The current plan separates source assets from optimized runtime delivery.

## What went poorly

1. Early image/moodboard generations repeatedly misunderstood the requested artifact:
   - illustration instead of moodboard;
   - literal demon/tattoo imagery;
   - aggressive fantasy/smoke reading;
   - inconsistent candidate independence.
2. The visual contract became sufficiently rigid only after multiple bad generations.
3. The initial toolchain was broader than necessary:
   - SuperDesign/Spline/Motion/v0/Figma/GSAP/Mobbin/etc. were all planned before their necessity was proven.
4. v0 was initially imported incorrectly:
   - empty workspace;
   - wrong/unclear base branch;
   - no repo materialized.
5. v0 consumed approximately US$5 while part of the interaction was repository/environment verification that cheaper tools could perform.
6. Some state documents became stale after H1/H2 approval, creating contradictory booleans/next-state text.
7. The original plan split v0 into three challenges, but the useful result could be obtained in one bounded branch/output; the initial granularity was not cost-optimal.
8. v0 generated technically sound generic IntersectionObserver reveals, but these did not satisfy the approved signature-motion narrative.
9. The v0 branch retained legacy page structures because it was a bounded challenger; therefore it is not safe to merge wholesale.
10. The current runtime asset masters are heavier than appropriate for direct web delivery.
11. A Vercel failure exists on the v0 challenger commit and has not yet been classified; this should be handled outside v0.
12. Tool usage/value was not tracked quantitatively from the beginning.

## Major deviations from the original premium plan

### Planned but skipped/deferred
- Spline spatial spike: no evidence yet that 3D is necessary.
- SuperDesign composition challenger: H1 was resolved without needing it.
- Motion package: not justified yet; CSS may handle local motion.
- additional generative asset tiers: unnecessary once A1/A2 were locked.

### Planned and completed
- safety baseline;
- context/product truth;
- visual direction contract;
- asset contract;
- H1;
- Figma foundations;
- desktop/mobile Golden;
- motion storyboard;
- H2;
- v0 challenger;
- challenger review.

### Changed
- v0 moved from “three possibly iterative challenges” to one bounded challenger branch and is now closed.
- cost efficiency is now an explicit gate.
- state reconciliation and paid-tool preflight are now mandatory before agent handoff.
- H3 evidence should become a requirement→verification→artifact matrix.

## Current intended tool allocation

- ChatGPT / orchestration: planning, audits, contracts, synthesis.
- GitHub: source inspection, branch/commit state, remote evidence.
- Figma Professional: canonical visual authority.
- Mobbin: bounded UX/reference sanity, not styling authority.
- Codex: production implementation/refactor/debugging.
- GSAP + ScrollTrigger: exactly one Hero → Manifesto signature sequence if needed for the approved storyboard.
- CSS: default microinteraction layer.
- Playwright/browser tooling: deterministic responsive/runtime evidence.
- axe: accessibility.
- Lighthouse or equivalent: performance evidence.
- GitHub Actions: repeatable CI.
- Vercel: preview/deployment verification.
- v0: CLOSED unless a future unresolved visual problem passes an explicit cost gate.

## Current known reusable lessons

Potential Noema capabilities:
- spend-aware tool routing;
- premium-tool stop-loss;
- authority/state graph;
- tool-trigger registry;
- run-level spend telemetry;
- challenger→production transition state.

Potential Skill Foundry candidates:
- external-codegen-repo-preflight;
- visual-artifact-contract;
- creative-candidate-controller;
- challenger-diff-evaluator;
- responsive-image-delivery;
- design-runtime-fidelity-audit;
- motion-contract-auditor;
- definition-of-done-evidence-matrix;
- project-state-reconciler.

## Questions the reviewer must answer

1. Which phases are redundant or can be collapsed?
2. Which tool calls should never be delegated to variable-cost visual/code generators?
3. Is Figma positioned correctly as authority?
4. Is v0 still useful in this pipeline; if yes, exactly when and with what budget?
5. Is Codex the correct production owner?
6. Which validation gates are missing or too subjective?
7. How should visual fidelity be measured without creating a heavyweight visual-regression platform?
8. Which process failures are local accidents versus reusable systemic lessons?
9. Which Noema capabilities are worth implementing versus over-engineering?
10. Which Skill Foundry candidates are atomic/reusable enough to become real skills?
11. What is the minimum professional workflow that preserves the same quality target?
12. Propose an improved version with:
    - phases;
    - authority chain;
    - tool routing;
    - cost gates;
    - DoDs;
    - evidence;
    - rollback;
    - human gates;
    - explicit stop conditions.

## Required response format

1. Executive diagnosis.
2. What to keep.
3. What to remove.
4. What to change.
5. Risk analysis.
6. Proposed optimized workflow.
7. Cost-control model.
8. Noema candidates.
9. Skill Foundry candidates.
10. Delta versus current workflow.

Do not implement code and do not assume that adding tools improves quality.
