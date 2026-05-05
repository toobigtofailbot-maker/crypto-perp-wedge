SELECT
    candidate_id,
    outcome_kind,
    pipeline_version,
    expectation_source_type,
    list_sort(list(reconciliation_id)) AS reconciliation_ids,
    list_sort(list(outcome_id)) AS outcome_ids,
    list_sort(list(overall_verdict)) AS verdicts,
    COUNT(*) AS reconciliation_count,
    3 AS inference_floor,
    CASE
        WHEN COUNT(*) >= 3 THEN 'MEETS_FLOOR'
        ELSE 'INSUFFICIENT_EVIDENCE'
    END AS floor_status
FROM reconciliations
GROUP BY candidate_id, outcome_kind, pipeline_version, expectation_source_type
ORDER BY candidate_id, outcome_kind, pipeline_version, expectation_source_type
