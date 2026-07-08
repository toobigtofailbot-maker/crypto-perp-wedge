# Gate Action Contract

## Prereg Preview

Inputs:

- `approval_requirement.json`
- `preregistration_packet.json`

Output:

- human-readable markdown preview

Authority:

- no approval marker is created
- no canonical, candidate lifecycle, crossing, promotion/readiness,
  paper/live/runtime, scheduler/autonomy, notification, provider/API/credential,
  dependency/config/data-acquisition, or protected-path authority is created

## Prereg Approval Marker

Inputs:

- `approval_requirement.json`
- `preregistration_packet.json`
- explicit operator fields

Required operator fields:

- `schema_version`
- `approved_by`
- `approval_scope`
- `approval_statement`
- `approval_timestamp_utc`
- `authorizes_noncanonical_offline_research_execution`
- `authorizes_canonical_write`
- `authorizes_candidate_lifecycle`
- `authorizes_paper_live_runtime`
- `authorizes_scheduler_autonomy`
- `authorizes_notifications`
- `preregistration_packet_sha256`

Output:

- `approval_marker.json` accepted by `tools.lab_pipeline.run --approval`

## Candidate-Surface Decision

Allowed decision values:

- `hold_for_review`
- `needs_more_evidence`
- `do_not_escalate`

Forbidden values and terms:

- `admit_candidate`
- `cross`
- `promote`
- `ready_for_paper`
- `start_paper`
- `start_shadow`
- `start_live`
- candidate lifecycle write terms
- runtime, scheduler/autonomy, provider/API/credential terms

Output:

- local advisory decision JSON only

## Path Safety

Repo-local output files are allowed only under:

```text
scratch/WP-LABPROD-INPRODUCT-GATE-ACTIONS-01/
```

Temporary validation outputs are allowed under the system temp directory.
