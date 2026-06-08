# WP-D5C - Result-Population Identity Collision Fix

## Scope

D5C changes result-population identity semantics only. It updates the build-and-test-only offline runner so `result_population_id` derivation includes execution/data provenance while preserving the existing result-population schema and committed corpus.

## Changed Files

- `tools/research_runner/run_offline_sweep.py`
- `tests/test_offline_research_runner.py`
- `docs/status_entries/WP-D5C.md`
- `docs/project_status.md`

## Root Cause

The runner previously derived `result_population_id` from parent Strategy Spec hash, parent manifest hash, parent sweep hash, and backtest assumptions only. Fixture-backed and real-D4-backed canonical 15m populations with the same parents and assumptions could therefore collide even though their result-population metadata later recorded different data provenance.

## Identity Fix

The runner now includes these additional runner-derived identity inputs in deterministic `result_population_id` generation:

- `data_slice_identity`
- D3 validation identity / validation report hash when present
- `execution_provenance_class`

The first explicit classes are:

- `fixture_offline`
- `canonical_real_data`

The class is recorded through the existing schema-supported `execution_context.environment_summary` field. No result-population schema change was needed.

## Proof Points

- Fixture-backed canonical 15m dry run and D4-provenance canonical 15m dry run with the same parents, assumptions, and synthetic test OHLCV now produce distinct IDs: fixture `RP-1588`, D4 provenance `RP-4492`.
- Repeated D4-provenance dry runs with identical inputs produce the same ID: `RP-4492`.
- D4 provenance output continues to record the D4 catalog ref, D4 slice identity, D3 validation hash, D2 import report hash, D4 catalog artifact hash, and contains no `csv_fixture:` data slice identity.
- Existing committed fixture corpus remains validator-clean.

## Boundary

D5C does not write D5, does not mutate existing evidence, does not rename or modify `RP-2134`, does not interpret results, does not authorize paper/live, and does not touch runtime/protected paths.
