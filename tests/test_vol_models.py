"""Unit tests for src.vol_models, with hand-checked expected values."""

import pandas as pd
import pytest

from src.vol_models import VOL_MODELS, ewma, expanding_mean, lag1, ma20

H4 = pd.Series([0.02, 0.04, 0.01, 0.03])
H21 = pd.Series([1.0] + [0.01] * 20)


def test_expanding_mean():
    assert expanding_mean(H4) == pytest.approx(0.025, abs=1e-9)


def test_lag1():
    assert lag1(H4) == pytest.approx(0.03, abs=1e-9)


def test_ewma_recursive():
    assert ewma(H4) == pytest.approx(0.02109632, abs=1e-8)


def test_ewma_is_not_adjusted():
    # 0.0250003 is what pandas ewm(adjust=True) gives; guards against that variant.
    assert ewma(H4) != pytest.approx(0.0250003, abs=1e-3)


def test_ma20_uses_last_20():
    assert ma20(H21) == pytest.approx(0.01, abs=1e-9)


def test_ma20_short_history_raises():
    with pytest.raises(ValueError):
        ma20(pd.Series([0.01] * 19))


def test_vol_models_keys():
    assert set(VOL_MODELS) == {"expanding_mean", "lag1", "ma20", "ewma"}
