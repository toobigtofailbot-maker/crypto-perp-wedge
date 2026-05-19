WITH selected_reconciliations AS (
    SELECT reconciliation_id
    FROM v_reconciliation_overview
    WHERE candidate_id = 'H-004'
      AND outcome_kind = 'research_oos'
      AND pipeline_version = 'post_wp_5b'
      AND expectation_source_type = 'exp_success_criteria'
),
compared_metrics AS (
    SELECT
        r.reconciliation_id,
        c.metric_name
    FROM reconciliations AS r,
    UNNEST(r.comparison.metric_comparisons) AS t(c)
    WHERE r.reconciliation_id IN (
        SELECT reconciliation_id
        FROM selected_reconciliations
    )
),
extracted_only AS (
    SELECT
        r.reconciliation_id,
        e.metric_name,
        e.expected_operator,
        e.expected_value,
        e.expected_unit,
        e.notes,
        e.source_text,
        'extracted_only_no_comparison_row' AS comparison_surface_posture
    FROM reconciliations AS r,
    UNNEST(r.expectation_extracted.metric_expectations) AS t(e)
    WHERE r.reconciliation_id IN (
        SELECT reconciliation_id
        FROM selected_reconciliations
    )
      AND NOT EXISTS (
          SELECT 1
          FROM compared_metrics AS c
          WHERE c.reconciliation_id = r.reconciliation_id
            AND c.metric_name = e.metric_name
      )
),
null_compared AS (
    SELECT
        r.reconciliation_id,
        c.metric_name,
        NULL AS expected_operator,
        c.expected_value,
        NULL AS expected_unit,
        c.comparison_notes AS notes,
        NULL AS source_text,
        CASE
            WHEN c.comparison_verdict = 'insufficient_evidence'
              AND c.realized_value IS NULL
              AND c.delta_absolute IS NULL
              AND c.delta_relative IS NULL
                THEN 'compared_as_insufficient_evidence_with_null_realized_and_delta'
            WHEN c.realized_value IS NULL
              OR c.delta_absolute IS NULL
              OR c.delta_relative IS NULL
                THEN 'comparison_row_with_null_realized_or_delta'
            ELSE 'comparison_row_available'
        END AS comparison_surface_posture
    FROM reconciliations AS r,
    UNNEST(r.comparison.metric_comparisons) AS t(c)
    WHERE r.reconciliation_id IN (
        SELECT reconciliation_id
        FROM selected_reconciliations
    )
      AND (
          c.comparison_verdict = 'insufficient_evidence'
          OR c.realized_value IS NULL
          OR c.delta_absolute IS NULL
          OR c.delta_relative IS NULL
      )
)
SELECT *
FROM extracted_only
UNION ALL
SELECT *
FROM null_compared
ORDER BY reconciliation_id, metric_name, comparison_surface_posture
