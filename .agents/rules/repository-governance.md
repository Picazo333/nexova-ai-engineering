# Repository Governance Rule

**Scope:** always active for coding agents operating in this repository.

## Rule
1. Preserve the top-level folder responsibilities defined by the repository template.
2. Treat `CONTEXT.md` as the canonical company briefing; do not invent or silently resolve company facts.
3. Treat historical strategy/blueprints as research/candidate input unless a current ADR or project-state artifact explicitly promotes a decision.
4. Keep coding-agent infrastructure in `.agents/`; do not place repository-development rules inside product `agents/` or `skills/`.
5. Implement the simplest architecture that satisfies the current requirement and quality contract.
6. Do not add material infrastructure without an activation trigger and explicit developer confirmation.
7. If a change affects a claim already supported by evidence, mark that evidence for freshness review and re-run the affected verification.
8. Do not claim PASS for a check that was not executed.

## Applies to
All files and all coding-agent sessions.

## Escalate
Escalate rather than infer when:
- primary sources conflict materially;
- a change would alter authority boundaries;
- a destructive/irreversible operation is required;
- the requested implementation needs a new material architecture decision.
