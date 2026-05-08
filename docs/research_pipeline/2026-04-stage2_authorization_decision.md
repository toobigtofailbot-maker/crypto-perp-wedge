# Stage 2 Authorization Decision (WP-10p)

## Purpose

WP-10p is a documentation-only Stage 2 authorization decision after the WP-10o
Stage 1 checkpoint lock. It authorizes Stage 2 to proceed only under a
conservative first-sub-stage shape and locks the decision framework for the
first implementation packages.

WP-10p does not implement Stage 2. It does not select a real candidate or
segment, define a cohort, create an EXP scaffold, create EXP, REP, OL, REC,
LCH, or registry artifacts, or change schemas, validators, query-layer
behavior, tests, runtime, configs, dependencies, data, or protected paths.

## Locked inputs

WP-10p consumes these locked inputs:

- WP-10o Stage 1 checkpoint lock:
  `docs/research_pipeline/2026-04-stage1_checkpoint_lock.md`.
- WP-10n Stage 1 candidate-agnostic mechanics proof:
  `docs/research_pipeline/2026-04-stage1_candidate_agnostic_mechanics_proof.md`.
- WP-10m target-strategy decision:
  `docs/research_pipeline/2026-04-target_strategy_decision.md`.
- WP-10l evidence-generation architecture detail:
  `docs/research_pipeline/2026-04-evidence_generation_architecture_detail.md`.
- WP-10h forward-flow evidence plan:
  `docs/research_pipeline/2026-04-forward_flow_evidence_plan.md`.
- WP-10i Phase 10 architecture plan:
  `docs/research_pipeline/2026-04-phase10_architecture_plan.md`.
- WP-10j candidate-selection rule design:
  `docs/research_pipeline/2026-04-candidate_selection_rule_design.md`.
- WP-10k candidate-selection eligibility matrix:
  `research/briefs/2026-04-candidate_selection_eligibility_matrix.md`.
- Current REC, OL, lifecycle, candidate-registry, EXP/REP, and project-status
  repo truth.

These inputs are authorization inputs only. They create no implementation,
candidate-selection result, cohort, EXP scaffold, evidence artifact, policy,
scoring, ranking, recommendation, paper-live, runtime, config, dependency, or
protected-path authority.

## Stage 2 authorization statement

Stage 2 proceeds under conservative first-sub-stage authorization.

This is an authorization decision only. The first implementation package after
WP-10p must independently pass its own changed-file scope, validation, and
protected-boundary checks before any later package can rely on it.

## Stage 2 non-implementation boundary

WP-10p does not cross from authorization into implementation. It authorizes a
bounded sequence of future package classes, but it creates no package drafts
for WP-10q, WP-10r, WP-10s, or WP-10t.

WP-10p creates no current evidence, no current artifact, no current selected
segment, no current selected cohort, and no current EXP scaffold.

## Stage 2 path-label definitions

WP-10p defines these labels in WP-10p scope:

- Path A: new REP against an existing committed EXP for a selected eligible
  segment, followed later by OL and REC append packages. No new EXP.
- Path B: new EXP variant for a selected eligible segment. Not authorized in
  the Stage 2 first sub-stage.
- Path C: new candidate / no-current-target evidence generation. Deferred.
- Path D: synthetic or fixture-only evidence. Excluded from the Stage 2 first
  sub-stage and not allowed for REC-5 satisfaction.
- Path E: paper-trading evidence path. Forbidden.
- Path F: live-trading evidence path. Forbidden.

Repo truth note: WP-10h uses a staged forward-flow sequence, not literal Path
A/B/C/D/E/F labels. WP-10o explicitly records that current repo truth does not
define literal `Path A`, `Path B`, or `Path C` labels in the WP-10h
forward-flow evidence plan.

WP-10p maps Path A to WP-10h's broader future evidence sequence:

```text
valid EXP/REP provenance -> OL append -> REC append -> descriptive validation/consumer posture
```

Stage 2 first sub-stage authorizes Path A only.

## S2-1 - Stage 2 proceeds

Stage 2 proceeds under conservative first-sub-stage authorization.

This decision does not implement Stage 2. Future Stage 2 packages still must
prove exact scope, validator coverage, integrity-view health, changed-file
limits, semantic non-claim discipline, and protected-boundary preservation.

## S2-2 - Identifier posture

