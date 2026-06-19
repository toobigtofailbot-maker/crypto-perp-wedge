# EXT-ROBUSTNESS-MC-PILOT-01 - Seeded Robustness / Monte Carlo Pilot

## Branch / PR

- Branch: `ext/robustness-mc-pilot-01`
- PR: `https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/511`

## Package Class

External-adoption pilot / research-lab robustness capability /
non-canonical advisory diagnostics.

## Precondition

- `EXT-CCXT-DATA-INGESTION-PILOT-01` is merged on refreshed `main`.
- Verification evidence: `git log --oneline --grep="EXT-CCXT-DATA-INGESTION-PILOT-01" -n 5`
  returned merge commit `3ad2b35` for PR #510.
- Open PR searches for this package and the CCXT pilot returned no conflicting
  open PRs.

## Scope Summary

This package adds an isolated, standard-library-only robustness pilot for the
committed `RP-2592` Result Population fixture. The pilot reads Result
Population rows and the linked Variant Manifest read-only, bootstraps finite
per-variant row metrics with an explicit seeded RNG, groups advisory parameter
sensitivity summaries by real VM parameter values, and writes non-canonical
scratch reports only.

The pilot does not synthesize trades. Trade-order resampling is reported as
`PER_TRADE_DATA_MISSING` because committed Result Population rows expose
aggregate per-variant metrics only and no real per-trade rows were used.

## Changed Files

- `tools/external_pilots/robustness_mc_pilot.py`
- `tests/test_external_robustness_mc_pilot.py`
- `docs/status_entries/EXT-ROBUSTNESS-MC-PILOT-01.md`
- `scratch/EXT-ROBUSTNESS-MC-PILOT-01/robustness_report.json`
- `scratch/EXT-ROBUSTNESS-MC-PILOT-01/robustness_report.md`
- `scratch/EXT-ROBUSTNESS-MC-PILOT-01/bootstrap_samples.sha256`

## Fixture Used

- Result Population: `RP-2592`
- Path: `research/result_populations/RP-2592.result_population.json`
- Fixture checksum:
  `sha256:d548bfe884b8ad3ec749627da60f54fff9d54d58032eb779342fa56111c713b8`
- Strategy Spec: `STRAT-SPEC-0004`
- Variant Manifest: `VM-0004`
- Sweep Plan: `SWEEP-PLAN-0004`
- Rows used: `8`
- Data slice:
  `binance_usdtm_btcusdt_ohlcv_15m:sha256:3daace53d727599b4cf5cc9d27ac2a3d53997bbf5b8401470097934e776bd664`

RP-2592 was selected because repo truth confirms it is the current external
pilot comparator fixture from the vectorbt pilot and has a complete VM-0004
parameter mapping. The earlier analytics pilot used RP-7134 for its formula
adapter scope; this package uses RP-2592 per the package fixture-selection rule.

## Pilot Result

- Command:
  `.\.venv\Scripts\python.exe -m tools.external_pilots.robustness_mc_pilot`
- Output directory:
  `scratch/EXT-ROBUSTNESS-MC-PILOT-01/`
- Seed: `20260618`
- Bootstrap samples: `1000`
- Confidence level: `0.95`
- Metrics used:
  `drawdown`, `fees`, `funding`, `return_pct`, `sharpe`, `slippage`,
  `trade_count`, `win_rate`
- Metrics skipped: none.
- Bootstrap sample checksum:
  `sha256:fc762b525e4b65046a337ec626a9f38be61f4829b8f527362c2eff76a213de49`
- Output checksum:
  `sha256:5c08c31bdf5130c75be573923b3280a1e60e947a6bef2d13fdbdb21adfdfef30`

Bootstrap CI summary over RP-2592 row metrics:

| metric | observed mean | ci lower | ci upper |
|---|---:|---:|---:|
| drawdown | 0.6396255106984028 | 0.6039042267534553 | 0.671806351909639 |
| fees | 11407.455777723917 | 8472.263352262817 | 13851.81356496969 |
| funding | 0.0 | 0.0 | 0.0 |
| return_pct | 0.29981331782578785 | -0.035842344218068714 | 0.6201552575064193 |
| sharpe | 0.2771542548171937 | 0.1584772859891341 | 0.3728077602107834 |
| slippage | 2851.8639444309792 | 2172.8725960581924 | 3509.662961568191 |
| trade_count | 929.5 | 753.871875 | 1110.403125 |
| win_rate | 0.3149938303694375 | 0.293201763495469 | 0.3341329677729225 |

## Diagnostics

- Bootstrap CI: performed over finite numeric `variant_result_rows[].metrics`
  values only.
- Trade-order resampling: `PER_TRADE_DATA_MISSING`; not performed; no synthetic
  per-trade data created.
- Parameter sensitivity: performed from `VM-0004.variant_manifest.json` using
  real `variant_assignments[].parameter_values` for
  `fast_lookback_bars`, `slow_lookback_bars`, and `trend_lookback_bars`.
- Optional empyrical reference: unavailable in the repo environment;
  repo-native formula mode used; dependency files unchanged.
- Jesse concept inspection: not inspected; not needed for the repo-native pilot.

## Validation Summary

- `.\.venv\Scripts\python.exe -m pytest tests/test_external_robustness_mc_pilot.py -q`:
  `PASS`, 11 passed.
- `.\.venv\Scripts\python.exe -m pytest tests/test_external_analytics_pilot.py -q`:
  `PASS`, 7 passed.
- `.\.venv\Scripts\python.exe -m pytest tests/test_research_query.py -q`:
  `PASS`, 64 passed in 444.69 seconds.
- `.\.venv\Scripts\python.exe -m tools.external_pilots.robustness_mc_pilot`:
  `PASS`; wrote report JSON, report Markdown, and bootstrap sample checksum
  under `scratch/EXT-ROBUSTNESS-MC-PILOT-01/`.
- `.\.venv\Scripts\python.exe tools\dev\verify.py --integrity-views --full-pytest-sharded --pytest-shards 4 --pytest-shard-workers 4 --full-pytest-timeout-seconds 900`:
  `PASS`; diff checks, forbidden-scope check, result-population validator,
  query view listing, 4 pytest shards over 73 test files, and all discovered
  integrity views passed/clean.

## Boundary Summary

- Canonical Result Population write: `NO`.
- Canonical Strategy Spec / VM / Sweep Plan mutation: `NO`.
- OHLCV mutation: `NO`.
- Trial log / candidate registry mutation: `NO`.
- Runner / backtester behavior change: `NO`.
- Runtime / paper / live / OMS / risk / broker / exchange / credential paths touched: `NO`.
- Screen-gate authority created: `NO`.
- Promotion / readiness authority created: `NO`.
- Candidate-evidence authority created: `NO`.
- Fabricated per-trade data: `NO`.
- Dependency files changed: `NO`.

## Recommendation

`ADOPT_AS_ROBUSTNESS_LAYER`.

Rationale: seeded row-level bootstrap diagnostics are deterministic over
committed RP rows, parameter sensitivity maps safely through committed VM
assignments, non-canonical labeling is explicit, and protected/canonical
boundaries are preserved. The missing per-trade layer is a useful next
capability but does not block adoption of this variant-level robustness layer.

Next gated WP suggestion: narrow scratch-only per-trade distribution
instrumentation design for committed RP lineage, without runner/backtester
mutation unless separately authorized.
