"""Walk-forward backtest loop: expanding window, one step ahead per test day."""

import pandas as pd


def run_backtest(prices: pd.Series, models: dict, warmup: int) -> pd.DataFrame:
    dates = []
    rows = []
    for t in range(warmup, len(prices)):
        history = prices.iloc[:t]
        row = {"actual": prices.iloc[t], "prev": prices.iloc[t - 1]}
        for name, model in models.items():
            row[name] = model(history)
        dates.append(prices.index[t])
        rows.append(row)
    return pd.DataFrame(rows, index=pd.Index(dates, name=prices.index.name))
