"""Unit tests for src.uncertainty, with hand-checked expected values."""

import numpy as np
import pandas as pd
import pytest

from src.uncertainty import bootstrap_relative_mae, moving_block_indices, ratio_of_mae


def test_ratio_of_mae_hand_values():
    model = np.array([1.0, 2.0, 3.0, 4.0])
    base = np.array([2.0, 2.0, 2.0, 2.0])
    assert ratio_of_mae(model, base, np.array([0, 0, 3, 3])) == pytest.approx(1.25)
    assert ratio_of_mae(model, base, np.array([0, 1, 0, 1])) == pytest.approx(0.75)
    assert ratio_of_mae(model, base, np.array([0, 1, 2, 3])) == pytest.approx(1.25)


@pytest.mark.parametrize("n", [100, 105])
def test_block_indices_structure(n):
    idx = moving_block_indices(n, 20, np.random.default_rng(0))
    assert len(idx) == n
    assert np.all((idx >= 0) & (idx < n))
    for k in range(1, n):
        if k % 20 != 0:
            assert idx[k] == idx[k - 1] + 1


def test_identical_errors_give_unit_interval():
    base = np.random.default_rng(1).uniform(0.5, 2.0, 200)
    result = bootstrap_relative_mae(pd.Series(np.zeros(200)), pd.Series(base), pd.Series(base))
    assert result == pytest.approx((1.0, 1.0), abs=1e-12)


def test_paired_resampling_scaled_errors():
    # Only paired resampling gives exactly 2.0 in every resample.
    base = np.random.default_rng(1).uniform(0.5, 2.0, 200)
    result = bootstrap_relative_mae(pd.Series(np.zeros(200)), pd.Series(2 * base), pd.Series(base))
    assert result == pytest.approx((2.0, 2.0), abs=1e-12)


def test_reproducible_with_seed():
    actual = pd.Series(np.zeros(200))
    pred = pd.Series(np.random.default_rng(2).uniform(0, 1, 200))
    baseline_pred = pd.Series(np.random.default_rng(3).uniform(0, 1, 200))
    first = bootstrap_relative_mae(actual, pred, baseline_pred, seed=42)
    second = bootstrap_relative_mae(actual, pred, baseline_pred, seed=42)
    assert second == pytest.approx(first, rel=0, abs=0)
