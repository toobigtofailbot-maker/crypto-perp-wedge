SELECT
    reconciliation_id,
    outcome_id,
    candidate_id,
    outcome_kind,
    pipeline_version,
    expectation_source_type,
    expectation_source_artifact_id,
    expectation_source_artifact_path,
    overall_verdict,
    interpretation,
    notes
FROM reconciliations
WHERE candidate_id = 'H-004'
ORDER BY reconciliation_id
