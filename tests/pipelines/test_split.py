"""La prueba de 2024–2025 no entra en el ajuste, y el corte sale del año de origen."""

from __future__ import annotations

import pandas as pd

from pipelines.build_features import build_features, drop_warmup_rows
from pipelines.load_sales import load_official_sales
from pipelines.split import split_train_test, training_cutoff_year


def test_split_respects_8_2_rule_and_no_leakage():
    raw, notes = load_official_sales()
    assert notes["official_hash_matches"] is True
    assert notes["rows_dropped_null"] == 0
    assert len(raw) == 120

    origin = int(raw["month"].dt.year.min())
    assert origin == 2016
    assert training_cutoff_year(origin) == 2024

    usable, dropped = drop_warmup_rows(build_features(raw))
    assert dropped == 12
    train, test = split_train_test(usable, origin_year=origin)

    train_years = set(train["month"].dt.year.astype(int))
    test_years = set(test["month"].dt.year.astype(int))
    assert test_years == {2024, 2025}
    assert len(test) == 24
    assert train_years.isdisjoint(test_years)
    assert max(train_years) < min(test_years)
    assert train_years <= set(range(2016, 2024))
    assert train["month"].max() < test["month"].min()
    assert set(train["month"]).isdisjoint(set(test["month"]))
    assert 2024 not in train_years
    assert 2025 not in train_years
    # 2016 se pierde por el lag de 12 meses. No se pasa a la prueba.
    assert 2016 not in test_years
    assert train["month"].min() == pd.Timestamp("2017-01-01")
    assert len(train) == 84


def test_eight_and_two_full_years_when_warmup_is_absent():
    frame = pd.DataFrame({"month": pd.date_range("2016-01-01", periods=120, freq="MS")})
    train, test = split_train_test(frame, origin_year=2016)
    assert set(train["month"].dt.year.astype(int)) == set(range(2016, 2024))
    assert len(train) == 96
    assert set(test["month"].dt.year.astype(int)) == {2024, 2025}
    assert len(test) == 24
    assert train["month"].max() < test["month"].min()


def test_cutoff_must_use_the_raw_origin_year():
    """Si el origen se corre a 2017, 2024 deja de ser prueba. El ajuste no hace eso."""
    frame = pd.DataFrame({"month": pd.date_range("2017-01-01", periods=108, freq="MS")})
    train, test = split_train_test(frame, origin_year=2016)
    assert 2024 not in set(train["month"].dt.year.astype(int))
    assert set(test["month"].dt.year.astype(int)) == {2024, 2025}

    leaked, _held_out = split_train_test(frame, origin_year=2017)
    assert 2024 in set(leaked["month"].dt.year.astype(int))
