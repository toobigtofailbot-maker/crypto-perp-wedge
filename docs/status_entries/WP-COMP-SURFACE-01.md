# WP-COMP-SURFACE-01 - Surface compiler/indicator first-block options

- Package class: T1 docs/design/decision-surface
- Branch: `docs/comp-surface-01-first-block-options`
- PR: https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/428
- Scope summary: Creates a docs-only decision surface for Main 5's first post-STRAT-CAP compiler/indicator expressiveness block. It reconciles S2c-213 ordering against current repo truth, classifies per-extension compatibility, and surfaces candidate next implementation/design blocks without authorizing any one block.
- Repo-truth basis: GitHub confirmed PR #427 / `WP-STRAT-CAP-01` merged. Open PR check returned no open PRs. Direct `git fetch origin` failed twice during startup with a network connection error, so the local branch was started from the merged PR #427 head at `f13472da96943f50544aa319ab0903aa6b3c9020`. Inspected current schema, validator, catalog, compiler, and tests rather than relying on S2c-213 where stale.
- Changed files:
  - `docs/research_pipeline/2026-06-compiler_indicator_first_block_options.md`
  - `docs/status_entries/WP-COMP-SURFACE-01.md`
  - `docs/project_status.md`
- S2c-213 reconciliation summary: Lookback parameter binding is already implemented in schema, validator, compiler, and tests, so no implementation WP is needed for E1. `crosses_above` / `crosses_below` remain schema-valid but compiler-fail-closed. `scale_by_one_plus_parameter` remains closed out by schema/validator/compiler. `both`, `z_score`, indicators, session/time, multi-timeframe, ATR-stop, and data-dependent extensions require design, catalog/builtin work, runner/backtester design, or Karl-gated data scope as classified.
- Compatibility summary: `crosses_*` is the cleanest candidate implementation surface because schema/validator support already exists and compiler behavior fails closed. Plus composition is a small but broader schema/validator/compiler package. Indicator additions need formula/catalog/builtin closure. Session, MTF, ATR-stop, and OI/L2/trade-flow surfaces are design, protected-adjacent, deferred, or data/Karl-gated.
- Candidate next blocks:
  - `WP-COMP-XOVER-01` - compiler/test implementation for `crosses_above` / `crosses_below`.
  - `WP-COMP-PLUS-01` - closed schema/validator/compiler/test package for `scale_by_one_plus_parameter`.
  - `WP-IND-DONCHIAN-DESIGN-01` - small indicator-catalog design package before any new indicator implementation.
- Validation summary:
  - `git diff --check`: pass.
  - `git diff --cached --check`: pass.
  - `git diff --cached --name-only`: expected three files.
  - `python -m tools.registry.validate_result_populations`: pass.
  - `python -m tools.research_query.run --list-views`: pass.
  - all discovered `v_integrity_*` views: pass, 55 clean / zero rows, via single-process query-layer check after per-view CLI loop timed out.
  - `python tools/dev/diff_scope_summary.py`: pass; no forbidden-path matches.
  - full pytest: not run; not required for this T1 docs/design package and not used as merge evidence.
- Boundary summary: Docs/design only. No compiler, schema, validator, catalog, tool, test, Strategy Spec, variant, sweep, result population, backtest, dashboard implementation, generated output, data acquisition, simulator, runtime, paper/live, OMS/risk, broker/exchange, or protected-path behavior is changed. No ranking, recommendation, readiness, promotion, canonical-use, or execution authority is created.
- Merge status: PR #428 is open, non-draft, and GitHub reports `mergeable=MERGEABLE`.
- Main 5 decision request: Choose one of the surfaced options: authorize `crosses_*`, authorize plus composition, authorize indicator design first, or request a narrower WP after resolving a blocker.

## Active-WP Requirement Traceability

| Requirement | Evidence | Status |
|---|---|---|
| First-block options doc created | `docs/research_pipeline/2026-06-compiler_indicator_first_block_options.md` | satisfied |
| Status fragment created | `docs/status_entries/WP-COMP-SURFACE-01.md` | satisfied |
| Project-status pointer added | `docs/project_status.md` | satisfied |
| S2c-213 ordering summarized | First-block options doc, `Reconciled S2c-213 Ordering` | satisfied |
| STRAT-CAP compiler/indicator gap inventory reconciled | First-block options doc, compatibility matrix and candidate blocks | satisfied |
| Current schema support classified | Schema inspection plus compatibility matrix | satisfied |
| Current compiler support classified | Compiler inspection plus compatibility matrix | satisfied |
| Current catalog support classified | Catalog inspection plus compatibility matrix | satisfied |
| Data/Karl-gated surfaces classified | Compatibility matrix | satisfied |
| Candidate next blocks presented without authorization | First-block options doc, `Candidate First Implementation Blocks` | satisfied |
| No implementation changes | Diff scope contains docs only | satisfied |
| Required validation run | Validation summary in this status fragment | satisfied |
| PR body/status finality clean | Final PR readiness gate | satisfied |
| No forbidden paths touched | Diff scope validation | satisfied |
