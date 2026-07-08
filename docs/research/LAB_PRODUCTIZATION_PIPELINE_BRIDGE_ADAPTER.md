# Lab Productization Pipeline Bridge Adapter

## Outcome

`WP-LABPROD-PIPELINE-BRIDGE-ADAPTER-03` records **Outcome B**: the
`bridge_spec_variant_sweep_preparation` stage cannot be safely made
adapter-backed from current repo truth without changing the existing
formalizer-runner bridge contracts.

No bridge module invocation path is added. No runner execution path is added.
Downstream runner, WFO/OOS, robustness, and candidate-review stages remain
gap-registered.

## Facts

- `tools.research_agents.formalizer_runner_bridge.FormalizerRunnerBridge`
  accepts only its existing ToolContext role and WP allowlist.
- The bridge derives its output root from `scratch/<tool_context.wp_id>/outputs`,
  not from the lab-pipeline bridge-adapter package scratch root.
- The bridge validates formalizer source paths against its existing scoped
  formalizer scratch prefixes.
- The bridge approval gate expects the legacy bridge approval shape with
  `approved_by = operator` and `approved_for_noncanonical_runner_bridge = true`.
- This package requires a distinct Karl-signed, exact-content-bound bridge
  marker and package-local scratch outputs.
- When the existing bridge is fully unblocked, its normal path invokes the
  offline runner. This package forbids runner execution.

## Inference

The package-local bridge adapter cannot invoke the existing bridge while also
preserving all of these constraints:

- existing bridge ToolContext WP boundary;
- existing bridge source-prefix boundary;
- existing bridge output-root boundary;
- existing bridge approval semantics;
- package-local scratch-only output requirement;
- no offline runner execution.

## Decision

Keep `bridge_spec_variant_sweep_preparation` gap-registered with a precise hard
blocker. Do not add a compatibility shim, approval substitution, copied bridge
output, or runner-suppression workaround.

## Open Question

A later architecture package must decide whether to extend the bridge with an
explicit lab-pipeline adapter mode, including its own ToolContext WP, source
prefix, output root, approval schema, and no-runner preparation mode.

## Future Option

Draft a narrow bridge-contract expansion package before any runner-adapter
package. That package would need to modify the bridge itself intentionally and
prove that the new mode remains scratch-only, exact-content-bound, and unable to
execute the offline runner unless a later runner package separately authorizes
that behavior.
