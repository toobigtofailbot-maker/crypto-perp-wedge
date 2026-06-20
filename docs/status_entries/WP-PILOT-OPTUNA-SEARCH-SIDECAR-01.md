# WP-PILOT-OPTUNA-SEARCH-SIDECAR-01 - Optuna Search Sidecar Pilot

## WP id / title

- WP id: `WP-PILOT-OPTUNA-SEARCH-SIDECAR-01`
- Title: Pilot Optuna bounded search sidecar

## Branch / PR

- Branch: `pilot/optuna-search-sidecar-01`
- Dedicated worktree: `C:\GitHub\crypto-perp-wedge-worktrees\pilot-optuna-search-sidecar-01`
- PR: pending

## Package class

- Scratch-only external-tool pilot / sidecar-candidate

## Scope summary

This package adds a bounded Optuna search sidecar wrapper under
`tools/sidecars/optuna_search_pilot/` and commits scratch-only pilot outputs
under `scratch/WP-PILOT-OPTUNA-SEARCH-SIDECAR-01/`.

The pilot uses a toy deterministic objective and never invokes the canonical
runner, backtester, result-population path, trial log, Strategy Spec, Variant
Manifest, Sweep Plan, dashboard implementation, or runtime path. It exports all
trial states, including complete, pruned, and failed trials, and keeps explicit
non-authority labels plus handoff requirements.

## Dependency / evidence result

- Default interpreter Optuna availability: unavailable
  (`ModuleNotFoundError: No module named 'optuna'`).
- Repo venv Optuna availability: unavailable.
- Real Optuna exercised: `false`.
- Execution status:
  `PARTIAL_BLOCKED_OPTIONAL_DEPENDENCY_UNAVAILABLE`.
- Recommendation: `preserve`.
- The committed run is partial blocked evidence only and uses the deterministic
  mock sampler explicitly labeled as `deterministic_mock_sampler`.
- Trial state export: 20 total rows; 16 complete, 2 pruned, 2 failed.
- Search-space hash:
  `sha256:daedc1604d83ad1cfa9ce8a71b3cef2ad5aa73a10985d9534ead981653414b7f`.
- Trial-population hash:
  `sha256:872df20f2a6039a2fad1daf00ad6076ac93c134aef265c88489ee6fe9045816c`.
- Summary output checksum:
  `sha256:1d7fd9acf3d4e887aab49dd9149d244e2c28fbd1d88ccc1666467e6eaaacc0cc`.

## Changed files

- `tools/sidecars/optuna_search_pilot/__init__.py`
- `tools/sidecars/optuna_search_pilot/run_optuna_search_pilot.py`
- `tests/test_optuna_search_pilot.py`
- `scratch/WP-PILOT-OPTUNA-SEARCH-SIDECAR-01/README.md`
- `scratch/WP-PILOT-OPTUNA-SEARCH-SIDECAR-01/search_space.json`
- `scratch/WP-PILOT-OPTUNA-SEARCH-SIDECAR-01/trial_population.jsonl`
- `scratch/WP-PILOT-OPTUNA-SEARCH-SIDECAR-01/trial_summary.json`
- `scratch/WP-PILOT-OPTUNA-SEARCH-SIDECAR-01/recommendation_report.md`
- `scratch/WP-PILOT-OPTUNA-SEARCH-SIDECAR-01/provenance.json`
- `scratch/WP-PILOT-OPTUNA-SEARCH-SIDECAR-01/dependency_probe.json`
- `scratch/WP-PILOT-OPTUNA-SEARCH-SIDECAR-01/requirements.poc.txt`
- `docs/status_entries/WP-PILOT-OPTUNA-SEARCH-SIDECAR-01.md`

## Validation summary

- `python -m pytest tests/test_optuna_search_pilot.py -q`: PASS, 8 tests.
- `python -m tools.sidecars.optuna_search_pilot.run_optuna_search_pilot --output-dir scratch/WP-PILOT-OPTUNA-SEARCH-SIDECAR-01 --trials 20 --seed 1729`: PASS; wrote scratch artifacts with `real_optuna_exercised=false`.
- `python tools/dev/diff_scope_summary.py`: PASS; forbidden-path matches: none.
- `git diff --check`: PASS.
- `python -m pytest tests/test_generate_static_dashboard.py tests/test_lab_run_registry.py -q`: PASS, 38 tests.
- `python -m tools.research_query.run --list-views`: PASS.
- `python -m pytest -q` with default Python 3.14: FAIL during collection after 6.84 seconds because the interpreter lacks `binance`, `pandas`, and `numpy`; no package-specific failure surfaced.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m pytest -q --maxfail=1 -ra`: FAIL after 51.27 seconds with 518 passed, 1 skipped, and the first failure in `tests/test_external_simulator_pilot.py::test_default_fixture_mapping_uses_rp_2592_lineage` because `fixture["normalized_data_local_exists"]` was `False` in this isolated worktree. This matches an existing local gitignored data-file limitation and is not caused by this package.

## Boundary summary

- Runtime / paper / live paths: not touched.
- OMS / risk / reconciliation / safe-mode / kill-switch / broker / exchange /
  order / capital paths: not touched.
- Canonical Strategy Specs / Variant Manifests / Sweep Plans: not touched.
- Canonical Result Populations: not touched.
- Trial log: not touched.
- Runner / backtester / `lib/backtest.py`: not touched.
- Dashboard implementation / query layer / lab registry: not touched.
- Dependency files: not touched.
- Private credentials / authenticated APIs: not used.
- Authority posture: scratch-only sidecar candidate; no winner-selection,
  ranking, candidate evidence, readiness, promotion, paper/live, or runtime
  authority.

## Guardrail statements

- Optuna suggestions are not winners.
- Any suggested params must be re-screened through the repo-owned honest
  full-population / OOS / robustness pipeline.
- No winner-only reporting is allowed.
- Pruned/failed trials remain part of search lineage.
