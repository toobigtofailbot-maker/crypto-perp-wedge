SELECT
    c.strategy_family,
    o.pipeline_version,
    COUNT(DISTINCT o.candidate_id) AS candidate_count,
    COUNT(*) AS ol_row_count,
    string_agg(DISTINCT o.candidate_id, ' | ' ORDER BY o.candidate_id) AS candidate_ids,
    string_agg(o.outcome_id, ' | ' ORDER BY o.outcome_id) AS outcome_ids,
    string_agg(DISTINCT o.derivation_record.source_artifact_id, ' | ' ORDER BY o.derivation_record.source_artifact_id) AS source_reps
FROM outcome_ledgers AS o
JOIN candidates AS c
  ON o.candidate_id = c.candidate_id
GROUP BY c.strategy_family, o.pipeline_version
ORDER BY
    c.strategy_family,
    CASE o.pipeline_version
        WHEN 'pre_wp_5b' THEN 1
        WHEN 'post_wp_5b' THEN 2
        ELSE 3
    END,
    o.pipeline_version
