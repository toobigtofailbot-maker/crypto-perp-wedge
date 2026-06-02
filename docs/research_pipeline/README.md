# Research Pipeline Foundation

This directory documents the candidate-agnostic foundation layer for the Phase 2
research machine.

## Documents

- `2026-04-candidate_registry.md` explains `research/candidate_registry.jsonl`,
  the registry schema, and how candidate status links to hypotheses, decision
  records, and the trial log.
- `2026-04-experiment_artifacts.md` explains JSON Experiment Plan and Experiment
  Report artifacts for the Continuous Improvement loop.

## Instances

The first exercise of the experiment artifact grammar is EXP-0001 / REP-0001
for H-005 under `research/experiments/`. See
`2026-04-retrospective_instance_convention.md` for the convention used when an
instance is authored after execution.

The first Stage 6 / Stage 7 retrospective instance pair is DCH-0001 / REL-0001
for the historical H-005 NO-GO archive outcome.

The first Stage 6 / Stage 7 forward-flow instance pair is DCH-0002 / REL-0002
for the H-004 REP-0011 current-evidence NO-GO archive outcome.

## Query Layer

`2026-04-query_layer.md` explains the read-only DuckDB query layer over the
candidate registry, experiment artifacts, and trial log.

## Stages 6-7 Artifacts

`2026-04-decision_change_artifact.md` and
`2026-04-release_notes_artifact.md` explain the JSON artifact conventions for
the Human Approval Gate and Release & Monitor stages.

## Advisory Agent Outputs

`2026-04-agent_output_artifact.md` and
`2026-04-regime_scoring_agent_stub.md` explain the first deterministic bounded
advisory agent output family introduced by WP-7a. The first instance is
fixture-backed, schema-validated, queryable, and advisory-only.

## Macro Window Agent Outputs

`2026-04-macro_window_agent_output_artifact.md` and
`2026-04-macro_narrative_agent_stub.md` explain the first deterministic
macro/narrative advisory lane introduced by WP-7f. The first instance is a
committed-fixture-backed macro-window flag with no runtime influence.

## Pre-Gate Advisory Snapshots

`2026-04-pre_gate_advisory_snapshot_artifact.md`,
`2026-04-pre_gate_advisory_snapshot_builder.md`, and
`2026-04-pgas_combination_rule_v1.md` explain the pre-gate advisory snapshot
family introduced by WP-7g and extended by WP-7h. `PGAS-0001` remains the
historical bundle-only snapshot. `PGAS-0002` is the first deterministic
`MACRO_AWARE_FLOOR` rule-applied snapshot with a committed combined bucket and
no runtime influence.

## Advisory Bucket Mappings

`2026-04-bucket_mapping_artifact.md` and `2026-04-score_bucket_mapper.md`
explain the first deterministic advisory score bucket mapper introduced by
WP-6j. The first instance consumes `AOUT-0001` only and maps it into the locked
`ALLOW` / `ALLOW_REDUCED` / `BLOCK` domain without overlay contact.

## Overlay Shadow Logs

`2026-04-overlay_shadow_log_artifact.md` and
`2026-04-overlay_shadow_external_hook.md` explain the first zero-override
overlay shadow log family introduced by WP-7c and extended by WP-7i. The
historical first instance compares `BMAP-0001` against an externally observable
overlay-side source without changing `lib/` or runtime behavior. `OSH-0002` is
the first PGAS-sourced shadow entry and compares `PGAS-0002.combined_bucket`
through the same external observation path.

`2026-04-shadow_signal_views.md` explains the first aggregate diagnostic views
over the committed overlay shadow-log family, now segmentable by
`advisory_source`.

## Briefs / Diagnostic Outputs

- `2026-04-cross_candidate_diagnostic.md`: First cross-candidate diagnostic
  brief (WP-6e). See the `queries/` + `outputs/` directory beside it.
- `research/briefs/2026-05-cross_candidate_diagnostic_brief.md`: Second
  cross-candidate diagnostic brief over the extended query layer, with adjacent
  `queries/` and `outputs/` evidence directories.
