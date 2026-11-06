"""Split cronológico: primeros 8 años para entrenar, 2 últimos para probar."""

from __future__ import annotations

import pandas as pd

TRAIN_YEARS = 8
TEST_YEARS = 2


def training_cutoff_year(origin_year: int, train_years: int = TRAIN_YEARS) -> int:
    """Primer año de la prueba. Con origen 2016 y 8 años de entrenamiento, 2024."""
    return int(origin_year) + int(train_years)


def split_train_test(
    df: pd.DataFrame,
    origin_year: int,
    train_years: int = TRAIN_YEARS,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Corta por año calendario. No baraja.

    ``origin_year`` es el primer año de la serie cruda, no el primer año que
    queda tras tirar el calentamiento de los lags. Si se usa el año posterior
    al calentamiento, el corte se corre y un año de prueba entra en el ajuste.
    """
    cutoff = training_cutoff_year(origin_year, train_years)
    years = df["month"].dt.year
    train = df.loc[years < cutoff].sort_values("month").reset_index(drop=True)
    test = df.loc[years >= cutoff].sort_values("month").reset_index(drop=True)
    if train.empty or test.empty:
        raise ValueError(f"El split quedó vacío. El corte de prueba es {cutoff}.")
    if train["month"].max() >= test["month"].min():
        raise ValueError("La prueba no queda estrictamente después del entrenamiento.")
    shared_months = set(train["month"]).intersection(set(test["month"]))
    if shared_months:
        raise ValueError("Hay meses repetidos en entrenamiento y en prueba.")
    shared_years = set(train["month"].dt.year).intersection(set(test["month"].dt.year))
    if shared_years:
        raise ValueError("Hay años compartidos entre entrenamiento y prueba.")
    return train, test
