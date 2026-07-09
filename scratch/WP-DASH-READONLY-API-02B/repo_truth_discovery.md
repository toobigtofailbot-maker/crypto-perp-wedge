# WP-DASH-READONLY-API-02B Repo Truth Discovery

Base branch: `main`

Base SHA: `6c0b173`

Working branch: `codex/wp-dash-readonly-api-02b`

## Dependency Status

FastAPI/TestClient import probe in repo `.venv`: PASS.

Observed output:

```text
fastapi_testclient_ok
```

Starlette emitted its existing deprecation warning for the current `httpx` TestClient path; the smoke assertion passed.

## Merge/Branch Preconditions

- PR #628 / `WP-DASH-ARCH-LOCK-01`: merged in current `main`.
- PR #629 / `WP-DASH-API-DEPS-02A`: merged in current `main`.
- PR #625/#626/#627: present in current `main` history.
- Required architecture lock exists at `docs/architecture/operator_dashboard_agent_inbox_architecture_lock.md`.
- Suggested branch `codex/wp-dash-readonly-api-02b` did not exist locally or remotely before creation.
- `gh pr list --state open --json number,title,headRefName,baseRefName,url --limit 100` returned `[]`; no competing open dashboard API PR was found.

## Existing Package Layout

Existing tool packages use `tools/<name>/__init__.py` plus focused modules and direct imports, with tests under `tests/test_<name>.py`. The package therefore uses `tools/operator_dashboard_api/{__init__,app,models,readers}.py` and `tests/test_operator_dashboard_api.py`.

## Existing Dashboard/Cockpit Entry Points

- `tools.dashboard.collector.collect_dashboard_data`
- `tools.lab_dashboard.data_model.build_dashboard_data`
- `tools.lab_cockpit.model.build_cockpit_data`
- `tools.lab_cockpit.model.build_product_pipeline_runs`
- `tools.lab_cockpit.model.build_product_candidate_funnel`
- `tools.lab_pipeline.queue_status.build_queue_status`
- `tools.lab_reporting.report_model.build_report_data`

These are deterministic read-only/static projection surfaces. They were read or imported only.

## Artifact Sources Used

- `research/result_populations/*.result_population.json`
- `research/strategy_specs/*.strategy_spec.json`
- `research/candidate_registry.jsonl`
- `scratch/WP-LABPROD-COCKPIT-REALRUN-REFRESH-08/product_runs/**`
- Static report/dashboard/cockpit docs and builders listed above.

## Query Surface

`tools.research_query` exists as the read-only DuckDB query layer. It lists 124 views on current `main`. Some full JSON view runs can exceed the local 30 second command cap, so the API uses direct committed JSON readers for result populations and strategy specs while recording the query layer as an available read-only source. No query-layer code or SQL was modified.

## API/Server Convention

No equivalent dashboard API or FastAPI server existed before this package. No server bind, `uvicorn` dependency, Dockerfile, deployment config, auth, or frontend app exists or was added.

## Route Subset Implemented

Implemented all required GET endpoints:

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

## Deferred Routes

- `POST /api/agent/intake-draft`: deferred because Agent Inbox writes belong to a later isolated package.
- Run/approval/execution/promotion/crossing/trading/scheduler/notification routes: forbidden by package scope and not implemented.
- Hosted run command: deferred because no `uvicorn` or deployment/server-runner surface is authorized here.
