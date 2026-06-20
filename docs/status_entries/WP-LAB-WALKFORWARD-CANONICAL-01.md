# WP-LAB-WALKFORWARD-CANONICAL-01 - Walk-forward canonical evidence contract

## WP id / title

- WP id: `WP-LAB-WALKFORWARD-CANONICAL-01`
- Follow-up: `WP-LAB-WALKFORWARD-CANONICAL-01-FOLLOWUP-01`
- Title: Promote walk-forward / OOS support from dry-run design to canonical evidence contract.
- Decision label: `CANONICAL_WALKFORWARD_CONTRACT_READY`

## Branch / PR

- Branch: `lab/walkforward-canonical-01`
- Dedicated worktree: `C:\GitHub\crypto-perp-wedge-worktrees\lab-walkforward-canonical-01`
- Base before rebase: `origin/main` at `2348f89` (after PR #519).
- Base after rebase: `origin/main` at `8a4c3c5` (after PR #520 and PR #521 merged).
- Rebase result: clean; no conflicts; no forbidden-file changes required.

## Continuation context

- This is a continuation of a previously blocked local branch. The prior Codex
  session implemented the contract but blocked before commit/PR because full
  local validation did not complete.
- The uncommitted implementation work was preserved in a commit, then rebased
  after PR #520 (EXT-ADOPTION-DECISION-01) and PR #521 (WP-LAB-RESULTS-SURFACE-01)
  merged, then re-validated.
- This package does not integrate with the merged results surface. It only
  confirms it does not conflict with that surface.
- No `docs/project_status.md` edit is made in this package.

## Package class

- Tier 3 evidence contract / schema-validator-query support.

## Scope summary

This package adds the first repo-owned walk-forward fold-manifest contract:

- closed JSON Schema for explicit IS/OOS fold boundaries and lineage;
- semantic validator for chronological ordering, non-overlap, denominator/count honesty, lineage uniqueness, result-population reference posture, purge/embargo explicitness, and non-authority flags;
- valid and invalid fixtures plus focused tests;
- read-only query registration and descriptive/integrity views over the manifest family.

It creates no canonical walk-forward manifest instance, no canonical Result Population, no strategy trial, no runner/backtester semantic change, and no promotion/readiness/screen-gate authority.

## Changed files

- `research/schemas/walkforward_fold_manifest.schema.json`
- `tools/registry/validate_walkforward_fold_manifest.py`
- `tests/test_walkforward_fold_manifest_validator.py`
- `tests/fixtures/walkforward/valid_walkforward_fold_manifest.json`
- `tests/fixtures/walkforward/invalid_walkforward_fold_manifest_overlap.json`
- `tests/fixtures/walkforward/invalid_walkforward_fold_manifest_counts.json`
- `tools/research_query/query_layer.py`
- `tools/research_query/views.sql`
- `tests/test_research_query.py` (registers the new walk-forward views into the existing query test contract: `REQUIRED_VIEWS` and `EXPECTED_COLUMNS`)
- `tests/test_research_query_walkforward_views.py`
- `docs/status_entries/WP-LAB-WALKFORWARD-CANONICAL-01.md`

## Validation summary

All commands run from the dedicated worktree after rebase onto `8a4c3c5`.

- `python -m pytest tests/test_walkforward_fold_manifest_validator.py tests/test_research_query_walkforward_views.py -q`: PASS, 7 tests.
- `python -m tools.registry.validate_walkforward_fold_manifest tests/fixtures/walkforward/valid_walkforward_fold_manifest.json`: PASS.
- `python -m tools.registry.validate_walkforward_fold_manifest`: PASS; zero-instance artifact directory `research/walkforward_fold_manifests` absent, nothing to validate.
- `python -m tools.research_query.run --list-views`: PASS; includes `v_walkforward_manifest_overview`, `v_walkforward_fold_boundaries`, `v_integrity_walkforward_fold_chronology`, `v_integrity_walkforward_fold_denominator`, and `v_integrity_walkforward_non_authority`.
- `python -m tools.research_query.run --view v_walkforward_manifest_overview` / `--view v_walkforward_fold_boundaries`: PASS, no rows (zero-instance state).
- `python -m tools.research_query.run --view v_integrity_walkforward_fold_chronology` / `--view v_integrity_walkforward_fold_denominator` / `--view v_integrity_walkforward_non_authority`: PASS, no rows.
- `python -m pytest tests/test_research_query.py::test_named_views_present tests/test_research_query.py::test_named_views_return_expected_columns -q`: PASS, 2 tests.
- `python -m pytest tests/test_research_query.py -q`: PASS, 64 tests in ~472s. (The prior session's "timeout after 300s" was only the 300s bound being too short; the adjacent query suite passes cleanly under a larger bound.)
- All 56 `v_integrity_*` views (including the 3 new walk-forward integrity views) reported `clean` / 0 rows via `tools/dev/verify.py --integrity-views`.
- `python tools/dev/diff_scope_summary.py --check-forbidden`: PASS; no forbidden-path matches.
- `git diff --check` and `git diff --cached --check`: PASS.

## Full-suite (full pytest) disclosure

Full pytest could not complete in this local environment because the scientific
stack (`pandas`, `numpy`) is not installed. Running `tools/dev/verify.py`
(sharded full pytest) produced collection-time `ModuleNotFoundError: No module
named 'pandas'` / `numpy` failures in modules unrelated to this package
(`test_backtest`, `test_evaluation`, `test_offline_research_runner`, paper-trader,
data-import, and similar). Every full-suite failure is one of these pre-existing
dependency-gap collection errors. No package-specific failure surfaced.

The package code imports neither `pandas` nor `numpy`; its schema, validator,
query views, fixtures, and tests are pure-stdlib. The focused package tests, the
full adjacent query suite (`tests/test_research_query.py`, 64 passed), and all
integrity views passed without the scientific stack. This dependency-gap result
is disclosed and is NOT counted as a full-suite pass.

## Boundary summary

- No `lib/backtest.py` changes.
- No `lib/evaluation.py` changes.
- No `tools/research_runner/run_offline_sweep.py` changes.
- No canonical Result Population, Strategy Spec, Variant Manifest, Sweep Plan, trial log, or data artifact mutation.
- No dashboard / results-surface, runtime, paper/live, OMS, risk, reconciliation, safe-mode, kill-switch, broker, exchange, order, dependency, or credential path touched.
- No `docs/project_status.md` edit.
- No funding-into-backtest wiring.
- No strategy trial executed.
- Query additions are read-only and descriptive; they do not compute strategy approval, rank variants, create readiness, or promote candidates.

## Merge status

- Ready for review.
- Focused package tests, fixture validator, default zero-instance validator,
  query list-views, new descriptive and integrity views (clean), full adjacent
  query suite, diff-scope, and git diff checks all pass.
- Full pytest dependency-gap result disclosed above and not counted as a pass.

## Next dependency / runway note

This package is intended to serialize before `WP-LAB-FUNDING-INTO-BACKTEST-01`. Funding-into-backtest remains out of scope here.
