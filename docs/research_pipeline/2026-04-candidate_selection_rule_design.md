# Candidate-Selection Rule Design (WP-10j)

## Purpose

WP-10j is a documentation-only rule-design package. It defines criteria a
future package may use when deciding which candidates should receive future
forward-flow evidence planning.

WP-10j does not apply the rules, select candidate IDs, rank or recommend
strategies, create a cohort, create EXP, REP, OL, or REC artifacts, implement
policy, score evidence quality, create paper/live semantics, or touch runtime,
deployment, OMS, risk, safe-mode, execution, configs, dependencies, or
protected paths.

## Locked Inputs

WP-10j consumes these locked descriptive inputs:

- WP-10i Phase 10 architecture plan.
- WP-10h forward-flow evidence plan.
- WP-10g `REC-0012` correction.
- WP-10f Phase 9 -> Phase 10 transition decision.
- WP-10e REC-5 floor-gap stability lock.
- WP-10d REC cross-expectation-source consumer.
- REC v1 stability lock.
- Outcome-ledger v1 stability lock.
- Lifecycle stability lock.

These inputs are rule-design inputs only. They create no implementation,
ranking, recommendation, promotion, demotion, policy, paper/live,
evidence-scoring, runtime, or protected-path authority.

## Current Machine State

Current repo truth records:

- REC corpus: 22 rows, `REC-0001` through `REC-0022`.
- REC expectation-source distribution: 11 `exp_success_criteria` rows and 11
  `d2_006_gates` rows.
- REC verdict distribution: 13 `partially_met`, 8 `none_met`, and 1
  `insufficient_evidence`.
- REC-5 state: every current `candidate_id / outcome_kind / pipeline_version /
  expectation_source_type` segment has `reconciliation_count = 1`.
- Outcome ledger: 11 rows, `OL-0001` through `OL-0011`.
- Lifecycle changes: 30 rows, with transition counts 10 / 10 / 10 for
  `proposed -> in_research`, `in_research -> research_concluded`, and
  `research_concluded -> archived`.
- Candidate registry overview exposes `H-001` through `H-011`.
- OL and REC coverage currently covers `H-001` through `H-010`.
- H-004 remains structurally split in OL and REC under both expectation
  sources.
- `REC-0012` correction is complete.
- `REC-0012`, `REC-0017`, and `REC-0019` preserve the extracted D2-006
  cost-drag gate and skip deterministic cost-drag pass/fail comparison when
  `gross_pnl <= 0`.
- No open D2 non-positive-gross-PnL cost-drag anomaly remains.

The H-004 REC split is:

```text
REC-0005 / OL-0005 / H-004 / pre_wp_5b / exp_success_criteria / partially_met
REC-0011 / OL-0011 / H-004 / post_wp_5b / exp_success_criteria / insufficient_evidence
REC-0016 / OL-0005 / H-004 / pre_wp_5b / d2_006_gates / partially_met
REC-0022 / OL-0011 / H-004 / post_wp_5b / d2_006_gates / partially_met
```

## Candidate-Selection Rule Objective

Future candidate selection means selecting a candidate to receive future
evidence planning. It does not mean candidate recommendation, strategy
ranking, promotion, demotion, paper/live readiness, policy readiness, or
runtime deployment.

Candidate-selection rules must preserve:

- REC-5 segment boundaries.
- expectation-source separation.
- pipeline-version separation.
- H-004 pre/post structural split semantics.

## Allowed Rule Inputs

A future rule-application package may consume these existing surfaces as
eligibility inputs only:

- candidate registry fields;
- lifecycle state;
- OL coverage;
- REC coverage;
- REC-5 evidence gap;
- expectation-source coverage;
- pipeline-version coverage;
- strategy-family coverage, if queryable;
- artifact validity and integrity state;
- data availability, if already documented;
- feasibility constraints, if documented;
- blocked or forbidden-path constraints.

These inputs are not scores. They must not be converted into performance
rankings, recommendations, promotion signals, policy actions, or paper/live
readiness claims without later explicit authorization.

## Hard Eligibility Gates

A candidate may be eligible for future forward-flow evidence planning only if:

1. The candidate exists in the registry or another authoritative candidate
   source.
2. The candidate has no integrity blockers.
3. The candidate has valid lifecycle provenance.
4. Relevant OL and REC artifacts, if present, are validator-clean.
5. The target segment can be identified as `candidate_id / outcome_kind /
   pipeline_version / expectation_source_type`.
6. The target segment remains below REC-5.
7. Future evidence can be generated without cloning or splitting retrospective
   artifacts.
8. No policy, ranking, scoring, paper/live, runtime, deployment, config,
   dependency, or protected-path work is required.

If any hard gate fails, future selection should be blocked until a separate
corrective or architecture package resolves the blocker.

## Descriptive Tie-Breaker Criteria

After hard gates pass, a future package may use these descriptive
tie-breakers only to decide where to spend future evidence-planning effort:

- artifact completeness;
- clarity of EXP/REP provenance;
- clearer evaluation-window path;
- lower ambiguity in pipeline-version handling;
- clean expectation-source mapping;
- data availability;
- lifecycle completeness;
- strategy-family representation;
- feasibility of future observation.

These tie-breakers must not be represented as performance rankings,
recommendations, scores, promotion signals, demotion signals, policy readiness,
paper/live readiness, or runtime actions.

