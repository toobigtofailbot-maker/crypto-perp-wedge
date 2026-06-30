# Reference Event Tape Summary

- Package: `WP-LAB-EVENT-TAPE-CONTRACT-01`
- Tape ID: `LAB-EVENT-TAPE-REFERENCE-001`
- Schema version: `lab_event_tape.v1`
- Event count: 40
- Job count: 10
- Deterministic: true
- Daily windows: 2
- Weekly windows: 1
- Dashboard ticks: 2
- Registry checkpoints: 2
- Source-reference validation mode: `strict_row_reference_validation`
- Source manifest SHA256: `sha256:c653f61feb4a5dfee60c7031df3073c9f1beedf33725ae1175919e64e0de7c5e`

## Event Types Covered

- `daily_window_tick`
- `dashboard_snapshot_tick`
- `job_blocked`
- `job_completed`
- `job_delayed`
- `job_enqueued`
- `job_failed`
- `job_invalid`
- `job_started`
- `metrics_insufficient`
- `metrics_withheld`
- `notification_worthy`
- `registry_checkpoint`
- `resource_limited`
- `review_needed`
- `weekly_window_tick`

## Job Outcomes Covered

- `blocked`
- `completed`
- `delayed`
- `failed`
- `insufficient`
- `invalid`
- `no_candidate`
- `not_terminal`
- `resource_limited`
- `review_needed`
- `withheld`

## Non-Authority Assertions

- construction_payload all events: true
- non_promotable all events: true
- operating_test_evidence all events: true
- strategy evidence any: false
- candidate eligible any: false
- promotion eligible any: false
- paper/live eligible any: false
- canonical crossing allowed any: false
- edge claim allowed any: false
- autonomous scheduler allowed any: false
- real notification sending allowed any: false
