# Phase 9 -> Phase 10 Transition Decision (WP-10f)

## Purpose

WP-10f is a documentation-only transition decision after the WP-10e REC-5
floor-gap stability lock.

It closes the Phase 9 / Tranche E descriptive research-machine tranche and
defines what Phase 10 may and may not start. It does not implement Phase 10
and creates no policy, ranking, recommendation, evidence-quality scoring,
paper/live, runtime, deployment, OMS, risk, safe-mode, execution, config,
dependency, or protected-path authority.

## Locked Inputs

WP-10f consumes these locked inputs:

- WP-10a post-REC architecture checkpoint.
- WP-10b D2-006 gates seed and methodology.
- WP-10c D2-006 gates retrospective bulk backfill.
- WP-10d cross-expectation-source REC consumer.
- WP-10e REC-5 floor-gap stability lock.
- REC v1 stability lock.
- Outcome-ledger v1 stability lock.
- Lifecycle stability lock.

These inputs are descriptive research-machine baselines only.

## Current Locked Machine State

- REC corpus: 22 rows, `REC-0001` through `REC-0022`.
- REC expectation-source distribution: 11 `exp_success_criteria` rows and
  11 `d2_006_gates` rows.
- REC-5 floor: `n >= 3 per candidate_id / outcome_kind / pipeline_version /
  expectation_source_type`.
- REC-5 current state: every current segment has `reconciliation_count = 1`;
  no current segment satisfies REC-5.
- Outcome ledger: 11 rows, `OL-0001` through `OL-0011`.
- Lifecycle changes: 30 rows, with transition counts 10 / 10 / 10 for
  `proposed -> in_research`, `in_research -> research_concluded`, and
  `research_concluded -> archived`.
- H-004 remains structurally split under both expectation sources:

```text
REC-0005 / OL-0005 / H-004 / pre_wp_5b / exp_success_criteria / partially_met
REC-0011 / OL-0011 / H-004 / post_wp_5b / exp_success_criteria / insufficient_evidence
REC-0016 / OL-0005 / H-004 / pre_wp_5b / d2_006_gates / partially_met
REC-0022 / OL-0011 / H-004 / post_wp_5b / d2_006_gates / partially_met
```

- `REC-0012` remains known anomaly debt: a pre-WP-10c D2 seed that compares
  cost drag despite `gross_pnl <= 0`, surfaced by WP-10d and locked by
  WP-10e as
  `compared_despite_non_positive_gross_pnl_pre_wp10c_seed_requires_followup`.

## Transition Decisions

### TD-1 - Phase 9 Descriptive Research Machine Is Closed But Not Policy-Authoritative

Decision:

- Phase 9 produced stable descriptive surfaces: lifecycle, outcome-ledger,
  REC, the cross-source REC consumer, and the REC-5 floor-gap lock.
- These surfaces are decision-support inputs only.

Non-authority:

- no promotion/demotion.
- no ranking/recommendation.
- no paper/live readiness.
- no policy.
- no runtime or protected-path authority.

### TD-2 - REC-5 Remains The Evidence Floor

Decision:

- REC-5 remains `n >= 3 per candidate_id / outcome_kind / pipeline_version /
  expectation_source_type`.
- Counts cannot be combined across expectation sources, pipeline versions, or
  the H-004 structural split.
- Dual-source coverage does not satisfy REC-5.

Consequence:

- Phase 10 cannot treat the current REC corpus as sufficient evidence for
  policy.

### TD-3 - REC-0012 Anomaly Is Carried As Known Debt, Not Clean Evidence

Decision:

- Do not silently reinterpret `REC-0012` as clean.
- Do not correct `REC-0012` in WP-10f.
- Any correction requires a future explicit artifact-correction package.
- Any policy, scoring, or ranking package must either correct it first or
  explicitly exclude it.

### TD-4 - Forward-Flow Evidence Is Required Before Policy / Promotion / Demotion

Decision:

- Retrospective backfill and dual-source coverage are not enough for
  promotion/demotion policy.
- Future sufficient-evidence work must plan additional forward-flow evidence
  or explicit new experiments before policy surfaces can claim evidence
  satisfaction.

### TD-5 - Phase 10 May Begin Only With Planning / Architecture Or Corrective Packages

Allowed immediate post-WP-10f package classes:

1. `REC-0012` correction package.
2. Forward-flow evidence plan.
3. Phase 10 architecture plan.
4. Evidence-generation design package.
5. Documentation-only decision-support package.

