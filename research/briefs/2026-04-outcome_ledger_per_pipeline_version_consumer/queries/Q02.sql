SELECT
    pipeline_version,
    COUNT(DISTINCT candidate_id) AS candidate_count,
    string_agg(DISTINCT candidate_id, ' | ' ORDER BY candidate_id) AS candidate_ids,
    string_agg(outcome_id, ' | ' ORDER BY outcome_id) AS outcome_ids,
    string_agg(derivation_record.source_artifact_id, ' | ' ORDER BY outcome_id) AS source_reps,
    string_agg(
        (
            SELECT string_agg(CAST(ref_value AS VARCHAR), ' + ' ORDER BY CAST(ref_value AS VARCHAR))
            FROM UNNEST(linked_artifacts) AS refs(ref_value)
            WHERE CAST(ref_value AS VARCHAR) LIKE 'EXP-%'
        ),
        ' | '
        ORDER BY outcome_id
    ) AS source_exps
FROM outcome_ledgers
GROUP BY pipeline_version
ORDER BY
    CASE pipeline_version
        WHEN 'pre_wp_5b' THEN 1
        WHEN 'post_wp_5b' THEN 2
        ELSE 3
    END,
    pipeline_version;
