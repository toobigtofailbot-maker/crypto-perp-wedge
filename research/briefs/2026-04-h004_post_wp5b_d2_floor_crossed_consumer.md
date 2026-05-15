# H-004 Post-WP-5b D2 Floor-Crossed Consumer Brief (WP-11a)

## 1. Package Identity

- Package label: WP-11a.
- Package title: First REC-5 Floor-Crossed Segment Consumer Brief.
- Exact segment:
  `H-004 / research_oos / post_wp_5b / d2_006_gates`.
- Package class: narrow descriptive consumer brief.

## 2. Purpose

WP-11a is the first descriptive consumer brief over a REC-5 floor-crossed exact
segment. It consumes committed repo truth for:

- `REC-0022`, `REC-0023`, and `REC-0024`;
- linked outcome-ledger rows `OL-0011`, `OL-0012`, and `OL-0013`;
- central query-layer views;
- package-local SQL outputs under
  `research/briefs/2026-04-h004_post_wp5b_d2_floor_crossed_consumer/outputs/`.

This brief creates no policy, scoring, ranking/recommendation, paper-live,
runtime, lifecycle, promotion/demotion, Path B, cohort, new-candidate, or
protected-path authority.

## 3. Source Bundle

Reproducibility assets:

- Brief:
  `research/briefs/2026-04-h004_post_wp5b_d2_floor_crossed_consumer.md`
- Query bundle:
  `research/briefs/2026-04-h004_post_wp5b_d2_floor_crossed_consumer/queries/`
- Output bundle:
  `research/briefs/2026-04-h004_post_wp5b_d2_floor_crossed_consumer/outputs/`
- Helper:
  `research/briefs/2026-04-h004_post_wp5b_d2_floor_crossed_consumer/run_all_queries.py`

Each substantive section below points to the package-local output file used for
that section.

## 4. Scope and Inference Boundaries

WP-10z PFC-2 permits this brief to state:

- per-observation facts for `REC-0022`, `REC-0023`, and `REC-0024`;
- three-observation facts for the exact segment;
- descriptive within-segment cross-observation patterns.

Within-segment patterns inside
`H-004 / research_oos / post_wp_5b / d2_006_gates` do not require an
`INSUFFICIENT_EVIDENCE` marker.

WP-10z PFC-2 forbids:

- cross-segment inference;
- claims about H-004 generally;
- H-004 pre/post pipeline comparison;
- comparison to H-004 post-WP-5b `exp_success_criteria`;
- predictive inference;
- policy implication;
- ranking, scoring, recommendation, promotion, demotion, paper-live, runtime,
  lifecycle, or operational framing.

Any claim outside this exact segment remains `INSUFFICIENT_EVIDENCE` or
explicitly forbidden by boundary language. Boundary claims are recorded in
`outputs/Q06.json`.

## 5. REC-5 Floor-Crossed Segment Snapshot

`outputs/Q01.json` records exactly one selected segment row:

```text
H-004 / research_oos / post_wp_5b / d2_006_gates
```

The selected segment has `reconciliation_count = 3` and
`overall_verdicts = [partially_met]`. Under current repo truth, REC-5 is
crossed for this exact segment only. Preflight query-layer discovery found all
other exact REC-5 segments below floor at `reconciliation_count = 1`.

This floor-crossing statement is segment inventory only. It does not compare
this segment to any other segment and does not create policy, scoring,
ranking/recommendation, paper-live, runtime, lifecycle, promotion, or demotion
authority.

## 6. Three REC Observations

`outputs/Q02.json` records the three REC observations in this segment:

| REC | OL | Overall verdict | Observation posture |
| --- | --- | --- | --- |
| `REC-0022` | `OL-0011` | `partially_met` | retrospective |
| `REC-0023` | `OL-0012` | `partially_met` | forward-flow |
| `REC-0024` | `OL-0013` | `partially_met` | forward-flow |

All three rows share:

```text
candidate_id: H-004
outcome_kind: research_oos
pipeline_version: post_wp_5b
expectation_source_type: d2_006_gates
```

The verdict distribution inside this exact segment is three
`partially_met` observations.

