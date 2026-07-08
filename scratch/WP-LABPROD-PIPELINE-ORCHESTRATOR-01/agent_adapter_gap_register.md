# Agent Adapter Gap Register

## Fact

PR #612 adds `tools/lab_pipeline` as a deterministic pipeline state spine and
exact-content prereg approval contract.

Approved runs write `noncanonical_execution_summary.json` with
`execution_kind=deterministic_spine_proof` and `runner_invoked=false`.

The current PR does not invoke the existing idea formalizer,
formalizer-runner bridge, robustness diagnostician, candidate-review packet
agent, WFO/OOS gate, or real offline runner.

## Inference

Existing agent modules remain bounded by package-specific ToolContext roles, WP
IDs, approval contracts, and scratch prefixes. Treating them as already wired
into `tools/lab_pipeline` would overstate the implementation and weaken reviewer
understanding of the boundary.

## Decision

Keep PR #612 scoped to the state spine / prereg approval contract. Do not claim
that it removes Codex work packages needed for a full hypothesis test or creates
a complete end-to-end productized agent flow.

## Required Follow-Up

`WP-LABPROD-PIPELINE-AGENT-ADAPTERS-02` should safely bind the pipeline state
spine to existing formalizer / bridge / runner / robustness / candidate-review
packet modules without weakening ToolContext, approval, scratch-prefix,
non-authority, or protected-boundary guarantees.
