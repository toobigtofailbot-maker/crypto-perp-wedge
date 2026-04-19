SELECT
    candidate_id,
    name,
    strategy_family,
    timeframe,
    free_parameter_count,
    pipeline_stage,
    trial_id_count
FROM v_concluded_candidates
ORDER BY candidate_id;
