# US inflation signals

`python research/us_inflation_signals/run.py [--refresh]` downloads FRED data (cached in `cache/`), builds five predictor blocks, extracts global and block factors, forecasts core PCE, and writes `report.md` and `report.html` (figures in `figures/`), ending with direct answers to the fifteen questions. About two minutes per run; `--refresh` re-downloads.

Non-FRED inputs, flagged in the report: the SPF individual CPI forecasts (Philadelphia Fed) and the excess bond premium (Federal Reserve). Latest-vintage data throughout; not a real-time evaluation.
