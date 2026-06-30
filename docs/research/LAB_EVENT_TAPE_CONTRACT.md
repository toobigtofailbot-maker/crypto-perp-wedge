# Lab Event Tape Contract v1

## Decision

`lab_event_tape.v1` is a closed deterministic contract for no-edge operating-readiness traffic. It creates operating-system evidence only. It is not strategy evidence, candidate evidence, edge evidence, crossing authority, promotion authority, paper/live authority, notification-send authority, or autonomous scheduler authority.

## Contract Route

- Contract document: `docs/research/LAB_EVENT_TAPE_CONTRACT.md`
- Machine-readable schema: `scratch/WP-LAB-EVENT-TAPE-CONTRACT-01/event_tape_schema.json`
- Reference tape: `scratch/WP-LAB-EVENT-TAPE-CONTRACT-01/reference_event_tape.json`
- Validator: `tools/lab_event_tape/validate.py`
- Source-reference mode: strict row-reference validation against `scratch/WP-LAB-FACTORYTEST-SYNTHETIC-POPULATION-01/synthetic_population_manifest.json` (`sha256:c653f61feb4a5dfee60c7031df3073c9f1beedf33725ae1175919e64e0de7c5e`)

## Tape-Level Requirements

Every tape must declare `schema_version`, `tape_id`, `package`, `description`, `deterministic`, `seed`, source-population provenance, authority-denial flags, and `events`. The required authority flags are fixed: `construction_payload=true`, `non_promotable=true`, `operating_test_evidence=true`, `strategy_evidence=false`, `candidate_evidence=false`, `edge_claim_allowed=false`, `canonical_crossing_allowed=false`, `paper_live_eligible=false`, `real_notification_sending_allowed=false`, and `autonomous_scheduler_allowed=false`.

## Event-Level Requirements

Every event must include `event_id`, contiguous `sequence_index`, UTC `event_time`, `event_type`, deterministic `job_id`, `source_row_id`, `source_variant_id`, all non-authority flags, `priority`, `job_state_before`, `job_state_after`, `job_outcome`, and `expected_operating_outcome`.

## Closed Enums

- `event_type`: `job_enqueued`, `job_started`, `job_completed`, `job_failed`, `job_invalid`, `job_blocked`, `metrics_withheld`, `metrics_insufficient`, `resource_limited`, `job_delayed`, `review_needed`, `notification_worthy`, `daily_window_tick`, `weekly_window_tick`, `dashboard_snapshot_tick`, `registry_checkpoint`
- `job_outcome`: `not_terminal`, `completed`, `failed`, `invalid`, `blocked`, `withheld`, `insufficient`, `resource_limited`, `delayed`, `review_needed`, `no_candidate`
- `job_state`: `not_seen`, `queued`, `running`, `completed`, `failed`, `invalid`, `blocked`, `withheld`, `insufficient`, `resource_limited`, `delayed`, `review_needed`, `no_candidate`
- `priority`: `low`, `normal`, `high`, `urgent`
- `expected_queue_action`: `none`, `enqueue`, `mark_running`, `mark_terminal`, `mark_invalid`, `mark_blocked`, `mark_withheld`, `mark_insufficient`, `mark_resource_limited`, `mark_delayed`, `mark_review_needed`
- `expected_scheduler_action`: `no_autonomous_dispatch`, `eligible_for_dry_run_start`, `hold_resource_limit`, `hold_dependency_blocked`, `mark_delayed`, `mark_terminal`
- `expected_notification_action`: `none`, `dry_run_blocked`, `dry_run_failed`, `dry_run_review_needed`, `dry_run_withheld`, `dry_run_resource_limited`, `dry_run_daily_summary`, `dry_run_weekly_summary`
- `expected_report_action`: `none`, `include_if_window_matches`, `include_in_daily_window`, `include_in_weekly_window`, `include_terminal_summary`, `include_blocker_summary`, `include_withheld_summary`
- `expected_dashboard_action`: `show_operating_test_state`, `show_queued`, `show_running`, `show_terminal`, `show_blocked`, `show_withheld`, `show_review_needed`, `show_resource_limited`, `show_no_candidate`
- `expected_agent_action`: `none`, `track_no_candidate_authority`, `track_terminal_no_candidate`, `track_blocker_no_candidate_authority`, `track_summary_no_candidate_authority`
- `expected_registry_action`: `none`, `record_operating_test_event`, `record_operating_test_checkpoint`

## Determinism Rules

`event_id` values must be unique and match contiguous `sequence_index` order starting at 1. `event_time` values must be deterministic UTC timestamps and non-decreasing. `job_id`, `source_row_id`, and `source_variant_id` must be deterministic strings. The reference tape uses the fixed seed `lab-event-tape-reference-v1-fixed-seed`. Validating the same tape twice must produce identical results.

## Source Reference Rules

When `source_row_id` and `source_variant_id` are present, the validator checks the exact pair against the #588 synthetic population manifest. This package uses strict row-reference validation, not a weakened declared-only mode.

## Non-Promotable Rules

Every tape and every event must remain a construction payload, non-promotable, and operating-test evidence. Events must explicitly deny strategy evidence, candidate eligibility, promotion eligibility, paper/live eligibility, canonical crossing, edge claims, real notification sending, and autonomous scheduling.

## Forbidden Aggregation Rules

Event tapes may be counted for operating-system readiness only. They must not be aggregated into strategy performance, candidate ranking, trial-log denominators, crossing decisions, paper/live readiness, promotion readiness, canonical Result Populations, or edge-search evidence. A later package may replay this tape only if explicitly authorized.

## Reference Tape Coverage

`LAB-EVENT-TAPE-REFERENCE-001` contains 40 events over 10 jobs, covers all closed event types, covers all required job outcomes, includes low/normal/high/urgent priority traffic, includes two daily windows, one weekly window, two dashboard snapshot ticks, and two registry checkpoints.