- `research/briefs/2026-06-third_cross_candidate_diagnostic_brief.md`: Third
  cross-candidate diagnostic brief with H-012 included, with adjacent
  `queries/` and `outputs/` evidence directories.
- `2026-04-shadow_log_diagnostic.md`: First shadow-log diagnostic brief (WP-7e).

## Consolidated Package Index

This consolidated index is a navigation aid for `docs/research_pipeline/`. It
does not supersede source documents, canonical artifacts, query outputs,
decision records, schemas, validators, or locked baseline documents.

### Core Foundation And Registry Docs

- `2026-04-candidate_registry.md` - candidate registry purpose, schema, and
  links to hypotheses, decisions, and trial logs; registry foundation.
- `2026-04-schema_family_inventory.md` - schema-family inventory for research
  artifacts; inventory surface.
- `2026-04-schema_versioning_discipline.md` - schema-versioning conventions;
  discipline surface.
- `2026-04-lifecycle_state_vocabulary.md` - lifecycle state vocabulary;
  lifecycle grammar surface.
- `2026-04-lifecycle_transition_graph.md` - lifecycle transition graph;
  lifecycle grammar surface.
- `2026-04-lifecycle_change_artifact.md` - lifecycle change artifact grammar;
  lifecycle artifact surface.
- `2026-04-lch_retrospective_backfill_methodology.md` - LCH retrospective
  backfill method; methodology surface.
- `2026-04-lifecycle_stability.md` - lifecycle stability lock; lock surface.
- `2026-04-phase9_decision_record.md` - Phase 9 decision record; decision
  surface.
- `2026-04-post_rec_architecture_checkpoint.md` - post-REC architecture
  checkpoint; checkpoint surface.
- `2026-04-phase9_to_phase10_transition_decision.md` - Phase 9 to Phase 10
  boundary decision; decision surface.
- `2026-04-forward_flow_evidence_plan.md` - future forward-flow evidence
  plan; planning surface.
- `2026-04-phase10_architecture_plan.md` - Phase 10 architecture plan;
  planning surface.
- `2026-04-candidate_selection_rule_design.md` - candidate-selection rule
  design; design surface.
- `2026-04-target_strategy_decision.md` - target-strategy decision document;
  decision surface.
- `2026-04-stage1_candidate_agnostic_mechanics_proof.md` - Stage 1
  candidate-agnostic mechanics proof; proof surface.
- `2026-04-stage1_checkpoint_lock.md` - Stage 1 checkpoint lock; lock surface.
- `2026-04-stage2_authorization_decision.md` - Stage 2 authorization decision;
  decision surface.
- `2026-04-stage2_candidate_selection_application.md` - Stage 2
  candidate-selection application; application surface.
- `2026-04-stage2_first_substage_checkpoint_lock.md` - Stage 2 first-substage
  checkpoint lock; lock surface.
- `2026-04-stage2_second_pass_segment_selection_application.md` - Stage 2
  second-pass segment-selection application; application surface.
- `2026-04-stage2_first_substage_stability_lock.md` - Stage 2 first-substage
  stability lock; lock surface.
- `2026-04-post_checkpoint_direction_decision.md` - post-checkpoint Stage 2
  direction decision; decision surface.
- `2026-04-post_consumer_brief_direction_decision.md` - post-consumer-brief
  Stage 2 direction decision; decision surface.
- `2026-04-post_floor_crossing_direction_decision.md` - post-floor-crossing
  Stage 2 direction decision; decision surface.
- `2026-05-stage2c_workflow_efficiency_operating_model_lock.md` - Stage 2c
  workflow-efficiency operating-model lock; workflow lock surface.
- `2026-05-stage2c_paired_source_reuse_methodology_design.md` - paired-source
  reuse methodology design; design surface.
- `2026-05-stage2c_batched_cycle_methodology_design.md` - batched cycle
  methodology design; design surface.

### Experiment, Report, And Trial-Log Grammar

- `2026-04-experiment_artifacts.md` - experiment plan and report artifact
  grammar; artifact grammar surface.
