# Target-Strategy Decision (WP-10m)

## 10.1 Purpose

WP-10m is a documentation-only target-strategy decision package after the WP-10l evidence-generation architecture detail. It decides the target-strategy shape for future Phase 10 evidence generation.

WP-10m does not name selected candidates, select a real cohort, create EXP scaffolds or plans, create EXP, REP, OL, or REC artifacts, satisfy REC-5, or implement policy, scoring, ranking, recommendation, paper-live, runtime, deployment, OMS, risk, safe-mode, execution, config, dependency, or protected-path behavior.

## 10.2 Locked Inputs

WP-10m consumes these locked descriptive inputs:

- WP-10l evidence-generation architecture detail: `docs/research_pipeline/2026-04-evidence_generation_architecture_detail.md`.
- WP-10k candidate-selection eligibility matrix: `research/briefs/2026-04-candidate_selection_eligibility_matrix.md`.
- WP-10j candidate-selection rule design: `docs/research_pipeline/2026-04-candidate_selection_rule_design.md`.
- WP-10i Phase 10 architecture plan: `docs/research_pipeline/2026-04-phase10_architecture_plan.md`.
- WP-10h forward-flow evidence plan: `docs/research_pipeline/2026-04-forward_flow_evidence_plan.md`.
- WP-10g REC-0012 correction.
- REC v1 stability and current corpus.
- OL v1 stability and current corpus.
- Lifecycle stability and current corpus.

These inputs are decision inputs only. They create no candidate-selection, cohort-selection, EXP-scaffold, evidence-generation, policy, scoring, ranking, recommendation, paper-live, runtime, or protected-path authority.

## 10.3 Current Machine State

Current repo truth records:

- REC corpus: 22 rows, `REC-0001` through `REC-0022`.
- REC expectation-source distribution: 11 `exp_success_criteria` rows and 11 `d2_006_gates` rows.
- REC-5 state: every current `candidate_id / outcome_kind / pipeline_version / expectation_source_type` segment has `reconciliation_count = 1`, below the `n >= 3` floor.
- OL corpus: 11 rows, `OL-0001` through `OL-0011`.
- LCH corpus: 30 rows, with transition counts 10 / 10 / 10 across `proposed->in_research`, `in_research->research_concluded`, and `research_concluded->archived`.
- Candidate registry overview exposes `H-001` through `H-011`.
- WP-10k eligibility posture marks current OL/REC target segments for `H-001` through `H-010` as eligible for future evidence planning and marks `H-011` as registry-present with no current OL/REC target segment.
- H-004 remains structurally split under both expectation sources by `pre_wp_5b` and `post_wp_5b` pipeline versions.
- REC-0012 correction is complete.
- `REC-0012`, `REC-0017`, and `REC-0019` preserve the D2 cost-drag expectation while excluding deterministic cost-drag comparison when `gross_pnl <= 0`.
- No open D2 non-positive-gross-PnL anomaly remains.

## 10.4 Decision Statement

Phase 10 target strategy is staged cohort with candidate-agnostic first stage.

Stage 1 proves mechanics without real target selection. Stage 2 may select a small real-candidate cohort only after Stage 1 validates and Main 3.0 authorizes the selection package. Stage 3 may expand beyond the small cohort only after Stage 2 validates.

No stage authorizes policy, scoring, ranking, recommendation, paper-live, runtime, deployment, OMS, risk, safe-mode, execution, config, dependency, or protected-path behavior.

## 10.5 Alternatives Considered

Candidate-agnostic only is rejected as the complete target strategy because it is safe but insufficient for the full future evidence-generation path. It is retained as Stage 1.

Single-candidate first is deferred and rejected for WP-10m because it overcommits to one candidate and risks creating a de facto recommendation.

Small-cohort first is deferred because it selects real targets before a candidate-agnostic mechanics proof exists.

Staged cohort with candidate-agnostic first stage is selected because it proves mechanics first, avoids implicit recommendation, and allows later controlled cohort selection only after authorization.

## 10.6 Stage Model

### Stage 1 - Candidate-Agnostic Mechanics Proof

Allowed:

- documentation-only decision/support packages;
- read-only query consumers if needed;
- placeholder worked examples or non-instance design surfaces.

Forbidden:

- real candidate selection;
- EXP scaffold or EXP plan;
- EXP, REP, OL, or REC artifacts;
- ranking, scoring, recommendation, policy, paper-live, runtime, or protected-path behavior.

### Stage 2 - Small Real-Candidate Cohort Selection

Allowed only after Stage 1 validates and Main 3.0 explicitly authorizes a candidate-selection application package.

Forbidden:

- performance ranking;
- policy readiness;
- paper-live readiness;
- runtime action.

### Stage 3 - Controlled Expansion

Allowed only after Stage 2 packages pass validation and Main 3.0 authorizes expansion.

Forbidden:

- automatic scale-up;
- policy, ranking, scoring, paper-live, runtime, or protected-path drift.

## 10.7 Candidate-Selection Package Boundary

