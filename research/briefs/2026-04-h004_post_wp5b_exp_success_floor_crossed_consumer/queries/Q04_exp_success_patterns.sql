WITH selected_reconciliations AS (
    SELECT reconciliation_id
    FROM v_reconciliation_overview
    WHERE candidate_id = 'H-004'
      AND outcome_kind = 'research_oos'
      AND pipeline_version = 'post_wp_5b'
      AND expectation_source_type = 'exp_success_criteria'
)
SELECT
    r.reconciliation_id,
    r.outcome_id,
    c.metric_name,
    c.expected_value,
    c.realized_value,
    c.delta_absolute,
    c.delta_relative,
    c.comparison_verdict,
    c.comparison_notes
FROM reconciliations AS r,
UNNEST(r.comparison.metric_comparisons) AS t(c)
WHERE r.reconciliation_id IN (
    SELECT reconciliation_id
    FROM selected_reconciliations
)
ORDER BY c.metric_name, r.reconciliation_id
