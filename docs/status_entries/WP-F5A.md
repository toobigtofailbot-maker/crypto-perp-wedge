# WP-F5A: Results dashboard_data contract and validator extension

**Package class:** F — Dashboard  
**Branch:** `dashboard/f5a-results-contract-validator`  
**PR:** https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/422

## Scope summary

Extends the `dashboard_data.v1` JSON schema contract and its validator, tests, and contract documentation to support an optional Results page. A future F5B collector can emit contract-valid data and a future F5C renderer can display it.

## Changed files

| File | Change |
|---|---|
| `research/schemas/dashboard_data.schema.json` | Added optional `pages.results` property and 8 new definitions: `results_page`, `results_result_population`, `results_complete_population`, `results_descriptive_summary`, `results_variant_table`, `results_variant_row`, `results_backtest_assumptions`, `results_non_authority_notes` |
| `tools/dashboard/validate_dashboard_data.py` | Added `RESULTS_ADDITIONAL_FORBIDDEN_KEYS`, `RESULTS_REQUIRED_ORDER_POLICY`, `_validate_results_page()`, wired into `validate_dashboard_data_file` |
| `tests/fixtures/dashboard/valid_dashboard_data_with_results.json` | New: valid fixture with `pages.results` populated from RP-4492 data (7 variants, ascending order). Follow-up PR #422: replaced row-singling-out observation with population-level wording |
| `tests/fixtures/dashboard/invalid_dashboard_data_results_authority.json` | New: invalid fixture with `outcome_category: "best_variant"` — caught by global `FORBIDDEN_AUTHORITY_VALUES` |
| `tests/fixtures/dashboard/invalid_dashboard_data_results_ordering.json` | New: invalid fixture with VAR-000002 before VAR-000001 — caught by Results ordering validator |
| `tests/test_validate_dashboard_data.py` | Added `RESULTS_FIXTURE`, `_load_results()`, 5 new tests (initial). Follow-up PR #422: added `test_results_specific_forbidden_key_fails` directly exercising `_validate_results_page` Results-specific key check with `leaderboard`. Imports `_validate_results_page` directly to bypass early schema exit. 21 tests total. |
| `docs/architecture/2026-06-dashboard_data_contract.md` | Added Results page section |
| `docs/project_status.md` | Appended compact WP-F5A pointer |

## Validation summary (PR #422 follow-up)

```
git status --short
 M tests/fixtures/dashboard/valid_dashboard_data_with_results.json
 M tests/test_validate_dashboard_data.py

git diff --check
(clean — no whitespace errors)

python -m tools.dashboard.validate_dashboard_data tests/fixtures/dashboard/valid_dashboard_data_minimal.json
OK: tests\fixtures\dashboard\valid_dashboard_data_minimal.json validates as dashboard_data.v1

python -m tools.dashboard.validate_dashboard_data tests/fixtures/dashboard/valid_dashboard_data_with_results.json
OK: tests\fixtures\dashboard\valid_dashboard_data_with_results.json validates as dashboard_data.v1

python -m pytest tests/test_validate_dashboard_data.py -q
21 passed in 0.98s

python -m pytest tests/test_generate_static_dashboard.py -q
11 passed in 3.77s

python -m tools.registry.validate_result_populations
OK: result-population artifacts under .../research/result_populations validate

v_integrity_result_population_authority_key_violation: (no rows)
v_integrity_result_population_denominator_mismatch: (no rows)
v_integrity_result_population_outcome_count_mismatch: (no rows)
v_integrity_result_population_parent_hash_chain_mismatch: (no rows)

python -m pytest -q (full suite)
17 collection errors — all pre-existing environment issues (pandas/numpy/binance not installed
in worktree): test_backtest, test_backtest_liquidation, test_binance_perp_realism,
test_catalog_binance_usdtm_15m, test_evaluation, test_evaluation_cost_drag,
test_import_binance_usdtm_15m, test_offline_research_runner, test_paper_scheduler,
test_paper_trader_once, test_paper_trader_position_flow, test_paper_trader_price_ref_flow,
test_paper_trader_signal_flow, test_price_ref_provider, test_spec_signal_compiler,
test_validate_binance_usdtm_15m, scripts/g4_api_smoke_test.
All errors are ModuleNotFoundError for pandas/numpy/binance — none are caused by F5A changes.
Installable-environment suite: see below.
```

Installable-environment pytest (pandas/numpy-dependent tests excluded, all others collected):
— result pending background run; to be updated when complete.

## Boundary summary

WP-F5A does **not**:
- Make `pages.results` required (no collector yet)
- Implement collector (`tools/dashboard/collector.py` unchanged)
- Implement renderer (`tools/dashboard/renderer.py` unchanged)
- Generate dashboard output
- Mutate result-population artifacts or any data under `research/result_populations/`
- Add ranking, recommendation, readiness, promotion, execution, or approval authority
- Contact runtime, paper/live, broker/exchange, OMS, or risk systems
- Modify `AGENTS.md`, `CLAUDE_START_HERE.md`, `.claude/README.md`, `docs/runbook.md`, strategy specs, variant manifests, sweep plans, or any protected path

## Merge status

PR #422 open: https://github.com/toobigtofailbot-maker/crypto-perp-wedge/pull/422

## Next dependency note

F5B (collector) may be drafted after this contract is merged. F5C (renderer) remains gated on F5B and separate Main authorization.
