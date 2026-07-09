# WP-DASH-ARCH-LOCK-01 Repo-Truth Discovery

Base branch: `main`

Base SHA: `ec5b42b8cc1331478757379aeeb0eb735c90c5a8`

Working branch: `codex/wp-dash-arch-lock-01`

## 1. Current Cockpit Implementation Status

Fact:

- `tools/lab_cockpit` exists with `model.py`, `render.py`, and `run.py`.
- `docs/research/LAB_PRODUCT_COCKPIT_SURFACE.md` describes it as a static,
  read-only product cockpit.
- `docs/research/LAB_PRODUCTIZATION_COCKPIT_REALRUN_REFRESH.md` records the
  real-run refresh for product bridge prepare -> product runner adapter ->
  product gates adapters.
- `docs/status_entries/WP-LABPROD-COCKPIT-REALRUN-REFRESH-08.md` records that
  the cockpit now projects committed real product-run fixtures and remains
  visualization only.

Inference:

- The cockpit is useful current repo truth, but it is not a proper application
  portal and it intentionally has no server or controls.

## 2. Current Cockpit Run Command and Artifact Behavior

Fact:

- Product cockpit command:
  `python -m tools.lab_cockpit.run --out-dir build/lab_cockpit`.
- The command writes `cockpit_data.json`, `cockpit.html`, and `cockpit.md`.
- The product cockpit doc says the page is usable from a local file or static
  output directory.
- Static/no-control guarantees include no server, live fetch, network,
  background daemon, auto-refresh, form submission, JavaScript, button, form,
  input, onclick, meta refresh, or external network reference.

Fact:

- Older `tools/dashboard` command:
  `python -m tools.dashboard.generate_static_dashboard --output-dir dashboard_build --data-dir dashboard_data --repo-root .`.
- It writes `dashboard_data/dashboard_data.json` and `dashboard_build/index.html`
  after validating `dashboard_data.v1`.

## 3. Current Dashboard and Cockpit Docs

Read docs:

- `docs/dashboard/README.md`
- `docs/research/LAB_RESULTS_DASHBOARD_SURFACE.md`
- `docs/research/LAB_VISUAL_COCKPIT_SURFACE.md`
- `docs/research/LAB_PRODUCT_COCKPIT_SURFACE.md`
- `docs/research/LAB_PRODUCT_COCKPIT_PIPELINE_STATE.md`
- `docs/research/LAB_PRODUCTIZATION_COCKPIT_REALRUN_REFRESH.md`
- `docs/architecture/2026-06-local_static_dashboard_design.md`
- `docs/research_pipeline/2026-05-phase3_monitoring_dashboard_sketch.md`

Findings:

- Existing dashboard lines are read-only and static/offline.
- `docs/architecture/2026-06-local_static_dashboard_design.md` locks a
  no-server, no-JavaScript-build-pipeline, no-auth MVP for the earlier static
  dashboard track.
- `docs/research_pipeline/2026-05-phase3_monitoring_dashboard_sketch.md` is a
  monitoring/dashboard sketch only and does not authorize implementation.
- No existing doc found a stronger lock for a Next.js / FastAPI operator portal
  plus isolated Agent Inbox.

## 4. Current Agent-Orchestration Status

Read docs:

- `docs/research/LAB_PRODUCTIZATION_PIPELINE_ORCHESTRATOR.md`
- `docs/research/LAB_PRODUCTIZATION_PIPELINE_AGENT_ADAPTERS.md`
- `docs/research/LAB_PRODUCTIZATION_LAB_QUEUE_STATUS.md`
- `docs/research/LAB_APPROVAL_QUEUE_SURFACE.md`
- `docs/status_entries/WP-LAB-APPROVAL-QUEUE-SURFACE-01.md`
- `docs/status_entries/WP-LAB-AGENTLOOP-BASELINE-EXERCISE-01.md`
- `docs/status_entries/WP-LAB-AGENTLOOP-DASHBOARD-REPLAY-01.md`
- `docs/status_entries/WP-LAB-SIDE12-OPERATING-READINESS-AUDIT-01.md`

Findings:

- `tools/lab_pipeline` is an operator-invocable deterministic offline pipeline
  state spine with exact-content prereg approval discipline.
- Agent adapter flow is package-local, scratch-only, non-canonical, and entered
  only after required approval validation.
- Queue/status visibility is read-only and does not invoke the orchestrator,
  runner adapter, gates adapter, scheduler, notification system, provider/API,
  paper/live/runtime, or protected paths.
- Agent-loop/dashboard replay evidence is operating-test evidence only. It
  creates no real agent autonomy, candidate lifecycle write, crossing, promotion,
  readiness, strategy run, edge search, or protected-path touch.

