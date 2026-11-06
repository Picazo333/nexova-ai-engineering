"""Orden cronológico, fuga de lags y métricas de la validación temporal."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from sklearn.model_selection import TimeSeriesSplit

from pipelines.build_features import FEATURE_COLUMNS, build_features
from pipelines.evaluate_regression import (
    CLOSE_GAP_RATIO,
    MIN_SPLITS,
    WIDE_GAP_RATIO,
    CurvePoint,
    assert_chronological,
    corrective_action,
    diagnose,
    features_ignore_future,
    fit_window,
    mean_and_std,
    prepared_frames,
    render_report,
    run_evaluation,
    seasonal_naive,
    time_series_folds,
    write_outputs,
)
from pipelines.load_sales import TARGET_COLUMN, load_official_sales
from pipelines.train_sales_model import (
    MAX_DEPTH,
    MIN_SAMPLES_LEAF,
    N_ESTIMATORS,
    SEED,
    fit_model,
)


@pytest.fixture(scope="module")
def raw_frame():
    raw, notes = load_official_sales()
    assert notes["official_hash_matches"] is True
    return raw


@pytest.fixture(scope="module")
def evaluation(raw_frame):
    return run_evaluation(raw_frame)


def _point(
    *,
    train_rmse: float,
    val_rmse: float,
    lag12_val_rmse: float,
    lag12_train_rmse: float,
    train_rows: int,
) -> CurvePoint:
    start = pd.Timestamp("2017-01-01") + pd.DateOffset(months=train_rows)
    return CurvePoint(
        train_rows=train_rows,
        val_rows=14,
        train_start=pd.Timestamp("2017-01-01"),
        train_end=start - pd.DateOffset(months=1),
        val_start=start,
        val_end=start + pd.DateOffset(months=13),
        train_rmse=train_rmse,
        val_rmse=val_rmse,
        train_mae=train_rmse / 2,
        val_mae=val_rmse / 2,
        lag12_val_rmse=lag12_val_rmse,
        lag12_val_mae=lag12_val_rmse / 2,
        lag12_train_rmse=lag12_train_rmse,
        mean_signed_val=0.0,
    )


def test_later_fold_index_does_not_precede_earlier_fold(raw_frame):
    train, test = prepared_frames(raw_frame)
    windows = time_series_folds(train, n_splits=MIN_SPLITS)
    assert len(windows) >= 5
    assert_chronological(windows)

    splitter = TimeSeriesSplit(n_splits=MIN_SPLITS)
    for window, (expected_train, expected_val) in zip(windows, splitter.split(train), strict=True):
        assert list(window.train_positions) == [int(index) for index in expected_train]
        assert list(window.val_positions) == [int(index) for index in expected_val]

    sequence = [index for window in windows for index in window.val_positions]
    assert sequence == sorted(sequence)
    assert len(sequence) == len(set(sequence))

    for earlier, later in zip(windows, windows[1:]):
        assert max(earlier.val_positions) < min(later.val_positions)
        assert min(later.train_positions) >= min(earlier.train_positions)
        assert max(later.val_positions) > max(earlier.val_positions)

    for window in windows:
        train_months = train["month"].iloc[list(window.train_positions)]
        val_months = train["month"].iloc[list(window.val_positions)]
        assert train_months.is_monotonic_increasing
        assert val_months.is_monotonic_increasing
        assert train_months.max() < val_months.min()
        assert list(window.train_positions) == sorted(window.train_positions)
        assert list(window.val_positions) == sorted(window.val_positions)

    assert test["month"].min() >= pd.Timestamp("2024-01-01")
    assert train["month"].max() < pd.Timestamp("2024-01-01")


def test_blanking_future_targets_does_not_change_past_features(raw_frame):
    train, _test = prepared_frames(raw_frame)
    featured = build_features(raw_frame)
    for window in time_series_folds(train):
        cutoff = pd.Timestamp(train["month"].iloc[window.val_positions[0]])
        assert features_ignore_future(raw_frame, train, cutoff)
        masked = raw_frame.copy()
        future = masked["month"] >= cutoff
        for column in ("revenue_usd", "active_contracts", "avg_contract_value_usd"):
            masked.loc[future, column] = np.nan
        rebuilt = build_features(masked)
        past = featured["month"] < cutoff
        for column in FEATURE_COLUMNS:
            left = featured.loc[past, column].to_numpy(dtype=float)
            right = rebuilt.loc[past, column].to_numpy(dtype=float)
            np.testing.assert_allclose(left, right, equal_nan=True)


def test_row_features_do_not_use_that_row_or_the_future(raw_frame):
    featured = build_features(raw_frame).dropna(subset=list(FEATURE_COLUMNS)).reset_index(drop=True)
    for timestamp in featured["month"]:
        masked = raw_frame.copy()
        future = masked["month"] >= timestamp
        for column in ("revenue_usd", "active_contracts", "avg_contract_value_usd"):
            masked.loc[future, column] = np.nan
        rebuilt = build_features(masked)
        left = featured.loc[featured["month"] == timestamp, list(FEATURE_COLUMNS)].iloc[0]
        right = rebuilt.loc[rebuilt["month"] == timestamp, list(FEATURE_COLUMNS)].iloc[0]
        np.testing.assert_allclose(
            left.to_numpy(dtype=float),
            right.to_numpy(dtype=float),
            equal_nan=True,
        )


def test_cv_reports_mean_std_and_keeps_the_035_model(evaluation, raw_frame):
    assert len(evaluation.folds) >= 5
    assert evaluation.held_out_start >= pd.Timestamp("2024-01-01")
    for fold in evaluation.folds:
        assert fold.val_end < pd.Timestamp("2024-01-01")
        assert fold.train_end < fold.val_start
        assert fold.leakage_check_passed
        assert fold.scaler_seen == fold.train_rows
        assert fold.n_estimators == N_ESTIMATORS
        assert fold.max_depth == MAX_DEPTH
        assert fold.min_samples_leaf == MIN_SAMPLES_LEAF
        assert fold.random_state == SEED
        assert fold.val_rows == evaluation.horizon

    rmse_mean, rmse_std = mean_and_std([fold.val_rmse for fold in evaluation.folds])
    assert rmse_std > 0
    rendered = f"{rmse_mean:,.2f} ± {rmse_std:,.2f}"
    report = render_report(evaluation)
    assert rendered in report
    assert "±" in report
    assert "MAE" in report and "RMSE" in report
    assert "y(t−12)" in report
    assert "Clasificación explícita:" in report
    assert evaluation.diagnosis.label in {"overfitting", "underfitting", "well fitted"}
    assert "revenue_usd" in report
    assert "business_line=consolidated" in report

    prepared = fit_model(raw_frame)
    train, _test = prepared_frames(raw_frame)
    assert list(train["month"]) == list(prepared["train"]["month"])
    assert list(FEATURE_COLUMNS) == list(prepared["feature_columns"])


def test_seasonal_baseline_inside_cv_is_y_t_minus_12(evaluation, raw_frame):
    train, _test = prepared_frames(raw_frame)
    for fold in evaluation.folds:
        months = train["month"].iloc[list(fold.val_positions)]
        baseline = seasonal_naive(raw_frame, months)
        actual = train[TARGET_COLUMN].iloc[list(fold.val_positions)].to_numpy(dtype=float)
        column = train["revenue_lag_12"].iloc[list(fold.val_positions)].to_numpy(dtype=float)
        np.testing.assert_allclose(baseline, column)
        for month, prediction in zip(months, baseline, strict=True):
            previous = month - pd.DateOffset(years=1)
            expected = float(raw_frame.loc[raw_frame["month"] == previous, TARGET_COLUMN].iloc[0])
            assert prediction == pytest.approx(expected)
        rmse = float(np.sqrt(np.mean((actual - baseline) ** 2)))
        assert fold.lag12_val_rmse == pytest.approx(rmse)


def test_learning_curve_last_point_matches_last_fold(evaluation):
    last = evaluation.curve[-1]
    fold = evaluation.folds[-1]
    assert last.train_rows == fold.train_rows
    assert last.val_rmse == pytest.approx(fold.val_rmse)
    assert last.train_rmse == pytest.approx(fold.train_rmse)
    assert last.lag12_val_rmse == pytest.approx(fold.lag12_val_rmse)
    assert [point.train_rows for point in evaluation.curve] == sorted(
        point.train_rows for point in evaluation.curve
    )
    assert last.val_end < pd.Timestamp("2024-01-01")


def test_fold_fit_is_reproducible(raw_frame):
    train, _test = prepared_frames(raw_frame)
    window = time_series_folds(train)[-1]
    first = fit_window(train, raw_frame, window.train_positions, window.val_positions)
    second = fit_window(train, raw_frame, window.train_positions, window.val_positions)
    assert first.val_rmse == pytest.approx(second.val_rmse)
    assert first.train_rmse == pytest.approx(second.train_rmse)


def test_diagnosis_rules_are_fixed():
    overfitting = diagnose(
        [
            _point(train_rmse=10, val_rmse=40, lag12_val_rmse=30, lag12_train_rmse=25, train_rows=40),
            _point(train_rmse=10, val_rmse=38, lag12_val_rmse=30, lag12_train_rmse=25, train_rows=50),
            _point(train_rmse=10, val_rmse=36, lag12_val_rmse=30, lag12_train_rmse=25, train_rows=60),
        ]
    )
    assert overfitting.label == "overfitting"
    assert overfitting.wide and overfitting.persistent

    underfitting = diagnose(
        [
            _point(train_rmse=28, val_rmse=31, lag12_val_rmse=20, lag12_train_rmse=20, train_rows=40),
            _point(train_rmse=27, val_rmse=30, lag12_val_rmse=20, lag12_train_rmse=20, train_rows=50),
            _point(train_rmse=26, val_rmse=30, lag12_val_rmse=20, lag12_train_rmse=20, train_rows=60),
        ]
    )
    assert underfitting.label == "underfitting"
    assert underfitting.close and underfitting.val_high
    assert underfitting.gap_ratio <= CLOSE_GAP_RATIO

    fitted = diagnose(
        [
            _point(train_rmse=12, val_rmse=16, lag12_val_rmse=30, lag12_train_rmse=28, train_rows=40),
            _point(train_rmse=12, val_rmse=15, lag12_val_rmse=30, lag12_train_rmse=28, train_rows=50),
            _point(train_rmse=12, val_rmse=14, lag12_val_rmse=30, lag12_train_rmse=28, train_rows=60),
        ]
    )
    assert fitted.label == "well fitted"
    assert fitted.close and fitted.val_low
    assert fitted.gap_ratio < WIDE_GAP_RATIO


def test_overfitting_action_names_the_leaf_and_keeps_2024_out():
    text = corrective_action(
        "overfitting",
        last_train_rmse=10_000,
        last_val_rmse=40_000,
        rmse_mean=35_000,
        rmse_std=2_000,
        lag12_mean=20_000,
        lag12_std=1_000,
        loses_to_lag12=True,
    )
    assert "min_samples_leaf de 2 a 8" in text
    assert "revenue_usd − y(t−12)" in text
    assert "No se usa 2024–2025" in text
    assert "Subir max_depth o n_estimators no está en esta acción" in text
    assert "35,000.00 ± 2,000.00" in text


def test_report_and_figures_are_written(tmp_path, evaluation):
    paths = write_outputs(evaluation, tmp_path)
    report = (tmp_path / "data" / "eval" / "evaluation_report.md").read_text(encoding="utf-8")
    assert "Clasificación explícita:" in report
    assert "TimeSeriesSplit" in report
    curve = tmp_path / "data" / "eval" / "learning_curve.png"
    stability = tmp_path / "data" / "eval" / "cv_stability.png"
    assert curve.stat().st_size > 10_000
    assert stability.stat().st_size > 10_000
    assert curve.read_bytes().startswith(b"\x89PNG")
    assert paths["report"].endswith("evaluation_report.md")
