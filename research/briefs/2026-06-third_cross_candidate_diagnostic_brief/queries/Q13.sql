-- Query-layer footprint/current view count including integrity surfaces.
WITH view_names AS (
    SELECT table_name
    FROM information_schema.tables
    WHERE table_name LIKE 'v_%'
),
classified AS (
    SELECT
        table_name,
        CASE
            WHEN table_name LIKE 'v_integrity_%' THEN 'integrity'
            WHEN table_name IN (
                'v_r2s_approval_records',
                'v_shadow_evidence_retention',
                'v_s2p_approval_records',
                'v_s2p_shadow_evidence_links',
                'v_scope6_candidate_packaging_overview'
            ) THEN 'scope6_base_link'
            WHEN table_name LIKE '%candidate%' OR table_name LIKE '%experiment%' OR table_name LIKE '%gate%' OR table_name LIKE '%information%' THEN 'candidate_experiment'
            WHEN table_name LIKE '%outcome%' OR table_name LIKE '%reconciliation%' OR table_name LIKE '%decision%' OR table_name LIKE '%release%' OR table_name LIKE '%lifecycle%' OR table_name LIKE '%stage%' THEN 'lifecycle_evidence'
            WHEN table_name LIKE '%shadow%' OR table_name LIKE '%agent%' OR table_name LIKE '%bucket%' OR table_name LIKE '%macro%' OR table_name LIKE '%advisory%' THEN 'advisory_shadow'
            ELSE 'other'
        END AS view_category
    FROM view_names
)
SELECT
    view_category,
    COUNT(*) AS view_count,
    string_agg(table_name, ', ' ORDER BY table_name) AS view_names
FROM classified
GROUP BY view_category
UNION ALL
SELECT
    'total_v_views' AS view_category,
    COUNT(*) AS view_count,
    string_agg(table_name, ', ' ORDER BY table_name) AS view_names
FROM classified
ORDER BY view_category;
