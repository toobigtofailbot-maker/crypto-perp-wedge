# Repo Truth Discovery - WP-LAB-COVERAGE-GAP-CLOSE-01

## Fact

- Base inspected: `origin/main` at `b64c4f2`, after PRs #573, #574, and #575.
- Required dependency paths are present on the refreshed worktree.
- Pre-binding refreshed audit totals: `{'total_discovered_artifacts': 1303, 'covered_coordinator_artifacts': 8, 'surface_visible_artifacts': 4, 'unmapped_gap_artifacts': 99, 'malformed_or_unreadable_artifacts': 0}`.
- The package brief quoted `total discovered artifacts: 1281`; refreshed repo truth enumerates `1303` because current `origin/main` has more tracked audited artifacts. The unmapped gap count remains exactly `99`.
- Malformed / unreadable artifacts: `0`.

## Exact 99 Pre-Binding Gap Artifacts

1. `docs/research/PRICEONLY_SYNTHESIS_2026-06.md` - synthesis_or_report
2. `research/candidate_registry.jsonl` - candidate_or_crossing_evidence
3. `research/result_populations/RP-2134.result_population.json` - candidate_or_crossing_evidence
4. `research/result_populations/RP-2592.result_population.json` - candidate_or_crossing_evidence
5. `research/result_populations/RP-3731.result_population.json` - candidate_or_crossing_evidence
6. `research/result_populations/RP-4492.result_population.json` - candidate_or_crossing_evidence
7. `research/result_populations/RP-6236.result_population.json` - candidate_or_crossing_evidence
8. `research/result_populations/RP-6688.result_population.json` - candidate_or_crossing_evidence
9. `research/result_populations/RP-7134.result_population.json` - candidate_or_crossing_evidence
10. `research/result_populations/RP-7520.result_population.json` - candidate_or_crossing_evidence
11. `scratch/WP-RESEARCH-EDGE-SMA-FAMILY-01/blocked_bridge_reason.json` - blocked_or_no_go_evidence
12. `scratch/WP-RESEARCH-EDGE-SMA-FAMILY-01/blocked_candidate_review_reason.json` - blocked_or_no_go_evidence
13. `scratch/WP-RESEARCH-EDGE-SMA-FAMILY-01/blocked_robustness_reason.json` - blocked_or_no_go_evidence
14. `scratch/WP-RESEARCH-EDGE-SMA-FAMILY-01/blocked_sweep_plan_reason.json` - blocked_or_no_go_evidence
15. `scratch/WP-RESEARCH-EDGE-SMA-FAMILY-01/blocked_variant_manifest_reason.json` - blocked_or_no_go_evidence
16. `scratch/WP-RESEARCH-EDGE-SMA-FAMILY-01/denominator_audit.json` - requires_followup_mapping
17. `scratch/WP-RESEARCH-EDGE-SMA-FAMILY-01/formalizer_output_reference.json` - requires_followup_mapping
18. `scratch/WP-RESEARCH-EDGE-SMA-FAMILY-01/missing_diagnostics.json` - blocked_or_no_go_evidence
19. `scratch/WP-RESEARCH-EDGE-SMA-FAMILY-01/repo_truth_discovery.md` - requires_followup_mapping
20. `scratch/WP-RESEARCH-EDGE-SMA-FAMILY-01/sma_family_research_idea.json` - requires_followup_mapping
21. `scratch/WP-RESEARCH-EDGE-SMA-FAMILY-01/sma_family_result_packet.json` - candidate_or_crossing_evidence
22. `scratch/WP-RESEARCH-EDGE-SMA-FAMILY-01/sma_family_summary.md` - requires_followup_mapping
23. `scratch/WP-RESEARCH-EDGE-SMA-FAMILY-01/strategy_spec_reference.json` - requires_followup_mapping
24. `scratch/WP-RESEARCH-FUNDING-CARRY-01/blocked_bridge_reason.json` - blocked_or_no_go_evidence
25. `scratch/WP-RESEARCH-FUNDING-CARRY-01/blocked_formalizer_reason.json` - blocked_or_no_go_evidence
26. `scratch/WP-RESEARCH-FUNDING-CARRY-01/blocked_robustness_reason.json` - blocked_or_no_go_evidence
27. `scratch/WP-RESEARCH-FUNDING-CARRY-01/blocked_rp_replay_harness_reason.json` - blocked_or_no_go_evidence
28. `scratch/WP-RESEARCH-FUNDING-CARRY-01/blocked_runner_reason.json` - blocked_or_no_go_evidence
29. `scratch/WP-RESEARCH-FUNDING-CARRY-01/denominator_manifest.json` - requires_followup_mapping
30. `scratch/WP-RESEARCH-FUNDING-CARRY-01/funding_family_adapter_contract.json` - requires_followup_mapping
31. `scratch/WP-RESEARCH-FUNDING-CARRY-01/funding_pnl_boundary_note.json` - requires_followup_mapping
32. `scratch/WP-RESEARCH-FUNDING-CARRY-01/main_report_back_guardrail.txt` - requires_followup_mapping
33. `scratch/WP-RESEARCH-FUNDING-CARRY-01/no_candidate_review_packet_reason.json` - blocked_or_no_go_evidence
34. `scratch/WP-RESEARCH-FUNDING-CARRY-01/pre_registered_hypothesis.md` - requires_followup_mapping
35. `scratch/WP-RESEARCH-FUNDING-CARRY-01/repo_truth_discovery.md` - requires_followup_mapping
36. `scratch/WP-RESEARCH-FUNDING-CARRY-01/sweep_plan_summary.json` - requires_followup_mapping
37. `scratch/WP-RESEARCH-FUNDING-CARRY-01/validation_summary.txt` - requires_followup_mapping
38. `scratch/WP-RESEARCH-FUNDING-CARRY-02-FOLLOWUP-01/local_data_staging_report.json` - requires_followup_mapping
39. `scratch/WP-RESEARCH-FUNDING-CARRY-02-FOLLOWUP-01/repo_truth_data_contract.md` - requires_followup_mapping
40. `scratch/WP-RESEARCH-FUNDING-CARRY-02-FOLLOWUP-01/retry_decision.md` - requires_followup_mapping
41. `scratch/WP-RESEARCH-FUNDING-CARRY-02/bridge_output.json` - requires_followup_mapping
42. `scratch/WP-RESEARCH-FUNDING-CARRY-02/denominator_manifest.json` - requires_followup_mapping
43. `scratch/WP-RESEARCH-FUNDING-CARRY-02/formalizer_output.json` - requires_followup_mapping
44. `scratch/WP-RESEARCH-FUNDING-CARRY-02/funding_family_adapter_contract.json` - requires_followup_mapping
45. `scratch/WP-RESEARCH-FUNDING-CARRY-02/funding_pnl_boundary_note.json` - requires_followup_mapping
46. `scratch/WP-RESEARCH-FUNDING-CARRY-02/main_report_back_guardrail.txt` - requires_followup_mapping
47. `scratch/WP-RESEARCH-FUNDING-CARRY-02/metrics_summary.json` - requires_followup_mapping
48. `scratch/WP-RESEARCH-FUNDING-CARRY-02/monte_carlo/fixed/bootstrap_samples.sha256` - requires_followup_mapping
49. `scratch/WP-RESEARCH-FUNDING-CARRY-02/monte_carlo/fixed/seeded_advisory_mc_report.json` - requires_followup_mapping
50. `scratch/WP-RESEARCH-FUNDING-CARRY-02/monte_carlo/fixed/seeded_advisory_mc_report.md` - requires_followup_mapping
51. `scratch/WP-RESEARCH-FUNDING-CARRY-02/monte_carlo/midline/bootstrap_samples.sha256` - requires_followup_mapping
52. `scratch/WP-RESEARCH-FUNDING-CARRY-02/monte_carlo/midline/seeded_advisory_mc_report.json` - requires_followup_mapping
53. `scratch/WP-RESEARCH-FUNDING-CARRY-02/monte_carlo/midline/seeded_advisory_mc_report.md` - requires_followup_mapping
54. `scratch/WP-RESEARCH-FUNDING-CARRY-02/monte_carlo_summary.json` - requires_followup_mapping
55. `scratch/WP-RESEARCH-FUNDING-CARRY-02/no_candidate_review_packet_reason.json` - blocked_or_no_go_evidence
56. `scratch/WP-RESEARCH-FUNDING-CARRY-02/outputs/813c51adc1879144/denominator_ledger.json` - requires_followup_mapping
57. `scratch/WP-RESEARCH-FUNDING-CARRY-02/outputs/813c51adc1879144/fixed_max_hold_only/inputs/STRAT-SPEC-9478.strategy_spec.json` - requires_followup_mapping
58. `scratch/WP-RESEARCH-FUNDING-CARRY-02/outputs/813c51adc1879144/fixed_max_hold_only/inputs/SWEEP-PLAN-9933.sweep_plan.json` - requires_followup_mapping
59. `scratch/WP-RESEARCH-FUNDING-CARRY-02/outputs/813c51adc1879144/fixed_max_hold_only/inputs/VM-9933.variant_manifest.json` - requires_followup_mapping
60. `scratch/WP-RESEARCH-FUNDING-CARRY-02/outputs/813c51adc1879144/fixed_max_hold_only/inputs/bridge_metadata.json` - requires_followup_mapping
61. `scratch/WP-RESEARCH-FUNDING-CARRY-02/outputs/813c51adc1879144/fixed_max_hold_only/runner_artifacts/RP-2009.result_population.json` - candidate_or_crossing_evidence
62. `scratch/WP-RESEARCH-FUNDING-CARRY-02/outputs/813c51adc1879144/human_review_packet.json` - candidate_or_crossing_evidence
63. `scratch/WP-RESEARCH-FUNDING-CARRY-02/outputs/813c51adc1879144/midline_reversion_or_max_hold/inputs/STRAT-SPEC-9477.strategy_spec.json` - requires_followup_mapping
64. `scratch/WP-RESEARCH-FUNDING-CARRY-02/outputs/813c51adc1879144/midline_reversion_or_max_hold/inputs/SWEEP-PLAN-9934.sweep_plan.json` - requires_followup_mapping
65. `scratch/WP-RESEARCH-FUNDING-CARRY-02/outputs/813c51adc1879144/midline_reversion_or_max_hold/inputs/VM-9934.variant_manifest.json` - requires_followup_mapping
66. `scratch/WP-RESEARCH-FUNDING-CARRY-02/outputs/813c51adc1879144/midline_reversion_or_max_hold/inputs/bridge_metadata.json` - requires_followup_mapping
67. `scratch/WP-RESEARCH-FUNDING-CARRY-02/outputs/813c51adc1879144/midline_reversion_or_max_hold/runner_artifacts/RP-7592.result_population.json` - candidate_or_crossing_evidence
68. `scratch/WP-RESEARCH-FUNDING-CARRY-02/outputs/b191967d3aff/STRAT-SPEC-9477.strategy_spec.json` - requires_followup_mapping
69. `scratch/WP-RESEARCH-FUNDING-CARRY-02/outputs/b191967d3aff/STRAT-SPEC-9478.strategy_spec.json` - requires_followup_mapping
70. `scratch/WP-RESEARCH-FUNDING-CARRY-02/outputs/b191967d3aff/formalized_idea.json` - requires_followup_mapping
71. `scratch/WP-RESEARCH-FUNDING-CARRY-02/outputs/b191967d3aff/human_review_packet.json` - candidate_or_crossing_evidence
72. `scratch/WP-RESEARCH-FUNDING-CARRY-02/outputs/b191967d3aff/operator_bridge_approval.json` - requires_followup_mapping
73. `scratch/WP-RESEARCH-FUNDING-CARRY-02/pre_registered_hypothesis.md` - requires_followup_mapping
74. `scratch/WP-RESEARCH-FUNDING-CARRY-02/repo_truth_discovery.md` - requires_followup_mapping
75. `scratch/WP-RESEARCH-FUNDING-CARRY-02/robustness_fixed.json` - requires_followup_mapping
76. `scratch/WP-RESEARCH-FUNDING-CARRY-02/robustness_midline.json` - requires_followup_mapping
77. `scratch/WP-RESEARCH-FUNDING-CARRY-02/robustness_summary.json` - requires_followup_mapping
78. `scratch/WP-RESEARCH-FUNDING-CARRY-02/rp_replay_harness_report.json` - requires_followup_mapping
79. `scratch/WP-RESEARCH-FUNDING-CARRY-02/runner_result_summary.json` - requires_followup_mapping
80. `scratch/WP-RESEARCH-FUNDING-CARRY-02/sweep_plan_summary.json` - requires_followup_mapping
81. `scratch/WP-RESEARCH-FUNDING-CARRY-02/validation_summary.txt` - requires_followup_mapping
82. `scratch/WP-RESEARCH-FUNDING-CARRY-02/walk_forward_summary.json` - requires_followup_mapping
83. `scratch/WP-RESEARCH-ORB-EXIT-RESPEC-01/blocked_bridge_reason.json` - blocked_or_no_go_evidence
84. `scratch/WP-RESEARCH-ORB-EXIT-RESPEC-01/blocked_candidate_review_reason.json` - blocked_or_no_go_evidence
85. `scratch/WP-RESEARCH-ORB-EXIT-RESPEC-01/blocked_robustness_reason.json` - blocked_or_no_go_evidence
86. `scratch/WP-RESEARCH-ORB-EXIT-RESPEC-01/denominator_audit.json` - requires_followup_mapping
87. `scratch/WP-RESEARCH-ORB-EXIT-RESPEC-01/formalizer_output_reference.json` - requires_followup_mapping
88. `scratch/WP-RESEARCH-ORB-EXIT-RESPEC-01/missing_diagnostics.json` - blocked_or_no_go_evidence
89. `scratch/WP-RESEARCH-ORB-EXIT-RESPEC-01/orb_exit_respec_idea.json` - requires_followup_mapping
90. `scratch/WP-RESEARCH-ORB-EXIT-RESPEC-01/orb_exit_respec_result_packet.json` - candidate_or_crossing_evidence
91. `scratch/WP-RESEARCH-ORB-EXIT-RESPEC-01/orb_exit_respec_summary.md` - requires_followup_mapping
92. `scratch/WP-RESEARCH-ORB-EXIT-RESPEC-01/repo_truth_discovery.md` - requires_followup_mapping
93. `scratch/WP-RESEARCH-PRICEONLY-SYNTHESIS-01/evidence_index.json` - requires_followup_mapping
94. `scratch/WP-RESEARCH-PRICEONLY-SYNTHESIS-01/lab_gap_checklist.json` - requires_followup_mapping
95. `scratch/WP-RESEARCH-PRICEONLY-SYNTHESIS-01/main_report_back_guardrail.txt` - requires_followup_mapping
96. `scratch/WP-RESEARCH-PRICEONLY-SYNTHESIS-01/open_decision_surfaces.txt` - requires_followup_mapping
97. `scratch/WP-RESEARCH-PRICEONLY-SYNTHESIS-01/priceonly_synthesis_source_audit.json` - requires_followup_mapping
98. `scratch/WP-RESEARCH-PRICEONLY-SYNTHESIS-01/repo_truth_discovery.md` - requires_followup_mapping
99. `scratch/WP-RESEARCH-PRICEONLY-SYNTHESIS-01/validation_summary.txt` - requires_followup_mapping

