-- Full discovered v_integrity_* sweep, represented as row counts per integrity view.
SELECT 'v_integrity_agent_output_refs' AS integrity_view, COUNT(*) AS issue_count FROM v_integrity_agent_output_refs
UNION ALL SELECT 'v_integrity_bucket_mapping_refs', COUNT(*) FROM v_integrity_bucket_mapping_refs
UNION ALL SELECT 'v_integrity_candidate_refs', COUNT(*) FROM v_integrity_candidate_refs
UNION ALL SELECT 'v_integrity_decision_refs', COUNT(*) FROM v_integrity_decision_refs
UNION ALL SELECT 'v_integrity_lifecycle_approval_completeness', COUNT(*) FROM v_integrity_lifecycle_approval_completeness
UNION ALL SELECT 'v_integrity_lifecycle_change_refs', COUNT(*) FROM v_integrity_lifecycle_change_refs
UNION ALL SELECT 'v_integrity_lifecycle_fast_track_completeness', COUNT(*) FROM v_integrity_lifecycle_fast_track_completeness
UNION ALL SELECT 'v_integrity_lifecycle_transition_graph', COUNT(*) FROM v_integrity_lifecycle_transition_graph
UNION ALL SELECT 'v_integrity_macro_window_agent_output_refs', COUNT(*) FROM v_integrity_macro_window_agent_output_refs
UNION ALL SELECT 'v_integrity_outcome_ledger_derivation', COUNT(*) FROM v_integrity_outcome_ledger_derivation
UNION ALL SELECT 'v_integrity_outcome_ledger_refs', COUNT(*) FROM v_integrity_outcome_ledger_refs
UNION ALL SELECT 'v_integrity_outcome_ledger_scope', COUNT(*) FROM v_integrity_outcome_ledger_scope
UNION ALL SELECT 'v_integrity_outcome_ledger_window_bounds', COUNT(*) FROM v_integrity_outcome_ledger_window_bounds
UNION ALL SELECT 'v_integrity_overlay_shadow_refs', COUNT(*) FROM v_integrity_overlay_shadow_refs
UNION ALL SELECT 'v_integrity_plan_report_pairs', COUNT(*) FROM v_integrity_plan_report_pairs
UNION ALL SELECT 'v_integrity_pre_gate_advisory_snapshot_refs', COUNT(*) FROM v_integrity_pre_gate_advisory_snapshot_refs
UNION ALL SELECT 'v_integrity_r2s_approval_candidate_refs', COUNT(*) FROM v_integrity_r2s_approval_candidate_refs
UNION ALL SELECT 'v_integrity_r2s_rec5_candidate_consistency', COUNT(*) FROM v_integrity_r2s_rec5_candidate_consistency
UNION ALL SELECT 'v_integrity_reconciliation_derivation', COUNT(*) FROM v_integrity_reconciliation_derivation
UNION ALL SELECT 'v_integrity_reconciliation_expectation_source', COUNT(*) FROM v_integrity_reconciliation_expectation_source
UNION ALL SELECT 'v_integrity_reconciliation_realized_metrics', COUNT(*) FROM v_integrity_reconciliation_realized_metrics
UNION ALL SELECT 'v_integrity_reconciliation_refs', COUNT(*) FROM v_integrity_reconciliation_refs
UNION ALL SELECT 'v_integrity_reconciliation_scope', COUNT(*) FROM v_integrity_reconciliation_scope
UNION ALL SELECT 'v_integrity_release_refs', COUNT(*) FROM v_integrity_release_refs
UNION ALL SELECT 'v_integrity_s2p_approval_candidate_refs', COUNT(*) FROM v_integrity_s2p_approval_candidate_refs
UNION ALL SELECT 'v_integrity_s2p_shadow_evidence_candidate_consistency', COUNT(*) FROM v_integrity_s2p_shadow_evidence_candidate_consistency
UNION ALL SELECT 'v_integrity_s2p_shadow_evidence_refs', COUNT(*) FROM v_integrity_s2p_shadow_evidence_refs
UNION ALL SELECT 'v_integrity_scope6_authority_flags', COUNT(*) FROM v_integrity_scope6_authority_flags
UNION ALL SELECT 'v_integrity_scope6_preservation_flags', COUNT(*) FROM v_integrity_scope6_preservation_flags
UNION ALL SELECT 'v_integrity_shadow_evidence_candidate_refs', COUNT(*) FROM v_integrity_shadow_evidence_candidate_refs
UNION ALL SELECT 'v_integrity_shadow_signal_summary_derivation', COUNT(*) FROM v_integrity_shadow_signal_summary_derivation
UNION ALL SELECT 'v_integrity_shadow_signal_summary_v2_derivation', COUNT(*) FROM v_integrity_shadow_signal_summary_v2_derivation
ORDER BY integrity_view;
