# Stage 2 Candidate-Selection Application (WP-10q)

## Purpose

WP-10q is a documentation-only Stage 2 candidate-selection methodology
application. It consumes WP-10p's Stage 2 authorization decision and WP-10k's
eligibility matrix, applies WP-10p's non-performance-based methodology, and
selects exactly one real exact segment for the Stage 2 first sub-stage.

The selected exact segment is a methodology output. It is not a cohort, not a
recommendation, not a policy decision, not a performance quality claim, and not
REC-5 satisfaction.

## Locked inputs

WP-10q consumes these locked inputs:

- WP-10p Stage 2 authorization decision:
  `docs/research_pipeline/2026-04-stage2_authorization_decision.md`.
- WP-10o Stage 1 checkpoint lock:
  `docs/research_pipeline/2026-04-stage1_checkpoint_lock.md`.
- WP-10h forward-flow evidence plan:
  `docs/research_pipeline/2026-04-forward_flow_evidence_plan.md`.
- WP-10j candidate-selection rule design:
  `docs/research_pipeline/2026-04-candidate_selection_rule_design.md`.
- WP-10k candidate-selection eligibility matrix:
  `research/briefs/2026-04-candidate_selection_eligibility_matrix.md`.
- WP-10k Q03 eligibility output:
  `research/briefs/2026-04-candidate_selection_eligibility_matrix/outputs/Q03.json`.
- Current candidate, EXP/REP, OL, REC, lifecycle, and central query-surface
  repo truth.

These inputs are read-only for WP-10q.

## WP-10p authorization boundary

WP-10p authorizes only a conservative Stage 2 first sub-stage. The first
sub-stage is single-segment only and Path A only.

Path A means one future new REP against an existing committed EXP for the
selected eligible segment, followed by later separately scoped OL and REC
append packages if they are authorized and validated. Path A creates no new
EXP.

EXP scaffolds remain blocked through the entire Stage 2 first sub-stage.
WP-10q creates no EXP scaffold, EXP, REP, OL, REC, LCH, or registry artifact.
WP-10q creates no schema, validator, query-layer, test, runtime, config,
dependency, data, or protected-path change.

## Candidate universe from Q03

Q03 contains 23 rows:

- 22 rows marked `eligible_for_future_evidence_planning`.
- 1 row for H-011 marked `not_applicable` with
  `no_current_ol_rec_target_segment`.

The eligible Q03 rows preserve exact REC-5 segment identity as:

```text
candidate_id / target_outcome_kind / target_pipeline_version / target_expectation_source_type
```

Every eligible row has non-null exact segment dimensions, `blocked_reason =
null`, and `required_future_evidence_units = 2`.

## Selection methodology

WP-10q applies WP-10p's methodology in this order:

1. Start from Q03 rows marked `eligible_for_future_evidence_planning`.
2. Exclude H-011, `not_applicable` rows, rows with missing exact segment
   dimensions, and rows requiring forbidden scope.
3. Require exact segment identity.
4. Require below-REC-5 posture.
5. Require existing committed provenance sufficient for future Path A review
   without creating a new EXP.
6. Require direct Path A applicability.
7. Prefer current post-WP-5b forward-flow semantics. Because post-WP-5b
   eligible rows exist, pre-WP-5b rows are not selectable for this first
   sub-stage.
8. Preserve expectation-source clarity.
9. Preserve H-004 pipeline-version and expectation-source separation.
10. Apply the stable lexical tie-break only after the hard gates.

WP-10q does not use realized metric strength, realized metric weakness, REC
verdict favorability, candidate quality ranking, policy readiness, paper/live
readiness, subjective preference, observed performance, Sharpe, drawdown,
trade count, PnL, or any other performance metric as selection criteria.

## Hard-gate application

The hard gates produce this current universe:

- Q03 eligible rows before current-forward-flow filtering: 22.
- H-011 rows eligible for selection: 0.
- Post-WP-5b eligible rows after current-forward-flow filtering: 2.

The two remaining rows are:

```text
H-004 / research_oos / post_wp_5b / d2_006_gates
H-004 / research_oos / post_wp_5b / exp_success_criteria
```

Both remaining rows have exact segment identity, remain below REC-5, have
committed OL/REC posture, and point to the existing post-WP-5b H-004
provenance chain.

## Exclusion summary

Pre-WP-5b eligible rows are excluded from selection because WP-10p says the
Stage 2 first sub-stage targets current forward-flow semantics and current
post-WP-5b eligible rows exist.

H-011 is excluded because Q03 marks it `not_applicable` with
`no_current_ol_rec_target_segment`.

No row is excluded because of realized metrics, REC verdict favorability,
strategy-family preference, candidate popularity, or narrative appeal.

## Deterministic tie-break

After hard gates, the remaining exact segment keys are sorted by stable
lexical order:

```text
candidate_id / target_outcome_kind / target_pipeline_version / target_expectation_source_type
```

The sorted remaining rows are:

