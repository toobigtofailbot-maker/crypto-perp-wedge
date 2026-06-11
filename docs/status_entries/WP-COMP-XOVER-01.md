# WP-COMP-XOVER-01 - Implement closed crossover compiler operators

- Package class: T3 compiler implementation
- Branch: `compiler/comp-xover-01-crosses-operators`
- PR: https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/429
- Scope summary: Implements compiler-only support for the closed `crosses_above` and `crosses_below` Strategy Spec operators, with focused tests for prior/current bar semantics, null behavior, no-lookahead behavior, determinism, and fail-closed unsupported operators.
- Authorization basis: Main 5 selected the compiler / indicator expressiveness lane after STRAT-CAP, and `WP-COMP-SURFACE-01` identified `crosses_above` / `crosses_below` as the narrowest implementation-ready compiler/test-only block after PR #428 merged.
- Changed files:
  - `tools/research_runner/spec_signal_compiler.py`
  - `tests/test_spec_signal_compiler.py`
  - `docs/status_entries/WP-COMP-XOVER-01.md`
  - `docs/project_status.md`
- Implementation summary: `crosses_above` and `crosses_below` are now in the compiler supported operator set. `in_set`, `is_true`, and `is_false` remain explicitly unsupported and fail closed with `UnsupportedSpecSignalCompilerFeature`. Unknown operators still raise `SpecSignalCompilerError`.
- Crossover semantics: `crosses_above` is true only when the immediately prior bar satisfies `left <= right` and the current bar satisfies `left > right`. `crosses_below` is true only when the immediately prior bar satisfies `left >= right` and the current bar satisfies `left < right`. The first row returns false. Any null prior/current left/right operand returns false. Scalar operands use the same scalar value at prior and current timestamps; Series operands use only the current timestamp and the immediately prior OHLCV index timestamp.
- Test summary: Added focused compiler tests for `crosses_above`, `crosses_below`, current equality, first-row false, null prior/current operands, series-vs-series operands, no-lookahead, deterministic repeated compilation, remaining unsupported operators, and unknown operator failure.
- Validation summary:
  - `python -m pytest tests/test_spec_signal_compiler.py -q` with root virtualenv: pass, 87 passed.
  - `python -m pytest tests/test_validate_strategy_specs.py -q` with root virtualenv: pass, 54 passed.
  - `python -m tools.registry.validate_result_populations` with root virtualenv: pass.
  - `python -m tools.research_query.run --list-views` with root virtualenv: pass.
  - All discovered `v_integrity_*` views: pass, 55 clean / zero rows, via single-process query-layer check after the per-view CLI loop exceeded the tool timeout.
  - `python tools/dev/diff_scope_summary.py` with root virtualenv: pass; no forbidden-path matches.
  - Initial full pytest attempt with root virtualenv: exceeded a 10-minute tool timeout with no failure output captured.
  - Final `python -m pytest -q` with root virtualenv: environment-only failure, 1257 passed / 1 failed because the isolated worktree lacks gitignored `data/processed/binance_um_perp_BTCUSDT_4h_2020-01-01_2026-04-11_2026-04-12T1655Z.parquet` required by `tests/test_backtest_liquidation.py::test_buy_and_hold_unchanged_on_benign_window`.
- Boundary summary: Compiler/test/status only. No schema, validator, indicator catalog, Strategy Spec, variant manifest, sweep plan, result population, runner output, dashboard implementation, generated output, data acquisition, simulator, runtime, paper/live, OMS/risk, broker/exchange, or protected-path behavior changed. No ranking, recommendation, readiness, promotion, canonical-use, or execution authority is created.
- Active-WP requirement traceability:

| Requirement | Evidence | Status |
|---|---|---|
| `crosses_above` implemented in compiler | `tools/research_runner/spec_signal_compiler.py`; focused compiler tests | satisfied |
| `crosses_below` implemented in compiler | `tools/research_runner/spec_signal_compiler.py`; focused compiler tests | satisfied |
| Prior/current bar semantics implemented | `_evaluate_crossover`; prior/current semantics tests | satisfied |
| First row false | `test_crosses_first_row_is_false` | satisfied |
| Null prior/current false | `test_crosses_null_prior_or_current_values_are_false` | satisfied |
| Current equality false | `test_crosses_current_equality_is_false` | satisfied |
| No-lookahead proven | `test_crosses_operator_has_no_lookahead` | satisfied |
| Determinism proven | `test_crosses_compiler_repeated_calls_are_deterministic` | satisfied |
| `in_set`, `is_true`, `is_false` still fail closed | `test_other_unsupported_operators_still_fail_closed` | satisfied |
| Unknown operators still fail closed | `test_unknown_operator_still_fails_closed` | satisfied |
| Existing threshold/composed/lookback behavior preserved | `tests/test_spec_signal_compiler.py -q`: 87 passed | satisfied |
| No schema/validator/catalog changes | Diff scope and changed-file list | satisfied |
| No Strategy Spec / artifact / result-population changes | Diff scope and changed-file list | satisfied |
| Required validation run | Validation summary in this fragment | satisfied |
| Full pytest final status recorded | Validation summary in this fragment | satisfied |
| PR body/status finality clean | Final PR readiness gate | satisfied |
| No forbidden paths touched | `tools/dev/diff_scope_summary.py`; changed-file list | satisfied |

- Merge status: PR #429 is open, non-draft, rebased onto `origin/main`, clean after final local diff checks, and GitHub reports `mergeable=MERGEABLE`.
