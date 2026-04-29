WITH edge_times AS (
    SELECT
        candidate_id,
        max(CASE WHEN transition_edge = 'proposed->in_research' THEN decided_at END) AS proposed_to_research_at,
        max(CASE WHEN transition_edge = 'in_research->research_concluded' THEN decided_at END) AS research_concluded_at,
        max(CASE WHEN transition_edge = 'research_concluded->archived' THEN decided_at END) AS archived_at
    FROM v_lifecycle_change_overview
    GROUP BY candidate_id
),
candidate_gaps AS (
    SELECT
        candidate_id,
        'in_research->research_concluded' AS target_transition_edge,
        date_diff(
            'second',
            CAST(proposed_to_research_at AS TIMESTAMP),
            CAST(research_concluded_at AS TIMESTAMP)
        ) AS gap_seconds,
        FALSE AS archival_timestamp_precedes_research_conclusion_timestamp
    FROM edge_times
    UNION ALL
    SELECT
        candidate_id,
        'research_concluded->archived' AS target_transition_edge,
        date_diff(
            'second',
            CAST(research_concluded_at AS TIMESTAMP),
            CAST(archived_at AS TIMESTAMP)
        ) AS gap_seconds,
        CASE
            WHEN CAST(archived_at AS TIMESTAMP) < CAST(research_concluded_at AS TIMESTAMP)
            THEN TRUE
            ELSE FALSE
        END AS archival_timestamp_precedes_research_conclusion_timestamp
    FROM edge_times
)
SELECT
    target_transition_edge,
    count(*) AS candidate_gap_count,
    min(gap_seconds) AS min_gap_seconds,
    max(gap_seconds) AS max_gap_seconds,
    avg(gap_seconds) AS avg_gap_seconds,
    sum(CASE WHEN gap_seconds < 0 THEN 1 ELSE 0 END) AS negative_gap_count,
    sum(
        CASE
            WHEN archival_timestamp_precedes_research_conclusion_timestamp THEN 1
            ELSE 0
        END
    ) AS archive_before_research_artifact_count,
    'artifact_commit_timestamp_gap_not_operational_duration' AS timing_interpretation
FROM candidate_gaps
GROUP BY target_transition_edge
ORDER BY
    CASE target_transition_edge
        WHEN 'in_research->research_concluded' THEN 2
        WHEN 'research_concluded->archived' THEN 3
        ELSE 99
    END;
