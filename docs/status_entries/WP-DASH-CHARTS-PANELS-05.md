# WP-DASH-CHARTS-PANELS-05 Status Entry

## Scope

First real chart layer over the already-merged, isolated `operator_dashboard_frontend/`
read-only operator dashboard. Presentation only: one charting dependency is added and
committed read-only data is drawn. The dashboard gains no control, write, runtime, or
candidate authority.

## Decision

Delivered. Eleven chart panels render from committed data across Command Center, Result
Populations, Strategies (list + detail), Candidates, Reports (daily + weekly), and System
Data. Ten charts the brief asked for have no data and render honest `withheld` /
`unavailable` / `deferred` states instead. No series is fabricated.

## Repo truth that shaped the package

The brief's headline charts — equity curve, drawdown curve, Monte Carlo, WFO — have **no
data**. The read-only API projects zero time-series. Robustness statistics are named as
withheld (`report.withheld_statistics: ["PSR","DSR","MinTRL"]`) and exposed with no values.
Per-trade distributions are withheld by the result-populations envelope.

Not anticipated by the brief: `GET /api/research/result-populations/{id}` — already merged,
already reachable via `apiClient.resultPopulation(id)` — projects per-variant `metrics`
(`return_pct`, `drawdown`, `sharpe`, `win_rate`, `trade_count`) verbatim. That is **66 real
variant rows across 8 committed result populations**, every one from an `offline_research`
run with `offline_only: true`, `no_runtime_contact: true`, `no_paper_live_contact: true`.
This package charts those, and defers or withholds everything else.

## What changed

- Added `echarts@6.1.0` (exact-pinned), imported tree-shaken from `echarts/core` with
  explicit module registration. No `echarts-for-react`; no second charting family.
  ECharts 5.x was installed first, then rejected: GHSA-fgmj-fm8m-jvvx (XSS) affects every
  `echarts < 6.1.0`.
- Added `components/charts/`: `EChart` (the whole ~30-line integration), `ChartCard`,
  `UnavailableChartState`, `ChartProvenanceNote`, `CategoricalCountChart`,
  `OutcomeDistributionChart`, `MetricHistogramChart` (exporting `ReturnDistributionChart`
  and `DrawdownDistributionChart`), `DrawdownVsReturnScatter`.
- Added `lib/chartData.ts` (display-only binning / sampling / pairing that reports dropped
  rows rather than zero-filling) and `lib/chartTheme.ts` (palette mirroring the Tailwind
  `cockpit.*` tokens).
- Added 8 result-population **detail** fixtures, captured verbatim from the unchanged API
  via FastAPI `TestClient` — the same provenance path as every pre-existing fixture. Wired
  through `lib/fixtures.ts` and recorded in `lib/fixtures/_manifest.json`.
- Upgraded from CSS bars to charts: queue-by-status, candidate funnel, registry
  by-status/by-verdict, report `by_overall_state`, result-population outcome distributions.
- New real charts: per-variant return histogram, per-variant max-drawdown histogram,
  drawdown-vs-return scatter — on `/research/result-populations`, and again on
  `/strategies/[strategy_id]` filtered by lineage (every population's
  `parent_strategy_spec_id` resolves to a committed spec).
- Replaced the strategy-detail WFO / Robustness placeholders with `UnavailableChartState`
  panels naming the exact repo-truth reason and where it is declared.

## Honesty properties, enforced in code

- `histogram()` returns no bins for an empty sample, so a chart is never drawn over an
  absent measurement.
- `sampleMetric()` / `pairMetrics()` drop absent or non-finite values and **return the
  dropped count**, which every `ChartProvenanceNote` prints.
- `/system/data` charts coverage gaps only when gaps exist; the committed slice has
  `gap_count: 0`, so an `unavailable` state renders instead of an empty axis.
- `ReportView` omits zero-count states and says how many it omitted; if all are zero it
  renders an `unavailable` state.
- No chart sorts by a metric, marks a best variant, or draws a threshold or benchmark line.
- `EquityCurveChart` and `RobustnessDistributionChart` were deliberately **not created**.
  An empty component named after an impossible series invites a later package to fill it.
  The absence is encoded as `ChartAbsence` data instead.
- The reports' committed `withheld.charting.enabled = false` flag governs each report
  artifact's own embedded output. It is left untouched and still surfaced; only the count
  blocks the envelope already exposes are charted dashboard-side.

## Files Created

