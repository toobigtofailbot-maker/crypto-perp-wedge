# Phase 10 Architecture Plan (WP-10i)

## Purpose

WP-10i is a documentation-only architecture plan after the WP-10h
forward-flow evidence plan. It translates the forward-flow evidence plan into
a Phase 10 package architecture.

WP-10i does not implement Phase 10, generate evidence, create experiments,
create EXP, REP, OL, or REC artifacts, implement policy, score evidence
quality, rank or recommend candidates, create paper/live semantics, or touch
runtime, deployment, OMS, risk, safe-mode, execution, configs, dependencies,
or protected paths.

## Locked Inputs

WP-10i consumes these locked descriptive inputs:

- WP-10g `REC-0012` correction.
- WP-10h forward-flow evidence plan.
- WP-10f Phase 9 -> Phase 10 transition decision.
- WP-10e REC-5 floor-gap stability lock.
- WP-10d REC cross-expectation-source consumer.
- REC v1 stability lock.
- Outcome-ledger v1 stability lock.
- Lifecycle stability lock.

These inputs are architecture inputs only. They create no implementation,
promotion, demotion, ranking, recommendation, policy, paper/live,
evidence-scoring, runtime, or protected-path authority.

## Current Machine State

Current repo truth records:

- REC corpus: 22 rows, `REC-0001` through `REC-0022`.
- REC expectation-source distribution: 11 `exp_success_criteria` rows and 11
  `d2_006_gates` rows.
- REC-5 state: every current `candidate_id / outcome_kind / pipeline_version /
  expectation_source_type` segment has `reconciliation_count = 1`, below the
  `n >= 3` floor.
- Outcome ledger: 11 rows, `OL-0001` through `OL-0011`.
- Lifecycle changes: 30 rows, with transition counts 10 / 10 / 10 for
  `proposed -> in_research`, `in_research -> research_concluded`, and
  `research_concluded -> archived`.
- H-004 remains structurally split under both expectation sources.
- `REC-0012` correction is complete.
- No open D2 non-positive-gross-PnL cost-drag anomaly remains.

The H-004 REC split is:

```text
REC-0005 / OL-0005 / H-004 / pre_wp_5b / exp_success_criteria
REC-0011 / OL-0011 / H-004 / post_wp_5b / exp_success_criteria
REC-0016 / OL-0005 / H-004 / pre_wp_5b / d2_006_gates
REC-0022 / OL-0011 / H-004 / post_wp_5b / d2_006_gates
```

`REC-0012`, `REC-0017`, and `REC-0019` preserve the extracted D2-006
cost-drag gate and skip deterministic cost-drag pass/fail comparison when
`gross_pnl <= 0`.

## Phase 10 Architecture Goal

Phase 10 initially starts as an evidence-generation architecture tranche. The
goal is to create a safe, validator-backed path from future evidence to:

```text
EXP plan -> REP report/artifact -> OL append -> REC append -> descriptive consumer/stability update
```

Phase 10 does not start with policy, ranking, paper/live, scoring, or runtime.
Current descriptive-only surfaces must remain descriptive until sufficient
evidence exists and Main 3.0 separately authorizes downstream package classes.

## Phase 10 Package Classes

### Class A - Documentation-Only Architecture Packages

Allowed now.

Purpose:

- refine sequence, gates, and candidate-selection criteria;
- define evidence-generation design;
- clarify data and evaluation-window requirements;
- plan validator expectations.

Forbidden:

- no artifacts;
- no policy;
- no runtime;
- no candidate recommendation.

### Class B - Candidate-Selection Rule Design Packages

Allowed after WP-10i if documentation-only.

Purpose:

- define rules for selecting future evidence candidates;
- specify criteria, not execution;
- propose cohorts only as future planning candidates when explicitly
  non-authoritative.

Forbidden:

- no ranking implementation;
- no recommendations;
- no promotion or demotion;
- no experiment execution.

### Class C - Future EXP Planning Packages

Allowed after candidate-selection rules and architecture approval.

