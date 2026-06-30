# Run Registry Inventory

Package: `WP-LAB-RUN-REGISTRY-PROVENANCE-HARDEN-01`

Entry count: 24

| Entry | Class | Terminal state | Validation | Source paths |
| --- | --- | --- | --- | --- |
| `RP-2134` | `canonical` | `complete_non_decisional` | `PASS` | `research/result_populations/RP-2134.result_population.json` |
| `RP-2592` | `canonical` | `NO-GO` | `PASS` | `research/result_populations/RP-2592.result_population.json` |
| `RP-3731` | `canonical` | `NO-GO` | `PASS` | `research/result_populations/RP-3731.result_population.json` |
| `RP-4492` | `canonical` | `complete_non_decisional` | `PASS` | `research/result_populations/RP-4492.result_population.json` |
| `RP-6236` | `canonical` | `complete_non_decisional` | `PASS` | `research/result_populations/RP-6236.result_population.json` |
| `RP-6688` | `canonical` | `NO-GO` | `PASS` | `research/result_populations/RP-6688.result_population.json` |
| `RP-7134` | `canonical` | `NO-GO` | `PASS` | `research/result_populations/RP-7134.result_population.json` |
| `RP-7520` | `canonical` | `NO-GO` | `PASS` | `research/result_populations/RP-7520.result_population.json` |
| `candidate_registry_current` | `canonical` | `mixed_NO-GO_and_reserved` | `PASS` | `research/candidate_registry.jsonl` |
| `funding_positioning_fade_synthesis_2026_06` | `scratch_only` | `NO-GO` | `PASS` | `docs/research/FUNDING_POSITIONING_FADE_SYNTHESIS_2026-06.md` |
| `funding_riskmanaged_triage_run_blocked` | `blocked` | `blocked` | `BLOCKED` | `scratch/WP-RESEARCH-FUNDING-RISKMANAGED-TRIAGE-RUN-01/blocked_reason.json` |
| `funding_riskmanaged_stage1_triage` | `scratch_only` | `NO-GO` | `PASS` | `scratch/WP-RESEARCH-FUNDING-RISKMANAGED-TRIAGE-01/stage1_verdict.json`<br>`scratch/WP-RESEARCH-FUNDING-RISKMANAGED-TRIAGE-01/row_accounting.json` |
| `priceonly_synthesis_2026_06` | `docs_only` | `complete` | `PASS` | `docs/research/PRICEONLY_SYNTHESIS_2026-06.md`<br>`scratch/WP-RESEARCH-PRICEONLY-SYNTHESIS-01/evidence_index.json` |
| `lab_state_model_surface` | `docs_only` | `complete` | `PASS` | `docs/research/LAB_COORDINATOR_STATE_MODEL.md`<br>`tools/lab_state/` |
| `lab_results_dashboard_surface` | `docs_only` | `complete` | `PASS` | `docs/research/LAB_RESULTS_DASHBOARD_SURFACE.md`<br>`tools/lab_dashboard/` |
| `lab_reporting_surface` | `docs_only` | `complete` | `PASS` | `docs/research/LAB_OPERATOR_BRIEF_REPORT_SURFACE.md`<br>`tools/lab_reporting/` |
| `lab_approval_queue_surface` | `docs_only` | `nothing_candidate_ready` | `PASS` | `docs/research/LAB_APPROVAL_QUEUE_SURFACE.md` |
| `lab_scheduler_shell_surface` | `docs_only` | `default_off_inert` | `PASS` | `docs/research/LAB_SCHEDULER_SHELL_DEFAULT_OFF.md` |
| `baseline_payload_define_pr583` | `docs_only` | `complete` | `PASS` | `scratch/WP-LAB-BASELINE-PAYLOAD-DEFINE-01/baseline_payload_catalog.json` |
| `gate_hardening_pr584` | `docs_only` | `complete` | `PASS` | `docs/research/LAB_STANDARD_CANDIDATE_GATES.md`<br>`scratch/WP-LAB-GATE-HARDENING-WALKFORWARD-ROBUSTNESS-01/baseline_gate_expectations.json` |
| `nonpromotable_crossing_guard_pr585` | `fixture_only` | `reject_by_construction` | `PASS` | `docs/research/LAB_NONPROMOTABLE_CROSSING_GUARD.md`<br>`scratch/WP-LAB-CROSSING-NONPROMOTABLE-GUARD-01/guard_validation_summary.json` |
| `agent_loop_baseline_pr586` | `fixture_only` | `no-candidate` | `PASS` | `scratch/WP-LAB-AGENTLOOP-BASELINE-EXERCISE-01/baseline_loop_result.json`<br>`scratch/WP-LAB-AGENTLOOP-BASELINE-EXERCISE-01/no_candidate_review_result.json`<br>`scratch/WP-LAB-AGENTLOOP-BASELINE-EXERCISE-01/crossing_rejection_result.json` |
| `completion_map_update_pr587` | `docs_only` | `complete_with_held_B_boundaries` | `PASS` | `docs/research/LAB_COMPLETION_MAP.md`<br>`scratch/WP-LAB-COMPLETION-MAP-UPDATE-BASELINE-PROVEN-01/completion_state_update.json`<br>`scratch/WP-LAB-COMPLETION-MAP-UPDATE-BASELINE-PROVEN-01/held_boundary_map.json` |
| `held_boundary_map_current` | `blocked` | `deferred_or_go_gated` | `PASS` | `scratch/WP-LAB-COMPLETION-MAP-UPDATE-BASELINE-PROVEN-01/held_boundary_map.json` |

This index is read-only and non-authoritative. It mutates no canonical artifacts and writes no candidate registry state.
