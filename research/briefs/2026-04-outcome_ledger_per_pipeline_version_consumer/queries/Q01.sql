WITH exp_sources AS (
    SELECT
        pipeline_version,
        COUNT(DISTINCT CAST(ref_value AS VARCHAR)) AS source_exp_count
    FROM outcome_ledgers,
    UNNEST(linked_artifacts) AS refs(ref_value)
    WHERE CAST(ref_value AS VARCHAR) LIKE 'EXP-%'
    GROUP BY pipeline_version
)
SELECT
    o.pipeline_version,
    COUNT(*) AS ol_row_count,
    COUNT(DISTINCT o.candidate_id) AS candidate_count,
    COUNT(DISTINCT o.derivation_record.source_artifact_id) AS source_rep_count,
    COALESCE(e.source_exp_count, 0) AS source_exp_count,
    SUM(len(o.linked_advisory_artifacts)) AS advisory_link_count
FROM outcome_ledgers AS o
LEFT JOIN exp_sources AS e
  ON o.pipeline_version = e.pipeline_version
GROUP BY o.pipeline_version, e.source_exp_count
ORDER BY
    CASE o.pipeline_version
        WHEN 'pre_wp_5b' THEN 1
        WHEN 'post_wp_5b' THEN 2
        ELSE 3
    END,
    o.pipeline_version;
