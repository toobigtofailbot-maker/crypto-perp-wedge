# WP-PHASEB-HYPO-DESIGN-01 Branch State

- Package: WP-PHASEB-HYPO-DESIGN-01 - first Phase-B edge-seeking hypothesis design draft.
- Package class: T1 docs/design-only.
- Branch: `docs/phaseb-hypo-design-01-first-edge-hypothesis`.
- Dedicated worktree: `C:\GitHub\crypto-perp-wedge-WP-PHASEB-HYPO-DESIGN-01`.
- Base: `origin/main` at PR #461 merge `39337da`, after PR #459, PR #460, and PR #461 were present on `origin/main`.

## Isolation

- A1 root worktree at `C:\GitHub\crypto-perp-wedge` was inspected only and not edited.
- A2 worktree at `C:\GitHub\crypto-perp-wedge-WP-EXPRESS-A2` was not touched.
- C1 worktree at `C:\GitHub\crypto-perp-wedge-WP-ROBUST-C1` was not touched.
- C2 worktree at `C:\GitHub\crypto-perp-wedge-WP-ROBUST-C2-DESIGN` was not touched.
- No A3 worktree was observed in the scoped worktree list check.
- Worktree was clean before editing.
- `gh pr list --state open` returned no open PRs, so no same-file project-status overlap was found before editing.

## Scope Summary

Creates a docs-only design draft for the first Phase-B edge-seeking hypothesis:
BTCUSDT 15m volatility-normalized regime-gated mean reversion. The draft uses
the merged A1 `z_score` / volatility-normalized vocabulary as repo truth,
treats A2 trend/regime and A3 trade-frequency semantics as future/pending, and
uses RP-7520 as evidence-level motivation without treating it as proof of an
edge.

The design separates fact, inference, decision, open question, and future
authorization. It records economic rationale, intended closed-spec shape,
cost-drag-mitigation logic, future test-design questions, draft success/failure
questions, and required future authorization before execution.

## Changed Files

- `docs/research_pipeline/2026-06-phaseb_first_hypothesis_design.md`
- `docs/research_pipeline/README.md`
- `docs/status_entries/WP-PHASEB-HYPO-DESIGN-01.md`
- `docs/project_status.md`

## Boundary Summary

- Docs/status/index only.
- No implementation.
- No Strategy Spec, variant manifest, sweep plan, result population, trial log,
  candidate registry, schema, validator, query-layer, compiler, runner,
  backtester, data catalog, canonical data, dashboard implementation, runtime,
  paper/live, OMS/risk/reconciliation, broker/exchange, collateral, dependency,
  CI, or workflow change.
- No candidate lifecycle, ranking, readiness, promotion, approval, or trading
  authority.
- A2/A3 semantics are explicitly pending and are not treated as settled.

## Repo-Truth Discovery

- A1 merged vocabulary used: closed `z_score` composed operand with fixed
  operands and `zero_scale_policy: "null_output"`.
- C1 robustness posture used: descriptive read-only diagnostics, denominator
  honesty, and withheld PSR/DSR/MinTRL values when formula inputs are absent.
- C2 windowing posture used: chronology, OOS selection/evaluation boundaries,
  full-population retention, and denominator honesty are future requirements.
- RP-7520 lesson incorporated: dynamic 1x evidence did not reproduce the fixed
  sizing liquidation artifact but showed no edge for raw SMA-band mean
  reversion, motivating volatility normalization, regime context, and lower
  churn.
- Equivalent design found: no equivalent Phase-B first-hypothesis design found
  by scoped search.

## Validation Detail

Validation results are recorded in the final report-back for this package.

Full pytest was not required for this docs-only package because no non-doc,
schema, validator, compiler, runner, query, or test file changed.
