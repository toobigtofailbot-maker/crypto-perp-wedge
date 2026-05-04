WITH exp_sources AS (
    SELECT
        COUNT(DISTINCT CAST(ref_value AS VARCHAR)) AS source_exp_count
    FROM outcome_ledgers,
    UNNEST(linked_artifacts) AS refs(ref_value)
    WHERE CAST(ref_value AS VARCHAR) LIKE 'EXP-%'
)
SELECT
    COUNT(*) AS ol_row_count,
    COUNT(DISTINCT o.candidate_id) AS candidate_count,
    COUNT(DISTINCT o.derivation_record.source_artifact_id) AS source_rep_count,
    COALESCE(e.source_exp_count, 0) AS source_exp_count,
    COUNT(DISTINCT o.pipeline_version) AS pipeline_version_count,
    COUNT(DISTINCT c.strategy_family) AS strategy_family_count,
    SUM(CASE WHEN o.pipeline_version = 'pre_wp_5b' THEN 1 ELSE 0 END) AS pre_wp_5b_count,
    SUM(CASE WHEN o.pipeline_version = 'post_wp_5b' THEN 1 ELSE 0 END) AS post_wp_5b_count,
    SUM(list_count(o.linked_advisory_artifacts)) AS advisory_link_count
FROM outcome_ledgers AS o
JOIN candidates AS c
  ON o.candidate_id = c.candidate_id
CROSS JOIN exp_sources AS e
GROUP BY e.source_exp_count
