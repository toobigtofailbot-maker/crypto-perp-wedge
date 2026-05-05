# REC v1 Consumer Synthesis Brief (WP-9y)

## 1. Purpose

WP-9y is a read-only synthesis over the completed REC v1 retrospective corpus,
`REC-0001` through `REC-0011`. It consumes the existing central query layer and
the package-local SQL outputs under
`research/briefs/2026-04-rec_v1_consumer_synthesis/`.

This package does not modify REC artifacts, REC schema, REC validator,
REC query-layer code, OL artifacts, EXP/REP artifacts, candidate registry,
lifecycle artifacts, helper tooling, promotion policy, paper/live semantics,
evidence-quality scoring, runtime, deployment, configs, dependencies, or
protected-path behavior.

## 2. Corpus Snapshot

`Q01` records 11 REC rows, 11 source OL rows, 10 represented candidates, and the
ID range `REC-0001` through `REC-0011`
(`research/briefs/2026-04-rec_v1_consumer_synthesis/outputs/Q01.json`).

Pipeline distribution is 10 `pre_wp_5b` rows and 1 `post_wp_5b` row.
Expectation-source distribution is 11 `exp_success_criteria` rows and 0
`d2_006_gates` fallback rows. H-004 has 2 REC rows.

## 3. Per-Candidate / Segment View

`Q02` records 11 current REC-5 segments. Each segment is keyed by
`candidate_id / outcome_kind / pipeline_version / expectation_source_type` and
contains exactly one reconciliation row
(`research/briefs/2026-04-rec_v1_consumer_synthesis/outputs/Q02.json`).

The current REC-to-OL mapping is:

```text
REC-0001 -> OL-0001 / H-001 / pre_wp_5b
REC-0002 -> OL-0002 / H-005 / pre_wp_5b
REC-0003 -> OL-0003 / H-002 / pre_wp_5b
REC-0004 -> OL-0004 / H-003 / pre_wp_5b
REC-0005 -> OL-0005 / H-004 / pre_wp_5b
REC-0006 -> OL-0006 / H-006 / pre_wp_5b
REC-0007 -> OL-0007 / H-007 / pre_wp_5b
REC-0008 -> OL-0008 / H-008 / pre_wp_5b
REC-0009 -> OL-0009 / H-009 / pre_wp_5b
REC-0010 -> OL-0010 / H-010 / pre_wp_5b
REC-0011 -> OL-0011 / H-004 / post_wp_5b
```

This is path inspection only. It does not compare, rank, or recommend
candidates.

## 4. Verdict Distribution

`Q03` records the current descriptive verdict distribution
(`research/briefs/2026-04-rec_v1_consumer_synthesis/outputs/Q03.json`):

- `none_met`: 3 rows, `REC-0001`, `REC-0007`, `REC-0009`.
- `partially_met`: 7 rows, `REC-0002` through `REC-0006`, `REC-0008`,
  `REC-0010`.
- `insufficient_evidence`: 1 row, `REC-0011`.

These verdicts are descriptive reconciliation results only. `partially_met`
does not imply policy eligibility. `none_met` does not imply rejection policy.
`insufficient_evidence` does not imply failure.

## 5. H-004 Structural Split

`Q04` records the H-004 split as two separate REC rows
(`research/briefs/2026-04-rec_v1_consumer_synthesis/outputs/Q04.json`):

```text
REC-0005 / OL-0005 / H-004 / pre_wp_5b / exp_success_criteria / partially_met
REC-0011 / OL-0011 / H-004 / post_wp_5b / exp_success_criteria / insufficient_evidence
```

The split remains structural only. WP-9y makes no improvement, degradation,
pipeline-performance, policy, promotion, demotion, ranking, paper/live, or
recommendation claim from the two rows.

## 6. Expectation Source and Comparison Surface

`Q05` records 11 `exp_success_criteria` rows and 0 `d2_006_gates` fallback
rows (`research/briefs/2026-04-rec_v1_consumer_synthesis/outputs/Q05.json`).

The deterministic mapped comparison metrics exposed by current REC rows are:

- `sharpe`
- `dsr`
- `max_drawdown`
- `cost_drag_fraction`
- `walk_forward_efficiency`

Those metrics are present for 10 rows. REC-0011 has no deterministic numeric
comparison surface because its selected EXP success criteria are operational or
qualitative rather than numeric OL metric thresholds. Gate-reference,
qualitative, sensitivity, PnL concentration, and free-parameter criteria are
preserved in REC extraction where present, but they do not create additional
verdict, policy, or runtime authority.

## 7. REC-5 Floor Posture

REC-5 requires at least `n >= 3` reconciliations per
`candidate_id / outcome_kind / pipeline_version / expectation_source_type`
before segment-level inference.

`Q02` records that all 11 current segments have `reconciliation_count = 1`.
All current REC-5 segments are below floor. All cross-reconciliation inference
therefore remains `INSUFFICIENT_EVIDENCE`.

## 8. Supported Descriptive Uses

`Q06` records supported descriptive uses
(`research/briefs/2026-04-rec_v1_consumer_synthesis/outputs/Q06.json`).
WP-9y supports:

- REC corpus inventory.
- REC-to-OL mapping inspection.
- Per-candidate REC path inspection.
- Verdict distribution inspection.
- Expectation-source distribution inspection.
- H-004 split inspection.
- REC-5 floor marking.
- Comparison-surface inspection limited to deterministic mapped metrics and
  preserved qualitative/gate-reference criteria.

These uses are descriptive and consumer-time only.

## 9. Unsupported / Future-Dependent Claims

`Q06` also records unsupported or future-dependent claims. WP-9y does not
support:

- promotion or demotion policy;
- candidate recommendation;
- ranking;
- paper/live readiness;
- evidence-quality scoring;
- strategy-family performance conclusions;
- pipeline-version performance comparison;
- cross-window inference below REC-5 floor;
- runtime or deployment authority;
- OMS, risk, safe-mode, or execution authority;
- protected-path authority.

These claims require later explicit packages where applicable.

## 10. Validation Snapshot

Reproducibility assets:

- Brief:
  `research/briefs/2026-04-rec_v1_consumer_synthesis.md`
- Query bundle:
  `research/briefs/2026-04-rec_v1_consumer_synthesis/queries/`
- Output bundle:
  `research/briefs/2026-04-rec_v1_consumer_synthesis/outputs/`
- Helper:
  `research/briefs/2026-04-rec_v1_consumer_synthesis/run_all_queries.py`

Discovery before authoring confirmed REC validation passed, REC overview
returned 11 rows, REC candidate/pipeline summary returned 11 segments, REC
integrity views returned `[]`, outcome-ledger validation passed, OL overview
returned 11 rows, and lifecycle overview returned 30 rows.

## 11. Next-Step Boundary

WP-9y is not a REC stability lock and not a Main 3.0 promotion, policy,
paper/live, evidence scoring, ranking, recommendation, or runtime decision.

The next valid step, if desired, is a later explicitly scoped package that
keeps REC consumer facts separate from future policy and execution authority.
