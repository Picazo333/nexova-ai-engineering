"""El baseline estacional del test 2024–2025 es y(t-12), no el mes anterior."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from pipelines.build_features import build_features, drop_warmup_rows
from pipelines.load_sales import TARGET_COLUMN, load_official_sales
from pipelines.split import split_train_test


def _seasonal_naive(raw: pd.DataFrame, months: pd.Series) -> np.ndarray:
    """Predicción ingenua: el ingreso del mismo mes un año antes."""
    lookup = {
        timestamp: float(value)
        for timestamp, value in zip(raw["month"], raw[TARGET_COLUMN], strict=True)
    }
    predictions = []
    for month in months:
        previous = month - pd.DateOffset(years=1)
        if previous not in lookup:
            raise AssertionError(f"No hay y(t-12) para {month.date()}.")
        predictions.append(lookup[previous])
    return np.asarray(predictions, dtype=float)


def test_seasonal_naive_baseline_is_revenue_twelve_months_earlier():
    raw, _notes = load_official_sales()
    origin = int(raw["month"].dt.year.min())
    usable, _dropped = drop_warmup_rows(build_features(raw))
    _train, test = split_train_test(usable, origin_year=origin)

    assert set(test["month"].dt.year.astype(int)) == {2024, 2025}
    assert len(test) == 24

    baseline = _seasonal_naive(raw, test["month"])
    actual = test[TARGET_COLUMN].to_numpy(dtype=float)
    np.testing.assert_allclose(baseline, test["revenue_lag_12"].to_numpy(dtype=float))

    for month, prediction, observed in zip(test["month"], baseline, actual, strict=True):
        previous = month - pd.DateOffset(years=1)
        expected = float(raw.loc[raw["month"] == previous, TARGET_COLUMN].iloc[0])
        assert prediction == pytest.approx(expected)
        assert prediction != pytest.approx(observed)

    squared = (actual - baseline) ** 2
    mse = float(np.mean(squared))
    rmse = float(np.sqrt(mse))
    assert mse == pytest.approx(float(np.sum(squared) / len(squared)))
    assert rmse == pytest.approx(mse ** 0.5)
    assert mse == pytest.approx(3_190_168_976.2504)
    assert rmse == pytest.approx(56_481.580858279805)
