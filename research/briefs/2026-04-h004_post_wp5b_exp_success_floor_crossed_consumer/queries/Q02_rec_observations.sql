SELECT
    reconciliation_id,
    outcome_id,
    overall_verdict,
    retrospective_flag,
    derivation_method,
    derivation_timestamp,
    expectation_source_artifact_id
FROM v_reconciliation_overview
WHERE candidate_id = 'H-004'
  AND outcome_kind = 'research_oos'
  AND pipeline_version = 'post_wp_5b'
  AND expectation_source_type = 'exp_success_criteria'
ORDER BY reconciliation_id
