SELECT
    reconciliation_id,
    outcome_id,
    overall_verdict,
    retrospective_flag,
    derivation_method,
    derivation_timestamp
FROM v_reconciliation_overview
WHERE candidate_id = 'H-004'
  AND outcome_kind = 'research_oos'
  AND pipeline_version = 'post_wp_5b'
  AND expectation_source_type = 'd2_006_gates'
ORDER BY reconciliation_id
