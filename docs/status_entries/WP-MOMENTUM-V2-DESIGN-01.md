# WP-MOMENTUM-V2-DESIGN-01 - Momentum v2 design after RP-2592

- Package class: docs-only / read-only research design.
- Branch: `design/momentum-v2-design-01`.
- Worktree: `C:\GitHub\crypto-perp-wedge-WP-MOMENTUM-V2-DESIGN-01`.
- Base: `origin/main` at `c3c9e63`.
- Scope summary: Adds a read-only design note after the valid `RP-2592`
  momentum `NO-GO`, comparing it against fade-family evidence and identifying
  the minimal dependency ladder before any future momentum v2 preregistration.
- Changed files:
  - `docs/research_pipeline/2026-06-momentum_v2_design.md`
  - `docs/status_entries/WP-MOMENTUM-V2-DESIGN-01.md`
- Evidence inputs: `RP-2592`, `RP-7134`, `RP-7520`, `STRAT-SPEC-0004`,
  `VM-0004`, `SWEEP-PLAN-0004`, Phase-B momentum preregistration and screen
  docs, Phase-B v1 failure decomposition, Phase-B pivot design, realism
  runway conclusion, and expressiveness / compiler-surface docs inspected
  read-only.
- Analysis snippets: local JSON calculations over committed result-population
  rows and `VM-0004` assignments to compute total cost, cost-to-initial-equity,
  per-trade cost, gross-return approximation, population summaries, axis
  medians, and correlations. No scratch canonical artifact or result
  population was written.
- Cost finding: `cost_to_initial_equity` likely includes a
  compounding-denominator artifact for winning dynamic-sizing rows, but
  explicit costs remain large and committed fields lack gross profit, absolute
  gross PnL, average equity, turnover, notional, equity curve, and per-trade
  data.
- Drawdown finding: drawdown is the primary viability constraint; every
  `RP-2592` row exceeds `0.50` drawdown, and positive-return rows still have
  median drawdown `0.628921`.
- Design conclusion: momentum v2 is justified as a future research-design
  direction, not as an immediate freeze. A future v2 should preserve the
  with-move SMA crossover premise only if it adds separately authorized
  stop-managed or volatility-scaled risk control and a prospective
  compounding-aware cost screen.
- ATR-stop dependency: evidence justifies ATR-stop / volatility-stop as a
  future dependency to design and prove, but not as implemented or sufficient
  in this package. Current repo truth treats ATR-stop consumption as deferred
  runner/backtester or compiler/schema work with bounded offline semantics.
- Boundary summary: no Strategy Spec, Variant Manifest, Sweep Plan, Result
  Population, prior artifact mutation, compiler/schema/catalog/query/runner/
  `lib` change, data acquisition, candidate, walk-forward, promotion,
  paper/live/runtime, OMS/risk/reconciliation, broker/exchange, safe-mode, or
  trading authority created.
- Next decision: Main/Karl should decide whether to authorize an ATR-stop /
  volatility-stop design runway, authorize a scratch per-trade diagnostic, or
  reject momentum v2 and choose a different archetype/data/timeframe route.

## Validation

- `git status --short`: PASS; only the two expected untracked docs/status
  files were present before staging.
- `git diff --check`: PASS.
- `git diff --cached --check`: PASS with no staged files at pre-stage check.
- `python -m tools.registry.validate_strategy_specs`: PASS.
- `python -m tools.registry.validate_variant_sweep_artifacts`: PASS.
- `python -m tools.registry.validate_result_populations`: PASS.
- `python -m tools.research_query.run --list-views`: PASS; listed query
  views.
- `v_integrity_*` single-process query check: PASS; 55 integrity views clean.
- `python tools/dev/diff_scope_summary.py --check-forbidden`: PASS; no
  forbidden-path matches.
- `python -m pytest --collect-only -q`: PASS; 1457 tests collected.
- `python -m pytest -q`: TIMED OUT after 20 minutes with no useful buffered
  failure output before timeout. No code, schema, validator, runtime, or
  artifact files changed.
