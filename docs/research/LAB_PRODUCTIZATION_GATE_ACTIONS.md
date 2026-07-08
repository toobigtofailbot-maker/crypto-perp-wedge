# Lab Productization Gate Actions

## Status And Authority

`tools.lab_pipeline.gate_actions` provides local, non-canonical product action
contracts for the merged lab pipeline preregistration gate and a future
candidate-surface advisory decision.

These actions are operator-callable scaffolding only. They do not create a
cockpit button, write canonical evidence, write candidate lifecycle records,
execute crossing, promote or mark readiness, contact paper/live/runtime paths,
use scheduler/autonomy, send notifications, contact providers/APIs, use
credentials, change dependencies/configs, acquire data, or touch protected
paths.

## Prereg Approval Preview

The prereg preview consumes:

- `approval_requirement.json`;
- `preregistration_packet.json`.

It writes a human-readable `approval_preview.md` or returns the same preview via
the CLI JSON summary. It does not create an approval marker.

The preview includes the packet hash, source idea, symbol/timeframe, execution
scope, denominator policy, authority flags, what approval would authorize, and
what it would not authorize.

## Prereg Approval Marker Action

The prereg approval marker action consumes:

- `approval_requirement.json`;
- `preregistration_packet.json`;
- explicit operator fields supplied at invocation time.

The marker is written only when the supplied fields exactly satisfy the merged
pipeline approval contract:

- `schema_version = lab_pipeline_prereg_approval_v1`;
- `approved_by = Karl`;
- `approval_scope = noncanonical_offline_research_execution_only`;
- exact approval statement from `approval_requirement.json`;
- `authorizes_noncanonical_offline_research_execution = true`;
- broader authority flags are false;
- exact `preregistration_packet_sha256` match;
- explicit non-empty UTC timestamp.

The output marker is suitable for:

```powershell
python -m tools.lab_pipeline.run --request <request.json> --approval <approval_marker.json>
```

## Candidate-Surface Advisory Decision

The candidate-surface decision action records only local advisory decisions:

- `hold_for_review`;
- `needs_more_evidence`;
- `do_not_escalate`.

It does not admit candidates, cross artifacts, promote, mark readiness, start
paper, start shadow, start live, touch runtime, use scheduler/autonomy, send
notifications, contact providers/APIs, or use credentials.

Unsupported or forbidden decision terms fail closed.

## Output Safety

Default action outputs write only under:

```text
scratch/WP-LABPROD-INPRODUCT-GATE-ACTIONS-01/outputs/<gate_action_id>/
```

Caller-specified output files are accepted only under the package scratch root
when they are inside the repo, or under the system temporary directory for
validation use. Repo-local path escapes are rejected before writing.

## CLI

Preview:

```powershell
python -m tools.lab_pipeline.run `
  --gate-action prereg-preview `
  --approval-requirement <approval_requirement.json> `
  --preregistration-packet <preregistration_packet.json> `
  --output <approval_preview.md> `
  --json
```

Approval marker:

```powershell
python -m tools.lab_pipeline.run `
  --gate-action prereg-approve `
  --approval-requirement <approval_requirement.json> `
  --preregistration-packet <preregistration_packet.json> `
  --schema-version lab_pipeline_prereg_approval_v1 `
  --approved-by Karl `
  --approval-scope noncanonical_offline_research_execution_only `
  --approval-statement "<exact statement from approval_requirement.json>" `
  --approval-timestamp-utc <timestamp> `
  --authorizes-noncanonical-offline-research-execution true `
  --authorizes-canonical-write false `
  --authorizes-candidate-lifecycle false `
  --authorizes-paper-live-runtime false `
  --authorizes-scheduler-autonomy false `
  --authorizes-notifications false `
  --preregistration-packet-sha256 <packet hash> `
  --json
```

Candidate-surface decision:

```powershell
python -m tools.lab_pipeline.run `
  --gate-action candidate-decision `
  --decision hold_for_review `
  --decided-by Karl `
  --decision-timestamp-utc <timestamp> `
  --json
```

## Non-Authority Assertions

Every action output asserts false for:

- canonical write;
- candidate lifecycle write;
- crossing;
- promotion/readiness;
- paper/live/runtime;
- scheduler/autonomy;
- notification sending;
- provider/API/credential;
- dependency/config/data acquisition;
- protected-path touch.
