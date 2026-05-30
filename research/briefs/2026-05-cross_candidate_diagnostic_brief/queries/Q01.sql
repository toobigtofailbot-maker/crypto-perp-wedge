SELECT
    status,
    pipeline_stage,
    COUNT(*) AS candidate_count,
    STRING_AGG(candidate_id, ', ' ORDER BY candidate_id) AS candidate_ids
FROM v_candidate_overview
GROUP BY status, pipeline_stage
ORDER BY status, pipeline_stage;
