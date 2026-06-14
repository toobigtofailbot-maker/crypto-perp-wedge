# WP-VERIFY-01A - RP-7520 stale corpus-count test correction

- Package class: T3 test-support / stale expectation correction.
- Branch: `tests/rp7520-corpus-count-expectations`.
- PR: https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/457
- Scope summary: Updates stale test expectations so the committed result-population corpus includes `RP-7520` alongside `RP-2134`, `RP-4492`, and `RP-6688`. The offline-runner scratch-write test now snapshots the current committed corpus before the scratch write and verifies it is unchanged afterward; the query-layer corpus view test now expects RP-7520's deterministic lineage, denominator, row, coverage, execution-context, and non-authority rows.
- Changed files: `tests/test_offline_research_runner.py`, `tests/test_research_query.py`, `docs/status_entries/WP-VERIFY-01A.md`.
- Reproduced stale failing nodeids on refreshed `main`: `tests/test_offline_research_runner.py::test_canonical_15m_scratch_result_population_validates`; `tests/test_research_query.py::test_first_canonical_15m_result_population_views_under_first_parent_instances`.
- Current canonical result-population inventory: `RP-2134.result_population.json`, `RP-4492.result_population.json`, `RP-6688.result_population.json`, `RP-7520.result_population.json`.
- RP-7520 expectation change: corpus count changed from `3` to `4`; RP-7520 is included as a 10-row complete `STRAT-SPEC-0002` / `VM-0002` / `SWEEP-PLAN-0002` offline result population over the D4 BTCUSDT 15m slice, with deterministic seed `190` and `reference_only` non-authority status.
- Validation summary: final commands ran with the repo `.venv` interpreter and passed unless noted below.
- Boundary summary: No production behavior, query-layer semantics, runner/backtester/lib/schema/validator behavior, result populations, data lineage, runtime, paper/live, OMS/risk, broker/exchange, candidate lifecycle, ranking, promotion, readiness, or protected paths changed.
- Merge status: PR #457 is open as a ready-for-review, non-draft PR from refreshed `origin/main`; validation evidence is final.
- Next dependency / runway note: After merge, revalidate the separate WP-VERIFY-01 branch and open that PR if clean.

## Validation Detail

- `git diff --check`: pass.
- `git diff --cached --check`: pass.
- `git diff --name-only`: pass; listed `tests/test_offline_research_runner.py` and `tests/test_research_query.py` before this status fragment was added.
- `.venv\Scripts\python.exe tools/dev/diff_scope_summary.py --check-forbidden`: pass; forbidden-path matches none.
- `.venv\Scripts\python.exe -m tools.registry.validate_result_populations`: pass.
- `.venv\Scripts\python.exe -m tools.research_query.run --list-views`: pass.
- `.venv\Scripts\python.exe -m pytest tests/test_offline_research_runner.py::test_canonical_15m_scratch_result_population_validates -q`: pass; `1 passed`.
- `.venv\Scripts\python.exe -m pytest tests/test_research_query.py::test_first_canonical_15m_result_population_views_under_first_parent_instances -q`: pass; `1 passed`.
- `.venv\Scripts\python.exe -m pytest tests/test_offline_research_runner.py -q`: pass; `73 passed, 2 warnings`.
- `.venv\Scripts\python.exe -m pytest tests/test_research_query.py -q`: pass; `63 passed`.
- `.venv\Scripts\python.exe -m pytest -q`: pass; `1376 passed, 6 warnings` in `1049.38s`.

## Non-Evidence Runs

- `python -m pytest -q` with system Python: collection failed because system Python lacks project dependencies (`binance`, `numpy`, `pandas`); not used as merge evidence.
- Parallel `.venv` full/query pytest attempt: timed out under concurrent load; not used as merge evidence.
- First `.venv` full pytest single run: timed out at a 15-minute command ceiling without reported test failures; superseded by the passing 30-minute full-pytest run.
