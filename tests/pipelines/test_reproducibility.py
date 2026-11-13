"""La semilla fija el pronóstico y el escalador no ve la prueba."""

from __future__ import annotations

import numpy as np
import pandas as pd

from pipelines.build_features import FEATURE_COLUMNS
from pipelines.load_sales import TARGET_COLUMN, load_official_sales
from pipelines.train_sales_model import fit_model


def test_two_fits_match_and_scaler_uses_train_only():
    raw, _notes = load_official_sales()
    first = fit_model(raw)
    second = fit_model(raw)
    np.testing.assert_allclose(first["predicted"], second["predicted"])
    assert first["model"].random_state == 42
    assert second["model"].random_state == 42

    train_mean = first["train"].loc[:, list(FEATURE_COLUMNS)].mean().to_numpy()
    full = pd.concat([first["train"], first["test"]], ignore_index=True)
    full_mean = full.loc[:, list(FEATURE_COLUMNS)].mean().to_numpy()
    np.testing.assert_allclose(first["scaler"].mean_, train_mean)
    assert not np.allclose(first["scaler"].mean_, full_mean)

    # El objetivo de prueba no está entre las filas con las que se ajustó el bosque.
    assert set(first["test"]["month"]).isdisjoint(set(first["train"]["month"]))
    assert first["test"][TARGET_COLUMN].mean() != first["train"][TARGET_COLUMN].mean()