- `2026-04-retrospective_instance_convention.md` - retrospective EXP/REP
  instance convention; convention surface.
- `2026-04-experiment_runner_interface_design.md` - experiment-runner
  interface design; design surface.
- `2026-04-evidence_generation_architecture_detail.md` - evidence-generation
  architecture detail; architecture surface.
- `2026-04-parameter_sweep_design.md` - parameter-sweep design; design
  surface.
- `2026-04-parameter_sweep_checkpoint.md` - parameter-sweep checkpoint;
  checkpoint surface.
- `2026-04-json_sweep_spec_materialization_design.md` - JSON sweep-spec
  materialization design; design surface.
- `2026-04-json_sweep_spec_loader_vertical_slice.md` - JSON sweep-spec loader
  vertical slice; implementation evidence surface.
- `2026-04-json_sweep_end_to_end_exercise.md` - JSON sweep end-to-end
  exercise; exercise surface.
- `2026-04-local_parameter_sweep_vertical_slice.md` - local parameter-sweep
  vertical slice; implementation evidence surface.
- `2026-04-local_parameter_sweep_second_shape.md` - local parameter-sweep
  second shape; design surface.
- `2026-04-local_parameter_sweep_usability_checkpoint.md` - local
  parameter-sweep usability checkpoint; checkpoint surface.
- `2026-04-local_run_registry_design.md` - local run-registry design; design
  surface.
- `2026-04-local_run_registry_vertical_slice.md` - local run-registry vertical
  slice; implementation evidence surface.
- `2026-04-local_run_registry_validation_slice.md` - local run-registry
  validation slice; validation surface.
- `2026-04-local_run_registry_validation_integration.md` - local run-registry
  validation integration; validation surface.
- `2026-04-local_sweep_result_index_design.md` - local sweep result-index
  design; design surface.
- `2026-04-local_sweep_result_index_vertical_slice.md` - local sweep
  result-index vertical slice; implementation evidence surface.
- `2026-04-local_sweep_usability_runway_checkpoint.md` - local sweep usability
  runway checkpoint; checkpoint surface.
- `2026-04-local_sweep_usability_consumer_brief.md` - local sweep usability
  consumer brief; brief surface.
- `2026-04-batch_manifest_format_design.md` - batch manifest format design;
  design surface.
- `2026-04-batch_manifest_vertical_slice.md` - batch manifest vertical slice;
  implementation evidence surface.
- `2026-04-batch_runner_design.md` - batch runner design; design surface.
- `2026-04-batch_run_summary_format_design.md` - batch-run summary format
  design; design surface.
- `2026-04-batch_run_summary_validation_vertical_slice.md` - batch-run summary
  validation vertical slice; validation surface.
- `2026-04-local_batch_runner_vertical_slice.md` - local batch-runner vertical
  slice; implementation evidence surface.
- `2026-04-local_batch_runner_summary_validation_integration.md` - local
  batch-runner summary validation integration; validation surface.
- `2026-04-local_dry_run_runner_vertical_slice.md` - local dry-run runner
  vertical slice; implementation evidence surface.

### Outcome-Ledger And Reconciliation Grammar

- `2026-04-outcome_ledger_artifact.md` - outcome-ledger artifact grammar;
  artifact grammar surface.
- `2026-04-outcome_ledger_backfill_methodology.md` - outcome-ledger
  retrospective backfill method; methodology surface.
- `2026-04-outcome_ledger_v1_stability.md` - outcome-ledger v1 stability lock;
  lock surface.
- `2026-04-reconciliation_artifact.md` - REC v1 reconciliation artifact
  grammar; artifact grammar surface.
- `2026-04-reconciliation_backfill_methodology.md` - REC v1 retrospective
  backfill method; methodology surface.
- `2026-04-rec_d2_006_gates_methodology.md` - D2-006 REC methodology;
  methodology surface.
- `2026-04-rec_v1_stability.md` - REC v1 stability lock; lock surface.
- `2026-04-rec5_floor_gap_stability.md` - REC-5 floor-gap stability lock; lock
  surface.