```text
H-004 / research_oos / post_wp_5b / d2_006_gates
H-004 / research_oos / post_wp_5b / exp_success_criteria
```

The deterministic tie-break therefore selects the first row:

```text
H-004 / research_oos / post_wp_5b / d2_006_gates
```

This is a deterministic methodology tie-break, not performance ranking.

## Selected exact segment

WP-10q selects exactly one exact segment:

```text
candidate_id: H-004
outcome_kind: research_oos
pipeline_version: post_wp_5b
expectation_source_type: d2_006_gates
```

This selected exact segment does not satisfy REC-5. Current repo truth records
`reconciliation_count = 1` for this exact segment, below the `n >= 3` floor.

## Paired expectation-source posture

H-004 post-WP-5b has paired expectation-source posture in current repo truth:

```text
REC-0022 / OL-0011 / H-004 / post_wp_5b / d2_006_gates
REC-0011 / OL-0011 / H-004 / post_wp_5b / exp_success_criteria
```

WP-10q selects only the `d2_006_gates` exact segment. The paired
`exp_success_criteria` row remains separate and may inform later WP-10t
planning if that later package is separately scoped and validated.

Expectation sources do not combine for REC-5, scoring, ranking,
recommendation, policy, paper/live readiness, or runtime authority.

## H-004 separation handling

H-004 is selected only as one exact segment:

```text
H-004 / research_oos / post_wp_5b / d2_006_gates
```

H-004 pre/post rows remain separate. WP-10q makes no pre/post comparison, no
improvement claim, no degradation claim, and no special-case policy treatment.

Current H-004 REC posture remains:

```text
REC-0005 / OL-0005 / H-004 / pre_wp_5b / exp_success_criteria
REC-0011 / OL-0011 / H-004 / post_wp_5b / exp_success_criteria
REC-0016 / OL-0005 / H-004 / pre_wp_5b / d2_006_gates
REC-0022 / OL-0011 / H-004 / post_wp_5b / d2_006_gates
```

## H-011 exclusion confirmation

H-011 is not selected and is not included in the Stage 2 first sub-stage.
Current repo truth records H-011 as registry-present with no current OL/REC
target segment. Q03 marks H-011 `not_applicable` with
`no_current_ol_rec_target_segment`.

WP-10q does not demote H-011, replace H-011 by comparison, register H-012 or
beyond, or authorize a new-candidate evidence path.

## Path A readiness statement

Current repo truth records existing committed H-004 post-WP-5b provenance:

```text
EXP-0011 / REP-0011 / OL-0011 / REC-0022
```

This is sufficient for WP-10q to record direct Path A applicability: a future
WP-10r may draft one new REP against existing committed `EXP-0011` for the
selected exact segment, if WP-10r is separately scoped and validates its own
evaluation window and artifact boundaries.

WP-10q does not define the future evaluation window and does not create the
future REP.

## What WP-10q authorizes next

WP-10q authorizes only the next package boundary:

```text
WP-10r may draft one new REP against existing committed EXP-0011 for
H-004 / research_oos / post_wp_5b / d2_006_gates,
if separately scoped and validated.
```

WP-10r must stop if it cannot define an unambiguous evaluation window, preserve
Path A, avoid new EXP creation, and pass its own validators and scope checks.

## What WP-10q does not authorize

WP-10q does not authorize:

- EXP scaffold or EXP plan creation.
- New EXP artifact creation.
- REP, OL, REC, LCH, or registry artifact creation.
- Path B.
- Small-cohort work.
- H-011 inclusion.
- New candidate or H-012-and-beyond work.
- Synthetic evidence for REC-5.
- REC-5 satisfaction.
- Policy implementation.
- Evidence-quality scoring.
- Ranking or recommendation implementation.
- Promotion or demotion.
- Paper/live readiness or semantics.
- Runtime, deployment, OMS, risk, safe-mode, execution, config, dependency,
  data, or protected-path behavior.

## Validation snapshot

WP-10q validation is expected to cover:

- all available `tools.registry.validate_*` validators;
- all discovered `v_integrity_*` views, expected `[]`;
- targeted registry, research-query, reconciliation, outcome-ledger, and
  lifecycle tests;
- full pytest;
- semantic scans for forbidden authority language;
- `git diff --check`;
- changed-file inspection.

The expected changed-file set is exactly:

```text
docs/project_status.md
docs/research_pipeline/2026-04-stage2_candidate_selection_application.md
```

## Non-claims

WP-10q creates no:

- cohort;
- EXP scaffold;
- EXP, REP, OL, REC, LCH, or registry artifact;
- schema;
- validator;
- query-layer view or behavior;
- test;
- runtime, deployment, OMS, risk, safe-mode, or execution authority;
- config, dependency, data, or protected-path change;
- Path B authority;
- H-011 inclusion;
- REC-5 satisfaction;
- performance-based selection;
- policy;
- scoring;
- ranking or recommendation;
- paper/live semantics.
