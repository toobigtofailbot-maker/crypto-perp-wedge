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
        count(DISTINCT candidate_id) AS candidate_count,
        count(*) AS lch_count
    FROM v_lifecycle_change_overview
    GROUP BY transition_edge
),
evidence_refs AS (
    SELECT
        l.lifecycle_change_id,
        l.candidate_id,
        l.transition_edge,
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
),
h005_exception_candidates AS (
    SELECT candidate_id
    FROM classified_refs
    WHERE evidence_artifact_type IN ('dch', 'rel')
    GROUP BY candidate_id
)
SELECT
    'wp_9h_current_lch_baseline_alignment' AS summary_scope,
    (SELECT count(*) FROM candidate_paths) AS candidate_count,
    (SELECT count(*) FROM v_lifecycle_change_overview) AS lch_count,
    (SELECT count(*) FROM edge_counts) AS transition_edge_count,
    (SELECT count(*) FROM classified_refs) AS evidence_ref_count,
    (SELECT count(DISTINCT evidence_artifact_type) FROM classified_refs WHERE evidence_artifact_type <> 'other') AS evidence_artifact_type_count,
    (SELECT count(DISTINCT lifecycle_path) FROM candidate_paths) AS distinct_path_count,
    (SELECT count(*) FROM h005_exception_candidates) AS h005_exception_count,
    (SELECT count(*) FROM classified_refs WHERE evidence_artifact_type = 'other') AS unknown_evidence_type_count,
    CASE
        WHEN (SELECT count(DISTINCT lifecycle_path) FROM candidate_paths) = 1
        THEN true
        ELSE false
    END AS all_candidates_share_path,
    CASE
        WHEN (SELECT min(candidate_count) FROM edge_counts) = 10
          AND (SELECT max(candidate_count) FROM edge_counts) = 10
        THEN true
        ELSE false
    END AS all_edges_cover_all_candidates,
    CASE
        WHEN (SELECT count(*) FROM candidate_paths) = 10
          AND (SELECT count(*) FROM v_lifecycle_change_overview) = 30
          AND (SELECT count(*) FROM edge_counts) = 3
          AND (SELECT count(*) FROM classified_refs) = 32
          AND (SELECT count(DISTINCT evidence_artifact_type) FROM classified_refs WHERE evidence_artifact_type <> 'other') = 5
          AND (SELECT count(*) FROM classified_refs WHERE evidence_artifact_type = 'other') = 0
          AND (SELECT count(*) FROM h005_exception_candidates) = 1
          AND (SELECT min(candidate_count) FROM edge_counts) = 10
          AND (SELECT max(candidate_count) FROM edge_counts) = 10
        THEN true
        ELSE false
    END AS consistent_with_wp9f_wp9g_current_lch_baselines;
