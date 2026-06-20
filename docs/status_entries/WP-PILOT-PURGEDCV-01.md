# WP-PILOT-PURGEDCV-01 - Scratch purged CV fold helper pilot

## Package

- Package: `WP-PILOT-PURGEDCV-01`
- Decision: `COMPLETE`
- Package class: scratch-only external-tool pilot / borrow-candidate.

## Branch / Worktree

- Branch: `pilot/purgedcv-01`
- Worktree: `C:\GitHub\crypto-perp-wedge-worktrees\pilot-purgedcv-01`
- Base: `origin/main` at `0ca18b9`.
- Rebase result: not needed; branch created from current `origin/main`.

## Repo-Truth Discovery

- Current walk-forward fold manifests already encode explicit `purge` and
  `embargo` fields.
- Current walk-forward validator checks representation, chronology,
  non-overlap, denominator honesty, lineage, and non-authority posture, but
  does not choose or enforce a purge/embargo sizing policy.
- Current scratch walk-forward runner remains explicit-window and scratch-only.
- Existing dry-run runner summary records purge/embargo as
  `not_implemented_deferred_by_design`.
- `docs/status_entries/WP-PLAN-SIDE12-ADOPTION-LOCK-01.md` was not present in
  the merged branch during this package.

## Scope Summary

This package adds a deterministic scratch-only pilot that compares naive
adjacent 15m-like walk-forward folds against a transparent repo-native
purged/embargoed fold sketch. The pilot probes whether `purgedcv` is importable
in the local environment and records the result honestly, but it does not use
the dependency for fold construction or grant dependency authority.

The pilot recommendation is `borrow`: use the purged/embargoed approach in a
future small repo-native helper rather than adopting `purgedcv` as a required
dependency or canonical sidecar from this evidence alone.

## Changed Files

- `tools/pilots/purgedcv_pilot/__init__.py`
- `tools/pilots/purgedcv_pilot/run_purgedcv_pilot.py`
- `tests/test_purgedcv_pilot.py`
- `scratch/WP-PILOT-PURGEDCV-01/README.md`
- `scratch/WP-PILOT-PURGEDCV-01/dependency_probe.json`
- `scratch/WP-PILOT-PURGEDCV-01/fold_comparison_report.json`
- `scratch/WP-PILOT-PURGEDCV-01/fold_comparison_report.md`
- `scratch/WP-PILOT-PURGEDCV-01/provenance.json`
- `scratch/WP-PILOT-PURGEDCV-01/requirements.poc.txt`
- `docs/status_entries/WP-PILOT-PURGEDCV-01.md`

## Validation Summary

Commands run from the dedicated worktree:

- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m pytest tests/test_purgedcv_pilot.py -q`: PASS, 5 tests.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.pilots.purgedcv_pilot.run_purgedcv_pilot --output-dir scratch/WP-PILOT-PURGEDCV-01`: PASS; rewrote only scratch pilot artifacts.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m tools.research_query.run --list-views`: PASS.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe tools/dev/diff_scope_summary.py`: PASS; no forbidden-path matches.
- `git diff --check`: PASS.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m pytest tests/test_walkforward_fold_manifest_validator.py tests/test_run_walkforward_scratch.py tests/test_research_query_walkforward_views.py -q`: PASS, 10 tests.

Default `python -m pytest tests/test_walkforward_fold_manifest_validator.py tests/test_run_walkforward_scratch.py tests/test_research_query_walkforward_views.py -q` was also tried before switching to the shared venv and failed during collection because the default Python lacks `pandas`; this is an interpreter/environment mismatch, not a package-specific failure.

Full pytest disclosure:

- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m pytest -q`: TIMED OUT after approximately 604 seconds.
- Last visible output: none captured before timeout.
- After the timeout, leftover `pytest -q` process pairs from the package validation attempt were stopped; no `pytest -q` process remained from this package attempt afterward.
- Full pytest is not counted as a pass. No package-specific failure surfaced before timeout.

## Boundary Summary

- No canonical walk-forward manifest written.
- No canonical Result Population, Strategy Spec, Variant Manifest, Sweep Plan,
  trial log, candidate record, or canonical evidence mutation.
- No `docs/project_status.md` edit.
- No repo dependency file mutation; `requirements.poc.txt` is scratch-only.
- No `lib/backtest.py`, `lib/evaluation.py`, runner, schema, validator,
  compiler, data, query-layer, dashboard implementation, runtime, paper/live,
  OMS, risk, reconciliation, safe-mode, kill-switch, broker, exchange, order,
  credential, or private API path touched.
- External-tool posture remains scratch-only, advisory, deterministic where
  possible, and non-authoritative.

## Recommendation

- Can this improve fold rigor? Yes.
- Should the repo borrow the approach repo-native? Yes.
- Should `purgedcv` become a dependency or sidecar now? No.
- Future WP: `WP-WALKFORWARD-PURGE-EMBARGO-HELPER-01`.
- Smallest integration surface: a pure fold-boundary helper that emits explicit
  purge/embargo fields for walk-forward fold manifests, plus validator checks
  that evaluation starts after selection end plus the required purge.

## Merge Status

- Ready for review with full-suite timeout disclosed and not counted as a pass.
