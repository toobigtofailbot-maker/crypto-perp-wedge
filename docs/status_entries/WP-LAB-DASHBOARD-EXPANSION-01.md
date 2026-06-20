# WP-LAB-DASHBOARD-EXPANSION-01 - Dashboard Operator Review Surface

## WP id / title

- WP id: `WP-LAB-DASHBOARD-EXPANSION-01`
- Title: Expand dashboard to operator review surface with blockers and uncertainty

## Branch / PR

- Branch: `lab/dashboard-expansion-01`
- Dedicated worktree: `C:\GitHub\crypto-perp-wedge-worktrees\lab-dashboard-expansion-01`
- PR: https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/524

## Package class

- Tier 3 operator surface / dashboard contract

## Scope summary

This package extends the local static dashboard and validated
`dashboard_data.v1` contract with an Operator Review page. The page displays
active-job availability, recent committed lab records, population completeness,
outcome counts, candidate caveats, walk-forward / OOS coverage, robustness
coverage, funding-realism blockers, lifecycle availability, manual approval
posture, blockers, warnings, uncertainty, and evidence links.

The surface is read-only and advisory. It does not rank, recommend, approve,
promote, declare readiness, satisfy gates, create paper/live authority, mutate
artifacts, or execute controls.

## Changed files

- `research/schemas/dashboard_data.schema.json`
- `tools/dashboard/collector.py`
- `tools/dashboard/renderer.py`
- `tools/dashboard/validate_dashboard_data.py`
- `tools/dashboard/templates/index.html`
- `tests/test_validate_dashboard_data.py`
- `tests/test_generate_static_dashboard.py`
- `tests/fixtures/dashboard/valid_dashboard_data_operator_review.json`
- `tests/fixtures/dashboard/invalid_dashboard_data_operator_authority.json`
- `docs/dashboard/README.md`
- `docs/status_entries/WP-LAB-DASHBOARD-EXPANSION-01.md`

## Validation summary

- `python -m pytest tests/test_validate_dashboard_data.py tests/test_generate_static_dashboard.py -q`: PASS, 55 tests.
- `python -m tools.dashboard.validate_dashboard_data tests/fixtures/dashboard/valid_dashboard_data_operator_review.json`: PASS.
- `python -m tools.dashboard.generate_static_dashboard --output-dir dashboard_build --data-dir dashboard_data --repo-root .`: PASS; generated `dashboard_data/dashboard_data.json` and `dashboard_build/index.html` as ignored local output.
- `python -m pytest tests/test_lab_run_registry.py -q`: PASS, 8 tests.
- `python -m tools.research_query.run --list-views`: PASS.
- `python tools/dev/verify.py --integrity-views`: PASS; all discovered `v_integrity_*` views clean / zero rows.
- `python tools/dev/diff_scope_summary.py`: PASS; no forbidden-path matches.
- `git diff --check`: PASS.
- `python -m pytest -q` with the default interpreter: collection failed because that interpreter lacks `binance`, `pandas`, and `numpy`; not used as merge evidence.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe -m pytest -q`: TIMED OUT after 15 minutes without surfacing a package-specific failure.
- `C:\GitHub\crypto-perp-wedge\.venv\Scripts\python.exe tools/dev/verify.py --full-pytest-sharded --pytest-shards 6 --pytest-shard-workers 3 --full-pytest-timeout-seconds 900 --max-output-chars 12000`: FAIL, 5/6 shards passed; shard 5 had one unrelated environment/data failure in `tests/test_external_simulator_pilot.py::test_default_fixture_mapping_uses_rp_2592_lineage` because `fixture["normalized_data_local_exists"]` was `False` in the isolated worktree. The failing check expects a gitignored local normalized data file and is not caused by dashboard/operator-review changes.

## Boundary summary

- Runtime / paper / live paths: not touched.
- OMS / risk / reconciliation / safe-mode / kill-switch / broker / exchange / order / capital paths: not touched.
- `lib/backtest.py` and `lib/evaluation.py`: not touched.
- `tools/research_runner/`: not touched.
- Canonical Result Populations, Strategy Specs, Variant Manifests, and Sweep Plans: read-only, not mutated.
- Dependencies: not touched.
- `docs/project_status.md`: not touched.
- Dashboard authority posture: display-only and advisory; no ranking, recommendation, readiness, promotion, approval, paper/live, capital, risk, or execution authority.

## Active-WP requirement traceability

| Active-WP requirement | Source section | Evidence location | Status |
|---|---|---|---|
| Show active / recent research jobs | Dashboard content requirements | `tools/dashboard/collector.py`, `tools/dashboard/renderer.py`, `tests/test_generate_static_dashboard.py` | satisfied |
| Show run/result registry and population completeness summaries | Dashboard content requirements | `tools/dashboard/collector.py`, `research/schemas/dashboard_data.schema.json` | satisfied |
| Show candidates with caveats and evidence links | Dashboard content requirements | `tools/dashboard/collector.py`, `tools/dashboard/renderer.py` | satisfied |
| Show failed / invalid / excluded / errored / aborted / data-unavailable counts | Dashboard content requirements | `research/schemas/dashboard_data.schema.json`, `tools/dashboard/collector.py` | satisfied |
| Show walk-forward / OOS, robustness, lifecycle, approvals, blockers, warnings, and uncertainty | Dashboard content requirements | `tools/dashboard/collector.py`, `tools/dashboard/renderer.py`, `docs/dashboard/README.md` | satisfied |
| Add explicit non-authority flags | Schema requirements | `research/schemas/dashboard_data.schema.json`, `tools/dashboard/validate_dashboard_data.py` | satisfied |
| Reject dashboard authority drift | Required boundary / forbidden display | `tests/fixtures/dashboard/invalid_dashboard_data_operator_authority.json`, `tests/test_validate_dashboard_data.py` | satisfied |
| Use status fragment instead of `docs/project_status.md` | Parallel execution discipline | `docs/status_entries/WP-LAB-DASHBOARD-EXPANSION-01.md`; `docs/project_status.md` unchanged | satisfied |

## Merge status

- Branch validation completed with the full-suite isolated-worktree data-file failure classified above.
- PR #524 is open and ready for review with the validation disclosure above.
- GitHub CLI reports `mergeable=MERGEABLE`, `mergeStateStatus=CLEAN`, and `isDraft=false`.

## Next dependency / runway note

The dashboard can display current lab-review blockers and missing evidence after
merge, while preserving canonical evidence authority and protected runtime
boundaries.
