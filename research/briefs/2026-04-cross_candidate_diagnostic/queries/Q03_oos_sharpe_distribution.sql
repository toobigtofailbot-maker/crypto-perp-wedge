SELECT
    m.candidate_id,
    m.strategy_family,
    m.timeframe,
    m.oos_sharpe,
    g.threshold AS gate1_threshold,
    g.pass AS gate1_pass
FROM v_oos_metrics_by_candidate AS m
JOIN v_gate_results_flat AS g
  ON m.candidate_id = g.candidate_id
 AND m.report_id = g.report_id
WHERE g.gate_id LIKE 'D2-006-G1:%'
ORDER BY m.oos_sharpe DESC, m.candidate_id;
