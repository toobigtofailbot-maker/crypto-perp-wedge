# WP-PHASEB-PREREG-01 Branch State

- Package: `WP-PHASEB-PREREG-01`.
- Branch: `prereg/phaseb-0003-draft`.
- Worktree: `C:\GitHub\crypto-perp-wedge-WP-PHASEB-PREREG-01`.
- Base: `origin/main` at PR #468 / `17b1dee`.
- Package class: Karl-gated pre-registration draft and surface.
- Status: Karl-approved Option A finalization PR scope; no canonical trial,
  result population, or runtime authority.

## Scope Summary

This package finalizes the exact candidate content for `STRAT-SPEC-0003`,
`VM-0003`, and `SWEEP-PLAN-0003` for PR review after Karl approved Option A.

The draft implements Main's selected v1 shape:

- drop the regime gate;
- do not use `STDDEV(close, vol_lookback_bars) > 1.0`;
- do not freeze the surfaced volatility-expansion substitute;
- keep A1 z-score entries, A2 trend gate, fixed A3 entry throttle
  `min_bars_between_entries = 8`, centerline exits, both-direction BTCUSDT
  15m posture, and dynamic-equity 1x future measurement posture inherited
  from RP-7520.

## Drafted Artifacts

- `research/strategy_specs/STRAT-SPEC-0003.strategy_spec.json`
- `research/variant_manifests/VM-0003.variant_manifest.json`
- `research/sweep_plans/SWEEP-PLAN-0003.sweep_plan.json`
- `docs/research_pipeline/2026-06-phaseb_prereg_0003.md`
- `docs/status_entries/WP-PHASEB-PREREG-01.md`
- `docs/research_pipeline/README.md`

## Denominator / Grid

The draft manifest declares 8 variants:

- `center_lookback_bars in {50, 100}`
- `vol_lookback_bars in {30, 50}`
- `trend_lookback_bars in {100, 200}`

Free-parameter count: `3`.

Committed denominator if finalized unchanged: `8`, plus retained non-success
rows under future result-population rules.

Option A repo-truth follow-up: current
`entry_controls.min_bars_between_entries` is a Strategy Spec literal and the
current offline runner passes the same spec to every variant row. This draft
therefore fixes the throttle at `8` in `STRAT-SPEC-0003`, does not sweep it,
and does not count it as a VM free parameter. No implementation, schema,
compiler, runner, or materialization change is included or authorized.

## Finalization PR Scope

- Karl approval: Option A fixed throttle.
- Commit/PR scope: pre-registration artifacts, draft surface document, status
  fragment, and README navigation pointer only.
- Exact denominator: `8`, plus retained non-success rows under future
  result-population rules.
- Fixed throttle: `entry_logic.entry_controls.min_bars_between_entries = 8`.
- Free-parameter count: `3`.
- Trial execution: not in scope.
- Canonical result population: not in scope.
- Candidate, paper/live, readiness, promotion, or runtime authority: not
  created.

## Boundary Summary

- Commit created: pending this finalization follow-up.
- PR opened: pending this finalization follow-up.
- Freeze finalized: NO.
- Canonical result population written: NO.
- Trial or canonical sweep run: NO.
- Candidate registry changed: NO.
- Compiler/schema/catalog/validator changed: NO.
- `lib/` or runner changed: NO.
- Runtime, paper/live, OMS/risk/reconciliation, broker/exchange, or protected
  path changed: NO.
- Candidate, readiness, promotion, ranking, recommendation, or runtime
  authority created: NO.

Karl approval for Option A commit and PR has been received. Canonical trial,
canonical result-population write, candidate promotion, paper/live readiness,
and runtime authority remain out of scope.
