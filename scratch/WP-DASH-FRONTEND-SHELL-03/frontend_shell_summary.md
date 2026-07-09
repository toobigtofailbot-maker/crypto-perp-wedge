# WP-DASH-FRONTEND-SHELL-03 — Frontend Shell Summary

## What was built

A local-first, read-only operator dashboard **frontend shell** in a new isolated
namespace `operator_dashboard_frontend/`. Presentation-only over the merged
read-only API (`tools/operator_dashboard_api`), rendering committed API-shaped
fixtures by default (no backend or network required to view).

Stack (per architecture lock §3): Next.js 14 App Router, React 18, TypeScript
(strict), Tailwind CSS. No charting/data/state/auth libraries — analytical
panels are later packages.

## Layout

- **AppShell**: sidebar + global status header + scrollable content region.
- **Sidebar** (`"use client"`): grouped navigation with active-route highlight
  via `usePathname` (navigation-only).
- **StatusHeader**: posture / read-only / paper / live badges from the
  dashboard-summary fixture.
- **PageHeader**: title + breadcrumb + per-page ReadOnly and Authority banners.
- **Primitives**: Card, CardTitle, StatCard, Badge, KeyValue.
- **States**: EmptyState, LoadingState, UnavailableState, PlaceholderCard.
- **ProvenanceFooter**: renders each envelope's source / provenance / warnings /
  withheld / unavailable.
- **ReportView**: compact report renderer (charting withheld by API).

## Routes (23)

- `/` Command Center — summary counts + paper/live placeholders.
- `/research` (index) + `jobs`, `result-populations` (fixture-backed) +
  `families`, `blockers`, `robustness` (scaffold placeholders).
- `/strategies` (list) + `/strategies/[strategy_id]` (fixture summary or
  unavailable placeholder; deep panels deferred).
- `/candidates` — registry rollup by status / verdict.
- `/reports` (index) + `daily`, `weekly` (fixture-backed) + `strategy-review`,
  `main` (scaffold placeholders).
- `/system` (index) + `data`, `validators`, `provenance` (fixture-backed) +
  `blockers` (scaffold placeholder).
- `/agent-inbox` — intake **schema preview only**, no form, no submit target.
- `/paper`, `/live` — honest "unavailable / GO-gated / not built" placeholders,
  no telemetry, no controls.

## Data behavior

- Default source: `src/lib/fixtures/*.json`, generated from the read-only API via
  FastAPI TestClient and committed verbatim. Typed via `src/lib/types.ts`
  mirrors of the `ApiEnvelope`.
- Optional `src/lib/apiClient.ts`: GET-only wrapper for a locally running API,
  **not imported by any page**. No POST/PUT/PATCH/DELETE helper exists.

## Boundary preserved

Read-only shell only. No controls, no writes, no Agent Inbox write, no
paper/live telemetry or controls, no notifications, no scheduler, no hosted
deployment, no auth, no Grafana/monitoring, no runtime/paper/live/provider
contact, no canonical/candidate writes. The API package was read, not modified.
See `no_control_evidence.md` and `non_authority_assertions.json`.

## Validation

See `validation_summary.txt`. Backend/repo validators pass here. Node-based
frontend checks (`install`/`typecheck`/`lint`/`build`) could not run because
Node/npm are not installed on this environment; commands are documented for the
operator.

## Deferred (out of scope for this shell)

Analytical panels (heatmaps, funnels, equity/drawdown, variant/WFO/robustness
tables, provenance graphs), dynamic per-item API detail wiring, Agent Inbox
write intake, hosted deployment/auth, charting libraries, and paper/live
telemetry — each a later, separately authorized package.
