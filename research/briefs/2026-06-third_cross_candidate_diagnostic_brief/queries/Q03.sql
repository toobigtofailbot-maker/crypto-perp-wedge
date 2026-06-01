-- Diff snapshot versus the WP-S2c-119-era ten-concluded-candidate state.
WITH current_counts AS (
    SELECT
        COUNT(*) FILTER (WHERE status = 'CONCLUDED') AS current_concluded_candidates,
        COUNT(*) FILTER (WHERE candidate_id = 'H-012' AND status = 'CONCLUDED') AS h012_concluded_rows,
        COUNT(*) FILTER (WHERE candidate_id = 'H-011' AND status = 'DRAFT') AS h011_draft_rows
    FROM v_candidate_overview
),
h012 AS (
    SELECT
        c.candidate_id,
        c.status,
        c.overall_verdict,
        c.pipeline_stage,
        c.strategy_family,
        c.timeframe,
        c.decision_record_path,
        e.plan_id,
        e.report_id,
        o.outcome_id,
        r.reconciliation_id
    FROM v_candidate_overview AS c
    LEFT JOIN v_experiment_instances AS e
      ON e.candidate_id = c.candidate_id
    LEFT JOIN v_outcome_ledger_overview AS o
      ON o.candidate_id = c.candidate_id
    LEFT JOIN v_reconciliation_overview AS r
      ON r.candidate_id = c.candidate_id
    WHERE c.candidate_id = 'H-012'
)
SELECT
    'wp_s2c_119_reference_concluded_count' AS metric,
    10 AS numeric_value,
    NULL AS text_value
UNION ALL
SELECT
    'current_concluded_candidate_count' AS metric,
    current_concluded_candidates AS numeric_value,
    NULL AS text_value
FROM current_counts
UNION ALL
SELECT
    'concluded_candidate_delta_since_wp_s2c_119' AS metric,
    current_concluded_candidates - 10 AS numeric_value,
    NULL AS text_value
FROM current_counts
UNION ALL
SELECT
    'h011_reserved_draft_rows' AS metric,
    h011_draft_rows AS numeric_value,
    NULL AS text_value
FROM current_counts
UNION ALL
SELECT
    'h012_concluded_rows' AS metric,
    h012_concluded_rows AS numeric_value,
    NULL AS text_value
FROM current_counts
UNION ALL
SELECT
    'h012_artifact_chain' AS metric,
    NULL AS numeric_value,
    concat(
        candidate_id, ' | ', status, ' | ', overall_verdict, ' | ', pipeline_stage,
        ' | ', strategy_family, ' | ', timeframe,
        ' | ', plan_id, ' | ', report_id, ' | ', outcome_id, ' | ',
        reconciliation_id, ' | ', decision_record_path
    ) AS text_value
FROM h012;
