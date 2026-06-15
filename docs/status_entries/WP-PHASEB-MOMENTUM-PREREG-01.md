# WP-PHASEB-MOMENTUM-PREREG-01 Branch State

- Package: `WP-PHASEB-MOMENTUM-PREREG-01`.
- Stage: finalized pre-registration after draft/probe/surface review.
- Branch: `prereg/phaseb-momentum-0004-draft`.
- Worktree: `C:\GitHub\crypto-perp-wedge-WP-PHASEB-MOMENTUM-PREREG-01`.
- Base: `origin/main` at PR #474 / `e9d0017`.
- Package class: Karl/Main-gated pre-registration artifact surface.
- Status: finalized PR scope; no canonical trial, result population, candidate
  approval, paper/live readiness, or runtime authority.

## Scope Summary

This package finalizes `STRAT-SPEC-0004`, `VM-0004`, and
`SWEEP-PLAN-0004` for PR review after Codex-chat finalize authorization on
2026-06-15.

The artifact set implements the selected Phase-B momentum shape:

- both-direction BTCUSDT 15m SMA crossover trend continuation;
- long entry: fast SMA crosses above slow SMA and close is above the trend SMA;
- short entry: fast SMA crosses below slow SMA and close is below the trend SMA;
- long exit: fast SMA crosses below slow SMA;
- short exit: fast SMA crosses above slow SMA;
- fixed entry throttle: `entry_logic.entry_controls.min_bars_between_entries = 16`;
- dynamic-equity 1x future measurement posture inherited from the RP-7520
  comparison surface.

Excluded primitives remain z-score, regime gate, ATR stop, fixed stop,
trailing stop, max holding period, centerline fade target, volatility filter,
slope primitive, breakout channel, and paper/live/runtime fields.

## Artifact Set

- `research/strategy_specs/STRAT-SPEC-0004.strategy_spec.json`
- `research/variant_manifests/VM-0004.variant_manifest.json`
- `research/sweep_plans/SWEEP-PLAN-0004.sweep_plan.json`
- `docs/research_pipeline/2026-06-phaseb_momentum_prereg_0004.md`
- `docs/status_entries/WP-PHASEB-MOMENTUM-PREREG-01.md`
- `docs/research_pipeline/README.md`

## Denominator / Grid

The manifest declares 8 variants:

- `fast_lookback_bars in {20, 50}`
- `slow_lookback_bars in {100, 200}`
- `trend_lookback_bars in {300, 400}`

Free-parameter count: `3`.

Committed denominator: `8`.

Every committed variant satisfies `fast_lookback_bars < slow_lookback_bars <
trend_lookback_bars`. Invalid and excluded cells: `0`.

## Finalization PR Scope

- Authorization: Codex-chat finalize authorization on 2026-06-15.
- Same-WP continuation authorization: narrow query-test expectation updates for
  the 0004 Strategy Spec / Variant Manifest / Sweep Plan corpus expansion.
- Commit/PR scope: pre-registration artifacts, final operational screen,
  status fragment, README navigation pointer, and current-corpus query-test
  expectations only.
- Exact denominator: `8`, plus retained non-success rows under future
  result-population rules.
- Fixed throttle: `entry_logic.entry_controls.min_bars_between_entries = 16`.
- Free-parameter count: `3`.
- Trial execution: not in scope.
- Canonical result population: not in scope.
- Candidate, paper/live, readiness, promotion, or runtime authority: not
  created.

## Boundary Summary

- Canonical result population written: NO.
- Existing result population changed: NO.
- Trial or canonical sweep run: NO.
- Candidate registry changed: NO.
- Compiler/schema/catalog/validator changed: NO.
- `lib/` or runner changed: NO.
- Query layer changed by this package: NO.
- Query-test current-corpus expectations changed by this package: YES,
  narrowly authorized for the 0004 preregistration corpus expansion.
- Runtime, paper/live, OMS/risk/reconciliation, broker/exchange, or protected
  path changed: NO.
- Candidate, readiness, promotion, ranking, recommendation, walk-forward, or
  runtime authority created: NO.

Future canonical trial execution remains separately unauthorized and requires a
later explicit package.

## Standing Validation Note

Any package that adds or changes query-visible research corpus artifacts must
run query-layer tests and full pytest. This applies to Strategy Specs, Variant
Manifests, Sweep Plans, and Result Populations; the rule is broader than a
result-population-only posture because this package showed that preregistration
artifact additions also change strict query-layer current-corpus expectations.
