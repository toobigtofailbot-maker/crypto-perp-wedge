WITH verdict_distribution AS (
    SELECT
        'registry_verdict' AS row_type,
        overall_verdict AS bucket,
        CAST(NULL AS VARCHAR) AS sub_bucket,
        COUNT(*) AS candidate_count,
        CAST(NULL AS BIGINT) AS artifact_count,
        STRING_AGG(candidate_id, ', ' ORDER BY candidate_id) AS candidate_ids
    FROM v_concluded_candidates
    GROUP BY overall_verdict
),
outcome_distribution AS (
    SELECT
        'outcome_ledger' AS row_type,
        outcome_kind AS bucket,
        pipeline_version AS sub_bucket,
        COUNT(DISTINCT candidate_id) AS candidate_count,
        SUM(outcome_count) AS artifact_count,
        STRING_AGG(candidate_id, ', ' ORDER BY candidate_id) AS candidate_ids
    FROM v_outcome_ledger_candidate_pipeline_summary
    GROUP BY outcome_kind, pipeline_version
)
SELECT *
FROM verdict_distribution
UNION ALL
SELECT *
FROM outcome_distribution
ORDER BY row_type, bucket, sub_bucket;
