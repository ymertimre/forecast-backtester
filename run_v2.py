"""Entry point for v2: walk-forward backtest of volatility models on |log returns|."""

import pandas as pd

from src.backtest import run_backtest
from src.metrics import mae, relative_mae
from src.vol_models import VOL_MODELS
from src.volatility import abs_log_returns

DATA_PATH = "data/btc_daily.csv"
WARMUP = 30  # D-012
BASELINE = "expanding_mean"  # D-018, D-020


def _dates(index) -> str:
    return ", ".join(str(d.date()) for d in index)


def load_close(path: str) -> pd.Series:
    df = pd.read_csv(path, parse_dates=["date"])
    close = df.set_index("date")["close"]

    missing = close[close.isna()].index
    if len(missing):
        raise ValueError(f"close has NaN on: {_dates(missing)}")

    duplicated = close.index[close.index.duplicated()]
    if len(duplicated):
        raise ValueError(f"duplicate dates: {_dates(duplicated)}")

    step = close.index.to_series().diff().iloc[1:]
    not_increasing = step[step <= pd.Timedelta(0)].index
    if len(not_increasing):
        raise ValueError(f"index not strictly increasing at: {_dates(not_increasing)}")

    gaps = step[step != pd.Timedelta(days=1)].index
    if len(gaps):
        raise ValueError(f"gap before (difference is not exactly 1 day): {_dates(gaps)}")

    return close


def main():
    close = load_close(DATA_PATH)

    a = abs_log_returns(close)
    missing = a[a.isna()].index
    if len(missing):
        raise ValueError(f"abs log returns have NaN on: {_dates(missing)}")

    results = run_backtest(a, VOL_MODELS, warmup=WARMUP)

    print(
        f"Test days: {len(results)} "
        f"({results.index.min().date()} to {results.index.max().date()})"
    )

    baseline_pred = results[BASELINE]
    rows = [
        {
            "Model": name,
            "MAE": f"{mae(results['actual'], results[name]):.6f}",
            "Relative MAE": f"{relative_mae(results['actual'], results[name], baseline_pred):.3f}",
        }
        for name in VOL_MODELS
    ]
    print(pd.DataFrame(rows).to_string(index=False))


if __name__ == "__main__":
    main()