Forbidden immediate package classes:

1. Promotion/demotion policy implementation.
2. Ranking/recommendation implementation.
3. Evidence-quality scoring implementation.
4. Paper/live readiness implementation.
5. Runtime, OMS, risk, safe-mode, execution, deployment, config, dependency,
   or protected-path implementation.

## Recommended Immediate Next Package Candidates

### Candidate A - WP-10g REC-0012 Artifact-Correction Package

Purpose:

- Correct the pre-WP-10c cost-drag comparison anomaly in `REC-0012`.

Allowed scope:

- `REC-0012`.
- Narrow docs/test updates if required.

Risks:

- Artifact mutation must be explicit and preserved.
- No bulk edits.
- No schema, validator, or query-layer changes unless separately decided.

### Candidate B - WP-10g Forward-Flow Evidence Plan

Purpose:

- Define how to generate enough future evidence to satisfy REC-5.

Allowed scope:

- Documentation-only planning artifact.
- No new experimental results.
- No policy.

Risks:

- Can drift into research execution or policy.

### Candidate C - WP-10g Phase 10 Architecture Plan

Purpose:

- Define Phase 10 package sequence and gates.

Allowed scope:

- Documentation-only planning/architecture.

Risks:

- Can prematurely authorize implementation.

Recommended posture:

- If Main 3.0 prioritizes semantic cleanliness, choose Candidate A.
- If Main 3.0 prioritizes evidence sufficiency, choose Candidate B.
- If Main 3.0 prioritizes broader sequencing, choose Candidate C.
- Do not choose policy, scoring, ranking, paper/live, or runtime as the
  immediate next package.

## Required Main 3.0 Decision Before Next Implementation

Ask Main 3.0 to decide:

1. Should `REC-0012` be corrected before any further consumer or planning work?
2. Should the next package be a corrective artifact package, forward-flow
   evidence plan, or Phase 10 architecture plan?
3. Are all downstream outputs still descriptive-only until REC-5 is satisfied?
4. What evidence-generation path may create new REC-satisfying observations?
5. What package classes remain forbidden?
6. Should Phase 10 have a new phase status doc or remain under
   research-pipeline docs until evidence exists?

## Supported Uses After WP-10f

Supported:

- architecture planning.
- known-debt tracking.
- floor-gap tracking.
- forward-flow evidence planning.
- descriptive research-machine inspection.
- package-sequence decision support.

## Unsupported Claims After WP-10f

Unsupported:

- promotion/demotion.
- ranking/recommendation.
- policy.
- paper/live readiness.
- evidence-quality scoring.
- strategy-family performance conclusion.
- pipeline-version performance comparison.
- cross-window inference.
- runtime/deployment authority.
- OMS/risk/safe-mode/execution authority.
- protected-path authority.

## Mutation / Evolution Rules

- Do not lower REC-5 silently.
- Do not combine expectation sources to satisfy REC-5.
- Do not combine pre/post pipeline versions to satisfy REC-5.
- Do not combine H-004 structural split rows to satisfy REC-5.
- Do not use dual-source coverage as floor satisfaction.
- Do not reinterpret `REC-0012` as clean without explicit correction.
- Future artifact correction must be explicit, narrow, and validator-backed.
- Phase 10 implementation requires Main 3.0 authorization after WP-10f.

## Validation Snapshot

WP-10f validation records:

- REC validator: PASS.
- `v_reconciliation_overview`: 22 rows.
- `v_reconciliation_candidate_pipeline_summary`: every segment has
  `reconciliation_count = 1`.
- REC integrity views: `[]`.
- All discovered `v_integrity_*` views: `[]`.
- Outcome-ledger validator: PASS.
- `v_outcome_ledger_overview`: 11 rows.
- `v_outcome_ledger_candidate_pipeline_summary`: H-004 split preserved.
- Lifecycle validator: PASS.
- `v_lifecycle_change_overview`: 30 rows.
- `v_lifecycle_state_transitions`: 10 / 10 / 10.
- Targeted tests: PASS.
- Full pytest: PASS.
- `git diff --check`: PASS.

## Non-Claims

WP-10f does not create:

- Phase 10 implementation.
- REC artifact correction.
- REC-5 satisfaction.
- policy.
- promotion/demotion.
- ranking/recommendation.
- paper/live semantics.
- evidence-quality scoring.
- schema.
- validator.
- query-layer view.
- artifact instance.
- runtime/deployment/OMS/risk/safe-mode/execution authority.
- protected-path authority.
