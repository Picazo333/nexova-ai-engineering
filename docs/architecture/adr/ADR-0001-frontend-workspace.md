# ADR-0001 — Frontend Workspace for 4g-006

**Status:** ACCEPTED / RUNTIME VALIDATION PENDING  
**Date:** 2026-09-21

## Context
The current milestone requires two independent frontend applications (`uis/website` and `uis/backoffice`) inside a cumulative monorepo. The template already contains a shared package namespace but no root runner.

## Decision
Use:
- npm workspaces at repository root;
- React 19.3.0;
- TypeScript 7.0.2 with strict compiler settings;
- Vite 8.3.0;
- `@vitejs/plugin-react` 6.1.1.

The apps remain independent workspaces with separate layouts and dev servers. Shared UI abstractions are **not** introduced yet; they require observed reuse.

## Why
- two real UI consumers justify a root workspace now;
- React + TypeScript gives a durable component/type baseline for later milestones;
- Vite keeps the development/build layer small and current;
- npm avoids adding a second monorepo orchestrator before caching/build-graph complexity is demonstrated.

## Alternatives rejected for now
- static HTML only: lower immediate setup, but weaker cumulative component/type substrate;
- Turborepo/Nx: useful only after the workspace has a meaningful build graph/caching need;
- Next.js: no current SSR/server framework requirement;
- shared design-system package immediately: abstraction before evidence.

## Validation pending
No dependency install/build/runtime claim is made by this ADR. Before the scaffold supports rubric PASS, capture:
- Node version;
- `npm install` / lockfile;
- `npm run typecheck`;
- `npm run build`;
- both dev-server runtime checks.
