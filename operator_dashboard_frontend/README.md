# Operator Dashboard Frontend Shell

Local-first, **read-only** operator dashboard frontend shell
(`WP-DASH-FRONTEND-SHELL-03`).

This is a presentation-only application shell over the read-only dashboard API
(`tools/operator_dashboard_api`). It renders committed **API-shaped fixtures** by
default, so it runs with no backend, no network contact, and no runtime, paper,
or live contact.

## Boundary (what this shell is NOT)

This shell has **no controls and no write paths**. It does not run backtests,
approve, execute, promote, cross, trade, start paper/live, send notifications,
activate a scheduler, write the Agent Inbox, mutate runtime/protected state,
deploy to a host, or implement auth. The only interactivity is navigation. The
optional `src/lib/apiClient.ts` performs `GET` requests only and is not imported
by any page.

Committed repo artifacts remain truth. Everything shown here is a derived
read-only projection.

## Stack

- Next.js 14 (App Router) · React 18 · TypeScript
- Tailwind CSS (dark operator-cockpit posture)
- No charting/data/state/auth libraries (analytical panels are later packages)

## Layout

```
src/
  app/            App Router pages (see Routes below) + layout + globals.css
  components/     AppShell, Sidebar, StatusHeader, PageHeader, banners,
                  cards, states, ReportView, ProvenanceFooter
  lib/
    nav.ts        Sidebar navigation model
    types.ts      TypeScript mirrors of the API envelope
    fixtures.ts   Typed accessors over committed fixtures
    apiClient.ts  Optional GET-only client (unused by default)
    fixtures/     API-shaped JSON generated from the read-only API
```

## Routes

`/` · `/research` (+ `jobs`, `result-populations`, `families`, `blockers`,
`robustness`) · `/strategies` (+ `[strategy_id]`) · `/candidates` · `/reports`
(+ `daily`, `weekly`, `strategy-review`, `main`) · `/system` (+ `data`,
`validators`, `provenance`, `blockers`) · `/agent-inbox` · `/paper` · `/live`.

Pages backed by fixture data: Command Center, Research Jobs, Result Populations,
Strategies (+ detail summary), Candidates, Reports Daily/Weekly, System
Data/Validators/Provenance, Agent Inbox, Paper, Live. Remaining routes are
honest scaffolds whose analytical panels are built by later packages.

## Fixtures

Fixtures under `src/lib/fixtures/` are generated from the merged read-only API
(`tools.operator_dashboard_api.app`) via FastAPI `TestClient`. To regenerate
against current committed artifacts, run from the repo root:

```powershell
.\.venv\Scripts\python.exe - <<'PY'
import json
from pathlib import Path
from fastapi.testclient import TestClient
from tools.operator_dashboard_api.app import app
out = Path("operator_dashboard_frontend/src/lib/fixtures")
client = TestClient(app)
endpoints = {
  "dashboard_summary": "/api/dashboard/summary",
  "research_jobs": "/api/research/jobs",
  "result_populations": "/api/research/result-populations",
  "strategies": "/api/strategies",
  "candidates_funnel": "/api/candidates/funnel",
  "reports_daily": "/api/reports/daily",
  "reports_weekly": "/api/reports/weekly",
  "system_data_health": "/api/system/data-health",
  "agent_intake_schema": "/api/agent/intake-schema",
}
for name, path in endpoints.items():
    r = client.get(path); r.raise_for_status()
    (out / f"{name}.json").write_text(json.dumps(r.json(), indent=2) + "\n", encoding="utf-8")
PY
```

## Develop / validate (requires Node.js)

> **Note:** Node.js/npm were not installed in the environment where this shell
> was authored, so `npm install`, `npm run typecheck`, `npm run lint`, and
> `npm run build` were **not executed here**. Run them in a Node-equipped
> environment.

```bash
cd operator_dashboard_frontend
npm install
npm run typecheck
npm run lint
npm run build
npm run dev      # http://localhost:3000
```

`node_modules/`, `.next/`, and `next-env.d.ts` are gitignored.

### Optional: point the shell at a locally running API

By default the shell uses fixtures. To inspect a live local API instead, run the
read-only backend locally (it binds locally only) and use `readOnlyApiClient`
from `src/lib/apiClient.ts`. This remains a read-only, local-first inspection
loop; it adds no control surface.
