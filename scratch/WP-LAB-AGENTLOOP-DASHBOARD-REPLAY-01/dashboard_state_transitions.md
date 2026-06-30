# Dashboard state transitions

Evidence class: operating_test_evidence.
Traffic label: operating_test_traffic_only.
No-candidate and no-authority labels are present on every snapshot.

- snapshot count: 40
- deterministic from event timestamps and sequence index: true
- category counts: {"blocked": 3, "completed": 3, "delayed": 2, "failed": 3, "insufficient": 2, "invalid": 2, "no_candidate": 1, "queued": 10, "resource_limited": 3, "review_needed": 2, "running": 6, "withheld": 3}

- `DASH-SNAP-0001` `EVT-0001` `queued` `show_queued` `no_candidate` `no_authority`
- `DASH-SNAP-0002` `EVT-0002` `running` `show_running` `no_candidate` `no_authority`
- `DASH-SNAP-0003` `EVT-0003` `completed` `show_terminal` `no_candidate` `no_authority`
- `DASH-SNAP-0004` `EVT-0004` `completed` `show_terminal` `no_candidate` `no_authority`
- `DASH-SNAP-0005` `EVT-0005` `queued` `show_queued` `no_candidate` `no_authority`
- `DASH-SNAP-0006` `EVT-0006` `running` `show_running` `no_candidate` `no_authority`
- `DASH-SNAP-0007` `EVT-0007` `failed` `show_terminal` `no_candidate` `no_authority`
- `DASH-SNAP-0008` `EVT-0008` `failed` `show_terminal` `no_candidate` `no_authority`
- `DASH-SNAP-0009` `EVT-0009` `queued` `show_queued` `no_candidate` `no_authority`
- `DASH-SNAP-0010` `EVT-0010` `invalid` `show_terminal` `no_candidate` `no_authority`
- `DASH-SNAP-0011` `EVT-0011` `queued` `show_queued` `no_candidate` `no_authority`
- `DASH-SNAP-0012` `EVT-0012` `blocked` `show_blocked` `no_candidate` `no_authority`
- `DASH-SNAP-0013` `EVT-0013` `blocked` `show_blocked` `no_candidate` `no_authority`
- `DASH-SNAP-0014` `EVT-0014` `queued` `show_queued` `no_candidate` `no_authority`
- `DASH-SNAP-0015` `EVT-0015` `running` `show_running` `no_candidate` `no_authority`
- `DASH-SNAP-0016` `EVT-0016` `withheld` `show_withheld` `no_candidate` `no_authority`
- `DASH-SNAP-0017` `EVT-0017` `withheld` `show_withheld` `no_candidate` `no_authority`
- `DASH-SNAP-0018` `EVT-0018` `queued` `show_queued` `no_candidate` `no_authority`
- `DASH-SNAP-0019` `EVT-0019` `running` `show_running` `no_candidate` `no_authority`
- `DASH-SNAP-0020` `EVT-0020` `insufficient` `show_withheld` `no_candidate` `no_authority`
- `DASH-SNAP-0021` `EVT-0021` `queued` `show_queued` `no_candidate` `no_authority`
- `DASH-SNAP-0022` `EVT-0022` `resource_limited` `show_resource_limited` `no_candidate` `no_authority`
- `DASH-SNAP-0023` `EVT-0023` `resource_limited` `show_resource_limited` `no_candidate` `no_authority`
- `DASH-SNAP-0024` `EVT-0024` `queued` `show_queued` `no_candidate` `no_authority`
- `DASH-SNAP-0025` `EVT-0025` `delayed` `show_blocked` `no_candidate` `no_authority`
- `DASH-SNAP-0026` `EVT-0026` `queued` `show_queued` `no_candidate` `no_authority`
- `DASH-SNAP-0027` `EVT-0027` `running` `show_running` `no_candidate` `no_authority`
- `DASH-SNAP-0028` `EVT-0028` `review_needed` `show_review_needed` `no_candidate` `no_authority`
- `DASH-SNAP-0029` `EVT-0029` `review_needed` `show_review_needed` `no_candidate` `no_authority`
- `DASH-SNAP-0030` `EVT-0030` `queued` `show_queued` `no_candidate` `no_authority`
- `DASH-SNAP-0031` `EVT-0031` `running` `show_running` `no_candidate` `no_authority`
- `DASH-SNAP-0032` `EVT-0032` `no_candidate` `show_no_candidate` `no_candidate` `no_authority`
- `DASH-SNAP-0033` `EVT-0033` `completed` `show_terminal` `no_candidate` `no_authority`
- `DASH-SNAP-0034` `EVT-0034` `failed` `show_terminal` `no_candidate` `no_authority`
- `DASH-SNAP-0035` `EVT-0035` `invalid` `show_terminal` `no_candidate` `no_authority`
- `DASH-SNAP-0036` `EVT-0036` `blocked` `show_blocked` `no_candidate` `no_authority`
- `DASH-SNAP-0037` `EVT-0037` `withheld` `show_withheld` `no_candidate` `no_authority`
- `DASH-SNAP-0038` `EVT-0038` `insufficient` `show_withheld` `no_candidate` `no_authority`
- `DASH-SNAP-0039` `EVT-0039` `resource_limited` `show_resource_limited` `no_candidate` `no_authority`
- `DASH-SNAP-0040` `EVT-0040` `delayed` `show_blocked` `no_candidate` `no_authority`
