# A2 Cohort Selection Methodology

## Package Metadata And Scope

- Package label: WP-12an / WP-S2c-5.
- Package title: A2 Cohort Selection Methodology.
- Package class: Tier 1 documentation-only methodology/design package.
- Effective base: post-WP-12am / post-cohort-architecture design.
- Committed files: this document and `docs/project_status.md` only.

This package designs a non-performance-based cohort selection methodology for
the first SS-D A2 cohort phase. It defines eligibility criteria, selection
criteria within the eligible set, cohort composition rules, deterministic
tie-breaking, ambiguity handling, and the output shape a future methodology
application package would produce.

This package prepares the mandatory WP-S2c-5 checkpoint. Methodology
application is future work and requires separate authorization.

This package has no implementation authority. It does not apply the
methodology, select cohort members, name chosen candidate IDs, create a cohort
definition, authorize cohort implementation, open Path B design beyond
deferred-status framing, author EXP scaffolds, create artifacts, modify
schemas, validators, query-layer behavior, implementation, configs,
dependencies, data, runtime, or protected paths, or create
policy/scoring/ranking/recommendation/promotion/readiness/lifecycle authority.

## Context

WP-12al / WP-S2c-3 locked SS-D:

```text
Cohort then Path B
```

WP-12am / WP-S2c-4 defined the cohort architecture for the first SS-D A2
phase. It set the first cohort envelope as:

- minimum cohort size: 2;
- default design target: 3;
- maximum first cohort phase size: 4.

WP-12am also kept exact evidence authority at:

```text
(candidate_id, outcome_kind, pipeline_version, expectation_source_type)
```

Expectation-source symmetry is the preferred target. Explicit partial-source
disclosure is allowed if one source is unavailable or blocked. Expectation
sources do not combine by default.

WP-S2c-5 defines methodology only. WP-S2c-5 is the endpoint of the authorized
WP-S2c-3 through WP-S2c-5 design mini-runway. After this package merges,
Main/Karl re-engagement is mandatory before any next package.

## Eligibility Criteria

A future cohort-member candidate or candidate/segment unit is eligible only if
all hard criteria below are satisfied:

- The candidate already exists in the candidate registry.
- The candidate is not an H-012+ registration.
- The candidate does not require H-011 first-time inclusion.
- The candidate/segment has existing committed EXP provenance where EXP is
  required for Path A-style evidence.
- Outcome kind remains `research_oos` under OL v1 / REC v1 scope.
- The candidate/segment is representable under current OL v1 and REC v1
  schemas.
- No schema expansion, validator addition, query-layer addition, or artifact
  family change is required.
- Pipeline version is explicitly recorded and is not collapsed across
  candidates.
- Expectation source is explicitly recorded and is not combined by default.
- Current floor state may vary. `n = 0`, below-floor, or already
  floor-crossed status does not by itself exclude a candidate/segment.
- Inclusion does not require Path B, new EXP scaffold authoring, H-011
  first-time inclusion, H-012+ registration, schema changes, or
  protected-path work.

Eligibility does not equal selection. Eligibility only defines the candidate
universe a future methodology-application package may evaluate.

## Selection Criteria Within Eligible Set

Selection criteria must be non-performance-based. The default methodology
posture is:

```text
Prefer a small cohort that maximizes non-performance evidence breadth while staying within existing committed EXP provenance and OL v1 / REC v1 schema limits.
```

Allowed selection dimensions include:

- Evidence-breadth contribution: candidates/segments with fewer existing REC
  observations may be favored to expand evidence breadth.
- Under-represented structural coverage: if repo truth exposes candidate
  families, tags, pipeline lineage, or comparable non-performance descriptors,
  methodology may favor structural diversity.
- EXP provenance readiness: candidates with existing committed EXP provenance
  can support Path A-style evidence without opening Path B.
- Expectation-source feasibility: candidates/segments where both
  `d2_006_gates` and `exp_success_criteria` are available may support
  expectation-source symmetry.
- Pipeline-version comparability: methodology may prefer a common pipeline
  version for the first cohort if that reduces design complexity.
- Floor-state clarity: methodology may favor candidates/segments whose current
  floor state can be cleanly verified from query truth.

These dimensions are methodology design inputs only. This package does not
convert them into an actual cohort selection.

## Explicitly Forbidden Selection Criteria

Future cohort selection must not use:

- performance-based selection;
- ranking by Sharpe, PnL, drawdown, hit rate, profit factor, gates passed,
  verdict, or any other performance metric;
- "best candidate" language;
- policy, scoring, recommendation, readiness, promotion, demotion, or
  lifecycle framing;
