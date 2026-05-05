WITH d2_rows AS (
    SELECT *
    FROM reconciliations
    WHERE expectation_source_type = 'd2_006_gates'
),
expected_metrics AS (
    SELECT
        r.reconciliation_id,
        e.metric_name
    FROM d2_rows AS r,
    UNNEST(r.expectation_extracted.metric_expectations) AS t(e)
),
comparison_metrics AS (
    SELECT
        r.reconciliation_id,
        c.metric_name,
        c.comparison_verdict
    FROM d2_rows AS r,
    UNNEST(r.comparison.metric_comparisons) AS t(c)
)
SELECT
    r.reconciliation_id,
    r.outcome_id,
    r.candidate_id,
    r.pipeline_version,
    r.overall_verdict,
    r.realized_metrics.gross_pnl AS gross_pnl,
    list_sort(list_distinct(list(e.metric_name))) AS extracted_metric_names,
    (
        SELECT list(
            struct_pack(
                metric_name := metric_name,
                comparison_verdict := comparison_verdict
            )
            ORDER BY metric_name
        )
        FROM comparison_metrics AS c
        WHERE c.reconciliation_id = r.reconciliation_id
    ) AS compared_metrics,
    EXISTS (
        SELECT 1
        FROM comparison_metrics AS c
        WHERE c.reconciliation_id = r.reconciliation_id
          AND c.metric_name = 'cost_drag_fraction'
    ) AS cost_drag_compared,
    r.realized_metrics.gross_pnl <= 0
      AND EXISTS (
          SELECT 1
          FROM comparison_metrics AS c
          WHERE c.reconciliation_id = r.reconciliation_id
            AND c.metric_name = 'cost_drag_fraction'
      ) AS cost_drag_compared_with_non_positive_gross_pnl,
    r.realized_metrics.gross_pnl <= 0
      AND NOT EXISTS (
          SELECT 1
          FROM comparison_metrics AS c
          WHERE c.reconciliation_id = r.reconciliation_id
            AND c.metric_name = 'cost_drag_fraction'
      ) AS cost_drag_skipped_due_to_non_positive_gross_pnl,
    CASE
        WHEN r.realized_metrics.gross_pnl <= 0
          AND EXISTS (
              SELECT 1
              FROM comparison_metrics AS c
              WHERE c.reconciliation_id = r.reconciliation_id
                AND c.metric_name = 'cost_drag_fraction'
          )
        THEN 'compared_despite_non_positive_gross_pnl_pre_wp10c_seed_requires_followup'
        WHEN r.realized_metrics.gross_pnl <= 0
          AND NOT EXISTS (
              SELECT 1
              FROM comparison_metrics AS c
              WHERE c.reconciliation_id = r.reconciliation_id
                AND c.metric_name = 'cost_drag_fraction'
          )
        THEN 'skipped_due_to_non_positive_gross_pnl'
        ELSE 'compared_with_positive_gross_pnl'
    END AS cost_drag_non_positive_gross_pnl_posture,
    EXISTS (
        SELECT 1
        FROM comparison_metrics AS c
        WHERE c.reconciliation_id = r.reconciliation_id
          AND c.metric_name = 'sensitivity_min_ratio'
    ) AS sensitivity_min_ratio_compared,
    EXISTS (
        SELECT 1
        FROM expected_metrics AS e2
        WHERE e2.reconciliation_id = r.reconciliation_id
          AND e2.metric_name = 'pnl_concentration_90d'
    )
      AND NOT EXISTS (
          SELECT 1
          FROM comparison_metrics AS c
          WHERE c.reconciliation_id = r.reconciliation_id
            AND c.metric_name = 'pnl_concentration_90d'
      ) AS pnl_concentration_90d_extracted_only,
    EXISTS (
        SELECT 1
        FROM expected_metrics AS e2
        WHERE e2.reconciliation_id = r.reconciliation_id
          AND e2.metric_name = 'free_parameter_count'
    )
      AND NOT EXISTS (
          SELECT 1
          FROM comparison_metrics AS c
          WHERE c.reconciliation_id = r.reconciliation_id
            AND c.metric_name = 'free_parameter_count'
      ) AS free_parameter_count_extracted_only,
    'comparison_surface_descriptive_only_no_evidence_quality_scoring_inference'
        AS comparison_surface_posture
FROM d2_rows AS r
JOIN expected_metrics AS e
  ON r.reconciliation_id = e.reconciliation_id
GROUP BY
    r.reconciliation_id,
    r.outcome_id,
    r.candidate_id,
    r.pipeline_version,
    r.overall_verdict,
    r.realized_metrics.gross_pnl
ORDER BY r.reconciliation_id
