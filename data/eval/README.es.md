# Carpeta `data/eval`

Esta carpeta está orientada a **evaluación y validación**: datasets de evaluación, “golden sets”, resultados de experimentos, métricas, y artefactos usados para medir calidad de modelos, RAG, agentes o pipelines.

- **Propósito principal**: centralizar los insumos y salidas de evaluación para asegurar mejoras medibles a lo largo de los hitos del proyecto.
- **Recomendación**: documenta cada set de evaluación (qué mide, cómo se construyó, criterios de éxito) y evita incluir datos sensibles; si es necesario, usa datos sintéticos o anonimizados.

## Evaluación del modelo de regresión

Comprueba el pronóstico de ingreso mensual de Nexova antes de llevarlo a staging. Reutiliza el bosque, las features causales, el split de 8 años / 2 años y `data/raw/nexova_sales.csv`. Los hiperparámetros no cambian.

`TimeSeriesSplit` arma cinco folds cronológicos solo con los años de entrenamiento. 2024–2025 queda fuera. Cada fold publica MAE y RMSE del bosque y del baseline estacional y(t−12). La métrica principal es el RMSE de validación, como media ± desviación estándar muestral. La curva y el diagnóstico se generan con:

```bash
uv run python scripts/evaluate_regression_model.py
uv run pytest tests/pipelines/test_temporal_cv.py
```

Salidas en esta carpeta: `evaluation_report.md`, `learning_curve.png` y `cv_stability.png`. No se guarda la matriz de features. El script la recalcula. English: [README.md](./README.md).
