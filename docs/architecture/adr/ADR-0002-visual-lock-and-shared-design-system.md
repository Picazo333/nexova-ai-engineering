# ADR-0002 — Oni Nocturne Oxblood visual lock and shared design system

**Status:** ACCEPTED  
**Date:** 2026-09-21

## Context
The 4g-006 milestone requires two separate UIs. Thirty visual-reference boards were explored after the user selected the Oni direction. Both applications now need a stable implementation language without turning the repository into a design-framework project.

## Decision
- Lock **Oni Nocturne Oxblood** for the current milestone.
- Treat final boards 26–30 as the visual implementation authority and 01–25 as supporting references.
- Extract only actually shared foundations into `packages/design-system`: colour/type tokens, focus/button primitives and lightweight symbolic SVG assets.
- Keep website/backoffice page structures separate.
- Do not commit the full high-resolution 30-board archive as a runtime dependency.

## Rationale
The two required UIs create real reuse for foundations, but not for their layouts. This gives future milestones consistent identity without premature component abstraction or a 50MB+ visual archive in the application graph.

## Consequences
- Public website can remain cinematic and editorial.
- Backoffice can retain the identity at much lower ornament density.
- Future redesign requires a new explicit decision; this lock does not freeze the Nexova product roadmap.
