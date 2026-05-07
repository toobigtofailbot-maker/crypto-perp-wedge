WITH lifecycle_coverage AS (
    SELECT
        candidate_id,
        COUNT(*) AS lifecycle_change_count,
        list_sort(list_distinct(list(transition_edge))) AS lifecycle_transition_edges
    FROM v_lifecycle_change_overview
    GROUP BY candidate_id
),
ol_segments AS (
    SELECT
        candidate_id,
        outcome_kind,
        pipeline_version,
        COUNT(*) AS ol_segment_count,
        list_sort(list_distinct(list(source_artifact_id))) AS source_rep_ids,
        SUM(linked_artifact_count) AS linked_artifact_count
    FROM v_outcome_ledger_overview
    GROUP BY candidate_id, outcome_kind, pipeline_version
),
rec_segments AS (
    SELECT
        r.candidate_id,
        r.outcome_kind,
        r.pipeline_version,
        r.expectation_source_type,
        COUNT(*) AS rec_segment_count,
        list_sort(list_distinct(list(r.reconciliation_id))) AS rec_ids,
        list_sort(list_distinct(list(r.outcome_id))) AS ol_ids,
        list_sort(list_distinct(list(r.expectation_source_artifact_id))) AS expectation_source_artifact_ids
    FROM v_reconciliation_overview AS r
    GROUP BY r.candidate_id, r.outcome_kind, r.pipeline_version, r.expectation_source_type
)
SELECT
    r.candidate_id,
    r.outcome_kind AS target_outcome_kind,
    r.pipeline_version AS target_pipeline_version,
    r.expectation_source_type AS target_expectation_source_type,
    CASE
        WHEN COALESCE(o.ol_segment_count, 0) > 0
          AND r.rec_segment_count > 0
        THEN 'available_ol_rec_segment_artifacts'
        ELSE 'missing_ol_or_rec_segment_artifacts'
    END AS artifact_completeness_note,
    CASE
        WHEN COALESCE(l.lifecycle_change_count, 0) = 3
        THEN 'complete_three_transition_lifecycle_path'
        WHEN COALESCE(l.lifecycle_change_count, 0) > 0
        THEN 'partial_lifecycle_path'
        ELSE 'missing_lifecycle_path'
    END AS lifecycle_completeness_note,
    CASE
        WHEN COALESCE(o.ol_segment_count, 0) > 0
          AND r.rec_segment_count > 0
        THEN 'ol_and_rec_coverage_present'
        ELSE 'ol_or_rec_coverage_missing'
    END AS ol_rec_coverage_note,
    CASE
        WHEN c.strategy_family IS NOT NULL THEN 'strategy_family_available'
        ELSE 'strategy_family_unavailable'
    END AS strategy_family_availability_note,
    c.strategy_family,
    CASE
        WHEN r.expectation_source_type IN ('exp_success_criteria', 'd2_006_gates')
        THEN 'expectation_source_mapping_clear'
        ELSE 'expectation_source_mapping_unclear'
    END AS expectation_source_mapping_note,
    CASE
        WHEN r.pipeline_version IS NOT NULL THEN 'pipeline_version_clear'
        ELSE 'pipeline_version_unclear'
    END AS pipeline_version_clarity_note,
    CASE
        WHEN c.timeframe IS NOT NULL THEN 'registry_timeframe_available'
        ELSE 'registry_timeframe_unavailable'
    END AS data_availability_note,
    c.timeframe,
    l.lifecycle_transition_edges,
    o.source_rep_ids,
    r.rec_ids,
    r.ol_ids,
    r.expectation_source_artifact_ids,
    'descriptive_inputs_only_no_score_rank_or_recommendation' AS descriptive_tie_breaker_notes
FROM rec_segments AS r
LEFT JOIN v_candidate_overview AS c
  ON r.candidate_id = c.candidate_id
LEFT JOIN lifecycle_coverage AS l
  ON r.candidate_id = l.candidate_id
LEFT JOIN ol_segments AS o
  ON r.candidate_id = o.candidate_id
 AND r.outcome_kind = o.outcome_kind
 AND r.pipeline_version = o.pipeline_version
ORDER BY r.candidate_id, r.outcome_kind, r.pipeline_version, r.expectation_source_type
