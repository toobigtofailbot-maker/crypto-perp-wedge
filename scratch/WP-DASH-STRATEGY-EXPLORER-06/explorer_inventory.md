# WP-DASH-STRATEGY-EXPLORER-06 — Explorer inventory

Every section of the Strategy Explorer, what it reads, and how it behaves when data is absent.

Visual verification method: the production build was served with `next start -p 3131` and each route's
rendered HTML was asserted. A headless/attached browser console check was **not** available in this
session (see §"Visual verification" at the bottom).

---

## Route: `/strategies`

| Field | Value |
|---|---|
| Component | `src/app/strategies/page.tsx` |
| Source data | `GET /api/strategies` fixture; `GET /api/research/result-populations/{id}` fixtures (×8) |
| Fields rendered | `items[].strategy_id`, `title`, `short_name`, `status`, `source_type`, `instrument_family`, `market_type`, `primary_timeframe`, `direction`, `max_free_parameters`, `not_executable`, `path` |
| Derived (display only) | per-facet tallies; `population_count` and `variant_row_count` per spec, by matching `parent_strategy_spec_id` |
| Unavailable handling | A spec with no linked population shows a `no linked result population` warn badge. `EmptyState` when the list is empty. |
| No-authority wording | "These are counts, not filters. This surface holds no state and offers no control." · "An evidence badge counts artifacts; it is not a quality, readiness, or approval signal, and no spec is ranked above another." |
| Visual verification | PASS — 6 spec cards. Evidence badges match fixtures exactly: `2 result populations / 14 variant rows` (0001), `2 / 20` (0002), `1 / 8` (0003–0006). Header stat `Committed Variant Rows = 66` = 14+20+8×4. |

New in this package: `With Linked Evidence` and `Committed Variant Rows` stat cards, a static-tally
card (status / source type / timeframe / direction), per-card evidence indicators, and the spec
artifact path. The two facet charts from `WP-DASH-CHARTS-PANELS-05` are retained unchanged.

Removed: the `Executable: none in this shell` stat card, and the `free params: n/a` card line — the
API projects `free_parameter_count: null` for every spec, so the line only ever printed `n/a`. The
card now shows `max free params`, which is real, and the derived count lives on the detail page where
it can be labelled as derived.

---

## Route: `/strategies/[strategy_id]`

Component: `src/app/strategies/[strategy_id]/page.tsx`. Prerendered via `generateStaticParams` for the
6 committed specs (build output: `● /strategies/[strategy_id]` + 6 paths). Unknown ids still render.

In-page navigation: `SectionNav` renders `<a href="#id">` anchors only. No tabs, no state.

### 1. Identity — `#identity`

| Field | Value |
|---|---|
| Component | inline + `ExplorerSection`, `KeyValue` |
| Source data | `GET /api/strategies` (lifecycle status) + `GET /api/strategies/{id}` (everything else) |
| Fields rendered | `strategy_id`, `short_name`, `title`, list `status`, `source_type`, `review.approval_scope`, `instrument_family`, `market_type`, `primary_timeframe`, `direction`, `max_free_parameters`, `not_executable` |
| Unavailable handling | Every absent value renders `—` via `orDash`. Never `null`, never `0`. |
| No-authority wording | `not executable` badge; footnote explaining that the detail endpoint overwrites `status` with the envelope status, so lifecycle status is read from the list endpoint. |
| Visual verification | PASS — `approved_for_variant_planning` and `variant_planning_only` both present on `/strategies/STRAT-SPEC-0001`. |

### 2. Evidence & result-population linkage — `#evidence`

| Field | Value |
|---|---|
| Component | `components/explorer/EvidencePanel.tsx` |
| Source data | `GET /api/research/result-populations/{id}` |
| Fields rendered | `result_population_id`, `path`, `committed_denominator`, `result_row_count`, projected `variant_result_rows` length, `outcome_counts`, `validator_status`, `review_status`, `execution_mode`, `offline_only`, `variant_manifest_id`, `sweep_plan_id`, `result_population_identity_hash`, `input_identity_hash` |
| Derived (display only) | 4 reconciliation checks per population, each comparing two committed counts |
| Unavailable handling | A check whose inputs are absent renders `not projected` (neutral), never `consistent`. Zero linked populations → `UnavailablePanel` (`unavailable`). |
| No-authority wording | "A consistent check means two committed counts agree. It is not a quality, readiness, or approval signal. Linkage is by `lineage.strategy_spec_id` only." |
| Visual verification | PASS — `RP-2134` and `RP-4492` both shown for 0001, with `VM-0001` and truncated `sha256:` digests. |