Purpose:

- create future experiment plans with success criteria and data requirements;
- specify D2-006 linkage if used.

Forbidden:

- no execution results;
- no REP artifacts;
- no OL or REC artifacts;
- no policy.

### Class D - Future REP Artifact Packages

Allowed only after real future evidence exists.

Purpose:

- record future evidence metrics and provenance.

Forbidden:

- no synthetic evidence;
- no retrospective clone evidence;
- no policy, ranking, scoring, or runtime.

### Class E - OL Append Packages

Allowed only from valid future REP/EXP evidence.

Purpose:

- append new outcome-ledger rows.

Forbidden:

- no mutation of locked OL v1 rows;
- no policy authority;
- no direct REC count manipulation.

### Class F - REC Append Packages

Allowed only from valid future OL rows and one expectation source.

Purpose:

- append new REC rows;
- move valid segments toward REC-5.

Forbidden:

- no combining expectation sources;
- no combining pipeline versions;
- no combining H-004 split rows;
- no retrospective duplicate splitting.

### Class G - Descriptive Consumer/Stability Packages

Allowed after new artifacts are validator-clean.

Purpose:

- update descriptive visibility and locks.

Forbidden:

- no policy, ranking, scoring, paper/live, or runtime authority.

### Class H - Policy/Ranking/Scoring/Paper-Live/Runtime Packages

Blocked.

This class may be considered only after:

- sufficient evidence exists under REC-5 or a later explicit evidence-floor
  decision;
- Main 3.0 explicitly authorizes that package class;
- protected runtime boundaries are separately reviewed.

## Required Phase 10 Gates

### Gate 1 - Evidence-Design Gate

Must decide:

- candidate-selection rule criteria;
- expectation-source priority;
- pipeline-version handling;
- H-004 handling;
- evaluation-window convention;
- data source and data version requirements;
- success/failure artifact rules.

### Gate 2 - Experiment-Plan Gate

Requires:

- valid future EXP plan;
- success criteria;
- D2-006 linkage if applicable;
- data requirements;
- no execution results.

### Gate 3 - Evidence-Realization Gate

Requires:

- actual future evidence;
- reproducible metric generation;
- clear evaluation window;
- cost, slippage, and funding assumptions;
- REP artifact validation.

### Gate 4 - OL Append Gate

Requires:

- valid REP/EXP source;
- outcome-ledger helper or methodology if applicable;
- validator-clean OL artifact;
- no mutation of locked OL v1 rows.

### Gate 5 - REC Append Gate

Requires:

- valid OL source;
- expectation source;
- validator-clean REC artifact;
- correct segment accounting.

### Gate 6 - REC-5 Review Gate

Requires:

- segment counts inspected per `candidate_id / outcome_kind /
  pipeline_version / expectation_source_type`;
- no forbidden dimension combining;
- integrity views empty;
- consumers updated descriptively only.

### Gate 7 - Policy Eligibility Gate

Blocked until future Main 3.0 authorization.

Minimum future prerequisites:

- REC-5 satisfied for the relevant segment or a separately approved
  evidence-floor revision;
- candidate-selection/ranking semantics explicitly designed;
- risk, paper/live, and runtime boundaries separately reviewed;
- no unresolved integrity issues;
- no protected-path drift.

## Candidate-Selection Architecture

WP-10i does not choose candidates.

A later candidate-selection rule design package may define criteria. Criteria
may include artifact completeness, REC/OL coverage, lifecycle state,
strategy-family representation, data availability, and feasibility.

Criteria must not become rankings or recommendations without later
authorization. H-004 cannot be treated as improved or degraded from the
current pre/post split alone.

## Expectation-Source Architecture

`exp_success_criteria` and `d2_006_gates` remain independent source types.
Phase 10 may choose to generate future evidence for one or both source types,
but WP-10i does not select priority. Counts do not combine across source
types.

Any new expectation-source type requires a schema and architecture decision
before implementation.

