# Cockpit surface contract — WP-LABPROD-COCKPIT-STATIC-01

Read-only contract for the static lab product cockpit
(`tools/lab_cockpit`). This records the data-model shape, the panels the
renderer emits, and the static/no-control guarantees.

## Module

- `tools/lab_cockpit/model.py` — `build_cockpit_data(repo_root)` → deterministic
  data model (pure projection of committed artifacts; no clock/git/network).
- `tools/lab_cockpit/render.py` — `render_html(data)` / `render_markdown(data)`
  (hand-generated HTML/CSS/SVG; no `<script>`/`<button>`/`<form>`/`<input>`/
  `onclick`/meta-refresh/network reference).
- `tools/lab_cockpit/run.py` — CLI (`--data-json` / `--html` / `--markdown` /
  `--out-dir`).

## Data model shape (`lab_product_cockpit_v1`)

```
{
  schema_version, surface_kind: "read_only_operator_cockpit",
  non_authority_declaration: {read_only, static_only, has_run_button, ...},
  edge_search_hold,
  overview: {productization_status, real_traffic_batch, denominator,
             candidate_state, top_blockers},
  real_traffic_batch: {available, frozen_denominator_rows, preserved_rows,
             dropped_rows, blocked_rows, executed_successful_rows,
             canonical_result_population_written, go_like_evidence,
             hypotheses: [{hypothesis_id, name, family_route, status,
             status_label, positive_pnl_rows, median_pnl, median_return_pct,
             max_drawdown, median_fees, median_slippage, trade_counts,
             walkforward_rows, walkforward_successful_rows, reading,
             result_context_flags, ...}], totals},
  candidate_funnel: {stages: [frozen→executed→positive_median→go_like→
             candidate_ready], candidate_ready_count: 0, winner_only_view: false},
  wfo_oos: {rigorous_oos_gate_pass: false, protocol, per_hypothesis},
  robustness: {monte_carlo_run: false, withheld_statistics, withheld_note},
  timeline: [{seq, ref: "PR #600".."PR #609", kind, label, detail, source}],
  coordinator: {denominator_summary, subjects, held_boundary_panel},
  artifact_drilldown: [{key, category, path, present}],
  boundary: {assertions},
  caveats: [...]
}
```

## Panels rendered (HTML)

1. Lab overview — KPI strip + top blockers/caveats banner.
2. Candidate funnel — full denominator, narrows honestly to zero candidate-ready.
3. Strategy / hypothesis explorer — one card per frozen hypothesis with a
   diverging PnL read, drawdown meter, positive-row pips, WFO/MC chips, reading.
4. Visual result panels — inline SVG: median-PnL diverging bars, drawdown
   severity bars, positive-row bars, non-promoting-reason callout.
5. Robustness · WFO/OOS — withheld statistics shown explicitly; dry-run
   walk-forward flagged as not a rigorous gate pass.
6. Activity / evidence timeline — committed PR #600→#606→#608→#609 sequence.
7. Coordinator state · held boundary — subjects-by-state, subjects list,
   deferred-B / GO-gated boundary (reused from the merged state model).
8. Artifact drilldown — repo-relative paths with present/missing + category.
9. Boundary · non-authority — committed batch assertions + cockpit declaration.

## Guarantees

- Static only: no server, no live fetch, no network, no background daemon, no
  auto-refresh, no form submission, no JavaScript.
- Deterministic: two builds over the same checkout are byte-identical.
- Honest: withheld statistics labelled, no candidate-ready fabricated
  (`candidate_ready_count == 0`), no canonical Result Population claimed, full
  denominator (32 rows / 4 hypotheses) always shown.
- No execution controls: no run/approve/promote/retry/candidate/scheduler
  control anywhere on the page.