Reconciliation checks: `result_row_count` vs `committed_denominator`; projected rows vs
`result_row_count`; `outcome_counts.counts_sum` vs `committed_denominator`; and the artifact's own
`counts_sum_equals_committed_denominator` assertion, surfaced rather than recomputed over it.

### 3. Variant grid — `#variants`

| Field | Value |
|---|---|
| Component | `components/explorer/VariantGrid.tsx` |
| Source data | `GET /api/research/result-populations/{id}` |
| Fields rendered | `result_population_id`, `variant_id`, `row_id`, `outcome_category`, and all 10 committed metrics: `return_pct`, `drawdown`, `sharpe`, `win_rate`, `trade_count`, `pnl`, `fees`, `funding`, `slippage`, `exposure` |
| Derived (display only) | per-metric missing counts, reported in the field note |
| Unavailable handling | An absent metric renders `—`, never `0`. **Per-variant parameter values render as an explicit `unavailable` block** naming the parent variant manifest as the holder. |
| No-authority wording | `offline research only`, `not ranked` badges. "No row is ranked, scored, or highlighted as preferable." "Values are printed as committed; no unit is reinterpreted." |
| Visual verification | PASS — 14 rows for 0001 across RP-2134 + RP-4492. |

Metric column headers use the exact committed field names. `return_pct` and `win_rate` are printed as
the committed ratios (e.g. `-0.0049`), **not** converted to a percentage — converting would reinterpret
a unit the artifact did not state.

### 4. Performance visuals — `#performance`

| Field | Value |
|---|---|
| Components | `ChartCard` + `OutcomeDistributionChart`, `ReturnDistributionChart`, `DrawdownDistributionChart`, `DrawdownVsReturnScatter` (all reused from `WP-DASH-CHARTS-PANELS-05`, unmodified) |
| Source data | `GET /api/research/result-populations/{id}` per-variant scalar `metrics` |
| Fields rendered | `outcome_category`, `metrics.return_pct`, `metrics.drawdown` |
| Unavailable handling | Each chart has a paired `UnavailableChartState` for the no-data branch. **Equity curve, drawdown curve, and return-series-over-time each render `deferred`** — the API projects no time series at all. |
| No-authority wording | "No bin is preferred." "No quadrant is preferred." "This is not a drawdown curve." |
| Visual verification | PASS — all three `deferred` cards present; `ChartProvenanceNote` reports drawn/missing counts. |

### 5. Walk-forward, OOS, robustness & Monte Carlo — `#robustness`

| Field | Value |
|---|---|
| Component | `UnavailableChartState` ×3 + `UnavailablePanel` ×1 |
| Source data | none — nothing is projected |
| Fields rendered | none |
| Unavailable handling | WFO/OOS → `deferred`; Monte Carlo → `deferred`; robustness (PSR/DSR/MinTRL) → `withheld`; linked-evidence review state → `unavailable`, quoting the real `review_status` (`not_reviewed`) |
| No-authority wording | "Nothing is fabricated to fill the section." "Nothing is inferred, zero-filled, or simulated." |
| Visual verification | PASS — `deferred`, `withheld`, and `unavailable` badges all render. |

**Zero fabrication.** No axis, no zero series, no placeholder curve.

### 6. Declared logic — `#logic`

| Field | Value |
|---|---|
| Component | `components/explorer/SpecLogicPanel.tsx` |
| Source data | `GET /api/strategies/{id}` |
| Fields rendered | `entry_logic`, `exit_logic`, `filters` → `groups[].group_id`, `group_role`, `logic`, `side`, `notes`, `conditions[].condition_id`, `condition_role`, `operator`, `left_operand`, `right_operand`, `units`, `notes`; `exit_logic.max_holding_period` |
| Derived (display only) | operand tree transcribed to text; group and condition counts |
| Unavailable handling | Group with no conditions → "This group declares no conditions." `filters.none_declared = true` is stated explicitly. |
| No-authority wording | "Transcribed from the spec's committed operand tree. Not evaluated, not simulated, not executable." |
| Visual verification | PASS — all five operand types and all six operators render correctly: |

