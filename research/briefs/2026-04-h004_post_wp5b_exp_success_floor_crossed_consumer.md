# H-004 Post-WP-5b EXP-Success Floor-Crossed Consumer Brief (WP-12ap / WP-S2c-7)

## 1. Package Identity

- Package label: WP-12ap / WP-S2c-7.
- Package title: H-004 Post-WP-5b EXP-Success Floor-Crossed Consumer Brief.
- Exact segment:
  `H-004 / research_oos / post_wp_5b / exp_success_criteria`.
- Package class: narrow descriptive consumer brief.
- Committed files:
  - `research/briefs/2026-04-h004_post_wp5b_exp_success_floor_crossed_consumer.md`
  - `research/briefs/2026-04-h004_post_wp5b_exp_success_floor_crossed_consumer/`
  - `docs/project_status.md`

## 2. Purpose

WP-12ap / WP-S2c-7 is the within-segment consumer brief for the floor-crossed
exact `exp_success_criteria` segment. It consumes committed repo truth for:

- `REC-0011`, `REC-0025`, and `REC-0026`;
- linked outcome-ledger rows `OL-0011`, `OL-0014`, and `OL-0015`;
- linked report artifacts `REP-0011`, `REP-0014`, and `REP-0015`;
- linked EXP provenance from `EXP-0011`;
- central query-layer views;
- package-local SQL outputs under
  `research/briefs/2026-04-h004_post_wp5b_exp_success_floor_crossed_consumer/outputs/`.

This brief mirrors WP-11a's sibling-segment consumer-brief structure for
`H-004 / research_oos / post_wp_5b / d2_006_gates`, but it does not compare the
two segments. It creates no policy, scoring, ranking/recommendation,
paper-live, runtime, lifecycle, promotion/demotion, Path B, cohort
implementation, paired-source reuse, new-candidate, H-001 runway, H-005/H-006,
or protected-path authority.

## 3. Source Bundle

Reproducibility assets:

- Brief:
  `research/briefs/2026-04-h004_post_wp5b_exp_success_floor_crossed_consumer.md`
- Query bundle:
  `research/briefs/2026-04-h004_post_wp5b_exp_success_floor_crossed_consumer/queries/`
- Output bundle:
  `research/briefs/2026-04-h004_post_wp5b_exp_success_floor_crossed_consumer/outputs/`
- Helper:
  `research/briefs/2026-04-h004_post_wp5b_exp_success_floor_crossed_consumer/run_all_queries.py`

Substantive sections below cite the package-local output file used for the
section.

## 4. Scope and Inference Boundaries

PFC-2-style boundaries permit this brief to state:

- per-observation facts for `REC-0011`, `REC-0025`, and `REC-0026`;
- three-observation facts for the exact segment;
- descriptive within-segment cross-observation patterns;
- per-comparison-surface availability review;
- floor-crossed exact-segment inventory.

Within-segment patterns inside
`H-004 / research_oos / post_wp_5b / exp_success_criteria` do not require an
`INSUFFICIENT_EVIDENCE` marker.

The boundaries forbid:

- cross-segment inference;
- comparison to the sibling `d2_006_gates` segment;
- claims about H-004 generally;
- H-004 pre/post comparison;
- aggregate-corpus inference;
- cohort implementation authority or cohort-level inference;
- predictive inference;
- policy implication;
- ranking, scoring, recommendation, promotion, demotion, paper-live, runtime,
  lifecycle, or operational framing;
- Path B, paired-source reuse, new-candidate, H-001 runway work, H-005/H-006
  work, or protected-path work.

Sibling-segment co-existence with `d2_006_gates` may be described as structural
inventory only. It is not comparison, combined evidence, or authority.
Boundary claims are recorded in `outputs/Q06.json`.

## 5. REC-5 Floor-Crossed Segment Snapshot

`outputs/Q01.json` records exactly one selected segment row:

```text
H-004 / research_oos / post_wp_5b / exp_success_criteria
```

The selected segment has `reconciliation_count = 3` and
`overall_verdicts = [insufficient_evidence]`. The exact REC IDs are:

- `REC-0011`
- `REC-0025`
- `REC-0026`

The linked OL IDs are:

- `OL-0011`
- `OL-0014`
- `OL-0015`

Under current repo truth, REC-5 is crossed for this exact segment. This
floor-crossing statement is segment inventory only. It does not compare this
segment to the sibling `d2_006_gates` segment, does not combine evidence with
that segment, and does not create policy, scoring, ranking/recommendation,
paper-live, runtime, lifecycle, promotion, or demotion authority.

## 6. Three REC Observations

`outputs/Q02.json` and `outputs/Q03.json` record the three REC observations in
this segment:

| REC | OL | REP/source artifact | Observation posture | Overall verdict | Evaluation window | Linked EXP | Expectation source |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `REC-0011` | `OL-0011` | `REP-0011` | retrospective | `insufficient_evidence` | null endpoints, no-formal-split baseline convention | `EXP-0011` | `exp_success_criteria` |
| `REC-0025` | `OL-0014` | `REP-0014` | forward-flow | `insufficient_evidence` | `2023-04-12` through `2024-04-11` | `EXP-0011` | `exp_success_criteria` |
| `REC-0026` | `OL-0015` | `REP-0015` | forward-flow | `insufficient_evidence` | `2022-04-12` through `2023-04-11` | `EXP-0011` | `exp_success_criteria` |

