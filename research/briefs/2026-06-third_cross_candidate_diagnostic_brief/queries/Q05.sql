-- Strategy-family/timeframe coverage matrix including H-012 15m trend_following.
SELECT
    f.strategy_family,
    f.timeframe,
    f.n_candidates,
    f.n_no_go,
    f.n_pass,
    f.n_conditional,
    f.n_inconclusive,
    string_agg(c.candidate_id, ', ' ORDER BY c.candidate_id) AS candidate_ids,
    COUNT(*) FILTER (WHERE c.status = 'CONCLUDED') AS concluded_rows,
    COUNT(*) FILTER (WHERE c.status <> 'CONCLUDED') AS non_concluded_rows
FROM v_candidate_by_family AS f
JOIN v_candidate_overview AS c
  ON c.strategy_family = f.strategy_family
 AND c.timeframe = f.timeframe
GROUP BY
    f.strategy_family,
    f.timeframe,
    f.n_candidates,
    f.n_no_go,
    f.n_pass,
    f.n_conditional,
    f.n_inconclusive
ORDER BY f.strategy_family, f.timeframe;
