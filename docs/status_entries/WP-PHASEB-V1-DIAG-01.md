# WP-PHASEB-V1-DIAG-01 - Phase-B v1 failure decomposition

- Package class: T2 read-only diagnostic plus docs.
- Branch: `docs/phaseb-v1-failure-diagnostic`.
- Worktree: `C:\GitHub\crypto-perp-wedge-WP-PHASEB-V1-DIAG-01`.
- Base: `origin/main` at PR #470 merge `6cd777e`.
- Scope summary: Adds a read-only diagnostic over `RP-7134` compared to
  `RP-7520` to classify the dominant Phase-B v1 failure mode without mutating
  frozen artifacts, result populations, compiler/schema/lib/runner, data,
  trial log, candidate lifecycle, runtime, paper/live, OMS/risk, or protected
  paths.
- Changed files:
  - `docs/research_pipeline/2026-06-phaseb_v1_failure_decomposition.md`
  - `docs/research_pipeline/README.md`
  - `docs/status_entries/WP-PHASEB-V1-DIAG-01.md`
  - `docs/project_status.md`
- Evidence inputs: `RP-7134`, `RP-7520`, `STRAT-SPEC-0003`, `VM-0003`,
  `SWEEP-PLAN-0003`, Phase-B prereg and trial screen docs, result-population
  schema/validator, and runner/backtest metric definitions inspected
  read-only.
- Analysis commands/snippets:
  - `git fetch origin`; `git log --oneline -10 origin/main`; required artifact
    presence checks with `git ls-tree`.
  - Structured JSON snippets over `research/result_populations/RP-7134.result_population.json`
    and `research/result_populations/RP-7520.result_population.json` to extract
    per-row metrics, total explicit cost, cost/equity, gross-return
    approximation, summary statistics, and cost/return correlations.
  - Targeted reads of `lib/backtest.py`, `lib/evaluation.py`,
    `tools/research_runner/run_offline_sweep.py`, and
    `research/schemas/result_population.schema.json` to confirm metric units
    and available committed fields.
- Optional scratch rerun used: NO. Committed rows do not include per-trade PnL
  distribution. The backtester exposes `trades_df`, but the committed D4A
  normalized CSV path referenced by the canonical artifact is not present in
  this dedicated worktree, and this package did not reconstruct or transform
  data.
- Classification: `fundamental gross-negative expectancy`, medium-high
  aggregate confidence. Tail/no-stop behavior is plausible but not proven as
  the dominant mechanism by committed fields.
- Key findings: RP-7134 reduced churn and explicit cost versus RP-7520, but
  all eight rows still have near-total net loss, near-total drawdown, negative
  Sharpe, and negative gross-return approximation. Costs are material but not
  sufficient to explain the failure.
- Boundary summary: no canonical result population written; no existing result
  population changed; no frozen Strategy Spec / Variant Manifest / Sweep Plan
  changed; no trial log changed; no compiler/schema/catalog/lib/runner changed;
  no data acquisition or transformation; no candidate, walk-forward,
  promotion, paper/live, runtime, OMS/risk/reconciliation, broker/exchange, or
  trading authority created.
- Next-decision surface: pivot away from BTC 15m centerline fading is favored
  unless a separately authorized v2 changes the gross expectancy surface.
  ATR-stop or other stop-loss primitive work would require a separate
  compiler/schema package if not currently expressible. A separate scratch
  per-trade diagnostic could quantify average-win/loss and tail concentration
  without creating canonical authority.

## Validation

- `git diff --check`: PASS.
- `git diff --cached --check`: PASS with no staged files at pre-stage check.
- `git status --short`: PASS; only the four expected docs/status files were
  modified or untracked.
- `python tools/dev/diff_scope_summary.py --check-forbidden`: PASS; no
  forbidden-path matches.
- `python -m tools.registry.validate_strategy_specs`: PASS.
- `python -m tools.registry.validate_variant_sweep_artifacts`: PASS.
- `python -m tools.registry.validate_indicator_catalogs`: PASS.
- `python -m tools.registry.validate_result_populations`: PASS.
- `python -m tools.research_query.run --list-views`: PASS; listed 118 views.
- `python tools/dev/verify.py --help`: PASS.

## PR status

PR URL is recorded in the package report-back after publication.
