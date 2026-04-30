WITH edge_times AS (
    SELECT
        candidate_id,
        max(CASE WHEN transition_edge = 'proposed->in_research' THEN decided_at END) AS proposed_to_research_at,
        max(CASE WHEN transition_edge = 'in_research->research_concluded' THEN decided_at END) AS research_concluded_at,
        max(CASE WHEN transition_edge = 'research_concluded->archived' THEN decided_at END) AS archived_at
    FROM v_lifecycle_change_overview
    GROUP BY candidate_id
),
archival_gaps AS (
    SELECT
        candidate_id,
        date_diff(
            'second',
            CAST(research_concluded_at AS TIMESTAMP),
            CAST(archived_at AS TIMESTAMP)
        ) AS archival_gap_seconds
    FROM edge_times
)
SELECT
    'timing_and_retrospective_boundary_synthesis' AS timing_scope,
    'artifact_commit_timestamp_gap_not_operational_duration' AS timing_interpretation,
    (SELECT count(*) FROM archival_gaps WHERE archival_gap_seconds < 0) AS archival_edge_negative_gap_count,
    (SELECT count(*) FROM lifecycle_changes WHERE fast_track_flag = true) AS fast_track_count,
    (SELECT count(*) FROM lifecycle_changes WHERE retrospective_flag IS DISTINCT FROM true) AS non_retrospective_count,
    true AS cannot_infer_operational_lifecycle_speed,
    true AS cannot_infer_process_speed,
    true AS cannot_infer_research_quality,
    true AS cannot_infer_candidate_quality,
    true AS cannot_infer_operational_readiness,
    true AS cannot_infer_promotion_readiness,
    true AS cannot_infer_evidence_strength
FROM archival_gaps
LIMIT 1;
