# H3 Evidence Matrix — Nexova Premium Website

**Status:** PENDING EXECUTION  
**Gate:** H3 Runtime Approval  
**Evidence rule:** No PASS without an observable artifact tied to the exact implementation commit.

| Requirement | Verification method | Evidence artifact | Commit/run | Status |
|---|---|---|---|---|
| 1440 desktop fidelity | deterministic runtime screenshot + Figma comparison | screenshot + finding log | pending | PENDING |
| 1024 responsive | browser/runtime capture | screenshot + overflow assertion | pending | PENDING |
| 768 responsive | browser/runtime capture | screenshot + overflow assertion | pending | PENDING |
| 430 responsive | browser/runtime capture | screenshot + overflow assertion | pending | PENDING |
| 390 mobile fidelity | deterministic runtime screenshot + Figma comparison | screenshot + finding log | pending | PENDING |
| Horizontal overflow | automated browser assertion | assertion output | pending | PENDING |
| TypeScript | repo typecheck | command/CI output | pending | PENDING |
| Production build | workspace build | command/CI output | pending | PENDING |
| Runtime health | start preview + browser request | runtime evidence | pending | PENDING |
| Console errors | browser console capture | 0-error assertion | pending | PENDING |
| Keyboard navigation | manual/automated keyboard pass | checklist/log | pending | PENDING |
| Visible focus | browser interaction | screenshots/checklist | pending | PENDING |
| Mobile navigation | interactive browser pass | checklist/video/screenshot | pending | PENDING |
| Reduced motion | emulate prefers-reduced-motion | screenshot/assertion | pending | PENDING |
| No-JS readability | JS-disabled browser pass | screenshot/assertion | pending | PENDING |
| Axe critical | axe | report | pending | PENDING |
| Axe serious | axe | report | pending | PENDING |
| A1 delivery | network/source inspection | format/srcset/bytes evidence | pending | PENDING |
| A2 delivery | network/source inspection | format/srcset/bytes evidence | pending | PENDING |
| LCP | Lighthouse/equivalent | report | pending | PENDING |
| CLS | Lighthouse/equivalent | report | pending | PENDING |
| INP | representative measurement when available | report/note | pending | PENDING |
| Hero→Manifesto contract | runtime interaction against storyboard | capture + motion audit | pending | PENDING |
| P0 visual findings | visual QA | finding log | pending | PENDING |
| P1 visual findings | visual QA | finding log | pending | PENDING |
| P2 visual findings | visual QA | finding log | pending | PENDING |
| Vercel preview | deployment | preview URL | pending | PENDING |
| Dependency discipline | package diff | dependency audit | pending | PENDING |
| Product truth | source/content comparison | provenance audit | pending | PENDING |
| 4Geeks rubric | Control Tower / grader rerun | 22/22 evidence | pending | PENDING |

## H3 pass rule

H3 may be presented to the user only when:
- P0 = 0;
- P1 = 0;
- P2 = 0;
- required technical checks PASS;
- Vercel preview is reachable;
- evidence references the exact candidate commit.

P3 findings may remain only when documented and explicitly non-material.
