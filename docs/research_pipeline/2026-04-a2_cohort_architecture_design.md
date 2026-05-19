# A2 Cohort Architecture Design

## Package Metadata And Scope

- Package label: WP-12am / WP-S2c-4.
- Package title: A2 Cohort Architecture Design.
- Package class: Tier 1 documentation-only architecture/design package.
- Effective base: post-WP-12al / post-SS-D scope-shape lock.
- Committed files: this document and `docs/project_status.md` only.

This package defines cohort architecture for the first SS-D A2 phase. It sets
architecture-level treatment for floor discipline, expectation-source symmetry,
cohort envelope, Tier 4 distance, schema posture, and the boundary to
WP-S2c-5.

This package has no implementation authority. It does not select cohort
members, apply cohort selection methodology, authorize cohort implementation,
open Path B design beyond deferred-status framing, author EXP scaffolds, create
artifacts, modify schemas, validators, query-layer behavior, implementation,
configs, dependencies, data, runtime, or protected paths, or create
policy/scoring/ranking/recommendation/promotion/readiness/lifecycle authority.

## Context

WP-12aj / WP-S2c-1 opened A2 architecture design after the A1 runway
checkpoint. WP-12ak / WP-S2c-2 surfaced A2 scope-shape options. WP-12al /
WP-S2c-3 locked SS-D:

```text
Cohort then Path B
```

Under SS-D, cohort design comes first and Path B remains staged and deferred.

A1 produced only single-candidate expectation-source symmetry for:

- `H-004 / research_oos / post_wp_5b / d2_006_gates`
- `H-004 / research_oos / post_wp_5b / exp_success_criteria`

Both exact segments are floor-crossed at `reconciliation_count = 3`, but this
is one-candidate expectation-source symmetry only. It is not cross-candidate
inference, policy authority, paper/live readiness, or operational authority.

The cohort phase is intended to design evidence breadth, not operational
authority. This package records cohort architecture only. WP-S2c-5 records
cohort selection methodology.

## Cohort Definition

An A2 cohort is a bounded set of at least two existing registry candidates or
candidate/segment units, evaluated under Path A-equivalent canonical evidence
mechanics using existing committed EXP provenance where required.

Required constraints:

- Cohort members must come from the existing candidate registry.
- No H-012+ registration is authorized.
- No H-011 first-time inclusion is authorized.
- No new EXP scaffold authoring is authorized.
- Cohort members must rely on existing committed EXP provenance where EXP is
  required.
- Outcome kind remains `research_oos` under OL v1 / REC v1 scope.
- Cohort members may begin at different REC states, including `n = 0` or below
  floor.
- Cohort membership does not itself create evidence authority.

This document does not name or select specific cohort members.

## Cohort Member Unit

Cohort membership may be described at candidate or candidate-pipeline level for
readability. That shorthand is descriptive only.

Cohort implementation should track evidence at the exact REC-5 segment level:

```text
(candidate_id, outcome_kind, pipeline_version, expectation_source_type)
```

The exact REC-5 segment remains the unit of evidence authority. A candidate,
candidate plus outcome kind, or candidate plus outcome kind plus pipeline
version description does not collapse expectation sources and does not create a
cohort-level evidence floor.

## Relationship To Existing Single-Candidate Evidence

H-004 post-WP-5b has both expectation-source segments floor-crossed:

- `d2_006_gates`
- `exp_success_criteria`

This is a reference point for why expectation-source symmetry is useful. It is
not a cohort member selection rule. Existing H-004 evidence does not generalize
to other candidates, pipeline versions, or expectation sources.

A2 cohort work exists because A1 lacks cross-candidate breadth. Cohort
architecture must prevent cross-candidate inference from H-004 alone.

## Floor-Discipline Interaction

REC-5 floor remains per exact segment:

```text
(candidate_id, outcome_kind, pipeline_version, expectation_source_type)
```

Architecture implications:

- Cohort-level analysis cannot aggregate below-floor segments into a
  floor-crossed cohort claim.
- One cohort member crossing floor does not imply another member crosses floor.
- One expectation source crossing floor does not imply the other expectation
  source crosses floor.
- Cohort membership may organize work, but does not alter REC-5 semantics.
- Cohort-level documents may summarize counts descriptively only, with no
  cross-segment inference under floor.