```
STRAT-SPEC-0001  close < sma(20) × (1 − entry_distance_threshold)
                 close ≥ sma(20)
STRAT-SPEC-0003  z_score(value=close, center=sma(center_lookback_bars), scale=stddev(vol_lookback_bars)) < -1.5
                 close > sma(trend_lookback_bars)
STRAT-SPEC-0004  sma(fast_lookback_bars) crosses above sma(slow_lookback_bars)
                 sma(fast_lookback_bars) crosses below sma(slow_lookback_bars)
```

Each line was cross-checked against the committed artifact. A `composed_operand` whose
`composition_type` is unrecognised renders as `<type>(…)` rather than being collapsed into a symbol
the artifact never wrote.

### 7. Free parameters — `#parameters`

| Field | Value |
|---|---|
| Component | `components/explorer/FreeParameterTable.tsx` |
| Source data | `GET /api/strategies/{id}` |
| Fields rendered | `free_parameters.parameters[].name`, `type`, `units`, `default`, `range`, `allowed_values`, `role`, `included_in_variant_generation`, `rationale`, `constraints`; `max_free_parameters`; `counting_rule` |
| Derived (display only) | free-parameter count, tallied from `parameters[]` per the spec's own `counting_rule` |
| Unavailable handling | `no_free_parameters_declared = true` → stated, table suppressed. Absent cells → `—`. |
| No-authority wording | "The parameter space the spec declares. Not a per-variant assignment." Field note states that the API's `free_parameter_count` reads `free_parameters.count`, which specs do not carry, so it projects `null` — and that the shown count is derived, not API-projected. |
| Visual verification | PASS — `entry_distance_threshold` renders for 0001 with its range, step, and 7 allowed values. |

### 8. Data requirements & backtest assumptions — `#data`

| Field | Value |
|---|---|
| Component | `components/explorer/DataAndAssumptions.tsx` |
| Source data | `GET /api/strategies/{id}` (`timeframe_and_data`) + `GET /api/research/result-populations/{id}` (`backtest_assumption_summary`, `data_coverage_summary`) |
| Fields rendered | `primary_timeframe`, `confirmation_timeframes[]`, `host_data_refs[]` (stream/timeframe/field/availability), `gap_handling_assumption`, `missing_data_blockers[]`; every committed key of both RP blocks |
| Derived (display only) | union of keys across populations, so a key present on one population and absent on another still appears |
| Unavailable handling | Absent cell → `—`. No populations → "No linked result population projects a backtest assumption block." Blockers list shows "No missing-data blocker is declared." when empty. |
| No-authority wording | "Assumptions record what an offline backtest presumed; they are not exchange, broker, or live-execution guarantees." |
| Visual verification | PASS — one column per linked population, so two populations with differing assumptions are visibly different rather than silently merged. |

### 9. Provenance & source artifacts — `#provenance`

| Field | Value |
|---|---|
| Component | `components/explorer/SourceArtifacts.tsx` |
| Source data | `GET /api/strategies/{id}` (`path`, `provenance`) + envelope `provenance[]` |
| Fields rendered | `path`, `provenance.source_type`, `prepared_by`, `created_at`, `updated_at`, `rationale`, `source_refs[]`, `source_constraints[]`, `unresolved_claims[]`; envelope `provenance[].path`, `.role`, `.sha256`, `.note` |
| Derived (display only) | sha256 truncated to 12 hex chars for display |
| Unavailable handling | Each list has its own "declares none" empty label. Absent values → `—`. |
| No-authority wording | "Paths and digests are shown as text. This surface performs no filesystem navigation." |
| Visual verification | PASS — `research/strategy_specs/STRAT-SPEC-0001.strategy_spec.json`, its `sha256:` digest, and the cited design doc all render. Unresolved claims render in warn tone with an `N open` badge (5 on STRAT-SPEC-0006). |

No `<a href>` points at a filesystem path. Paths are inert text.

### 10. Boundary & non-authority — `#boundary`

