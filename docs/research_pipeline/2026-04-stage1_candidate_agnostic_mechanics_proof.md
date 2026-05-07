# Stage 1 Candidate-Agnostic Mechanics Proof (WP-10n)

## Purpose

WP-10n is a documentation-only Stage 1 mechanics proof after the WP-10m target-strategy decision and the WP-10l evidence-generation architecture detail.

The package proves only that placeholder mechanics can preserve the Phase 10 boundary from candidate-agnostic eligibility through later possible gates. It does not select any real candidate, select a cohort, create an EXP scaffold, create EXP, REP, OL, or REC artifacts, satisfy REC-5, or authorize later-stage work.

## Locked Inputs

WP-10n consumes these locked inputs:

- WP-10m target-strategy decision: `docs/research_pipeline/2026-04-target_strategy_decision.md`.
- WP-10l evidence-generation architecture detail: `docs/research_pipeline/2026-04-evidence_generation_architecture_detail.md`.
- WP-10j candidate-selection rule design: `docs/research_pipeline/2026-04-candidate_selection_rule_design.md`.
- WP-10k candidate-selection eligibility matrix brief: `research/briefs/2026-04-candidate_selection_eligibility_matrix.md`.
- Current REC, OL, lifecycle, and candidate-registry facts as background context only.

These inputs are descriptive controls. They create no candidate-selection, cohort-selection, evidence-generation, policy, scoring, ranking, recommendation, paper-live, runtime, config, dependency, or protected-path authority.

## Stage 1 Boundary

Stage 1 is candidate-agnostic and documentation-only.

Allowed:

- placeholder worked examples;
- non-instance mechanics surfaces;
- documentation-only decision support;
- read-only validation of existing repo truth.

Forbidden:

- real candidate selection;
- selected cohort;
- EXP scaffold or EXP plan;
- EXP, REP, OL, or REC artifact creation;
- synthetic evidence artifact content;
- policy, scoring, ranking, recommendation, paper-live, runtime, config, dependency, or protected-path behavior.

Stage 1 validates the mechanics boundary only. It does not validate evidence readiness.

## Placeholder Convention

WP-10n uses inline placeholder notation only:

```text
<eligible_segment_X>
<candidate_id_X>
<outcome_kind_X>
<pipeline_version_X>
<expectation_source_type_X>
<future_exp_id_X>
<future_rep_id_X>
<future_ol_id_X>
<future_rec_id_X>
<observation_window_X>
```

Placeholders are not real candidate IDs. They do not imply candidate choice, cohort choice, artifact existence, artifact reservation, execution intent, or future authorization.

## Candidate-Agnostic Mechanics Proof

The Stage 1 proof starts from a placeholder eligibility segment:

```text
<eligible_segment_X>
```

The placeholder segment can be described by the REC-5 dimensions:

```text
<candidate_id_X> / <outcome_kind_X> / <pipeline_version_X> / <expectation_source_type_X>
```

This proves only that the required dimensions can remain explicit without selecting a real candidate. The placeholder segment does not become a target, does not become a cohort member, and does not create a future EXP plan.

The placeholder chain can then describe a later possible artifact path:

```text
<future_exp_id_X> -> <future_rep_id_X> -> <future_ol_id_X> -> <future_rec_id_X>
```

The chain is narrative only. It is not a scaffold, template, reserved ID sequence, or artifact instruction.

## Mechanics Flow

Stage 1 preserves the WP-10l mechanics flow as a non-instance proof:

```text
placeholder eligibility segment
-> placeholder planning boundary
-> placeholder EXP-authoring boundary
-> placeholder future research boundary
-> placeholder REP boundary
-> placeholder OL boundary
-> placeholder REC boundary
-> placeholder validation and descriptive-consumer boundary
```

Every arrow is a boundary description, not an authorization. A later package must receive explicit Main 3.0 authorization before crossing from Stage 1 documentation into real-candidate Stage 2 selection or later evidence work.

## Gate-by-Gate Placeholder Proof

Planning boundary:

- Input: `<eligible_segment_X>`.
- Required identity: `<candidate_id_X> / <outcome_kind_X> / <pipeline_version_X> / <expectation_source_type_X>`.
- Output: a placeholder planning-ready descriptor only.
- Stop if a real candidate or cohort would be selected.

EXP-authoring boundary:

- Input: placeholder planning-ready descriptor.
- Future reference: `<future_exp_id_X>`.
- Output: no current EXP file, no scaffold, no plan.
- Stop if the package would need a real candidate binding or committed EXP shape.

Future research boundary:

- Input: placeholder future EXP reference.
- Window notation: `<observation_window_X>`.
- Output: no run, no metrics, no data mutation.
- Stop if runtime, config, dependency, OMS, risk, safe-mode, execution, or protected paths would be touched.

REP boundary:

