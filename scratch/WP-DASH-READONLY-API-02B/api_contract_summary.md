# WP-DASH-READONLY-API-02B API Contract Summary

All responses use `operator_dashboard_api_v1` envelopes:

- `schema_version`
- `source`
- `provenance`
- `authority`
- `warnings`
- `withheld`
- `unavailable`
- `data`

Every response states that the API is a derived read-only projection and that committed repo artifacts remain truth.

## Implemented Endpoints

| Endpoint | Source |
| --- | --- |
| `GET /api/dashboard/summary` | committed artifacts, queue reader, cockpit product-run reader |
| `GET /api/research/jobs` | `tools.lab_pipeline.queue_status.build_queue_status` |
| `GET /api/research/result-populations` | `research/result_populations/*.result_population.json` |
| `GET /api/research/result-populations/{id}` | matching committed Result Population artifact |
| `GET /api/strategies` | `research/strategy_specs/*.strategy_spec.json` |
| `GET /api/strategies/{id}` | matching committed Strategy Spec artifact |
| `GET /api/candidates/funnel` | `research/candidate_registry.jsonl` plus cockpit product candidate funnel |
| `GET /api/reports/daily` | `tools.lab_reporting.report_model.build_report_data` |
| `GET /api/reports/weekly` | `tools.lab_reporting.report_model.build_report_data` |
| `GET /api/system/data-health` | `tools.dashboard.collector.collect_dashboard_data` |
| `GET /api/agent/intake-schema` | architecture-lock boundary placeholder only |

## Deferred / Absent

- `POST /api/agent/intake-draft`
- run routes
- approval routes
- execution routes
- promotion routes
- crossing routes
- trading routes
- scheduler routes
- notification routes
- hosted/deployment runner

## Placeholder / Unavailable Behavior

- Paper/live telemetry is returned as unavailable because no authorized read-only snapshots exist.
- Agent Inbox write schema is returned as a future placeholder only; no draft endpoint exists.
- Missing Result Population or Strategy Spec ids return a 200 JSON envelope with `status: unavailable` and explicit `unavailable` reason.
- Withheld metrics are named in `withheld`; unavailable surfaces are named in `unavailable`; no missing metric is fabricated as zero.

## Authority Boundary

The API is local-first and read-only. It grants no recommendation, ranking, readiness, promotion, approval, execution, paper/live, runtime, scheduler, notification, candidate lifecycle, or Agent Inbox write authority.
