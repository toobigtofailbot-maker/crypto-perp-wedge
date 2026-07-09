# Operator Dashboard and Agent Inbox Architecture Lock

Package: `WP-DASH-ARCH-LOCK-01`

## 1. Scope

This document locks the architecture direction for a future operator-grade
dashboard and isolated Agent Inbox runway. It is a documentation-only
architecture lock. It does not implement a dashboard, API server, Agent Inbox,
hosting layer, authentication system, monitoring sidecar, scheduler,
notification path, or runtime connection.

The current merged cockpit and dashboard surfaces remain repo truth:

- `tools/dashboard` is a local/offline static dashboard generator over
  `dashboard_data.v1`.
- `tools/lab_dashboard` is a deterministic static lab results dashboard.
- `tools/lab_cockpit` is a richer static read-only product cockpit.
- `tools/lab_pipeline.queue_status` exposes read-only product pipeline queue
  and status visibility.

This lock is the next architecture target after those static surfaces. It does
not supersede their no-control guarantees and does not retrofit them into a
server.

## 2. Repo-Truth Basis

Facts:

- PR #627 (`WP-LABPROD-COCKPIT-REALRUN-REFRESH-08`) is merged and refreshed the
  static product cockpit for real product-run fixtures.
- PR #625 (`WP-LABPROD-LAB-QUEUE-STATUS-07`) is merged and added read-only
  queue/status visibility.
- PR #626 (`WP-LABPROD-BOUNDED-SWEEP-SCALE-06`) is merged and added bounded
  sweep scale enforcement to the product pipeline.
- Current dashboard/cockpit implementations are static or CLI-driven Python
  surfaces. No FastAPI service, Next.js app, package manifest, hosted portal, or
  Agent Inbox implementation exists in current repo truth.
- Existing static dashboard architecture (`docs/architecture/2026-06-local_static_dashboard_design.md`)
  intentionally forbade React/server/auth for its MVP. That constraint remains
  true for the existing static dashboard line.

Inference:

- Karl's current operator goal needs a richer application shell than the static
  cockpit, but that richer shell must be introduced as a new local-first,
  read-only portal architecture rather than by widening the authority of existing
  static tools.

Decision:

- The first real operator portal will be designed as a local-first web
  application with a Next.js frontend and a read-only FastAPI artifact-reader
  backend, implemented only by later explicit packages.

## 3. Accepted Portal Stack

Frontend direction:

- React / Next.js / TypeScript.
- Tailwind CSS.
- Component library selection is deferred until the first frontend-shell package
  or a separate design-system package. The choice must follow repo convention if
  one exists by then.

Backend direction:

- FastAPI.
- Pydantic schemas.
- Read-only artifact-reader service.
- Repo query layer and artifact readers as the source of facts.
- JSON contracts between backend and frontend.

Charting direction:

- Apache ECharts for dashboards, heatmaps, funnels, timelines, trees, gauges,
  and dense operating-status views.
- TradingView Lightweight Charts for candles, equity, drawdown, and trade
  markers.
- Plotly only where analytical drilldowns need behavior that ECharts or
  Lightweight Charts cannot provide cleanly.

Decision:

- The dashboard frontend is an application shell; the dashboard backend is an
  artifact reader. Neither side owns research truth, runtime truth, candidate
  truth, promotion truth, or approval truth.

## 4. Local-First Posture

The first implementation package must be local-first.

Locked requirements:

- No hosted server in the first implementation package.
- No public network exposure before an explicit auth/security package.
- The first FastAPI implementation must bind locally only.
- Hosted deployment is a later explicit package.
- Local-first operation must not require secrets, exchange credentials, provider
  credentials, paper/live accounts, scheduler activation, or notification
  firing.

Future implementation may use local browser access to the frontend and local
API calls to the read-only backend. That local loop remains an operator
inspection surface, not an execution or approval surface.

## 5. VPS and Hosting Posture

Facts:

- A VPS is not needed for the Phase 1 local-first dashboard.
- Remote or always-on access will need a later hosted-deployment package.

Minimum future VPS expectation for portal-only hosting:

- 2 vCPU.
- 4GB RAM.
- 40GB SSD.
- HTTPS-capable.
- Operator-only access.

Potential future paper/live host expectation:

- 4 vCPU.
- 8GB RAM.
- 80GB SSD.
- Persistent process management.
- Telemetry and log storage.
- Stronger monitoring.

Decision:

- Exact paper/live VPS sizing remains future and GO-gated. This package does not
  select a host, deploy a service, add Docker, add process management, add DNS,
  or create environment-variable requirements.

## 6. Auth and Security Posture

Locked requirements:

- Authentication is mandatory from the first hosted deployment.
- Local-first implementation must not expose the portal publicly.
- No hosted deployment may happen without an explicit auth/hosting package.
- When hosted, the API must not be reachable unauthenticated.
- No credentials, secrets, OAuth client ids, API keys, `.env` requirements, or
  secret-handling code are added by this package.

Future auth/security package must define at least:

- operator identity model;
- session/token posture;
- HTTPS and reverse-proxy posture;
- API authentication requirements;
- secret storage;
- allowed origin / network exposure policy;
- audit expectations for write-capable surfaces, if any exist by then.

## 7. Read-Only Dashboard Boundary

The future read-only dashboard may display:

- lab status;
- authority state;
- approvals needed;
- result populations;
- strategies;
- candidate funnel state;
- reports;
- data health;
- validator status;
- blockers;
- provenance;
- later paper/live placeholders;
- later authorized read-only paper/live telemetry snapshots.

