# WP-COMP-BOTHDIR-01d - Implement both-direction compiler support

- Package class: T3 compiler + tests implementation
- Branch: `compiler/comp-bothdir-01d-both-direction`
- PR: https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/436
- Scope summary: Implements deterministic compiler support for locked closed `entry_logic.direction == "both"` semantics using explicit side-labeled root condition groups.
- Authorization basis: Main 5 locked both-direction semantics in `docs/research_pipeline/2026-06-both_direction_semantics_lock.md`; WP-COMP-BOTHDIR-01c merged schema and validator support in PR #435.
- Changed files:
  - `tools/research_runner/spec_signal_compiler.py`
  - `tests/test_spec_signal_compiler.py`
  - `docs/status_entries/WP-COMP-BOTHDIR-01d.md`
  - `docs/project_status.md`
- Implementation summary: The compiler now dispatches `direction == "both"` into a separate three-state single-stream state machine. It evaluates root `side == "long"` entry groups for long entries and root `side == "short"` entry groups for short entries, applies unlabeled filters to both sides, rejects schema-bypass side-label violations, stays flat when both entries fire while flat, applies exits only for the held side, prevents same-bar or in-position opposite-side reversals, and preserves max-holding behavior for the current side. Existing `long` and `short` direction paths remain unchanged.
- Validation summary:
  - `python -m pytest tests/test_spec_signal_compiler.py -q`: pass, 124 passed.
  - `python -m pytest tests/test_validate_strategy_specs.py -q`: pass, 72 passed.
  - `python -m tools.registry.validate_strategy_specs`: pass.
  - `python -m tools.registry.validate_result_populations`: pass.
  - `python -m tools.research_query.run --list-views`: pass.
  - All discovered `v_integrity_*` views: pass, 55 clean / zero rows.
  - `python tools/dev/diff_scope_summary.py`: pass; tracked changes were limited to compiler and compiler tests before status files were added.
  - `python -m pytest -q`: environment-only failure, 1312 passed / 1 failed / 6 warnings. The failure is `tests/test_backtest_liquidation.py::test_buy_and_hold_unchanged_on_benign_window`, which requires gitignored local file `data/processed/binance_um_perp_BTCUSDT_4h_2020-01-01_2026-04-11_2026-04-12T1655Z.parquet` that is absent from the isolated worktree.
  - Additional diagnostic coverage: `tests/test_backtest_liquidation.py -q -k "not buy_and_hold_unchanged_on_benign_window"` passed, 14 passed / 1 deselected; per-file pytest runs for top-level non-liquidation test files passed after allowing slow query tests enough time.
- Boundary summary: No schema, validator, catalog, Strategy Spec, variant manifest, sweep plan, result population, dashboard, data acquisition, simulator, runtime, paper/live, OMS/risk, broker/exchange, or protected-path files were modified.
- Active-WP requirement traceability:

| Requirement | Evidence | Status |
|---|---|---|
| direction both compiles | compiler dispatch + `test_both_direction_enters_long_from_long_side_group` | satisfied |
| explicit long side groups evaluated | `_split_root_side_groups`; long entry tests | satisfied |
| explicit short side groups evaluated | `_split_root_side_groups`; short entry tests | satisfied |
| no compiler mirroring | side-split compiler structure + entry-side tests | satisfied |
| single-stream mutual exclusivity | `test_both_direction_emits_single_stream_mutually_exclusive_values` | satisfied |
| simultaneous fire while flat stays flat | `test_both_direction_simultaneous_long_short_entry_while_flat_stays_flat` | satisfied |
| long exits close long only | `test_both_direction_long_exit_only_closes_long` | satisfied |
| short exits close short only | `test_both_direction_short_exit_only_closes_short` | satisfied |
| opposite-side entry while long does not flip | `test_both_direction_opposite_entry_while_long_does_not_flip` | satisfied |
| opposite-side entry while short does not flip | `test_both_direction_opposite_entry_while_short_does_not_flip` | satisfied |
| same-bar exit plus opposite entry goes flat, not reversed | `test_both_direction_same_bar_exit_and_opposite_entry_goes_flat_not_reversed` | satisfied |
| max holding preserved for current side | `test_both_direction_respects_max_holding_for_current_side` | satisfied |
| no-lookahead preserved | `test_both_direction_preserves_no_lookahead` | satisfied |
| deterministic repeated compilation | `test_both_direction_repeated_calls_are_deterministic` | satisfied |
| existing long direction unchanged | `test_existing_long_direction_signal_unchanged` | satisfied |
| existing short direction unchanged | `test_existing_short_direction_signal_unchanged` | satisfied |
| crosses operators work under both direction | `test_both_direction_supports_crosses_above_below_conditions` | satisfied |
| plus/minus composed operands work under both direction | `test_both_direction_supports_plus_minus_composed_operands` | satisfied |
| schema/validator untouched | final changed-file list | satisfied |
| Strategy Specs/artifacts untouched | final changed-file list | satisfied |
| required validation run | validation summary in this fragment | satisfied |
| PR body/status finality clean | final PR readiness gate before review | satisfied |
| no forbidden paths touched | diff scope and changed-file list | satisfied |

- Merge status: PR #436 is open, non-draft, and GitHub reports `mergeable=MERGEABLE`.
- Next authority: After this PR merges, report the completed BOTHDIR runway back to Main 5 and ask Main 5 for the next direction.
