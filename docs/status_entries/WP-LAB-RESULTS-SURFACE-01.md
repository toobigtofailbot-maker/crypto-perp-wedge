# WP-LAB-RESULTS-SURFACE-01 - Lab Results Surface

## WP id / title

- WP id: `WP-LAB-RESULTS-SURFACE-01`
- Title: Build run/result registry and dashboard results surface for lab review

## Branch / PR

- Branch: `lab/results-surface-01`
- PR: https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/521

## Package class

- Tier 3 operator surface / registry / dashboard-data support

## Scope summary

This package adds a read-only lab run/result registry over committed Result
Populations and adopted advisory report links, then projects that validated
registry into the existing local static dashboard Results page.

The registry and dashboard surface are display-only. They do not create
ranking, recommendation, readiness, promotion, approval, paper/live, runtime,
or execution authority.

## Changed files

- `research/schemas/lab_run_registry.schema.json`
- `tools/lab_registry/__init__.py`
- `tools/lab_registry/build_lab_run_registry.py`
- `tools/lab_registry/validate_lab_run_registry.py`
- `tests/test_lab_run_registry.py`
- `tests/fixtures/lab_registry/valid_lab_run_registry.json`
- `tests/fixtures/lab_registry/invalid_lab_run_registry_authority.json`
- `tests/fixtures/lab_registry/invalid_lab_run_registry_ordering.json`
- `research/schemas/dashboard_data.schema.json`
- `tools/dashboard/collector.py`
- `tools/dashboard/renderer.py`
- `tools/dashboard/validate_dashboard_data.py`
- `tests/test_generate_static_dashboard.py`
- `docs/dashboard/README.md`
- `docs/architecture/2026-06-dashboard_data_contract.md`
- `docs/status_entries/WP-LAB-RESULTS-SURFACE-01.md`

## Validation summary

- `python -m pytest tests/test_lab_run_registry.py -q`: PASS, 8 tests.
- `python -m pytest tests/test_validate_dashboard_data.py tests/test_generate_static_dashboard.py -q`: PASS, 47 tests.
- `python -m tools.lab_registry.validate_lab_run_registry tests/fixtures/lab_registry/valid_lab_run_registry.json`: PASS.
- `python -m tools.dashboard.generate_static_dashboard --output-dir dashboard_build --data-dir dashboard_data --repo-root .`: PASS; generated local output only.
- `python -m tools.dashboard.validate_dashboard_data dashboard_data/dashboard_data.json`: PASS.
- `python -m tools.dashboard.validate_dashboard_data tests/fixtures/dashboard/valid_dashboard_data_with_results.json`: PASS.
- `python -m tools.research_query.run --list-views`: PASS.
- `python tools/dev/diff_scope_summary.py`: PASS; schema paths under `research/` are scoped to this package, and no result-population writes were reported.
- `git diff --check`: PASS.
- `python -m tools.registry.validate_result_populations`: PASS.
- `python -m pytest -q` with default interpreter: collection failed because the interpreter lacks `binance`, `pandas`, and `numpy`; not used as merge evidence.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m pytest -q`: timed out after 15 minutes; no package-specific failure was surfaced before timeout.

## Boundary summary

- Runtime / paper / live paths: not touched.
- OMS / risk / reconciliation / broker / exchange / order paths: not touched.
- Canonical Result Populations, Strategy Specs, Variant Manifests, and Sweep Plans: read-only, not mutated.
- Runner / backtester / `lib/backtest.py`: not touched.
- Dependencies: not touched.
- Authority posture: display-only, no ranking, no recommendation, no readiness, no promotion, no approval, no execution, no paper/live authority.

## Active-WP requirement traceability

| Active-WP requirement | Source section | Evidence location | Status |
|---|---|---|---|
| Build lab run/result registry with config/status/evidence/lineage fields | Implementation requirements | `research/schemas/lab_run_registry.schema.json`, `tools/lab_registry/build_lab_run_registry.py`, `tests/fixtures/lab_registry/valid_lab_run_registry.json` | satisfied |
| Validate registry and reject authority/ranking/order drift | Implementation requirements / Validation | `tools/lab_registry/validate_lab_run_registry.py`, `tests/test_lab_run_registry.py` | satisfied |
| Extend dashboard/results surface from validated data only | Dashboard/results surface | `research/schemas/dashboard_data.schema.json`, `tools/dashboard/collector.py`, `tools/dashboard/renderer.py`, `tools/dashboard/validate_dashboard_data.py` | satisfied |
| Show per-strategy/per-variant summaries and adopted report links where available | Dashboard/results surface | `tools/dashboard/collector.py`, `tools/dashboard/renderer.py`, `tests/test_generate_static_dashboard.py` | satisfied |
| Preserve variant/result ordering without quality ranking | Dashboard/results surface / Additional forbidden scope | `tools/dashboard/validate_dashboard_data.py`, `tests/test_lab_run_registry.py`, `tests/test_generate_static_dashboard.py` | satisfied |
| Avoid source artifact mutation and protected runtime paths | Files forbidden to modify / Global forbidden scope | `git diff --name-only`, `python tools/dev/diff_scope_summary.py`, boundary summary above | satisfied |
| Keep generated dashboard outputs uncommitted | Validation | `git status --short` after generation; `dashboard_data/` and `dashboard_build/` absent from status | satisfied |
| Record package status in per-WP status fragment, not `docs/project_status.md` | Parallel collision note | `docs/status_entries/WP-LAB-RESULTS-SURFACE-01.md`; `docs/project_status.md` unchanged | satisfied |

## Merge status

- PR #521 is open and ready for review with the full-suite timeout classification above.

## Next dependency / runway note

If merged, the dashboard can show a lab-wide run/result registry for human
review while preserving canonical evidence and protected runtime boundaries.