| Field | Value |
|---|---|
| Component | `components/explorer/BoundaryPanel.tsx` |
| Source data | `GET /api/strategies/{id}` + `GET /api/research/result-populations/{id}` |
| Fields rendered | `non_execution_declaration` (11 flags), `review.approval_scope`, `.human_review_required`, `.reviewer`, `.reviewed_at`, `.review_notes[]`, `.non_authority_acknowledgement` (10 flags), RP `non_authority_declaration` (23 flags) |
| Derived (display only) | union of committed boolean flags across linked populations |
| Unavailable handling | `reviewer` / `reviewed_at` are `null` on several specs → `—`. Non-boolean values are skipped rather than cast. |
| No-authority wording | Six fixed surface-posture lines (read-only, not executable, not approval/promotion/readiness/crossing, not paper/live, not a ranking, no Agent Inbox write), **plus the artifacts' own flags** rather than prose this dashboard invented. |
| Visual verification | PASS — flags render from the committed records. |

### Envelope footer

`BoundaryNotes` + `ProvenanceFooter` render the detail envelope's `warnings`, `withheld`
(`execution_results`), `unavailable`, `source`, `schema_version`, and `provenance[]`.

---

## Route: `/strategies/<unknown id>`

| Field | Value |
|---|---|
| Source data | none — `fixtures.strategyDetail(id)` returns `undefined` |
| Unavailable handling | `UnavailableState` titled "Strategy unavailable", stating the id is not present as a committed artifact, that the API answers with an `unavailable` envelope rather than a 404, and that nothing is substituted |
| Visual verification | PASS — `/strategies/STRAT-SPEC-9999` and `/strategies/not%20a%20spec` both return HTTP 200 and render the unavailable page, matching the live API's real behaviour (200 + `unavailable` envelope, never a 404) |

---

## Components added

| File | Purpose |
|---|---|
| `src/components/explorer/primitives.tsx` | `ExplorerSection`, `SectionNav`, `DataTable`/`Row`/`Cell`, `FlagGrid`, `NoteList`, `FieldNote`, `UnavailablePanel` |
| `src/components/explorer/SpecLogicPanel.tsx` | entry/exit/filter condition transcription |
| `src/components/explorer/FreeParameterTable.tsx` | declared parameter space |
| `src/components/explorer/VariantGrid.tsx` | committed variant rows + metrics |
| `src/components/explorer/EvidencePanel.tsx` | RP linkage + denominator reconciliation |
| `src/components/explorer/SourceArtifacts.tsx` | provenance, source refs, unresolved claims |
| `src/components/explorer/BoundaryPanel.tsx` | non-authority flags |
| `src/components/explorer/DataAndAssumptions.tsx` | data requirements + backtest assumptions |
| `src/lib/explorer.ts` | display-only derivations (operand formatting, reconciliation, evidence tallies) |

All are **server components**. None declares `"use client"`. The only client components in the app
remain `Sidebar` and the five chart components, all pre-existing.

## Fixtures added

`src/lib/fixtures/strategies/STRAT-SPEC-000{1..6}.json` — captured verbatim from the unchanged
`GET /api/strategies/{id}` via FastAPI `TestClient`
(`scratch/WP-DASH-STRATEGY-EXPLORER-06/generate_strategy_detail_fixtures.py`), and registered in
`src/lib/fixtures/_manifest.json`.

---

## Visual verification

Method: `npm run build` then `npx next start -p 3131`, and assertion over the served HTML of
`/strategies`, `/strategies/STRAT-SPEC-0001`, `/strategies/STRAT-SPEC-0003`,
`/strategies/STRAT-SPEC-0006`, `/strategies/STRAT-SPEC-9999`, `/strategies/not%20a%20spec`.
All six returned HTTP 200 with the expected content, and the derived counts matched the fixtures.

**Browser console was not checked.** The Chrome extension was not connected in this session, and
`preview_start` requires `.claude/launch.json`, which is a forbidden path for this package. The chart
components that execute client-side are reused unmodified from `WP-DASH-CHARTS-PANELS-05`, where they
were browser-validated; this package passes them the same prop shapes (`OutcomeDistributionChart`,
`ReturnDistributionChart`, `DrawdownDistributionChart`, `DrawdownVsReturnScatter`), and the production
build compiles clean. A console check remains a reasonable follow-up before merge if desired.
