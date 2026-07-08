# Repo Truth Discovery

## Fact

- Base branch at package start: `origin/main` at `3d5eb0632b99d002b83e210089a65b7a2073eb02`.
- Open PR preflight returned no open PRs.
- `tools/research_agents/formalizer_runner_bridge.py` is the current formalizer-runner bridge module.
- `FormalizerRunnerBridge.__init__` rejects ToolContext role/WP combinations outside role `formalizer_runner_bridge` and the existing bridge, Donchian adapter, and funding research WP IDs.
- The bridge output root is computed as `scratch/<tool_context.wp_id>/outputs`.
- The bridge formalizer source validation accepts only legacy formalizer scratch prefixes.
- The bridge approval contract expects `approved_by = operator`, `approved_for_noncanonical_runner_bridge = true`, `approval_scope = noncanonical_scratch_runner_bridge_only`, a timestamp, and matching source formalizer run ID.
- The bridge derives Strategy Spec, Variant Manifest, Sweep Plan, and bridge metadata artifacts under its output root, validates them, writes a denominator ledger and human review packet, and invokes the offline runner when unblocked.
- `tools/agent_sandbox/permissions.py` grants `RUN_NONCANONICAL_OFFLINE_SWEEP` to role `formalizer_runner_bridge` and scopes noncanonical offline sweep targets under active WP outputs.
- `tools/lab_pipeline/model.py` defines a separate product approval shape: `approved_by = Karl`, `approval_scope = noncanonical_offline_research_execution_only`, exact statement, prereg packet hash binding, and false flags for canonical/candidate/runtime/scheduler/notification authority.
- `tools/lab_pipeline/adapter_contract.py` records `bridge_spec_variant_sweep_preparation` as blocked by ToolContext, source-prefix, output-root, and legacy approval shape.
- `tests/test_lab_pipeline_bridge_adapter.py` proves current bridge rejection of the lab pipeline package ToolContext, package-local formalizer prefix, product output-root expectation, and Karl hash-bound approval shape.
- `docs/research/LAB_PRODUCTIZATION_PIPELINE_BRIDGE_ADAPTER.md` records WP03 Outcome B.

## Inference

- Product-side pre-bridge adaptation cannot preserve current product package-local scratch and Karl exact-content approval semantics without faking or bypassing legacy bridge constraints.
- The bridge code has separable preparation concepts, but current repo truth exposes no supported preparation-only mode.
- A safe product invocation path requires a deliberate bridge-contract change rather than adapter plumbing.

## Decision

Recommend an additive bridge product-mode contract plus an explicit bridge-preparation-only path. Preserve the legacy bridge behavior unchanged by default. Reject product-side bridge reimplementation.

## Open Questions

- Exact product-mode approval schema and whether it should be distinct from broad pipeline prereg approval.
- Exact product-mode ToolContext WP allowlist.
- Whether the product-mode output schema should reuse or version the bridge human review packet.
- Later runner consumption approval shape.
