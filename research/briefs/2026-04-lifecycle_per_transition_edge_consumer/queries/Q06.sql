SELECT
    'integrity_and_boundary_snapshot' AS summary_scope,
    (SELECT count(*) FROM v_integrity_lifecycle_change_refs) AS lifecycle_change_ref_integrity_count,
    (SELECT count(*) FROM v_integrity_lifecycle_transition_graph) AS lifecycle_transition_graph_integrity_count,
    (SELECT count(*) FROM v_integrity_lifecycle_approval_completeness) AS lifecycle_approval_completeness_integrity_count,
    (SELECT count(*) FROM v_integrity_lifecycle_fast_track_completeness) AS lifecycle_fast_track_completeness_integrity_count,
    (SELECT count(*) FROM lifecycle_changes WHERE fast_track_flag = TRUE) AS fast_track_true_count,
    (SELECT count(*) FROM lifecycle_changes WHERE retrospective_flag IS DISTINCT FROM TRUE) AS non_retrospective_count,
    (SELECT sum(len(linked_advisory_artifacts)) FROM lifecycle_changes) AS linked_advisory_ref_count,
    (SELECT sum(len(strong_candidate_criteria_refs)) FROM lifecycle_changes) AS strong_candidate_criteria_ref_count,
    (SELECT count(*) FROM lifecycle_changes) AS lch_row_count,
    (SELECT count(DISTINCT transition_edge) FROM lifecycle_changes) AS transition_edge_count;
