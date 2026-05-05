WITH source_segments AS (
    SELECT
        candidate_id,
        outcome_kind,
        pipeline_version,
        expectation_source_type,
        COUNT(*) AS reconciliation_count,
        list(reconciliation_id ORDER BY reconciliation_id) AS rec_ids,
        list(outcome_id ORDER BY reconciliation_id) AS ol_ids,
        list(overall_verdict ORDER BY reconciliation_id) AS verdicts
    FROM reconciliations
    GROUP BY
        candidate_id,
        outcome_kind,
        pipeline_version,
        expectation_source_type
),
segment_matrix AS (
    SELECT
        candidate_id,
        outcome_kind,
        pipeline_version,
        COALESCE(SUM(CASE WHEN expectation_source_type = 'exp_success_criteria' THEN reconciliation_count ELSE 0 END), 0)
            AS exp_success_criteria_count,
        COALESCE(SUM(CASE WHEN expectation_source_type = 'd2_006_gates' THEN reconciliation_count ELSE 0 END), 0)
            AS d2_006_gates_count,
        MAX(CASE WHEN expectation_source_type = 'exp_success_criteria' THEN rec_ids ELSE NULL END)
            AS exp_success_criteria_rec_ids,
        MAX(CASE WHEN expectation_source_type = 'd2_006_gates' THEN rec_ids ELSE NULL END)
            AS d2_006_gates_rec_ids,
        MAX(CASE WHEN expectation_source_type = 'exp_success_criteria' THEN ol_ids ELSE NULL END)
            AS exp_success_criteria_ol_ids,
        MAX(CASE WHEN expectation_source_type = 'd2_006_gates' THEN ol_ids ELSE NULL END)
            AS d2_006_gates_ol_ids,
        MAX(CASE WHEN expectation_source_type = 'exp_success_criteria' THEN verdicts ELSE NULL END)
            AS exp_success_criteria_verdicts,
        MAX(CASE WHEN expectation_source_type = 'd2_006_gates' THEN verdicts ELSE NULL END)
            AS d2_006_gates_verdicts
    FROM source_segments
    GROUP BY candidate_id, outcome_kind, pipeline_version
)
SELECT
    candidate_id,
    outcome_kind,
    pipeline_version,
    exp_success_criteria_count,
    d2_006_gates_count,
    exp_success_criteria_rec_ids,
    d2_006_gates_rec_ids,
    exp_success_criteria_ol_ids,
    d2_006_gates_ol_ids,
    exp_success_criteria_verdicts,
    d2_006_gates_verdicts,
    exp_success_criteria_count < 3 AS exp_success_criteria_below_rec5_floor,
    d2_006_gates_count < 3 AS d2_006_gates_below_rec5_floor,
    true AS counts_are_not_combined_across_expectation_sources,
    (
        exp_success_criteria_count < 3
        AND d2_006_gates_count < 3
    ) AS all_source_segments_below_rec5_floor
FROM segment_matrix
ORDER BY candidate_id, outcome_kind, pipeline_version
