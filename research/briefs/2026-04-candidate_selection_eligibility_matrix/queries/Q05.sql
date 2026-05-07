SELECT
    candidate_id,
    pipeline_version,
    expectation_source_type,
    reconciliation_id AS rec_id,
    outcome_id AS ol_id,
    false AS combined_for_rec5,
    false AS comparison_claim_supported,
    'h004_rows_remain_separate_by_pipeline_version_and_expectation_source'
        AS separation_note
FROM v_reconciliation_overview
WHERE candidate_id = 'H-004'
ORDER BY pipeline_version, expectation_source_type, reconciliation_id
