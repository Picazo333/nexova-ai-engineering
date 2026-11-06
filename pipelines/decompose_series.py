"""Descomposición diagnóstico. No es el modelo de pronóstico."""

from __future__ import annotations

import pandas as pd
from statsmodels.tsa.seasonal import seasonal_decompose

from pipelines.load_sales import TARGET_COLUMN

# El briefing describe agosto y enero-febrero como porcentajes sobre el
# promedio, y el nivel crece cada año. Por eso el diagnóstico es
# multiplicativo (period=12), no una amplitud fija en dólares.
DECOMPOSE_MODEL = "multiplicative"
DECOMPOSE_PERIOD = 12


def decompose_revenue(df: pd.DataFrame):
    series = (
        df.set_index("month")[TARGET_COLUMN]
        .astype(float)
        .sort_index()
        .asfreq("MS")
    )
    if series.isna().any():
        raise ValueError("Hay huecos mensuales: no se descompone la serie.")
    return seasonal_decompose(
        series,
        model=DECOMPOSE_MODEL,
        period=DECOMPOSE_PERIOD,
        extrapolate_trend="period",
    )


def _year_relative_profile(df: pd.DataFrame) -> pd.Series:
    """Ingreso de cada mes dividido por la media de su mismo año.

    Sirve para leer el briefing («respecto al promedio»). Usa la media del
    año cerrado, así que es un diagnóstico de la serie ya observada, no una
    feature del modelo.
    """
    frame = df.copy()
    year_mean = frame.groupby(frame["month"].dt.year)[TARGET_COLUMN].transform("mean")
    frame["relative"] = frame[TARGET_COLUMN] / year_mean
    return frame.groupby(frame["month"].dt.month)["relative"].mean()


def seasonality_report(df: pd.DataFrame, result) -> dict:
    """Compara la serie real con el patrón del briefing de Nexova.

    Briefing: agosto cae 15–25 % respecto al promedio; enero y febrero suben
    15–20 %. El resto se mueve cerca de la tendencia. El texto numérico sale
    de esta medición; no se copia la frase del briefing si los números no dan.
    """
    profile = _year_relative_profile(df)
    seasonal = result.seasonal
    factors = seasonal.groupby(seasonal.index.month).mean()

    def month_view(month: int) -> dict:
        relative = float(profile.loc[month])
        return {
            "month": month,
            "relative_to_year_mean": relative,
            "gap_vs_year_mean": relative - 1.0,
            "seasonal_factor": float(factors.loc[month]),
        }

    august = month_view(8)
    january = month_view(1)
    february = month_view(2)
    other_months = [month for month in range(1, 13) if month not in (1, 2, 8)]
    other_abs_gap = float(profile.loc[other_months].sub(1.0).abs().mean())
    direction_matches = bool(
        august["relative_to_year_mean"] == float(profile.min())
        and january["relative_to_year_mean"] > 1.0
        and february["relative_to_year_mean"] > 1.0
        and float(factors.loc[8]) == float(factors.min())
    )
    percent_bands_match = bool(
        0.15 <= -august["gap_vs_year_mean"] <= 0.25
        and 0.15 <= january["gap_vs_year_mean"] <= 0.20
        and 0.15 <= february["gap_vs_year_mean"] <= 0.20
    )
    return {
        "model": DECOMPOSE_MODEL,
        "period": DECOMPOSE_PERIOD,
        "august": august,
        "january": january,
        "february": february,
        "other_months_mean_abs_gap": other_abs_gap,
        "direction_matches_briefing": direction_matches,
        "percent_bands_match_briefing": percent_bands_match,
        "profile_by_month": {int(month): float(profile.loc[month]) for month in range(1, 13)},
    }


def growth_report(df: pd.DataFrame) -> dict:
    """Crecimiento anual observado. El briefing dice que es siempre positivo."""
    annual = (
        df.groupby(df["month"].dt.year)[TARGET_COLUMN]
        .sum()
        .sort_index()
        .astype(float)
    )
    yoy = (annual / annual.shift(1) - 1.0).dropna()
    return {
        "annual_revenue_usd": {int(year): float(value) for year, value in annual.items()},
        "yoy_growth": {int(year): float(value) for year, value in yoy.items()},
        "all_yoy_positive": bool((yoy > 0).all()),
        "min_yoy": float(yoy.min()),
        "max_yoy": float(yoy.max()),
    }
