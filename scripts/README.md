# `scripts` folder

This folder contains **helper scripts** for the monorepo: development automation, maintenance utilities, repetitive tasks (setup, lint, migrations, data generation, etc.), and internal tooling.

- **Main purpose**: group support tools that do not belong to a specific app, agent, or pipeline but make the team’s work easier.
- **Recommendation**: document each script (what it does, parameters, requirements, usage examples) and keep them reproducible (and safe) across environments.

> _Spanish version: [README.es.md](./README.es.md)._

## `analyze.py`

Analyses the Nexova support CSV. From this directory:

```bash
python analyze.py incidents-nexova.csv
```

Answer `y` to write `results.csv` in the current directory (one metric per row). `s` is also accepted. `--export` and `--no-export` skip the question. The test file `incidents-nexova.csv` is the official syllabus sample and contains `customer_email`; do not send it to an external AI tool. The script never prints those addresses. Expected figures are in `nexova-BRIEFING.en.md`.
