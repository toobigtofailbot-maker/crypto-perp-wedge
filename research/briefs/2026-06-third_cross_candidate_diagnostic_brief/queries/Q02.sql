-- Concluded candidate distribution by verdict, strategy family, and timeframe.
SELECT
    overall_verdict,
    strategy_family,
    timeframe,
    COUNT(*) AS concluded_candidate_count,
    string_agg(candidate_id, ', ' ORDER BY candidate_id) AS candidate_ids
FROM v_concluded_candidates
GROUP BY overall_verdict, strategy_family, timeframe
ORDER BY overall_verdict, strategy_family, timeframe;
