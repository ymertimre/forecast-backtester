"""Forecasting methods sharing predict(history: pd.Series) -> float."""

import numpy as np
import pandas as pd

N = 7  # window for moving_average and linear_trend, per D-011


def naive(history: pd.Series) -> float:
    if len(history) < 1:
        raise ValueError(f"naive requires at least 1 observation, got {len(history)}")
    return float(history.iloc[-1])


def moving_average(history: pd.Series) -> float:
    if len(history) < N:
        raise ValueError(f"moving_average requires at least {N} observations, got {len(history)}")
    return float(history.iloc[-N:].mean())


def linear_trend(history: pd.Series) -> float:
    if len(history) < N:
        raise ValueError(f"linear_trend requires at least {N} observations, got {len(history)}")
    window = history.iloc[-N:].to_numpy(dtype=float)
    x = np.arange(N)
    slope, intercept = np.polyfit(x, window, 1)
    return float(slope * N + intercept)


MODELS = {
    "Naive": naive,
    "Moving average": moving_average,
    "Linear trend": linear_trend,
}
