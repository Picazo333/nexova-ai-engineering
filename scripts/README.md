# `scripts` folder

This folder contains **helper scripts** for the monorepo: development automation, maintenance utilities, repetitive tasks (setup, lint, migrations, data generation, etc.), and internal tooling.

- **Main purpose**: group support tools that do not belong to a specific app, agent, or pipeline but make the team’s work easier.
- **Recommendation**: document each script (what it does, parameters, requirements, usage examples) and keep them reproducible (and safe) across environments.

## Scripts

| Script | Purpose |
| --- | --- |
| `train_sales_forecast.py` | Train and evaluate the Nexova monthly revenue forecast. Writes `output/metrics.md`, `output/metrics.json`, and the plots. Run: `uv run python scripts/train_sales_forecast.py`. |

> _Spanish version: [README.es.md](./README.es.md)._
