# Stage 1 Checkpoint Lock (WP-10o)

## Purpose

WP-10o is a documentation-only checkpoint lock after the completed Stage 1 work-set for the Phase 10 staged-cohort strategy. It declares Stage 1 complete-as-built through WP-10l, WP-10m, and WP-10n, and records the decisions that must be made before any Stage 2 drafting begins.

WP-10o does not authorize Stage 2, draft Stage 2, select real candidates, define a cohort, create EXP scaffolds, create EXP, REP, OL, REC, lifecycle, or registry artifacts, or change schemas, validators, query-layer behavior, tests, runtime, configs, dependencies, data, or protected paths.

## Locked inputs

- WP-10l evidence-generation architecture detail: `docs/research_pipeline/2026-04-evidence_generation_architecture_detail.md`.
- WP-10m target-strategy decision: `docs/research_pipeline/2026-04-target_strategy_decision.md`.
- WP-10n Stage 1 candidate-agnostic mechanics proof: `docs/research_pipeline/2026-04-stage1_candidate_agnostic_mechanics_proof.md`.
- WP-10k candidate-selection eligibility matrix brief: `research/briefs/2026-04-candidate_selection_eligibility_matrix.md`.
- WP-10h forward-flow evidence plan: `docs/research_pipeline/2026-04-forward_flow_evidence_plan.md`.
- WP-10i Phase 10 architecture plan: `docs/research_pipeline/2026-04-phase10_architecture_plan.md`.
- WP-10j candidate-selection rule design: `docs/research_pipeline/2026-04-candidate_selection_rule_design.md`.
- Current REC, OL, lifecycle, candidate-registry, and project-status repo truth.

These inputs are descriptive controls only. They create no Stage 2, candidate-selection, cohort-selection, EXP-scaffold, evidence-generation, policy, scoring, ranking, recommendation, paper-live, runtime, or protected-path authority.

## Stage 1 completed work-set

Stage 1 is complete-as-built through this work-set:

- WP-10l defines candidate-agnostic evidence-generation application mechanics from an eligible segment through planning, EXP authoring, future research, REP, OL, REC, validation, and descriptive consumer/stability boundaries using placeholder worked-example notation only.
- WP-10m locks the Phase 10 target strategy as staged cohort with a candidate-agnostic first stage.
- WP-10n proves the Stage 1 candidate-agnostic mechanics boundary with placeholders only and no later-stage authorization.

## Stage 1 completion summary

Stage 1 is documentation-only and descriptive. It selected no real candidates, selected no cohort, created no EXP scaffold or EXP plan, created no EXP/REP/OL/REC artifacts, created no lifecycle or registry artifacts, and created no synthetic evidence artifacts.

Stage 1 changed no schemas, validators, query-layer behavior, tests, runtime, configs, dependencies, data, protected paths, policy, scoring, ranking, recommendation, paper-live semantics, or runtime authority.

## Stage 1 constraint posture

Stage 1 validates only that the candidate-agnostic mechanics boundary can be described without crossing into real target selection or artifact creation. It does not validate evidence readiness, candidate readiness, cohort readiness, EXP sufficiency, observation-window sufficiency, policy readiness, paper-live readiness, or runtime readiness.

Future packages must keep eligibility, selection, evidence generation, artifact append, validation, and descriptive consumer work separated unless Main 3.0 explicitly authorizes a narrower package crossing one of those boundaries.

## REC-5 floor status

REC-5 remains:

```text
n >= 3 per candidate_id / outcome_kind / pipeline_version / expectation_source_type
```

Current repo truth records 22 REC rows, `REC-0001` through `REC-0022`, with 11 `exp_success_criteria` rows and 11 `d2_006_gates` rows. Every current exact `candidate_id / outcome_kind / pipeline_version / expectation_source_type` segment has `reconciliation_count = 1`, below the floor.

Stage 1 did not satisfy REC-5. Sources do not combine. Pipeline versions do not combine. H-004 pre/post or other historical split rows do not combine. Eligibility, placeholder planning, EXP scaffolds, EXP plans, REP artifacts without REC append, and descriptive consumers do not count as REC-5 satisfaction.

## Cost-drag non-positive-gross-PnL verification posture

Current repo truth confirms that `REC-0012`, `REC-0017`, and `REC-0019` preserve the extracted D2-006 cost-drag expectation while excluding deterministic cost-drag pass/fail comparison when the referenced OL metrics have `gross_pnl <= 0`. The current docs record no open D2 non-positive-gross-PnL cost-drag anomaly after the WP-10g correction.

WP-10o records only that Stage 1 inherits this cleaned descriptive posture. No policy, scoring, ranking, recommendation, evidence-quality inference, paper-live readiness, or runtime implication follows from the correction.

## H-004 split / pipeline-version / expectation-source separation

H-004 remains structurally split in current REC and OL repo truth. The current REC split is:

