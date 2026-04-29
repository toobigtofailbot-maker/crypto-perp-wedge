WITH edge_ordered AS (
    SELECT
        *,
        CASE transition_edge
            WHEN 'proposed->in_research' THEN 1
            WHEN 'in_research->research_concluded' THEN 2
            WHEN 'research_concluded->archived' THEN 3
            ELSE 99
        END AS transition_order
    FROM v_lifecycle_change_overview
)
SELECT
    transition_order,
    transition_edge,
    from_state,
    to_state,
    count(DISTINCT candidate_id) AS candidate_count,
    count(*) AS lch_count,
    string_agg(candidate_id, ' | ' ORDER BY candidate_id) AS candidate_ids,
    string_agg(lifecycle_change_id, ' | ' ORDER BY candidate_id, lifecycle_change_id) AS lch_ids,
    min(decided_at) AS first_artifact_timestamp,
    max(decided_at) AS last_artifact_timestamp,
    CASE
        WHEN count(DISTINCT candidate_id) = 10
          AND count(*) = 10
        THEN TRUE
        ELSE FALSE
    END AS covers_all_ten_candidates
FROM edge_ordered
GROUP BY transition_order, transition_edge, from_state, to_state
ORDER BY transition_order;