WP-10m does not select candidates.

A future candidate-selection application package must use WP-10j rules and WP-10k matrix fields. It may produce a selected small cohort only if Main 3.0 explicitly authorizes that package.

The future package must not rank, score, or recommend candidates based on performance. It must preserve forbidden output exclusions:

```text
rank
score
recommendation
promotion_status
paper_live_readiness
policy_action
runtime_action
```

## 10.8 EXP Scaffold Boundary

EXP scaffolds remain forbidden in WP-10m.

The first EXP scaffold is earliest WP-10n or later. The first EXP scaffold requires WP-10m merged, explicit Main 3.0 authorization, and the selected target-strategy package complete.

No execution results, OL appends, REC appends, policy, ranking, scoring, recommendation, paper-live, runtime, or protected-path behavior are authorized by this decision.

## 10.9 REC-5 Handling

REC-5 remains:

```text
n >= 3 per candidate_id / outcome_kind / pipeline_version / expectation_source_type
```

WP-10m does not satisfy REC-5. Stage selection, candidate selection, and EXP scaffolds do not count as evidence.

Sources, pipeline versions, and H-004 pre/post rows do not combine. Future REC appends increment only exact `candidate_id / outcome_kind / pipeline_version / expectation_source_type` segments.

## 10.10 H-004 Handling

H-004 remains a structural split.

WP-10m does not choose H-004 as a target and does not infer improvement or degradation. Any future H-004 target selection must specify pipeline version and expectation source.

No special-casing of H-004 is authorized without later explicit authorization.

## 10.11 Evidence-Generation Package Implications

Future Stage 1 packages should be documentation/read-only only.

Future Stage 2 packages may be candidate-selection application packages only if explicitly authorized by Main 3.0.

A future EXP package may not occur until after Stage 2 unless Main 3.0 grants an explicit exception. OL/REC append packages require valid future EXP/REP evidence.

Consumers and stability packages remain descriptive.

## 10.12 Validation Requirements for Future Packages

Future packages must run applicable registry validators, EXP/REP validators when touched, OL validator when OL is touched, REC validator when REC is touched, all discovered integrity views, REC-5 segment delta checks when REC is touched, H-004 separation checks, forbidden-field scans, targeted pytest, full pytest where appropriate, `git diff --check`, changed-file checks, and preservation checks.

## 10.13 Stop Conditions for Future Packages

Future packages must stop if target selection occurs without Main 3.0 authorization, EXP scaffold is created before authorization, candidate ranking/score/recommendation appears, policy/paper-live/runtime language appears, evidence is synthetic or cloned, REC-5 dimension combining is required, integrity views become non-empty, protected paths are touched, tests fail, or changed-file scope expands.

## 10.14 Next Package Boundary

The next package after WP-10m should be a Stage 1 candidate-agnostic mechanics proof / decision-support package, documentation-only, unless Main 3.0 explicitly chooses otherwise.

It must not create EXP scaffolds. It may use placeholders and read-only query checks. The first EXP scaffold remains WP-10n or later only if explicitly authorized.

## 10.15 Supported Uses

WP-10m supports:

- target-strategy decision;
- sequencing control;
- future package boundary setting;
- preventing candidate-selection drift;
- preventing EXP scaffold drift;
- Main 3.0 decision support.

## 10.16 Unsupported Claims

WP-10m does not support claims of:

- selected candidates;
- selected cohort;
- ranking or recommendation;
- promotion or demotion;
- policy readiness;
- paper-live readiness;
- evidence-quality scoring;
- new evidence creation;
- EXP, REP, OL, or REC artifact creation;
- REC-5 satisfaction;
- runtime, deployment, OMS, risk, safe-mode, or execution authority;
- protected-path authority.

## 10.17 Validation Snapshot

WP-10m package validation results:

- REC validator: PASS.
- REC overview: PASS, 22 rows, `REC-0001` through `REC-0022`.
- REC expectation-source distribution: PASS, 11 `exp_success_criteria` / 11 `d2_006_gates`.
- REC-5 segment summary: PASS, all 22 current segments have `reconciliation_count = 1`.
- REC integrity views: PASS, `[]`.
- All discovered integrity views: PASS, `[]`.
- OL validator and overview: PASS, 11 rows, `OL-0001` through `OL-0011`.
- Candidate registry validator and overview: PASS, `H-001` through `H-011`.
- Lifecycle validator and overview: PASS, 30 rows with transitions 10 / 10 / 10.
- Targeted tests: PASS.
- Full pytest: PASS.
- `git diff --check`: PASS.

## 10.18 Non-Claims

WP-10m does not create:

- candidate selection;
- candidate cohort;
- EXP scaffold;
- EXP, REP, OL, or REC artifact;
- REC-5 satisfaction;
- schema change;
- validator change;
- query-layer view;
- policy;
- scoring;
- ranking or recommendation;
- paper-live semantics;
- runtime, deployment, OMS, risk, safe-mode, or execution authority;
- protected-path authority.