The dashboard must not:

- run backtests;
- approve preregistration;
- approve execution;
- write canonical artifacts;
- write Strategy Specs;
- write Variant Manifests;
- write Sweep Plans;
- create candidates;
- cross candidates;
- promote strategies;
- trigger paper/live;
- send notifications;
- activate scheduler/autonomy;
- contact providers, exchanges, or brokers;
- mutate runtime or protected state.

Decision:

- All future `GET` dashboard endpoints belong to a read-only API package. Any
  endpoint or UI element that can write must be outside the read-only dashboard
  package and separately authorized.

## 8. Agent Inbox Boundary

The Agent Inbox is separate from the read-only dashboard API.

Locked requirements:

- Agent Inbox is its own later runway.
- Agent Inbox must not be bundled into the read-only API implementation.
- Agent Inbox may eventually create scratch-only intake packets only if a later
  package explicitly authorizes that exact write surface.
- Agent Inbox must not trigger prepare, execute, runner, gates, candidate,
  crossing, promotion, paper/live, scheduler, or notification behavior.
- Agent Inbox must not write canonical Strategy Spec, Variant Manifest, or Sweep
  Plan artifacts unless a future package explicitly authorizes that exact
  surface.

Contract implication:

- `POST /api/agent/intake-draft` is not part of the future read-only dashboard
  API. It belongs to the later isolated Agent Inbox runway.

## 9. Deferred Monitoring Sidecar

Grafana, Prometheus, Loki, TimescaleDB, and telemetry monitoring are deferred.

Locked requirements:

- They are future paper/live telemetry infrastructure, not part of this package.
- They must not be scheduled or implemented now.
- The dashboard architecture may contain placeholders or notes only.
- Monitoring sidecar work gets its own future package when telemetry exists.

Decision:

- The operator portal may show monitoring placeholders before telemetry exists,
  but it must not fabricate telemetry or imply paper/live readiness.

## 10. Portal Sections

The future portal information architecture must preserve these target sections:

- Command Center.
- Research Lab.
- Strategy Explorer.
- Candidate Funnel.
- Reports.
- System / Data.
- Agent Inbox.
- Paper Trading placeholder.
- Live Trading placeholder.

Paper and Live sections are placeholders until later authorized read-only
telemetry snapshots exist. They must not expose controls.

## 11. Route Targets

These are architectural targets only:

```text
/
/research
/research/jobs
/research/result-populations
/research/result-populations/{id}
/research/families
/research/blockers
/research/robustness
/strategies
/strategies/{strategy_id}
/strategies/{strategy_id}/variants
/strategies/{strategy_id}/wfo
/strategies/{strategy_id}/robustness
/strategies/{strategy_id}/artifacts
/candidates
/candidates/{candidate_id}
/reports
/reports/daily
/reports/weekly
/reports/strategy-review
/reports/main
/system
/system/data
/system/validators
/system/provenance
/system/blockers
/agent-inbox
/paper
/live
```

## 12. API Endpoint Targets

These are target contracts only and do not create implementation authority:

```text
GET /api/dashboard/summary
GET /api/research/jobs
GET /api/research/result-populations
GET /api/research/result-populations/{id}
GET /api/strategies
GET /api/strategies/{id}
GET /api/candidates/funnel
GET /api/reports/daily
GET /api/reports/weekly
GET /api/system/data-health
GET /api/agent/intake-schema
POST /api/agent/intake-draft
```

Endpoint ownership:

- All `GET` endpoints above are future read-only API targets.
- `POST /api/agent/intake-draft` belongs to the later isolated Agent Inbox
  runway, not to the read-only API package.

## 13. Truth and Data Flow

Future read-only data flow:

```text
committed repo artifacts / authorized read-only local snapshots
-> artifact readers and repo query surfaces
-> FastAPI read-only JSON contracts
-> Next.js operator portal
-> operator inspection only
```

Truth-source order:

- committed repo artifacts and locked repo docs;
- protected runtime truth only when a later package creates authorized read-only
  snapshots;
- API response as derived projection;
- frontend display as presentation only.

If the portal disagrees with repo artifacts, repo artifacts win. If the portal
disagrees with protected runtime/reconciliation truth after future read-only
runtime snapshots exist, protected truth wins.

## 14. Deferred Choices

Open questions for future packages:

- exact component library;
- exact frontend directory namespace;
- exact FastAPI package namespace;
- local dev port and process launch convention;
- API schema version naming;
- cache policy;
- chart data downsampling policy;
- auth provider and session model for hosting;
- deployment target and process manager;
- telemetry storage once paper/live monitoring exists.

Future options:

- preserve static cockpit generation as a fallback artifact view;
- use static dashboard contracts as seed input for FastAPI readers;
- add websocket or server-sent event refresh only after a later package proves it
  remains read-only and local-first;
- add hosted deployment after auth/security is locked.

None of these options are authorized by this document.

## 15. Non-Authority Summary

This architecture lock creates no:

- implementation;
- server process;
- frontend app;
- dependency change;
- config change;
- hosted deployment;
- auth implementation;
- monitoring implementation;
- canonical evidence;
- Strategy Spec, Variant Manifest, or Sweep Plan;
- candidate lifecycle record;
- crossing;
- promotion or readiness marker;
- scheduler or autonomy;
- notification firing;
- provider, broker, exchange, credential, paper/live, OMS, reconciliation, risk,
  safe-mode, or protected-path contact.

Future implementation packages must preserve these boundaries unless a later
package explicitly changes the allowed scope.
