"""Confidence intervals for relative MAE via a 20-day moving-block bootstrap (D-015).

Blocks preserve the volatility clustering that an i.i.d. day-level resample would
destroy, and each resample is paired: model and baseline errors are drawn with the
same indices, so a volatile day enters numerator and denominator together.
"""

import math

import numpy as np
import pandas as pd


def moving_block_indices(n: int, block: int, rng: np.random.Generator) -> np.ndarray:
    n_blocks = math.ceil(n / block)
    starts = rng.integers(0, n - block + 1, size=n_blocks)
    return (starts[:, None] + np.arange(block)).ravel()[:n]


def ratio_of_mae(abs_err_model: np.ndarray, abs_err_base: np.ndarray, idx: np.ndarray) -> float:
    return float(abs_err_model[idx].mean() / abs_err_base[idx].mean())


def bootstrap_relative_mae(
    actual: pd.Series,
    pred: pd.Series,
    baseline_pred: pd.Series,
    block: int = 20,  # defaults fixed a priori (D-015), not tuned
    n_boot: int = 2000,
    seed: int = 42,
) -> tuple[float, float]:
    abs_err_model = np.abs(actual.to_numpy(dtype=float) - pred.to_numpy(dtype=float))
    abs_err_base = np.abs(actual.to_numpy(dtype=float) - baseline_pred.to_numpy(dtype=float))

    rng = np.random.default_rng(seed)
    n = len(abs_err_model)
    ratios = np.empty(n_boot)
    for i in range(n_boot):
        idx = moving_block_indices(n, block, rng)
        ratios[i] = ratio_of_mae(abs_err_model, abs_err_base, idx)

    low, high = np.percentile(ratios, [2.5, 97.5])
    return float(low), float(high)
