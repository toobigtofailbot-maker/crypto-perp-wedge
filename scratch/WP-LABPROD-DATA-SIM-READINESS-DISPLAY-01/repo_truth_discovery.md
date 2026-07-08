# Repo Truth Discovery

Package: `WP-LABPROD-DATA-SIM-READINESS-DISPLAY-01`

## Preflight

- Root checkout refreshed on `main`.
- Package worktree created at
  `C:\GitHub\crypto-perp-wedge-worktrees\labprod-data-sim-readiness-display-01`.
- Open PR list was empty before work.
- No open PR collision was found for the package readiness paths.

## Files Inspected

- `docs/project_status.md`
- `CLAUDE_START_HERE.md`
- `docs/runbook.md`
- package brief attachment
- `research/data_feature_availability/PERP-DERIVED-FEATURE-AVAILABILITY-0001.json`
- `tools/registry/validate_data_feature_availability.py`
- `docs/status_entries/WP-DATA-AVAILABILITY-LABELS-01.md`
- `docs/status_entries/WP-RUNNER-DATA-PATH-NONOHLCV-01.md`
- `docs/status_entries/WP-RESEARCH-FUNDING-RISKMANAGED-TRIAGE-UNBLOCK-01.md`
- `docs/research/LAB_COMPLETION_MAP.md`
- `docs/research_pipeline/2026-06-strategy_research_lab_target_operating_model.md`
- `docs/research_pipeline/2026-06-strategy_research_lab_design_consolidation_roadmap.md`
- `docs/research_pipeline/2026-06-strategy_spec_computable_surface_audit.md`
- `research/indicator_catalogs/IND-CATALOG-0001.indicator_catalog.json`
- `research/schemas/indicator_catalog.schema.json`
- `research/schemas/strategy_spec.schema.json`
- `tools/research_runner/spec_signal_compiler.py`
- `tools/research_runner/run_offline_sweep.py`
- `lib/backtest.py`
- existing lab tool/test examples under `tools/lab_*` and `tests/test_lab_*.py`

## Facts

- The data feature availability catalog has closed coverage classes:
  `FULL_HISTORY_PUBLIC_ARCHIVE`, `RECENT_ONLY_PUBLIC_REST`,
  `STREAMING_ONLY_PUBLIC_WS`, `VENDOR_ONLY_FOR_HISTORY`,
  `PUBLIC_SNAPSHOT_ONLY`, and `UNKNOWN_OR_BLOCKED`.
- Funding, mark, index, premium, timestamp-derived fields, and taker-flow
  archive derivations have conditional public full-history labels.
- Open interest is public snapshot/recent-only; long/short ratios are recent-only
  public REST; liquidation volume is vendor-only for history and not
  compiler-visible.
- Current compiler truth includes closed builtin indicators and primitives beyond
  the older computable-surface audit: SMA, EMA, ATR, StdDev, RSI, Donchian,
  SMA-distance, RVOL, rolling candle-VWAP, timestamp-derived fields, z-score /
  rolling percentile composed operands, and session/opening-range primitives.
- Current backtest truth supports explicit fee/slippage assumptions, default-off
  opt-in funding cashflows, fixed/dynamic sizing, deterministic liquidity cap,
  zero-equity and maintenance-margin liquidation assumptions, and close-only
  mark source.
- Current runner truth includes declared non-OHLCV column preservation and
  build-test/offline canonical paths, but funding-feature CSV materialization and
  real funding-event runner wiring remain separate prerequisites.
- Lab completion map keeps paper/live/runtime, OMS/risk/reconciliation,
  broker/exchange/order, autonomy, and first real crossing protected and
  GO-gated.

## Decisions

- Implement a package-local closed readiness taxonomy, not a schema or query
  layer change.
- Mark OHLCV closed builtin families as testable now only on the offline research
  path and with explicit non-authority flags.
- Mark funding feature history and taker-flow archive support as local
  materialization blockers rather than strategy failures.
- Mark funding PnL/cost realism as runner/materialization blocked despite
  backtest-core opt-in support.
- Mark unavailable historical OI/liquidation/L2/ratio surfaces as
  vendor/captured-history blockers rather than accepted full-history features.

## Open Questions

- Whether a later package should materialize runner-consumable full-history
  funding, taker-flow, mark/index/premium, or other declared non-OHLCV columns.
- Whether a later simulator-realism package should support external mark/index
  marking/liquidation semantics.
- Whether a later vendor/capture package should be authorized for OI,
  long/short ratio, liquidation, or L2 history.

## Future Options

- Add a schema/validator for readiness rows only if a future package authorizes a
  canonical readiness artifact.
- Add query-layer views only if future orchestrator/cockpit packages need
  committed read-model integration.
- Feed this display into future idea-intake UI surfaces without adding execution
  authority.
