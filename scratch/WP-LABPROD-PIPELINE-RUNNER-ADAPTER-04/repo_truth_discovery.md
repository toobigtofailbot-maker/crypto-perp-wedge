# WP-LABPROD-PIPELINE-RUNNER-ADAPTER-04 Repo Truth Discovery

## Branch / Base

- Branch: `codex/wp-labprod-pipeline-runner-adapter-04`
- Base: `origin/main`
- Base SHA: `0e968f67dfce783950fd02f79dd772c5b53599e1`
- Open PR collision check: `gh pr list --state open --limit 100 --json number,title,headRefName,baseRefName,files` returned `[]`.

## Lab Pipeline Adapter Registry

- Registry location: `tools/lab_pipeline/adapter_contract.py`.
- Orchestrator location: `tools/lab_pipeline/orchestrator.py`.
- Adapter flow location: `tools/lab_pipeline/adapters.py`.
- Current placeholder: `build_adapter_registry()` records `noncanonical_offline_runner_execution` as blocked with source module `tools.research_runner.run_offline_sweep` and callable `run_offline_sweep`.
- Current bridge placeholder: `bridge_spec_variant_sweep_preparation` remains blocked for the old adapter package because the legacy bridge could not satisfy product-local approval/output/no-runner constraints.

## Bridge Product Prepare-Only Shape

- Bridge implementation: `tools/research_agents/formalizer_runner_bridge.py`.
- Product mode: `PRODUCT_BRIDGE_INVOCATION_MODE = product_bridge_prepare_only`.
- Product prepare WP: `WP-LABPROD-BRIDGE-PRODUCT-MODE-IMPLEMENT-01B`.
- Product bridge stage identity: `bridge_spec_variant_sweep_preparation`.
- Product bridge approval schema: `product_bridge_preparation_approval_v1`.
- Product bridge output root: `scratch/WP-LABPROD-BRIDGE-PRODUCT-MODE-IMPLEMENT-01B/outputs`.
- Product prepare-only result status: `prepared`.
- Product prepare-only result artifact paths include:
  - `artifact_paths.strategy_spec`
  - `artifact_paths.variant_manifest`
  - `artifact_paths.sweep_plan`
  - `artifact_paths.denominator_ledger`
  - `artifact_paths.human_review_packet`
  - `artifact_paths.runner_result = null`
  - `artifact_paths.runner_results = {}`
  - `artifact_paths.input_sets`
- Product human review packet records `runner_invocation_metadata.runner_invoked = false`, `runner_boundary = not_requested`, and `runner_artifact_paths = []`.
- Product human review packet records `product_bridge_preparation_metadata` with source product packet path/hash, source formalizer output path/hash, approval marker path/hash/content hash, product pipeline run id, bridge stage identity, product output root, stale approval policy, and `runner_execution_authorized = false`.

## Offline Runner Contract

- Existing runner entry point: `tools/research_runner/run_offline_sweep.py`.
- Callable: `run_offline_sweep(strategy_spec_path, variant_manifest_path, sweep_plan_path, output_dir=None, *, write_result_population=False, run_label=None, deterministic_seed=0, canonical_15m=False, canonical_4h=False, ohlcv_input_path=None, ...)`.
- CLI: `python -m tools.research_runner.run_offline_sweep --strategy-spec ... --variant-manifest ... --sweep-plan ...`.
- Writer behavior: with `write_result_population=True`, runner requires `output_dir` and writes `<result_population_id>.result_population.json`.
- Canonical guard: runner rejects writes under `research/result_populations`.
- Direct invocation with only Strategy Spec / Variant Manifest / Sweep Plan is allowed by the current function contract. Canonical real-data execution requires additional explicit runner flags/paths, but those are not required for the runner to emit a full Result Population-shaped denominator.
- Runner validates Strategy Specs, Variant Manifests, Sweep Plans, and Result Populations through existing validators before returning/writing.

## Result Population Schema / Validator

- Validator: `tools/registry/validate_result_populations.py`.
- Default canonical directory: `research/result_populations`.
- Validator accepts an explicit scratch `result_populations_dir` with parent input directories.
- Outcome categories: `successful`, `failed`, `invalid`, `excluded`, `errored`, `aborted`, `filtered`, `data_unavailable`, `not_attempted`.
- Denominator expectations require parent manifest/sweep counts, result row count, outcome count sum, complete population rows, non-authority declaration, audit envelope, append-only ledger, and identity hash validity.

## Denominator Status Handling

- Existing bridge trial statuses: `completed`, `failed`, `invalid`, `pruned`, `blocked`.
- Existing bridge runner mapping:
  - `successful -> completed`
  - `failed -> failed`
  - `invalid -> invalid`
  - `excluded` / `filtered -> pruned`
  - `errored` / `aborted` / `data_unavailable` / `not_attempted -> blocked`
- Product runner adapter should preserve the runner Result Population rows and produce status counts in that same allowed status vocabulary without winner narrowing.

## Approval / Exact-Content Marker Idiom

- Pipeline prereg approval is `lab_pipeline_prereg_approval_v1` and cannot authorize bridge product preparation or runner execution.
- Bridge product preparation approval is `product_bridge_preparation_approval_v1` and explicitly sets `authorizes_runner_execution = false`.
- Bridge product stale-approval semantics are content-bound: timestamp is required for audit syntax, with no wall-clock expiry.
- Runner execution in this package needs a separate execute approval marker bound to prepared Strategy Spec / Variant Manifest / Sweep Plan path+hash, bridge preparation run id, product pipeline run id, runner adapter stage identity, and product output root.

## ToolContext Permission

- `tools/agent_sandbox/permissions.py` grants `formalizer_runner_bridge` the `noncanonical_offline_sweep_run` action.
- `RUN_NONCANONICAL_OFFLINE_SWEEP` is allowed only under `scratch/<active wp id>/outputs/`.
- The runner adapter can use a `ToolContext` with package WP `WP-LABPROD-PIPELINE-RUNNER-ADAPTER-04` and role `formalizer_runner_bridge` to audit the noncanonical offline sweep target under its package-local scratch output root.
- No permission file change is required.

## Direct-Runner Reconciliation

- Repo-defined normalization exists at `tools/research_replay/normalization.py`.
- `compare_result_populations()` compares normalized Result Population payloads and is explicitly read-only.
- Raw byte equality is possible when the same runner inputs/options produce identical payloads; normalization is available in repo truth for path spelling and audit-envelope variance if needed.

## Deterministic / Volatile Fields

- Runner `run_label` only appears in `audit_envelope.operator_notes`, outside scientific identity.
- Runner audit timestamps use fixed `FIXED_AUDIT_TIMESTAMP`.
- Result Population identity includes parent identities, runner identity, data identity, denominator, rows, outcome counts, append-only creation event ref, validation identity, and optional sizing/data-availability metadata.
- Output directory path is not embedded in the Result Population payload by the current runner.

## Files That Must Remain Untouched

- `tools/research_agents/formalizer_runner_bridge.py` is read-only for this package.
- `tools/research_runner/**` is read-only for this package.
- `tools/registry/**` validators and schemas are read-only for this package.
- `research/result_populations/**`, `research/strategy_specs/**`, `research/variant_manifests/**`, and `research/sweep_plans/**` are read-only.
- `src/**`, `lib/**`, `configs/**`, `.claude/**`, `data/**`, runtime, OMS, risk, reconciliation, paper/live, scheduler, notification, provider/API, dependency/config/data-acquisition paths are forbidden.
