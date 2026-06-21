# Candidate Lifecycle Review Packet

- Engine: WP-LAB-CANDIDATE-LIFECYCLE-ENGINE-01
- Created at UTC: 2026-06-20T12:00:00Z
- Posture: scratch-only, reference-only, human-gated

## Non-Authority Flags
- human_gated
- not_auto_promotion
- not_readiness_authority
- not_paper_live
- not_canonical_evidence_mutation
- not_execution_authority

## CANDIDATE-FIXTURE-0001
- Current state: research_concluded
- Pending state: human_approval_required
- Requested transition: research_concluded->paper_eligible
- Evidence links:
  - result_population_ref: RP-FIXTURE-0001
  - walkforward_run_ref: scratch/WP-LAB-WALKFORWARD-RUN-01/walkforward_run_report.json
  - robustness_report_ref: missing
  - dashboard_review_ref: scratch/WP-LAB-DASHBOARD-EXPANSION-01/static_dashboard_review.json
  - idea_intake_ref: tests/fixtures/candidate_lifecycle_engine/valid_candidate_inputs.json
- Blockers:
  - none
- Missing evidence:
  - none
- Caveats:
  - Scratch lifecycle report only.
  - Evidence links are references only and are not mutated.
  - Promotion and paper/live decisions remain human-gated outside this engine.
- Manual gate requirement: A human gate owner must make any promotion, paper, live, or readiness decision outside this engine.
- Next allowed human decisions:
  - record paper eligibility by separate human lifecycle change
  - reject
  - archive
