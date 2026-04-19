SELECT
    information_input,
    COUNT(DISTINCT candidate_id) AS n_candidates,
    STRING_AGG(candidate_id, ', ' ORDER BY candidate_id) AS candidate_ids
FROM v_information_inputs
GROUP BY information_input
ORDER BY n_candidates DESC, information_input;
