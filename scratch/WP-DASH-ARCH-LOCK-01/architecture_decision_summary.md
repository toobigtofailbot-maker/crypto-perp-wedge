# WP-DASH-ARCH-LOCK-01 Architecture Decision Summary

## Facts

- Current dashboard/cockpit surfaces are static, local/offline, and read-only.
- The current product cockpit now renders real product-run fixtures but still
  creates no server, controls, scheduler, notification, or runtime authority.
- PR #625, PR #626, and PR #627 are merged into current `main`.
- No FastAPI backend, Next.js frontend, package manifest, hosted deployment,
  auth implementation, monitoring sidecar, or Agent Inbox implementation exists
  in current repo truth.
- Existing static-dashboard design remains valid for static MVP surfaces and
  does not authorize a server retrofit.

## Inferences

- A proper operator portal is now an architecture/productization need, but it
  must remain a derived presentation surface over repo truth.
- The portal should start local-first to preserve the no-public-exposure,
  no-secret, no-hosting boundary while the read-only contracts are established.
- Agent Inbox is the first plausible write surface, so it must be isolated from
  the read-only API and handled as a later scratch-write runway.
- Grafana/Prometheus/Loki are premature until paper/live telemetry exists.

## Decisions

- Future portal frontend direction: React / Next.js / TypeScript / Tailwind.
- Future backend direction: FastAPI / Pydantic read-only artifact-reader API.
- Charting direction: ECharts, TradingView Lightweight Charts, and Plotly only
  where needed.
- First implementation posture: local-first, local bind only, no hosted server.
- Hosted deployment posture: later explicit package only; auth mandatory before
  first hosted deployment.
- Agent Inbox posture: separate future runway; not bundled into read-only API.
- Monitoring posture: Grafana / Prometheus / Loki / TimescaleDB deferred until
  telemetry exists.

## Open Questions

- Exact frontend and backend directory names.
- Component library selection.
- API schema version naming and contract layout.
- Local dev port and process launch convention.
- Hosted auth provider, session model, and secret storage.
- Deployment target and process manager.
- Telemetry storage model once paper/live telemetry exists.

## Future Options

- Reuse current static dashboard/cockpit contracts as seed inputs for API
  readers.
- Preserve generated static cockpit output as a fallback inspection artifact.
- Add local-only live refresh after a future package proves read-only behavior.
- Add hosted deployment after auth/security is locked.
- Add Agent Inbox scratch draft writes after a separate package locks exact
  schema, storage location, and non-authority constraints.

None of these future options are implemented or authorized by this package.
