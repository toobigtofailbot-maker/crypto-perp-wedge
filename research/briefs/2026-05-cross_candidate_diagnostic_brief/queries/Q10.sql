SELECT
    'v_scope6_candidate_packaging_overview' AS scope6_view,
    COUNT(*) AS row_count,
    SUM(r2s_approval_record_count) AS r2s_approval_record_count,
    SUM(shadow_evidence_retention_count) AS shadow_evidence_retention_count,
    SUM(s2p_approval_record_count) AS s2p_approval_record_count
FROM v_scope6_candidate_packaging_overview
UNION ALL
SELECT
    'v_s2p_shadow_evidence_links' AS scope6_view,
    COUNT(*) AS row_count,
    CAST(NULL AS HUGEINT) AS r2s_approval_record_count,
    CAST(NULL AS HUGEINT) AS shadow_evidence_retention_count,
    CAST(NULL AS HUGEINT) AS s2p_approval_record_count
FROM v_s2p_shadow_evidence_links
ORDER BY scope6_view;
