# WP-DASH-CHARTS-PANELS-05 — Chart inventory

Every chart added by this package, and every chart the brief asked for that is *not* drawn.

Legend for **Handling**:

- `rendered` — drawn from real committed fixture / API envelope data.
- `withheld` — data exists upstream but is deliberately not exposed to this surface.
- `unavailable` — no such artifact or measurement has been produced.
- `deferred` — the read-only API does not project enough data; widening it is out of scope.

Every rendered chart carries a `ChartProvenanceNote` with the sentence:
*"Descriptive only. This chart ranks nothing, recommends nothing, and confers no readiness,
promotion, admission, or execution authority."*
Every non-rendered chart carries an `UnavailableChartState` with the sentence:
*"No series is rendered. Nothing is inferred, zero-filled, or simulated."*

---

## Rendered charts

### 1. `/` — Queue by status

- **Component:** `CategoricalCountChart` (horizontal bar)
- **Source:** `GET /api/dashboard/summary` → `dashboard_summary.json`
- **Source fields:** `queue_summary.by_status`
- **Derived:** tone per status via `toneForStatus` (colour only)
- **Handling:** rendered — 8 committed statuses
- **Disclaimer:** "Bar length is a count, not a priority or a rank." Approval-needed states are
  shown, not actionable.
- **Verified:** SSR emits `aria-label="Bar chart of 8 committed queue statuses"`

### 2. `/research/result-populations` — Outcome distribution by population

- **Component:** `OutcomeDistributionChart` (stacked horizontal bar)
- **Source:** `GET /api/research/result-populations`
- **Source fields:** `items[].result_population_id`, `items[].outcome_counts`
- **Derived:** stacked segment order; bookkeeping keys `counts_sum` and
  `counts_sum_equals_committed_denominator` excluded via `OUTCOME_META`
- **Handling:** rendered — 8 populations, full committed denominator
- **Disclaimer:** no winner-only slice; failing buckets keep a `bad` tone
- **Verified:** `aria-label="Stacked outcome distribution across 8 committed result populations"`

### 3. `/research/result-populations` — Per-variant return distribution

- **Component:** `ReturnDistributionChart` (histogram, 12 bins)
- **Source:** `GET /api/research/result-populations/{id}` × 8
- **Source fields:** `variant_result_rows[].metrics.return_pct`
- **Derived:** equal-width histogram bins over observed `[min, max]`
- **Handling:** rendered — 66 rows drawn, 0 dropped
- **Disclaimer:** offline research backtest outputs; an empty bin means no variant landed there
- **Verified:** `aria-label="Histogram of per-variant return_pct across 66 committed variant rows"`

### 4. `/research/result-populations` — Per-variant max-drawdown distribution

- **Component:** `DrawdownDistributionChart` (histogram, 12 bins)
- **Source fields:** `variant_result_rows[].metrics.drawdown`
- **Handling:** rendered — 66 rows drawn, 0 dropped
- **Disclaimer:** explicitly labelled *"scalar max drawdown committed per variant. This is not a
  drawdown curve over time."*
- **Verified:** `aria-label="Histogram of per-variant max drawdown across 66 committed variant rows"`

### 5. `/research/result-populations` — Max drawdown vs return

- **Component:** `DrawdownVsReturnScatter`
- **Source fields:** `variant_result_rows[].metrics.drawdown`, `…metrics.return_pct`
- **Handling:** rendered — 66 pairs, 0 dropped
- **Disclaimer:** "No quadrant is preferred and no variant is selected." Rows missing either value
  are omitted, not placed at the origin.
- **Verified:** `aria-label="Scatter of per-variant max drawdown against return across 66 …"`

### 6. `/strategies` — Specs by primary timeframe / by direction

- **Component:** `CategoricalCountChart` × 2 (horizontal bar)
- **Source:** `GET /api/strategies`
- **Source fields:** `items[].primary_timeframe`, `items[].direction`
- **Derived:** count per distinct committed value
- **Handling:** rendered — 6 committed specs
- **Disclaimer:** "Strategy specs are planning artifacts and are not executable."

