SELECT
    pipeline_version,
    candidate_id,
    outcome_id,
    derivation_record.source_artifact_id AS source_rep,
    (
        SELECT string_agg(CAST(ref_value AS VARCHAR), ' | ' ORDER BY CAST(ref_value AS VARCHAR))
        FROM UNNEST(linked_artifacts) AS refs(ref_value)
        WHERE CAST(ref_value AS VARCHAR) LIKE 'EXP-%'
    ) AS source_exp,
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
ORDER BY
    CASE pipeline_version
        WHEN 'pre_wp_5b' THEN 1
        WHEN 'post_wp_5b' THEN 2
        ELSE 3
    END,
    pipeline_version,
    candidate_id,
    outcome_id;
