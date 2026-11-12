# Carpeta `scripts`

Esta carpeta contiene **scripts auxiliares** del monorepo: automatizaciones de desarrollo, utilidades de mantenimiento, tareas repetitivas (setup, lint, migraciones, generación de datos, etc.) y tooling interno.

- **Propósito principal**: agrupar herramientas de soporte que no pertenecen a una app/agente/pipeline específico, pero facilitan el trabajo del equipo.
- **Recomendación**: documenta cada script (qué hace, parámetros, requisitos, ejemplos de uso) y procura que sean reproducibles (y seguros) en distintos entornos.

## `analyze.py`

Analiza el CSV de tickets de soporte de Nexova. Desde esta carpeta:

```bash
python analyze.py incidents-nexova.csv
```

Responde `y` (también vale `s`) para guardar `results.csv` en el directorio actual, una métrica por fila. `--export` y `--no-export` no preguntan. `incidents-nexova.csv` es la muestra oficial del syllabus e incluye `customer_email`; no lo envíes a una herramienta de IA externa. El script no imprime esas direcciones. Las cifras esperadas están en `nexova-BRIEFING.es.md`.

## `seed_incidents.py`

Carga ese mismo CSV en el gestor de incidencias. Las filas válidas entran con origen `customer` y sede `central`. Las inválidas se listan por línea y regla, sin correo ni descripción, y no se insertan. Una segunda ejecución no duplica un `ticket_id` ya guardado.

```bash
services/api/.venv/bin/python scripts/seed_incidents.py
```

Los mapas de campos están en `nexova-incident-manager-BRIEFING.es.md`. El fichero `incident_records.json` queda en `INCIDENTS_DATA_DIR` o en `services/api/.data`, y no se versiona.
