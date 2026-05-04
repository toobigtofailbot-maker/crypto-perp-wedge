SELECT
    candidate_id,
    outcome_id,
    derivation_record.source_artifact_id AS source_rep,
    (
        SELECT string_agg(CAST(ref_value AS VARCHAR), ' | ' ORDER BY CAST(ref_value AS VARCHAR))
        FROM UNNEST(linked_artifacts) AS refs(ref_value)
        WHERE CAST(ref_value AS VARCHAR) LIKE 'EXP-%'
    ) AS source_exp,
    pipeline_version,
    metrics.sharpe AS sharpe,
    metrics.max_drawdown AS max_drawdown,
    metrics.n_obs AS n_obs,
    metrics.trades AS trades,
    metrics.gates_passed AS gates_passed,
    metrics.gates_total AS gates_total,
    derivation_record.derivation_method AS derivation_method,
    notes
FROM outcome_ledgers
WHERE candidate_id = 'H-004'
ORDER BY outcome_id;
