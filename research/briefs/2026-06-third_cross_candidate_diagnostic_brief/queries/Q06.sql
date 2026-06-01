-- Information-input coverage including ohlcv_15m and funding_8h.
SELECT
    information_input,
    COUNT(DISTINCT candidate_id) AS candidate_count,
    string_agg(DISTINCT candidate_id, ', ' ORDER BY candidate_id) AS candidate_ids,
    COUNT(DISTINCT candidate_id) FILTER (WHERE candidate_id = 'H-012') AS h012_rows
FROM v_information_inputs
GROUP BY information_input
ORDER BY candidate_count DESC, information_input;