Inference:

- Agent Inbox can be a future scratch-intake runway only if isolated from the
  read-only dashboard API and separately authorized.

## 5. FastAPI / Next.js / Dashboard App Existence Check

Searches:

- `rg -n "FastAPI|Next\\.js|NextJS|React|TypeScript|Tailwind|Agent Inbox|agent inbox|Grafana|Prometheus|Loki|\\bVPS\\b|hosted deployment|operator portal|operator dashboard|dashboard architecture|authentication|\\bauth\\b" docs tools -S --glob '!scratch/**'`
- `rg --files . | rg "(^|/)(package\\.json|pnpm-lock\\.yaml|package-lock\\.json|yarn\\.lock|next\\.config\\.|app/|pages/|src/app|pyproject\\.toml|requirements.*\\.txt)$|fastapi|FastAPI"`
- Directory scan for `app`, `pages`, `frontend`, `web`, `server`, `api`, and
  dashboard/portal/FastAPI/Next namespaces.

Findings:

- No `package.json`, lockfile, Next.js config, frontend app, FastAPI server, or
  portal app exists in the current tree.
- Existing dashboard directories are `docs/dashboard`, `tools/dashboard`,
  `tools/lab_dashboard`, and `tools/lab_cockpit`.

## 6. Existing Auth / Deployment Guidance

Findings:

- Existing static dashboard architecture explicitly deferred or forbade auth and
  hosting for the earlier static MVP.
- No current auth implementation, hosted deployment implementation, or portal
  deployment guide was found.
- `docs/architecture/event_log_schema.md` mentions auth headers only as event
  payload considerations, not as portal auth guidance.

Decision supported:

- Auth/security and hosted deployment must be later explicit packages.

## 7. Exact Merged Evidence for PR #625 / #626 / #627

GitHub / git evidence:

- PR #625: `WP-LABPROD-LAB-QUEUE-STATUS-07: Add lab queue status visibility`,
  merged at `2026-07-09T16:09:47Z`, merge commit
  `99201f84bd6c6871439cf78a5d00eb5d0deffe79`.
- PR #626: `WP-LABPROD-BOUNDED-SWEEP-SCALE-06: Enforce bounded sweep scale`,
  merged at `2026-07-09T16:09:58Z`, merge commit
  `ec5b42b8cc1331478757379aeeb0eb735c90c5a8`.
- PR #627: `WP-LABPROD-COCKPIT-REALRUN-REFRESH-08: refresh cockpit for real
  product runs`, merged at `2026-07-09T16:09:36Z`, merge commit
  `9342adf5502f4130cea831b4ffc2356ecebf9c25`.

Repo evidence:

- `docs/status_entries/WP-LABPROD-LAB-QUEUE-STATUS-07.md`
- `docs/status_entries/WP-LABPROD-BOUNDED-SWEEP-SCALE-06.md`
- `docs/status_entries/WP-LABPROD-COCKPIT-REALRUN-REFRESH-08.md`
- `docs/research/LAB_PRODUCTIZATION_LAB_QUEUE_STATUS.md`
- `docs/research/LAB_PRODUCTIZATION_BOUNDED_SWEEP_SCALE.md`
- `docs/research/LAB_PRODUCTIZATION_COCKPIT_REALRUN_REFRESH.md`

## 8. Open PR and Branch Checks

Fact:

- No local or remote branch named `codex/wp-dash-arch-lock-01` existed before
  package branch creation.
- `gh pr list --state open --json number,title,headRefName,baseRefName,url,files --limit 100`
  returned `[]`.

Decision:

- No open PR was found implementing the same operator portal architecture.
- No open PR was found touching `docs/project_status.md`.

## 9. Contradictions With Requested Architecture

Fact:

- Existing static dashboard architecture forbids React/server/auth for the
  earlier MVP.

Inference:

- This is not a contradiction if the new operator portal is treated as a later
  local-first application architecture and not a change to the existing static
  dashboard MVP line.

Decision:

- The architecture lock must state that current static cockpit/dashboard
  boundaries remain true and that the Next.js/FastAPI direction applies only to
  future explicit operator-portal implementation packages.

## 10. Forbidden Scope Check

Package work must not modify:

- `src/**`
- `lib/**`
- `configs/**`
- `.claude/**`
- `data/**`
- runtime / OMS / risk / reconciliation / safe-mode paths
- paper/live paths
- exchange/broker/provider/API/credential files
- scheduler/autonomy code
- notification firing code
- current cockpit Python implementation
- runner / bridge / gates adapters
- canonical evidence artifacts
- candidate registry / lifecycle artifacts
- schemas / validators / query-layer code
- dependency files or deployment files

Planned changed files are docs/status/scratch only.