### Query-Layer And Integrity Docs

- `2026-04-query_layer.md` - read-only DuckDB query layer and integrity views;
  query-layer foundation.
- `2026-05-pre_execution_exp_integrity_refinement_design.md` - pre-execution
  EXP integrity refinement design; integrity design surface.
- `2026-05-scope6_query_layer_extension_design.md` - Scope 6 query-layer
  extension design; query-layer design surface.
- `2026-05-auto_bridge_schema_validator_query_validation_design.md` - AUTO
  bridge schema, validator, and query validation expectations; design surface.
- `2026-05-auto_bridge_validation_integrity_implementation.md` - AUTO bridge
  validation and integrity implementation; implementation surface.

### Scope 6 / Stage 6-7 Approval And Shadow-Evidence Docs

- `2026-04-decision_change_artifact.md` - decision-change artifact grammar for
  Human Approval Gate state changes; artifact grammar surface.
- `2026-04-release_notes_artifact.md` - release-notes artifact grammar for
  Release & Monitor state changes; artifact grammar surface.
- `2026-05-scope6_packaging_design_opening.md` - Scope 6 packaging design
  opening; design surface.
- `2026-05-scope6_packaging_design_consolidation.md` - Scope 6 packaging design
  consolidation; design surface.
- `2026-05-scope6_packaging_locking_decision.md` - Scope 6 packaging locking
  decision; decision surface.
- `2026-05-permanent_human_gate_preservation_sketch.md` - permanent human-gate
  preservation sketch; sketch surface.
- `2026-05-research_to_shadow_readiness_criteria_sketch.md` - research-to-shadow
  criteria sketch; sketch surface.
- `2026-05-shadow_to_paper_readiness_criteria_sketch.md` - shadow-to-paper
  criteria sketch; sketch surface.
- `2026-05-approval_readiness_criteria_design_opening.md` - approval/readiness
  criteria design opening; design surface.
- `2026-05-approval_readiness_criteria_refinement.md` - approval/readiness
  criteria focused refinement; design surface.
- `2026-05-approval_readiness_criteria_consolidation.md` - approval/readiness
  criteria consolidation; design surface.
- `2026-05-approval_readiness_criteria_locking_decision.md` -
  approval/readiness criteria locking decision; decision surface.
- `2026-05-approval_readiness_criteria_tranche_checkpoint.md` -
  approval/readiness criteria tranche checkpoint; checkpoint surface.

### Advisory / Macro / Pre-Gate / Overlay Diagnostic Docs

- `2026-04-agent_output_artifact.md` - advisory agent output artifact grammar;
  artifact grammar surface.
- `2026-04-regime_scoring_agent_stub.md` - deterministic regime/scoring agent
  stub; advisory stub surface.
- `2026-04-bucket_mapping_artifact.md` - advisory bucket-mapping artifact
  grammar; artifact grammar surface.
- `2026-04-score_bucket_mapper.md` - deterministic score-bucket mapper;
  mapper surface.
- `2026-04-macro_window_agent_output_artifact.md` - macro-window agent output
  artifact grammar; artifact grammar surface.
- `2026-04-macro_narrative_agent_stub.md` - macro/narrative agent stub;
  advisory stub surface.
- `2026-04-pre_gate_advisory_snapshot_artifact.md` - pre-gate advisory snapshot
  artifact grammar; artifact grammar surface.
- `2026-04-pre_gate_advisory_snapshot_builder.md` - pre-gate advisory snapshot
  builder; builder surface.
- `2026-04-pgas_combination_rule_v1.md` - PGAS combination rule v1; rule
  surface.
- `2026-04-overlay_shadow_log_artifact.md` - overlay shadow-log artifact
  grammar; artifact grammar surface.
- `2026-04-overlay_shadow_external_hook.md` - external overlay shadow hook;
  shadow evidence surface.
- `2026-04-shadow_run_helper.md` - manual/on-demand shadow-run helper;
  helper surface.
- `2026-04-shadow_signal_views.md` - aggregate shadow-signal views; query
  surface.
