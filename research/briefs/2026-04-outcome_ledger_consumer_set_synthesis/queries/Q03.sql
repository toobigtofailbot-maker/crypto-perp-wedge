WITH exp_refs AS (
    SELECT
        o.outcome_id,
        string_agg(DISTINCT CAST(ref_value AS VARCHAR), ' | ' ORDER BY CAST(ref_value AS VARCHAR)) AS source_exps
    FROM outcome_ledgers AS o,
    UNNEST(o.linked_artifacts) AS refs(ref_value)
    WHERE o.candidate_id = 'H-004'
      AND CAST(ref_value AS VARCHAR) LIKE 'EXP-%'
    GROUP BY o.outcome_id
)
SELECT
    o.candidate_id,
    c.strategy_family,
    string_agg(o.outcome_id, ' | ' ORDER BY o.outcome_id) AS outcome_ids,
    string_agg(CAST(o.derivation_record.source_artifact_id AS VARCHAR), ' | ' ORDER BY CAST(o.derivation_record.source_artifact_id AS VARCHAR)) AS source_reps,
    string_agg(e.source_exps, ' | ' ORDER BY e.source_exps) AS source_exps,
    string_agg(
        o.pipeline_version,
        ' | '
        ORDER BY
            CASE o.pipeline_version
                WHEN 'pre_wp_5b' THEN 1
                WHEN 'post_wp_5b' THEN 2
                ELSE 3
            END,
            o.pipeline_version
    ) AS pipeline_versions,
    'only current two-entry candidate in the per-candidate axis' AS candidate_axis_role,
    'only current cross-pipeline candidate and only post_wp_5b contributor' AS pipeline_axis_role,
    'trend_following split contributor across pre_wp_5b and post_wp_5b' AS strategy_family_axis_role,
    'structural exception only; no improvement, degradation, comparability, recommendation, or promotion claim' AS inference_boundary
FROM outcome_ledgers AS o
JOIN candidates AS c
  ON o.candidate_id = c.candidate_id
LEFT JOIN exp_refs AS e
  ON o.outcome_id = e.outcome_id
WHERE o.candidate_id = 'H-004'
GROUP BY o.candidate_id, c.strategy_family
