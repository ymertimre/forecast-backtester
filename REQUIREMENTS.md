# Requirements — v1

Written before any code. Anything not listed here is out of scope for v1.

---

## 1. What it does

A tool that evaluates a time-series forecasting method against a naive baseline
using walk-forward backtesting.

The product is the evaluation framework. Bitcoin is the first dataset it is
pointed at, not the subject of the project.

## 2. User and question

**User:** an analyst who has a forecasting method and wants to know whether it is
worth using.

**Question:** *"Does my method do better than doing nothing?"*

The user is explicitly **not** someone looking for a price prediction. Losing
that distinction turns the project into a crypto predictor, which is not what is
being built.

## 3. Input

| | |
|---|---|
| Asset | BTCUSDT, single asset |
| Granularity | Daily close |
| History | 3 years (~1,095 rows) |
| Source | Binance public API, `klines` endpoint — no key required |
| Storage | **Frozen snapshot** committed as `data/btc_daily.csv` |

Columns: `date`, `close`.

The snapshot is deliberate. Fetching live would mean the numbers change on every
run and no one could reproduce a published finding. `src/fetch.py` regenerates the
snapshot on demand; the backtest never calls the API.

The API returns a maximum of ~1,000 candles per request, so three years requires
paging and concatenating.

## 4. Output

**Headline number:** relative MAE — `MAE(model) / MAE(naive)`.
Below 1 means the model beats the baseline. At or above 1 it does not.

A ratio rather than an absolute error, because "1,240 USD" means nothing on its
own while "1.03" says immediately that the model is 3% worse than doing nothing.

**Results table:** one row per model.

| Model | MAE | RMSE | Directional accuracy | Relative MAE |
|---|---|---|---|---|

**Chart:** actual series with model predictions overlaid.

**Per-year breakdown:** each model's error by calendar year. A single overall
figure hides a method that only works in one market regime; splitting by year
makes that visible.

## 5. Out of scope

- User accounts, database, authentication
- Live or streaming price data
- More than three models
- More than one asset
- **Any trading signal, position recommendation or return simulation**

The last item is a boundary, not a scoping choice. This tool evaluates methods; it
does not advise on financial decisions.

---

## Analytical decisions

**Horizon: one day ahead.** The cleanest test and the hardest one — it is exactly
where the random-walk baseline is strongest. A seven-day horizon looks more useful
but is noisier and blurs the finding.

**Models: three, including the baseline.**

| Model | Prediction for t+1 |
|---|---|
| Naive (baseline) | Close at t |
| Moving average | Mean of the last N closes |
| Linear trend | Line fitted to the last N closes, extended one step |

N is a parameter, not a constant. Its value is a decision to record in
`DECISIONS.md` once chosen.

**Baseline: naive, `price(t+1) = price(t)`.** Every other model is measured
against it.

**Metrics:** MAE as primary, RMSE alongside it, directional accuracy as a separate
lens, relative MAE as the headline.

**Backtest: walk-forward, expanding window.** Re-fit at every step, predict one
step, record the error. Never a single train/test split.

**Warm-up:** the first W observations are used only to seed the models and are
excluded from the error statistics, so that early predictions made on almost no
history do not distort the result. W is to be decided and recorded.

---

## Acceptance criteria for v1

Version 1 is done when all of the following hold:

1. `data/btc_daily.csv` contains roughly 1,095 rows with no gaps and no duplicate
   dates, and the final row matches the real BTC close for that date.
2. Every model implements `predict(history) -> float` and is called only with
   data available before the predicted point.
3. The walk-forward loop produces one out-of-sample error per model per test day.
4. The metric functions are covered by unit tests with hand-checked expected
   values.
5. The report shows the table, the chart and the per-year breakdown.
6. The README states the finding in plain language, including the case where no
   model beats the baseline.
