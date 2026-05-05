# REC Cross-Expectation-Source Consumer Brief (WP-10d)

## 1. Purpose

WP-10d is a read-only descriptive consumer over the completed dual-source REC
corpus, `REC-0001` through `REC-0022`. It consumes the central query layer and
the package-local SQL outputs under
`research/briefs/2026-04-rec_cross_expectation_source_consumer/`.

WP-10d makes the completed REC cross-expectation-source posture visible. It
does not modify REC artifacts, REC schema, REC validator, query-layer code,
OL artifacts, EXP/REP artifacts, candidate registry, lifecycle artifacts,
policy surfaces, paper/live semantics, evidence scoring, ranking,
recommendation logic, runtime, deployment, configs, dependencies, or
protected-path behavior.

## 2. Source Bundle

Reproducibility assets:

- Brief: `research/briefs/2026-04-rec_cross_expectation_source_consumer.md`
- Query bundle:
  `research/briefs/2026-04-rec_cross_expectation_source_consumer/queries/`
- Output bundle:
  `research/briefs/2026-04-rec_cross_expectation_source_consumer/outputs/`
- Helper:
  `research/briefs/2026-04-rec_cross_expectation_source_consumer/run_all_queries.py`

The bundle uses the existing `reconciliations` relation and central query-layer
views only. It reads committed REC and OL corpus state descriptively.

## 3. Corpus Snapshot

`Q01` records 22 REC rows, the ID range `REC-0001` through `REC-0022`, 11
source OL rows, and 10 represented candidates
(`research/briefs/2026-04-rec_cross_expectation_source_consumer/outputs/Q01.json`).

The expectation-source distribution is 11 `exp_success_criteria` rows and 11
`d2_006_gates` rows. Pipeline distribution remains 20 `pre_wp_5b` rows and 2
`post_wp_5b` rows because H-004 has both pre-WP-5b and post-WP-5b outcome
rows under both expectation sources.

## 4. Cross-Source Coverage

`Q03` records one side-by-side row per locked OL v1 outcome
(`research/briefs/2026-04-rec_cross_expectation_source_consumer/outputs/Q03.json`).
Each locked OL v1 row has both expectation sources represented:

- one `exp_success_criteria` REC row;
- one `d2_006_gates` REC row.

These source pairs are descriptive only. Side-by-side presence does not imply
source superiority, automatic source preference, policy eligibility, ranking,
recommendation, promotion, demotion, paper/live readiness, or runtime
authority.

## 5. H-004 Structural Split

`Q04` records the four H-004 REC rows
(`research/briefs/2026-04-rec_cross_expectation_source_consumer/outputs/Q04.json`):

```text
REC-0005 / OL-0005 / H-004 / pre_wp_5b / exp_success_criteria / partially_met
REC-0011 / OL-0011 / H-004 / post_wp_5b / exp_success_criteria / insufficient_evidence
REC-0016 / OL-0005 / H-004 / pre_wp_5b / d2_006_gates / partially_met
REC-0022 / OL-0011 / H-004 / post_wp_5b / d2_006_gates / partially_met
```

The split remains structural. WP-10d makes no pre/post comparison,
improvement, degradation, pipeline-performance, policy, promotion, demotion,
ranking, paper/live, or recommendation inference from the four rows.

## 6. D2 Comparison-Surface Exceptions

`Q05` records the D2 comparison surface by REC row
(`research/briefs/2026-04-rec_cross_expectation_source_consumer/outputs/Q05.json`).
The D2 rows compare only metrics that are deterministically mapped and
semantically valid.

`REC-0017` and `REC-0019` correctly exclude cost-drag pass/fail comparison
because their referenced OL rows have `gross_pnl <= 0`; both rows have
`overall_verdict = none_met`.

`REC-0012` is a pre-WP-10c seed with cost-drag still compared despite
`gross_pnl <= 0`. WP-10d surfaces this as a descriptive anomaly and follow-up
candidate in `Q05`; it does not modify the REC artifact and does not fix the
seed inside this read-only consumer package.

`REC-0022` compares `sensitivity_min_ratio` because `OL-0011` directly
contains the metric. `pnl_concentration_90d` and `free_parameter_count` remain
extracted-only across the D2 rows because the OL metrics do not directly carry
those realized values.

These observations describe comparison-surface availability only. They do not
create evidence-quality scoring, policy, ranking, recommendation, paper/live,
or runtime implications.

## 7. REC-5 Floor Posture

REC-5 remains `n >= 3` per
`candidate_id / outcome_kind / pipeline_version / expectation_source_type`.

`Q02` records every current source segment with `reconciliation_count = 1`
(`research/briefs/2026-04-rec_cross_expectation_source_consumer/outputs/Q02.json`).
All current segments remain below REC-5. Adding a second expectation source
does not combine counts across sources, and cross-source coverage does not
satisfy REC-5.

## 8. Supported Descriptive Uses

`Q06` records supported descriptive uses
(`research/briefs/2026-04-rec_cross_expectation_source_consumer/outputs/Q06.json`).
WP-10d supports:

- corpus inventory;
- expectation-source coverage inspection;
- REC-to-OL mapping inspection;
- per-candidate cross-source inspection;
- H-004 split inspection;
- D2 comparison-surface exception inspection;
- REC-5 below-floor marking.

These uses are descriptive and consumer-time only.

## 9. Unsupported / Future-Dependent Claims

`Q06` also records unsupported and future-dependent claims. WP-10d does not
support:

- policy;
- promotion or demotion;
- ranking or recommendation;
- paper/live readiness;
- evidence-quality scoring;
- strategy-family performance conclusions;
- pipeline-version performance comparison;
- cross-window inference;
- runtime or deployment authority;
- OMS, risk, safe-mode, or execution authority;
- protected-path authority.

These claims require later explicit packages where applicable.

## 10. Next Package Boundary

WP-10d does not satisfy REC-5 and does not authorize WP-10f or Phase 10
decisions by itself.

The next bounded package should be WP-10e, which should lock the REC-5
floor-gap posture over the completed cross-expectation-source REC corpus.
