# Nexova Premium Website — v0 Challenger Evaluation

**Status:** CLOSED / ARCHIVED  
**Gate:** Completed Post-H2 challenger evaluation

## Current-state note

This document is the archived evaluation contract used during the v0 challenger phase. The phase is CLOSED. Current execution state is governed by `PROJECT_STATE.md` and `LOCKED_EXECUTION_PLAN.md`.

## Evaluation rule

v0 is not judged by whether the output is visually attractive in isolation.

It is judged by whether it provides implementation value **without weakening the Figma Golden Lock, product truth, architecture, accessibility, or performance discipline**.

## Automatic rejection conditions

Reject an output if any of the following occurs:

- migrates React/Vite to another framework;
- introduces Tailwind/shadcn without explicit approval;
- changes approved factual copy;
- invents proof/testimonials/metrics;
- turns the Hero into a generic centered SaaS pattern;
- replaces the editorial capability language with cards/bento;
- weakens A1/A2 asset roles;
- adds uncontrolled scroll hijacking;
- removes reduced-motion support;
- materially harms mobile readability;
- introduces unjustified dependencies;
- rewrites unrelated repository areas.

## Challenge A — Hero

PASS requires:
- composition still maps to the H2 Golden;
- A1 remains dominant image mass;
- proposition is immediately readable;
- header remains conventional and usable;
- CTA hierarchy remains clear;
- no generic AI/SaaS visual grammar;
- mobile strategy is explicit;
- image/LCP strategy is technically credible.

## Challenge B — Editorial section

PASS requires:
- inverse bone field is preserved;
- asymmetry remains authored;
- material imagery is not wallpaper;
- typography remains primary;
- no unnecessary JS;
- no generic split-card abstraction;
- mobile crop/rhythm is intentional;
- accessibility contrast remains defensible.

## Challenge C — Mobile

PASS requires:
- mobile is not desktop stacking;
- 390 layout has no horizontal overflow;
- art crop is intentionally changed;
- ornament/motion are reduced;
- semantic hierarchy is preserved;
- navigation remains predictable;
- reduced motion has a final readable state.

## Review output

For each challenger record:

```yaml
challenge:
classification: KEEP | ADAPT | REJECT
useful_mechanics:
rejected_mechanics:
dependency_impact:
figma_deviations:
accessibility_findings:
performance_findings:
codex_takeaways:
```

## Exit condition

The v0 phase is complete when:
- V0-A has a classification;
- V0-B has a classification;
- V0-C has a classification;
- selected mechanics are translated into explicit Codex implementation instructions;
- no v0 code is merged automatically.
