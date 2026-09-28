"""Volatility forecasting methods for v2, sharing predict(history: pd.Series) -> float."""

import pandas as pd

# D-019: fixed a priori (RiskMetrics convention for lambda), not searched.
MA_WINDOW = 20
EWMA_LAMBDA = 0.94


def expanding_mean(history: pd.Series) -> float:
    return float(history.mean())


def lag1(history: pd.Series) -> float:
    return float(history.iloc[-1])


def ma20(history: pd.Series) -> float:
    if len(history) < MA_WINDOW:
        raise ValueError(f"ma20 requires at least {MA_WINDOW} observations, got {len(history)}")
    return float(history.iloc[-MA_WINDOW:].mean())


def ewma(history: pd.Series) -> float:
    # adjust=False gives the recursion s_1 = a_1, s_t = lambda*s_{t-1} + (1-lambda)*a_t;
    # the pandas default adjust=True is a different estimator.
    return float(history.ewm(alpha=1 - EWMA_LAMBDA, adjust=False).mean().iloc[-1])


VOL_MODELS = {
    "expanding_mean": expanding_mean,
    "lag1": lag1,
    "ma20": ma20,
    "ewma": ewma,
}
