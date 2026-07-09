# WP-DASH-FRONTEND-SHELL-03 Branch State

## Scope Summary

Adds the first local-first, **read-only** operator dashboard **frontend shell**
in a new isolated namespace `operator_dashboard_frontend/`. It is presentation
only over the merged read-only dashboard API (`tools/operator_dashboard_api`),
rendering committed API-shaped fixtures by default so it needs no backend and
makes no network, runtime, paper, or live contact.

The package creates no controls, no write paths, no Agent Inbox write, no
paper/live telemetry or controls, no notifications, no scheduler, no hosted
deployment, no auth, no monitoring, no charting libraries, no canonical/candidate
writes, and no provider/runtime/protected-path contact. The read-only API
package was read for its contract and fixtures only and was **not modified**.

## Delivered

Frontend shell (`operator_dashboard_frontend/`):

- Toolchain: `package.json`, `tsconfig.json`, `next.config.mjs`,
  `postcss.config.mjs`, `tailwind.config.ts`, `.eslintrc.json`, `.gitignore`,
  `README.md` (isolated; no root/dependency changes; `node_modules/`, `.next/`,
  `next-env.d.ts` gitignored).
- App Router: `src/app/layout.tsx`, `globals.css`, and 23 route pages —
  Command Center; Research (index, jobs, result-populations, families, blockers,
  robustness); Strategies (list + `[strategy_id]`); Candidates; Reports (index,
  daily, weekly, strategy-review, main); System (index, data, validators,
  provenance, blockers); Agent Inbox; Paper; Live.
- Components: `AppShell`, `Sidebar`, `StatusHeader`, `PageHeader`, `Banners`
  (ReadOnly/Authority), `ui` (Card/StatCard/Badge/KeyValue), `States`
  (Empty/Loading/Unavailable/Placeholder), `ReportView`, `ProvenanceFooter`.
- Lib: `nav.ts`, `types.ts` (ApiEnvelope mirrors), `fixtures.ts` (typed
  accessors), `apiClient.ts` (GET-only, unused by default), and
  `src/lib/fixtures/*.json` generated from the read-only API.

Docs / evidence:

- `docs/status_entries/WP-DASH-FRONTEND-SHELL-03.md`
- `scratch/WP-DASH-FRONTEND-SHELL-03/repo_truth_discovery.md`
- `scratch/WP-DASH-FRONTEND-SHELL-03/frontend_shell_summary.md`
- `scratch/WP-DASH-FRONTEND-SHELL-03/no_control_evidence.md`
- `scratch/WP-DASH-FRONTEND-SHELL-03/non_authority_assertions.json`
- `scratch/WP-DASH-FRONTEND-SHELL-03/validation_summary.txt`

## Boundary

Read-only frontend shell only. No controls; no Agent Inbox write; no
hosting/auth/paper-live/runtime contact; no API change. Existing dashboard/
cockpit/API surfaces are read, not modified. No `src/**`, `lib/**`, `configs/**`,
`.claude/**`, `data/**`, `tools/**`, `tests/**`, schema/validator/query-layer,
canonical evidence, candidate lifecycle, crossing, promotion, or readiness paths
are changed.

## Validation

Backend/repo validators pass (recorded in
`scratch/WP-DASH-FRONTEND-SHELL-03/validation_summary.txt`): the API test suite,
JSON assertion parse, research-query view listing, result-population and
candidate-registry validators, diff-scope summary (no forbidden-path matches),
and whitespace checks.

Node.js/npm are not installed in this environment, so the frontend
`npm install` / `typecheck` / `lint` / `build` were **not executed here**; the
exact commands are documented in the frontend `README.md` and validation summary
for an operator to run in a Node-equipped environment.
