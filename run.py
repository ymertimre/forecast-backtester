"""Entry point: run the walk-forward backtest and print the results table."""

import pandas as pd

from src.backtest import run_backtest
from src.metrics import directional_accuracy, mae, relative_mae, rmse
from src.models import MODELS

DATA_PATH = "data/btc_daily.csv"
WARMUP = 30  # per D-012
BASELINE = "Naive"


def main():
    df = pd.read_csv(DATA_PATH, parse_dates=["date"]).sort_values("date")
    prices = df.set_index("date")["close"]

    results = run_backtest(prices, MODELS, warmup=WARMUP)

    print(
        f"Test days: {len(results)} "
        f"({results.index.min().date()} to {results.index.max().date()})"
    )

    baseline_pred = results[BASELINE]
    rows = []
    for name in MODELS:
        pred = results[name]
        da = directional_accuracy(results["prev"], results["actual"], pred)
        rows.append(
            {
                "Model": name,
                "MAE": f"{mae(results['actual'], pred):.2f}",
                "RMSE": f"{rmse(results['actual'], pred):.2f}",
                "Directional accuracy": "N/A" if da is None else f"{da * 100:.1f}%",
                "Relative MAE": f"{relative_mae(results['actual'], pred, baseline_pred):.3f}",
            }
        )

    print(pd.DataFrame(rows).to_string(index=False))


if __name__ == "__main__":
    main()
