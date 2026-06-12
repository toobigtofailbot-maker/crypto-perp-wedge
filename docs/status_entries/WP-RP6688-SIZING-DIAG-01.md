# WP-RP6688-SIZING-DIAG-01 - RP-6688 sizing/leverage diagnostic

- Package class: T1 docs-only diagnostic / read-only audit.
- Branch: `docs/rp6688-sizing-diagnostic`.
- PR: https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/441
- Scope summary: Diagnoses `RP-6688` read-only to classify the uniform
  `-100%` terminal return pattern against sizing, leverage, and cost-model
  mechanics.
- Authorization basis: Main 5 accepted `WP-SPEC-BOTHDIR-01d` and authorized a
  read-only diagnostic before robustness, expressiveness, or lifecycle
  follow-on; no Karl gate.
- Source artifacts:
  - `research/result_populations/RP-6688.result_population.json`
  - `research/strategy_specs/STRAT-SPEC-0002.strategy_spec.json`
  - `research/variant_manifests/VM-0002.variant_manifest.json`
  - `research/sweep_plans/SWEEP-PLAN-0002.sweep_plan.json`
  - `docs/research_pipeline/2026-06-rp6688_both_direction_sma_band_checkpoint.md`
  - `lib/backtest.py` and `lib/evaluation.py`, inspected read-only
- Created docs:
  - `docs/research_pipeline/2026-06-rp6688_sizing_leverage_diagnostic.md`
  - `docs/status_entries/WP-RP6688-SIZING-DIAG-01.md`
- Modified docs:
  - `docs/project_status.md`
  - `docs/research_pipeline/README.md`
- Classification: Primary classification is `(b) sizing / leverage artifact`.
- Key evidence:
  - Canonical runner calls `run_backtest()` with `initial_equity=10000`,
    `order_size=1.0`, taker/taker 4 bps fees, 1 bps slippage, zero funding
    input, and `liquidation_mode=zero_equity`.
  - `lib/backtest.py` computes PnL as price change times fixed `order_size`
    and costs as bps of `price * size`.
  - `RP-6688` rows all record `return_pct=-1.0`, `pnl=-10000.0`, and
    `drawdown=1.0`, while win rates range from about 61% to 76% and six
    Sharpe values are positive.
  - Inferred average costed-fill notional is about `7890.72` to `31842.66`,
    implying about `0.79x` to `3.18x` average costed-fill leverage versus
    starting equity; direct cost totals range from about 48.72% to 466.65% of
    starting equity.
- Integrity status: No integrity stop condition identified. Result population
  denominator, row count, outcome counts, provenance string, and identity
  hashes match the package prior-state requirements.
- Validation summary:
  - `python -m tools.registry.validate_result_populations`: pass.
  - `python -m tools.research_query.run --list-views`: pass.
  - All discovered `v_integrity_*` views: pass, 55 clean / zero rows.
  - Initial per-view CLI loop timed out before completion; final integrity
    evidence used the same query-layer view registry in one Python process and
    confirmed zero rows for all 55 integrity views.
  - `git diff --check`: pass.
  - `python tools/dev/diff_scope_summary.py`: pass; expected docs-only scope
    and no forbidden-path matches.
  - Read-only proof: no diff/status for `RP-6688`, `lib/backtest.py`, or
    `lib/evaluation.py`.
  - Full pytest: not run; not required for this T1 docs-only package.
- Authority/finality audit: Completed over changed files and PR body. Search
  hits are diagnostic classification, future-not-authorized package options,
  non-authority caveats, forbidden-scope statements, validation evidence,
  limitations, quoted audit terms, or source artifact/status identifiers. No
  wording describes a variant favorably as a selection, recommendation,
  readiness, promotion, or edge.
- Boundary summary: Docs-only diagnostic. No result-population mutation, no
  backtest rerun, no Strategy Spec / VM / sweep plan mutation, no lib/code
  change, no schema/validator/compiler/runner/query-layer behavior change, no
  data mutation, no candidate registry change, no dashboard implementation
  change, and no runtime/paper/live/protected-path authority.
- Merge status: PR #441 is open as a non-draft PR; merge not performed by this
  package.
- Next authority: After this PR merges, report the classification to Main 5.
  Any sizing/leverage or cost-model follow-up is a separate future package and
  is not authorized here.

## Active-WP requirement traceability

| Requirement | Source section | Evidence location | Status |
|---|---|---|---|
| Use dedicated worktree from refreshed `origin/main` | WP sections 6-8 | `C:\GitHub\crypto-perp-wedge-rp6688-sizing-diag` on `docs/rp6688-sizing-diagnostic` | satisfied |
| Verify PR #440 merged | WP section 6 | base commit `244f465` | satisfied |
| Verify required source artifacts exist | WP section 6 | diagnostic source-artifacts section | satisfied |
| Verify `RP-6688` denominator and identity facts | WP section 6 | diagnostic source-artifacts section | satisfied |
| Create one diagnostic doc | WP sections 9 and 12 | `docs/research_pipeline/2026-06-rp6688_sizing_leverage_diagnostic.md` | satisfied |
| Create status fragment | WP section 19 | this file | satisfied |
| Update project status compactly | WP section 20 | `docs/project_status.md` | satisfied |
| Update research pipeline README index | WP section 21 | `docs/research_pipeline/README.md` | satisfied |
| Classify exactly one primary outcome | WP sections 11 and 14 | diagnostic classification section | satisfied |
| Preserve read-only boundary | WP sections 10, 13, and 23 | diagnostic boundary sections and git diff checks | satisfied |
| Run required validation | WP section 22 | validation summary | satisfied |
| Complete authority/finality semantic audit | WP section 24 | authority/finality audit and PR body | satisfied |
| Push and open PR with required title | WP section 26 | PR #441 | satisfied |
| Complete final rebase and mergeability gate | WP section 27 | merge status and final report-back | satisfied |
