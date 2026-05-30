SELECT
    gate_id,
    COUNT(*) AS gate_result_count,
    COUNT(DISTINCT candidate_id) AS distinct_candidate_count,
    SUM(CASE WHEN pass THEN 1 ELSE 0 END) AS pass_count,
    SUM(CASE WHEN pass THEN 0 ELSE 1 END) AS fail_count,
    COUNT(DISTINCT candidate_id) FILTER (WHERE pass = false) AS distinct_failed_candidate_count,
    STRING_AGG(candidate_id, ', ' ORDER BY candidate_id) FILTER (WHERE pass = false)
        AS failed_candidate_ids
FROM v_gate_results_flat
GROUP BY gate_id
ORDER BY gate_id;
