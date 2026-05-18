# Stage 2 Second-Pass Segment Selection Application

## Package Metadata

- Package label: WP-12ac / S2b-1.
- Package title: Stage 2 Second-Pass Segment Selection Application.
- Package class: Tier 1 documentation-only / decision-support selection package.
- Effective base: refreshed `main` after merged WP-12ab / AUTO-27.
- Committed files: this document and `docs/project_status.md` only.
- No implementation files.
- No test files.
- No generated query outputs.
- No EXP, REP, OL, REC, LCH, or registry artifacts.

## Purpose

This package applies the locked WP-10j / WP-10k / WP-10q non-performance
selection methodology to current repo truth and selects exactly one exact
segment for the A1 additional Path A floor-crossing extension runway.

The selected segment is a methodology output only. It is not a recommendation,
ranking, score, approval, promotion, readiness claim, policy action, lifecycle
action, runtime decision, or downstream authority.

## Runway Framing And A2 Preservation

Per PCB-3 resolution and Karl's A1-with-A2-preserved clarification: this
package is part of the A1 floor-crossing extension runway. A2 (Stage 2 second
sub-stage / cohort / Path B architecture) remains the queued reassessment
target for after this runway's checkpoint, subject to repo truth and boundary
review at WP-S2b-8. This package does not authorize A2 work, does not
pre-commit A2 direction, and does not retire A2 as a future option.

## Locked Inputs

Reviewed locked inputs:

- WP-12ab post-AUTO-usability direction decision:
  `docs/research_pipeline/2026-04-post_auto_usability_direction_decision.md`.
- Main/Karl A1 runway direction, with A2 preserved for later checkpoint
  reassessment.
- WP-11c Stage 2 first-sub-stage stability lock:
  `docs/research_pipeline/2026-04-stage2_first_substage_stability_lock.md`.
- WP-11b post-consumer-brief direction decision:
  `docs/research_pipeline/2026-04-post_consumer_brief_direction_decision.md`.
- WP-10p Stage 2 authorization decision:
  `docs/research_pipeline/2026-04-stage2_authorization_decision.md`.
- WP-10q Stage 2 candidate-selection application:
  `docs/research_pipeline/2026-04-stage2_candidate_selection_application.md`.
- WP-10j candidate-selection rule design:
  `docs/research_pipeline/2026-04-candidate_selection_rule_design.md`.
- WP-10k candidate-selection eligibility matrix:
  `research/briefs/2026-04-candidate_selection_eligibility_matrix.md`.
- Current REC / OL / REP / EXP / LCH artifacts and central query surfaces.

## Current Exact-Segment State

Current repo truth exposes 22 exact REC segments in
`v_reconciliation_candidate_pipeline_summary`, keyed by:

```text
candidate_id / outcome_kind / pipeline_version / expectation_source_type
```

The already floor-crossed exact segment is:

```text
H-004 / research_oos / post_wp_5b / d2_006_gates
```

That segment has `reconciliation_count = 3` through `REC-0022`, `REC-0023`,
and `REC-0024`.

All other exact REC segments remain below REC-5. The paired post-WP-5b H-004
segment remains:

```text
H-004 / research_oos / post_wp_5b / exp_success_criteria
```

with `reconciliation_count = 1` through `REC-0011`.

Current post-WP-5b H-004 provenance includes committed `EXP-0011`, `REP-0011`,
`REP-0012`, `REP-0013`, `OL-0011`, `OL-0012`, `OL-0013`, `REC-0011`,
`REC-0022`, `REC-0023`, and `REC-0024`. The selected below-floor segment can
therefore reference existing committed `EXP-0011` for future Path A work.

No cross-segment performance inference is made from this state.

## Selection Methodology

The applied method follows WP-10j / WP-10q order:

1. Start from exact REC segment identities in current repo truth.
2. Exclude segments already REC-5 floor-crossed.
3. Exclude rows lacking exact segment identity.
4. Exclude rows requiring Path B, cohort scope, EXP scaffold creation, H-011
   first-time inclusion, H-012+ registration, or forbidden authority expansion.
