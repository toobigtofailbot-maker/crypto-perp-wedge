# WP-COMP-PLUSCOMP-01c — Implement plus composition compiler support

- Package class: T3 compiler + tests implementation
- Branch: `compiler/comp-pluscomp-01c-plus-eval`
- PR: https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/432
- Scope summary: Implements compiler support for the closed `scale_by_one_plus_parameter` composed operand as the symmetric sibling of existing `scale_by_one_minus_parameter`.
- Authorization basis: Main 5 conditional runway after merged `WP-COMP-PLUSCOMP-01a` design lock and merged `WP-COMP-PLUSCOMP-01b` schema/validator support.
- Changed files:
  - `tools/research_runner/spec_signal_compiler.py`
  - `tests/test_spec_signal_compiler.py`
  - `docs/status_entries/WP-COMP-PLUSCOMP-01c.md`
  - `docs/project_status.md`
- Implementation summary: The compiler now uses a closed two-value composed-operand allow-set containing exactly `scale_by_one_minus_parameter` and `scale_by_one_plus_parameter`. `_resolve_composed_operand` preserves exact-key checks, base operand restriction to `data_ref` / `indicator_ref`, parameter operand restriction to `parameter_ref`, non-nesting, numeric non-bool finite `(0, 1)` parameter validation, null propagation through pandas arithmetic, and fail-closed rejection of unsupported composition types. Minus composition remains `base * (1 - p)`, and plus composition evaluates `base * (1 + p)`.
- Validation summary:
  - `python -m pytest tests/test_spec_signal_compiler.py -q`: pass, 105 tests.
  - `python -m pytest tests/test_validate_strategy_specs.py -q`: pass, 55 tests.
  - `python -m tools.registry.validate_result_populations`: pass.
  - `python -m tools.research_query.run --list-views`: pass.
  - All discovered `v_integrity_*` views: pass, 55 clean / zero rows, via single-process query-layer check after the per-view subprocess loop exceeded the tool timeout.
  - `python tools/dev/diff_scope_summary.py`: pass; no forbidden-path matches and no untracked files at the time run.
  - `python -m pytest -q`: environment-only failure, 1276 passed / 1 failed; `tests/test_backtest_liquidation.py::test_buy_and_hold_unchanged_on_benign_window` requires gitignored `data/processed/binance_um_perp_BTCUSDT_4h_2020-01-01_2026-04-11_2026-04-12T1655Z.parquet`, which is absent from the isolated worktree. This is classified under the active WP's missing-local-data rule and is not used as a package-code failure.
- Boundary summary: No schema, validator, catalog, Strategy Spec, variant manifest, sweep plan, result population, dashboard, data acquisition, simulator, runtime, paper/live, OMS/risk, broker/exchange, or protected-path change.
- Active-WP requirement traceability:

| Requirement | Evidence | Status |
|---|---|---|
| plus composition evaluates `base * (1 + p)` | `tools/research_runner/spec_signal_compiler.py`; focused compiler tests | satisfied |
| minus composition remains `base * (1 - p)` | focused compiler tests | satisfied |
| numeric finite `(0,1)` parameter check preserved | compiler implementation; focused compiler tests | satisfied |
| base restriction preserved | compiler implementation; focused compiler tests | satisfied |
| parameter restriction preserved | compiler implementation; focused compiler tests | satisfied |
| nesting remains rejected | focused compiler tests | satisfied |
| unsupported composition types rejected | focused compiler tests | satisfied |
| null/NaN base values preserved | focused compiler tests | satisfied |
| no-lookahead behavior proven | focused compiler tests | satisfied |
| deterministic repeated compilation proven | focused compiler tests | satisfied |
| schema/validator not modified | changed-file list | satisfied |
| no Strategy Specs/artifacts touched | changed-file list | satisfied |
| required validation run | validation summary | satisfied |
| PR body/status finality clean | final PR readiness gate | satisfied |
| no forbidden paths touched | diff scope and changed-file list | satisfied |

- Merge status: PR #432 is open and ready for review after branch push. GitHub mergeability evidence is reported in PR metadata and final report-back.
- Next authority: After this PR merges, Side reports the completed plus-composition runway back to Main 5 and asks Main 5 for next direction. Do not draft the next implementation WP automatically.
