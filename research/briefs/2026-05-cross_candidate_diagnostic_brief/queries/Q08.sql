SELECT 'v_integrity_agent_output_refs' AS integrity_view, to_json(i) AS issue_json FROM v_integrity_agent_output_refs AS i
UNION ALL
SELECT 'v_integrity_bucket_mapping_refs' AS integrity_view, to_json(i) AS issue_json FROM v_integrity_bucket_mapping_refs AS i
UNION ALL
SELECT 'v_integrity_candidate_refs' AS integrity_view, to_json(i) AS issue_json FROM v_integrity_candidate_refs AS i
UNION ALL
SELECT 'v_integrity_decision_refs' AS integrity_view, to_json(i) AS issue_json FROM v_integrity_decision_refs AS i
UNION ALL
SELECT 'v_integrity_lifecycle_approval_completeness' AS integrity_view, to_json(i) AS issue_json FROM v_integrity_lifecycle_approval_completeness AS i
UNION ALL
SELECT 'v_integrity_lifecycle_change_refs' AS integrity_view, to_json(i) AS issue_json FROM v_integrity_lifecycle_change_refs AS i
UNION ALL
SELECT 'v_integrity_lifecycle_fast_track_completeness' AS integrity_view, to_json(i) AS issue_json FROM v_integrity_lifecycle_fast_track_completeness AS i
UNION ALL
SELECT 'v_integrity_lifecycle_transition_graph' AS integrity_view, to_json(i) AS issue_json FROM v_integrity_lifecycle_transition_graph AS i
UNION ALL
SELECT 'v_integrity_macro_window_agent_output_refs' AS integrity_view, to_json(i) AS issue_json FROM v_integrity_macro_window_agent_output_refs AS i
UNION ALL
SELECT 'v_integrity_outcome_ledger_derivation' AS integrity_view, to_json(i) AS issue_json FROM v_integrity_outcome_ledger_derivation AS i
UNION ALL
SELECT 'v_integrity_outcome_ledger_refs' AS integrity_view, to_json(i) AS issue_json FROM v_integrity_outcome_ledger_refs AS i
UNION ALL
SELECT 'v_integrity_outcome_ledger_scope' AS integrity_view, to_json(i) AS issue_json FROM v_integrity_outcome_ledger_scope AS i
UNION ALL
SELECT 'v_integrity_outcome_ledger_window_bounds' AS integrity_view, to_json(i) AS issue_json FROM v_integrity_outcome_ledger_window_bounds AS i
UNION ALL
SELECT 'v_integrity_overlay_shadow_refs' AS integrity_view, to_json(i) AS issue_json FROM v_integrity_overlay_shadow_refs AS i
UNION ALL
SELECT 'v_integrity_plan_report_pairs' AS integrity_view, to_json(i) AS issue_json FROM v_integrity_plan_report_pairs AS i
UNION ALL
SELECT 'v_integrity_pre_gate_advisory_snapshot_refs' AS integrity_view, to_json(i) AS issue_json FROM v_integrity_pre_gate_advisory_snapshot_refs AS i
UNION ALL
SELECT 'v_integrity_r2s_approval_candidate_refs' AS integrity_view, to_json(i) AS issue_json FROM v_integrity_r2s_approval_candidate_refs AS i
UNION ALL
SELECT 'v_integrity_r2s_rec5_candidate_consistency' AS integrity_view, to_json(i) AS issue_json FROM v_integrity_r2s_rec5_candidate_consistency AS i
UNION ALL
SELECT 'v_integrity_reconciliation_derivation' AS integrity_view, to_json(i) AS issue_json FROM v_integrity_reconciliation_derivation AS i
UNION ALL
SELECT 'v_integrity_reconciliation_expectation_source' AS integrity_view, to_json(i) AS issue_json FROM v_integrity_reconciliation_expectation_source AS i
UNION ALL
SELECT 'v_integrity_reconciliation_realized_metrics' AS integrity_view, to_json(i) AS issue_json FROM v_integrity_reconciliation_realized_metrics AS i
UNION ALL
SELECT 'v_integrity_reconciliation_refs' AS integrity_view, to_json(i) AS issue_json FROM v_integrity_reconciliation_refs AS i
UNION ALL
SELECT 'v_integrity_reconciliation_scope' AS integrity_view, to_json(i) AS issue_json FROM v_integrity_reconciliation_scope AS i
UNION ALL
SELECT 'v_integrity_release_refs' AS integrity_view, to_json(i) AS issue_json FROM v_integrity_release_refs AS i
UNION ALL
SELECT 'v_integrity_s2p_approval_candidate_refs' AS integrity_view, to_json(i) AS issue_json FROM v_integrity_s2p_approval_candidate_refs AS i
UNION ALL
SELECT 'v_integrity_s2p_shadow_evidence_candidate_consistency' AS integrity_view, to_json(i) AS issue_json FROM v_integrity_s2p_shadow_evidence_candidate_consistency AS i
UNION ALL
SELECT 'v_integrity_s2p_shadow_evidence_refs' AS integrity_view, to_json(i) AS issue_json FROM v_integrity_s2p_shadow_evidence_refs AS i
UNION ALL
SELECT 'v_integrity_scope6_authority_flags' AS integrity_view, to_json(i) AS issue_json FROM v_integrity_scope6_authority_flags AS i
UNION ALL
SELECT 'v_integrity_scope6_preservation_flags' AS integrity_view, to_json(i) AS issue_json FROM v_integrity_scope6_preservation_flags AS i
UNION ALL
SELECT 'v_integrity_shadow_evidence_candidate_refs' AS integrity_view, to_json(i) AS issue_json FROM v_integrity_shadow_evidence_candidate_refs AS i
UNION ALL
SELECT 'v_integrity_shadow_signal_summary_derivation' AS integrity_view, to_json(i) AS issue_json FROM v_integrity_shadow_signal_summary_derivation AS i
UNION ALL
SELECT 'v_integrity_shadow_signal_summary_v2_derivation' AS integrity_view, to_json(i) AS issue_json FROM v_integrity_shadow_signal_summary_v2_derivation AS i
ORDER BY integrity_view;
