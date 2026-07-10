# Runtime discovery

- Isolated worktree: `C:/GitHub/crypto-perp-wedge-wp-inbox-local-runbook-01`
- Branch: `codex/wp-inbox-local-runbook-01`
- Base: `b2f1f480411fa29684f8e9ee5d4375f8400ce9c7`
- Base commit: merge of PR #644 (`WP-INBOX-ASGI-SERVER-DEPS-00`)
- Launch worktree: `C:/GitHub/crypto-perp-wedge`
- Launch branch: `codex/wp-dash-artifact-projections-04`
- Launch worktree was not switched or edited.

## Repo-truth findings

- `requirements.txt` declares `uvicorn`; `requirements.lock.txt` locks
  `uvicorn==0.51.0` and its resolver dependencies.
- `tools.agent_inbox_intake.app:app` is the isolated FastAPI app.
- Intake owns `POST /api/agent/intake-draft` and read-only history at
  `GET /api/agent/drafts` and `GET /api/agent/drafts/{draft_id}`.
- Default packet storage is
  `scratch/WP-DASH-AGENT-INBOX-WRITE-01A/drafts/`.
- The dashboard same-origin route forwards only the intake POST to the origin in
  server-only `AGENT_INBOX_SERVICE_ORIGIN`; there is no default origin.
- The frontend uses Next.js `next dev`; its documented development port is 3000.
- `tools/dev/` contains bounded advisory/validation utilities but no existing
  service-process launcher convention. Separate operator-owned terminals are
  therefore the narrower repo-idiomatic choice for this package.

## Boundary decision

Runbook-only implementation. No process supervisor or launcher was added. No
frontend, intake-service, dashboard-API, dependency, config, runtime, canonical,
queue, research-execution, scheduler, notification, paper, or live path is
modified.
