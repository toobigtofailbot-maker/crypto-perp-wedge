# WP-LAB-FUNDING-BACKTEST-DEFAULT-OFF-RECONCILIATION-01

- Title: Reconcile existing default-on funding behavior into Karl-preauthorized default-off funding mode.
- Branch: `lab/funding-backtest-default-off-reconciliation-01-preauth`.
- PR: created after the initial preauthorized push; this field is replaced with the actual URL before final review handoff.
- Package class: Protected cost-model reconciliation, Karl-preauthorized under the package's ten strict conditions.
- Scope summary: Adds one deterministic `funding_cost_mode` switch to `lib/backtest.py`. Omitted/default mode is `off`; explicit `on` preserves the prior sign, event alignment, and entry-price/mark-price notional behavior.
- Changed files: `lib/backtest.py`; `tests/test_backtest.py`; this status entry; `scratch/WP-LAB-FUNDING-BACKTEST-DEFAULT-OFF-RECONCILIATION-01/repo_truth_discovery.md`; `scratch/WP-LAB-FUNDING-BACKTEST-DEFAULT-OFF-RECONCILIATION-01/PREAUTHORIZED_COMMIT_REPORT.md`.
- Validation summary: focused backtest suite passed (`81 passed, 1 skipped`); Result Population tests passed (`61 passed`); canonical Result Population validator passed; research query view discovery passed (`124` views); diff-scope helper passed with only the explicitly authorized `lib/backtest.py` protected-path match; `git diff --check` passed. Full pytest completed with `1961 passed, 1 skipped, 1 failed`; the sole failure was `tests/test_external_simulator_pilot.py::test_default_fixture_mapping_uses_rp_2592_lineage` because the isolated worktree lacks the gitignored D4A normalized CSV, which is the package's expressly permitted caveat.
- Boundary summary: No canonical Result Population, schema, validator, query-layer, runner, fee, slippage, fill, sizing, runtime, paper, live, OMS, risk, reconciliation, capital, credential, promotion, or readiness path changed. The only protected file changed is the explicitly authorized research backtester.
- Merge status: Karl preauthorization conditions are satisfied; preauthorized commit and PR publication are allowed.
- Next dependency / runway note: Merge only after review confirms default-off behavior, explicit-on compatibility, exact changed-file scope, and the disclosed isolated-worktree D4A caveat. This package creates no runtime or promotion authority.

## Validation command notes

- Ambient `python -m pytest tests/test_backtest*.py -q` could not collect because the ambient interpreter lacks `numpy` and `pandas`; it is not validation evidence.
- The literal wildcard path is not expanded when passed through PowerShell to pytest. The equivalent explicit repo-venv command, `python -m pytest tests/test_backtest.py tests/test_backtest_liquidation.py -q`, is the focused evidence and passed.
