-- Scope 6 integrity views zero rows.
SELECT 'v_integrity_r2s_approval_candidate_refs' AS integrity_view, COUNT(*) AS issue_count FROM v_integrity_r2s_approval_candidate_refs
UNION ALL SELECT 'v_integrity_r2s_rec5_candidate_consistency', COUNT(*) FROM v_integrity_r2s_rec5_candidate_consistency
UNION ALL SELECT 'v_integrity_s2p_approval_candidate_refs', COUNT(*) FROM v_integrity_s2p_approval_candidate_refs
UNION ALL SELECT 'v_integrity_s2p_shadow_evidence_candidate_consistency', COUNT(*) FROM v_integrity_s2p_shadow_evidence_candidate_consistency
UNION ALL SELECT 'v_integrity_s2p_shadow_evidence_refs', COUNT(*) FROM v_integrity_s2p_shadow_evidence_refs
UNION ALL SELECT 'v_integrity_scope6_authority_flags', COUNT(*) FROM v_integrity_scope6_authority_flags
UNION ALL SELECT 'v_integrity_scope6_preservation_flags', COUNT(*) FROM v_integrity_scope6_preservation_flags
UNION ALL SELECT 'v_integrity_shadow_evidence_candidate_refs', COUNT(*) FROM v_integrity_shadow_evidence_candidate_refs
ORDER BY integrity_view;
