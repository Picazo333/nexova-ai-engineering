# `packages` folder

This folder contains **shared packages** for the monorepo: internal libraries, utilities, types, shared components, SDKs, clients, and any code reused by multiple applications, agents, or pipelines.

Each subfolder under `packages/` should represent **one versionable package** (for example `shared-types`, `ui`, `analytics-sdk`) with its own README.

- **Main purpose**: encourage reuse and consistency across all company deliverables.
- **Recommendation**: document packages as you add them—their public API and how they are consumed from `apps/`, `agents/`, and `workflows/`.

> _Spanish version: [README.es.md](./README.es.md)._

## `shared/nexova_incidents/`

Validación del CSV de tickets y reglas del gestor de incidencias (categorías, sedes, ciclo de vida y mapa CSV → modelo). La importa quien tenga `packages/shared` en el `PYTHONPATH`.

## `incident_analysis/`

Python rules for the Nexova support CSV, shared by `scripts/analyze.py` and `services/api`. See [`incident_analysis/README.md`](./incident_analysis/README.md).