## Classification

- Research conclusions / blocked-or-NO-GO evidence: `17`
- Result Populations / candidate registry / lifecycle evidence: `15`
- Synthesis/report artifacts: `1`
- Bundle/support artifacts that require explicit binding for denominator and provenance visibility: `66`

## Decision

- Every one of the 99 artifacts can be represented safely as read-only coordinator visibility: either as a stage artifact for a historical subject or as supplemental artifact drill-down on that subject.
- Non-bindable artifacts: `0`.
- No new state vocabulary is required; existing `no_go`, `blocked`, `experiment_complete`, `reported`, `oos_gate_fail`, and `not_started` stage states are sufficient.

## Binding Groups

- `canonical_registry_result_populations` -> `historical_canonical_evidence_bundle`: 9 artifact(s), overall `experiment_complete`.
- `edge_sma_family` -> `edge_sma_family_blocked`: 13 artifact(s), overall `blocked`.
- `funding_carry_01` -> `funding_carry_01_blocked_no_go`: 14 artifact(s), overall `no_go`.
- `funding_carry_02` -> `funding_carry_02_no_go`: 45 artifact(s), overall `no_go`.
- `orb_exit_respec` -> `orb_exit_respec_blocked`: 10 artifact(s), overall `blocked`.
- `priceonly_synthesis` -> `priceonly_synthesis_reported`: 8 artifact(s), overall `reported`.
