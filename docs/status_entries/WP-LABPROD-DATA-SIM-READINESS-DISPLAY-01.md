# WP-LABPROD-DATA-SIM-READINESS-DISPLAY-01 Branch State

## Scope Summary

Adds a deterministic read-only lab readiness display under `tools/lab_readiness`.
The display classifies whether required idea-intake feature/data/simulator
surfaces are testable now, caveated, data-blocked, vendor/capture-blocked,
runner/compiler-blocked, simulator-blocked, protected, or unknown.

## Repo-Truth Basis

Inspected repo truth includes the committed data feature availability catalog,
availability validator, current indicator catalog, Strategy Spec schema,
offline runner, signal compiler, backtester, lab completion map, lab operating
model, lab design roadmap, and package-relevant status entries.

Current merged repo truth superseded an older computable-surface audit in one
important way: the current compiler and indicator catalog now include closed
builtin support for SMA, EMA, ATR, StdDev, RSI, Donchian, SMA-distance, RVOL,
rolling candle-VWAP, timestamp-derived fields, and session/opening-range
primitives. The readiness display records that current fact while preserving the
non-authority boundary of the offline research path.

## Implementation Summary

- Added closed readiness taxonomy and non-authority flags in
  `tools/lab_readiness/model.py`.
- Added deterministic repo-file-only projection builder and markdown renderer in
  `tools/lab_readiness/readiness.py`.
- Added CLI in `tools/lab_readiness/run.py`:
  - `--json`
  - `--markdown`
  - `--out-dir`
- Added focused tests in `tests/test_lab_readiness.py`.
- Added operator-facing documentation in
  `docs/research/LAB_DATA_SIM_READINESS_DISPLAY.md`.
- Added scratch discovery, contract, fixture, non-authority audit, and validation
  notes under `scratch/WP-LABPROD-DATA-SIM-READINESS-DISPLAY-01/`.

## Classification Highlights

- OHLCV builtin indicator families and Donchian/SMA-StdDev families are
  classified as testable now on the offline research path, not as candidate or
  promotion-ready.
- EMA/RVOL/rolling-VWAP/session surfaces are classified as testable with caveats;
  rolling VWAP is explicitly a candle approximation, not true trade-level VWAP.
- Funding-rate features are blocked on local full-history materialization for
  runner-consumable columns.
- Funding PnL/cost realism is blocked on runner support and local funding-event
  materialization despite backtest-core opt-in funding support.
- Taker-flow archive-derived support is blocked on local full-history
  materialization and deterministic reconstruction.
- Open interest, long/short ratios, liquidation history, and L2/order-book
  features are not marked full-history testable without vendor/captured history
  and any required future support.
- Simulator/paper-shadow boundary is GO-gated/protected.

## Boundary Summary

No data was acquired. No public/private API, provider, credential, vendor, or
network path was used. No runner/compiler/backtester/schema/validator/query-layer
behavior changed. No Strategy Specs, Variant Manifests, Sweep Plans, Result
Populations, candidate registry entries, trial-log entries, canonical evidence,
crossings, approvals, promotions, scheduler/autonomy, paper/live/runtime files,
OMS, risk, reconciliation, broker/exchange/order, configs, dependencies, or
protected paths were changed.

Read-only readiness display only; no data acquisition, runner/compiler behavior
change, execution, candidate, crossing, promotion, paper/live/runtime,
provider/API, credential, dependency, config, or protected-path authority.
