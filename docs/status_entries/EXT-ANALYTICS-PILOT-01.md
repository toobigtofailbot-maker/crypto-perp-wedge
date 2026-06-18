# EXT-ANALYTICS-PILOT-01 - External Analytics Metrics Pilot

## Branch / PR

- Branch: `ext/analytics-pilot-01`
- PR: `https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/509`

## Package Class

External-repo adoption pilot / non-canonical analytics comparator / additive reporting.

## Scope Summary

This package adds an isolated analytics metrics pilot for the committed
`RP-7134` Result Population fixture. The pilot reads Result Population rows
read-only, builds a deterministic row-level return fixture from successful
`return_pct` values sorted by `variant_id`, compares formula-overlap metrics
against optional `empyrical` output when available, and writes non-canonical
scratch reports only.

Annualized Sharpe, Sortino, and Calmar are reported as unsupported for this
fixture because committed Result Population rows are per-variant outputs rather
than a chronological strategy return series. The package does not invent an
annualization assumption.

## Changed Files

- `tools/external_pilots/analytics_metrics_pilot.py`
- `tests/test_external_analytics_pilot.py`
- `docs/status_entries/EXT-ANALYTICS-PILOT-01.md`
- `scratch/EXT-ANALYTICS-PILOT-01/analytics_report.json`
- `scratch/EXT-ANALYTICS-PILOT-01/analytics_report.md`
- `scratch/EXT-ANALYTICS-PILOT-01/metric_comparison.csv`

## Dependency / Adoption Mode

No repo dependency file is changed. Current repo truth has a single broad
`requirements.txt` / `requirements.lock.txt` dependency surface and no
non-runtime external-pilot dependency group. The active repo venv does not have
`empyrical`, `QuantStats`, or `pyfolio` installed, so the committed scratch
report uses formula-adapter-only mode.

The adapter supports optional `empyrical` import if an operator runs it in an
isolated analytics environment, but this package does not promote that
dependency into the repo environment.

Recommendation: `FORMULA_ADAPT_ONLY`.

## Fixture Used

- Result Population: `RP-7134`
- Strategy Spec: `STRAT-SPEC-0003`
- Variant Manifest: `VM-0003`
- Sweep Plan: `SWEEP-PLAN-0003`
- Data slice:
  `binance_usdtm_btcusdt_ohlcv_15m:sha256:3daace53d727599b4cf5cc9d27ac2a3d53997bbf5b8401470097934e776bd664`
- Fields used:
  `variant_result_rows[].variant_id`,
  `variant_result_rows[].metrics.return_pct`,
  `variant_result_rows[].metrics.drawdown`,
  `variant_result_rows[].metrics.sharpe`,
  `variant_result_rows[].metrics.trade_count`,
  `variant_result_rows[].metrics.win_rate`,
  `variant_result_rows[].metrics.fees`,
  `variant_result_rows[].metrics.funding`,
  `variant_result_rows[].metrics.slippage`

## Pilot Result

- Command:
  `.\.venv\Scripts\python.exe -m tools.external_pilots.analytics_metrics_pilot --formula-only`
- Output directory:
  `scratch/EXT-ANALYTICS-PILOT-01/`
- Dependency mode:
  `formula_adapter_only_no_repo_dependency_change`
- External engine:
  `empyrical`, unavailable in current repo venv
- Matched metrics:
  none in committed scratch output because the external dependency is not
  installed in the repo environment
- Formula-overlap metrics emitted:
  `cumulative_return`, `max_drawdown`, `tail_ratio`, and underwater-period
  diagnostics over the deterministic RP row fixture
- Unsupported metrics:
  `annualized_sharpe`, `sortino`, `calmar`

## Validation Summary

- `.\.venv\Scripts\python.exe -m tools.external_pilots.analytics_metrics_pilot --formula-only`:
  `PASS`; wrote `analytics_report.json`, `analytics_report.md`, and
  `metric_comparison.csv` under `scratch/EXT-ANALYTICS-PILOT-01/`.
- `.\.venv\Scripts\python.exe -m pytest tests/test_external_analytics_pilot.py -q`:
  `PASS`, 7 passed.
- `.\.venv\Scripts\python.exe -m pytest tests/test_offline_research_runner.py -q`:
  `PASS`, 94 passed, 2 existing timestamp parsing warnings.
- `.\.venv\Scripts\python.exe -m pytest tests/test_research_query.py -q`:
  first attempt timed out at 5 minutes with no failure output; rerun with a
  longer timeout `PASS`, 64 passed in 465.67 seconds.
- `.\.venv\Scripts\python.exe tools\dev\verify.py --integrity-views --full-pytest-sharded --pytest-shards 4 --pytest-shard-workers 4 --full-pytest-timeout-seconds 900`:
  `PASS`; diff checks, forbidden-scope check, result-population validator,
  query view listing, 4 pytest shards over 71 test files, and all discovered
  integrity views passed/clean.

## Boundary Summary

- Canonical Result Population write: `NO`.
- Canonical Strategy Spec / VM / Sweep Plan mutation: `NO`.
- `lib/backtest.py` canonical behavior change: `NO`.
- Offline runner behavior change: `NO`.
- Query-layer behavior change: `NO`.
- Runtime / paper / live / OMS / risk / broker / exchange / credential paths touched: `NO`.
- Analytics output authority: non-canonical scratch comparator only.

## Merge Status

Ready PR #509 opened. GitHub connector reported `mergeable=false` immediately
after creation; this may be transient, but this fragment does not call the PR
merge-ready while GitHub reports that state.

## Next Dependency / Runway Note

Future option: add a dedicated non-runtime external-pilot dependency group
before adopting `empyrical` or `QuantStats` as committed repo dependencies.