WP-10p defines selection methodology using placeholder and abstract segment
language only.

WP-10p does not choose a real candidate or segment. WP-10q must apply the
methodology to the real eligibility matrix and commit exactly one chosen real
eligible segment.

The chosen unit for WP-10q is the exact REC-5 segment:

```text
candidate_id / outcome_kind / pipeline_version / expectation_source_type
```

## S2-3 - First-sub-stage shape

The first Stage 2 sub-stage is single-segment only.

Small cohort selection is not authorized by WP-10p. A small cohort may be
considered only after the first single-segment sub-stage completes and is
checkpointed or explicitly reviewed.

## S2-4 - H-011 disposition

Current repo truth records H-011 as registry-present, draft/reserved, and with
no current OL/REC target segment.

H-011 remains registry-present with no current OL/REC target segment. H-011 is
excluded from the Stage 2 first sub-stage.

WP-10p does not demote H-011, select another candidate by comparison, or
change H-011 registry status. H-011 inclusion requires a future separately
authorized new-candidate / no-current-target evidence-generation decision.

## S2-5 - Target-selection methodology

WP-10p commits methodology only. WP-10q commits the selection result.

The selection unit is the exact REC-5 segment:

```text
candidate_id / outcome_kind / pipeline_version / expectation_source_type
```

Selection criteria must be non-performance-based.

Forbidden as selection criteria:

- realized metric strength;
- realized metric weakness;
- REC verdict favorability;
- candidate quality ranking;
- policy readiness;
- paper-live readiness;
- subjective preference.

Allowed selection criteria may include:

- lowest infrastructural risk;
- clearest existing EXP/REP/OL/REC provenance;
- least ambiguity in pipeline version;
- clean expectation-source mapping;
- clean observation-window feasibility;
- direct applicability to Path A;
- deterministic tie-breaking.

Tie-breaking must be deterministic and non-performance-based. The default
tie-breaker is the lowest eligible segment key by stable lexical order, after
all hard methodology gates are satisfied.

## S2-6 - Evidence path

Stage 2 first sub-stage authorizes Path A only.

Path A creates one future REP against an existing committed EXP for the chosen
eligible segment. Later separately scoped packages may append one OL entry and
one or two REC entries derived from that OL entry. Path A creates no new EXP.

Path B is not authorized in the Stage 2 first sub-stage. Path B and any first
EXP scaffold work require a future Stage 2 second-sub-stage authorization
decision.

Path C is deferred. Path D is excluded and cannot satisfy REC-5. Path E and
Path F remain forbidden.

## S2-7 - Resource envelope

The Stage 2 first-sub-stage envelope is:

- 1 selected exact segment;
- 0 new EXPs;
- 1 new REP against an existing committed EXP;
- 1 new OL entry derived from that REP;
- 1 or 2 new REC entries derived from that OL entry, depending on applicable
  expectation sources;
- 1 new evaluation window for the REP, distinct from existing OL evaluation
  windows for the same exact segment;
- no small cohort;
- no new candidate;
- no EXP scaffold.

Observation-window definition is not finalized in WP-10p. The first future
package that creates a REP must define the exact evaluation window and stop if
it cannot do so without ambiguity or retrospective cloning.

## S2-8 - Expectation-source posture

Use both `exp_success_criteria` and `d2_006_gates` where applicable.

Expectation sources remain separate. Sources do not combine for REC-5, and
outputs do not aggregate across sources into scoring, ranking,
recommendation, policy, or paper/live readiness.

If only one expectation source applies for the chosen exact segment, the
package must record why and stop if repo truth is ambiguous.

## S2-9 - Pipeline-version handling

Pipeline version disclosure is mandatory for every future Stage 2 artifact.

H-004 pre/post split remains structural only. There is no pipeline-version
combining and no pre/post comparison claim.

New REPs should use current post-WP-5b pipeline semantics unless repo truth
identifies a different current pipeline-version label. Existing pre-WP-5b
artifacts remain historical and unchanged.

Stage 2 first sub-stage targets current forward-flow semantics and does not
create new pre-WP-5b evidence.

## S2-10 - Validation discipline

First Stage 2 packages must preserve existing Phase 9 / Phase 10 validation
discipline.

For WP-10q selection methodology application:

