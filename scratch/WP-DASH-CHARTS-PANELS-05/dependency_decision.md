# WP-DASH-CHARTS-PANELS-05 — Charting dependency decision

## Decision

Add exactly one charting dependency family:

```
echarts@6.1.0   (exact-pinned, --save-exact)
  └── zrender@6.1.0   (transitive, same family)
```

Integrated **directly** through `echarts/core` with explicit module registration. No
`echarts-for-react`. No second charting family. No other UI, data, or state library.

## Why ECharts 6.1.0 and not the 5.x line

`npm install echarts@5.5.1` (the current 5.x) was installed first and audited:

```
npm audit --omit=dev
  echarts  moderate  <6.1.0
  Apache ECharts has a cross-site scripting (XSS) vulnerability
  https://github.com/advisories/GHSA-fgmj-fm8m-jvvx   CWE-79
  fixAvailable: echarts@6.1.0 (isSemVerMajor: true)
```

The advisory covers **every** `echarts < 6.1.0`, so no 5.x pin avoids it. Since this package is
adding the dependency fresh, there is no migration cost to paying — there is nothing to migrate
from. Taking a known XSS into a new dependency in order to stay on an older major would be a
worse trade than adopting the fixed major on day one.

`echarts@6.1.0` was installed and re-audited: **zero** advisories against `echarts` or `zrender`.
The 5.5.1 install was discarded; only 6.1.0 appears in `package.json` / `package-lock.json`.

The package brief's escalation clause covers *changing Next/React/Tailwind versions*. ECharts is a
new leaf dependency with no peer relationship to those, so choosing its major is a free choice
inside this package rather than an escalation.

## Why direct `echarts/core` and not `echarts-for-react`

1. **One family, not two.** `echarts-for-react` is a separate package that would still pull
   `echarts`. The brief allows one charting dependency family; direct integration keeps it at one.
2. **Bundle.** `echarts-for-react` imports the full `echarts` build. Direct `echarts/core` lets us
   register only what we draw:

   ```ts
   echarts.use([BarChart, ScatterChart, GridComponent,
                TooltipComponent, LegendComponent, CanvasRenderer]);
   ```

   No `LineChart`, no `CandlestickChart`, no `toolbox`, no `dataZoom`, no SVG renderer, no maps.
3. **React version drift.** `echarts-for-react` historically lags React majors. The wrapper we
   need is ~30 lines (`useRef` + `init` + `ResizeObserver` + `dispose`), which is less code than
   the risk it removes.
4. **Server-component boundary.** Direct integration lets exactly one file carry `"use client"`
   semantics for the chart host, keeping pages as server components that pass serializable props.

The whole integration is `src/components/charts/EChart.tsx`.

## Measured effect on bundle

From `npm run build`, First Load JS:

| Route class | Before | After |
| --- | --- | --- |
| Chart-free routes (`/paper`, `/live`, `/research/jobs`, …) | 87.4 kB | **87.4 kB** |
| Chart routes (`/`, `/candidates`, `/reports/daily`, `/system/data`) | 87.4 kB | ~279 kB |
| `/strategies`, `/strategies/[strategy_id]` | 87.4 kB | ~288–289 kB |

Chart-free routes are byte-for-byte unchanged, which is the direct evidence that the tree-shaken
registration works and that ECharts is confined to the routes that actually draw.

## What was NOT added, and why

- **TradingView Lightweight Charts** — deferred per the brief. No candle or trade-marker data
  contract exists: `system_data_health` projects slice identity, row counts, and gap facts, not
  bars. Adding it now would mean fabricating a series.
- **Any second charting family** (Recharts, Chart.js, visx, D3) — not needed and not permitted.
- **Any state / data-fetching library** — the shell has no client state and makes no network calls.
- **`echarts-gl`, `echarts-liquidfill`, ECharts extensions** — no use case.

## Audit trail

```
npm audit --omit=dev   (baseline, before)
  {"info":0,"low":0,"moderate":1,"high":1,"critical":0,"total":2}
  next: high     — DoS / cache-poison / XSS chain; fixAvailable next@16 (semver-major)
  postcss: moderate — XSS via unescaped </style>; reached through next

npm audit --omit=dev   (after echarts@5.5.1 — REJECTED)
  {"info":0,"low":0,"moderate":2,"high":1,"critical":0,"total":3}
  echarts: moderate — GHSA-fgmj-fm8m-jvvx

npm audit --omit=dev   (after echarts@6.1.0 — ADOPTED)
  {"info":0,"low":0,"moderate":1,"high":1,"critical":0,"total":2}
  flagged: ["next","postcss"]   echarts flagged: false
```

The two remaining advisories are **pre-existing**, sit in the `next` dependency chain, are not
introduced or worsened by this package, and are only fixable by a Next.js semver-major bump that
is out of scope here. Nothing is suppressed; `npm audit fix --force` was not run.
