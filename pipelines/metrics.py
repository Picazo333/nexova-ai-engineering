"""MSE, PSI, Gini y K² de D'Agostino–Pearson. Solo tienen sentido en prueba."""

from __future__ import annotations

import numpy as np
from scipy import stats

PSI_BINS = 5
PSI_EPSILON = 1e-6


def mean_squared_error(actual: np.ndarray, predicted: np.ndarray) -> float:
    actual = np.asarray(actual, dtype=float)
    predicted = np.asarray(predicted, dtype=float)
    return float(np.mean((actual - predicted) ** 2))


def population_stability_index(
    expected: np.ndarray,
    actual: np.ndarray,
    bins: int = PSI_BINS,
) -> float:
    """PSI clásico. ``expected`` es el periodo de entrenamiento y ``actual`` el de prueba.

    Los cortes salen de los cuantiles del entrenamiento. Un valor bajo indica
    que la distribución del periodo de prueba se parece a la de entrenamiento.
    Guía habitual: por debajo de 0.10 estable, de 0.10 a 0.25 cambio moderado,
    por encima de 0.25 cambio notable. No es una métrica de acierto del modelo.
    """
    expected = np.asarray(expected, dtype=float)
    actual = np.asarray(actual, dtype=float)
    if expected.size == 0 or actual.size == 0:
        raise ValueError("PSI necesita observaciones en los dos periodos.")
    edges = np.quantile(expected, np.linspace(0.0, 1.0, bins + 1))
    edges = np.unique(edges.astype(float))
    if edges.size < 3:
        low = float(min(expected.min(), actual.min()))
        high = float(max(expected.max(), actual.max()))
        if high == low:
            high = low + 1.0
        edges = np.linspace(low, high, num=min(bins, 3) + 1)
    edges = edges.copy()
    edges[0] = min(float(edges[0]), float(expected.min()), float(actual.min()))
    edges[-1] = max(float(edges[-1]), float(expected.max()), float(actual.max()))
    if not np.all(np.diff(edges) > 0):
        edges = np.linspace(edges[0], edges[-1] + 1e-6, num=3)

    expected_counts, _ = np.histogram(expected, bins=edges)
    actual_counts, _ = np.histogram(actual, bins=edges)
    expected_share = expected_counts / expected_counts.sum()
    actual_share = actual_counts / actual_counts.sum()
    expected_share = np.clip(expected_share, PSI_EPSILON, None)
    actual_share = np.clip(actual_share, PSI_EPSILON, None)
    expected_share = expected_share / expected_share.sum()
    actual_share = actual_share / actual_share.sum()
    return float(np.sum((actual_share - expected_share) * np.log(actual_share / expected_share)))


def _gini_sorted(actual: np.ndarray, predicted: np.ndarray) -> float:
    """Gini de Lorenz ordenando el ingreso real por la predicción, de mayor a menor."""
    actual = np.asarray(actual, dtype=float)
    predicted = np.asarray(predicted, dtype=float)
    count = actual.size
    order = np.lexsort((np.arange(count), -predicted))
    ordered = actual[order]
    total = float(ordered.sum())
    if total == 0.0:
        return float("nan")
    cumulative = np.cumsum(ordered)
    return float((cumulative.sum() / total - (count + 1) / 2.0) / count)


def normalized_gini(actual: np.ndarray, predicted: np.ndarray) -> float:
    """1 si el pronóstico ordena los meses igual que el ingreso real; 0 si no ordena.

    Laura necesita separar un agosto flojo de una caída rara. El Gini mide ese
    orden, no el tamaño del error en dólares. Se normaliza por el Gini del
    propio ingreso para que un ranking perfecto valga 1.
    """
    denominator = _gini_sorted(actual, actual)
    if not np.isfinite(denominator) or denominator == 0.0:
        return float("nan")
    return float(_gini_sorted(actual, predicted) / denominator)


def dagostino_k2(residuals: np.ndarray) -> tuple[float, float]:
    """K² de D'Agostino–Pearson sobre los residuos de prueba, y su p-valor.

    Contrasta si los residuos se parecen a una normal. Un MSE pequeño con un
    K² alto (p pequeño) indica errores sesgados o con colas: el promedio
    esconde meses que fallan siempre hacia el mismo lado. Con 24 meses el
    contraste tiene poca potencia; el número se reporta, no se sobreinterpreta.
    """
    sample = np.asarray(residuals, dtype=float)
    if sample.size < 8:
        raise ValueError("K² de D'Agostino–Pearson pide al menos 8 residuos.")
    statistic, p_value = stats.normaltest(sample)
    return float(statistic), float(p_value)
