# WP-ONLINE-OHLCV-PARAM-LOCK-01 - Online OHLCV hypothesis parameter lock

- Package class: docs-only research-intake / hypothesis and parameter lock.
- Branch: `docs/online-ohlcv-param-lock-01`.
- Worktree: `C:\GitHub\crypto-perp-wedge-WP-ONLINE-OHLCV-PARAM-LOCK-01`.
- Base: `origin/main` at merge `8eab20c`.
- Scope summary: Adds a non-authoritative parameter-lock surface for three
  online-derived BTCUSDT OHLCV strategy hypotheses.
- Changed files:
  - `docs/research_pipeline/2026-06-online_ohlcv_hypothesis_param_lock.md`
  - `docs/research_pipeline/README.md`
  - `docs/status_entries/WP-ONLINE-OHLCV-PARAM-LOCK-01.md`
- Preserved hypotheses:
  - ORB break-and-retest.
  - No-wick trend pullback.
  - Deterministic ORB-derived bias variant.
- Parameter envelopes:
  - ORB break-and-retest: 30m UTC daily opening range, close-confirmed
    breakout by 0.1 ATR, retest windows `{2, 4}`, retest tolerance 0.1 ATR,
    stop at opposite range side, targets `{1R, 2R}`, session-end exit, one
    trade per session, no-trade days preserved, expected first-test variants
    `~4`.
  - No-wick trend pullback: 1h bars, close vs EMA50 trend filter, wick
    tolerance `<= 10%` of range, body `>= 60%` of range, midpoint pullback,
    next-open entry after confirmation, stops `{signal-candle extreme,
    1.5 ATR}`, targets `{1.5R, 2R}`, time exit allowed, one active position
    per symbol/timeframe, expected first-test variants `~4`.
  - Deterministic ORB-derived bias variant: 30m opening range, 4h close vs
    SMA50 trend bias, close-confirmed breakout beyond OR high/low by 0.1 ATR,
    no retest, stop at opposite OR side, targets `{1R, 2R}`, session-end exit,
    no martingale, one trade per session, expected first-test variants `~2`.
- Explicit no-implementation boundary: no Strategy Spec, Variant Manifest,
  Sweep Plan, Result Population, compiler primitive, indicator, runner logic,
  data package, canonical/scratch trial, candidate, walk-forward/OOS,
  paper/live/runtime/capital authority, OMS/risk/reconciliation, broker/
  exchange, or protected-path change is created.
- Next package needed: `ONLINE-OHLCV-PRIMITIVE-FEASIBILITY-01` or equivalent,
  only after the diagnostic route allows it.

## Validation

- `git diff --check`: PASS.
- `git diff --cached --check`: PASS before staging.
- `git status --short`: PASS; only expected docs/status files changed.
- `python -m tools.registry.validate_strategy_specs`: PASS.
- `python -m tools.registry.validate_variant_sweep_artifacts`: PASS.
- `python -m tools.registry.validate_indicator_catalogs`: PASS.
- `python -m tools.registry.validate_result_populations`: PASS.
- `python -m tools.registry.validate_candidate_registry`: PASS.
- `python -m tools.registry.validate_paper_state`: PASS.
- `python -m tools.research_query.run --list-views`: PASS; 118 views listed,
  including 55 integrity views.
- `python tools/dev/diff_scope_summary.py --check-forbidden`: PASS; no
  forbidden-path matches.
- `python tools/dev/verify.py --integrity-views --integrity-max-workers 4
  --timeout-seconds 300 --max-output-chars 6000 --json`: PASS; integrity
  views clean.
- Full sharded pytest: NOT RUN - docs-only hypothesis/parameter lock; no
  code/schema/validator/query/runner changes.
