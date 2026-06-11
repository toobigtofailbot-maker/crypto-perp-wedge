# WP-COMP-PLUSCOMP-01b — Add plus composition schema validator support

- Package class: T3 schema + validator + tests implementation
- Branch: `schema/comp-pluscomp-01b-validator`
- PR: https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/431
- Scope summary: Extends Strategy Spec schema and validator acceptance for the closed `scale_by_one_plus_parameter` composed operand as the symmetric sibling of existing `scale_by_one_minus_parameter`.
- Authorization basis: Main 5 conditional runway after merged `WP-COMP-PLUSCOMP-01a`, with design semantics locked in `docs/research_pipeline/2026-06-plus_parameter_composition_design.md`.
- Changed files:
  - `research/schemas/strategy_spec.schema.json`
  - `tools/registry/validate_strategy_specs.py`
  - `tests/test_validate_strategy_specs.py`
  - `docs/status_entries/WP-COMP-PLUSCOMP-01b.md`
  - `docs/project_status.md`
- Implementation summary: The schema now uses a closed two-value `composition_type` enum containing exactly `scale_by_one_minus_parameter` and `scale_by_one_plus_parameter`. The validator now uses a closed two-value allow-set for composed operands, while preserving base operand, parameter operand, parameter-bound, and non-nesting checks for the accepted forms. Focused validator tests cover minus acceptance, plus acceptance, rejection of unsupported composition types, plus-form base/parameter restrictions, plus-form nesting rejection, plus-form `(0, 1)` bound checks, and the validator import boundary.
- Validation summary:
  - `python -m pytest tests/test_validate_strategy_specs.py -q`: pass, 55 tests.
  - `python -m pytest tests/test_spec_signal_compiler.py -q`: pass, 87 tests.
  - `python -m tools.registry.validate_strategy_specs`: pass.
  - `python -m tools.registry.validate_result_populations`: pass.
  - `python -m tools.research_query.run --list-views`: pass.
  - All discovered `v_integrity_*` views: pass, 55 clean / zero rows, via single-process query-layer check after the per-view subprocess loop exceeded the tool timeout.
  - `python tools/dev/diff_scope_summary.py`: pass; changed files match the WP scope, with the allowed schema path noted under `research/`.
  - `python -m pytest -q`: environment-only failure, 1258 passed / 1 failed; `tests/test_backtest_liquidation.py::test_buy_and_hold_unchanged_on_benign_window` requires gitignored `data/processed/binance_um_perp_BTCUSDT_4h_2020-01-01_2026-04-11_2026-04-12T1655Z.parquet`, which is absent from the isolated worktree. This is classified under the active WP's missing-local-data rule and is not used as a package-code failure.
- Boundary summary: No compiler implementation, catalog, Strategy Spec, variant manifest, sweep plan, result population, dashboard, data acquisition, simulator, runtime, paper/live, OMS/risk, broker/exchange, or protected-path change. Compiler remains intentionally unchanged for WP-COMP-PLUSCOMP-01c.
- Active-WP requirement traceability:

| Requirement | Evidence | Status |
|---|---|---|
| schema accepts plus composition | `research/schemas/strategy_spec.schema.json`; focused tests | satisfied |
| schema still accepts minus composition | `research/schemas/strategy_spec.schema.json`; focused tests | satisfied |
| validator accepts plus composition | `tools/registry/validate_strategy_specs.py`; focused tests | satisfied |
| validator still accepts minus composition | `tools/registry/validate_strategy_specs.py`; focused tests | satisfied |
| unsupported composition types still rejected | `tests/test_validate_strategy_specs.py` | satisfied |
| base restriction preserved | `tests/test_validate_strategy_specs.py` | satisfied |
| parameter restriction preserved | `tests/test_validate_strategy_specs.py` | satisfied |
| `(0,1)` bound preserved | `tests/test_validate_strategy_specs.py` | satisfied |
| nesting remains forbidden | `tests/test_validate_strategy_specs.py` | satisfied |
| compiler not modified | changed-file list | satisfied |
| compiler boundary remains fail-closed until 01c | compiler tests / no compiler diff | satisfied |
| no Strategy Specs/artifacts touched | changed-file list | satisfied |
| required validation run | validation summary | satisfied |
| PR body/status finality clean | PR body + status fragment | satisfied |
| no forbidden paths touched | diff scope | satisfied |

- Merge status: PR #431 is open and ready for review; final mergeability status is checked in PR metadata.
- Next authority: After this PR merges cleanly, Side may prepare `WP-COMP-PLUSCOMP-01c` only from refreshed `origin/main`, with no competing `docs/project_status.md` PR open and with compiler-only scope.