- selection because a candidate appears likely to pass;
- selection because a candidate is live-closer or deployment-attractive;
- selection requiring H-011 first-time inclusion;
- selection requiring H-012+ registration;
- selection requiring new EXP scaffold authoring;
- selection requiring schema, validator, query-layer, runtime, data, config,
  dependency, or protected-path changes.

## Cohort Composition Rules

A valid future cohort definition must satisfy the WP-S2c-4 envelope:

- minimum cohort size: 2;
- default target: 3;
- maximum first cohort phase size: 4;
- a larger cohort requires later Main/Karl authorization.

Methodology-level composition rules:

- All members must satisfy eligibility.
- Selected members should maximize non-performance evidence breadth within the
  envelope.
- The cohort definition must record candidate ID, outcome kind, pipeline
  version, and expectation-source targets for each member.
- If expectation-source symmetry is not feasible for a member, partial source
  coverage must be disclosed explicitly.
- The cohort definition must record current per-segment REC count before any
  implementation.
- The cohort definition must not aggregate below-floor evidence into a
  cohort-level claim.
- If structural tags or families are available in repo truth, prefer diversity
  across those descriptors, but do not invent missing metadata.

This package does not name specific candidates.

## Tie-Breaking And Ambiguity Resolution

A future methodology-application package should apply deterministic
tie-breaking in this order:

1. Exclude any candidate/segment that violates eligibility.
2. Prioritize candidates/segments with existing committed EXP provenance and no
   need for Path B.
3. Prioritize broader non-performance structural coverage if repo metadata
   supports it.
4. Prioritize cleaner expectation-source symmetry feasibility.
5. Prioritize clearer current REC-count verification.
6. Use deterministic lexical ordering by stable candidate ID only as the final
   tie-breaker.

Lexical ordering is a deterministic fallback, not a ranking of quality.
Performance metrics must not be used. This package does not produce a selected
list.

If repo truth is ambiguous, a future methodology-application package must
either disclose the ambiguity and apply the deterministic rules above or stop
if safe application would require schema, validator, query-layer, artifact,
Path B, EXP scaffold, runtime, protected-path, or authority expansion.

## Methodology Output Shape

If later authorized, a future methodology-application package would produce a
documentation artifact or section containing:

- cohort label / package label;
- selected candidate/candidate-segment units;
- for each member:
  - `candidate_id`;
  - `outcome_kind`;
  - `pipeline_version`;
  - existing EXP provenance reference where required;
  - target `expectation_source_type` values;
  - current REC count per exact segment;
  - current floor status per exact segment;
  - source of eligibility evidence;
  - reason selected under the non-performance methodology;
  - explicit partial-source disclosure if symmetry is not feasible;
- total cohort size;
- implementation package-envelope estimate;
- stop triggers for implementation;
- non-claims and authority boundaries.

This package does not create that output.

## Relationship To WP-10j / WP-10k Pattern

WP-S2c-5 mirrors the earlier non-performance selection discipline used for
single-segment selection and extends it to a bounded cohort.

Like WP-10j candidate-selection rule design, this package designs criteria
first. Like WP-10k candidate-selection eligibility matrix and later
application-style packages, any future application must be separately scoped,
validated, and reported against current repo truth.

This package is methodology only. Methodology application is a future
Main/Karl decision.

## Methodology Application Deferred

This package explicitly defers:

- applying criteria to repo truth;
- listing selected cohort members;
- producing a cohort definition document;
- creating implementation packages;
- producing REP, OL, or REC chains;
- creating consumer briefs;
- opening Path B;
- changing schema, query, or validator surfaces.

A future methodology-application package requires separate authorization at or
after the WP-S2c-5 checkpoint.

## Checkpoint Decision Surface

WP-S2c-5 is the runway endpoint. After WP-S2c-5 merges, Main/Karl must decide
among at least:

1. authorize a cohort methodology-application package;
2. authorize a bounded cohort implementation runway after methodology
   application;
3. authorize optional WP-S2c-6 within-segment consumer brief for
   `exp_success_criteria`;
4. pause A2 cohort work;
5. request more design refinement;
6. redirect to another track;
7. later authorize Path B architecture design only after cohort phase
   completion / checkpoint.

No package follows automatically from WP-S2c-5.

## Explicit Non-Claims

WP-S2c-5 does not:

- select cohort members;
- name candidate IDs as chosen members;
- apply the methodology;
- create a cohort definition;
- authorize cohort implementation;
- create any EXP, REP, OL, REC, LCH, registry, or brief artifact;
- open Path B design beyond deferred-status framing;
- authorize EXP scaffold authoring;
- change schemas, validators, query-layer behavior, implementation, configs,
  dependencies, data, runtime, or protected paths;
- reactivate AUTO;
- authorize H-011 first-time inclusion or H-012+ registration;
- authorize policy, scoring, ranking, recommendation, promotion, readiness, or
  lifecycle authority;
- authorize an automatic next package.