- `2026-04-signal_definition_v1.md` - signal definition v1; definition
  surface.
- `2026-04-sss_v1_stability.md` - SSS v1 stability lock; lock surface.
- `2026-04-sss_v2_schema.md` - SSS v2 schema design; schema design surface.
- `2026-04-sss_v2_stability.md` - SSS v2 stability lock; lock surface.

### Cross-Candidate And Shadow Diagnostic Briefs

- `research/briefs/2026-04-cross_candidate_diagnostic.md` - first
  cross-candidate diagnostic brief; diagnostic brief surface.
- `research/briefs/2026-05-cross_candidate_diagnostic_brief.md` - second
  cross-candidate diagnostic brief; diagnostic brief surface.
- `research/briefs/2026-06-third_cross_candidate_diagnostic_brief.md` - third
  cross-candidate diagnostic brief; diagnostic brief surface.
- `2026-05-cross_candidate_diagnostic_brief_design.md` - cross-candidate
  diagnostic brief design; design surface.
- `2026-05-third_cross_candidate_diagnostic_brief_design.md` - third
  cross-candidate diagnostic brief design; design surface.
- `research/briefs/2026-04-shadow_log_diagnostic.md` - first shadow-log
  diagnostic brief; diagnostic brief surface.
- `2026-05-broad_floor_crossing_expectation_source_coverage_brief.md` -
  broad-floor-crossing expectation-source coverage brief; brief surface.
- `2026-05-broad_floor_crossing_h004_pipeline_version_split_brief.md` -
  broad-floor-crossing H-004 pipeline-version split brief; brief surface.
- `2026-05-broad_floor_crossing_combined_cohort_enumeration_brief.md` -
  broad-floor-crossing combined-cohort enumeration brief; brief surface.
- `2026-05-broad_floor_crossing_interpretation_tranche_checkpoint.md` -
  broad-floor-crossing interpretation tranche checkpoint; checkpoint surface.
- `2026-05-broad_floor_crossing_sufficiency_decision.md` -
  broad-floor-crossing sufficiency decision; decision surface.

### Path B Design, Locking, Tranche, Checkpoint, And Integrity-Refinement Docs

- `2026-05-path_b_reassessment_design_opening.md` - Path B reassessment design
  opening; design surface.
- `2026-05-path_b_reassessment_design_substance.md` - Path B reassessment
  design substance; design surface.
- `2026-05-path_b_reassessment_design_consolidation.md` - Path B reassessment
  design consolidation; design surface.
- `2026-05-path_b_reassessment_locking_decision.md` - Path B reassessment
  locking decision; decision surface.
- `2026-05-path_b_execution_design_opening.md` - Path B execution design
  opening; design surface.
- `2026-05-path_b_execution_candidate_selection_design.md` - Path B execution
  candidate-selection design; design surface.
- `2026-05-path_b_execution_tranche_checkpoint.md` - Path B execution tranche
  checkpoint; checkpoint surface.
- `2026-06-h_011_reserved_slot_resolution_design.md` - H-011 reserved-slot
  resolution design; design surface.
- `2026-06-h_011_reserved_slot_resolution_decision.md` - H-011 reserved-slot
  resolution decision; decision surface.
- `2026-06-second_path_b_execution_design_opening.md` - second Path B
  execution design opening; design surface.

### Research Automation And AUTO Bridge Docs

- `2026-06-strategy_research_lab_target_operating_model_design_opening.md` -
  Strategy Research Lab target operating-model design opening; design surface.
- `2026-06-strategy_research_lab_target_operating_model.md` - Strategy
  Research Lab substantive target operating model; design surface.
- `2026-06-strategy_dsl_design_opening.md` - Strategy DSL design opening for
  lab strategy-spec representation; design surface.
- `2026-04-automation_build_operating_model.md` - automation build operating
  model; operating-model surface.
- `2026-04-research_automation_architecture_map.md` - research automation
  architecture map; architecture surface.
- `2026-05-auto_bridge_architecture_design_sketch.md` - AUTO bridge
  architecture design sketch; sketch surface.
