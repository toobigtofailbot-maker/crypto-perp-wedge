SELECT
    'v_r2s_approval_records' AS scope6_view,
    COUNT(*) AS row_count
FROM v_r2s_approval_records
UNION ALL
SELECT
    'v_shadow_evidence_retention' AS scope6_view,
    COUNT(*) AS row_count
FROM v_shadow_evidence_retention
UNION ALL
SELECT
    'v_s2p_approval_records' AS scope6_view,
    COUNT(*) AS row_count
FROM v_s2p_approval_records
ORDER BY scope6_view;