- `docs/status_entries/WP-DASH-CHARTS-PANELS-05.md`
- `operator_dashboard_frontend/src/components/charts/` (8 components)
- `operator_dashboard_frontend/src/lib/chartData.ts`
- `operator_dashboard_frontend/src/lib/chartTheme.ts`
- `operator_dashboard_frontend/src/lib/fixtures/result_populations/RP-*.json` (8 fixtures)
- `scratch/WP-DASH-CHARTS-PANELS-05/repo_truth_discovery.md`
- `scratch/WP-DASH-CHARTS-PANELS-05/chart_inventory.md`
- `scratch/WP-DASH-CHARTS-PANELS-05/dependency_decision.md`
- `scratch/WP-DASH-CHARTS-PANELS-05/no_control_evidence.md`
- `scratch/WP-DASH-CHARTS-PANELS-05/non_authority_assertions.json`
- `scratch/WP-DASH-CHARTS-PANELS-05/validation_summary.txt`

## Boundary

Frontend chart/presentation work only. Read-only. One charting dependency family. No
API/backend change (`tools/operator_dashboard_api/**` is byte-for-byte unchanged), no
POST/mutation, no Agent Inbox write, no execution/approval/promotion/crossing/paper-live/
notification/scheduler controls, no hosted deployment, no auth, no Grafana, no runtime or
paper/live contact, no canonical/candidate-lifecycle/crossing/promotion/readiness writes,
no protected-path changes, no fabricated chart data. Chart interactions are hover tooltips
and legend series-toggle only — both repaint a canvas and reach nothing outside it. ECharts
`toolbox`, `dataZoom`, `brush`, `markLine`, and `markArea` are deliberately not registered.

## Validation

`npm install` / `typecheck` / `lint` / `build` PASS (25/25 static pages).
`npm audit --omit=dev`: 2 vulnerabilities (1 high, 1 moderate) — **identical to baseline**,
both pre-existing in the `next` chain, fixable only by a `next@16` semver-major bump that is
out of scope. `echarts` / `zrender` not flagged. Nothing suppressed.

`tests/test_operator_dashboard_api.py` 11 passed. `research_query --list-views`,
`validate_result_populations`, `validate_candidate_registry` all PASS.
`diff_scope_summary.py`: forbidden-path matches — none. `git diff --check` clean.

No-control static scan: 0 mutation verbs, 0 forms, 0 buttons/onClick, 0 server actions,
0 storage writes, 0 `useState`. The single `fetch(` is the pre-existing GET-only
`apiClient.ts`, imported by no page. Charts import no fixtures and no client; they receive
serializable props only.

Visual verification: production build served; all 10 chart routes returned HTTP 200 with a
clean server log, and every chart host server-rendered with row counts matching the
committed artifacts (66 variant rows; 14 for `STRAT-SPEC-0001`; 8 queue statuses; 5 funnel
stages; 5 non-zero report states).

Browser verification (follow-up pass, `npm run dev`, real Chromium): canvases genuinely
paint — confirmed by counting non-transparent pixels in each canvas's backing store, not by
asserting the host element exists. **0 console errors, 0 warnings, 0 failed requests.**
**0 buttons / forms / inputs** on every route. Tooltip `formatter` functions run under an
error trap and print committed values (`RP-4492 · VAR-000006 · drawdown 29.1% · return
368.5%`); legend clicks and paging throw nothing, and a series toggle repainted and restored
cleanly. All withheld / unavailable / deferred states render as designed.

**One rendering defect was found and fixed during that pass.** ECharts 6 ignores
`grid.containLabel` unless `LegacyGridContainLabel` is registered, so `grid.top: 16` reserved
no room for a y-axis `name` and the axis names "variants" (histograms) and "return" (scatter)
were clipped at the canvas top edge. Fix, confined to the chart layer: remove the ignored
`containLabel` (provably a no-op — ECharts states it is ignored, so removing it cannot change
layout, and the horizontal bar charts confirm no label regression) and give the two charts
that name a y-axis a `GRID_TOP_WITH_AXIS_NAME = 32` top margin.

## Follow-ups

- `components/viz.tsx::Funnel` is now unused (the candidate funnel became a chart).
  `Meter` was already unused before this package. Both are merged presentational primitives
  a later package (Strategy Explorer) may reuse; neither was deleted here to avoid churning
  a merged public surface.
- Charting equity curves, WFO folds, or Monte Carlo paths requires the read-only API to
  project those series. That is a backend change and therefore a separate package.
- At a 375px viewport the whole shell overflows: the sidebar is fixed-width and never
  collapses, squeezing prose, badges, and charts alike. This predates this package (shell
  layout from `WP-DASH-FRONTEND-SHELL-03`) and is not chart-specific — the charts shrink
  without throwing. Left untouched here.
