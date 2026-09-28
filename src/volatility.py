"""Volatility target series for v2 (D-017)."""

import numpy as np
import pandas as pd


def abs_log_returns(prices: pd.Series) -> pd.Series:
    """a_t = |ln(P_t / P_{t-1})|, indexed by the later date; length n-1."""
    # iloc[1:] rather than dropna(): a missing price must stay visible as NaN.
    return np.log(prices / prices.shift(1)).abs().iloc[1:]
