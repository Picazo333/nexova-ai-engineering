# Nexova monthly revenue forecast

Forecast of consolidated monthly revenue for Nexova Solutions. The series is the official file `data/raw/nexova_sales.csv` (2016-01 through 2025-12, 120 rows). It is not generated in this repository. Provenance and SHA-256: [`data/raw/SALES_DATASET.md`](../data/raw/SALES_DATASET.md). Column meanings and the seasonality pattern: [`data/raw/nexova-BRIEFING.en.md`](../data/raw/nexova-BRIEFING.en.md).

_Versión en español: [README.es.md](./README.es.md)._

## Run

From the repository root, with [uv](https://docs.astral.sh/uv/):

```bash
uv sync --all-groups
uv run python scripts/train_sales_forecast.py
uv run pytest
```

The training script writes:

| File | Content |
| --- | --- |
| `output/metrics.md` | Test-set metrics, split, seasonality check, observed annual growth |
| `output/metrics.json` | The same numbers for diffing |
| `output/forecast_vs_actual.png` | 2024–2025 actual revenue, forecast, and tree-dispersion band |
| `output/decomposition.png` | Multiplicative trend / seasonality / residual |
| `output/feature_importance.png` | Impurity importance of the features the forest actually splits on |
| `output/train.log` | The short terminal summary |

`data/process/` is intentionally empty of a second copy of the series. Features are recomputed by the script.

## What the model is asked to do

Predict `revenue_usd` for `business_line=consolidated`. Training uses the first 8 calendar years of the raw series (2016–2023). The check uses the 2 most recent years (2024–2025). The split is chronological. Rows are not shuffled.

The first 12 months are dropped after feature construction because a 12-month lag and a 12-month rolling window have no past yet. Those months are all of 2016. They are not moved into the test set. Usable training rows are 2017-01 through 2023-12 (84 months). The test set is 2024-01 through 2025-12 (24 months). The cutoff year is `origin_year + 8` (2024), and `origin_year` is taken from the raw file, not from the first row that survives the warmup.

## Features

All of these are inputs to `RandomForestRegressor`. The target column is not an input.

| Family | Columns | Rule |
| --- | --- | --- |
| Lag | `revenue_lag_1`, `revenue_lag_12`, `contracts_lag_1`, `avg_contract_value_lag_1` | `shift`. Row `t` sees the value at `t-k`, never at `t` or later. |
| Rolling | `revenue_roll_mean_3`, `revenue_roll_std_12` | `shift(1)` and then `rolling`. The current month is outside the window. |
| Calendar | `month_sin`, `month_cos`, `quarter`, `trend_month_index` | Taken from the month label, which is known before revenue is closed. |

Same-month `active_contracts` and `avg_contract_value_usd` are not features. They describe the month being forecast.

Null and blank cells in the raw columns are dropped before training. The official file has none (`rows_dropped_null = 0`). The warmup nulls created by lags are dropped and counted.

`StandardScaler` is fit on the training rows only and then applied to the test rows. A random forest is invariant to a per-column affine rescaling, so the scaler does not change the forest's splits in substance. It is still fit on train only: the assignment asks for scaling across different magnitudes, and a later linear model must not see the test period.

## Why Random Forest

`RandomForestRegressor` from scikit-learn, not XGBoost.

- **Size.** 84 training months is a short series. A depth-capped forest does not need a boosting search.
- **Explainability.** Finance asked for an error that can be explained, and for a range rather than one optimistic number. The forest averages trees. The band on the chart is the standard deviation across those trees.
- **Tuning time.** Hyperparameters stay fixed: 400 trees, `max_depth=6`, `min_samples_leaf=2`, `random_state=42`, `n_jobs=1`. They are not chosen by looking at 2024–2025.

XGBoost would be the choice if the goal were to squeeze accuracy and there was time to tune it. That is not this request.

The same justification is in the module docstring area of `pipelines/train_sales_model.py` (`MODEL_JUSTIFICATION`).

## Metrics (test set only)

Reported in `output/metrics.md`. Definitions:

- **MSE** — mean of `(actual − forecast)²` on the 24 test months, in USD². Also reported as RMSE in USD, and RMSE divided by the mean test-month revenue, so the error can be read as a percent of a typical month. A low MSE on the training years would only show that the model remembers them. The number that counts is the test number. Training MSE is printed underneath as a diagnostic and is not the result.
- **PSI** — Population Stability Index between the training-period distribution (expected) and the test-period distribution (actual), using quantile bins from the training period. It does not score whether a given month was forecast well. It scores whether the test years moved away from the training distribution. The official CSV contains only `consolidated` rows, so there is no business-line mix to compare. Inventing headhunting, outsourcing, and training series would contradict the briefing. Two PSI figures are published: one on the revenue level (growth shows up here) and one on revenue divided by its own year's mean (the within-year shape). Usual reading guide: under 0.10 stable, 0.10 to 0.25 moderate, above 0.25 a clear shift.
- **Gini** — normalized Gini of the ranking. Months are ordered by the forecast, from high to low, and the cumulative actual revenue is compared with a perfect ranking of actual revenue. 1 means the forecast orders high-revenue months above low-revenue months perfectly. This is the metric that speaks to telling a normal August from an abnormal drop. It is not the dollar error.
- **K² Score** — D'Agostino–Pearson K² from `scipy.stats.normaltest` on the test residuals (`actual − forecast`), plus the p-value. A large K² and a small p-value mean the residuals do not look normal, so a single MSE hides skew or heavy tails. With 24 months the test has little power; both numbers are reported and not over-read.

A lag-1 naive forecast (predict each test month with the previous month's actual revenue) is included as a reference, not as a second model.

## Results and limitations

The level PSI is 6.3753. That means 2024–2025 revenue sits above the training range, and a random forest does not extrapolate the trend. On the test set the highest prediction is 987,295.59 USD and the highest actual value is 1,145,988.88 USD.

On the same 24 months the forest is compared with a naive seasonal baseline: each month is predicted as revenue twelve months earlier, y(t−12). The model and its hyperparameters are unchanged.

| Model | MSE (USD²) | RMSE (USD) |
| --- | --- | --- |
| Random Forest | 4,612,858,070.60 | 67,918.02 |
| Seasonal baseline y(t−12) | 3,190,168,976.25 | 56,481.58 |

The random forest loses to that baseline on MSE and on RMSE.

## Decomposition

`statsmodels.tsa.seasonal.seasonal_decompose` with `model="multiplicative"` and `period=12`. The briefing describes August and January–February as percentages of the average, on a series that grows, so an additive swing in dollars would mix trend into the seasonal amplitude. `extrapolate_trend="period"` only fills the ends of the diagnostic trend line. The decomposition is not the forecaster.

`output/metrics.md` states whether August is the low month and whether January and February sit above the within-year mean, using the numbers measured on this file. The percent bands in the briefing are checked, not assumed.

## Plots

`output/forecast_vs_actual.png` shows actual 2024–2025 revenue, the forest mean, and a band of ±1 standard deviation across trees. That band is the spread of the forest, not a calibrated 95% interval. August is shaded. January and February are labeled. The RMSE in dollars and as a percent of mean test revenue is printed on the figure from the same run.

`output/feature_importance.png` is the impurity importance. It favors continuous columns and is not a causal effect.

The typeface is Arial or Helvetica when installed, otherwise Liberation Sans. The run log records which face was used. There is no web UI in this project.

## Tests

```bash
uv run pytest
```

| File | What it locks |
| --- | --- |
| `tests/pipelines/test_split.py` | 8-year / 2-year cutoff, disjoint months and years, no shuffle, raw origin year |
| `tests/pipelines/test_features.py` | Lag equals the past raw value; rolling window excludes the current row; nulls and blanks are dropped; the forest is fit on those features |
| `tests/pipelines/test_metrics.py` | Gini of a perfect ranking is 1; PSI reacts to a shift; K² returns a finite statistic |
| `tests/pipelines/test_reproducibility.py` | Two fits with seed 42 match; scaler mean equals the training mean, not the combined mean |
| `tests/pipelines/test_seasonal_baseline.py` | On 2024–2025 the seasonal baseline is y(t−12), and its MSE/RMSE are computed from that vector |

## Layout

The monorepo documents ETL under `data/pipelines/`. This assignment asks for tests in `tests/pipelines/` and, in the Nexova briefing, a training script in `scripts/`. The importable code therefore lives in `pipelines/` so the tests can import it, and `scripts/train_sales_forecast.py` is the entry point. `data/pipelines/README.md` points here.
