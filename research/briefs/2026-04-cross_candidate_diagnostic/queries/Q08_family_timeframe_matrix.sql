SELECT
    strategy_family,
    timeframe,
    COUNT(*) AS n_registry_rows,
    SUM(CASE WHEN status = 'CONCLUDED' THEN 1 ELSE 0 END) AS n_concluded_baselines,
    SUM(CASE WHEN status <> 'CONCLUDED' THEN 1 ELSE 0 END) AS n_non_concluded_slots,
    STRING_AGG(candidate_id, ', ' ORDER BY candidate_id) AS candidate_ids
FROM v_candidate_overview
GROUP BY strategy_family, timeframe
ORDER BY timeframe, strategy_family;
