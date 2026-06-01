-- H-012 artifact-chain and result summary from read-only query-layer views.
WITH h012_gate_counts AS (
    SELECT
        candidate_id,
        report_id,
        COUNT(*) FILTER (WHERE pass) AS gates_passed,
        COUNT(*) AS gates_total
    FROM v_gate_results_flat
    WHERE candidate_id = 'H-012'
      AND gate_id LIKE 'D2-006%'
    GROUP BY candidate_id, report_id
)
SELECT
    c.candidate_id,
    c.status,
    c.overall_verdict,
    c.pipeline_stage,
    c.strategy_family,
    c.timeframe,
    c.information_inputs,
    c.decision_record_path,
    p.plan_id,
    er.report_id,
    ol.outcome_id,
    rec.reconciliation_id,
    er.overall_verdict AS report_verdict,
    rec.overall_verdict AS reconciliation_verdict,
    CAST(json_extract(er.metrics, '$.out_of_sample.sharpe') AS DOUBLE) AS report_oos_sharpe,
    CAST(json_extract(er.metrics, '$.out_of_sample.max_drawdown') AS DOUBLE) AS report_oos_max_drawdown,
    CAST(json_extract(er.metrics, '$.out_of_sample.final_equity') AS DOUBLE) AS report_final_equity,
    CAST(json_extract(er.metrics, '$.out_of_sample.liquidated') AS BOOLEAN) AS report_liquidated,
    CAST(json_extract(er.metrics, '$.out_of_sample.trades') AS BIGINT) AS report_trades,
    gc.gates_passed AS report_gates_passed,
    gc.gates_total AS report_gates_total,
    CAST(json_extract(ol.metrics, '$.gates_passed') AS BIGINT) AS outcome_gates_passed,
    CAST(json_extract(ol.metrics, '$.gates_total') AS BIGINT) AS outcome_gates_total,
    rec.outcome_kind,
    rec.pipeline_version,
    rec.expectation_source_type
FROM candidates AS c
LEFT JOIN exp_plans AS p
  ON p.candidate_id = c.candidate_id
LEFT JOIN exp_reports AS er
  ON er.candidate_id = c.candidate_id
LEFT JOIN h012_gate_counts AS gc
  ON gc.candidate_id = er.candidate_id
 AND gc.report_id = er.report_id
LEFT JOIN outcome_ledgers AS ol
  ON ol.candidate_id = c.candidate_id
LEFT JOIN reconciliations AS rec
  ON rec.candidate_id = c.candidate_id
WHERE c.candidate_id = 'H-012';
