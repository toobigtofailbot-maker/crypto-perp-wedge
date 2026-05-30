SELECT
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
            THEN 'integrity_other'
        WHEN table_name LIKE 'v_shadow_%'
          OR table_name LIKE 'v_overlay_%'
          OR table_name LIKE 'v_pre_gate_%'
          OR table_name LIKE 'v_bucket_%'
          OR table_name LIKE 'v_agent_%'
          OR table_name LIKE 'v_macro_%'
            THEN 'advisory_shadow'
        WHEN table_name LIKE 'v_outcome_%'
          OR table_name LIKE 'v_reconciliation_%'
          OR table_name LIKE 'v_lifecycle_%'
          OR table_name LIKE 'v_decision_%'
          OR table_name LIKE 'v_release_%'
          OR table_name LIKE 'v_stage_%'
            THEN 'lifecycle_evidence'
        ELSE 'candidate_experiment'
    END AS footprint_category,
    COUNT(*) AS view_count,
    STRING_AGG(table_name, ', ' ORDER BY table_name) AS view_names
FROM information_schema.tables
WHERE table_schema = 'main'
  AND table_type = 'VIEW'
  AND table_name LIKE 'v\_%' ESCAPE '\'
GROUP BY footprint_category
ORDER BY footprint_category;
