SELECT
    gate_id,
    COUNT(*) AS n_candidates,
    SUM(CASE WHEN pass THEN 1 ELSE 0 END) AS n_pass,
    SUM(CASE WHEN pass THEN 0 ELSE 1 END) AS n_fail,
    STRING_AGG(candidate_id, ', ' ORDER BY candidate_id) FILTER (WHERE pass = false) AS failed_candidate_ids
FROM v_gate_results_flat
GROUP BY gate_id
ORDER BY gate_id;
