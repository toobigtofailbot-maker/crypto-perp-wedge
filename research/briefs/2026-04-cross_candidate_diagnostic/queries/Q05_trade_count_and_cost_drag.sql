SELECT
    candidate_id,
    strategy_family,
    timeframe,
    oos_total_trades,
    oos_cost_drag,
    COUNT(*) OVER (PARTITION BY timeframe) AS timeframe_candidate_count,
    AVG(oos_total_trades) OVER (PARTITION BY timeframe) AS timeframe_avg_trades,
    AVG(oos_cost_drag) OVER (PARTITION BY timeframe) AS timeframe_avg_cost_drag
FROM v_oos_metrics_by_candidate
ORDER BY
    CASE timeframe
        WHEN '30m' THEN 1
        WHEN '1h' THEN 2
        WHEN '4h' THEN 3
        WHEN '1d' THEN 4
        ELSE 99
    END,
    candidate_id;
