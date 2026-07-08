# Bridge Adapter Blocker Report

## Blocker

`bridge_spec_variant_sweep_preparation` cannot be safely adapter-backed from
the lab pipeline in the current merged repo state.

## Exact Existing Contracts That Block Invocation

- ToolContext WP contract: the bridge rejects the lab-pipeline bridge package
  WP ID.
- Source-prefix contract: the bridge rejects package-local formalizer outputs.
- Output-root contract: bridge outputs are rooted under the bridge or agent WP,
  not under `scratch/WP-LABPROD-PIPELINE-BRIDGE-ADAPTER-03/`.
- Approval contract: the bridge expects legacy operator approval, while this
  package requires a Karl-signed exact-content bridge marker.
- Runner boundary: the existing bridge's successful unblocked path invokes the
  offline runner, which this package forbids.

## Non-Authority

This blocker report creates no Strategy Spec, Variant Manifest, Sweep Plan,
Result Population, WFO/OOS result, robustness diagnostic, candidate-review
packet, candidate lifecycle record, crossing, promotion/readiness, runtime,
paper/live, scheduler/autonomy, notification, provider/API, credential,
dependency/config, data-acquisition, or protected-path authority.

## Required Next Decision

Decide whether to authorize a future bridge-contract expansion package that
adds a lab-pipeline adapter mode with package-local scratch outputs, a
Karl-signed exact-content approval schema, and an explicit no-runner bridge
preparation mode.
