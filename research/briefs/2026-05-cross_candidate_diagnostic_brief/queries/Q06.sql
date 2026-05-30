SELECT
    information_input,
    COUNT(DISTINCT candidate_id) AS candidate_count,
    STRING_AGG(candidate_id, ', ' ORDER BY candidate_id) AS candidate_ids
FROM v_information_inputs
GROUP BY information_input
ORDER BY candidate_count DESC, information_input;
