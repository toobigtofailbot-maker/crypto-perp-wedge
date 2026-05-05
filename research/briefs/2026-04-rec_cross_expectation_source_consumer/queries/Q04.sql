WITH comparison_counts AS (
    SELECT
        r.reconciliation_id,
        COUNT(*) AS comparison_count,
        SUM(CASE WHEN c.comparison_verdict IN ('met', 'not_met') THEN 1 ELSE 0 END)
            AS deterministic_comparison_count,
        SUM(CASE WHEN c.comparison_verdict = 'met' THEN 1 ELSE 0 END)
            AS met_comparison_count,
        SUM(CASE WHEN c.comparison_verdict = 'not_met' THEN 1 ELSE 0 END)
            AS not_met_comparison_count
    FROM reconciliations AS r,
    UNNEST(r.comparison.metric_comparisons) AS t(c)
    GROUP BY r.reconciliation_id
)
SELECT
    r.reconciliation_id,
    r.outcome_id,
    r.candidate_id,
    r.pipeline_version,
    r.expectation_source_type,
    r.overall_verdict,
    COALESCE(c.comparison_count, 0) AS comparison_count,
    COALESCE(c.deterministic_comparison_count, 0) AS deterministic_comparison_count,
    COALESCE(c.met_comparison_count, 0) AS met_comparison_count,
    COALESCE(c.not_met_comparison_count, 0) AS not_met_comparison_count,
    'structural_split_only_no_pre_post_improvement_or_degradation_inference'
        AS h004_split_posture
FROM reconciliations AS r
LEFT JOIN comparison_counts AS c
  ON r.reconciliation_id = c.reconciliation_id
WHERE r.candidate_id = 'H-004'
ORDER BY r.expectation_source_type, r.pipeline_version, r.reconciliation_id
