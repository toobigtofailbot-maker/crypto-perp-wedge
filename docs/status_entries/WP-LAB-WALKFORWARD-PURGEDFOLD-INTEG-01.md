# WP-LAB-WALKFORWARD-PURGEDFOLD-INTEG-01 - Repo-native purged walk-forward folds

## Package

- Package: `WP-LAB-WALKFORWARD-PURGEDFOLD-INTEG-01`
- Decision: `COMPLETE`
- Package class: walk-forward rigor / repo-native borrow integration.

## Branch / Worktree

- Branch: `lab/walkforward-purgedfold-integ-01`
- Worktree: `C:\GitHub\crypto-perp-wedge-worktrees\lab-walkforward-purgedfold-integ-01`
- Base: `origin/main` at `4da388a289fb0df4547d204e17b05b151f1cb595`.
- Rebase result: not needed; branch created from current `origin/main`.

## Repo-Truth Discovery

- The current walk-forward fold manifest contract already includes explicit
  `purge` and `embargo` fields.
- The current fold-manifest validator validates schema shape, chronology,
  selection/evaluation non-overlap, gap object representation, denominator
  honesty, lineage uniqueness, and non-authority posture.
- The current scratch walk-forward runner already consumes an explicit fold
  manifest and writes scratch-only run reports without changing runner or
  backtester semantics.
- `STRAT-SPEC-0004`, `VM-0004`, and `SWEEP-PLAN-0004` exist in current repo
  truth and are usable for the scratch demonstration.

## Scope Summary

This package adds a repo-native purged/embargoed fold helper at
`tools/walkforward/purged_folds.py`. The helper deterministically builds an
existing-contract fold manifest, validates it with the existing manifest
validator, and emits scratch-only comparison/provenance sidecars. It does not
depend on `purgedcv`.

The scratch demonstration uses `STRAT-SPEC-0004` / `VM-0004` /
`SWEEP-PLAN-0004` over the BTCUSDT 15m D4A slice identity and executes the
generated manifest through the existing scratch walk-forward runner. The output
remains non-canonical and advisory only.

## Changed Files

- `tools/walkforward/purged_folds.py`
- `tests/test_walkforward_purged_folds.py`
- `scratch/WP-LAB-WALKFORWARD-PURGEDFOLD-INTEG-01/README.md`
- `scratch/WP-LAB-WALKFORWARD-PURGEDFOLD-INTEG-01/purged_fold_manifest.json`
- `scratch/WP-LAB-WALKFORWARD-PURGEDFOLD-INTEG-01/purged_fold_comparison_report.json`
- `scratch/WP-LAB-WALKFORWARD-PURGEDFOLD-INTEG-01/purged_walkforward_run_report.json`
- `scratch/WP-LAB-WALKFORWARD-PURGEDFOLD-INTEG-01/walkforward_run_report.json`
- `scratch/WP-LAB-WALKFORWARD-PURGEDFOLD-INTEG-01/walkforward_dashboard_fragment.json`
- `scratch/WP-LAB-WALKFORWARD-PURGEDFOLD-INTEG-01/provenance.json`
- `docs/status_entries/WP-LAB-WALKFORWARD-PURGEDFOLD-INTEG-01.md`

## Required Conclusion

- Did the purged manifest validate against the existing canonical contract?
  `YES`; `tools.registry.validate_walkforward_fold_manifest` passed against
  `scratch/WP-LAB-WALKFORWARD-PURGEDFOLD-INTEG-01/purged_fold_manifest.json`.
- Did any contract mutation occur? `NO`; no schema or validator files changed.
- Did any runner/backtester semantics change? `NO`; `tools/walkforward/run_walkforward_scratch.py`,
  `tools/research_runner/`, `lib/backtest.py`, and `lib/evaluation.py` were not
  changed.
- What leakage risk does purge/embargo address? Adjacent training labels whose
  horizons overlap early OOS bars, rolling feature/warmup contamination at the
  IS/OOS boundary, and immediate post-test rows bleeding into later selection
  windows.
- What fold parameters were used? Timeframe `15m`, fold count `2`, selection
  `35040` bars, evaluation `8640` bars, purge `96` bars, embargo `32` bars,
  boundary semantics `start_inclusive_end_exclusive`.
- What remains non-canonical? The manifest, comparison report, run report,
  dashboard fragment, and provenance under `scratch/` are non-canonical,
  scratch-only evidence and grant no ranking, readiness, promotion, candidate,
  result-population write, paper/live, runtime, broker, exchange, or order
  authority.
