# `data/pipelines` folder

This folder groups **all data pipelines in the monorepo** related to the company: ingestion, ETL/ELT, cleaning, transformation, and loading into analytical or production systems.

Each subfolder or file under `data/pipelines/` should represent **one pipeline or job set** (for example `sales-etl`, `telemetry-stream`, `customer-segmentation`) and include the required configuration (scripts, orchestration, connectors, schemas, etc.).

- **Main purpose**: consolidate in one place the data movement and transformation logic that powers the company’s applications and analytics.
- **Recommendation**: document pipelines as you add them—their goal, data sources and sinks, dependencies, and how to run them in development, testing, and production.

## Sales forecast

The sales-forecast project keeps its importable code in [`/pipelines`](../../pipelines) and its entry point in [`/scripts/train_sales_forecast.py`](../../scripts/train_sales_forecast.py), because the assignment asks for unit tests in `tests/pipelines/` and a training script in `scripts/`. This folder stays the monorepo slot for other ETL jobs.

> _Spanish version: [README.es.md](./README.es.md)._
