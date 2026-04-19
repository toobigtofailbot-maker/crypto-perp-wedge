SELECT
    strategy_family,
    overall_verdict,
    COUNT(*) AS n_candidates
FROM v_concluded_candidates
GROUP BY strategy_family, overall_verdict
ORDER BY strategy_family, overall_verdict;
