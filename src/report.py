"""Result tables and the prediction chart. Computation only — nothing here prints."""

import os

import matplotlib.pyplot as plt
import pandas as pd

from src.metrics import directional_accuracy, mae, relative_mae, rmse
from src.models import N

BASELINE = "Naive"

# Theoretical relative MAE under a pure random walk, derived for N = 7 (D-014).
# Each model is a fixed weighted average of past prices, so its error variance
# under a random walk follows from its weights alone.
RANDOM_WALK_RELATIVE_MAE = {
    "Naive": 1.000,
    "Moving average": 1.690,
    "Linear trend": 1.309,
}

LINE_COLORS = ["#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B2"]


def _model_columns(results: pd.DataFrame) -> list:
    return [c for c in results.columns if c not in ("actual", "prev")]


def results_table(results: pd.DataFrame) -> pd.DataFrame:
    assert N == 7, (
        f"Random-walk constants in report.py are derived for N=7 (D-014); "
        f"models.N is {N}. Re-derive RANDOM_WALK_RELATIVE_MAE before using this function."
    )

    baseline_pred = results[BASELINE]
    rows = []
    for name in _model_columns(results):
        pred = results[name]
        rows.append(
            {
                "Model": name,
                "MAE": mae(results["actual"], pred),
                "RMSE": rmse(results["actual"], pred),
                "Directional accuracy": directional_accuracy(results["prev"], results["actual"], pred),
                "Relative MAE": relative_mae(results["actual"], pred, baseline_pred),
                "Random walk": RANDOM_WALK_RELATIVE_MAE.get(name),
            }
        )
    return pd.DataFrame(rows, columns=["Model", "MAE", "RMSE", "Directional accuracy", "Relative MAE", "Random walk"])


def yearly_table(results: pd.DataFrame) -> pd.DataFrame:
    model_names = _model_columns(results)
    rows = {}
    for year, group in results.groupby(results.index.year):
        baseline_pred = group[BASELINE]
        row = {name: relative_mae(group["actual"], group[name], baseline_pred) for name in model_names}
        row["Test days"] = len(group)
        rows[year] = row

    table = pd.DataFrame.from_dict(rows, orient="index", columns=model_names + ["Test days"])
    table.index.name = "Year"
    table["Test days"] = table["Test days"].astype(int)
    return table.sort_index()


def plot_predictions(results: pd.DataFrame, path: str, days: int = 90) -> None:
    subset = results.tail(days)

    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(subset.index, subset["actual"], color="#1a1a1a", linewidth=2.2, label="Actual")
    for name, color in zip(_model_columns(subset), LINE_COLORS):
        ax.plot(subset.index, subset[name], color=color, linewidth=1.2, label=name)

    ax.set_ylabel("Price (USDT)")
    ax.set_title(f"Actual vs. predicted — last {len(subset)} test days")
    ax.legend(frameon=False)
    ax.grid(axis="y", color="#dddddd", linewidth=0.6)
    ax.grid(axis="x", visible=False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.autofmt_xdate()
    fig.tight_layout()

    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    fig.savefig(path, dpi=150)
    plt.close(fig)
