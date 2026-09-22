# Progress

## Current state
**Milestone:** 4g-006 — AI-driven Engineering  
**Phase:** academic baseline validated; final PR/audit pending  
**Branch:** `feature/agent-memory-bank`

### Completed
- Nexova company selection and root `CONTEXT.md` already existed before this milestone.
- Existing repository/template structure inspected.
- Required branch created from the pre-milestone baseline.
- 4Geeks rubric extracted into Control Tower.
- Noema/Control Tower/Nexova authority boundaries reviewed.
- Agent/context foundation is being established in this commit.

### Completed in the current branch
- minimal durable repo governance;
- required Memory Bank;
- coding-agent rule + recurring verification Skill;
- source authority classification;
- root npm workspace scaffold;
- React + TypeScript + Vite app shells for `uis/website` and `uis/backoffice`.

### Visual lock
The selected identity is **Oni Nocturne Oxblood**. The 30-board exploration is closed. Boards 26–30 are distilled into `docs/design/VISUAL_LOCK.md`; earlier boards remain supporting design references.

### UI implementation
- complete public website source implemented under `uis/website`;
- independent operations backoffice source implemented under `uis/backoffice`;
- shared design-system tokens/primitives extracted after real reuse appeared;
- backoffice explicitly labels its metrics as source baselines rather than live telemetry;
- no backend was introduced.

### Validation status
GitHub Actions run `35679157613` completed successfully on the feature branch. It executed dependency installation, real typecheck, production build, runtime smoke for both apps, headless-browser DOM assertions, rendered screenshots, artifact upload and evidence/lockfile commit.

Committed evidence:
- `package-lock.json`;
- `docs/evidence/4g-006/website.png`;
- `docs/evidence/4g-006/backoffice.png`.

### Next
1. reconcile the successful runtime evidence into Control Tower;
2. perform the bounded Excellence Review without destabilizing the validated baseline;
3. create the required PR to `main` with website/backoffice screenshots and direct `AGENTS.md` link;
4. confirm PR validation;
5. show the final audit and exact campus submission URL.

## Deferred
Backend, DB, RAG, persistent agents, multi-agent orchestration, advanced observability and productization remain deferred until a real milestone/failure mode activates them.