## Expectation-Source Symmetry Posture

Expectation-source symmetry is preferred as the design target for cohort
members, but the first cohort phase may proceed with explicit per-source
disclosure if one source is unavailable or blocked.

A1 demonstrated the value of both `d2_006_gates` and `exp_success_criteria`
coverage for H-004. Requiring both sources for every cohort member is stronger
but package-expensive. Allowing partial source coverage is cheaper but weaker.

The preferred posture is:

- Target both expectation sources for cohort members.
- Disclose partial coverage explicitly.
- Never combine expectation sources by default.
- Call out any deviation from symmetry in later implementation authorization.

This posture is a recommended design default, not an implementation lock or
authorization.

## Cohort Envelope

The bounded first cohort design envelope is:

- Minimum cohort size: 2.
- Default design target: 3.
- Maximum first cohort phase size: 4.
- The default should favor a small first cohort to keep package count bounded.
- A larger cohort requires later Main/Karl authorization.

Rough package-envelope estimate:

- WP-S2c-4: architecture design.
- WP-S2c-5: selection methodology.
- A later methodology application / cohort definition package requires
  separate future authorization.
- Later artifact production, if authorized, likely follows per-member
  REP -> OL -> REC chains where existing EXPs support Path A-style evidence.
- Approximate later implementation cost after design is 3 packages per
  additional REP/OL/REC observation chain, multiplied by members and needed
  observations.
- Total cohort implementation runway may be large and must be separately
  authorized after WP-S2c-5.

This document does not authorize the implementation runway.

## Cohort-Level Language Rules

Allowed cohort-level language:

- `cohort member`
- `cohort phase`
- `cohort evidence-production plan`
- `per-member observations`
- `per-segment floor status`
- `descriptive cohort coverage`

Forbidden unless separately authorized:

- `cohort approved`
- `cohort ready`
- `cohort promoted`
- `ranked cohort`
- `best cohort`
- `recommended cohort`
- `policy cohort`
- `deployment cohort`
- `paper/live cohort`
- cross-candidate inference from pooled below-floor results

## Tier 4 Distance

The cohort phase produces canonical research evidence only. Tier 4, runtime,
paper-live, OMS, risk, safe-mode, and execution remain untouched.

Evidence breadth may inform future decisions, but no operational consequences
follow from cohort architecture. No runtime or protected-path package is made
more likely or nearer by this document.

## Schema Versioning Posture

Cohort architecture must operate within OL v1 and REC v1 unless a separate
schema decision is authorized later. No schema changes are required by this
architecture document.

If later cohort work surfaces metrics or evidence relationships not
representable in OL v1 / REC v1, that is a stop trigger and Main/Karl decision
point. Later packages must not smuggle schema expansion into implementation
work.

## Methodology Deferred To WP-S2c-5

WP-S2c-5 is responsible for methodology-level decisions, including:

- eligible-set construction;
- non-performance selection criteria;
- tie-breaking;
- diversity/composition criteria;
- actual cohort definition shape;
- whether to recommend a specific size within the envelope;
- methodology output form;
- any actual application of methodology.

This package does not resolve those items beyond recording that they are
deferred.

## Explicit Non-Claims

WP-S2c-4 does not:

- select cohort members;
- name candidate IDs as chosen members;
- define full selection methodology;
- apply methodology;
- authorize cohort implementation;
- create any EXP, REP, OL, REC, LCH, registry, or brief artifact;
- open Path B design beyond deferred-status framing;
- authorize EXP scaffold authoring;
- change schemas, validators, query-layer behavior, implementation, configs,
  dependencies, data, runtime, or protected paths;
- reactivate AUTO;
- authorize H-011 first-time inclusion or H-012+ registration;
- authorize policy/scoring/ranking/recommendation/promotion/readiness/
  lifecycle authority;
- authorize an automatic package beyond WP-S2c-5.

## Next Package Surface

The next package is:

```text
WP-S2c-5 - Cohort Selection Methodology
```

It drafts automatically after WP-S2c-4 merges if refreshed-main preflight
passes, integrity views remain clean, exact changed-file scope holds, and no
stop trigger fires. WP-S2c-5 remains methodology-only unless separately scoped
otherwise.
