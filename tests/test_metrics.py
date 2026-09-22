"""Unit tests for src.metrics, with hand-checked expected values."""

import pandas as pd
import pytest

from src.metrics import directional_accuracy, mae, relative_mae, rmse

PREV = pd.Series([100, 102, 101, 105])
ACTUAL = pd.Series([102, 101, 105, 104])
PRED = pd.Series([103, 100, 108, 109])


def test_mae():
    assert mae(ACTUAL, PRED) == pytest.approx(2.5)


def test_rmse():
    assert rmse(ACTUAL, PRED) == pytest.approx(3.0)


def test_directional_accuracy():
    assert directional_accuracy(PREV, ACTUAL, PRED) == pytest.approx(0.75)


def test_relative_mae():
    assert relative_mae(ACTUAL, PRED, PREV) == pytest.approx(1.25)


def test_directional_accuracy_none_when_prediction_equals_last_observed():
    # D-013: a prediction equal to prev states no direction, so every day is
    # ambiguous and the metric is undefined rather than a misleading 0%.
    assert directional_accuracy(PREV, ACTUAL, PREV) is None
