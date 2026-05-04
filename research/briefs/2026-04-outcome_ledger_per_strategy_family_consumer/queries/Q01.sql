WITH family_exp_sources AS (
    SELECT
        c.strategy_family,
        COUNT(DISTINCT CAST(ref_value AS VARCHAR)) AS source_exp_count
    FROM outcome_ledgers AS o
    JOIN candidates AS c
      ON o.candidate_id = c.candidate_id,
    UNNEST(o.linked_artifacts) AS refs(ref_value)
    WHERE CAST(ref_value AS VARCHAR) LIKE 'EXP-%'
    GROUP BY c.strategy_family
)
SELECT
    c.strategy_family,
    COUNT(DISTINCT o.candidate_id) AS candidate_count,
    COUNT(*) AS ol_row_count,
    COUNT(DISTINCT o.derivation_record.source_artifact_id) AS source_rep_count,
    COALESCE(e.source_exp_count, 0) AS source_exp_count,
    string_agg(DISTINCT o.pipeline_version, ' | ' ORDER BY o.pipeline_version) AS pipeline_versions,
    SUM(len(o.linked_advisory_artifacts)) AS advisory_link_count
FROM outcome_ledgers AS o
JOIN candidates AS c
  ON o.candidate_id = c.candidate_id
LEFT JOIN family_exp_sources AS e
  ON c.strategy_family = e.strategy_family
GROUP BY c.strategy_family, e.source_exp_count
ORDER BY
    ol_row_count DESC,
    candidate_count DESC,
    c.strategy_family
