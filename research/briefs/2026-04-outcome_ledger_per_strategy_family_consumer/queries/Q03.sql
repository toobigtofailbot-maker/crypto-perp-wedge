WITH family_summary AS (
    SELECT
        c.strategy_family,
        COUNT(DISTINCT o.candidate_id) AS candidate_count,
        COUNT(*) AS ol_row_count,
        string_agg(DISTINCT o.candidate_id, ' | ' ORDER BY o.candidate_id) AS candidate_ids,
        string_agg(o.outcome_id, ' | ' ORDER BY o.outcome_id) AS outcome_ids,
        string_agg(DISTINCT o.derivation_record.source_artifact_id, ' | ' ORDER BY o.derivation_record.source_artifact_id) AS source_reps,
        string_agg(DISTINCT o.pipeline_version, ' | ' ORDER BY o.pipeline_version) AS pipeline_versions
    FROM outcome_ledgers AS o
    JOIN candidates AS c
      ON o.candidate_id = c.candidate_id
    GROUP BY c.strategy_family
)
SELECT
    strategy_family,
    candidate_count,
    ol_row_count,
    candidate_ids,
    outcome_ids,
    source_reps,
    pipeline_versions,
    'multi-entry structural family; not a ranking or performance conclusion' AS structural_note
FROM family_summary
WHERE candidate_count > 1
   OR ol_row_count > 1
ORDER BY
    ol_row_count DESC,
    candidate_count DESC,
    strategy_family
