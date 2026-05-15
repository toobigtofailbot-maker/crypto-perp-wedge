SELECT
    r.reconciliation_id,
    r.outcome_id,
    c.metric_name,
    c.expected_value,
    c.realized_value,
    c.comparison_verdict,
    c.comparison_notes
FROM reconciliations AS r,
UNNEST(r.comparison.metric_comparisons) AS t(c)
WHERE r.reconciliation_id IN ('REC-0022', 'REC-0023', 'REC-0024')
ORDER BY c.metric_name, r.reconciliation_id