- `2026-05-auto_bridge_design_continuation_candidate_binding.md` - AUTO bridge
  candidate-binding posture; design surface.
- `2026-05-auto_bridge_provenance_canonical_target_design.md` - AUTO bridge
  provenance and canonical-target design; design surface.
- `2026-05-auto_bridge_retroactivity_posture.md` - AUTO bridge retroactivity
  posture; posture surface.
- `2026-05-auto_bridge_design_tranche_checkpoint.md` - AUTO bridge design
  tranche checkpoint; checkpoint surface.
- `2026-05-auto_bridge_implementation_tranche_boundary.md` - AUTO bridge
  implementation tranche boundary; boundary surface.
- `2026-05-auto_bridge_intake_source_layer_implementation.md` - AUTO bridge
  intake/source-layer implementation; implementation surface.
- `2026-05-auto_bridge_transformation_normalization_implementation.md` - AUTO
  bridge transformation/normalization implementation; implementation surface.
- `2026-05-auto_bridge_candidate_artifact_draft_implementation.md` - AUTO
  bridge candidate-artifact draft implementation; implementation surface.
- `2026-05-auto_bridge_implementation_tranche_checkpoint.md` - AUTO bridge
  implementation tranche checkpoint; checkpoint surface.

### A2 / A2C Cohort And Floor-Expansion Docs

- `2026-04-a2_architecture_design_opening.md` - A2 architecture-design opening;
  design surface.
- `2026-04-a2_scope_shape_lock.md` - A2 scope-shape lock; lock surface.
- `2026-04-a2_scope_shape_resolution.md` - A2 scope-shape resolution surface;
  resolution surface.
- `2026-04-a2_cohort_selection_methodology.md` - A2 cohort-selection
  methodology; methodology surface.
- `2026-04-a2_cohort_architecture_design.md` - A2 cohort architecture design;
  design surface.
- `2026-04-a2_cohort_methodology_application.md` - A2 cohort methodology
  application; application surface.
- `2026-04-a2c001_h001_first_member_runway_checkpoint.md` - A2C-001 H-001
  first-member runway checkpoint; checkpoint surface.
- `2026-04-a2c001_h001_interim_interpretation.md` - A2C-001 H-001 interim
  interpretation; interpretation surface.
- `2026-05-a2c001_reopening_h005_status_reconciliation.md` - A2C-001 reopening
  and H-005 status reconciliation; reconciliation surface.
- `2026-05-a2c001_h005_runway_checkpoint.md` - A2C-001 H-005 runway
  checkpoint; checkpoint surface.
- `2026-05-a2c001_h006_runway_checkpoint.md` - A2C-001 H-006 runway
  checkpoint; checkpoint surface.
- `2026-05-a2c001_cohort_completion_checkpoint.md` - A2C-001 cohort
  completion checkpoint; checkpoint surface.
- `2026-05-a2c001_cohort_interpretation_stability.md` - A2C-001 cohort
  interpretation stability; lock surface.
- `2026-05-a2c001_approval_readiness_discussion_surface.md` - A2C-001
  approval/readiness discussion surface; discussion surface.
- `2026-05-a2c001_deferral_no_approval_decision_lock.md` - A2C-001
  deferral/no-approval decision lock; lock surface.
- `2026-05-a2c001_stop_defer_hold_lock.md` - A2C-001 stop/defer hold lock;
  lock surface.
- `2026-05-a2c001_post_deferral_closeout_index.md` - A2C-001 post-deferral
  closeout index; index surface.
- `2026-05-a2c001_cohort_phase_closure_decision.md` - A2C-001 cohort-phase
  closure decision; decision surface.
- `2026-05-a2c002_cohort_definition.md` - A2C-002 cohort definition;
  definition surface.
- `2026-05-a2c002_runway_shape.md` - A2C-002 runway shape; planning surface.
- `2026-05-a2c002_h002_completion_checkpoint.md` - A2C-002 H-002 completion
  checkpoint; checkpoint surface.
