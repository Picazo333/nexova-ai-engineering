# Informe de auditoría adversaria — actividad 53

- **Auditor:** Rodrigo Salcedo (independiente; no es el autor)
- **Fecha:** 13 de noviembre de 2026, 11:15 CST (America/Mexico_City, UTC-6)
- **Slug:** `ai-eng-sales-forecasting-regression`
- **Tarea LMS:** 1022116 (GET 13 nov 2026: `task_status=PENDING`, `revision_status=PENDING`, `github_url` vacío)
- **Repo / PR:** [Picazo333/nexova-ai-engineering#12](https://github.com/Picazo333/nexova-ai-engineering/pull/12)
- **Rama:** `feature/sales-forecast-model`
- **Head auditado:** `8e99ec8a219c8ba22bbb5b2c83ea3ede3257e1e3`
- **Fuente de criterios:** Enunciado oficial: `/workspace/ejecucion/035-ai-eng-sales-forecasting-regression/source/OFFICIAL_README.md` @ syllabus `fd2da034`, L100–L108. Primera pasada (monorepo).
- **Alcance:** primera pasada (el monorepo, no un repo independiente). Enunciado oficial `/workspace/ejecucion/035-ai-eng-sales-forecasting-regression/source/OFFICIAL_README.md` (L100–L108): modelo de regresión, split 8/2, métricas, justificación. pytest `tests/pipelines/` en entorno limpio (sklearn + statsmodels): **12 passed en 2,15 s**. El PR va contra `main` y está mergeable clean. Sin merge, sin LMS.

## Veredicto

**PASA** (READY). `RandomForestRegressor` (400 árboles, profundidad 6, semilla 42), corte 2017–2023 / 2024–2025, features de lag/rolling/calendario sin contemporáneos al objetivo, cuatro métricas de prueba (MSE, RMSE 67 918,02 USD = 7,08 % del ingreso medio, MAE, más PSI/Gini/K²), gráfica y descomposición estacional alineada con el briefing. 0 GRAVE.

HITL abiertos, no restan: envío al LMS, merge.

## Hallazgos

GRAVE 0. **MENOR 1:** el bosque pierde contra y(t−12) (RMSE 56 481,58 USD). Limitación honesta de extrapolación; no es casilla oficial. IRRELEVANTE 0.

