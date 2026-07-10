# WP-DASH-CHARTS-PANELS-05 — Repo-truth discovery

Base: `main` @ `74e6464` (includes `WP-DASH-PANELS-04`, merged as `b01d15e`).
Branch: `claude/wp-dash-charts-panels-05-4d1f75`.

## 1. Hard dependency check

| Dependency | Result |
| --- | --- |
| `WP-DASH-PANELS-04` merged | yes (`b01d15e`) |
| `operator_dashboard_frontend/` exists | yes |
| `package.json` + `package-lock.json` exist | yes |
| Node / npm available | Node `v24.18.0`, npm `11.16.0` |
| Baseline `npm ci` / `typecheck` / `lint` / `build` | all pass |
| `tools/operator_dashboard_api` exists and unchanged | yes; untouched by this package |
| No open PR already adding dashboard charting | none found |
| No data contract exposes chart-ready values that must read as authority | see §6 — resolved, with mitigations |

## 2. Current frontend dependency versions (before this package)

Runtime: `next 14.2.35`, `react 18.3.1`, `react-dom 18.3.1`.
Dev: `typescript 5.5.3`, `tailwindcss 3.4.6`, `eslint 8.57.0`, `eslint-config-next 14.2.35`,
`postcss 8.4.39`, `autoprefixer 10.4.19`, `@types/*`.

No charting dependency of any kind was present.

## 3. Existing components / helpers that render panel summaries

- `src/components/viz.tsx` — CSS-only primitives: `Meter`, `CountBars`, `StackedBar`, `Funnel`.
- `src/components/ui.tsx` — `Card`, `CardTitle`, `StatCard`, `Badge`, `KeyValue`.
- `src/components/States.tsx` — `UnavailableState`, `EmptyState`, `LoadingState`, `PlaceholderCard`.
- `src/components/BoundaryNotes.tsx` — renders `warnings` / `withheld` / `unavailable` per envelope.
- `src/components/ProvenanceFooter.tsx` — renders envelope provenance refs.
- `src/components/ReportView.tsx` — report envelope renderer.
- `src/lib/status.ts` — `toneForStatus`, `humanize`, `sumCounts`.
- `src/lib/fixtures.ts` — API-shaped fixture accessors.
- `src/lib/apiClient.ts` — optional GET-only client, imported by no page.

## 4. Available API-shaped fixtures (before this package)

All generated from `tools.operator_dashboard_api.app` GET endpoints via FastAPI `TestClient`.

`dashboard_summary`, `research_jobs`, `result_populations` (list), `strategies`,
`candidates_funnel`, `reports_daily`, `reports_weekly`, `system_data_health`,
`agent_intake_schema`.

## 5. Exact fields available for charting

### 5.1 Categorical / count data (present, chartable)

| Envelope | Field | Shape |
| --- | --- | --- |
| `dashboard_summary` | `queue_summary.by_status` | 8 committed statuses |
| `dashboard_summary` | `counts.*`, `product_run_summary.*` | scalar tiles |
| `candidates_funnel` | `product_candidate_funnel.stages[]` | 5 stages, committed order |
| `candidates_funnel` | `candidate_registry.by_status` / `.by_overall_verdict` | 2 + 2 buckets |
| `result_populations` | `items[].outcome_counts` | 9 outcome buckets + 2 bookkeeping keys |
| `strategies` | `items[].primary_timeframe` / `.direction` / … | committed facets, 6 specs |
| `reports_daily` / `reports_weekly` | `report.counts.by_overall_state` | 13 states, 5 non-zero |
| `system_data_health` | `d4_slice.gap_facts.{gap_count,missing_bar_count,gaps[]}` | `gaps: []`, 0 gaps |

### 5.2 Numeric per-variant metrics (present, chartable — not anticipated by the brief)

`GET /api/research/result-populations/{id}` (already merged, unchanged) projects
`variant_result_rows[].metrics` verbatim via `readers.py::_variant_rows`:

`drawdown`, `exposure`, `fees`, `funding`, `pnl`, `return_pct`, `sharpe`,
`slippage`, `trade_count`, `win_rate`.

Population: **66 variant rows across 8 committed result populations**, every row carrying
a finite `return_pct` and `drawdown`. Every population's `parent_strategy_spec_id`
resolves to a committed strategy spec, so a per-strategy drilldown is real.

Observed ranges (offline research runs): `return_pct` −1.0000 … 5.0472;
`drawdown` 0.0052 … 1.0000; `sharpe` −28.7555 … 1.2477; `trade_count` 9 … 12 962.

