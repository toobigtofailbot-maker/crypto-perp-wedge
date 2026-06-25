# Lab Operator Surface — Unified Index (read-only)

_schema: `lab_operator_surface_integration_v1` -- read_only_operator_surface_index_

> Read-only operator index. This is where to look, not a control panel: no run, approve, reject, promote, retry, scheduler, or live-fetch control.

> No further edge-search is authorized by the coordinator state model. Strategy generation/search remains held until separate operator authorization.

_as-of label: `2026-06-25` -- period label: `2026-W26` (descriptive only; no clock is read)_

## Honest current state

- No candidate is ready for human review and no operator gate is pending. The queue correctly shows only NO-GO / blocked / advisory-only items. This is the honest current state, not an error.
- candidate ready (committed evidence): 0
- operator gate pending: 0
- nothing candidate-ready: `true`

## Batch boundary (full population, not winners only)

- subjects: 2
- completed experiment runs reached: 2
- NO-GO: 1
- blocked: 0
- candidate ready for human review: 0
- operator gate pending: 0
- distinct Result Population sets: 1

### Subjects by overall state

| overall state | count |
| --- | ---: |
| `not_started` | 0 |
| `formalized` | 0 |
| `experiment_complete` | 0 |
| `replay_checked` | 0 |
| `oos_gate_fail` | 1 |
| `oos_gate_blocked` | 0 |
| `candidate_review_blocked` | 0 |
| `robustness_advisory` | 0 |
| `no_go` | 1 |
| `blocked` | 0 |
| `candidate_ready_for_human_review` | 0 |
| `operator_gate_pending` | 0 |
| `reported` | 0 |

## Surfaces

### Coordinator state snapshot

- package: `WP-LAB-COORDINATOR-STATE-MODEL-01`
- module: `tools/lab_state`
- open: `python -m tools.lab_state.run --snapshot`
- doc: [`docs/research/LAB_COORDINATOR_STATE_MODEL.md`](docs/research/LAB_COORDINATOR_STATE_MODEL.md)
- summary:
  - subject_count: 2
  - by_overall_state: not_started=0, formalized=0, experiment_complete=0, replay_checked=0, oos_gate_fail=1, oos_gate_blocked=0, candidate_review_blocked=0, robustness_advisory=0, no_go=1, blocked=0, candidate_ready_for_human_review=0, operator_gate_pending=0, reported=0

### Results dashboard

- package: `WP-LAB-RESULTS-DASHBOARD-01`
- module: `tools/lab_dashboard`
- open: `python -m tools.lab_dashboard.run --markdown`
- doc: [`docs/research/LAB_RESULTS_DASHBOARD_SURFACE.md`](docs/research/LAB_RESULTS_DASHBOARD_SURFACE.md)
- summary:
  - completed_experiment_run_count: 2
  - no_go_count: 1
  - blocked_count: 0
  - candidate_ready_count: 0
  - operator_gate_pending_count: 0
  - distinct_result_population_sets: 1

### Latest daily brief

- package: `WP-LAB-OPERATOR-BRIEF-REPORT-01`
- module: `tools/lab_reporting`
- open: `python -m tools.lab_reporting.run --daily-brief --as-of <label>`
- doc: [`docs/research/LAB_OPERATOR_BRIEF_REPORT_SURFACE.md`](docs/research/LAB_OPERATOR_BRIEF_REPORT_SURFACE.md)
- summary:
  - as_of: 2026-06-25
  - completed_runs: 2
  - blocked_runs: 0
  - no_gos: 1
  - open_decision_surfaces: 0

### Latest weekly report

- package: `WP-LAB-OPERATOR-BRIEF-REPORT-01`
- module: `tools/lab_reporting`
- open: `python -m tools.lab_reporting.run --weekly-report --period <label>`
- doc: [`docs/research/LAB_OPERATOR_BRIEF_REPORT_SURFACE.md`](docs/research/LAB_OPERATOR_BRIEF_REPORT_SURFACE.md)
- summary:
  - period: 2026-W26
  - subjects: 2
  - candidate_review_evidence: 0
  - withheld_statistics: DSR, MinTRL, PSR

### Approval / gate queue

- package: `WP-LAB-APPROVAL-QUEUE-SURFACE-01`
- module: `tools/lab_approval_queue`
- open: `python -m tools.lab_approval_queue.run --markdown`
- doc: [`docs/research/LAB_APPROVAL_QUEUE_SURFACE.md`](docs/research/LAB_APPROVAL_QUEUE_SURFACE.md)
- summary:
  - by_queue_status: operator_gate_pending=0, no_go=1, blocked_validation=1, advisory_only=0, not_actionable=0
  - operator_gate_pending_count: 0
  - blocked_validation_count: 1
  - no_go_count: 1
  - candidate_review_packet_created_count: 0
  - nothing_candidate_ready: True
  - honest_state_note: No candidate is ready for human review and no operator gate is pending. The queue correctly shows only NO-GO / blocked / advisory-only items. This is the honest current state, not an error.

### Scheduler shell (inert, default-off)

- package: `WP-LAB-SCHEDULER-SHELL-DEFAULT-OFF-01`
- module: `tools/lab_scheduler_shell`
- open: `python -m tools.lab_scheduler_shell.run --snapshot`
- doc: [`docs/research/LAB_SCHEDULER_SHELL_DEFAULT_OFF.md`](docs/research/LAB_SCHEDULER_SHELL_DEFAULT_OFF.md)
- summary:
  - all_default_off: True
  - enabled_flags: none
  - queue_entry_count: 4
  - dry_run_all_actions_noop: True
  - dry_run_executed_any_action: False
  - dry_run_noop_reason_code: SCHED_AUTONOMY_DISABLED

## Related artifacts and docs

| role | path | present |
| --- | --- | --- |
| integration | [`docs/research/LAB_OPERATOR_SURFACE_INTEGRATION.md`](docs/research/LAB_OPERATOR_SURFACE_INTEGRATION.md) | present |
| state_model | [`docs/research/LAB_COORDINATOR_STATE_MODEL.md`](docs/research/LAB_COORDINATOR_STATE_MODEL.md) | present |
| dashboard | [`docs/research/LAB_RESULTS_DASHBOARD_SURFACE.md`](docs/research/LAB_RESULTS_DASHBOARD_SURFACE.md) | present |
| brief_report | [`docs/research/LAB_OPERATOR_BRIEF_REPORT_SURFACE.md`](docs/research/LAB_OPERATOR_BRIEF_REPORT_SURFACE.md) | present |
| approval_queue | [`docs/research/LAB_APPROVAL_QUEUE_SURFACE.md`](docs/research/LAB_APPROVAL_QUEUE_SURFACE.md) | present |
| scheduler_shell | [`docs/research/LAB_SCHEDULER_SHELL_DEFAULT_OFF.md`](docs/research/LAB_SCHEDULER_SHELL_DEFAULT_OFF.md) | present |

## Caveats

- This is a read-only index of where to look; it is not a control panel and holds no execution authority.
- Every state value is taken verbatim from the surface that owns it (ultimately the coordinator state model); this index re-ranks nothing and adds no new state vocabulary.
- The denominator is the full population (every run and state), shown by the dashboard and brief/report — not winners only.
- Honest current state: no candidate is ready for human review unless the approval queue's committed evidence records it.
- The scheduler shell is inert and default-off; its dry-run actions are all no-ops and it has no executor.
- Any real transition, approval, promotion, or run requires separate human action through the human-gated candidate lifecycle engine; this index cannot grant it.