### 7. `/strategies/[strategy_id]` — Outcome distribution by linked population

- **Component:** `OutcomeDistributionChart`
- **Source:** `GET /api/research/result-populations/{id}`, filtered on `parent_strategy_spec_id`
- **Source fields:** `parent_strategy_spec_id`, `variant_result_rows[].outcome_category`
- **Derived:** count per outcome category
- **Handling:** rendered where the strategy has linked populations; `unavailable` state otherwise
- **Verified:** `STRAT-SPEC-0001` → 2 linked populations, 14 variant rows (7 + 7), matching
  `RP-2134` and `RP-4492`

### 8. `/strategies/[strategy_id]` — Per-variant return distribution + drawdown-vs-return scatter

- **Components:** `ReturnDistributionChart` (8 bins), `DrawdownVsReturnScatter`
- **Source fields:** `variant_result_rows[].metrics.{return_pct,drawdown}`
- **Handling:** rendered per linked strategy; `unavailable` state when no population links
- **Verified:** `aria-label="Histogram of per-variant return_pct across 14 committed variant rows"`

### 9. `/candidates` — Product candidate funnel

- **Component:** `CategoricalCountChart` (horizontal bar). Replaces the CSS `Funnel`.
- **Source:** `GET /api/candidates/funnel`
- **Source fields:** `product_candidate_funnel.stages[].label`, `…stages[].count`
- **Handling:** rendered — 5 committed stages, committed display order preserved
- **Disclaimer:** "Stage order implies no promotion, admission, or ranking authority." Full
  denominator; `winner_only_view` is `false`.

### 10. `/candidates` — Registry by status / by overall verdict

- **Component:** `CategoricalCountChart` × 2. Replaces CSS `CountBars`.
- **Source fields:** `candidate_registry.by_status`, `candidate_registry.by_overall_verdict`
- **Handling:** rendered — 2 + 2 buckets (11 `CONCLUDED` / 1 `DRAFT`; 11 `NO-GO` / 1 `PENDING`)
- **Disclaimer:** "Verdicts are read from the committed registry; this surface issues none."

### 11. `/reports/daily`, `/reports/weekly` — `by_overall_state`

- **Component:** `CategoricalCountChart`, via `ReportView`. Replaces CSS `CountBars`.
- **Source fields:** `report.counts.by_overall_state`
- **Handling:** rendered — 5 non-zero states of 13; the 8 zero-count states are omitted from the
  bars and the omission is stated in the provenance note. If every state were zero, an
  `unavailable` state renders instead of an empty axis.
- **Disclaimer:** the report artifact's own `charting.enabled = false` flag is untouched and still
  surfaced; only the count block the envelope already exposes is charted.
- **Verified:** `aria-label="Bar chart of report by_overall_state across 5 non-zero states"`

---

## Charts requested but NOT drawn

| # | Route(s) | Chart | Handling | Reason surfaced in UI | Declared by |
| --- | --- | --- | --- | --- | --- |
| 12 | `/` | Portfolio equity curve | `deferred` | No equity series is projected; no authorized paper/live telemetry snapshot exists to curve. | `envelope.unavailable.paper_live_telemetry` |
| 13 | `/` | Realised drawdown over time | `deferred` | Drawdown is committed as a scalar per variant, not a time series. | `readers.py::_variant_rows` |
| 14 | `/research/result-populations` | Equity curve | `deferred` | API projects committed scalar metrics per variant only. | `readers.py::_variant_rows` |
| 15 | `/research/result-populations` | Per-trade return distribution | `withheld` | Reason string is read live from the envelope. | `envelope.withheld.per_trade_distributions` |
| 16 | `/strategies/[id]` | Walk-forward (WFO) | `deferred` | No folds, windows, or per-fold statistics are projected. | `tools/operator_dashboard_api/readers.py` |
| 17 | `/strategies/[id]` | Robustness / Monte Carlo | `withheld` | PSR, DSR, MinTRL are named as withheld and exposed with no values. | `report.withheld_statistics` |
| 18 | `/strategies/[id]` | Equity curve | `deferred` | No per-bar or per-trade series for a spec or its populations. | `readers.py::_variant_rows` |
| 19 | `/reports/daily`, `/reports/weekly` | Robustness distribution | `withheld` | Reason names the withheld statistics read from the artifact. | `report.withheld_statistics` |
| 20 | `/system/data` | Detected coverage gaps | `unavailable` | Slice reports 0 gaps and 0 missing bars — nothing to plot. Chart *would* render if gaps existed. | `d4_slice.gap_facts` |
| 21 | `/system/data` | Price / OHLCV series | `deferred` | Endpoint projects slice identity, row counts, and gap facts — not bars. | `GET /api/system/data-health` |

