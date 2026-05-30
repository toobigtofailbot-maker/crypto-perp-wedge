SELECT 'v_integrity_r2s_approval_candidate_refs' AS integrity_view, to_json(i) AS issue_json FROM v_integrity_r2s_approval_candidate_refs AS i
UNION ALL
SELECT 'v_integrity_shadow_evidence_candidate_refs' AS integrity_view, to_json(i) AS issue_json FROM v_integrity_shadow_evidence_candidate_refs AS i
UNION ALL
SELECT 'v_integrity_s2p_approval_candidate_refs' AS integrity_view, to_json(i) AS issue_json FROM v_integrity_s2p_approval_candidate_refs AS i
UNION ALL
SELECT 'v_integrity_r2s_rec5_candidate_consistency' AS integrity_view, to_json(i) AS issue_json FROM v_integrity_r2s_rec5_candidate_consistency AS i
UNION ALL
SELECT 'v_integrity_s2p_shadow_evidence_refs' AS integrity_view, to_json(i) AS issue_json FROM v_integrity_s2p_shadow_evidence_refs AS i
UNION ALL
SELECT 'v_integrity_s2p_shadow_evidence_candidate_consistency' AS integrity_view, to_json(i) AS issue_json FROM v_integrity_s2p_shadow_evidence_candidate_consistency AS i
UNION ALL
SELECT 'v_integrity_scope6_authority_flags' AS integrity_view, to_json(i) AS issue_json FROM v_integrity_scope6_authority_flags AS i
UNION ALL
SELECT 'v_integrity_scope6_preservation_flags' AS integrity_view, to_json(i) AS issue_json FROM v_integrity_scope6_preservation_flags AS i
ORDER BY integrity_view;
