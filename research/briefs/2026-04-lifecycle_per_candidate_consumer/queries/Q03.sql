WITH transition_timestamps AS (
    SELECT
        candidate_id,
        max(CASE WHEN transition_edge = 'proposed->in_research' THEN decided_at END) AS proposed_to_research_at,
        max(CASE WHEN transition_edge = 'in_research->research_concluded' THEN decided_at END) AS research_concluded_at,
        max(CASE WHEN transition_edge = 'research_concluded->archived' THEN decided_at END) AS archived_at
    FROM v_lifecycle_change_overview
    GROUP BY candidate_id
)
SELECT
    candidate_id,
    proposed_to_research_at,
    research_concluded_at,
    archived_at,
    date_diff(
        'second',
        CAST(proposed_to_research_at AS TIMESTAMP),
        CAST(research_concluded_at AS TIMESTAMP)
    ) AS gap_seconds_t1_to_t2,
    date_diff(
        'second',
        CAST(research_concluded_at AS TIMESTAMP),
        CAST(archived_at AS TIMESTAMP)
    ) AS gap_seconds_t2_to_t3,
    CASE
        WHEN CAST(archived_at AS TIMESTAMP) < CAST(research_concluded_at AS TIMESTAMP)
        THEN TRUE
        ELSE FALSE
    END AS archival_timestamp_precedes_research_conclusion_timestamp,
    'artifact_commit_timestamp_gap_not_operational_duration' AS timing_interpretation
FROM transition_timestamps
ORDER BY candidate_id;