No fixture for this endpoint existed. One was generated per artifact from the **unchanged**
API via `TestClient` — the same provenance path as every other committed fixture.

### 5.3 Absent (must not be drawn)

| Wanted chart | Classification | Repo truth |
| --- | --- | --- |
| Equity curve | **deferred** | No per-bar / per-trade equity series is projected anywhere. `_variant_rows` projects scalars only. Exposing one needs a backend change (forbidden, and a stop condition). |
| Drawdown *curve* over time | **deferred** | `drawdown` is committed as a scalar max per variant, not a series. |
| Per-trade return distribution | **withheld** | `result_populations` envelope: `withheld.per_trade_distributions = "Only fields committed in each result population artifact are projected."` |
| Monte Carlo / robustness distribution | **withheld** | Report rows carry `withheld_statistics: ["PSR","DSR","MinTRL"]` — named, never valued. `robustness_state` is `not_started` for 8 of 10 runs. |
| Walk-forward (WFO) windows | **deferred** | No folds, windows, or per-fold statistics are projected. |
| Candle / OHLCV series | **deferred** | `system_data_health` projects slice identity, row counts, and gap facts — not bars. |
| Paper / live telemetry | **unavailable** | `dashboard_summary.unavailable.paper_live_telemetry = "No paper/live read-only snapshot is authorized or present."` |

Additionally, both report envelopes carry `withheld.charting = {enabled: false, note: "Charting
deferred: weekly report is table-based static output only; no safe dependency-light static-chart
path is adopted."}`. This flag governs the **report artifact's own embedded output**, produced by
`tools/lab_reporting` — not the dashboard's presentation of the counts the envelope already
exposes. The flag is left untouched, still surfaced by `BoundaryNotes` and by `ReportView`'s
footnote, and no withheld statistic is drawn.

## 6. Authority risk assessment (hard dependency 7)

Charting `return_pct`, `drawdown`, and `sharpe` is the one place this package could manufacture
false visual authority. Findings that make it safe to render, and the mitigations applied:

- The values are committed artifact fields, read verbatim. Nothing is computed, scored, or ranked.
- Every population declares `execution_mode: "offline_research"`, `offline_only: true`,
  `no_runtime_contact: true`, `no_paper_live_contact: true`.
- Every population carries a `non_authority_declaration` and a `review.non_authority_acknowledgement`
  (`not_approval`, `not_readiness`, `not_recommendation`, `not_runtime_authority`, …).
- `candidate_admitted_count` is `0`; the registry is 11 `NO-GO` + 1 `DRAFT`. No candidate exists to
  be flattered by a chart.

Mitigations, applied in code:

- No chart sorts by a metric, marks a best variant, or draws a threshold line.
- The scatter states in its own copy that no quadrant is preferred.
- Every chart carries a `ChartProvenanceNote` naming source endpoint, committed fields, derived
  display quantities, rows drawn, rows dropped, and an explicit non-authority sentence.
- Full committed denominators are charted; no winner-only slice is taken.
- Rows lacking a value are dropped and **counted**, never zero-filled.

## 7. Chosen charting dependency

`echarts@6.1.0`, exact-pinned, imported tree-shaken from `echarts/core`. See
`dependency_decision.md` for the audit trail and the rejection of `echarts-for-react`.

## 8. Dependency audit before / after

`npm audit --omit=dev`:

- **Before:** 2 vulnerabilities (1 high, 1 moderate) — `next` and its bundled `postcss`.
  Fix requires `next@16` (semver-major); already evaluated under `WP-DASH-FRONTEND-NEXT16-EVAL-03B`.
- **After `echarts@5.5.1` (rejected):** 3 (1 high, 2 moderate) — added GHSA-fgmj-fm8m-jvvx,
  an XSS affecting all `echarts < 6.1.0`.
- **After `echarts@6.1.0` (adopted):** 2 (1 high, 1 moderate). Identical to baseline.
  `echarts` and `zrender` are not flagged.

No audit result is suppressed, and no `audit fix --force` was run.

## 9. No-control constraints found in the current shell

- `apiClient.ts` defines GET helpers only, with no generic `request(method, …)` escape hatch, and
  is imported by no page.
- No page contains a `<form>`, `<button>`, `onClick`, or `onSubmit`.
- `agent-inbox`, `paper`, and `live` are honest placeholders; `POST /api/agent/intake-draft` is
  documented as intentionally not implemented.
- `Sidebar.tsx` was the only pre-existing `"use client"` component.

These constraints are preserved. Charts add four `"use client"` components whose only client state
is the ECharts instance and a `ResizeObserver`. See `no_control_evidence.md`.