## 7. Evaluation-Window Posture

`outputs/Q03.json` records the linked OL evaluation windows and source
artifacts:

- `REC-0022 / OL-0011` derives from `REP-0011`; its OL evaluation window
  endpoints are null because the source preserved the no-formal-split baseline
  convention.
- `REC-0023 / OL-0012` derives from `REP-0012`; its evaluation window is
  `2025-04-12` through `2026-04-11`.
- `REC-0024 / OL-0013` derives from `REP-0013`; its evaluation window is
  `2024-04-12` through `2025-04-11`.

These are timing and source-artifact facts only. The brief does not claim that
one window is better, worse, more predictive, or more representative than
another.

## 8. Within-Segment Metric Comparison Patterns

`outputs/Q04.json` records compared D2 metrics for `REC-0022`, `REC-0023`, and
`REC-0024`.

Within this exact segment:

- `dsr` is `not_met` in all three observations.
- `max_drawdown` is `not_met` in all three observations.
- `walk_forward_efficiency` is `met` in all three observations.
- `sharpe` varies by observation: `not_met`, `not_met`, then `met`.
- `sensitivity_min_ratio` varies by observation: `met`, `not_met`, then
  `met`.
- `cost_drag_fraction` differs by row: `REC-0022` is `met`, `REC-0023` is not
  deterministically compared, and `REC-0024` is `not_met`.

These are within-segment descriptive patterns only. They are not performance
approval, strategy approval, evidence scoring, ranking/recommendation, policy,
paper-live readiness, runtime readiness, lifecycle, promotion, or demotion
claims.

## 9. Extracted-Only / Skipped Comparison Posture

`outputs/Q05.json` records D2 expectations preserved in
`expectation_extracted.metric_expectations` but absent from deterministic
`comparison.metric_comparisons`.

Within this exact segment:

- `pnl_concentration_90d` is preserved for all three REC rows but not compared
  because the linked OL metrics do not expose a realized 90-day contribution
  metric.
- `free_parameter_count` is preserved for all three REC rows but not compared
  because the linked OL metrics do not expose a realized free-parameter count.
- `REC-0023` preserves `cost_drag_fraction` but skips deterministic pass/fail
  comparison because `OL-0012.metrics.gross_pnl <= 0`; the negative
  `cost_drag_fraction` is not treated as a pass.

This posture describes comparison-surface availability only. It is not a
policy fact, ranking/scoring fact, recommendation, paper-live fact, runtime
fact, lifecycle fact, promotion fact, or demotion fact.

## 10. Supported Descriptive Uses

`outputs/Q06.json` records supported uses. WP-11a supports:

- floor-crossed exact-segment inventory;
- per-observation review;
- within-segment cross-observation summary;
- per-metric comparison pattern review;
- comparison-surface gap review;
- consumer-brief methodology example for later floor-crossed segments.

These uses are descriptive and consumer-time only.

## 11. Unsupported / INSUFFICIENT_EVIDENCE / Forbidden Claims

`outputs/Q06.json` also records unsupported claim categories. WP-11a does not
support:

- cross-segment inference;
- H-004 general inference;
- H-004 pre/post comparison;
- H-004 post-WP-5b D2 versus `exp_success_criteria` comparison;
- predictive inference;
- policy action;
- ranking, scoring, or recommendation;
- paper-live readiness;
- runtime readiness;
- lifecycle transition;
- promotion or demotion;
- Path B;
- cohort;
- new candidate;
- protected-path work.

Within-segment patterns in this crossed exact segment do not require an
`INSUFFICIENT_EVIDENCE` marker. Cross-boundary claim categories remain
`INSUFFICIENT_EVIDENCE` or forbidden under WP-10z PFC-2.

## 12. Next Package Boundary

WP-11a does not authorize further Stage 2 work. WP-10z PFC-3 remains active
after this brief: after WP-11a merges, another explicit chat-level
direction-setting decision is required before any further Stage 2 work.

Possible later directions remain non-authorized until Main 3.0 decides:

- additional floor crossing;
- Stage 2 second-sub-stage;
- Path B;
- stop/hold;
- stability lock.
