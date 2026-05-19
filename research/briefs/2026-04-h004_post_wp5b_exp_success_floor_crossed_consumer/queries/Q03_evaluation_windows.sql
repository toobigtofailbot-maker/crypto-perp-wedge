SELECT
    r.reconciliation_id,
    r.outcome_id,
    o.evaluation_window_start,
    o.evaluation_window_end,
    r.retrospective_flag,
    o.source_artifact_id,
    o.source_artifact_path,
    r.expectation_source_artifact_id
FROM v_reconciliation_overview AS r
JOIN v_outcome_ledger_overview AS o
  ON r.outcome_id = o.outcome_id
WHERE r.candidate_id = 'H-004'
  AND r.outcome_kind = 'research_oos'
  AND r.pipeline_version = 'post_wp_5b'
  AND r.expectation_source_type = 'exp_success_criteria'
ORDER BY r.reconciliation_id
