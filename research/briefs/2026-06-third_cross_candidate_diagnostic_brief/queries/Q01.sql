-- Candidate inventory/status distribution with H-012 included.
WITH status_distribution AS (
    SELECT
        status,
        overall_verdict,
        pipeline_stage,
        COUNT(*) AS candidate_count,
        string_agg(candidate_id, ', ' ORDER BY candidate_id) AS candidate_ids
    FROM v_candidate_overview
    GROUP BY status, overall_verdict, pipeline_stage
)
SELECT
    'status_distribution' AS row_type,
    status,
    overall_verdict,
    pipeline_stage,
    candidate_count,
    candidate_ids,
    NULL AS candidate_id,
    NULL AS strategy_family,
    NULL AS timeframe,
    NULL AS decision_record_path,
    NULL AS trial_id_count
FROM status_distribution
UNION ALL
SELECT
    'candidate_inventory' AS row_type,
    status,
    overall_verdict,
    pipeline_stage,
    NULL AS candidate_count,
    NULL AS candidate_ids,
    candidate_id,
    strategy_family,
    timeframe,
    decision_record_path,
    trial_id_count
FROM v_candidate_overview
ORDER BY row_type DESC, status, overall_verdict, pipeline_stage, candidate_id;
