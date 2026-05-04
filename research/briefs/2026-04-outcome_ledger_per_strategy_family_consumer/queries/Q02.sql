SELECT
    c.strategy_family,
    string_agg(DISTINCT o.candidate_id, ' | ' ORDER BY o.candidate_id) AS candidate_ids,
    string_agg(o.outcome_id, ' | ' ORDER BY o.outcome_id) AS outcome_ids,
    string_agg(DISTINCT o.derivation_record.source_artifact_id, ' | ' ORDER BY o.derivation_record.source_artifact_id) AS source_reps,
    (
        SELECT string_agg(DISTINCT CAST(ref_value AS VARCHAR), ' | ' ORDER BY CAST(ref_value AS VARCHAR))
        FROM outcome_ledgers AS inner_o,
        UNNEST(inner_o.linked_artifacts) AS refs(ref_value)
        WHERE inner_o.candidate_id IN (
            SELECT candidate_id
            FROM outcome_ledgers AS family_o
            WHERE family_o.outcome_id IN (
                SELECT scoped_o.outcome_id
                FROM outcome_ledgers AS scoped_o
                JOIN candidates AS scoped_c
                  ON scoped_o.candidate_id = scoped_c.candidate_id
                WHERE scoped_c.strategy_family = c.strategy_family
            )
        )
          AND CAST(ref_value AS VARCHAR) LIKE 'EXP-%'
    ) AS source_exps,
    string_agg(DISTINCT o.pipeline_version, ' | ' ORDER BY o.pipeline_version) AS pipeline_versions
FROM outcome_ledgers AS o
JOIN candidates AS c
  ON o.candidate_id = c.candidate_id
GROUP BY c.strategy_family
ORDER BY
    COUNT(*) DESC,
    COUNT(DISTINCT o.candidate_id) DESC,
    c.strategy_family
