# Nexova Source of Truth

## Principle
Nexova separates **what a source is** from whether it is current guidance.

## Reference roles
- `PRIMARY_SOURCE` — original company/course source.
- `CANONICAL_STATE` — current Nexova operational/project state owned by this repo.
- `CURRENT_EVIDENCE` — verified current repository/runtime result.
- `DERIVED_VIEW` — summary, presentation, index or explanation derived from stronger sources.
- `HISTORICAL_RECORD` — valid evidence of an earlier decision/state, not automatically current guidance.
- `CANDIDATE` — potentially useful idea not promoted into current architecture/roadmap.
- `QUARANTINED_CONFLICT` — materially contradictory claims that remain unresolved.

## Current precedence
For company/domain facts:
1. `CONTEXT.md` and captured primary supporting company material;
2. explicit current ADRs/approved project decisions;
3. verified current implementation/evidence;
4. historical strategy/selection analysis;
5. derived presentations/blueprints;
6. inference, clearly labeled.

For 4Geeks academic requirements, the 4Geeks rubric/source governed in Control Tower outranks Nexova-local summaries.

## Critical rules
- A polished deck does not become architecture authority.
- Historical product/agent concepts do not become roadmap commitments without a new decision.
- New evidence may supersede an old derived view without rewriting history.
- Material source conflicts remain visible until the governing authority resolves them.
- Domain authority remains in Nexova even while the repository conforms to Noema.
