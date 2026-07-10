# WP-DASH-CHARTS-PANELS-05 — No-control evidence

Static scan over `operator_dashboard_frontend/src` after all chart work, plus targeted checks on
the client boundary the charts introduce.

## 1. Static scan results

| Check | Pattern | Result |
| --- | --- | --- |
| HTTP mutation verbs | `"(POST\|PUT\|PATCH\|DELETE)"`, `method: "POST"…` | **0 — pass** |
| Form elements | `<form`, `onSubmit`, `FormData`, `<input`, `<textarea`, `<select` | **0 — pass** |
| Buttons / click handlers | `<button`, `onClick`, `onChange`, `onKeyDown`, `type="submit"` | **0 — pass** |
| Network calls | `fetch(`, `XMLHttpRequest`, `WebSocket`, `EventSource`, `axios` | 1 — see §2 |
| Server actions / mutations | `"use server"`, `revalidatePath`, `revalidateTag`, `redirect(` | **0 — pass** |
| Action verbs wired to UI | `onClick=.*(run\|approve\|execute\|promote\|cross\|trade\|admit\|deploy)` | **0 — pass** |
| Cookies / storage writes | `localStorage`, `sessionStorage`, `document.cookie` | **0 — pass** |
| Agent Inbox write | `agent.?inbox.?write`, `intake.?draft`, `POST.*intake` | 22 — see §3 |
| React state | `useState`, `useReducer` | **0 — pass** |

## 2. The single `fetch` hit

`src/lib/apiClient.ts:23` — pre-existing, unchanged by this package.

- It is a `GET`-only helper: `method: "GET"` is hard-coded, and the module defines no
  POST/PUT/PATCH/DELETE helper and no generic `request(method, …)` escape hatch.
- It is imported by **no page and no component**. Verified: the only file matching `apiClient` is
  `lib/apiClient.ts` itself.
- It already exposed `resultPopulation(id)` before this package. The detail endpoint this package
  charts was therefore already part of the merged read-only contract; no new endpoint, route, or
  capability was introduced to reach it.

## 3. The 22 "agent inbox write" hits

Every hit is a **negative** declaration or explanatory prose, not a write:

- `agent_inbox_write_created: false` and `post_endpoint_created: false` in the intake fixture.
- `not_agent_inbox_write_authority: true` in the `authority` block of all 20 envelopes, including
  the 8 result-population detail fixtures added by this package.
- `unavailable.agent_inbox_write = "POST /api/agent/intake-draft is intentionally not implemented."`
- `app/agent-inbox/page.tsx` renders that string and the `false` flags as read-only text.

No Agent Inbox write behaviour is created, touched, or made reachable.

## 4. Client-boundary evidence for the new charts

Four chart components carry `"use client"` (`EChart`, `CategoricalCountChart`,
`OutcomeDistributionChart`, `MetricHistogramChart`, `DrawdownVsReturnScatter`). `Sidebar.tsx` was
the only pre-existing one.

- **No client state beyond rendering.** The only hooks in the chart layer are, in `EChart.tsx`:
  `useRef` (chart instance + container) and two `useEffect`s (init/dispose, and `setOption`).
  `useMemo` is used to build option objects — derivation, not state. `useState` appears nowhere in
  the entire `src` tree.
- **Charts cannot reach data.** No file under `components/charts/` imports `@/lib/fixtures` or
  `apiClient`. Charts receive plain serializable props (numbers, strings, arrays) from server
  components. They cannot fetch, and they have nothing to fetch with.
- **Interactions are visual only.** The registered ECharts components are `BarChart`,
  `ScatterChart`, `GridComponent`, `TooltipComponent`, `LegendComponent`, `CanvasRenderer`.
  `TooltipComponent` yields hover tooltips and `LegendComponent` yields series toggling — both
  repaint a canvas and reach nothing outside it. Deliberately **not** registered: `toolbox`
  (which ships save-as-image and data-view export), `dataZoom`, `brush`, `MarkLineComponent`,
  `MarkAreaComponent`.
- **No control-shaped affordance.** There is no button, no link that mutates, no drag handle, no
  editable axis, and no threshold marker that could read as an approval or execution gesture.

## 5. Data-honesty checks specific to charts

- `chartData.ts::histogram` returns **no bins** for an empty sample, so a chart is never drawn over
  an absent measurement — callers render `UnavailableChartState` instead.
- `chartData.ts::sampleMetric` and `pairMetrics` drop non-finite / absent values and **return the
  dropped count**, which every `ChartProvenanceNote` prints. Nothing is zero-filled.
- `ReportView` omits zero-count states from the bars and prints how many were omitted; if *all*
  states are zero it renders an `unavailable` state rather than a flat axis.
- `/system/data` renders a gap chart only when `gap_facts.gaps` is non-empty. The committed slice
  has `gap_count: 0`, so an `unavailable` state is shown — an empty chart is not drawn in place of
  a clean slice.
- No chart sorts by a metric, marks a "best" variant, or draws a threshold, target, or benchmark
  line.
- `RobustnessDistributionChart` and `EquityCurveChart` do not exist as components. Their absence is
  encoded as `ChartAbsence` data, so no later package inherits an empty shell inviting a plausible
  fill.

## 6. Scope

`tools/dev/diff_scope_summary.py` reports **`## Forbidden-path matches — none`**.

Backend, API, runtime, protected paths, canonical evidence, candidate lifecycle artifacts,
schemas, validators, scheduler, notification, and provider/credential files are all untouched.
`tools/operator_dashboard_api/**` is byte-for-byte unchanged; its 11 tests pass.
