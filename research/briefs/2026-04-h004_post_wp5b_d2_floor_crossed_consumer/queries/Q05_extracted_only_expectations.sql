WITH compared_metrics AS (
    SELECT
        r.reconciliation_id,
        c.metric_name
    FROM reconciliations AS r,
    UNNEST(r.comparison.metric_comparisons) AS t(c)
    WHERE r.reconciliation_id IN ('REC-0022', 'REC-0023', 'REC-0024')
)
SELECT
    r.reconciliation_id,
    e.metric_name,
    e.expected_operator,
    e.expected_value,
    e.expected_unit,
    e.notes,
    e.source_text,
    CASE
        WHEN e.metric_name = 'cost_drag_fraction'
            THEN 'skipped_due_to_non_positive_gross_pnl'
        ELSE 'extracted_only_no_realized_ol_metric'
    END AS comparison_surface_posture
FROM reconciliations AS r,
UNNEST(r.expectation_extracted.metric_expectations) AS t(e)
WHERE r.reconciliation_id IN ('REC-0022', 'REC-0023', 'REC-0024')
  AND NOT EXISTS (
      SELECT 1
      FROM compared_metrics AS c
      WHERE c.reconciliation_id = r.reconciliation_id
        AND c.metric_name = e.metric_name
  )
ORDER BY r.reconciliation_id, e.metric_name
