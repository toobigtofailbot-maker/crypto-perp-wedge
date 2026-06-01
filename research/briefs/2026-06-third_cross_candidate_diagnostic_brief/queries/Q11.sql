-- Scope 6 inventory/link views zero-instance behavior.
SELECT
    'v_scope6_candidate_packaging_overview' AS scope6_view,
    COUNT(*) AS row_count,
    SUM(r2s_approval_record_count) AS r2s_approval_record_count,
    SUM(shadow_evidence_retention_count) AS shadow_evidence_retention_count,
    SUM(s2p_approval_record_count) AS s2p_approval_record_count,
    COUNT(*) FILTER (WHERE has_r2s_approval_record) AS candidates_with_r2s,
    COUNT(*) FILTER (WHERE has_shadow_evidence_retention) AS candidates_with_shadow_evidence,
    COUNT(*) FILTER (WHERE has_s2p_approval_record) AS candidates_with_s2p
FROM v_scope6_candidate_packaging_overview
UNION ALL
SELECT
    'v_s2p_shadow_evidence_links' AS scope6_view,
    COUNT(*) AS row_count,
    NULL AS r2s_approval_record_count,
    NULL AS shadow_evidence_retention_count,
    NULL AS s2p_approval_record_count,
    NULL AS candidates_with_r2s,
    NULL AS candidates_with_shadow_evidence,
    NULL AS candidates_with_s2p
FROM v_s2p_shadow_evidence_links
ORDER BY scope6_view;