- changed-file scope check;
- candidate, eligibility, REC, OL, and lifecycle validators;
- all discovered integrity views;
- targeted pytest;
- full pytest where appropriate;
- forbidden-scope scan;
- no artifact creation;
- no performance-based selection scan;
- deterministic methodology application evidence.

For later REP, OL, and REC artifact packages:

- applicable artifact schema validator;
- applicable registry validators;
- central query-layer visibility where relevant;
- all discovered `v_integrity_*` views;
- REC-5 segment delta checks when REC is touched;
- H-004, pipeline-version, and expectation-source separation checks;
- non-positive-gross-PnL cost-drag handling checks when D2 source applies;
- targeted pytest;
- full pytest where appropriate;
- `git diff --check`;
- changed-file inspection;
- protected-boundary preservation checks.

Validation must be reported as normal pass/fail results with warning counts
where present.

## S2-11 - Forbidden scopes under Stage 2

The following remain blocked even under Stage 2 authorization:

- promotion / demotion policy implementation or schema;
- ranking / recommendation implementation or schema;
- evidence-quality scoring implementation or schema;
- paper extension implementation or schema;
- live extension implementation or schema;
- operationally consequential lifecycle transitions;
- runtime, OMS, risk, safe-mode, execution, deployment, configs,
  dependencies, protected-path implementation;
- `lib/`, `src/`, and `configs/` changes;
- `docs/architecture/LONG_TERM_SCOPE.md`,
  `docs/onboarding/PHASE2_BASELINE.md`, `.claude/`, `data/`, and
  `docs/data_catalog.md` changes;
- existing committed schema mutation;
- existing committed instance mutation;
- cross-segment inference under the REC-5 floor;
- performance-based candidate selection;
- synthetic content for REC-5 satisfaction;
- new candidate registration such as H-012 or beyond.

## S2-12 - EXP scaffold blocking

EXP scaffolds remain blocked through the entire Stage 2 first sub-stage.

WP-10p does not authorize EXP scaffold drafting. WP-10q must not create an EXP
scaffold. WP-10r, under the default Path A sequence, creates a new REP against
an existing EXP, not an EXP scaffold.

Path B and first EXP scaffold work require a future Stage 2 second-sub-stage
authorization decision after the first sub-stage closes.

## Immediate post-WP-10p sequence

Default sequence after WP-10p:

1. WP-10q: candidate-selection methodology application.
   Documentation-only. Applies WP-10p methodology to the eligibility matrix
   and commits one chosen real exact segment. No EXP scaffold. No REP, OL, or
   REC creation.
2. WP-10r: first new REP against existing EXP for the chosen segment.
   Artifact package. Path A. No new EXP. Must define evaluation window. No OL
   or REC append in the same package unless Main 3.0 later explicitly changes
   scope.
3. WP-10s: first new OL entry from WP-10r REP.
   Artifact append package. No REC append unless explicitly scoped later.
4. WP-10t: first new REC entries from WP-10s OL entry.
   One or two REC entries depending on applicable expectation sources. No
   source or pipeline combining.
5. Stage 2 first-sub-stage checkpoint / stability lock.
   Documentation-only closure after WP-10t or equivalent first-sub-stage
   completion.

WP-10p does not draft WP-10q, WP-10r, WP-10s, or WP-10t.

## Stage 2 first-sub-stage closure rule

The Stage 2 first sub-stage closes only after the authorized single-segment
sequence completes or is explicitly reviewed and checkpointed.

Closure requires validated package evidence for the selected segment and a
documentation-only checkpoint that records what was created, what remains
below or at REC-5, whether Path A stayed within scope, and whether a later
Stage 2 second-sub-stage decision may consider Path B or a small cohort.

## Validation snapshot

WP-10p validation is expected to cover:

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
docs/research_pipeline/2026-04-stage2_authorization_decision.md
```

## Non-claims

WP-10p creates no:

- Stage 2 implementation;
- candidate selection;
- selected cohort;
- EXP scaffold or EXP plan;
- EXP, REP, OL, REC, LCH, or registry artifact;
- synthetic evidence artifact;
- REC-5 satisfaction;
- schema change;
- validator change;
- query-layer change;
- test change;
- runtime, deployment, OMS, risk, safe-mode, or execution authority;
- config, dependency, data, or protected-path change;
- policy;
- scoring;
- ranking or recommendation;
- paper-live semantics.
