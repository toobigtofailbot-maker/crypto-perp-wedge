# WP-LAB-RP-REPLAY-NORMALIZATION-CONTRACT-01 Repo-Truth Discovery

## Search Executed

Ran the package-required search over `docs/**/*.md`, `tools/**/*.py`, `tests/**/*.py`, `research/**/*.json`, and `scratch/**/*.json|md` for:

`Result Population|result_population|RP-|replay|determinism|normalization|hash|normalized stable metrics|trial_log|variant_id|strategy_spec|Variant Manifest|Sweep Plan|WP-RESEARCH-FUNDING-CARRY-02|RP-2009|RP-7592`

## Files Inspected

- `research/schemas/result_population.schema.json`
- `tools/registry/validate_result_populations.py`
- `tools/research_runner/run_offline_sweep.py`
- `tools/research_query/query_layer.py`
- `tools/research_query/run.py`
- `tests/test_validate_result_populations.py`
- `tests/test_offline_research_runner.py`
- `scratch/WP-RESEARCH-FUNDING-CARRY-02/rp_replay_harness_report.json`
- `scratch/WP-RESEARCH-FUNDING-CARRY-02/runner_result_summary.json`
- `scratch/WP-RESEARCH-FUNDING-CARRY-02/validation_summary.txt`
- `docs/status_entries/WP-RESEARCH-FUNDING-CARRY-02.md`
- PR #563 scratch Result Populations `RP-2009` and `RP-7592`

## Facts

- The Result Population schema is non-executing and records parent Strategy Spec, Variant Manifest, Sweep Plan, data identity, denominator snapshot, variant rows, outcome counts, identity hashes, audit envelope, and non-authority fields.
- The result-population validator already recomputes declared input and result identity hashes from the artifact's declared hash scopes.
- The offline runner writes deterministic Result Population payloads with sorted JSON and a fixed audit timestamp.
- The offline runner prevents canonical `research/result_populations` writes through its output-dir guard.
- The research query layer registers committed Result Populations read-only and must not write research artifacts.
- Prior packages explicitly recorded that no reusable repo-native exact RP replay command or canonical normalization contract existed.
- PR #563 added scratch-only replay proof for `RP-2009` and `RP-7592`, including input, parent, result, and normalized metrics hashes, but that proof was package-specific and not a reusable contract.

## Current Replay Gaps

- No reusable owned helper existed for stable replay-normalization summaries across Result Population families.
- No contract doc defined which RP fields may be normalized and which fields must remain hash-bearing.
- No fixture tests proved that metric, denominator, parent-hash, or path-portability changes behave as intended.
- PR #563's normalized metrics hash was a scratch proof, not a schema-backed, family-agnostic normalized payload.

## Decision

Continue with owned-file-only implementation:

- add `tools/research_replay/**`
- add `tests/test_research_replay*.py`
- add `docs/research/RP_REPLAY_NORMALIZATION_CONTRACT.md`
- add package scratch/status artifacts

No conditional files are required. `tools/registry/validate_result_populations.py` and `tests/test_validate_result_populations.py` remain untouched.
