SELECT
    strategy_family,
    timeframe,
    overall_verdict,
    COUNT(*) AS concluded_candidate_count,
    STRING_AGG(candidate_id, ', ' ORDER BY candidate_id) AS candidate_ids
FROM v_concluded_candidates
GROUP BY strategy_family, timeframe, overall_verdict
ORDER BY timeframe, strategy_family, overall_verdict;
