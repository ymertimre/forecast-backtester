"""Error metrics for comparing forecasts against actuals."""

import numpy as np
import pandas as pd


def mae(actual: pd.Series, pred: pd.Series) -> float:
    return float((actual - pred).abs().mean())


def rmse(actual: pd.Series, pred: pd.Series) -> float:
    return float(np.sqrt(((actual - pred) ** 2).mean()))


def directional_accuracy(prev: pd.Series, actual: pd.Series, pred: pd.Series):
    pred_diff = pred - prev
    if (pred_diff == 0).all():
        # D-013: a prediction equal to prev states no direction, so the
        # metric is undefined rather than a misleading 0%.
        return None
    actual_diff = actual - prev
    correct = np.sign(pred_diff) == np.sign(actual_diff)
    return float(correct.mean())


def relative_mae(actual: pd.Series, pred: pd.Series, baseline_pred: pd.Series) -> float:
    return float(mae(actual, pred) / mae(actual, baseline_pred))
