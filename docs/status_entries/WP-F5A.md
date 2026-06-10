# WP-F5A: Results dashboard_data contract and validator extension

**Package class:** F — Dashboard  
**Branch:** `dashboard/f5a-results-contract-validator`  
**PR:** (to be added on merge)

## Scope summary

Extends the `dashboard_data.v1` JSON schema contract and its validator, tests, and contract documentation to support an optional Results page. A future F5B collector can emit contract-valid data and a future F5C renderer can display it.

## Changed files

| File | Change |
|---|---|
| `research/schemas/dashboard_data.schema.json` | Added optional `pages.results` property and 8 new definitions: `results_page`, `results_result_population`, `results_complete_population`, `results_descriptive_summary`, `results_variant_table`, `results_variant_row`, `results_backtest_assumptions`, `results_non_authority_notes` |
| `tools/dashboard/validate_dashboard_data.py` | Added `RESULTS_ADDITIONAL_FORBIDDEN_KEYS`, `RESULTS_REQUIRED_ORDER_POLICY`, `_validate_results_page()`, wired into `validate_dashboard_data_file` |
| `tests/fixtures/dashboard/valid_dashboard_data_with_results.json` | New: valid fixture with `pages.results` populated from RP-4492 data (7 variants, ascending order) |
| `tests/fixtures/dashboard/invalid_dashboard_data_results_authority.json` | New: invalid fixture with `outcome_category: "best_variant"` — caught by global `FORBIDDEN_AUTHORITY_VALUES` |
| `tests/fixtures/dashboard/invalid_dashboard_data_results_ordering.json` | New: invalid fixture with VAR-000002 before VAR-000001 — caught by Results ordering validator |
| `tests/test_validate_dashboard_data.py` | Added `RESULTS_FIXTURE`, `_load_results()`, and 5 new tests |
| `docs/architecture/2026-06-dashboard_data_contract.md` | Added Results page section |
| `docs/project_status.md` | Appended compact WP-F5A pointer |

## Validation summary

- 20/20 pytest tests pass (`tests/test_validate_dashboard_data.py`)
- Validation profile: T3 implementation with full pytest
- Schema meta-valid (`Draft7Validator.check_schema`)
- Minimal fixture still passes (no regression)
- Valid results fixture passes
- Invalid authority and ordering fixtures each produce at least one error

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

Pending PR review.

## Next dependency note

F5B (collector) may be drafted after this contract is merged. F5C (renderer) remains gated on F5B and separate Main authorization.