## Pipeline-Version And H-004 Architecture

Pipeline versions remain separate REC-5 dimensions. H-004 pre/post remains
structural. Future H-004 evidence must specify pipeline version.

No pre/post performance comparison is supported without explicit future design
and sufficient evidence.

## Artifact Evolution Rules

Future evidence artifacts are append-only by default. Corrections require
explicit correction packages.

Locked REC/OL v1 rows are not mutated except through explicit correction
packages. Future EXP, REP, OL, and REC artifacts must be validator-clean.

Synthetic evidence is forbidden. Cloning or splitting retrospective artifacts
to satisfy REC-5 is forbidden.

## Validation And Preservation Rules

Future packages must run:

- relevant registry validators;
- REC validator when REC is touched;
- OL validator when OL is touched;
- EXP/REP validators when EXP/REP are touched;
- all discovered `v_integrity_*` views;
- lifecycle, OL, and REC regressions;
- targeted pytest;
- full pytest where appropriate;
- `git diff --check`;
- changed-file set inspection;
- protected-path preservation check.

## Forbidden Scope Register

Forbidden until later Main 3.0 authorization:

- promotion/demotion policy;
- candidate ranking/recommendation;
- evidence-quality scoring;
- paper/live readiness;
- execution/routing;
- OMS;
- risk limits;
- safe mode;
- deployment;
- runtime config;
- dependency changes for execution;
- protected-path changes.

## Recommended Immediate Next Package Candidates

These are package candidates only. WP-10i does not select implementation.

### Candidate A - WP-10j Candidate-Selection Rule Design

Documentation-only.

Purpose:

- define criteria for which candidates should receive forward-flow evidence
  first.

Risk:

- can drift into ranking/recommendation.

### Candidate B - WP-10j Evidence-Generation Architecture Detail

Documentation-only.

Purpose:

- refine data/window requirements, artifact templates, and stage gates.

Risk:

- can drift into experiment creation.

### Candidate C - WP-10j Future EXP Planning Scaffold

Only if Main 3.0 authorizes moving beyond architecture.

Purpose:

- create one or more future EXP plan templates or plans.

Risk:

- may create execution pressure before candidate-selection rules.

Recommended default:

- choose Candidate A or B before any EXP planning;
- do not choose policy, scoring, ranking, paper/live, or runtime.

## Main 3.0 Decision Required After WP-10i

Ask Main 3.0 to decide:

1. Should the next package be candidate-selection rule design or
   evidence-generation architecture detail?
2. May any future EXP planning package proceed before candidate-selection
   rules?
3. Should Phase 10 track one candidate, a small cohort, or remain
   candidate-agnostic until a rules package?
4. Which expectation source should be prioritized, if any?
5. Are all downstream outputs still descriptive-only until REC-5 is satisfied?
6. Which package classes remain forbidden?

## Supported Uses

WP-10i supports:

- Phase 10 architecture planning;
- package sequence design;
- gate definition;
- future evidence planning;
- candidate-selection rules planning;
- preserving REC-5 boundaries;
- preventing policy/runtime drift.

## Unsupported Claims

WP-10i does not support claims of:

- REC-5 satisfaction;
- new evidence creation;
- candidate selection;
- ranking/recommendation;
- promotion/demotion;
- policy readiness;
- paper/live readiness;
- evidence-quality scoring;
- strategy-family performance conclusion;
- pipeline-version performance comparison;
- cross-window inference;
- runtime/deployment/OMS/risk/safe-mode/execution authority;
- protected-path authority.

## Validation Snapshot

WP-10i validation records:

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

WP-10i creates no:

- Phase 10 implementation;
- new EXP, REP, OL, or REC artifacts;
- REC-5 satisfaction;
- candidate selection;
- policy;
- promotion or demotion;
- ranking or recommendation;
- paper/live semantics;
- evidence-quality scoring;
- schema;
- validator;
- query-layer view;
- runtime, deployment, OMS, risk, safe-mode, or execution authority;
- protected-path authority.
