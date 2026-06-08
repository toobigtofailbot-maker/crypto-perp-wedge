# WP-D5C / Data Block 1 - Result-population identity collision fix

## Branch / PR

- Branch: `codex/wp-d5c-result-population-identity`
- PR: `#414`

## Package Class

T3 runner identity-semantics fix / canonical-evidence blocker-resolution package.

## Scope Summary

D5C changes deterministic `result_population_id` semantics only. It includes data/execution provenance in the runner-derived ID basis. It does not write D5.

## Changed Files

- `tools/research_runner/run_offline_sweep.py`
- `tests/test_offline_research_runner.py`
- `docs/status_entries/WP-D5C.md`
- `docs/project_status.md`

## Root Cause

The runner previously derived `result_population_id` from parent Strategy Spec hash, parent manifest hash, parent sweep hash, and backtest assumptions only. Fixture-backed and real-D4-backed canonical 15m populations with the same parents and assumptions could therefore collide even though their result-population metadata later recorded different data provenance.

## Identity Basis

The deterministic runner-derived `result_population_id` basis now includes:

- parent strategy hash
- parent manifest hash
- parent sweep hash
- backtest assumptions
- `data_slice_identity`
- D3 validation identity / validation report hash where present
- `execution_provenance_class`

## Execution Provenance Classes

- `fixture_offline`
- `canonical_real_data`

## Schema Caveat

No result-population schema change was needed. `execution_provenance_class` is implemented as a runner-internal identity input and recorded through existing schema-supported `execution_context.environment_summary`. If future work requires a schema-level identity-bearing field, that must be a separate reviewed schema package.

## Proof Points

- Fixture-backed canonical 15m dry run and D4-provenance canonical 15m dry run with same parents/assumptions produce distinct IDs: fixture `RP-1588`, D4 provenance `RP-4492`.
- Identical D4-provenance dry runs produce the same stable ID: `RP-4492`.
- Existing fixture corpus remains validator-clean / preserved.
- D4 provenance still records D4 catalog ref, D4 slice identity, D3 validation hash, D2 import report hash, D4 catalog artifact hash, and no fixture data slice identity.
- `RP-2134` remains untouched.

## Validation Summary

- `git diff --check`: pass
- `python -m pytest tests/test_offline_research_runner.py -q`: 41 passed
- `python -m pytest tests/test_validate_result_populations.py -q`: 42 passed
- `python -m tools.registry.validate_result_populations`: pass
- `python -m tools.research_query.run --list-views`: pass
- `v_integrity_*`: clean, 55 views
- `python tools/dev/diff_scope_summary.py`: pass, no forbidden-path matches
- `python -m pytest -q`: 1228 passed
- `git diff --cached --check`: pass
- `git diff --cached --name-only`: expected changed files only

## Boundary Summary

- no D5 result population write
- no mutation/replacement/deletion/rename of `RP-2134`
- no result-population schema change
- no D4A/D3/D2 artifact mutation
- no Strategy Spec / variant manifest / sweep plan mutation
- no interpretation/ranking/readiness/promotion
- no paper/live/runtime/protected paths

## Merge Status

Pending PR `#414`.

At final follow-up readiness check:

- GitHub reports `mergeable=true`.
- PR is not draft.
- PR title begins with `D5C:`.

## Next Dependency / Runway Note

After D5C merges cleanly, retry D5 from preflight under existing Karl-gated D5 authorization. D5 remains separate. D5 must create exactly one canonical real-data result population. D5 requires mandatory Main/Karl report-back after merge. Post-D5 descriptive interpretation/checkpoint follows only after D5 lands and report-back is accepted. F5 follows after the descriptive interpretation/checkpoint pack, per Main.
