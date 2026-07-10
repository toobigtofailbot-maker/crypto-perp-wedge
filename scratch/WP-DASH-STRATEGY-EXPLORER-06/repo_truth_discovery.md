# WP-DASH-STRATEGY-EXPLORER-06 — Repo-truth discovery

Base: `main` @ `9c0fb08` (merge of `WP-DASH-CHARTS-PANELS-05`, PR #636).
Branch: `claude/strategy-explorer-drilldown-28dbb6`.

Everything below was read from the repo. Nothing is assumed.

---

## 1. Hard dependencies — verified

| Dependency | State |
|---|---|
| `WP-DASH-CHARTS-PANELS-05` merged | YES — `9c0fb08` is its merge commit, and it is `origin/main` |
| `operator_dashboard_frontend/` exists and validates | YES — baseline `npm ci` / `typecheck` / `lint` / `build` all pass |
| Chart components exist and validate | YES — 8 files under `src/components/charts/` |
| `tools/operator_dashboard_api` read-only | YES — 11 `@api.get` routes, zero POST/PUT/PATCH/DELETE |
| Node/npm available | YES — node v24.18.0, npm 11.16.0 |
| No open PR implementing Strategy Explorer | YES — no `claude/wp-dash-strategy-explorer-06` on origin |
| Data sufficient for a useful drilldown | YES — see §4. **No new endpoint is needed.** |

---

## 2. Current strategy routes (pre-change)

| Route | File | State before this package |
|---|---|---|
| `/strategies` | `src/app/strategies/page.tsx` | Static list. Reads `/api/strategies` fixture only. Two `CategoricalCountChart` facet charts, spec cards, `BoundaryNotes`, `ProvenanceFooter`. |
| `/strategies/[strategy_id]` | `src/app/strategies/[strategy_id]/page.tsx` | Dynamic (`ƒ`). Reads the **list** fixture and finds the id in it. Renders a 11-row `KeyValue` summary, RP-derived charts, 4 unavailable/placeholder cards. |

The pre-existing detail page carries this comment:

> `The live read-only API exposes GET /api/strategies/{id}; wiring it is deferred to a later panel package.`

**This package is that package.** The detail endpoint already exists and is unchanged; only a fixture capture was missing.

---

## 3. API surface (read-only, unchanged by this package)

`tools/operator_dashboard_api/app.py` — 11 GET routes. Relevant ones:

| Route | Reader | Projects |
|---|---|---|
| `GET /api/strategies` | `read_strategies` | `{status, count, items[]}` — `_strategy_summary` per spec |
| `GET /api/strategies/{id}` | `read_strategy` | `_strategy_summary` **plus** `provenance`, `non_execution_declaration`, `timeframe_and_data`, `entry_logic`, `exit_logic`, `filters`, `free_parameters`, `review` |
| `GET /api/research/result-populations` | `read_result_populations` | RP summaries (no variant rows) |
| `GET /api/research/result-populations/{id}` | `read_result_population` | RP detail **with** `variant_result_rows[]` |

### 3.1 `GET /api/strategies/{id}` unavailable branch

Exercised against the live API (`readers.py:341-347`):

```json
{"data": {"status": "unavailable", "strategy_id": "STRAT-SPEC-DOES-NOT-EXIST"},
 "unavailable": {"strategy": "STRAT-SPEC-DOES-NOT-EXIST is not present as a committed artifact."}}
```

The detail route returns HTTP 200 with an `unavailable` envelope; it does not 404. The Explorer renders that envelope shape verbatim for unknown ids.

### 3.2 Three API projection quirks — observed, NOT fixed here

Fixing any of these is a backend change and is out of scope (§9.3). The Explorer routes around them honestly.

1. **`data.status` is clobbered on the detail endpoint.** `_strategy_summary` sets `status` from the artifact (`approved_for_variant_planning`), then `read_strategy` overwrites it with `"available"` (`readers.py:349-351`). The spec's *lifecycle* status therefore only survives on the **list** endpoint.
   → Explorer reads lifecycle status from the list fixture, envelope status from the detail fixture, and labels each.

2. **`approval_scope` is always `null`.** `_strategy_summary` reads `review.review_scope` (`readers.py:305`); the committed specs carry `review.approval_scope`. All 6 specs project `approval_scope: null` while really declaring `approval_scope: "variant_planning_only"`.
   → Explorer reads the real value from the detail `review` block and cites `review.approval_scope` as its field.

3. **`free_parameter_count` is always `null`.** `_strategy_summary` reads `free_parameters.count` (`readers.py:303`); the committed specs carry `free_parameters.parameters[]`. All 6 project `null`.
   → Explorer renders the parameter table from `free_parameters.parameters[]`, and shows a **derived** count labelled as derived, alongside the fact that the API field is not projected.

### 3.3 What the API does NOT project — searched, confirmed absent

`grep -rniE "equity|wfo|walk_forward|monte|psr|dsr|mintrl|robustness|oos|curve|series" tools/operator_dashboard_api/` → **zero matches.**

- No equity curve, no drawdown curve, no return series, no per-bar or per-trade series of any kind.
- No walk-forward folds/windows/per-fold statistics.
- No Monte Carlo paths or resamples.
- No robustness statistics (PSR / DSR / MinTRL). These are named as *withheld* in committed report artifacts.

The only real numeric surface is **per-variant scalar metrics** on the RP detail endpoint.

### 3.4 Variant parameter values — structurally unavailable

`_variant_rows` (`readers.py:134-155`) projects exactly: `variant_id`, `row_id`, `outcome_category`, `attempted`, `metrics`, `non_success`, `error`.

The underlying artifact row (`research/result_populations/RP-2134.result_population.json`) carries `assignment_hash` and `assignment_ref: null` — **the parameter assignment itself is not in the result population at all.** It lives in the parent variant manifest (`VM-0001`), which **no read-only endpoint projects**.

→ The variant grid renders ids, outcome, and metrics. Parameter values render as an explicit `unavailable` note naming the variant manifest as the holder. They are **not** guessed from the spec's `allowed_values`.

---

## 4. Available fixture/API fields

### 4.1 Strategy list (`strategies.json`) — 6 specs

`strategy_id`, `strategy_spec_id`, `path`, `title`, `short_name`, `status`, `source_type`,
`instrument_family`, `market_type`, `primary_timeframe`, `direction`,
`free_parameter_count` (always null), `max_free_parameters`, `approval_scope` (always null), `not_executable`.

All 6: `status=approved_for_variant_planning`, `not_executable=true`, `market_type=perpetual`, `instrument_family=crypto_perp`.
`primary_timeframe`: 15m ×5, 4h ×1. `direction`: both ×5, long ×1. `source_type`: research_note ×5, manual_idea ×1.

Note `strategy_spec_id` and `path` are projected but were **absent from the TS `StrategySummary` type**. Added.

### 4.2 Strategy detail (`strategies/STRAT-SPEC-000N.json`) — NEW, 6 files

Captured from the **unchanged** API via `TestClient`, the same provenance path as every other committed fixture
(`scratch/WP-DASH-STRATEGY-EXPLORER-06/generate_strategy_detail_fixtures.py`).

| Block | Real content across all 6 specs |
|---|---|
| `provenance` | `source_type`, `source_refs[]` (1–5 docs), `prepared_by`, `created_at`, `updated_at`, `rationale`, `source_constraints[]` (1–12), `unresolved_claims[]` (0–5) |
| `non_execution_declaration` | 11 boolean non-authority flags, all `true` |
| `timeframe_and_data` | `primary_timeframe`, `confirmation_timeframes[]` (all empty), `host_data_refs[]` (6–7), `gap_handling_assumption`, `missing_data_blockers[]` (all empty) |
| `entry_logic` | `direction`, `groups[]` with `group_id`, `group_role`, `logic`, `side`, `conditions[]`, `notes` |
| `exit_logic` | `groups[]`, `max_holding_period` (`enabled:false` on all 6), `notes` |
| `filters` | `groups[]`, `none_declared` (true ×3, false ×3) |
| `free_parameters` | `max_free_parameters:5`, `counting_rule`, `parameters[]` (1–3), `no_free_parameters_declared:false` |
| `review` | `human_review_required`, `reviewer` (null ×3, named ×3), `reviewed_at` (null ×6), `review_notes[]` (1–4), `approval_scope:"variant_planning_only"`, `non_authority_acknowledgement{10 flags}` |

Envelope: `withheld = {execution_results: "Strategy specs are planning artifacts; result populations are exposed separately."}`,
`provenance = [{path, role:"strategy_spec_artifact", sha256}]`.

### 4.3 Condition/operand grammar — enumerated across all 6 specs

- `operand_type`: `data_ref` (15), `indicator_ref` (39), `parameter_ref` (3), `constant` (2), `composed_operand` (5)
- `constant.ref` holds the numeric literal (e.g. `-1.5`), not a name.
- `lookback` is `{bars: N}` **or** `{bars_parameter_ref: "name"}`.
- `composition_type`: `scale_by_one_minus_parameter`, `scale_by_one_plus_parameter` → `{base_operand, parameter_operand}`;
  `z_score` → `{value_operand, center_operand, scale_operand, zero_scale_policy}`.
- `operator`: `lt`, `lte`, `gt`, `gte`, `crosses_above`, `crosses_below`.
- `subgroups` is present on every group and **empty on all 25 groups** — no recursion occurs in practice, but the renderer handles it.

### 4.4 Result population detail — 8 artifacts, all `status=available`

| RP | parent spec | denominator | rows | outcome |
|---|---|---|---|---|
| RP-2134 | STRAT-SPEC-0001 | 7 | 7 | successful 7 |
| RP-4492 | STRAT-SPEC-0001 | 7 | 7 | successful 7 |
| RP-6688 | STRAT-SPEC-0002 | 10 | 10 | successful 10 |
| RP-7520 | STRAT-SPEC-0002 | 10 | 10 | successful 10 |
| RP-7134 | STRAT-SPEC-0003 | 8 | 8 | successful 8 |
| RP-2592 | STRAT-SPEC-0004 | 8 | 8 | successful 8 |
| RP-3731 | STRAT-SPEC-0005 | 8 | 8 | successful 8 |
| RP-6236 | STRAT-SPEC-0006 | 8 | 8 | successful 8 |

**Every one of the 6 specs has ≥1 linked result population.** Coverage is complete; no spec renders an empty drilldown.

Unrendered-before-now RP detail fields now surfaced: `variant_manifest_id`, `sweep_plan_id`,
`result_population_identity_hash`, `input_identity_hash`, `outcome_counts` (incl. the
`counts_sum_equals_committed_denominator` reconciliation flag), `data_coverage_summary`,
`backtest_assumption_summary`, `error_summary`, `validator_status`, `review_status`,
`execution_mode`, `offline_only`, `no_runtime_contact`, `no_paper_live_contact`.

Per-variant `metrics`: `drawdown`, `exposure`, `fees`, `funding`, `pnl`, `return_pct`, `sharpe`, `slippage`, `trade_count`, `win_rate`.

---

## 5. Available chart components (reused, not modified)

`EChart`, `ChartCard`, `ChartProvenanceNote`, `UnavailableChartState`, `CategoricalCountChart`,
`OutcomeDistributionChart`, `MetricHistogramChart` (`ReturnDistributionChart`, `DrawdownDistributionChart`),
`DrawdownVsReturnScatter`.

Helpers in `src/lib/chartData.ts`: `collectVariantPoints`, `sampleMetric`, `histogram`, `pairMetrics`,
`countCategories`, `outcomeCategoryCounts`, `formatNumber`, `formatPercent`.

---

## 6. Section → data mapping

| §10.2 section | Source | Handling |
|---|---|---|
| 1. Strategy identity | list + detail | Rendered. Lifecycle status from list; envelope status from detail. |
| 2. Evidence / RP linkage | RP detail ×N | Rendered, incl. denominator reconciliation (`counts_sum_equals_committed_denominator`). |
| 3. Variant grid | RP detail `variant_result_rows[]` | Rendered: ids, outcome chip, metrics. **Parameter values: `unavailable`** (§3.4). |
| 4. Performance visuals | RP detail `metrics` | Return histogram + drawdown histogram + drawdown-vs-return scatter rendered from real scalars. **Equity / drawdown / return *curves*: `deferred`** (§3.3) — no series exists. |
| 5. WFO / OOS / robustness / MC | — | All `deferred` / `withheld`. Nothing drawn. |
| 6. Provenance & source artifacts | detail `provenance`, envelope `provenance` | Rendered as text: paths, roles, sha256, source_refs. No filesystem links. |
| 7. Boundary panel | `non_execution_declaration`, `review.non_authority_acknowledgement`, RP `non_authority_declaration` | Rendered from committed flags, not hardcoded prose. |

Spec sections *beyond* the package minimum that real data supports, and that are therefore rendered:
strategy logic (entry/exit/filters), free-parameter table, data requirements (`host_data_refs`),
backtest assumptions, error summary, unresolved claims, append-only review state.

---

## 7. Missing fields → honest rendering

| Missing | Absence class | Rendered as |
|---|---|---|
| Equity curve | `deferred` | `UnavailableChartState`, cites `readers.py::_variant_rows` |
| Drawdown curve | `deferred` | `UnavailableChartState` |
| Return series over time | `deferred` | `UnavailableChartState` |
| WFO folds / OOS | `deferred` | `UnavailableChartState` |
| Monte Carlo | `deferred` | `UnavailableChartState` |
| Robustness (PSR/DSR/MinTRL) | `withheld` | `UnavailableChartState`, cites `report.withheld_statistics` |
| Variant parameter values | `unavailable` | Inline note in variant grid, cites the variant manifest |
| `free_parameter_count` | not projected | Derived count shown, explicitly labelled derived |
| `approval_scope` (summary) | not projected | Real value read from `review.approval_scope` |
| `reviewer` / `reviewed_at` | null on some specs | `—`, never invented |

No zero-fill. No interpolation. No fabricated series.

---

## 8. Does a new read-only API endpoint appear necessary?

**No.** `GET /api/strategies/{id}` already exists and already projects every field the Explorer needs.
The only gap was a committed fixture for it, which this package captures from the unchanged API.

Per §8 of the package, work proceeds without stopping.

---

## 9. No-control constraints

- `tools/operator_dashboard_api/**` has 11 GET routes and no mutation route. Untouched.
- The frontend has no `fetch`/`axios`/mutation client; it imports committed JSON fixtures.
- Every navigation is a `next/link` `<Link>`.
- No `<form>`, no `<button>`, no `onClick`/`onSubmit`, no `"use client"` in any Explorer file.
- Verified post-change in `no_control_evidence.md`.
