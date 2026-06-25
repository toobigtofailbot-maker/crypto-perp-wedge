# Lab state-model coverage audit report

Read-only coverage audit. Mutates no artifact, runs no strategy, fetches no data, changes no coordinator/candidate bindings, and resumes no edge-search. Gaps are reported, never fixed here.

Schema: `lab_state_coverage_audit/v1`
Coordinator subjects: funding_positioning_fade_no_go, oos_gate_fail_demo

## Totals

- total discovered artifacts: 1281
- covered coordinator artifacts: 8
- surface-visible artifacts: 4
- unmapped gap artifacts: 99
- malformed / unreadable artifacts: 0

## By category

- coordinator_subject_covered: 4
- surface_visible: 4
- known_supporting_artifact: 264
- known_fixture: 0
- status_entry_only: 168
- synthesis_or_report: 3
- blocked_or_no_go_evidence: 17
- candidate_or_crossing_evidence: 15
- orphan_research_artifact: 4
- requires_followup_mapping: 66
- intentionally_out_of_scope: 736

## By coverage status

- covered: 8
- out_of_scope: 1174
- unmapped_gap: 99
- malformed: 0

## Findings (unmapped committed conclusions)

- **docs/research/PRICEONLY_SYNTHESIS_2026-06.md** (1 artifact(s)): Committed research conclusion not bound to any coordinator subject; not represented in dashboard/report/approval/scheduler.
    - `docs/research/PRICEONLY_SYNTHESIS_2026-06.md`
- **research/candidate_registry.jsonl** (1 artifact(s)): Committed research conclusion not bound to any coordinator subject; not represented in dashboard/report/approval/scheduler.
    - `research/candidate_registry.jsonl`
- **research/result_populations** (8 artifact(s)): Committed research conclusion not bound to any coordinator subject; not represented in dashboard/report/approval/scheduler.
    - `research/result_populations/RP-2134.result_population.json`
    - `research/result_populations/RP-2592.result_population.json`
    - `research/result_populations/RP-3731.result_population.json`
    - `research/result_populations/RP-4492.result_population.json`
    - `research/result_populations/RP-6236.result_population.json`
- **scratch/WP-RESEARCH-EDGE-SMA-FAMILY-01** (13 artifact(s)): Committed research conclusion not bound to any coordinator subject; not represented in dashboard/report/approval/scheduler.
    - `scratch/WP-RESEARCH-EDGE-SMA-FAMILY-01/blocked_bridge_reason.json`
    - `scratch/WP-RESEARCH-EDGE-SMA-FAMILY-01/blocked_candidate_review_reason.json`
    - `scratch/WP-RESEARCH-EDGE-SMA-FAMILY-01/blocked_robustness_reason.json`
    - `scratch/WP-RESEARCH-EDGE-SMA-FAMILY-01/blocked_sweep_plan_reason.json`
    - `scratch/WP-RESEARCH-EDGE-SMA-FAMILY-01/blocked_variant_manifest_reason.json`
- **scratch/WP-RESEARCH-FUNDING-CARRY-01** (14 artifact(s)): Committed research conclusion not bound to any coordinator subject; not represented in dashboard/report/approval/scheduler.
    - `scratch/WP-RESEARCH-FUNDING-CARRY-01/blocked_bridge_reason.json`
    - `scratch/WP-RESEARCH-FUNDING-CARRY-01/blocked_formalizer_reason.json`
    - `scratch/WP-RESEARCH-FUNDING-CARRY-01/blocked_robustness_reason.json`
    - `scratch/WP-RESEARCH-FUNDING-CARRY-01/blocked_rp_replay_harness_reason.json`
    - `scratch/WP-RESEARCH-FUNDING-CARRY-01/blocked_runner_reason.json`
- **scratch/WP-RESEARCH-FUNDING-CARRY-02** (42 artifact(s)): Committed research conclusion not bound to any coordinator subject; not represented in dashboard/report/approval/scheduler.
    - `scratch/WP-RESEARCH-FUNDING-CARRY-02/bridge_output.json`
    - `scratch/WP-RESEARCH-FUNDING-CARRY-02/denominator_manifest.json`
    - `scratch/WP-RESEARCH-FUNDING-CARRY-02/formalizer_output.json`
    - `scratch/WP-RESEARCH-FUNDING-CARRY-02/funding_family_adapter_contract.json`
    - `scratch/WP-RESEARCH-FUNDING-CARRY-02/funding_pnl_boundary_note.json`
- **scratch/WP-RESEARCH-FUNDING-CARRY-02-FOLLOWUP-01** (3 artifact(s)): Committed research conclusion not bound to any coordinator subject; not represented in dashboard/report/approval/scheduler.
    - `scratch/WP-RESEARCH-FUNDING-CARRY-02-FOLLOWUP-01/local_data_staging_report.json`
    - `scratch/WP-RESEARCH-FUNDING-CARRY-02-FOLLOWUP-01/repo_truth_data_contract.md`
    - `scratch/WP-RESEARCH-FUNDING-CARRY-02-FOLLOWUP-01/retry_decision.md`
- **scratch/WP-RESEARCH-ORB-EXIT-RESPEC-01** (10 artifact(s)): Committed research conclusion not bound to any coordinator subject; not represented in dashboard/report/approval/scheduler.
    - `scratch/WP-RESEARCH-ORB-EXIT-RESPEC-01/blocked_bridge_reason.json`
    - `scratch/WP-RESEARCH-ORB-EXIT-RESPEC-01/blocked_candidate_review_reason.json`
    - `scratch/WP-RESEARCH-ORB-EXIT-RESPEC-01/blocked_robustness_reason.json`
    - `scratch/WP-RESEARCH-ORB-EXIT-RESPEC-01/denominator_audit.json`
    - `scratch/WP-RESEARCH-ORB-EXIT-RESPEC-01/formalizer_output_reference.json`
- **scratch/WP-RESEARCH-PRICEONLY-SYNTHESIS-01** (7 artifact(s)): Committed research conclusion not bound to any coordinator subject; not represented in dashboard/report/approval/scheduler.
    - `scratch/WP-RESEARCH-PRICEONLY-SYNTHESIS-01/evidence_index.json`
    - `scratch/WP-RESEARCH-PRICEONLY-SYNTHESIS-01/lab_gap_checklist.json`
    - `scratch/WP-RESEARCH-PRICEONLY-SYNTHESIS-01/main_report_back_guardrail.txt`
    - `scratch/WP-RESEARCH-PRICEONLY-SYNTHESIS-01/open_decision_surfaces.txt`
    - `scratch/WP-RESEARCH-PRICEONLY-SYNTHESIS-01/priceonly_synthesis_source_audit.json`

## Recommended follow-up packages

- **WP-LAB-COORDINATOR-SUBJECT-COVERAGE-EXTENSION-01** — Bind the unmapped committed research conclusions as additional read-only coordinator subjects so the operator view stops omitting them. No new research; mapping only.

