# forecast-backtester

A tool for evaluating time-series forecasting methods against a naive baseline,
using walk-forward backtesting.

**Status:** in progress — see [Scope](#scope) for what is and is not built yet.

---

## The question

Most forecasting write-ups report how closely a model fits the data. That is the
wrong question. The right one is:

> **Does this forecasting method do better than doing nothing?**

For a price series, "doing nothing" means predicting that tomorrow equals today —
the random-walk baseline. A model that cannot beat it has produced nothing of
value, however sophisticated it looks. This tool measures that comparison
honestly.

The first dataset is Bitcoin daily closing prices. The tool itself is not
specific to crypto, or to prices: any ordered series can be passed through it.

## Method

### Walk-forward backtesting

A single train/test split tells you how one arbitrary period happened to go. This
tool re-fits at every step instead:

```
train on days 1..t     → predict day t+1 → record the error
train on days 1..t+1   → predict day t+2 → record the error
train on days 1..t+2   → ...
```

Every prediction is made on data the model has never seen, and the result is a
distribution of hundreds of out-of-sample errors rather than a single number.

### No lookahead by construction

Every model implements the same interface:

```python
def predict(history: pd.Series) -> float:
    """Given prices up to and including day t, return a prediction for t+1."""
```

A model receives only the history available at the time of the prediction. It
cannot see the future because it is never given the future — the constraint is
enforced by the architecture rather than by care.

This matters: fitting a model on the whole series and then measuring its error on
that same series produces excellent results that mean nothing. It is the most
common failure in published price-forecasting work.

### Models

| Model | Prediction for day t+1 |
|---|---|
| **Naive** (baseline) | The closing price on day t |
| Moving average | The mean of the last N closes |
| Linear trend | A line fitted to the last N closes, extended one step |

### Metrics

- **MAE** — mean absolute error, the primary measure
- **RMSE** — penalises large misses more heavily
- **Directional accuracy** — how often the predicted direction of movement was
  correct. A model can have a respectable MAE and still be a coin flip on
  direction, which makes it useless for a decision.
- **Relative MAE** — `MAE(model) / MAE(naive)`, the headline number. Below 1 means
  the model beats the baseline; at or above 1 it does not.

Errors are also reported per calendar year, because a single overall figure can
hide a method that only works in one market regime.

## Data

Bitcoin (BTCUSDT) daily closes, three years, from the Binance public API.

The data is committed to the repository as a frozen snapshot (`data/btc_daily.csv`)
rather than fetched at run time, so that every run reproduces the same numbers.
`src/fetch.py` regenerates the snapshot when needed.

## Repository layout

```
data/          frozen price snapshot
src/
  fetch.py     Binance API -> CSV (run once)
  models.py    one function per forecasting method
  backtest.py  the walk-forward loop
  metrics.py   MAE, RMSE, directional accuracy, relative MAE
  report.py    table and chart output
tests/         unit tests for the metric functions
run.py         entry point
```

## How to run

*To be completed once the engine runs.*

## Findings

*To be completed once the backtest runs.*

## Scope

Built for version 1:

- One asset (BTC), daily granularity, three years of history
- One-day-ahead forecasts
- Three models including the baseline
- Results as a table, a chart and a per-year breakdown

Deliberately excluded:

- Live or streaming price data
- More than three models
- Multiple assets
- Any trading signal, position sizing or return simulation

## Not investment advice

This project evaluates forecasting *methods*. It does not predict prices and is
not intended to inform any financial decision. The expected result is that none
of the models beat the naive baseline.
