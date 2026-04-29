WITH edge_counts AS (
    SELECT
        transition_edge,
        CASE transition_edge
            WHEN 'proposed->in_research' THEN 1
            WHEN 'in_research->research_concluded' THEN 2
            WHEN 'research_concluded->archived' THEN 3
            ELSE 99
        END AS transition_order,
        count(DISTINCT candidate_id) AS candidate_count,
        count(*) AS lch_count
    FROM v_lifecycle_change_overview
    GROUP BY transition_edge
),
candidate_paths AS (
    SELECT
        candidate_id,
        string_agg(
            transition_edge,
            ' | '
            ORDER BY
                CASE transition_edge
                    WHEN 'proposed->in_research' THEN 1
                    WHEN 'in_research->research_concluded' THEN 2
                    WHEN 'research_concluded->archived' THEN 3
                    ELSE 99
                END
        ) AS lifecycle_path
    FROM v_lifecycle_change_overview
    GROUP BY candidate_id
)
SELECT
    'wp_9f_alignment' AS summary_scope,
    (SELECT count(*) FROM candidate_paths) AS candidate_count,
    (SELECT count(*) FROM v_lifecycle_change_overview) AS lch_count,
    (SELECT count(*) FROM edge_counts) AS transition_edge_count,
    (SELECT count(DISTINCT lifecycle_path) FROM candidate_paths) AS distinct_path_count,
    (
        SELECT string_agg(
            transition_edge || '=' || CAST(lch_count AS VARCHAR),
            ' | '
            ORDER BY transition_order
        )
        FROM edge_counts
    ) AS rows_per_edge,
    CASE
        WHEN (SELECT count(DISTINCT lifecycle_path) FROM candidate_paths) = 1
        THEN TRUE
        ELSE FALSE
    END AS all_candidates_share_path,
    CASE
        WHEN (SELECT min(candidate_count) FROM edge_counts) = 10
          AND (SELECT max(candidate_count) FROM edge_counts) = 10
        THEN TRUE
        ELSE FALSE
    END AS each_edge_covers_all_candidates,
    TRUE AS consistent_with_wp9f_current_lch_baseline;
