WITH ordered_lifecycle AS (
    SELECT
        candidate_id,
        lifecycle_change_id,
        transition_edge,
        decided_at,
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
        string_agg(transition_edge, ' | ' ORDER BY transition_order, lifecycle_change_id) AS lifecycle_path,
        string_agg(lifecycle_change_id, ' | ' ORDER BY transition_order, lifecycle_change_id) AS ordered_lch_ids,
        min(decided_at) AS first_decided_at,
        max(decided_at) AS final_decided_at,
        count(*) AS transition_count
    FROM ordered_lifecycle
    GROUP BY candidate_id
)
SELECT
    candidate_id,
    lifecycle_path,
    ordered_lch_ids,
    first_decided_at,
    final_decided_at,
    transition_count,
    CASE
        WHEN lifecycle_path = 'proposed->in_research | in_research->research_concluded | research_concluded->archived'
          AND transition_count = 3
        THEN TRUE
        ELSE FALSE
    END AS follows_expected_retrospective_path
FROM candidate_paths
ORDER BY candidate_id;
