"""PSI, Gini y K² sobre vectores conocidos, sin tocar el CSV de Nexova."""

from __future__ import annotations

import numpy as np

from pipelines.metrics import dagostino_k2, normalized_gini, population_stability_index


def test_normalized_gini_rewards_a_perfect_ranking():
    actual = np.arange(1, 21, dtype=float)
    perfect = normalized_gini(actual, actual)
    reversed_rank = normalized_gini(actual, actual[::-1])
    np.testing.assert_allclose(perfect, 1.0)
    assert reversed_rank < 0.0


def test_psi_is_near_zero_on_the_same_sample_and_rises_when_it_shifts():
    generator = np.random.default_rng(42)
    base = generator.normal(loc=0.0, scale=1.0, size=800)
    shifted = generator.normal(loc=1.5, scale=1.0, size=800)
    assert population_stability_index(base, base) < 0.02
    assert population_stability_index(base, shifted) > 0.25


def test_k2_returns_a_finite_statistic_and_a_pvalue():
    residuals = np.array([1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 40.0])
    statistic, p_value = dagostino_k2(residuals)
    assert np.isfinite(statistic)
    assert 0.0 <= p_value <= 1.0
