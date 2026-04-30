WITH evidence_refs AS (
    SELECT
        CAST(ref.ref_value AS VARCHAR) AS evidence_ref
    FROM lifecycle_changes AS l,
    UNNEST(l.evidence_artifact_refs) AS ref(ref_value)
),
classified_refs AS (
    SELECT
        evidence_ref,
        CASE
            WHEN regexp_matches(evidence_ref, '^research/hypotheses/.*/HYPOTHESIS[.]md$') THEN 'hypothesis_path'
            WHEN regexp_matches(evidence_ref, '^REP-[0-9]{4}$') THEN 'rep'
            WHEN regexp_matches(evidence_ref, '^research/decisions/DEC-[0-9]{4}[.]md$') THEN 'dec_path'
            WHEN regexp_matches(evidence_ref, '^DCH-[0-9]{4}$') THEN 'dch'
            WHEN regexp_matches(evidence_ref, '^REL-[0-9]{4}$') THEN 'rel'
            ELSE 'other'
        END AS evidence_artifact_type
    FROM evidence_refs
),
integrity_counts AS (
    SELECT 'v_integrity_agent_output_refs' AS integrity_view, count(*) AS row_count FROM v_integrity_agent_output_refs
    UNION ALL
    SELECT 'v_integrity_bucket_mapping_refs', count(*) FROM v_integrity_bucket_mapping_refs
    UNION ALL
    SELECT 'v_integrity_candidate_refs', count(*) FROM v_integrity_candidate_refs
    UNION ALL
    SELECT 'v_integrity_decision_refs', count(*) FROM v_integrity_decision_refs
    UNION ALL
    SELECT 'v_integrity_lifecycle_approval_completeness', count(*) FROM v_integrity_lifecycle_approval_completeness
    UNION ALL
    SELECT 'v_integrity_lifecycle_change_refs', count(*) FROM v_integrity_lifecycle_change_refs
    UNION ALL
    SELECT 'v_integrity_lifecycle_fast_track_completeness', count(*) FROM v_integrity_lifecycle_fast_track_completeness
    UNION ALL
    SELECT 'v_integrity_lifecycle_transition_graph', count(*) FROM v_integrity_lifecycle_transition_graph
    UNION ALL
    SELECT 'v_integrity_macro_window_agent_output_refs', count(*) FROM v_integrity_macro_window_agent_output_refs
    UNION ALL
    SELECT 'v_integrity_overlay_shadow_refs', count(*) FROM v_integrity_overlay_shadow_refs
    UNION ALL
    SELECT 'v_integrity_plan_report_pairs', count(*) FROM v_integrity_plan_report_pairs
    UNION ALL
    SELECT 'v_integrity_pre_gate_advisory_snapshot_refs', count(*) FROM v_integrity_pre_gate_advisory_snapshot_refs
    UNION ALL
    SELECT 'v_integrity_release_refs', count(*) FROM v_integrity_release_refs
    UNION ALL
    SELECT 'v_integrity_shadow_signal_summary_derivation', count(*) FROM v_integrity_shadow_signal_summary_derivation
    UNION ALL
    SELECT 'v_integrity_shadow_signal_summary_v2_derivation', count(*) FROM v_integrity_shadow_signal_summary_v2_derivation
)
SELECT
    'integrity_and_boundary_snapshot' AS summary_scope,
    (SELECT count(*) FROM v_integrity_lifecycle_change_refs) AS lifecycle_change_ref_integrity_count,
    (SELECT count(*) FROM v_integrity_lifecycle_transition_graph) AS lifecycle_transition_graph_integrity_count,
    (SELECT count(*) FROM v_integrity_lifecycle_approval_completeness) AS lifecycle_approval_completeness_integrity_count,
    (SELECT count(*) FROM v_integrity_lifecycle_fast_track_completeness) AS lifecycle_fast_track_completeness_integrity_count,
    (SELECT count(*) FROM integrity_counts) AS discovered_integrity_view_count,
    (SELECT sum(row_count) FROM integrity_counts) AS all_discovered_integrity_row_count,
    (SELECT count(*) FROM lifecycle_changes WHERE fast_track_flag = true) AS fast_track_true_count,
    (SELECT count(*) FROM lifecycle_changes WHERE retrospective_flag IS DISTINCT FROM true) AS non_retrospective_count,
    (SELECT sum(list_count(linked_advisory_artifacts)) FROM lifecycle_changes) AS linked_advisory_ref_count,
    (SELECT sum(list_count(strong_candidate_criteria_refs)) FROM lifecycle_changes) AS strong_candidate_criteria_ref_count,
    (SELECT count(*) FROM lifecycle_changes) AS lch_row_count,
    (SELECT count(*) FROM classified_refs) AS evidence_ref_count,
    (SELECT count(*) FROM classified_refs WHERE evidence_artifact_type = 'other') AS unknown_evidence_type_count,
    3 AS consumer_brief_count;
