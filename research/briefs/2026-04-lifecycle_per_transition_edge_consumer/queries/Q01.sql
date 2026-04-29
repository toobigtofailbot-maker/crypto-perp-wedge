WITH ordered_lifecycle AS (
    SELECT
        CASE transition_edge
            WHEN 'proposed->in_research' THEN 1
            WHEN 'in_research->research_concluded' THEN 2
            WHEN 'research_concluded->archived' THEN 3
            ELSE 99
        END AS transition_order,
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
)
SELECT
    transition_order,
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
FROM ordered_lifecycle
ORDER BY transition_order, candidate_id, lifecycle_change_id;