5. Require candidate presence in the authoritative candidate source.
6. Require no integrity blockers.
7. Require valid lifecycle provenance and validator-clean relevant OL / REC
   artifacts.
8. Require the segment to remain below REC-5.
9. Require direct A1 Path A applicability against an existing committed EXP,
   without cloning or splitting retrospective artifacts.
10. Apply descriptive tie-breakers only after hard gates.
11. Apply stable lexical tie-break only if multiple candidates remain.

No REC verdict favorability, performance superiority, Sharpe, drawdown, trade
count, PnL, candidate popularity, narrative preference, expectation-source
combining, pipeline-version combining, H-004 pre/post combining,
evidence-quality scoring, or manual REC-5 override was used.

## Hard-Gate Application

Hard-gate reduction:

- Exact REC segments considered: 22.
- Excluded because already REC-5 floor-crossed: 1.
- Excluded because they are not direct A1 runway Path A targets against the
  current post-WP-5b H-004 `EXP-0011` provenance: 20.
- Excluded because forbidden scope would be required: 0.
- Final eligible count before tie-break: 1.

The final eligible exact segment is:

```text
H-004 / research_oos / post_wp_5b / exp_success_criteria
```

Because exactly one eligible segment remains after hard gates, no stable
lexical tie-break is used.

## Selected Exact Segment

```text
candidate_id: H-004
outcome_kind: research_oos
pipeline_version: post_wp_5b
expectation_source_type: exp_success_criteria
current_reconciliation_count: 1
rec5_target: 3
additional_observations_needed: 2
existing_exp_id_for_path_a: EXP-0011
```

This selection does not satisfy REC-5. It does not create REP, OL, REC, LCH,
registry, or EXP artifacts. It does not create or authorize an EXP scaffold. It
does not create recommendation, ranking, score, policy, readiness, lifecycle,
runtime, or downstream authority.

## What This Package Authorizes Next

The next runway package may draft one new REP against the existing committed
EXP identified above for the selected exact segment, if separately scoped and
validated.

## What This Package Does Not Authorize

This package does not authorize:

- EXP scaffold.
- EXP artifact.
- REP, OL, REC, LCH, or registry artifact.
- Path B.
- Cohort scope.
- H-011 first-time inclusion.
- H-012+ or new candidate registration.
- A2 implementation.
- AUTO successor package.
- Schema, validator, or query-layer change.
- Implementation or tests.
- Runtime, paper-live, OMS, risk, safe-mode, exchange, broker, or order
  behavior.
- Protected-path behavior.
- Policy, scoring, ranking, recommendation, approval, promotion, demotion,
  readiness, lifecycle, or downstream authority.

## Validation Snapshot

Package discovery and validation expectations are:

- Registry validators: all discovered `tools/registry/validate_*.py` modules.
- Query views: `tools.research_query.run --list-views`.
- Integrity views: all discovered `v_integrity_*` views with JSON output,
  expected `[]`.
- Scope checks: changed files limited to this document and
  `docs/project_status.md`.
- Confidence tests: scoped pytest selection and full pytest.

At package drafting time, standing integrity discovery found:

- Registry validators: 14 discovered, 14 passed.
- Query views: 55 listed.
- `v_integrity_*` views: 24 checked, all returned `[]`.

Final validation results are reported in the PR and execution report-back.

## Non-Claims

WP-12ac / S2b-1 creates no EXP, REP, OL, REC, LCH, registry artifact,
canonical evidence artifact, generated query-output bundle, query-layer view,
schema, validator, implementation, test, config, dependency, data, AUTO
successor, Path B, cohort, H-011 inclusion, H-012+ registration, runtime,
paper-live, OMS, risk, safe-mode, exchange, broker, order behavior,
protected-path behavior, policy, scoring, ranking, recommendation, approval,
promotion, demotion, readiness, lifecycle transition, REC-5 satisfaction, or
downstream authority.
