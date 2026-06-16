# WP-PROBE-METHODOLOGY-CANONICAL-REGROUNDING-01

Status: branch-state docs-only methodology guardrail package.

## Scope

Package class: docs-only methodology / evidence-integrity guardrail.

Branch: `docs/probe-methodology-canonical-regrounding-01`

Worktree:
`C:\GitHub\crypto-perp-wedge-WP-PROBE-METHODOLOGY-CANONICAL-REGROUNDING-01`

Base: `origin/main` at `bee70a7` after PR #497 merge and refreshed-main preflight.

Authorization: user/Main-authorized follow-up after
`WP-DIAG-4H-PROBE-CANONICAL-RECONCILE-01`.

## Changed Files

- `docs/research_pipeline/2026-06-probe_methodology_canonical_regrounding.md`
- `docs/research_pipeline/README.md`
- `docs/status_entries/WP-PROBE-METHODOLOGY-CANONICAL-REGROUNDING-01.md`

## Source Docs Inspected

- `docs/project_status.md`
- `CLAUDE_START_HERE.md`
- `docs/runbook.md`
- `docs/research_pipeline/2026-05-stage2c_workflow_efficiency_operating_model_lock.md`
- `docs/ai/codex/CODEX_TOKEN_EFFICIENCY.md`
- `docs/research_pipeline/2026-06-momentum_4h_probe_canonical_reconcile.md`
- `docs/status_entries/WP-DIAG-4H-PROBE-CANONICAL-RECONCILE-01.md`
- `docs/research_pipeline/2026-06-momentum_4h_trial_0006_result.md`
- `docs/status_entries/WP-MOMENTUM-4H-TRIAL-01.md`
- `docs/research_pipeline/2026-06-momentum_4h_prereg_0006.md`
- `docs/research_pipeline/README.md`
- `docs/architecture/future_strategy_capability_matrix.md`

## Methodology Lock Summary

The lock records that future premise probes may gate canonical expectations
only when they are canonical-equivalent: exact Strategy Spec, exact grid /
Variant Manifest, exact Sweep Plan, canonical runner path, exact data lineage,
and equivalent sizing, cost, funding, slippage, timeframe, denominator, and
reproducibility assumptions.

Exploratory, scratch, direct/custom, altered-grid, altered-route, or
noncanonical probes must be labeled non-gating and cannot set canonical
expectations.

The 0006 divergence cause recorded from repo truth is that the premise probe
used the 0005 bar-count grid directly on 4h bars, while canonical `RP-6236`
used the frozen 0006 horizon-rescaled 4h grid. The diagnostic classified the
canonical runner as sound for that diagnostic, the trend gate as applied as
intended, probe methodology as needing canonical regrounding, and `RP-6236` as
valid canonical evidence for the exact frozen 0006 population.

## No Implementation Boundary

- `RP-6236` mutation, annotation, correction, replacement, or rerun: `NO`
- Result Population write: `NO`
- Runner/compiler/lib changes: `NO`
- Strategy Spec / Variant Manifest / Sweep Plan changes: `NO`
- Schema / validator / query-layer changes: `NO`
- Data / catalog changes: `NO`
- Candidate / walk-forward / paper/live / runtime / capital authority: `NO`
- Protected paths touched: `NO`

## Validation Summary

Completed from this worktree:

- `git status --short`: expected three-file docs-only package diff
- `git diff --check`: `PASS`
- `git diff --cached --check`: `PASS`
- `python -m tools.registry.validate_strategy_specs`: `PASS`
- `python -m tools.registry.validate_variant_sweep_artifacts`: `PASS`
- `python -m tools.registry.validate_indicator_catalogs`: `PASS`
- `python -m tools.registry.validate_result_populations`: `PASS`
- `python -m tools.registry.validate_candidate_registry`: `PASS`
- `python -m tools.registry.validate_paper_state`: `PASS`
- `python -m tools.research_query.run --list-views`: `PASS`
- `python tools/dev/diff_scope_summary.py --check-forbidden`: `PASS`
- `python tools/dev/verify.py --integrity-views --integrity-max-workers 4
  --timeout-seconds 300 --max-output-chars 6000 --json`: `PASS`
  (`v_integrity_*`: clean, 55)

Full sharded pytest: `NOT RUN` - docs-only methodology guardrail; no code,
schema, validator, query-layer, runner, or protected-path behavior changed.

## Next Package Options

- Online OHLCV primitive feasibility only after this package is merged and only
  if separately authorized.
- No 0006 rerun is indicated by the diagnostic.
