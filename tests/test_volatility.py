"""Unit tests for src.volatility, with hand-checked expected values."""

import pandas as pd
import pytest

from src.volatility import abs_log_returns

PRICES = pd.Series(
    [100.0, 110.0, 99.0, 99.0],
    index=pd.date_range("2024-01-01", periods=4, freq="D"),
)


def test_values():
    result = abs_log_returns(PRICES)
    assert result.tolist() == pytest.approx([0.09531, 0.10536, 0.0], abs=1e-5)


def test_zero_return_is_exactly_zero():
    result = abs_log_returns(PRICES)
    assert result.iloc[2] == pytest.approx(0.0, abs=1e-12)


def test_length_and_index():
    result = abs_log_returns(PRICES)
    assert len(result) == 3
    assert result.index.equals(PRICES.index[1:])


def test_non_negative():
    result = abs_log_returns(PRICES)
    assert (result >= 0).all()
