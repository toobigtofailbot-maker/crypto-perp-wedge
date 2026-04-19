SELECT
    m.candidate_id,
    m.strategy_family,
    m.timeframe,
    m.oos_max_drawdown,
    g.threshold AS gate3_threshold,
    g.pass AS gate3_pass
FROM v_oos_metrics_by_candidate AS m
JOIN v_gate_results_flat AS g
  ON m.candidate_id = g.candidate_id
 AND m.report_id = g.report_id
WHERE g.gate_id LIKE 'D2-006-G3:%'
ORDER BY m.oos_max_drawdown DESC, m.candidate_id;
