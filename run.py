"""Entry point: run the walk-forward backtest and print the results."""

import pandas as pd

from src.backtest import run_backtest
from src.metrics import relative_mae
from src.models import MODELS
from src.report import plot_predictions, results_table, yearly_table
from src.report import BASELINE
from src.uncertainty import bootstrap_relative_mae

DATA_PATH = "data/btc_daily.csv"
WARMUP = 30  # per D-012
CHART_PATH = "output/predictions.png"


def _format_results_table(table: pd.DataFrame) -> pd.DataFrame:
    formatted = table[["Model"]].copy()
    formatted["MAE"] = table["MAE"].map(lambda v: f"{v:.2f}")
    formatted["RMSE"] = table["RMSE"].map(lambda v: f"{v:.2f}")
    formatted["Directional accuracy"] = table["Directional accuracy"].map(
        lambda v: "N/A" if pd.isna(v) else f"{v * 100:.1f}%"
    )
    formatted["Relative MAE"] = table["Relative MAE"].map(lambda v: f"{v:.3f}")
    formatted["Random walk"] = table["Random walk"].map(lambda v: f"{v:.3f}")
    return formatted


def _format_yearly_table(table: pd.DataFrame) -> pd.DataFrame:
    formatted = pd.DataFrame(index=table.index)
    for column in table.columns:
        if column == "Test days":
            formatted[column] = table[column]
        else:
            formatted[column] = table[column].map(lambda v: f"{v:.3f}")
    return formatted


def main():
    df = pd.read_csv(DATA_PATH, parse_dates=["date"]).sort_values("date")
    prices = df.set_index("date")["close"]

    results = run_backtest(prices, MODELS, warmup=WARMUP)

    print(
        f"Test days: {len(results)} "
        f"({results.index.min().date()} to {results.index.max().date()})"
    )
    print(_format_results_table(results_table(results)).to_string(index=False))
    print()
    print(_format_yearly_table(yearly_table(results)).to_string())

    plot_predictions(results, CHART_PATH)
    print(f"\nChart written to {CHART_PATH}")

    print(f"\nRelative MAE vs {BASELINE}, 95% moving-block bootstrap interval (D-015):")
    baseline_pred = results[BASELINE]
    for name in MODELS:
        if name == BASELINE:
            continue
        point = relative_mae(results["actual"], results[name], baseline_pred)
        low, high = bootstrap_relative_mae(results["actual"], results[name], baseline_pred)
        print(f"  {name}: {point:.3f} [{low:.3f}, {high:.3f}]")


if __name__ == "__main__":
    main()
