# Carpeta `scripts`

Esta carpeta contiene **scripts auxiliares** del monorepo: automatizaciones de desarrollo, utilidades de mantenimiento, tareas repetitivas (setup, lint, migraciones, generación de datos, etc.) y tooling interno.

- **Propósito principal**: agrupar herramientas de soporte que no pertenecen a una app/agente/pipeline específico, pero facilitan el trabajo del equipo.
- **Recomendación**: documenta cada script (qué hace, parámetros, requisitos, ejemplos de uso) y procura que sean reproducibles (y seguros) en distintos entornos.

## Scripts

| Script | Qué hace |
| --- | --- |
| `train_sales_forecast.py` | Entrena y evalúa el pronóstico de ingreso mensual de Nexova. Escribe `output/metrics.md`, `output/metrics.json` y las gráficas. Ejecución: `uv run python scripts/train_sales_forecast.py`. |
