"""Features de serie de tiempo. Lags y rolling solo miran el pasado."""

from __future__ import annotations

import numpy as np
import pandas as pd

from pipelines.load_sales import TARGET_COLUMN

FEATURE_COLUMNS = (
    "revenue_lag_1",
    "revenue_lag_12",
    "revenue_roll_mean_3",
    "revenue_roll_std_12",
    "contracts_lag_1",
    "avg_contract_value_lag_1",
    "month_sin",
    "month_cos",
    "quarter",
    "trend_month_index",
)
LAG_COLUMNS = (
    "revenue_lag_1",
    "revenue_lag_12",
    "contracts_lag_1",
    "avg_contract_value_lag_1",
)
ROLLING_COLUMNS = ("revenue_roll_mean_3", "revenue_roll_std_12")
CALENDAR_COLUMNS = ("month_sin", "month_cos", "quarter", "trend_month_index")
SERIES_ORIGIN = pd.Timestamp("2016-01-01")


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """Añade lags, rolling causal y calendario.

    El rolling se calcula sobre ``shift(1)``: el ingreso del mes en curso no
    entra en su propia feature. Contratos y valor medio del mismo mes tampoco:
    describen el mes que se quiere pronosticar. El calendario sale de la
    fecha, que se conoce antes de cerrar el ingreso.
    """
    frame = df.sort_values("month").reset_index(drop=True).copy()
    revenue = frame[TARGET_COLUMN]
    past_revenue = revenue.shift(1)
    frame["revenue_lag_1"] = past_revenue
    frame["revenue_lag_12"] = revenue.shift(12)
    frame["revenue_roll_mean_3"] = past_revenue.rolling(window=3).mean()
    frame["revenue_roll_std_12"] = past_revenue.rolling(window=12).std()
    frame["contracts_lag_1"] = frame["active_contracts"].shift(1)
    frame["avg_contract_value_lag_1"] = frame["avg_contract_value_usd"].shift(1)

    month_number = frame["month"].dt.month.astype(float)
    frame["month_sin"] = np.sin(2 * np.pi * month_number / 12.0)
    frame["month_cos"] = np.cos(2 * np.pi * month_number / 12.0)
    frame["quarter"] = frame["month"].dt.quarter.astype(float)
    frame["trend_month_index"] = (
        (frame["month"].dt.year - SERIES_ORIGIN.year) * 12
        + (frame["month"].dt.month - SERIES_ORIGIN.month)
    ).astype(float)
    return frame


def drop_warmup_rows(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """Tira el tramo inicial donde lag 12 o el rolling de 12 meses no existen."""
    before = len(df)
    usable = df.dropna(subset=list(FEATURE_COLUMNS)).reset_index(drop=True)
    return usable, before - len(usable)
