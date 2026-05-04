SELECT
    c.strategy_family,
    o.candidate_id,
    o.outcome_id,
    o.pipeline_version,
    o.derivation_record.source_artifact_id AS source_rep,
    (
        SELECT string_agg(CAST(ref_value AS VARCHAR), ' | ' ORDER BY CAST(ref_value AS VARCHAR))
        FROM UNNEST(o.linked_artifacts) AS refs(ref_value)
        WHERE CAST(ref_value AS VARCHAR) LIKE 'EXP-%'
    ) AS source_exp,
    len(o.linked_artifacts) AS linked_artifact_count,
    len(o.linked_advisory_artifacts) AS linked_advisory_artifact_count,
    o.metrics.sharpe AS sharpe,
    o.metrics.max_drawdown AS max_drawdown,
    o.metrics.n_obs AS n_obs,
    o.metrics.trades AS trades,
    o.metrics.hit_rate AS hit_rate,
    o.metrics.profit_factor AS profit_factor,
    o.metrics.final_equity AS final_equity,
    o.metrics.total_pnl AS total_pnl,
    o.metrics.gross_pnl AS gross_pnl,
    o.metrics.fees_paid AS fees_paid,
    o.metrics.slippage_paid AS slippage_paid,
    o.metrics.funding_paid AS funding_paid,
    o.metrics.cost_drag_fraction AS cost_drag_fraction,
    o.metrics.dsr AS dsr,
    o.metrics.walk_forward_efficiency AS walk_forward_efficiency,
    o.metrics.gates_passed AS gates_passed,
    o.metrics.gates_total AS gates_total
FROM outcome_ledgers AS o
JOIN candidates AS c
  ON o.candidate_id = c.candidate_id
ORDER BY
    c.strategy_family,
    o.candidate_id,
    CASE o.pipeline_version
        WHEN 'pre_wp_5b' THEN 1
        WHEN 'post_wp_5b' THEN 2
        ELSE 3
    END,
    o.pipeline_version,
    o.outcome_id
