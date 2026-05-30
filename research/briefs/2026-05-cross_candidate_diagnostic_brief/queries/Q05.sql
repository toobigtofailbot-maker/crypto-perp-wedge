SELECT
    f.strategy_family,
    f.timeframe,
    f.n_candidates,
    f.n_no_go,
    f.n_pass,
    f.n_conditional,
    f.n_inconclusive,
    STRING_AGG(o.candidate_id, ', ' ORDER BY o.candidate_id) AS candidate_ids
FROM v_candidate_by_family AS f
LEFT JOIN v_candidate_overview AS o
  ON f.strategy_family = o.strategy_family
 AND f.timeframe = o.timeframe
GROUP BY
    f.strategy_family,
    f.timeframe,
    f.n_candidates,
    f.n_no_go,
    f.n_pass,
    f.n_conditional,
    f.n_inconclusive
ORDER BY f.timeframe, f.strategy_family;
