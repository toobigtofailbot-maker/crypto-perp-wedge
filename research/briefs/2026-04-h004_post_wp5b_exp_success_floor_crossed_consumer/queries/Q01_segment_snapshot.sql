SELECT
    candidate_id,
    outcome_kind,
    pipeline_version,
    expectation_source_type,
    reconciliation_count,
    overall_verdicts,
    reconciliation_count = 3 AS rec5_floor_crossed_for_selected_segment
FROM v_reconciliation_candidate_pipeline_summary
WHERE candidate_id = 'H-004'
  AND outcome_kind = 'research_oos'
  AND pipeline_version = 'post_wp_5b'
  AND expectation_source_type = 'exp_success_criteria'
