# WP-DASH-ARCH-LOCK-01 Status

## Decision

`READY_FOR_REVIEW`

## Scope

Locks the architecture direction for a future local-first operator portal and
separate Agent Inbox runway. The package is documentation-only and creates no
dashboard implementation, API server, frontend app, Agent Inbox write surface,
hosting/auth layer, monitoring sidecar, dependency change, or runtime contact.

## Repo Truth Discovery

Recorded in `scratch/WP-DASH-ARCH-LOCK-01/repo_truth_discovery.md`.

Key findings:

- PR #625, PR #626, and PR #627 are merged to current `main`.
- Current dashboard/cockpit surfaces are local/static/read-only Python surfaces:
  `tools/dashboard`, `tools/lab_dashboard`, and `tools/lab_cockpit`.
- `tools/lab_cockpit` already displays real product-run fixtures read-only after
  `WP-LABPROD-COCKPIT-REALRUN-REFRESH-08`.
- No FastAPI service, Next.js app, package manifest, hosted deployment, auth
  implementation, Grafana/Prometheus/Loki sidecar, or Agent Inbox implementation
  exists in current repo truth.
- Older static dashboard architecture remains valid for existing static tools;
  this package locks a later portal architecture, not a retrofit of current
  static outputs.

## Delivered

- `docs/architecture/operator_dashboard_agent_inbox_architecture_lock.md`
- `docs/status_entries/WP-DASH-ARCH-LOCK-01.md`
- `scratch/WP-DASH-ARCH-LOCK-01/repo_truth_discovery.md`
- `scratch/WP-DASH-ARCH-LOCK-01/architecture_decision_summary.md`
- `scratch/WP-DASH-ARCH-LOCK-01/non_authority_assertions.json`
- `scratch/WP-DASH-ARCH-LOCK-01/validation_summary.txt`

## Architecture Locked

- Frontend target: React / Next.js / TypeScript / Tailwind.
- Backend target: FastAPI / Pydantic read-only artifact-reader API.
- Charting target: ECharts, TradingView Lightweight Charts, and Plotly only
  where needed.
- Local-first target: first implementation binds locally only; no hosted server
  before a future auth/hosting package.
- VPS target: portal-only minimum future VPS expectation is 2 vCPU / 4GB RAM /
  40GB SSD; paper/live sizing remains future and GO-gated.
- Auth target: mandatory for first hosted deployment; no unauthenticated hosted
  API.
- Agent Inbox target: separate future scratch-write runway, not bundled into the
  read-only dashboard API.
- Monitoring target: Grafana / Prometheus / Loki / TimescaleDB deferred until
  telemetry exists.

## Boundary

Docs/status/scratch only. No implementation code, schema, validator, query-layer
behavior, config, dependency, data, canonical evidence, candidate lifecycle,
crossing, promotion/readiness, scheduler/autonomy, notification, provider/API,
paper/live/runtime, OMS/risk/reconciliation, broker/exchange, or protected-path
behavior changed.

## Validation

Recorded in `scratch/WP-DASH-ARCH-LOCK-01/validation_summary.txt`.

## Next Authority

Future read-only API and frontend-shell implementation require separate explicit
packages. Future Agent Inbox, hosted deployment, auth/security, and monitoring
sidecar work also require separate explicit packages.
