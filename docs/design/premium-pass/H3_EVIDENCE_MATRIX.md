# H3 Evidence Matrix — Nexova Premium Website

**Status:** BLOCKED_EXTERNAL — INTERNAL H3 GATES PASS  
**Gate:** H3 Runtime Approval  
**Candidate implementation commit:** `f10cd71572ea3b5883b9bf746f48d4cb04afbc36`  
**GitHub Actions run:** `35929968292` — **SUCCESS**  
**Evidence artifact:** `website-premium-h3` / artifact `10780717461`  
**Evidence rule:** No PASS without an observable artifact tied to the exact implementation commit.

| Requirement | Verification method | Evidence artifact | Commit/run | Status |
|---|---|---|---|---|
| 1440 desktop fidelity | deterministic runtime screenshot + Figma comparison | `runtime-1440.png` + H2 Golden | f10cd715 / 35929968292 | PASS |
| 1024 responsive | browser/runtime capture + overflow assertion | `runtime-1024.png` + `browser-audit.json` | f10cd715 / 35929968292 | PASS |
| 768 responsive | browser/runtime capture + overflow assertion | `runtime-768.png` + `browser-audit.json` | f10cd715 / 35929968292 | PASS |
| 430 responsive | browser/runtime capture + overflow assertion | `runtime-430.png` + `browser-audit.json` | f10cd715 / 35929968292 | PASS |
| 390 mobile fidelity | deterministic runtime screenshot + Figma comparison | `runtime-390.png` + H2 Golden | f10cd715 / 35929968292 | PASS |
| Horizontal overflow | CDP assertion at 1440/1024/768/430/390 | `browser-audit.json` | f10cd715 / 35929968292 | PASS |
| TypeScript | repo typecheck | GitHub Actions | f10cd715 / 35929968292 | PASS |
| Production build | workspace build | GitHub Actions | f10cd715 / 35929968292 | PASS |
| Runtime health | start dev runtime + browser navigation | GitHub Actions + browser audit | f10cd715 / 35929968292 | PASS |
| Console errors | CDP Runtime + Log capture | `browser-audit.json`: `consoleErrors: []` | f10cd715 / 35929968292 | PASS |
| Keyboard navigation | synthetic Tab interaction | `browser-audit.json` | f10cd715 / 35929968292 | PASS |
| Visible focus | computed `:focus-visible` + outline assertion | `browser-audit.json` | f10cd715 / 35929968292 | PASS |
| Mobile navigation | interactive open/close assertion | `browser-audit.json` | f10cd715 / 35929968292 | PASS |
| Reduced motion | emulated `prefers-reduced-motion: reduce` | `reduced-motion-390.png` + audit | f10cd715 / 35929968292 | PASS |
| No-JS readability | JS-disabled accessibility-tree assertion | `no-js-390.png` + audit | f10cd715 / 35929968292 | PASS |
| Axe critical | axe-core 4.10.3 | `axe.json`: critical = 0 | f10cd715 / 35929968292 | PASS |
| Axe serious | axe-core 4.10.3 | `axe.json`: serious = 0 | f10cd715 / 35929968292 | PASS |
| A1 delivery | source/network/build inspection | optimized Golden runtime derivative; heavy master not imported | f10cd715 | PASS |
| A2 delivery | source/network/build inspection | optimized Golden runtime derivative; heavy master not imported | f10cd715 | PASS |
| LCP | Lighthouse | 2.5 s | f10cd715 / 35929968292 | PASS |
| CLS | Lighthouse | 0.061 | f10cd715 / 35929968292 | PASS |
| INP | representative proxy where lab INP unavailable | TBT 0 ms; no long-task interaction blocker observed | f10cd715 / 35929968292 | PASS WITH LAB LIMITATION |
| Hero→Manifesto contract | runtime motion audit against REST→SEPARATE→YIELD→RELEASE storyboard | source + runtime review | f10cd715 | PASS |
| P0 visual findings | independent red team + recapture | `H3_RED_TEAM_2026-09-23.md` + repaired captures | f10cd715 | PASS — 0 open |
| P1 visual findings | independent red team + recapture | bounded repair closed internal P1 findings | f10cd715 | PASS — 0 internal open |
| P2 visual findings | Figma comparison + bounded repair | Golden philosophy material field restored | f10cd715 | PASS — 0 open |
| Vercel preview | Vercel deployment | GitHub Vercel status targets historical `nexova-premium-v0-challenger` project and fails | f10cd715 | BLOCKED_EXTERNAL |
| Dependency discipline | package/build diff | no production dependency added; axe is ephemeral CI-only auditor | f10cd715 | PASS |
| Product truth | source/content comparison | `CONTEXT.md` / `PRODUCT_TRUTH.md` audit | f10cd715 | PASS |
| 4Geeks rubric | Control Tower R01–R22 | Full refresh belongs to metaplan S5 after website + backoffice + integrated QA; R18/R21 cannot be final on Codex implementation branch | deferred to S5 | DEFERRED_BY_PLAN |

## Measured final candidate

```yaml
candidate: f10cd71572ea3b5883b9bf746f48d4cb04afbc36
github_actions_run: 35929968292
ci: PASS
browser_audit: PASS
horizontal_overflow:
  1440: false
  1024: false
  768: false
  430: false
  390: false
console_errors: 0
keyboard: PASS
visible_focus: PASS
mobile_navigation: PASS
no_js: PASS
reduced_motion: PASS
axe:
  engine: axe-core 4.10.3
  critical: 0
  serious: 0
  total_violations: 0
lighthouse:
  performance: 0.96
  accessibility: 1.00
  fcp: 1.5s
  lcp: 2.5s
  cls: 0.061
  tbt: 0ms
```

## H3 pass rule

H3 can be presented for final user approval only when:
- P0 = 0;
- P1 = 0;
- P2 = 0;
- required technical checks PASS;
- Vercel preview is reachable;
- evidence references the exact candidate commit.

All internal conditions are now satisfied. The **only current H3 blocker is the external Vercel project/auth configuration**.

## Rubric sequencing clarification

The authoritative Control Tower rubric is R01–R22 on branch `assignment/4g-006-ai-driven-engineering`.

A full 22/22 rerun is intentionally **not** performed at website-only H3 because:
- R18 requires the final assignment implementation on `feature/agent-memory-bank`;
- R20 requires PR #1 from that branch to `main`;
- R21 requires the final website and backoffice screenshots in that PR;
- the approved metaplan places the rubric refresh at S5, after S2 Backoffice Premium and S4 Integrated QA.

The website-impacting technical criteria are nevertheless revalidated here; the final academic score remains an S5 gate.
