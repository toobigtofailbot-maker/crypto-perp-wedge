# Lab Productization Pipeline Orchestrator

## Status And Authority

`tools/lab_pipeline` is an operator-invocable, deterministic, offline
orchestration spine for non-canonical research-lab packets.

It creates no canonical evidence, candidate lifecycle record, crossing,
promotion, readiness, paper/live/runtime behavior, scheduler/autonomous
dispatch, notification firing, provider/API use, credential use, dependency
change, data acquisition, or protected-path authority.

## Relationship To Existing Lab State

The existing coordinator model in `tools/lab_state` remains the canonical
read-only operator-state vocabulary. The pipeline stage names in
`tools/lab_pipeline` are local run-state names for one operator-invoked packet
and do not alter `tools/lab_state`.

Existing research-agent WPs remain bounded by their own ToolContext roles,
approval markers, and scratch prefixes. This orchestrator does not change those
agents or bypass their approval scopes. It records a deterministic pipeline
spine and can be extended by later authorized adapter packages if a clean
callable integration is locked.

## Flow

The supported flow is:

```text
request_loaded
-> idea_formalized
-> availability_checked
-> prereg_packet_prepared
-> awaiting_prereg_approval
-> approved_for_noncanonical_execution
-> noncanonical_execution_running
-> noncanonical_execution_complete
-> gate_review_complete
-> robustness_review_complete
-> candidate_review_packet_prepared
-> complete
```

`blocked` is the fail-closed terminal state for malformed input, unavailable
bounded capability, broad approvals, or requested authority outside this
package.

## Approval Binding

The pipeline halts at `awaiting_prereg_approval` unless a file-based approval
marker is supplied. The marker must bind exactly to the frozen
`preregistration_packet.json` hash and must use:

- `schema_version = lab_pipeline_prereg_approval_v1`
- `approval_scope = noncanonical_offline_research_execution_only`
- the exact approval statement recorded in `approval_requirement.json`
- `authorizes_noncanonical_offline_research_execution = true`
- canonical, candidate, paper/live/runtime, scheduler/autonomy, and notification
  authority flags set to `false`

Missing, mismatched, broad, stale, or malformed markers block and preserve the
reason in `pipeline_state.json` and `pipeline_trace.json`.

## Outputs

Each run writes under:

```text
scratch/WP-LABPROD-PIPELINE-ORCHESTRATOR-01/outputs/<pipeline_run_id>/
```

Core files:

- `pipeline_request.json`
- `pipeline_state.json`
- `pipeline_trace.json`
- `artifact_index.json`
- `preregistration_packet.json`
- `approval_requirement.json`
- `non_authority_assertions.json`
- `operator_review_packet.md`

Approved runs also write `noncanonical_execution_summary.json`. That file is a
deterministic spine proof, not canonical evidence and not a runner result.

## CLI

```powershell
python -m tools.lab_pipeline.run --request <request.json> --json
python -m tools.lab_pipeline.run --request <request.json> --approval <approval.json> --json
```

Exit codes:

- `0`: complete
- `1`: malformed CLI/input error
- `2`: blocked
- `3`: awaiting prereg approval

## Boundary

The orchestrator blocks requests that ask for canonical Result Population
writes, candidate admission or lifecycle writes, crossing, promotion/readiness,
paper/live/runtime contact, scheduler/autonomous dispatch, notification firing,
or provider/API/credential use.

Any such downstream action requires a separate approved work package.
