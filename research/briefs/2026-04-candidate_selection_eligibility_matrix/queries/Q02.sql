SELECT
    candidate_id,
    outcome_kind,
    pipeline_version,
    expectation_source_type,
    reconciliation_count,
    3 AS rec5_target,
    GREATEST(0, 3 - reconciliation_count) AS additional_observations_needed,
    CASE
        WHEN reconciliation_count >= 3 THEN 'AT_OR_ABOVE_FLOOR'
        ELSE 'BELOW_FLOOR'
    END AS rec5_status,
    overall_verdicts
FROM v_reconciliation_candidate_pipeline_summary
ORDER BY candidate_id, outcome_kind, pipeline_version, expectation_source_type
