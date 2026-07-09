# Operator Dashboard Read-Only API

This package exposes the first local-first FastAPI artifact-reader API for the future operator dashboard.

It is read-only and local inspection only. It reads committed repo artifacts and existing static projection builders, then returns normalized JSON envelopes for a future frontend. The API response is a derived projection; committed repo artifacts remain truth.

## Routes

- `GET /api/dashboard/summary`
- `GET /api/research/jobs`
- `GET /api/research/result-populations`
- `GET /api/research/result-populations/{id}`
- `GET /api/strategies`
- `GET /api/strategies/{id}`
- `GET /api/candidates/funnel`
- `GET /api/reports/daily`
- `GET /api/reports/weekly`
- `GET /api/system/data-health`
- `GET /api/agent/intake-schema`

## Boundary

The API creates no mutation endpoints, Agent Inbox write path, run path, approval path, execution path, promotion path, scheduler path, notification path, hosted deployment, auth implementation, frontend, provider/API contact, paper/live contact, canonical evidence write, strategy write, variant write, sweep write, candidate lifecycle write, or protected runtime contact.

`POST /api/agent/intake-draft` is intentionally absent. Agent Inbox writes belong to a later isolated package.

Paper and live data are surfaced only as unavailable placeholders unless a later package creates authorized read-only snapshots.

## Sources

Current readers use:

- `research/result_populations/*.result_population.json`
- `research/strategy_specs/*.strategy_spec.json`
- `research/candidate_registry.jsonl`
- `tools.lab_pipeline.queue_status.build_queue_status`
- `tools.lab_cockpit.model` product-run and funnel builders
- `tools.lab_reporting.report_model.build_report_data`
- `tools.dashboard.collector.collect_dashboard_data`

Every response carries `provenance`, `authority`, `warnings`, `withheld`, and `unavailable` fields.

## Tests

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_operator_dashboard_api.py -q
```

The app object is importable as `tools.operator_dashboard_api.app:app`. This package does not add a server runner or deployment command because no server dependency is authorized here.
