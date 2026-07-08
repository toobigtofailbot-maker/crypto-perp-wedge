# Pipeline Contract

## Current Product Boundary

This contract describes the Wave 1 pipeline state spine and exact-content
prereg approval flow only. It does not describe an end-to-end existing-agent
chain.

The current CLI does not invoke the existing idea formalizer,
formalizer-runner bridge, robustness diagnostician, candidate-review packet
agent, WFO/OOS gate, or real offline runner. Approved runs write
`noncanonical_execution_summary.json` as deterministic non-canonical spine
proof, and that summary records `runner_invoked=false`.

Adapter wiring for the real existing modules is a required later package:
`WP-LABPROD-PIPELINE-AGENT-ADAPTERS-02`.

## Request

Input is a JSON object with:

- `source_idea`
- `symbol`
- `timeframe`
- `requested_by`
- optional `request_id`
- optional `requested_authority`
- optional `requested_outputs`

The bounded implementation supports `BTCUSDT` and the locked research
timeframes only.

## Approval

The pipeline pauses at `awaiting_prereg_approval` until a file-based approval
marker matches the frozen preregistration packet hash.

Approval is valid only when:

- `schema_version` is `lab_pipeline_prereg_approval_v1`
- `approved_by` is `Karl`
- `approval_scope` is `noncanonical_offline_research_execution_only`
- `approval_statement` exactly matches the packet requirement
- `authorizes_noncanonical_offline_research_execution` is `true`
- canonical, candidate, paper/live/runtime, scheduler/autonomy, and
  notification flags are all `false`
- `preregistration_packet_sha256` matches the frozen packet hash

## Blocked Authority

The pipeline blocks requests for canonical Result Population writes, candidate
lifecycle/admission writes, crossing, promotion/readiness, paper/live/runtime
contact, scheduler/autonomous dispatch, notification firing, or provider/API
credential use.

## Outputs

The output packet writes only under
`scratch/WP-LABPROD-PIPELINE-ORCHESTRATOR-01/outputs/<pipeline_run_id>/`.

All emitted JSON state/review surfaces carry non-authority flags.
