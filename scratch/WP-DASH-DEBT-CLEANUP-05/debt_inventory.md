# WP-DASH-DEBT-CLEANUP-05 — Debt inventory

Narrow UI-debt pass over the operator dashboard frontend. Baseline: `main` @
`1969251` (PRs #636 and #639 merged). Frontend only; no new architecture,
routes, data fetching, dependencies, or controls.

## 1. Redundant Agent Inbox error copy — FIXED

`IntakeForm.tsx` rendered every submit error through `UnavailableState` with:

```
reason={`${submission.message} No draft packet was created, and nothing is shown in its place.`}
```

That trailing sentence was redundant three ways:

- The `UnavailableState` **title** already says `"Draft not created"` /
  `"Intake service unreachable"`.
- The passthrough messages already end with `"No draft was created."` (see
  `app/agent-inbox/intake-draft/route.ts`, the 503/502 branches), so the
  operator saw "…No draft was created. No draft packet was created, and nothing
  is shown in its place."
- On error the form renders nothing below, so "nothing is shown in its place"
  restated the absence the operator was already looking at.

Fix: `reason={submission.message}`. Every path stays honest — the title always
conveys "not created", and the unavailable messages still assert
"No draft was created." No service error meaning changed (the passthrough and
service messages themselves are untouched).

## 2. Dead `Funnel` / `FunnelStageRow` — REMOVED

After Charts 05 (#636), the candidates page renders the product funnel with the
ECharts `CategoricalCountChart`, not the CSS `Funnel` primitive.

Importer search on `main` (`operator_dashboard_frontend/src`):

- `Funnel` (word-boundary) → only the `export function Funnel` definition in
  `viz.tsx`, plus unrelated string literals on the candidates page
  (`title="Candidate Funnel"`, an `ariaLabel`) and unrelated identifiers
  (`candidatesFunnel`, `CandidatesFunnelData`, `ProductCandidateFunnel`,
  `FunnelStage`, `funnelBars`).
- `FunnelStageRow` → only its own `export interface` in `viz.tsx`.

Zero importers → removed the `Funnel` component and the `FunnelStageRow`
interface from `viz.tsx`. The module docstring ("bars, funnels") was updated to
match ("labelled count bars and a stacked bar").

Kept (still used by `CountBars` / `StackedBar`): `BAR_CLASS`, `DOT_CLASS`,
`pct`, `CountRow`, `CountBars`, `StackSegment`, `StackedBar`. `typecheck`
(which flags unused exports via lint) stays green, confirming they are live.

## 3. Mobile / narrow-viewport shell overflow — FIXED

Observed at 375px on `main`: the shell is `flex h-screen … overflow-hidden`
with a fixed `w-60` (240px) `shrink-0` sidebar. On a 375px viewport the sidebar
consumed 240px, leaving the content column **135px** wide; content (StatusHeader
badges, provenance mono strings, tables) overflowed that column and was
**clipped** by the outer `overflow-hidden` with no way to scroll to it.

Measured before: `main` left=240, width=135, scrollWidth=400 (clipped).

Fix (within existing sidebar layout intent — no drawer, no toggle, no new
component/route/control):

- `AppShell.tsx`: stack vertically on mobile (`flex-col` + `min-h-screen`,
  natural page scroll), restore the persistent side-by-side sidebar from `md`
  up (`md:h-screen md:flex-row md:overflow-hidden`, `md:overflow-y-auto` on
  `main`). Mobile content padding trimmed `px-6`→`px-4` (md keeps `px-6`).
- `Sidebar.tsx`: full-width nav block on mobile, `md:w-60` sidebar from `md` up;
  border flips bottom→right at `md`. Top-level nav list wraps horizontally on
  mobile (`flex-row flex-wrap`), stays vertical on desktop (`md:flex-col`) —
  this dropped the mobile nav height from ~440px to ~322px while keeping every
  link and the active group's sub-nav.

After: content column full 375px, no clipped shell content, desktop layout
unchanged (240px vertical sidebar).

## 4. Small operator-facing clarity fixes (directly related to #3) — FIXED

Long unbreakable `font-mono` identifiers still clipped the content column even
at full width. Added `break-all` at the three shared spots that render them, so
they wrap instead of being cut off:

- `ProvenanceFooter.tsx` — artifact path `<li>` (every page's footer).
- `ChartProvenanceNote.tsx` — the `source` path span (every chart footnote).
- `charts/UnavailableChartState.tsx` — the "Declared by <source>" span.
- `explorer/EvidencePanel.tsx` — reconciliation `check.detail` id span, plus
  `min-w-0` on its flex wrapper so it can shrink and wrap.

Plus the `viz.tsx` docstring correction noted in #2.

## Out of scope / intentionally NOT changed

- Wide explorer data tables on `/strategies/{id}` already sit in
  `overflow-x-auto` scroll containers (the intended pattern for wide tables).
  They report widths > viewport but scroll within their own box — verified
  scrollable, not clipped. Left as-is.
- No route, data-fetch, endpoint, dependency, or control was added. `tools/**`
  and the read-only dashboard API were not touched.
