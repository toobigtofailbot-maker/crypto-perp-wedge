SELECT
    table_name AS view_name,
    CASE
        WHEN table_name LIKE 'v_integrity_scope6_%'
          OR table_name LIKE 'v_integrity_r2s_%'
          OR table_name LIKE 'v_integrity_s2p_%'
          OR table_name = 'v_integrity_shadow_evidence_candidate_refs'
            THEN 'scope6_integrity'
        WHEN table_name IN (
            'v_r2s_approval_records',
            'v_shadow_evidence_retention',
            'v_s2p_approval_records',
            'v_scope6_candidate_packaging_overview',
            'v_s2p_shadow_evidence_links'
        )
            THEN 'scope6_base_or_link'
        WHEN table_name LIKE 'v_integrity_%'
            THEN 'integrity'
        ELSE 'other'
    END AS view_category,
    table_type
FROM information_schema.tables
WHERE table_schema = 'main'
  AND table_type = 'VIEW'
  AND table_name LIKE 'v\_%' ESCAPE '\'
ORDER BY view_category, view_name;
