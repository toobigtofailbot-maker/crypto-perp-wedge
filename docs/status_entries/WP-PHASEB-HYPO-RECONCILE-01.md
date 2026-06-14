# WP-PHASEB-HYPO-RECONCILE-01 Branch State

- Package: `WP-PHASEB-HYPO-RECONCILE-01`.
- Branch: `docs/phaseb-hypo-reconcile-01`.
- Worktree: `C:\GitHub\crypto-perp-wedge-WP-PHASEB-HYPO-RECONCILE-01`.
- Base: `origin/main` after PR #465 / `WP-EXPRESS-A3` and PR #464 /
  `WP-ROBUST-C3` were present.
- Package class: T2 docs plus read-only compile probe.

## Scope Summary

This package reconciles the first Phase-B hypothesis design draft to the merged
A1 / A2 / A3 grammar and current C3 trial-accounting surface. It creates
`docs/research_pipeline/2026-06-phaseb_hypothesis_reconciliation.md`, adds a
research-pipeline index pointer, records this status fragment, and adds a
compact branch-state pointer to `docs/project_status.md`.

The reconciled non-frozen shape is a both-direction BTCUSDT 15m
volatility-normalized mean-reversion design that uses A1 `z_score`, shared A2
`trend` / `regime` entry gates through `filters.groups`, and A3
`entry_logic.entry_controls.min_bars_between_entries`.

## Probe Summary

The read-only compile probe used an in-memory Strategy Spec-like payload
derived from `STRAT-SPEC-0002` shape conventions and synthetic OHLCV data. It
wrote no Strategy Spec, variant manifest, sweep plan, result population,
scratch artifact, or test.

Result:

- schema validation: PASS.
- compiler construction: PASS.
- signal output: `signal`, length `260`, index range
  `2026-01-01T00:00:00+00:00` through `2026-01-03T16:45:00+00:00`, unique
  values `[-1.0, 0.0]`, nonzero count `18`.
- temp/probe artifacts committed: NO.

Repo-truth nuance surfaced by the probe: under `direction: "both"`, root
`entry_logic.groups` must be side-labeled; shared `trend` and `regime` gates
compile through `filters.groups`.

## C3 Trial-Accounting Summary

Read-only C3 diagnostic over `RP-7520` reports:

- result-population denominator: `10`;
- current trial-log denominator: `32`;
- numeric PSR / DSR / MinTRL: withheld because required formula inputs remain
  absent;
- DSR-relevant future posture: future Phase-B result populations use their
  committed pre-registered population denominator, and trial-log DSR posture
  also considers the full valid trial-log row count available at evaluation
  time.

## Boundary Summary

- No Strategy Spec, variant manifest, sweep plan, result population, canonical
  artifact, or trial log was created or changed.
- No compiler, schema, validator, catalog, runner, backtester, `lib/`, `src/`,
  test, data catalog, raw/processed data, candidate lifecycle, ranking,
  readiness, promotion, paper/live/runtime, OMS/risk/reconciliation,
  broker/exchange, collateral, dependency, or CI behavior changed.
- No freeze, pre-registration, canonical-write, candidate, or runtime authority
  was created.
