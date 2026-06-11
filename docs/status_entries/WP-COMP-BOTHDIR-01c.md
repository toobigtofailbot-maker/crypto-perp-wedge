# WP-COMP-BOTHDIR-01c - Add both-direction schema validator support

- Package class: T3 schema + validator + tests implementation
- Branch: `schema/comp-bothdir-01c-validator`
- PR: https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/435
- Scope summary: Adds closed Strategy Spec schema and validator support for explicit long/short side-labeled condition groups under `entry_logic.direction == "both"` while preserving existing single-direction long/short behavior.
- Authorization basis: Main 5 locked both-direction semantics in `docs/research_pipeline/2026-06-both_direction_semantics_lock.md`; this package is the gated WP-COMP-BOTHDIR-01c schema + validator + tests package after WP-COMP-BOTHDIR-01b merge.
- Changed files:
  - `research/schemas/strategy_spec.schema.json`
  - `tools/registry/validate_strategy_specs.py`
  - `tests/test_validate_strategy_specs.py`
  - `docs/status_entries/WP-COMP-BOTHDIR-01c.md`
  - `docs/project_status.md`
- Implementation summary: Adds the closed `side` enum field (`long`, `short`) to reusable condition-group schema definitions; validator logic requires long and short root entry groups for `direction: "both"`, requires side-labeled root exits when exits are present under `both`, rejects filter side labels, rejects side labels for single-direction specs, and rejects nested side-label contradictions.
- Validation summary:
  - `python -m pytest tests/test_validate_strategy_specs.py -q`: pass, 72 passed.
  - `python -m pytest tests/test_spec_signal_compiler.py -q`: pass, 105 passed.
  - `python -m tools.registry.validate_strategy_specs`: pass.
  - `python -m tools.registry.validate_result_populations`: pass.
  - `python -m tools.research_query.run --list-views`: pass.
  - All discovered `v_integrity_*` views: pass, 55 clean / zero rows.
  - `python tools/dev/diff_scope_summary.py`: pass; tracked changes match the package files before status-fragment creation, with the authorized schema file reported as a generic `research/` match.
  - `python -m pytest -q`: environment-only failure, 1293 passed / 1 failed / 6 warnings; `tests/test_backtest_liquidation.py::test_buy_and_hold_unchanged_on_benign_window` requires gitignored `data/processed/binance_um_perp_BTCUSDT_4h_2020-01-01_2026-04-11_2026-04-12T1655Z.parquet`, which is absent from the isolated worktree.
- Boundary summary: No compiler implementation, compiler test edit, Strategy Spec mutation, variant manifest, sweep plan, result population, catalog, dashboard, data acquisition, simulator, runtime, paper/live, OMS/risk, broker/exchange, or protected-path change.
- Active-WP requirement traceability:

| Requirement | Evidence | Status |
|---|---|---|
| schema supports closed side labels | `research/schemas/strategy_spec.schema.json`; validator tests | satisfied |
| validator enforces closed side labels | `tools/registry/validate_strategy_specs.py`; validator tests | satisfied |
| both direction requires long root entry group | `test_both_direction_rejects_missing_long_entry_side` | satisfied |
| both direction requires short root entry group | `test_both_direction_rejects_missing_short_entry_side` | satisfied |
| both direction rejects unlabeled root entry group | `test_both_direction_rejects_entry_group_without_side` | satisfied |
| both direction rejects unknown side label | `test_both_direction_rejects_unknown_side_label` | satisfied |
| both direction rejects unlabeled exit group when exit group is present | `test_both_direction_rejects_unlabeled_exit_group` | satisfied |
| single-direction existing specs remain valid | long/short preservation tests | satisfied |
| single-direction side labels rejected or justified | single-direction reject tests | satisfied |
| depth <= 3 preserved | `test_both_direction_preserves_condition_group_depth_limit` | satisfied |
| closed operators preserved | `test_both_direction_preserves_closed_operator_validation` | satisfied |
| composed operand validation preserved | `test_both_direction_preserves_composed_operand_validation` | satisfied |
| compiler files untouched | final changed-file list | satisfied |
| Strategy Specs/artifacts untouched | final changed-file list | satisfied |
| required validation run | validation summary in this fragment | satisfied |
| PR body/status finality clean | final PR readiness gate | satisfied |
| no forbidden paths touched | diff scope and changed-file list | satisfied |

- Merge status: PR #435 is open, non-draft, and GitHub reports `mergeable=MERGEABLE`.
- Next authority: WP-COMP-BOTHDIR-01d compiler work remains unauthorized until this PR cleanly merges and a later package is drafted from refreshed `origin/main`.