- `2026-05-a2c002_h003_completion_checkpoint.md` - A2C-002 H-003 completion
  checkpoint; checkpoint surface.
- `2026-05-a2c002_h004_completion_checkpoint.md` - A2C-002 H-004 completion
  checkpoint; checkpoint surface.
- `2026-05-a2c002_cohort_completion_checkpoint.md` - A2C-002 cohort
  completion checkpoint; checkpoint surface.
- `2026-05-a2c002_cohort_phase_closure_decision.md` - A2C-002 cohort-phase
  closure decision; decision surface.
- `2026-05-r1_r2_h006_approval_use_lock.md` - H-006 R1/R2 approval-use
  decision lock; lock surface.

### Phase 3 Boundary And Implementation Planning Docs

- `2026-05-phase3_architecture_design_opening.md` - Phase 3 architecture
  design opening; design surface.
- `2026-05-phase3_shadow_deployment_sketch.md` - Phase 3 shadow-deployment
  sketch; sketch surface.
- `2026-05-phase3_shadow_adapter_authorization_scope.md` - Phase 3 shadow
  adapter authorization-scope sketch; sketch surface.
- `2026-05-phase3_monitoring_dashboard_sketch.md` - Phase 3 monitoring
  dashboard sketch; sketch surface.
- `2026-05-phase3_paper_trading_bridge_sketch.md` - Phase 3 paper-trading
  bridge sketch; sketch surface.
- `2026-05-phase3_monitoring_paper_bridge_authorization_scope.md` - Phase 3
  monitoring, dashboard, and paper-bridge authorization-scope sketch; sketch
  surface.
- `2026-05-phase3_live_trading_boundary_sketch.md` - Phase 3 live-trading
  boundary sketch; sketch surface.
- `2026-05-phase3_architecture_sketch_tranche_checkpoint.md` - Phase 3
  architecture-sketch tranche checkpoint; checkpoint surface.
- `2026-05-phase3_implementation_authorization_opening.md` - Phase 3
  implementation authorization opening; design surface.
- `2026-05-phase3_implementation_authorization_decision.md` - Phase 3
  implementation authorization decision; decision surface.
- `2026-05-phase3_implementation_tranche_planning.md` - Phase 3 implementation
  tranche planning; planning surface.
- `2026-05-phase3_implementation_tranche_checkpoint.md` - Phase 3
  implementation tranche checkpoint; checkpoint surface.
- `2026-05-post_a2c_active_track_selection_gate.md` - post-A2C active-track
  selection gate; gate surface.
- `2026-05-post_a2c_lessons_decision_review.md` - post-A2C lessons decision
  review; review surface.

### Navigation / Index-Maintenance Docs

- `README.md` - research-pipeline overview and consolidated index; navigation
  surface.
- `2026-06-index_consolidation_design.md` - consolidated README index design;
  design surface.

Future packages creating a new research-pipeline document should add one
concise index entry. They should not rewrite old entries unless correcting a
factual path, title, or surface-type error.

## Relationship To Architecture

This package supports the research-pipeline side of the accepted research
machine direction. It creates structured candidate and experiment artifacts so
future work can compare candidates systematically instead of relying on
prose-only status scattered across decision records.

Diagram 2 stages 3 through 6 depend on this grammar:

- Propose: create an Experiment Plan.
- Validate Offline: execute the plan and log trials.
- Validate Paper: report paper or shadow evidence when scoped later.
- Human Approval: review schema-validated artifacts before any promotion.

The decision-pipeline side, including agents, score-bucket mapping, and any
advisory automation, remains later work.

## Validation Commands

Run the registry validator:

```powershell
.venv\Scripts\python.exe tools\registry\validate_registry.py
```

Run the experiment artifact validator:

```powershell
.venv\Scripts\python.exe tools\registry\validate_experiment_artifacts.py
```

Run the regression tests:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_registry_validation.py -q
```

## Out Of Scope

- No candidate auto-generation.
- No agent in the loop.
- No DuckDB query layer.
- No Monte Carlo infrastructure.
- No gold data procurement.
- No H-011 pre-registration.
- No execution-core changes.
