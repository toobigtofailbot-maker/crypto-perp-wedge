# WP-LABPROD-BRIDGE-PRODUCT-MODE-IMPLEMENT-01B Repo-Truth Discovery

## Branch / Base

- Branch: `codex/wp-labprod-bridge-product-mode-implement-01b`
- Refreshed base: `origin/main` at `3c26aa7c90cf4c5d99bb0869725b10be7c988f21`
- Local `main` was fast-forwarded before branch creation.
- Open PR collision check: `gh pr list --state open --json number,title,headRefName,baseRefName,files --limit 100` returned `[]`.
- Suggested package branch did not exist locally or remotely before creation.

## Bridge Class / Config Names

- Bridge module: `tools/research_agents/formalizer_runner_bridge.py`
- Bridge class: `FormalizerRunnerBridge`
- Bridge config: `FormalizerRunnerBridgeConfig`
- Bridge role: `formalizer_runner_bridge`
- Legacy bridge version constant: `formalizer-runner-bridge-v1`

## Current Legacy Accepted Role / WP List

The current legacy constructor accepts only role `formalizer_runner_bridge` with one of:

- `WP-AGENT-FORMALIZER-RUNNER-BRIDGE-01`
- `WP-AGENT-ADAPTER-DONCHIAN-FAMILY-01`
- `WP-RESEARCH-FUNDING-CARRY-02`

Unsupported WP IDs raise `ValueError("FormalizerRunnerBridge requires its exact ToolContext role and WP")`.

## Current Legacy Approval Parser Shape

Legacy `_require_approval` requires:

- approval path colocated with the formalizer output directory;
- `approved_for_noncanonical_runner_bridge = true`;
- `approved_by = operator`;
- `approval_scope = noncanonical_scratch_runner_bridge_only`;
- nonempty string `approval_timestamp_utc`;
- matching `source_formalizer_run_id`;
- when `funding_cost_mode = on`, `approved_funding_cost_mode = on`.

Failure attempts `approval_gate_bypass`, which is hard-blocked by `ToolContext`.

## Current Source-Prefix Validation

Legacy `_validate_formalizer_contract` accepts only `formalized_idea.json` under:

- `scratch/WP-AGENT-IDEA-FORMALIZER-01/outputs/`
- `scratch/WP-AGENT-ADAPTER-DONCHIAN-FAMILY-01/formalizer/outputs/`
- `scratch/WP-RESEARCH-FUNDING-CARRY-02/outputs/`

It also requires schema `agent_formalized_idea_v1`, status `accepted`, nonempty `run_id`, BTCUSDT/15m research object, supported family features, produced draft Strategy Spec, scratch-only non-authority, and family adapter metadata where applicable.

## Current Output-Root Derivation

Legacy constructor sets:

```text
self.output_root = Path("scratch") / tool_context.wp_id / "outputs"
```

Legacy default output root is therefore `scratch/<tool_context.wp_id>/outputs`.

## Current Runner Invocation Location

Runner boundary is `_invoke_runner`, which calls `tools.research_runner.run_offline_sweep` through `ToolAction(RUN_NONCANONICAL_OFFLINE_SWEEP, ...)`.

Legacy `run()` invokes `_invoke_runner` twice when no availability blockers exist:

- bridged run with `write_result_population=True`;
- direct manual-equivalent run with `write_result_population=False`.

## Current Validator Calls

Bridge-owned validators are:

- draft Strategy Spec: `validate_strategy_specs`
- derived Strategy Spec: `validate_strategy_specs`
- derived Variant Manifest / Sweep Plan: `validate_variant_sweep_artifacts`

Both validator calls are routed through `RUN_READ_ONLY_VALIDATION`.

## Current Denominator / Review Outputs

Legacy `run()` writes:

- `formalizer_runner_bridge_denominator_ledger_v1`
- `formalizer_runner_bridge_human_review_packet_v1`

Ledger rows preserve trial denominator status and non-authority flags. Review packet records derived inputs, runner metadata, denominator counts, reconciliation result, runner artifact paths, funding mode, blockers, and non-authority flags.

## Current ToolContext Permission Model

`tools/agent_sandbox/permissions.py` grants role `formalizer_runner_bridge`:

- `read_non_secret_files`
- `write_scratch`
- `run_read_only_validation`
- `noncanonical_offline_sweep_run`

`ToolContext` casefolds normalized target paths before policy evaluation. Writes are restricted to `scratch/<wp_id>/`. Noncanonical offline sweep targets are restricted to `scratch/<wp_id>/outputs/`. Canonical write prefixes and protected runtime prefixes are hard-blocked.

## Lab Product Approval Marker Shape / Exact-Content Conventions

Current lab product prereg approval idiom is `lab_pipeline_prereg_approval_v1` with:

- `approved_by = Karl`
- `approval_scope = noncanonical_offline_research_execution_only`
- exact approval statement from `tools/lab_pipeline/model.py`
- preregistration packet SHA binding
- explicit false authority flags for canonical write, candidate lifecycle, paper/live runtime, scheduler/autonomy, and notifications

Repo truth before this package did not define product bridge stale-window semantics. Karl's package decision now defines stale approval as content/path/hash/run/stage/output-root/authority mismatch only, with timestamp required for audit and no wall-clock expiry.

## Product-Local Scratch Conventions

Lab product adapter output root defaults to:

```text
scratch/WP-LABPROD-PIPELINE-BRIDGE-ADAPTER-03/outputs
```

Product bridge mode must use package-local scratch roots of the same shape, not legacy bridge scratch. Paths must remain repo-relative and under the active product package scratch root.

## Current Tests That Must Remain Passing

Focused existing tests:

- `tests/test_agent_formalizer_runner_bridge.py`
- `tests/test_lab_pipeline_bridge_adapter.py`

Package validation also requires:

- `tests/test_lab_pipeline*.py`
- registry validators
- query view listing
- full pytest when feasible

## Exact Deterministic Fixtures Available For Byte Regression

`tests/test_agent_formalizer_runner_bridge.py` provides deterministic helpers:

- `_setup_source`
- `_write_ohlcv_fixture`
- `_copy_templates`
- fixed ToolContext clock `2026-06-22T01:02:03Z`
- deterministic bridge config timestamp default `2026-06-22T00:00:00Z`

The approved legacy test `test_approved_bridge_runs_real_runner_and_reconciles` exercises the unblocked runner path and validates derived artifacts, denominator ledger, human review packet, runner result artifact, and audit permission.

## Volatile Fields That May Prevent Byte-For-Byte Comparison

The legacy run identity is content-derived from formalizer bytes, approval bytes, draft hashes, OHLCV hash, config, and bridge version. With fixed tmp-path content and fixed config, output paths and JSON payloads are expected deterministic.

No repo-truth normalizer is needed for the focused legacy fixture. If future broader comparisons encounter nondeterministic absolute paths, timestamps, or UUIDs, package rules require stopping rather than inventing normalization.

## Karl Stale-Approval Decision Mapping

Product mode must:

- require a parseable timestamp string for audit;
- perform no wall-clock comparison;
- reject mismatch in actor, scope, exact statement, source product packet path/hash, source formalizer output path/hash, approval marker content/hash, source formalizer run id, product/pipeline run id, bridge stage identity, output root, required true bridge-preparation authority, required false runner authority, and all required false protected authority flags.

This maps to a bridge-owned product approval validator that is separate from legacy `_require_approval`, plus product-mode path/hash binding before derived artifacts are written.
