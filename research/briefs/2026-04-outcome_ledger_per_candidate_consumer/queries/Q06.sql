SELECT
    candidate_id,
    outcome_id,
    pipeline_version,
    metrics.sharpe AS sharpe,
    metrics.max_drawdown AS max_drawdown,
    metrics.n_obs AS n_obs,
    metrics.trades AS trades,
    metrics.hit_rate AS hit_rate,
    metrics.profit_factor AS profit_factor,
    metrics.final_equity AS final_equity,
    metrics.total_pnl AS total_pnl,
    metrics.gross_pnl AS gross_pnl,
    metrics.fees_paid AS fees_paid,
    metrics.slippage_paid AS slippage_paid,
    metrics.funding_paid AS funding_paid,
    metrics.cost_drag_fraction AS cost_drag_fraction,
    metrics.dsr AS dsr,
    metrics.walk_forward_efficiency AS walk_forward_efficiency,
    metrics.gates_passed AS gates_passed,
    metrics.gates_total AS gates_total
FROM outcome_ledgers
ORDER BY candidate_id, pipeline_version, outcome_id;