- Input: placeholder future result provenance.
- Future reference: `<future_rep_id_X>`.
- Output: no report artifact and no synthetic evidence.
- Stop if reproducibility, source linkage, or non-claim boundaries cannot be preserved.

OL boundary:

- Input: placeholder future EXP/REP chain.
- Future reference: `<future_ol_id_X>`.
- Output: no outcome-ledger artifact.
- Stop if locked rows would be mutated or window provenance would be ambiguous.

REC boundary:

- Input: placeholder future OL plus expectation source.
- Future reference: `<future_rec_id_X>`.
- Output: no reconciliation artifact and no REC-5 satisfaction.
- Stop if source, pipeline, or historical split rows would need combining.

Validation and descriptive-consumer boundary:

- Input: placeholder future validated artifact chain.
- Output: no consumer, stability lock, or authority change in WP-10n.
- Stop if validation fails, integrity rows appear, changed-file scope expands, or forbidden authority language appears.

## REC-5 Accounting Preservation

REC-5 remains:

```text
n >= 3 per candidate_id / outcome_kind / pipeline_version / expectation_source_type
```

Stage 1 does not count toward REC-5 because it creates no real REC artifact and no evidence observation.

Selection, eligibility, placeholder planning, and narrative future IDs do not count as evidence. A future REC append can increment only the exact segment represented by:

```text
<candidate_id_X> / <outcome_kind_X> / <pipeline_version_X> / <expectation_source_type_X>
```

Expectation sources do not combine. Pipeline versions do not combine. Historical split rows do not combine.

## Historical Split / Pipeline-Version / Expectation-Source Separation

Current repo truth includes a locked historical split that must remain structural background only in WP-10n.

Stage 1 proves that a placeholder future package must keep these dimensions separate:

- `<pipeline_version_X>` remains part of the segment identity.
- `<expectation_source_type_X>` remains part of the segment identity.
- historical split rows remain separate when a future real package names an applicable candidate and source.

WP-10n does not choose either side of any historical split, compare split rows, infer improvement or degradation, or authorize special-case handling.

## What Stage 1 Validates

Stage 1 validates only that:

- placeholder mechanics can represent the required REC-5 dimensions;
- a future path can be described without real candidate IDs;
- Stage 2 selection remains behind an explicit Main 3.0 authorization boundary;
- future EXP work remains behind a later explicit authorization boundary;
- REC-5 source, pipeline-version, and historical-split separation can be preserved in documentation.

## What Stage 1 Does Not Validate

Stage 1 does not validate:

- evidence readiness;
- candidate readiness;
- cohort readiness;
- future EXP sufficiency;
- future observation-window sufficiency;
- artifact schema sufficiency beyond current locked repo truth;
- REC-5 satisfaction;
- policy, scoring, ranking, recommendation, paper-live, runtime, config, dependency, or protected-path readiness.

## Future Stage 2 Handoff Boundary

Future Stage 2 real-candidate selection requires explicit Main 3.0 authorization.

A Stage 2 package may not treat this document as automatic selection authority. It must independently prove its allowed scope, real changed-file set, validation path, and forbidden-scope preservation.

Future EXP work remains forbidden unless explicitly authorized after the needed prior decision boundary. If a later package cannot preserve candidate selection, EXP authorization, REC-5 accounting, and protected-path boundaries, it must stop.

## Stop Conditions for Later Packages

Later packages must stop if they require:

- selecting a real candidate or cohort without explicit Main 3.0 authorization;
- creating an EXP scaffold before explicit authorization;
- creating EXP, REP, OL, REC, lifecycle, or registry artifacts outside scope;
- mutating locked retrospective artifacts;
- combining expectation sources, pipeline versions, or historical split rows for REC-5;
- schema, validator, query-layer, test, runtime, config, dependency, or protected-path changes outside scope;
- non-empty integrity views;
- failed validators or tests;
- policy, scoring, ranking, recommendation, paper-live, runtime, or protected-path authority.

## Validation Snapshot

WP-10n validation is expected to cover:

- REC validator;
- OL validator;
- lifecycle validator;
- candidate registry validator;
- EXP/REP artifact validator where available;
- all discovered integrity views, expected `[]`;
- targeted registry, research-query, reconciliation, outcome-ledger, and lifecycle tests;
- full pytest;
- forbidden-scope scans;
- `git diff --check`;
- changed-file inspection.

The expected changed-file set is exactly:

```text
docs/project_status.md
docs/research_pipeline/2026-04-stage1_candidate_agnostic_mechanics_proof.md
```

## Non-Claims

WP-10n creates no:

- real candidate selection;
- selected cohort;
- EXP scaffold;
- EXP, REP, OL, or REC artifact;
- synthetic evidence artifact;
- REC-5 satisfaction;
- schema change;
- validator change;
- query-layer change;
- test change;
- policy;
- scoring;
- ranking or recommendation;
- paper-live semantics;
- runtime, deployment, OMS, risk, safe-mode, or execution authority;
- config or dependency change;
- protected-path authority.
