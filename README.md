# US core PCE forecasting

What current inflation-related indicators imply for future US core PCE inflation, how much
they agree with one another, and which past episodes today's configuration resembles.

**Live report:** https://jasonzhixinglu.github.io/us-core-pce-forecasting/

## What the report does

1. **Five blocks of indicators**, each summarized by its own principal components: inflation
   measures, the cross-category distribution of price changes, inflation expectations, demand
   and labor, and financial conditions.
2. **A dynamic factor model** on the full panel (two global factors plus one per block, joint
   VAR(1), AR(1) idiosyncratic components), estimated by EM with a Kalman smoother.
3. **Iterated forecasts** of core PCE: the model's projection of the 3-month rate at
   non-overlapping quarters, accumulated and combined with realized months to give the
   12-month rate 3, 6, 12 and 24 months ahead.
4. **News**: how each month's data releases revised the 12-month-ahead forecast, by block.
5. **Information sets**: the DFM against a global-factor-only DFM and a univariate AR, with
   recursive pseudo-out-of-sample RMSE.
6. **Agreement and analogs**: a one-factor model across the five block factors, the residual
   by block, and cosine similarity of today's residual pattern to every past month.

## Running it

```
python run.py                # regenerate report.md, report.html and figures/ (about 30 seconds)
python run.py --refresh      # re-download the FRED series first
python run.py --refit        # re-estimate the factor models by EM (a few minutes, in a separate process)
python run.py --recompute    # recompute the cached stages (news, out-of-sample evaluation, block PCAs)
```

Expensive results are cached under `cache/` and reused until their inputs change: the fitted
DFM parameters (`dfm_params_*.npz`, keyed by a fingerprint of the panel) and the slow stages
(`cache/stages/`). A fresh clone runs without refitting.

Requires Python 3.12+ (nested f-strings) with numpy, pandas, statsmodels, scipy, matplotlib, requests and pyarrow.

## Layout

| file | role |
|---|---|
| `run.py` | the pipeline: data, blocks, model, forecasts, report |
| `text.py` | the hand-written prose the report carries; edit here, not in `report.md` |
| `dfm_spec.py` | the factor model specification shared by `run.py` and `fit_dfm.py` |
| `fit_dfm.py` | EM estimation, run in its own process and cached |
| `report.md`, `report.html` | generated; `index.html` redirects the live page to `report.html` |
| `figures/` | generated |
| `cache/` | FRED series as CSV, the SPF and excess-bond-premium inputs, fitted parameters, stage caches |

`report.md` is regenerated on every run. Prose lives in `text.py`; sentences that quote
computed numbers are f-strings in `run.py`.

## Data

Latest-vintage FRED series (CSV endpoint, no key). Two inputs are not on FRED and are
flagged where used: the Survey of Professional Forecasters individual CPI forecasts
(Philadelphia Fed) and the Gilchrist-Zakrajsek excess bond premium (Federal Reserve).

Not a real-time evaluation: the pseudo-out-of-sample forecasts use revised data and
parameters estimated once on the full sample.
