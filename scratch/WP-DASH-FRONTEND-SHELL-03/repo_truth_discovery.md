# WP-DASH-FRONTEND-SHELL-03 — Repo-Truth Discovery

## Preflight state

- Effective base: `main` at merge `54d12c5` (PR #630, `WP-DASH-READONLY-API-02B`).
- Hard dependency satisfied: the read-only API package is merged. `tools/operator_dashboard_api/{app,models,readers}.py` exposes the 11 GET endpoints and no mutation route.
- Working tree clean before implementation; branch `claude/wp-dash-frontend-shell-a2f4c0` is the active worktree branch.
- `tests/test_operator_dashboard_api.py` passes on base (11 passed).

## Frontend tooling / package convention

- **No `package.json` exists anywhere in the repo** (searched repo-wide, excluding `node_modules`). No `tsconfig.json`, `next.config.*`, or `*.tsx` exist. This is a greenfield frontend surface.
- `AGENTS.md` contains no frontend/Node/dependency policy (grep for depend/npm/node/frontend/package.json/typescript/react/next returned nothing). No repo convention constrains the choice.
- The architecture lock (`docs/architecture/operator_dashboard_agent_inbox_architecture_lock.md`, §3) already **decided the stack**: React / Next.js / TypeScript / Tailwind CSS, component library deferred, ECharts + TradingView Lightweight Charts for later analytical panels. This package builds the shell only and adds **no charting libraries** yet.

## Node/npm availability — IMPORTANT

- **Node.js and npm are not installed on this environment** (not on the Git Bash PATH, not on the Windows PATH; `node`/`npm` both resolve to nothing).
- Consequence: `npm install`, `npm run typecheck`, `npm run lint`, and `npm run build` **cannot be executed here**. No lockfile can be generated locally.
- This does not block the deliverable: the frontend shell is source-only and its toolchain is added in an isolated namespace with **zero root/dependency changes**. Per §13 the stop conditions are about whether the toolchain can be *added narrowly* (it can) — not whether Node happens to be installed on this box.
- The status entry, `validation_summary.txt`, and the frontend `README.md` record the exact Node commands the operator must run in a Node-equipped environment, and flag that Node-based checks were **not run here**.

## Proposed frontend directory and why

- Namespace: **`operator_dashboard_frontend/`** at repo root.
  - No existing convention to follow; §14 of the lock lists "exact frontend directory namespace" as a deferred choice for the first frontend-shell package (this package).
  - Mirrors the backend namespace `tools/operator_dashboard_api/` in intent (operator dashboard, read-only), while keeping the Node project self-contained and out of `tools/` (which is Python-only).
  - Fully isolated: no root `package.json`, no monorepo wiring, no root dependency/lock file touched.

## Dependency / toolchain additions (isolated to the new namespace)

Declared in `operator_dashboard_frontend/package.json` only:

- Runtime: `next@14.2.x`, `react@18.3.x`, `react-dom@18.3.x`.
- Dev: `typescript@5`, `@types/{node,react,react-dom}`, `tailwindcss@3.4.x`, `postcss`, `autoprefixer`, `eslint@8`, `eslint-config-next@14.2.x`.
- No charting libs, no data/state libs, no auth libs, no server/deploy tooling. `node_modules/`, `.next/`, and `next-env.d.ts` are gitignored via a package-local `.gitignore`.

## API endpoints consumed / stubbed

The shell consumes **API-shaped fixtures generated from the merged read-only API** (`src/lib/fixtures/*.json`, produced via `TestClient` over `tools.operator_dashboard_api.app`). A GET-only `apiClient.ts` wrapper is provided but **not used by default** (local-first, no runtime contact). Endpoints represented:

- `/api/dashboard/summary`, `/api/research/jobs`, `/api/research/result-populations`,
  `/api/strategies`, `/api/candidates/funnel`, `/api/reports/daily`, `/api/reports/weekly`,
  `/api/system/data-health`, `/api/agent/intake-schema`.

Detail routes (`/api/research/result-populations/{id}`, `/api/strategies/{id}`) are represented by list fixtures; per-item detail pages render honest "detail projection deferred" placeholders (deferred dynamic data, documented below).

## Pages / routes implemented

All routes from §10.1 of the package (and §11 of the lock) as App Router pages:
`/`, `/research`(+ jobs, result-populations, families, blockers, robustness),
`/strategies` (+ `[strategy_id]`), `/candidates`, `/reports` (+ daily, weekly, strategy-review, main),
`/system` (+ data, validators, provenance, blockers), `/agent-inbox`, `/paper`, `/live`.

Deferred dynamic data (documented, not silently dropped):
- `/strategies/[strategy_id]` renders the fixture summary for a matched id, otherwise an unavailable placeholder; deep per-strategy variants/WFO/robustness/artifacts panels are later panel packages.
- `families`, `robustness`, `strategy-review`, `main`, `validators`, `provenance`, `blockers` render honest scaffold/empty-state cards; their analytical panels are later packages.

## No-control checks

- No `<form>` submit-to-API, no POST/PUT/PATCH/DELETE, no mutation `fetch`, no run/approve/execute/promote/cross/trade/paper-live/notification/scheduler controls.
- Only interactive elements are navigation `<Link>`s (sidebar/cards). The optional `apiClient.ts` performs `GET` only.
- `/agent-inbox` shows the intake **schema preview** and an explicit "no submit / write is a later package" notice — no wired submit button.
- `/paper` and `/live` are honest "not built / GO-gated / unavailable" placeholders with no telemetry and no controls.
- Full evidence in `no_control_evidence.md`.

## Deferred pages/panels

Analytical panels (heatmaps, funnels, equity/drawdown, variant tables, WFO, robustness, provenance graphs) and Agent-Inbox write intake are explicitly **out of scope** for this shell and belong to later panel/write packages.