```text
REC-0005 / OL-0005 / H-004 / pre_wp_5b / exp_success_criteria
REC-0011 / OL-0011 / H-004 / post_wp_5b / exp_success_criteria
REC-0016 / OL-0005 / H-004 / pre_wp_5b / d2_006_gates
REC-0022 / OL-0011 / H-004 / post_wp_5b / d2_006_gates
```

The split is structural only. WP-10o makes no pre/post comparison, improvement claim, degradation claim, special-case handling decision, candidate preference, policy claim, paper-live claim, or runtime claim.

## H-011 / registry-present no-current-target posture

Current candidate-registry overview exposes `H-001` through `H-011`. H-011 is registry-present as a reserved/draft candidate with no current OL/REC target segment.

The WP-10k eligibility matrix marks H-011 `not_applicable` with `no_current_ol_rec_target_segment`. This does not demote H-011, select another candidate, define a cohort, or authorize any future evidence package.

## Eligibility matrix coverage posture

WP-10k remains descriptive only. It marks current OL/REC target segments for H-001 through H-010 as `eligible_for_future_evidence_planning`, and preserves the exact REC-5 dimensions:

```text
candidate_id / outcome_kind / pipeline_version / expectation_source_type
```

Eligibility is not selection. Eligibility does not rank, score, recommend, promote, demote, define a cohort, satisfy REC-5, or authorize EXP, REP, OL, REC, lifecycle, registry, policy, paper-live, or runtime work.

## Stage 1 checkpoint lock statement

Stage 1 is locked complete-as-built through WP-10l, WP-10m, and WP-10n.

The lock means the candidate-agnostic mechanics stage is complete and can be used as background for a later Main 3.0 direction-setting decision. The lock does not move the repo into Stage 2, does not authorize Stage 2 drafting, and does not authorize real-candidate selection, cohort definition, or EXP scaffold creation.

## Stage 1 -> Stage 2 transition prerequisites

A later Main 3.0 capsule must explicitly decide these items before any Stage 2 drafting begins:

- Whether Stage 2 proceeds at all.
- Whether Stage 2 follows the WP-10h forward-flow sequence directly, uses another Main 3.0 path framing, or maps to the WP-10i Candidate A/B/C package-candidate language. Current repo truth does not define literal `Path A`, `Path B`, or `Path C` labels in the forward-flow evidence plan.
- Whether Stage 2 starts with a single segment, a small cohort, or one more worked-example-only iteration.
- Whether Stage 2 uses real candidate identifiers or continues placeholders for one more authorized iteration.
- The Stage 2 resource envelope, including number of EXPs, number of REPs, and observation-window scope.
- The expectation-source posture for Stage 2.
- Pipeline-version handling, including H-004 or other split handling if applicable.
- The target-selection prerequisite before any EXP scaffold.
- The validation discipline for the first Stage 2 deliverable.
- The forbidden scope that remains blocked even after Stage 2 authorization.

Listing these prerequisites does not satisfy them.

## Future WP-10p boundary

WP-10p may become a future Main 3.0 direction-setting package after WP-10o merges. WP-10o does not draft WP-10p, reserve WP-10p content, authorize WP-10p, or decide whether WP-10p is the next package.

## Stability / additive-evolution rule

Future packages must preserve Stage 1 as a completed documentation-only checkpoint. They may add later authorized decisions or evidence packages, but they must not rewrite Stage 1 into an implicit Stage 2 authorization or use Stage 1 placeholders as real candidate, cohort, EXP, REP, OL, REC, lifecycle, or registry instructions.

## Stop conditions for later packages

Later packages must stop if they require:

- selecting a real candidate or cohort without explicit Main 3.0 authorization;
- creating an EXP scaffold before explicit authorization;
- creating EXP, REP, OL, REC, lifecycle, or registry artifacts outside authorized scope;
- mutating locked retrospective artifacts;
- combining expectation sources, pipeline versions, or historical split rows for REC-5;
- schema, validator, query-layer, test, runtime, config, dependency, data, or protected-path changes outside authorized scope;
- policy, scoring, ranking, recommendation, paper-live, runtime, or protected-path authority;
- non-empty integrity views;
- failed validators or tests;
- changed-file scope expansion beyond the active package.

## Validation snapshot

WP-10o validation is expected to cover:

- all available `tools.registry.validate_*` validators;
- all discovered `v_integrity_*` views, expected `[]`;
- targeted registry, research-query, reconciliation, outcome-ledger, and lifecycle tests;
- full pytest;
- semantic scans for forbidden authority language;
- `git diff --check`;
- changed-file inspection.

The expected changed-file set is exactly:

```text
docs/project_status.md
docs/research_pipeline/2026-04-stage1_checkpoint_lock.md
```

## Non-claims

WP-10o creates no:

- Stage 2 authorization;
- Stage 2 draft;
- real candidate selection;
- selected cohort;
- EXP scaffold or EXP plan;
- EXP, REP, OL, or REC artifact;
- lifecycle or registry artifact;
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
