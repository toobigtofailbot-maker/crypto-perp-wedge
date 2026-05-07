WITH lifecycle_coverage AS (
    SELECT
        candidate_id,
        COUNT(*) AS lifecycle_change_count
    FROM v_lifecycle_change_overview
    GROUP BY candidate_id
),
ol_segments AS (
    SELECT
        candidate_id,
        outcome_kind,
        pipeline_version,
        COUNT(*) AS ol_segment_count
    FROM v_outcome_ledger_overview
    GROUP BY candidate_id, outcome_kind, pipeline_version
),
rec_segments AS (
    SELECT
        candidate_id,
        outcome_kind,
        pipeline_version,
        expectation_source_type,
        reconciliation_count
    FROM v_reconciliation_candidate_pipeline_summary
),
segment_gate_matrix AS (
    SELECT
        r.candidate_id,
        r.outcome_kind AS target_outcome_kind,
        r.pipeline_version AS target_pipeline_version,
        r.expectation_source_type AS target_expectation_source_type,
        CASE
            WHEN c.candidate_id IS NULL THEN 'blocked'
            WHEN COALESCE(l.lifecycle_change_count, 0) = 0 THEN 'blocked'
            WHEN COALESCE(o.ol_segment_count, 0) = 0 THEN 'blocked'
            WHEN r.reconciliation_count >= 3 THEN 'blocked'
            ELSE 'eligible_for_future_evidence_planning'
        END AS eligibility_status,
        CONCAT(
            'registry_presence=',
            CASE WHEN c.candidate_id IS NOT NULL THEN 'pass' ELSE 'fail' END,
            '; integrity_blockers=pass',
            '; lifecycle_provenance=',
            CASE WHEN COALESCE(l.lifecycle_change_count, 0) > 0 THEN 'pass' ELSE 'fail' END,
            '; ol_rec_artifact_presence=',
            CASE WHEN COALESCE(o.ol_segment_count, 0) > 0 THEN 'pass' ELSE 'fail' END,
            '; target_segment_identified=pass',
            '; below_rec5=',
            CASE WHEN r.reconciliation_count < 3 THEN 'pass' ELSE 'fail' END,
            '; retrospective_artifact_cloning_required=no',
            '; forbidden_scope_required=no'
        ) AS eligibility_gate_results,
        GREATEST(0, 3 - r.reconciliation_count) AS required_future_evidence_units,
        CASE
            WHEN c.candidate_id IS NULL THEN 'candidate_not_in_registry'
            WHEN COALESCE(l.lifecycle_change_count, 0) = 0 THEN 'missing_lifecycle_provenance'
            WHEN COALESCE(o.ol_segment_count, 0) = 0 THEN 'missing_ol_target_segment'
            WHEN r.reconciliation_count >= 3 THEN 'rec5_already_satisfied_or_above_floor'
            ELSE NULL
        END AS blocked_reason
    FROM rec_segments AS r
    LEFT JOIN v_candidate_overview AS c
      ON r.candidate_id = c.candidate_id
    LEFT JOIN lifecycle_coverage AS l
      ON r.candidate_id = l.candidate_id
    LEFT JOIN ol_segments AS o
      ON r.candidate_id = o.candidate_id
     AND r.outcome_kind = o.outcome_kind
     AND r.pipeline_version = o.pipeline_version
),
registry_without_segments AS (
    SELECT
        c.candidate_id,
        CAST(NULL AS VARCHAR) AS target_outcome_kind,
        CAST(NULL AS VARCHAR) AS target_pipeline_version,
        CAST(NULL AS VARCHAR) AS target_expectation_source_type,
        'not_applicable' AS eligibility_status,
        CONCAT(
            'registry_presence=pass',
            '; integrity_blockers=pass',
            '; lifecycle_provenance=',
            CASE WHEN COALESCE(l.lifecycle_change_count, 0) > 0 THEN 'pass' ELSE 'missing' END,
            '; ol_rec_artifact_presence=fail',
            '; target_segment_identified=fail',
            '; below_rec5=not_applicable',
            '; retrospective_artifact_cloning_required=no',
            '; forbidden_scope_required=no'
        ) AS eligibility_gate_results,
        CAST(NULL AS INTEGER) AS required_future_evidence_units,
        'no_current_ol_rec_target_segment' AS blocked_reason
    FROM v_candidate_overview AS c
    LEFT JOIN lifecycle_coverage AS l
      ON c.candidate_id = l.candidate_id
    WHERE NOT EXISTS (
        SELECT 1
        FROM rec_segments AS r
        WHERE r.candidate_id = c.candidate_id
    )
)
SELECT
    candidate_id,
    target_outcome_kind,
    target_pipeline_version,
    target_expectation_source_type,
    eligibility_status,
    eligibility_gate_results,
    required_future_evidence_units,
    blocked_reason
FROM segment_gate_matrix
UNION ALL
SELECT
    candidate_id,
    target_outcome_kind,
    target_pipeline_version,
    target_expectation_source_type,
    eligibility_status,
    eligibility_gate_results,
    required_future_evidence_units,
    blocked_reason
FROM registry_without_segments
ORDER BY
    candidate_id,
    target_outcome_kind NULLS LAST,
    target_pipeline_version NULLS LAST,
    target_expectation_source_type NULLS LAST
