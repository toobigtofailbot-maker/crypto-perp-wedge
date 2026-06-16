# WP-MOMENTUM-V2-PREREG-01 - Momentum v2 preregistration draft surface

- Package class: draft-and-surface preregistration package; Karl-gated
  finalize.
- Branch: `prereg/momentum-v2-0005-draft-surface`.
- Worktree: `C:\GitHub\crypto-perp-wedge-WP-MOMENTUM-V2-PREREG-01`.
- Base: refreshed `main` at `0d1248d`.
- Status: ready-for-review surface; merge/finalize remains `HOLD` pending
  Karl gate.

## Scope Summary

This package surfaces `STRAT-SPEC-0005`, `VM-0005`, and
`SWEEP-PLAN-0005` plus the proposed 0005 single-slice screen after A6
ATR-stop support merged.

The artifact set implements:

- both-direction BTCUSDT 15m SMA crossover trend continuation;
- exact 0004 fast/slow/trend entry grid and opposite-crossover exits;
- fixed entry throttle `min_bars_between_entries = 16`;
- fixed A6 ATR-stop with `atr_lookback=14`, `atr_multiplier=3.0`,
  `entry_reference_price=next_bar_open_pre_fee_slippage`,
  `evaluation_price=close`, and `evaluation_timing=bar_close`;
- no ATR parameter sweep and no intrabar/fill realism.

## Artifact Set

- `research/strategy_specs/STRAT-SPEC-0005.strategy_spec.json`
- `research/variant_manifests/VM-0005.variant_manifest.json`
- `research/sweep_plans/SWEEP-PLAN-0005.sweep_plan.json`
- `docs/research_pipeline/2026-06-momentum_v2_prereg_0005.md`
- `docs/status_entries/WP-MOMENTUM-V2-PREREG-01.md`
- `docs/research_pipeline/README.md`
- `tests/test_research_query.py`

## Denominator / Grid

The manifest declares 8 variants:

- `fast_lookback_bars in {20, 50}`
- `slow_lookback_bars in {100, 200}`
- `trend_lookback_bars in {300, 400}`

Free-parameter count: `3`.

Committed denominator: `8`.

Every committed variant satisfies `fast_lookback_bars < slow_lookback_bars <
trend_lookback_bars`. Invalid and excluded cells: `0`.

## Cost Classification

Committed `RP-2592` fields expose aggregate cost and performance fields but do
not expose gross PnL, average equity, equity curve, per-trade PnL, or turnover.

A local scratch diagnostic was used in memory only for `VAR-000006` and
`VAR-000004`, using the existing documented local D4A CSV path and no canonical
write. The full eight-row scratch diagnostic timed out after 300 seconds before
output and was not used as evidence.

Classification: `mixed`.

Screen consequence: 0005 must use a compounding-aware cost metric, preferably
cost-to-gross-PnL. If that or a repo-supported equivalent is unavailable in a
future canonical result population, the v2 screen must stop rather than freeze
an undecidable cost verdict.

## Boundary Summary

- Canonical result population written: NO.
- Existing result population changed: NO.
- `RP-2592` changed: NO.
- `STRAT-SPEC-0004`, `VM-0004`, `SWEEP-PLAN-0004` changed: NO.
- Trial or canonical sweep run: NO.
- Candidate registry changed: NO.
- Compiler/schema/catalog/validator changed: NO.
- `lib/` or runner changed: NO.
- Query layer changed by this package: NO.
- Query-test current-corpus expectations changed by this package: YES,
  narrowly for the 0005 preregistration corpus expansion.
- Runtime, paper/live, OMS/risk/reconciliation, broker/exchange, or protected
  path changed: NO.
- Candidate, readiness, promotion, ranking, recommendation, walk-forward, or
  runtime authority created: NO.

Future canonical trial execution remains separately unauthorized and requires a
later explicit package.