- What future canonical run gate remains Karl-gated? Any canonical
  walk-forward evidence write, canonical result-population write, or use of
  purged/embargoed folds for promotion/readiness remains explicitly Karl-gated.

## Scratch Evidence

- Manifest: `scratch/WP-LAB-WALKFORWARD-PURGEDFOLD-INTEG-01/purged_fold_manifest.json`
- Comparison: `scratch/WP-LAB-WALKFORWARD-PURGEDFOLD-INTEG-01/purged_fold_comparison_report.json`
- Run report: `scratch/WP-LAB-WALKFORWARD-PURGEDFOLD-INTEG-01/purged_walkforward_run_report.json`
- Provenance: `scratch/WP-LAB-WALKFORWARD-PURGEDFOLD-INTEG-01/provenance.json`

Boundary comparison:

- Total naive selection bars: `70080`
- Total purged/embargoed selection bars: `69856`
- Total removed selection bars: `224`
- Folds with purge boundary gap: `2`
- Folds with embargo-shifted selection start: `1`

Scratch run summary:

- Run id: `WF-RUN-40BB0B209274054B`
- Fold count: `2`
- Successful fold count: `2`
- Comparable variant pairs: `16`
- Mean Sharpe delta: `0.44655263432592573`
- Mean return pct delta: `0.05303762646674898`
- Mean drawdown delta: `-0.1352295328461466`
- Warning: `sharpe_efficiency_unavailable_non_positive_or_missing_is_sharpe`

## Validation Summary

Commands run from the dedicated worktree using
`C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe`.

- `python -m pytest tests/test_walkforward_purged_folds.py -q`: PASS, 5 tests.
- `python -m tools.walkforward.purged_folds --output scratch\WP-LAB-WALKFORWARD-PURGEDFOLD-INTEG-01\purged_fold_manifest.json`: PASS.
- Local ignored D4A CSV copied from the root checkout into the worktree for
  validation only; it remains ignored by `/data/processed/**` and is not part
  of the package diff.
- `python -m tools.walkforward.run_walkforward_scratch --walkforward-manifest scratch\WP-LAB-WALKFORWARD-PURGEDFOLD-INTEG-01\purged_fold_manifest.json --ohlcv-input data\processed\d4a\binance_um_perp_BTCUSDT_15m_2020-01-01_2026-04-11_d4a_normalized.csv --output-dir scratch\WP-LAB-WALKFORWARD-PURGEDFOLD-INTEG-01 --created-at-utc 2026-06-20T12:00:00Z`: PASS.
- `python -m pytest tests/test_walkforward_purged_folds.py tests/test_run_walkforward_scratch.py -q`: PASS, 8 tests.
- `python -m tools.registry.validate_walkforward_fold_manifest scratch\WP-LAB-WALKFORWARD-PURGEDFOLD-INTEG-01\purged_fold_manifest.json`: PASS.
- `python -m tools.registry.validate_walkforward_run_report scratch\WP-LAB-WALKFORWARD-PURGEDFOLD-INTEG-01\purged_walkforward_run_report.json`: PASS.
- `python -m pytest tests/test_walkforward_fold_manifest_validator.py tests/test_research_query_walkforward_views.py -q`: PASS, 7 tests.
- `python -m tools.research_query.run --list-views`: PASS.
- `python tools/dev/diff_scope_summary.py`: PASS; no forbidden-path matches.
- `git diff --check`: PASS.

Full pytest disclosure:

- `python -m pytest -q`: TIMED OUT after approximately 904 seconds.
- Last visible output: none captured before timeout.
- Full pytest is not counted as a pass. No package-specific failure surfaced in
  captured output before timeout.

## Boundary Summary

- No canonical walk-forward manifest written.
- No canonical Result Population, Strategy Spec, Variant Manifest, Sweep Plan,
  trial log, candidate record, or canonical evidence mutation.
- No `docs/project_status.md` edit.
- No schema or validator mutation.
- No `lib/backtest.py`, `lib/evaluation.py`, `tools/research_runner/`, or
  scratch runner semantic change.
- No dependency file mutation.
- No dashboard implementation change; the dashboard fragment is the existing
  scratch runner output.
- No runtime, paper/live, OMS, risk, reconciliation, safe-mode, kill-switch,
  broker, exchange, order, credential, or private API path touched.

## Merge Status

- Ready for review.
- Full pytest timeout disclosed and not counted as a pass.
