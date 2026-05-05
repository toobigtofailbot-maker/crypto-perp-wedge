WITH source_rows AS (
    SELECT
        outcome_id,
        candidate_id,
        outcome_kind,
        pipeline_version,
        MAX(CASE WHEN expectation_source_type = 'exp_success_criteria' THEN reconciliation_id ELSE NULL END)
            AS exp_success_criteria_rec_id,
        MAX(CASE WHEN expectation_source_type = 'exp_success_criteria' THEN overall_verdict ELSE NULL END)
            AS exp_success_criteria_verdict,
        MAX(CASE WHEN expectation_source_type = 'd2_006_gates' THEN reconciliation_id ELSE NULL END)
            AS d2_006_gates_rec_id,
        MAX(CASE WHEN expectation_source_type = 'd2_006_gates' THEN overall_verdict ELSE NULL END)
            AS d2_006_gates_verdict
    FROM reconciliations
    GROUP BY outcome_id, candidate_id, outcome_kind, pipeline_version
)
SELECT
    outcome_id,
    candidate_id,
    outcome_kind,
    pipeline_version,
    exp_success_criteria_rec_id,
    exp_success_criteria_verdict,
    d2_006_gates_rec_id,
    d2_006_gates_verdict,
    exp_success_criteria_rec_id IS NOT NULL
      AND d2_006_gates_rec_id IS NOT NULL AS both_expectation_sources_present,
    'side_by_side_descriptive_presence_only' AS comparison_posture
FROM source_rows
ORDER BY outcome_id
