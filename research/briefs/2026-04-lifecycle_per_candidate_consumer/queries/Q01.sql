SELECT
    lifecycle_change_id,
    schema_version,
    candidate_id,
    transition_edge,
    from_state,
    to_state,
    decided_by,
    decided_at,
    retrospective_flag,
    fast_track_flag,
    evidence_ref_count,
    linked_advisory_ref_count,
    strong_candidate_criteria_ref_count
FROM v_lifecycle_change_overview
ORDER BY lifecycle_change_id;
