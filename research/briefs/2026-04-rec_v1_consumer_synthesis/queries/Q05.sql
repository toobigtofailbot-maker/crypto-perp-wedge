WITH expectation_sources AS (
    SELECT
        expectation_source_type,
        COUNT(*) AS row_count
    FROM reconciliations
    GROUP BY expectation_source_type
),
comparison_metrics AS (
    SELECT
        c.metric_name,
        COUNT(*) AS comparison_count,
        list_sort(list_distinct(list(c.comparison_verdict))) AS comparison_verdicts
    FROM reconciliations AS r,
    UNNEST(r.comparison.metric_comparisons) AS t(c)
    GROUP BY c.metric_name
),
expectation_metrics AS (
    SELECT
        e.metric_name,
        e.expected_operator,
        COUNT(*) AS expectation_count
    FROM reconciliations AS r,
    UNNEST(r.expectation_extracted.metric_expectations) AS t(e)
    GROUP BY e.metric_name, e.expected_operator
),
no_deterministic_numeric_comparison AS (
    SELECT
        r.reconciliation_id,
        r.outcome_id,
        r.candidate_id,
        r.pipeline_version,
        r.overall_verdict,
        list_sort(list(e.metric_name)) AS preserved_metric_names
    FROM reconciliations AS r,
    UNNEST(r.expectation_extracted.metric_expectations) AS t(e)
    WHERE NOT EXISTS (
        SELECT 1
        FROM UNNEST(r.comparison.metric_comparisons) AS u(c)
        WHERE c.metric_name = e.metric_name
          AND c.comparison_verdict IN ('met', 'not_met')
    )
    GROUP BY r.reconciliation_id, r.outcome_id, r.candidate_id, r.pipeline_version, r.overall_verdict
)
SELECT
    COALESCE((
        SELECT row_count
        FROM expectation_sources
        WHERE expectation_source_type = 'exp_success_criteria'
    ), 0) AS exp_success_criteria_count,
    COALESCE((
        SELECT row_count
        FROM expectation_sources
        WHERE expectation_source_type = 'd2_006_gates'
    ), 0) AS d2_006_gates_count,
    (
        SELECT list(
            struct_pack(
                metric_name := metric_name,
                comparison_count := comparison_count,
                comparison_verdicts := comparison_verdicts
            )
            ORDER BY metric_name
        )
        FROM comparison_metrics
        WHERE list_contains(comparison_verdicts, 'met')
           OR list_contains(comparison_verdicts, 'not_met')
    ) AS deterministic_comparison_metrics,
    (
        SELECT list(
            struct_pack(
                metric_name := metric_name,
                expected_operator := expected_operator,
                expectation_count := expectation_count
            )
            ORDER BY metric_name, expected_operator
        )
        FROM expectation_metrics
        WHERE expected_operator IN ('gate_reference', 'qualitative')
    ) AS preserved_qualitative_or_gate_reference_metrics,
    (
        SELECT list(
            struct_pack(
                reconciliation_id := reconciliation_id,
                outcome_id := outcome_id,
                candidate_id := candidate_id,
                pipeline_version := pipeline_version,
                overall_verdict := overall_verdict,
                preserved_metric_names := preserved_metric_names
            )
            ORDER BY reconciliation_id
        )
        FROM no_deterministic_numeric_comparison
    ) AS rows_with_preserved_non_numeric_surface,
    (
        SELECT struct_pack(
            reconciliation_id := reconciliation_id,
            outcome_id := outcome_id,
            candidate_id := candidate_id,
            pipeline_version := pipeline_version,
            overall_verdict := overall_verdict,
            interpretation := interpretation
        )
        FROM reconciliations
        WHERE reconciliation_id = 'REC-0011'
    ) AS rec_0011_posture
