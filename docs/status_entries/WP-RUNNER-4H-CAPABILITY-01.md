# WP-RUNNER-4H-CAPABILITY-01 Status

## Scope

User-authorized runner/data-path plumbing package. It adds an official offline
runner route for the derived canonical BTCUSDT 4h slice while preserving the
existing `--canonical-15m` route.

Changed files:

- `tools/research_runner/run_offline_sweep.py`
- `tests/test_offline_research_runner.py`
- `docs/status_entries/WP-RUNNER-4H-CAPABILITY-01.md`

## Capability

The runner now accepts `--canonical-4h` with `--ohlcv-input`, defaulting to the
committed 4h catalog, validation report, and derivation report paths. The 4h
route validates local CSV presence, CSV SHA, validation status, derivation
metadata, exact 4h spacing, row count, range, gap/duplicate facts, and partial
window count. The official committed 4h slice identity enforces row count
`13758`.

The 4h route binds the 4h catalog ref and 4h data slice identity into the
existing result-population identity fields, and records CSV SHA, validation
report SHA/status, derivation report SHA, parent 15m data slice identity, parent
15m normalized SHA, parent validation report SHA, resampling method, and
resampling version in existing data coverage provenance notes. No schema or
validator changes were made.

Backtest execution interval now follows the canonical execution input timeframe:
`15m` for `--canonical-15m`, `4h` for `--canonical-4h`. Metrics continue to use
`lib.evaluation.sharpe(returns, freq)`, where repo truth already defines `15m =
35040` bars/year and `4h = 2190` bars/year.

Funding remains the current runner behavior: synthetic zero funding for
canonical OHLCV-only runner inputs.

## Evidence

15m regression:

- Target: `RP-3731` / `STRAT-SPEC-0005` / `VM-0005` / `SWEEP-PLAN-0005`
- Command: official `--canonical-15m` route with D4 catalog provenance,
  dynamic equity target leverage `1.0`, and `--max-workers 4`
- Result: scratch `RP-3731.result_population.json` matched the committed
  `research/result_populations/RP-3731.result_population.json` byte-for-byte
- SHA256: `e8d6bc5c48a80c32f9495a0d63d05be0cf8513b8f3912d6b81c6dbca715672c2`
- Scientific identity, result identity, outcome counts, denominator, data
  coverage, assumptions, sizing metadata, and per-variant metrics all matched

4h smoke/reconciliation:

- Target: `STRAT-SPEC-0006` / `VM-0006` / `SWEEP-PLAN-0006`
- Command: official `--canonical-4h` route over
  `data/processed/d4h/binance_um_perp_BTCUSDT_4h_2020-01-01_2026-04-11_d4h_resampled.csv`
  with dynamic equity target leverage `1.0`
- 4h data identity:
  `binance_usdtm_btcusdt_ohlcv_4h:sha256:4379d2f0fad5e79bfd5576b308d01fb6134b0f5acf04013e73e00ce33ca96b30`
- Denominator: `8`
- Outcome counts: `8 successful`, all other outcome categories `0`
- Official route wrote no result population
- Same-input direct route comparison matched all per-variant metrics exactly

The older scratch 4h premise probe used a different comparison basis than the
exact 0006 official-route smoke. The same-input direct-route reconciliation is
the metric-equivalence proof for this package.

## Boundary

- Canonical result population written: `NO`
- Canonical 4h trial run: `NO`
- Existing result populations mutated: `NO`
- Strategy Specs, variant manifests, and sweep plans mutated: `NO`
- 4h data/catalog/validation/derivation metadata mutated: `NO`
- 15m data/catalog/import/validation metadata mutated: `NO`
- `lib/backtest.py` semantics changed: `NO`
- Signal compiler semantics changed: `NO`
- Schema/validator/query-layer behavior changed: `NO`
- Runtime, paper/live, OMS, risk, broker/exchange, credential, capital, or
  safe-mode paths touched: `NO`
- Candidate, walk-forward, paper/live, runtime, or capital authority added:
  `NO`

## Validation

Validation was run from
`C:\GitHub\crypto-perp-wedge-WP-RUNNER-4H-CAPABILITY-01`.

Initial `tests/test_research_query.py -q` with a 300s local timeout timed out
without failure output. The same command passed with a longer timeout.

Completed:

- `git diff --check`: `PASS`
- `git diff --cached --check`: `PASS`
- `python -m pytest tests/test_offline_research_runner.py -q`: `PASS`
- `python -m pytest tests/test_research_query.py -q`: `PASS`
- `python -m tools.registry.validate_strategy_specs`: `PASS`
- `python -m tools.registry.validate_variant_sweep_artifacts`: `PASS`
- `python -m tools.registry.validate_indicator_catalogs`: `PASS`
- `python -m tools.registry.validate_result_populations`: `PASS`
- `python -m tools.registry.validate_candidate_registry`: `PASS`
- `python -m tools.registry.validate_paper_state`: `PASS`
- `python -m tools.research_query.run --list-views`: `PASS`
- `python tools/dev/diff_scope_summary.py --check-forbidden`: `PASS`
- `python tools/dev/verify.py --integrity-views --integrity-max-workers 4
  --timeout-seconds 300 --max-output-chars 6000 --json`: `PASS`
- `python tools/dev/verify.py --full-pytest-sharded --pytest-shards 4
  --pytest-shard-workers 4 --timeout-seconds 300
  --full-pytest-timeout-seconds 1800 --max-output-chars 6000 --json`: `PASS`
