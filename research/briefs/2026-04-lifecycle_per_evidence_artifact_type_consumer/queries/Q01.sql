WITH evidence_refs AS (
    SELECT
        l.lifecycle_change_id,
        l.schema_version,
        l.candidate_id,
        CASE l.transition_edge
            WHEN 'proposed->in_research' THEN 1
            WHEN 'in_research->research_concluded' THEN 2
            WHEN 'research_concluded->archived' THEN 3
            ELSE 99
        END AS transition_order,
        l.transition_edge,
        l.from_state,
        l.to_state,
        l.decided_by,
        l.decided_at,
        COALESCE(l.retrospective_flag, false) AS retrospective_flag,
        COALESCE(l.fast_track_flag, false) AS fast_track_flag,
        CAST(ref.ref_value AS VARCHAR) AS evidence_ref
    FROM lifecycle_changes AS l,
    UNNEST(l.evidence_artifact_refs) AS ref(ref_value)
),
classified_refs AS (
    SELECT
        *,
        CASE
            WHEN regexp_matches(evidence_ref, '^research/hypotheses/.*/HYPOTHESIS[.]md$') THEN 'hypothesis_path'
            WHEN regexp_matches(evidence_ref, '^REP-[0-9]{4}$') THEN 'rep'
            WHEN regexp_matches(evidence_ref, '^research/decisions/DEC-[0-9]{4}[.]md$') THEN 'dec_path'
            WHEN regexp_matches(evidence_ref, '^DCH-[0-9]{4}$') THEN 'dch'
            WHEN regexp_matches(evidence_ref, '^REL-[0-9]{4}$') THEN 'rel'
            ELSE 'other'
        END AS evidence_artifact_type
    FROM evidence_refs
)
SELECT
    lifecycle_change_id,
    schema_version,
    candidate_id,
    transition_order,
    transition_edge,
    from_state,
    to_state,
    decided_by,
    decided_at,
    evidence_ref,
    evidence_artifact_type,
    retrospective_flag,
    fast_track_flag
FROM classified_refs
ORDER BY
    evidence_artifact_type,
    transition_order,
    candidate_id,
    lifecycle_change_id,
    evidence_ref;
