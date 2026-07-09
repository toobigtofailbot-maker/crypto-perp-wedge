# Lab Productization Queue / Status Visibility

## Summary

`WP-LABPROD-LAB-QUEUE-STATUS-07` adds a read-only operator queue/status projection for product lab pipeline runs.

The surface is implemented in `tools.lab_pipeline.queue_status`. It reads existing product pipeline artifacts and joins them by `pipeline_run_id`:

- `pipeline_state.json` from the lab pipeline spine;
- `runner_adapter_result.json` from the product runner adapter, when present;
- `advisory_review_packet.json` from the product gates adapter, when present.

It does not invoke the orchestrator, runner adapter, gates adapter, scheduler, notification system, provider/API, paper/live/runtime, or any protected path.

## Status States

Allowed operator-visible states are:

- `queued`;
- `running`;
- `awaiting_prereg_approval`;
- `awaiting_execute_approval`;
- `blocked`;
- `complete`;
- `failed`;
- `advisory_packet_ready`.

`awaiting_prereg_approval` is distinct from `blocked`: it means Karl approval is needed for the exact preregistration packet. `awaiting_execute_approval` is distinct from `blocked`: it means preregistration has completed and the next product runner step requires separate execute approval.

`advisory_packet_ready` is shown only when an existing gates-adapter advisory packet is present and completed for the same product pipeline run.

## Current Repo Projection

On current `main` plus this package branch, committed pipeline fixtures project to:

- `LPIPE-0508a68667a87ce9`: `awaiting_execute_approval`;
- `LPIPE-2201304f65ac6f79`: `awaiting_prereg_approval`;
- `LPIPE-e7d1a256221a28aa`: `blocked`.

No committed product runner/gates output directory is present, so the current committed snapshot has zero `complete` and zero `advisory_packet_ready` runs. Focused tests create package-local temp artifacts to verify those states without committing execution outputs.

## Notification Posture

The model includes `notification_preview` fields only as dry-run display metadata:

- `dry_run_only = true`;
- `notification_fired = false`;
- `dispatch_enqueued = false`;
- `channels = []`.

No email, Slack, push, webhook, scheduler, dispatch, or job control path is imported or called.

## Boundary

The surface is status visibility only. It writes no canonical evidence, candidate lifecycle, crossing, promotion/readiness, runtime, paper/live, provider/API, dependency/config/data-acquisition, or protected-path state.
