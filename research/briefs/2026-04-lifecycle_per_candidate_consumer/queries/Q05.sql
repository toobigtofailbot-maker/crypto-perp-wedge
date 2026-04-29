WITH ordered_lifecycle AS (
    SELECT
        candidate_id,
        transition_edge,
        CASE transition_edge
            WHEN 'proposed->in_research' THEN 1
            WHEN 'in_research->research_concluded' THEN 2
            WHEN 'research_concluded->archived' THEN 3
            ELSE 99
        END AS transition_order
    FROM v_lifecycle_change_overview
),
candidate_paths AS (
    SELECT
        candidate_id,
        string_agg(transition_edge, ' | ' ORDER BY transition_order, transition_edge) AS lifecycle_path,
        count(*) AS transition_count
    FROM ordered_lifecycle
    GROUP BY candidate_id
),
edge_counts AS (
    SELECT
        transition_edge,
        transition_count
    FROM v_lifecycle_state_transitions
)
SELECT
    'corpus_summary' AS summary_scope,
    (SELECT count(*) FROM candidate_paths) AS candidate_count,
    (SELECT count(*) FROM v_lifecycle_change_overview) AS lch_count,
    (SELECT count(DISTINCT lifecycle_path) FROM candidate_paths) AS distinct_path_count,
    (SELECT count(*) FROM edge_counts) AS transition_edge_count,
    (SELECT min(transition_count) FROM edge_counts) AS min_count_per_transition,
    (SELECT max(transition_count) FROM edge_counts) AS max_count_per_transition,
    (
        SELECT string_agg(
            transition_edge || '=' || CAST(transition_count AS VARCHAR),
            ' | '
            ORDER BY transition_edge
        )
        FROM edge_counts
    ) AS transition_counts,
    CASE
        WHEN (SELECT count(DISTINCT lifecycle_path) FROM candidate_paths) = 1
          AND (SELECT min(transition_count) FROM candidate_paths) = 3
          AND (SELECT max(transition_count) FROM candidate_paths) = 3
        THEN TRUE
        ELSE FALSE
    END AS all_candidates_share_three_transition_path
;