## Explicitly Forbidden Criteria

Future candidate-selection rule application must not use:

- current performance superiority;
- inferred improvement or degradation;
- strategy ranking;
- policy readiness;
- paper/live readiness;
- runtime deployability;
- subjective preference;
- combined expectation-source counts;
- combined pipeline-version counts;
- combined H-004 pre/post rows;
- evidence-quality scoring;
- manual REC-5 override.

## REC-5 Handling

REC-5 remains:

```text
n >= 3 per candidate_id / outcome_kind / pipeline_version / expectation_source_type
```

Rules may consider the evidence gap for a target segment. Every current segment
has `reconciliation_count = 1`, so the minimum additional observations for any
current target segment remains 2.

Selection does not satisfy REC-5. No expectation sources, pipeline versions,
or H-004 split rows may be combined to satisfy REC-5.

## H-004 Handling

H-004 is structurally split under both expectation sources. Future H-004
evidence planning must identify either `pre_wp_5b` or `post_wp_5b` as the
target pipeline version.

H-004 pre/post rows cannot be combined. The current H-004 split supports no
improvement or degradation inference, no pipeline-version performance
comparison, no ranking, no recommendation, no policy readiness, and no
paper/live readiness claim.

## Expectation-Source Handling

`exp_success_criteria` and `d2_006_gates` remain independent expectation
source types. Counts do not combine across sources.

A future package may target one or both expectation sources only if Main 3.0
authorizes that decision. WP-10j does not select source priority and does not
infer source superiority.

## Future Output Shape

A future candidate-selection rule-application package may output:

```text
candidate_id
target_outcome_kind
target_pipeline_version
target_expectation_source_type
eligibility_status
eligibility_gate_results
descriptive_tie_breaker_notes
required_future_evidence_units
blocked_reason, if blocked
```

Forbidden output fields:

```text
rank
score
recommendation
promotion_status
paper_live_readiness
policy_action
runtime_action
```

## Candidate-Selection Application Package Boundary

A future application package must be documentation/query-consumer only unless
Main 3.0 authorizes otherwise. It may consume central query surfaces and
produce a descriptive eligibility matrix.

It may not create EXP plans, select final execution candidates, implement
scoring, implement ranking, recommend strategies, imply policy authority,
create paper/live semantics, or touch runtime or protected paths.

## Validation Requirements For Future Application

A future rule-application package must run:

- relevant registry validators;
- REC validator;
- OL validator;
- lifecycle validator;
- candidate registry validation if available;
- all discovered `v_integrity_*` views;
- REC, OL, and lifecycle overview regressions;
- targeted pytest;
- full pytest where appropriate;
- `git diff --check`;
- changed-file scope inspection;
- protected-path preservation.

## Stop Conditions For Future Application

A future rule-application package must stop if it requires:

- artifact mutation;
- schema, validator, or query-layer changes without an architecture decision;
- ranks, scores, or recommendations;
- promotion, demotion, or policy implications;
- runtime or protected-path changes;
- forbidden REC-5 dimension combining;
- non-empty integrity views;
- failing tests.

## Supported Uses

WP-10j supports:

- defining candidate-selection criteria;
- defining eligibility gates;
- defining a future output shape;
- informing a future rule-application package;
- preserving REC-5 boundaries;
- preventing ranking or recommendation drift.

## Unsupported Claims

WP-10j does not support claims of:

- candidate selection;
- ranking;
- recommendation;
- promotion or demotion;
- policy readiness;
- paper/live readiness;
- evidence-quality scoring;
- REC-5 satisfaction;
- new evidence creation;
- experiment creation;
- runtime, deployment, OMS, risk, safe-mode, or execution authority;
- protected-path authority.

## Next Package Boundary

The next package should be either:

- WP-10k candidate-selection eligibility matrix / rule application,
  documentation/query-consumer only; or
- WP-10k evidence-generation architecture detail if Main 3.0 prefers more
  planning before applying rules.

No future EXP planning scaffold should proceed until Main 3.0 explicitly
approves moving beyond architecture. Policy, ranking, scoring, paper/live, and
runtime packages remain forbidden.

## Validation Snapshot

WP-10j validation records:

- REC validator: PASS.
- `v_reconciliation_overview`: 22 rows.
- REC expectation-source distribution: 11 `exp_success_criteria` rows and 11
  `d2_006_gates` rows.
- `v_reconciliation_candidate_pipeline_summary`: every current segment has
  `reconciliation_count = 1`.
- REC integrity views: `[]`.
- all discovered `v_integrity_*` views: `[]`.
- outcome-ledger validator: PASS.
- `v_outcome_ledger_overview`: 11 rows.
- `v_outcome_ledger_candidate_pipeline_summary`: H-004 split preserved.
- lifecycle validator: PASS.
- `v_lifecycle_change_overview`: 30 rows.
- `v_lifecycle_state_transitions`: 10 / 10 / 10.
- targeted tests: PASS.
- full pytest: PASS.
- `git diff --check`: PASS.

## Non-Claims

WP-10j creates no:

- candidate selection;
- ranking or recommendation;
- EXP, REP, OL, or REC artifacts;
- REC-5 satisfaction;
- policy;
- promotion or demotion;
- paper/live semantics;
- evidence-quality scoring;
- schema;
- validator;
- query-layer view;
- runtime, deployment, OMS, risk, safe-mode, or execution authority;
- protected-path authority.
