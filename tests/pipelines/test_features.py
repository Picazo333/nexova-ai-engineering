"""El lag de la fila t es el ingreso de t-1, y el rolling no incluye t."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from pipelines.build_features import (
    CALENDAR_COLUMNS,
    FEATURE_COLUMNS,
    build_features,
    drop_warmup_rows,
)
from pipelines.load_sales import clean_frame, load_official_sales
from pipelines.train_sales_model import SEED, fit_model


def test_lag_and_rolling_features_are_causal():
    raw, _notes = load_official_sales()
    frame = build_features(raw)
    revenue = frame["revenue_usd"]

    assert pd.isna(frame["revenue_lag_1"].iloc[0])
    for index in range(1, len(frame)):
        assert frame["revenue_lag_1"].iloc[index] == revenue.iloc[index - 1]
    for index in range(12, len(frame)):
        assert frame["revenue_lag_12"].iloc[index] == revenue.iloc[index - 12]

    assert pd.isna(frame["revenue_roll_mean_3"].iloc[2])
    leak_gaps = []
    for index in range(3, len(frame)):
        window = revenue.iloc[index - 3 : index]
        assert frame["revenue_roll_mean_3"].iloc[index] == pytest.approx(window.mean())
        leaky_window = revenue.iloc[index - 2 : index + 1]
        leak_gaps.append(abs(frame["revenue_roll_mean_3"].iloc[index] - float(leaky_window.mean())))
    assert max(leak_gaps) > 1.0

    assert pd.isna(frame["revenue_roll_std_12"].iloc[11])
    for index in range(12, len(frame)):
        window = revenue.iloc[index - 12 : index]
        assert frame["revenue_roll_std_12"].iloc[index] == pytest.approx(window.std())

    assert not np.allclose(
        frame["revenue_lag_1"].iloc[1:].to_numpy(dtype=float),
        revenue.iloc[1:].to_numpy(dtype=float),
    )
    assert frame["contracts_lag_1"].iloc[5] == frame["active_contracts"].iloc[4]
    assert frame["avg_contract_value_lag_1"].iloc[5] == pytest.approx(
        frame["avg_contract_value_usd"].iloc[4]
    )


def test_calendar_features_ignore_revenue_and_target_is_not_a_feature():
    raw, _notes = load_official_sales()
    scaled = raw.copy()
    scaled["revenue_usd"] = scaled["revenue_usd"] * 3.0
    original = build_features(raw)
    mutated = build_features(scaled)
    for column in CALENDAR_COLUMNS:
        pd.testing.assert_series_equal(original[column], mutated[column])

    assert "revenue_usd" not in FEATURE_COLUMNS
    assert "active_contracts" not in FEATURE_COLUMNS
    assert "avg_contract_value_usd" not in FEATURE_COLUMNS
    assert "revenue_lag_1" in FEATURE_COLUMNS
    assert "revenue_roll_mean_3" in FEATURE_COLUMNS
    assert "month_sin" in FEATURE_COLUMNS


def test_blank_and_null_rows_are_dropped():
    raw = pd.DataFrame(
        {
            "month": ["2016-01-01", "2016-02-01", "2016-03-01", "2016-04-01"],
            "revenue_usd": ["100.5", "  ", None, "80"],
            "active_contracts": [10, 11, 12, 13],
            "avg_contract_value_usd": [5.0, 5.0, 5.0, 5.0],
            "business_line": ["consolidated", "consolidated", "consolidated", ""],
        }
    )
    cleaned, dropped = clean_frame(raw)
    assert dropped == 3
    assert len(cleaned) == 1
    assert cleaned.loc[0, "revenue_usd"] == pytest.approx(100.5)
    assert cleaned.loc[0, "month"] == pd.Timestamp("2016-01-01")


def test_model_is_trained_on_lag_rolling_and_calendar_features():
    raw, _notes = load_official_sales()
    prepared = fit_model(raw)
    model = prepared["model"]
    assert model.__class__.__name__ == "RandomForestRegressor"
    assert model.random_state == SEED
    assert model.n_features_in_ == len(FEATURE_COLUMNS)
    assert set(prepared["feature_columns"]) == set(FEATURE_COLUMNS)
    usable, _dropped = drop_warmup_rows(build_features(raw))
    assert len(prepared["predicted"]) == 24
    assert prepared["test"]["month"].min() == pd.Timestamp("2024-01-01")
    assert prepared["train"]["month"].max() < prepared["test"]["month"].min()
    assert len(usable) == len(prepared["train"]) + len(prepared["test"])
