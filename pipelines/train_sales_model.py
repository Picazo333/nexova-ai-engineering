"""Ajuste y evaluación del pronóstico. La semilla va fija."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler

from pipelines.build_features import FEATURE_COLUMNS, build_features, drop_warmup_rows
from pipelines.decompose_series import decompose_revenue, growth_report, seasonality_report
from pipelines.load_sales import TARGET_COLUMN, load_official_sales, repo_root
from pipelines.metrics import (
    dagostino_k2,
    mean_squared_error,
    normalized_gini,
    population_stability_index,
)
from pipelines.plots import (
    choose_font,
    plot_decomposition,
    plot_feature_importance,
    plot_forecast,
)
from pipelines.reporting import render_markdown, render_terminal
from pipelines.split import split_train_test, training_cutoff_year

# Criterio de elección (tamaño, explicabilidad, tiempo de ajuste):
# Tras el calentamiento causal quedan 84 meses para entrenar. Es una serie
# corta. Finanzas pidió un error explicable, no una caja negra. Random Forest
# promedia árboles y la dispersión entre ellos es la banda del gráfico, con
# hiperparámetros fijos y sin búsqueda sobre la prueba. XGBoost suele pedir
# más ajuste y es más difícil de contar. Por eso el modelo es
# RandomForestRegressor de scikit-learn.
SEED = 42
N_ESTIMATORS = 400
MAX_DEPTH = 6
MIN_SAMPLES_LEAF = 2

MODEL_JUSTIFICATION = (
    "RandomForestRegressor de scikit-learn, no XGBoost. "
    "La serie útil de entrenamiento tiene 84 meses: es corta para una búsqueda "
    "de boosting. Finanzas necesita explicar el error y ver un rango, no un "
    "solo número. El bosque promedia árboles; la desviación estándar entre "
    "árboles es la banda de variabilidad. Los hiperparámetros quedan fijos "
    "(400 árboles, profundidad 6, mínimo 2 muestras por hoja, semilla 42) y "
    "no se eligen mirando la prueba. XGBoost quedaría solo si el objetivo "
    "fuera ganar precisión y hubiera tiempo de ajuste."
)


def make_model(seed: int = SEED) -> RandomForestRegressor:
    return RandomForestRegressor(
        n_estimators=N_ESTIMATORS,
        max_depth=MAX_DEPTH,
        min_samples_leaf=MIN_SAMPLES_LEAF,
        max_features="sqrt",
        bootstrap=True,
        random_state=seed,
        n_jobs=1,
    )


def _matrix(frame: pd.DataFrame) -> pd.DataFrame:
    return frame.loc[:, list(FEATURE_COLUMNS)]


def fit_model(raw: pd.DataFrame, seed: int = SEED) -> dict:
    """Entrena solo con años anteriores al corte y evalúa los dos años finales."""
    origin_year = int(raw["month"].dt.year.min())
    featured = build_features(raw)
    usable, warmup_dropped = drop_warmup_rows(featured)
    train, test = split_train_test(usable, origin_year=origin_year)
    scaler = StandardScaler()
    scaler.fit(_matrix(train))
    model = make_model(seed)
    model.fit(scaler.transform(_matrix(train)), train[TARGET_COLUMN].to_numpy())
    x_test = scaler.transform(_matrix(test))
    predicted = model.predict(x_test)
    tree_matrix = np.vstack([estimator.predict(x_test) for estimator in model.estimators_])
    tree_std = tree_matrix.std(axis=0)
    actual = test[TARGET_COLUMN].to_numpy(dtype=float)
    residuals = actual - predicted
    train_predicted = model.predict(scaler.transform(_matrix(train)))
    train_actual = train[TARGET_COLUMN].to_numpy(dtype=float)
    shape_train = _shape_values(train)
    shape_test = _shape_values(test)
    mse = mean_squared_error(actual, predicted)
    rmse = float(np.sqrt(mse))
    mean_revenue = float(np.mean(actual))
    k2_statistic, k2_pvalue = dagostino_k2(residuals)
    baseline = test["revenue_lag_1"].to_numpy(dtype=float)
    baseline_mse = mean_squared_error(actual, baseline)
    return {
        "origin_year": origin_year,
        "cutoff_year": training_cutoff_year(origin_year),
        "warmup_dropped": int(warmup_dropped),
        "train": train,
        "test": test,
        "model": model,
        "scaler": scaler,
        "predicted": predicted,
        "tree_std": tree_std,
        "actual": actual,
        "residuals": residuals,
        "feature_columns": list(FEATURE_COLUMNS),
        "metrics": {
            "mse_usd2": mse,
            "rmse_usd": rmse,
            "mae_usd": float(np.mean(np.abs(residuals))),
            "mean_test_revenue_usd": mean_revenue,
            "rmse_over_mean_revenue": rmse / mean_revenue,
            "psi_revenue_level": population_stability_index(
                train[TARGET_COLUMN].to_numpy(dtype=float),
                actual,
            ),
            "psi_revenue_shape": population_stability_index(shape_train, shape_test),
            "gini": normalized_gini(actual, predicted),
            "k2_statistic": k2_statistic,
            "k2_pvalue": k2_pvalue,
            "baseline_lag1_mse_usd2": baseline_mse,
            "baseline_lag1_rmse_usd": float(np.sqrt(baseline_mse)),
            "train_mse_usd2_diagnostic": mean_squared_error(train_actual, train_predicted),
            "train_rmse_usd_diagnostic": float(
                np.sqrt(mean_squared_error(train_actual, train_predicted))
            ),
        },
    }


def _shape_values(frame: pd.DataFrame) -> np.ndarray:
    """Ingreso dividido por la media de su año. Diagnóstico de forma, no feature."""
    year_mean = frame.groupby(frame["month"].dt.year)[TARGET_COLUMN].transform("mean")
    return (frame[TARGET_COLUMN] / year_mean).to_numpy(dtype=float)


def _jsonable(value):
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if isinstance(value, np.floating):
        return float(value)
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, float) and not np.isfinite(value):
        return None
    return value


def build_payload(notes: dict, prepared: dict, season: dict, growth: dict, font_name: str) -> dict:
    train = prepared["train"]
    test = prepared["test"]
    importances = prepared["model"].feature_importances_
    return {
        "dataset": notes,
        "split": {
            "origin_year": prepared["origin_year"],
            "cutoff_year": prepared["cutoff_year"],
            "train_years_rule": 8,
            "test_years_rule": 2,
            "warmup_rows_dropped": prepared["warmup_dropped"],
            "train_rows": int(len(train)),
            "test_rows": int(len(test)),
            "train_start": train["month"].min().strftime("%Y-%m-%d"),
            "train_end": train["month"].max().strftime("%Y-%m-%d"),
            "test_start": test["month"].min().strftime("%Y-%m-%d"),
            "test_end": test["month"].max().strftime("%Y-%m-%d"),
            "train_years": sorted({int(year) for year in train["month"].dt.year}),
            "test_years": sorted({int(year) for year in test["month"].dt.year}),
        },
        "features": list(FEATURE_COLUMNS),
        "model": {
            "algorithm": "RandomForestRegressor",
            "library": "scikit-learn",
            "random_state": int(prepared["model"].random_state),
            "n_estimators": N_ESTIMATORS,
            "max_depth": MAX_DEPTH,
            "min_samples_leaf": MIN_SAMPLES_LEAF,
            "n_jobs": 1,
            "justification": MODEL_JUSTIFICATION,
            "scaler": "StandardScaler ajustado solo con entrenamiento",
        },
        "test_metrics": prepared["metrics"],
        "feature_importance": [
            {"feature": name, "importance": float(value)}
            for name, value in sorted(
                zip(FEATURE_COLUMNS, importances, strict=True),
                key=lambda item: item[1],
                reverse=True,
            )
        ],
        "seasonality": season,
        "growth": growth,
        "font": font_name,
        "variability_band": (
            "±1 desviación estándar de las predicciones de los árboles "
            "en cada mes de prueba. No es un intervalo calibrado al 95 %."
        ),
    }


def run_forecast(root: Path | None = None) -> dict:
    root = root or repo_root()
    raw, notes = load_official_sales(root)
    prepared = fit_model(raw)
    decomposed = decompose_revenue(raw)
    season = seasonality_report(raw, decomposed)
    growth = growth_report(raw)
    font_name = choose_font()
    payload = build_payload(notes, prepared, season, growth, font_name)
    output = root / "output"
    output.mkdir(parents=True, exist_ok=True)
    rmse_pct = payload["test_metrics"]["rmse_over_mean_revenue"] * 100.0
    subtitle = (
        f"RMSE en prueba: {payload['test_metrics']['rmse_usd']:,.0f} USD "
        f"({rmse_pct:.1f} % del ingreso mensual medio de 2024–2025). "
        "Banda: ±1 desviación estándar entre árboles, no un intervalo al 95 %. "
        "Fuente: data/raw/nexova_sales.csv."
    )
    plot_forecast(
        months=prepared["test"]["month"],
        actual=prepared["actual"],
        predicted=prepared["predicted"],
        low=prepared["predicted"] - prepared["tree_std"],
        high=prepared["predicted"] + prepared["tree_std"],
        path=output / "forecast_vs_actual.png",
        subtitle=subtitle,
        font_name=font_name,
    )
    plot_decomposition(decomposed, output / "decomposition.png", font_name)
    plot_feature_importance(
        list(FEATURE_COLUMNS),
        prepared["model"].feature_importances_,
        output / "feature_importance.png",
        font_name,
    )
    markdown = render_markdown(payload)
    (output / "metrics.md").write_text(markdown, encoding="utf-8")
    (output / "metrics.json").write_text(
        json.dumps(_jsonable(payload), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    terminal = render_terminal(payload)
    (output / "train.log").write_text(terminal + "\n", encoding="utf-8")
    payload["terminal_summary"] = terminal
    payload["outputs"] = {
        "metrics_md": str(output / "metrics.md"),
        "metrics_json": str(output / "metrics.json"),
        "forecast_png": str(output / "forecast_vs_actual.png"),
        "decomposition_png": str(output / "decomposition.png"),
        "importance_png": str(output / "feature_importance.png"),
    }
    return payload


def main() -> int:
    try:
        payload = run_forecast(repo_root())
    except (FileNotFoundError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(payload["terminal_summary"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
