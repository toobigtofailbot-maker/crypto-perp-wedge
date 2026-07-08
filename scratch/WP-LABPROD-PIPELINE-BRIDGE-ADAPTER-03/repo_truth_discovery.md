# Repo Truth Discovery

## Fact

- `FormalizerRunnerBridge.__init__` rejects ToolContext WP IDs outside its
  existing bridge / Donchian / funding allowlist.
- The bridge output root is `scratch/<tool_context.wp_id>/outputs`.
- The bridge formalizer input contract accepts only existing formalizer scratch
  prefixes.
- The bridge approval contract expects `approved_by = operator` and
  `approved_for_noncanonical_runner_bridge = true`.
- The package requires package-local bridge outputs and a Karl-signed,
  exact-content-bound bridge approval marker.
- The bridge can invoke `tools.research_runner.run_offline_sweep` on its
  unblocked path.

## Inference

Adapting the bridge from the lab pipeline would require modifying the bridge's
ToolContext, scratch-prefix, output-root, approval, or runner-invocation
contract.

## Decision

Do not invoke the bridge in this package. Preserve the adapter gap and record an
Outcome B blocker.

## Open Question

Whether a future bridge-contract package should add a lab-pipeline no-runner
adapter mode.
