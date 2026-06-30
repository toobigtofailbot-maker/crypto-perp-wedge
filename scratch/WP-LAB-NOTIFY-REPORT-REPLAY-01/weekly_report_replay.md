# Weekly report replay

Evidence class: operating_test_evidence.
Deterministic source: reference event-tape timestamps.

## WEEKLY-0001

- tick event: `EVT-0037`
- window end: 2026-01-12T09:00:00Z
- events: 40
- categories: {"blocked": 2, "failed": 2, "insufficient": 1, "invalid": 1, "resource_limited": 2, "review_needed": 2, "withheld": 2}

- `EVT-0001` `job_enqueued` `not_terminal` report `include_if_window_matches`
- `EVT-0002` `job_started` `not_terminal` report `include_if_window_matches`
- `EVT-0003` `job_completed` `completed` report `include_terminal_summary`
- `EVT-0004` `notification_worthy` `completed` report `include_terminal_summary`
- `EVT-0005` `job_enqueued` `not_terminal` report `include_if_window_matches`
- `EVT-0006` `job_started` `not_terminal` report `include_if_window_matches`
- `EVT-0007` `job_failed` `failed` report `include_terminal_summary`
- `EVT-0008` `notification_worthy` `failed` report `include_terminal_summary`
- `EVT-0009` `job_enqueued` `not_terminal` report `include_if_window_matches`
- `EVT-0010` `job_invalid` `invalid` report `include_terminal_summary`
- `EVT-0011` `job_enqueued` `not_terminal` report `include_if_window_matches`
- `EVT-0012` `job_blocked` `blocked` report `include_blocker_summary`
- `EVT-0013` `notification_worthy` `blocked` report `include_blocker_summary`
- `EVT-0014` `job_enqueued` `not_terminal` report `include_if_window_matches`
- `EVT-0015` `job_started` `not_terminal` report `include_if_window_matches`
- `EVT-0016` `metrics_withheld` `withheld` report `include_withheld_summary`
- `EVT-0017` `notification_worthy` `withheld` report `include_withheld_summary`
- `EVT-0018` `job_enqueued` `not_terminal` report `include_if_window_matches`
- `EVT-0019` `job_started` `not_terminal` report `include_if_window_matches`
- `EVT-0020` `metrics_insufficient` `insufficient` report `include_withheld_summary`
- `EVT-0021` `job_enqueued` `not_terminal` report `include_if_window_matches`
- `EVT-0022` `resource_limited` `resource_limited` report `include_blocker_summary`
- `EVT-0023` `notification_worthy` `resource_limited` report `include_blocker_summary`
- `EVT-0024` `job_enqueued` `not_terminal` report `include_if_window_matches`
- `EVT-0025` `job_delayed` `delayed` report `include_blocker_summary`
- `EVT-0026` `job_enqueued` `not_terminal` report `include_if_window_matches`
- `EVT-0027` `job_started` `not_terminal` report `include_if_window_matches`
- `EVT-0028` `review_needed` `review_needed` report `include_blocker_summary`
- `EVT-0029` `notification_worthy` `review_needed` report `include_blocker_summary`
- `EVT-0030` `job_enqueued` `not_terminal` report `include_if_window_matches`
- `EVT-0031` `job_started` `not_terminal` report `include_if_window_matches`
- `EVT-0032` `job_completed` `no_candidate` report `include_terminal_summary`
- `EVT-0033` `daily_window_tick` `not_terminal` report `include_in_daily_window`
- `EVT-0034` `dashboard_snapshot_tick` `not_terminal` report `include_if_window_matches`
- `EVT-0035` `registry_checkpoint` `not_terminal` report `include_if_window_matches`
- `EVT-0036` `daily_window_tick` `not_terminal` report `include_in_daily_window`
- `EVT-0037` `weekly_window_tick` `not_terminal` report `include_in_weekly_window`
- `EVT-0038` `dashboard_snapshot_tick` `not_terminal` report `include_if_window_matches`
- `EVT-0039` `registry_checkpoint` `not_terminal` report `include_if_window_matches`
- `EVT-0040` `notification_worthy` `delayed` report `include_blocker_summary`
