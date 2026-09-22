# Progress

## Current state
**Milestone:** 4g-006 — AI-driven Engineering  
**Phase:** foundation before UI implementation  
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

### Validation status
The workspace files are structurally committed but dependency installation/build/runtime are still `UNVERIFIED` because no executable Codespaces/local runner is attached to this chat and the account-level GitHub Actions issue currently prevents reliable runner execution.

### Human gate — visual direction
Three independent visual routes are documented in `docs/design/VISUAL_ROUTES.md`. Implementation must not propagate a final visual system until one route is selected or a new route is requested.

### Next
1. obtain the visual-direction lock;
2. implement the complete corporate website and independent backoffice;
3. install dependencies and capture lockfile/build/typecheck/runtime evidence in an execution environment;
4. run full rubric/evidence loop;
5. run bounded excellence review after baseline academic PASS;
6. open the required PR to `main`.

## Deferred
Backend, DB, RAG, persistent agents, multi-agent orchestration, advanced observability and productization remain deferred until a real milestone/failure mode activates them.