`RobustnessDistributionChart` and `EquityCurveChart` components were **not created**. Building an
empty component named after a series that cannot exist would invite a later package to fill it
with something plausible. The absence is expressed as data (`ChartAbsence`), not as a stub.

---

## Visual verification

Production build (`npm run build`) followed by `npx next start -p 3517`. Every route returned
HTTP 200; the server log recorded zero errors, warnings, or exceptions.

| Route | HTTP | Charts SSR'd | Absence states |
| --- | --- | --- | --- |
| `/` | 200 | 1 | 2 |
| `/research/result-populations` | 200 | 4 | 2 |
| `/strategies` | 200 | 2 | 0 |
| `/strategies/STRAT-SPEC-0001` | 200 | 3 | 3 |
| `/strategies/STRAT-SPEC-0003` | 200 | 3 | 3 |
| `/candidates` | 200 | 3 | 0 |
| `/reports` | 200 | 0 | 0 |
| `/reports/daily` | 200 | 1 | 1 |
| `/reports/weekly` | 200 | 1 | 1 |
| `/system/data` | 200 | 0 | 2 |

Chart presence was confirmed from the rendered `aria-label` of each chart host, whose row counts
were cross-checked against the committed artifacts (66 total variant rows; 14 for
`STRAT-SPEC-0001`; 8 queue statuses; 5 funnel stages; 5 non-zero report states). All matched.

### Browser validation (follow-up pass) — limitation now closed

Every route above was loaded in a real browser against `npm run dev`. **Canvases genuinely
paint** — verified by reading each canvas's 2D backing store and counting non-transparent
pixels, not by asserting the host element exists. Console: **0 errors, 0 warnings, 0 failed
requests**. Controls: **0 buttons, 0 forms, 0 inputs** on every route.

Tooltips were exercised with synthetic mouse events under a `window.onerror` /
`unhandledrejection` trap. The custom `formatter` functions run and print committed values —
e.g. the scatter yields `RP-4492 · VAR-000006 · drawdown 29.1% · return 368.5%`, and the stacked
chart yields `RP-7520 … successful 10`, which matches RP-7520's committed 10 rows. Legend clicks
and the legend scroll-page arrow throw nothing; a series toggle produced a real repaint
(310,519 → 282,611 lit pixels) and restored cleanly.

**One defect was found and fixed.** ECharts 6 ignores `grid.containLabel` unless
`LegacyGridContainLabel` is registered (it logged this once per chart). Consequently `grid.top: 16`
reserved no room for a y-axis `name`, and the axis names **"variants"** (both histograms) and
**"return"** (scatter) were clipped at the canvas top edge. Fix, confined to the chart layer:
drop the ignored `containLabel` (provably a no-op) and give the two charts that name a y-axis a
`GRID_TOP_WITH_AXIS_NAME = 32` top margin. Re-verified afterwards — axis names fully visible, the
ECharts message gone, horizontal bar charts (queue, funnel, registry) still un-clipped, tooltips
and legend still fine.

**Not fixed (pre-existing, out of scope):** at a 375px viewport the whole shell overflows because
the sidebar is fixed-width and never collapses. That is shell layout from
`WP-DASH-FRONTEND-SHELL-03`, affects prose and badges as much as charts, and the charts shrink
without throwing.