All three rows share:

```text
candidate_id: H-004
outcome_kind: research_oos
pipeline_version: post_wp_5b
expectation_source_type: exp_success_criteria
```

The verdict distribution inside this exact segment is three
`insufficient_evidence` observations.

## 7. Evaluation-Window Posture

`outputs/Q03.json` records the linked OL evaluation windows and source
artifacts:

- `REC-0011 / OL-0011` derives from `REP-0011`; its OL evaluation window
  endpoints are null because the source preserved the no-formal-split baseline
  convention.
- `REC-0025 / OL-0014` derives from `REP-0014`; its evaluation window is
  `2023-04-12` through `2024-04-11`.
- `REC-0026 / OL-0015` derives from `REP-0015`; its evaluation window is
  `2022-04-12` through `2023-04-11`.

These are timing and source-artifact facts only. The brief does not claim that
one window is better, worse, more predictive, or more representative than
another.

## 8. EXP-Success Comparison Patterns

`outputs/Q04.json` records EXP-success comparison rows for `REC-0011`,
`REC-0025`, and `REC-0026`.

Within this exact segment, the same seven EXP-success criteria appear in all
three REC observations:

- `d2_006_gates`
- `plan_file_authored`
- `registered_h004_parameters`
- `trial_log_append_count`
- `report_trial_reference`
- `historical_h004_artifact_preservation`
- `scope_preservation`

All seven criteria in all three REC observations have
`comparison_verdict = insufficient_evidence`. For each row, `realized_value`,
`delta_absolute`, and `delta_relative` are null. The comparison notes state
that REC v1 cannot compare the EXP-0011 operational, qualitative, or
gate-reference criteria to the linked OL row without inventing an OL metric
mapping, numeric threshold, operational pass/fail authority, or, for the
forward-flow rows, D2 direct-threshold fallback.

These are within-segment comparison-surface facts only. They are not
performance approval, strategy approval, evidence scoring, ranking/
recommendation, policy, paper-live readiness, runtime readiness, lifecycle,
promotion, or demotion claims.

## 9. Extracted-Only / Skipped / Unavailable Comparison Posture

`outputs/Q05.json` records comparison-surface availability posture.

Current artifact truth exposes no extracted-only EXP-success criterion that is
absent from deterministic `comparison.metric_comparisons` for the three exact
REC observations. Instead, all preserved criteria are present as comparison
rows and are recorded as `insufficient_evidence` with null realized and delta
fields.

Current artifact truth does not expose cost-drag-skip-like logic for this
`exp_success_criteria` segment. The cost-drag-skip posture belongs to a D2
comparison-surface pattern and is not used here.

This section describes comparison-surface availability only. It is not a
policy fact, ranking/scoring fact, recommendation, paper-live fact, runtime
fact, lifecycle fact, promotion fact, or demotion fact.

## 10. Supported Descriptive Uses

`outputs/Q06.json` records supported uses. WP-12ap / WP-S2c-7 supports:

- floor-crossed exact-segment inventory;
- per-observation review;
- within-segment cross-observation summary;
- EXP-success comparison-surface review;
- consumer-brief methodology example for later floor-crossed
  expectation-source segments;
- gap review for brief coverage.

These uses are descriptive, consumer-time, and within-segment only.

## 11. Unsupported / INSUFFICIENT_EVIDENCE / Forbidden Claims

`outputs/Q06.json` also records unsupported and forbidden claim categories.
WP-12ap / WP-S2c-7 does not support:

- cross-segment inference;
- D2 versus EXP-success comparison;
- H-004 general inference;
- H-004 pre/post inference;
- aggregate-corpus inference;
- cohort-level inference;
- predictive inference;
- policy action;
- ranking, scoring, or recommendation;
- paper-live readiness;
- runtime readiness;
- lifecycle transition;
- promotion or demotion;
- Path B;
- new candidate;
- protected-path work.

Within-segment patterns in this crossed exact segment do not require an
`INSUFFICIENT_EVIDENCE` marker. Cross-boundary claim categories remain
`INSUFFICIENT_EVIDENCE` or forbidden under the boundaries above.

## 12. Next Package Boundary

WP-S2c-7 does not authorize further work. It does not start or modify the
A2C-001 H-001 runway. It does not authorize cohort implementation, paired-source
reuse, H-005 work, H-006 work, Path B, EXP scaffold authoring, artifacts,
schema/validator/central query-layer changes, implementation, configs,
dependencies, data changes, runtime/protected paths, AUTO, H-011 first-time
inclusion, H-012+ registration, policy/scoring/ranking/recommendation,
approval, promotion/demotion, readiness, lifecycle transition, or downstream
authority.

The authorized next runway package remains WP-S2c-8 only as separately
authorized by Main/Karl's first-member runway and only after refreshed-main
preflight. No package follows automatically from WP-S2c-7 itself.
