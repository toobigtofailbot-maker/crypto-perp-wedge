# Adapter Contract

## Closed Registry

The registry lives in `tools/lab_pipeline/adapter_contract.py`.

Implemented adapters:

- `adapter.idea_formalizer.fake_offline.v1`
- `adapter.lab_readiness.projection.v1`

Blocked adapters:

- `adapter.formalizer_runner_bridge.v1`
- `adapter.offline_runner.noncanonical.v1`
- `adapter.wfo_oos_gate.v1`
- `adapter.robustness_diagnostician.v1`
- `adapter.candidate_review_packet.v1`

## Status Vocabulary

Stage statuses:

- `adapter_complete`
- `adapter_blocked`
- `adapter_skipped`
- `adapter_failed`
- `awaiting_prereg_approval`
- `blocked_unsafe_to_adapt`

Run statuses:

- `awaiting_prereg_approval`
- `complete_with_gaps`
- `complete_without_gaps`
- `adapter_failed`

## Non-Authority Assertions

Every adapter packet asserts false for canonical evidence writes, candidate
lifecycle writes, candidate admission, crossing, promotion/readiness,
paper/live/runtime contact, scheduler/autonomous dispatch, notification firing,
provider/API/credential use, dependency/config/data acquisition, and protected
path touch.
