-- REC-5 exact segment counts for H-012 and broader current REC corpus.
SELECT
    candidate_id,
    outcome_kind,
    pipeline_version,
    expectation_source_type,
    reconciliation_count AS exact_segment_count,
    CASE WHEN reconciliation_count >= 3 THEN true ELSE false END AS rec5_floor_satisfied,
    array_to_string(overall_verdicts, ', ') AS overall_verdicts
FROM v_reconciliation_candidate_pipeline_summary
ORDER BY candidate_id, outcome_kind, pipeline_version, expectation_source_type;
