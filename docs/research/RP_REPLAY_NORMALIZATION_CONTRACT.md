# Result Population Replay Normalization Contract

## Purpose

This contract defines a reusable, family-agnostic way to compare Result Population replays without granting execution, ranking, candidate lifecycle, canonical crossing, paper/live, OMS, risk, reconciliation, or capital authority.

The contract is implemented by `tools.research_replay.normalization` and summarized by `tools/research_replay/replay_normalization_contract.schema.json`.

## Inputs

A replay comparison consumes an existing Result Population JSON artifact. The helper may also receive an operator-supplied runner command string for recording only. It does not run a strategy, call the offline runner, fetch data, write canonical evidence, or mutate research artifacts.

Pinned input identity fields:

- data identity: `data_coverage_summary.data_catalog_ref`, `data_coverage_summary.data_slice_identity`, timeframe, stream, and optional `data_availability_claim`
- Strategy Spec identity: `parent_strategy_spec.strategy_spec_id` and `parent_strategy_spec.strategy_spec_hash`
- Variant Manifest identity: `parent_variant_manifest.variant_manifest_id` and `parent_variant_manifest.manifest_hash`
- Sweep Plan identity: `parent_sweep_plan.sweep_plan_id` and `parent_sweep_plan.sweep_plan_identity_hash`
- runner identity: `execution_context.repo_commit`, `runner_code_ref`, `runner_version`, `determinism_seed`, offline/no-runtime flags, environment/dependency summaries, and optional recorded runner command
- declared RP identity hashes: `input_identity_hash` and `result_population_identity_hash`
- raw Result Population file hash when a file path is provided

## Normalized Stable Payload

The normalized stable hash is computed from a deterministic JSON projection using sorted keys and compact JSON separators. It includes:

- result population ID and status
- parent identities and portable artifact refs
- runner identity
- data identity
- declared identity hashes and scopes
- trial count
- variant IDs in row order
- outcome/status counts
- committed denominator snapshot
- metric set
- sizing metadata when present
- backtest assumption summary
- validator identity and status, excluding validation timestamp
- each result row's row ID, variant ID, row identity hash, assignment hash/ref, outcome, attempted flag, metrics, non-success/error/data coverage records, assumption ref, and parent lineage

## Allowed Normalization

Only deterministic, explicitly allowed fields may be normalized:

- administrative timestamps excluded from RP identity semantics, including audit-envelope timestamps, validation timestamps, and append-only event timestamps
- absolute local paths that resolve under the repo root, converted to repo-relative portable paths
- path separators converted to `/`
- JSON object key ordering, through canonical JSON serialization

The helper does not round floating metrics. Current repo truth has no general Result Population metric-precision convention beyond JSON canonicalization, so metric values are preserved exactly as parsed from JSON.

## Fail-Closed Behavior

Identity-bearing path fields and Result Population rows are normalized fail-closed:

- Absolute paths under the repo root are normalized to repo-relative paths.
- Relative paths normalize path separators only.
- Absolute paths outside the repo root fail closed unless a future separately authorized contract explicitly supports preserving them. They are not collapsed to a shared placeholder, because that would hide identity-bearing differences between distinct external paths.
- Malformed or non-object Result Population rows fail closed. Every entry in `variant_result_rows` must be an object; non-object entries are not silently skipped, because skipping would corrupt the trial count and row identity.

The helper must not normalize away row count, trial count, metrics, variant IDs, outcomes, failure reasons, denominator counts, or identity-bearing paths.

## Forbidden Normalization

The helper must not normalize away:

- metrics
- variant IDs
- trial outcomes
- row counts
- denominator counts
- failure reasons or error classifications
- input data hashes or data-slice identity
- Strategy Spec, Variant Manifest, or Sweep Plan hashes
- candidate state
- risk, capital, runtime, paper/live, OMS, reconciliation, broker/exchange, or safe-mode state

Any change to these fields changes the normalized stable hash.

## Hash Outputs

The contract distinguishes two hash classes:

- raw Result Population file hash: `sha256` over the exact file bytes, recorded as source evidence
- normalized stable hash: `sha256` over the normalized stable payload, used for replay-equivalence checks

The raw file hash is intentionally outside the normalized stable hash. This lets replay checks tolerate allowed administrative timestamp/path spelling differences while still recording the exact source bytes.

## Comparison Semantics

`compare_result_populations(left, right)` returns:

- whether the normalized stable hashes match
- both source paths and raw hashes when available
- field-family equality flags for trial count, variant IDs, status counts, denominator counts, metric set, parent identities, runner identity, data identity, and rows

A match means the compared Result Population artifacts are equivalent under this replay-normalization contract. It is not candidate approval, canonical crossing, promotion, ranking, recommendation, paper/live readiness, or execution authority.

## PR #563 Fixture Application

The first repo-resident application is the PR #563 scratch funding-family pair:

- `RP-2009`: `scratch/WP-RESEARCH-FUNDING-CARRY-02/outputs/813c51adc1879144/fixed_max_hold_only/runner_artifacts/RP-2009.result_population.json`
- `RP-7592`: `scratch/WP-RESEARCH-FUNDING-CARRY-02/outputs/813c51adc1879144/midline_reversion_or_max_hold/runner_artifacts/RP-7592.result_population.json`

Both normalize successfully under the contract. They intentionally do not match each other because they are different exit-mode populations with different parent identities, variant IDs, row identities, and metrics.
