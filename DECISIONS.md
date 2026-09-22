# Decision log

Every decision that shaped this project, with the alternatives that were rejected
and why. Written as the work happens, not reconstructed afterwards.

This file exists for three reasons: it becomes the reasoning section of the
README, it is what I answer from when someone asks why the project looks like
this, and it is what reminds me six months from now.

**Format**

```
## D-011 · N = 7, chosen a priori rather than searched

**Date:** 2026-09-22

**Decision:** The window for the moving average and the linear trend is 7 days.

**Alternatives:** Searching N over a grid and keeping the best performer.

**Why:** Selecting N by its backtest score means choosing a parameter on the same
data used to report performance, which turns an out-of-sample result back into an
in-sample one. Seven is fixed by reasoning instead: it is the only natural period
in a daily series. A longer window such as 30 would lag so far behind a trending
series that its loss is guaranteed before the test runs, which makes the
comparison uninformative rather than honest.

---

## D-012 · W = 30 warm-up

**Date:** 2026-09-22

**Decision:** The first 30 observations seed the models and are excluded from all
error statistics.

**Alternatives:** W = N, the technical minimum.

**Why:** N is enough for a prediction to be defined, but fixing W above it keeps
the evaluation window identical if N is ever changed, so two runs stay comparable.
Thirty days costs 3% of the series and removes any prediction made on a partially
filled window.

---

## D-013 · Directional accuracy is undefined for the naive baseline

**Date:** 2026-09-22

**Decision:** `directional_accuracy` returns `None` when every prediction equals
the last observed value, and the report prints `N/A` for that cell.

**Alternatives:** Reporting the computed 0%, or dropping zero-change days from the
denominator.

**Why:** The naive model predicts no change, so its predicted direction is neither
up nor down and never matches the realised one. The computed figure is therefore
0% for a model that makes no directional claim at all — a number that reads as
catastrophic next to the same model topping the MAE column. Dropping zero-change
days is not an option either: for the naive model that is every day, leaving an
empty denominator. Marking the metric undefined is the only reading that does not
mislead.

---

## D-0NN · *(next decision goes here)*
```

---

## D-001 · The tool evaluates forecasting methods; it does not forecast prices

**Date:** 2026-09-22

**Decision:** Build a backtesting and evaluation framework whose first dataset
happens to be Bitcoin, rather than a Bitcoin price predictor.

**Alternatives:** A crypto price prediction app, which was the original idea.

**Why:** Price series are close to a random walk, so a predictor would backtest
well and fail forward. It is also the most common beginner portfolio project,
which makes it a negative signal rather than a differentiator. Reframing it as an
evaluation framework keeps the dataset and discards the false claim — and the
honest finding ("nothing beats the naive baseline") is more memorable than a
prediction nobody should trust.

---

## D-002 · Python

**Date:** 2026-09-22

**Decision:** Python for the whole engine.

**Alternatives:** JavaScript/TypeScript running in the browser; Streamlit.

**Why:** pandas makes walk-forward and metric computation natural, and Python is
the language this work continues in. JavaScript would add friction without adding
anything to learn. Streamlit would ship faster but teaches almost nothing about
structuring software, which is part of the point of this project.

---

## D-003 · Binance public API as the data source

**Date:** 2026-09-22

**Decision:** Binance `klines` endpoint, BTCUSDT, daily interval.

**Alternatives:** CoinGecko.

**Why:** No API key, no registration, daily OHLCV directly, and no restriction on
how far back the free tier reaches. CoinGecko's free tier limits historical range.

**Consequence:** the endpoint returns at most ~1,000 candles per request, so three
years of daily data requires paging and concatenating.

---

## D-004 · Frozen snapshot, not live fetching

**Date:** 2026-09-22

**Decision:** Fetch once, commit `data/btc_daily.csv`, and have the backtest read
only from that file.

**Alternatives:** Call the API on every run.

**Why:** Reproducibility. The value of this project is a finding, and a finding
that changes on every run cannot be checked by anyone else. `src/fetch.py`
regenerates the snapshot when the data needs refreshing; that is a separate,
deliberate act.

---

## D-005 · One-day-ahead horizon

**Date:** 2026-09-22

**Decision:** Predict one day ahead.

**Alternatives:** Seven or thirty days.

**Why:** It is the cleanest comparison and the hardest test, because the naive
baseline is strongest at short horizons. Longer horizons look more useful but add
noise and blur the finding.

---

## D-006 · Three models, one of them the baseline

**Date:** 2026-09-22

**Decision:** Naive, moving average, linear trend.

**Alternatives:** Adding ARIMA, Prophet or an LSTM.

**Why:** The point is the comparison, not the model zoo. Three simple methods that
can each be explained in one sentence make the result legible. A neural network
would add complexity without changing the conclusion, and would make the project
harder to defend.

---

## D-007 · Relative MAE as the headline number

**Date:** 2026-09-22

**Decision:** Report `MAE(model) / MAE(naive)` as the primary result, with MAE,
RMSE and directional accuracy alongside it.

**Alternatives:** Absolute MAE as the headline.

**Why:** An absolute error of "1,240 USD" carries no judgement. A ratio of "1.03"
says immediately that the model is three per cent worse than doing nothing.
Directional accuracy is kept separate because a model can have a reasonable MAE
and still be a coin flip on direction, which makes it useless for a decision.

---

## D-008 · Walk-forward, not a single train/test split

**Date:** 2026-09-22

**Decision:** Re-fit at every step and predict one step forward, producing one
out-of-sample error per test day.

**Alternatives:** Split the series once into train and test.

**Why:** A single split measures how one arbitrary period happened to go. Walk-
forward produces a distribution of hundreds of errors, so both the average and its
stability are meaningful.

---

## D-009 · A shared model interface, enforcing no lookahead

**Date:** 2026-09-22

**Decision:** Every model is `predict(history: pd.Series) -> float`, receiving only
the data available before the point being predicted.

**Alternatives:** Letting each model access the full series and trusting the
implementation not to look ahead.

**Why:** Two benefits from one contract. The backtest loop becomes independent of
the models, so adding a method changes nothing else. And lookahead bias becomes
structurally impossible rather than something to be careful about — a model cannot
see the future because it is never handed the future.

---

## D-010 · Two stages, and stage one is complete on its own

**Date:** 2026-09-22

**Decision:** Stage 1 is the engine, run from the terminal, producing results and a
chart. Stage 2 is an optional static page deployed to GitHub Pages.

**Alternatives:** Building the web interface alongside the engine.

**Why:** Stage 1 alone is a finished, defensible artefact. An unfinished web page
attached to a working engine is worth less than the engine by itself.

---

## D-0NN · *(next decision goes here)*
