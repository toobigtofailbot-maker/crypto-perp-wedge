WITH candidate_transition_counts AS (
    SELECT
        candidate_id,
        count(*) AS transition_count
    FROM lifecycle_changes
    GROUP BY candidate_id
),
edge_candidate_counts AS (
    SELECT
        transition_edge,
        count(DISTINCT candidate_id) AS candidate_count
    FROM lifecycle_changes
    GROUP BY transition_edge
),
paths AS (
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
        ) AS path
    FROM lifecycle_changes
    GROUP BY candidate_id
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
evidence_alignment AS (
    SELECT
        count(*) FILTER (
            WHERE transition_edge = 'proposed->in_research'
              AND evidence_artifact_type = 'hypothesis_path'
        ) AS hypothesis_path_on_proposed_edge_count,
        count(*) FILTER (
            WHERE transition_edge = 'in_research->research_concluded'
              AND evidence_artifact_type = 'rep'
        ) AS rep_on_research_concluded_edge_count,
        count(*) FILTER (
            WHERE transition_edge = 'research_concluded->archived'
              AND evidence_artifact_type = 'dec_path'
        ) AS dec_path_on_archival_edge_count,
        count(*) FILTER (WHERE evidence_artifact_type = 'other') AS unknown_evidence_ref_count,
        count(*) FILTER (
            WHERE candidate_id = 'H-005'
              AND transition_edge = 'research_concluded->archived'
              AND evidence_artifact_type IN ('dch', 'rel')
        ) AS h005_dch_rel_ref_count,
        count(DISTINCT candidate_id) FILTER (
            WHERE evidence_artifact_type IN ('dch', 'rel')
        ) AS dch_rel_candidate_count
    FROM classified_refs
)
SELECT
    'cross_axis_structural_consistency' AS consistency_scope,
    (SELECT count(DISTINCT path) FROM paths) AS distinct_path_count,
    (SELECT count(*) FROM candidate_transition_counts WHERE transition_count = 3) AS candidates_with_all_three_transitions,
    (SELECT count(*) FROM edge_candidate_counts WHERE candidate_count = 10) AS edges_covering_all_candidates,
    (SELECT min(candidate_count) FROM edge_candidate_counts) AS min_candidates_per_edge,
    (SELECT max(candidate_count) FROM edge_candidate_counts) AS max_candidates_per_edge,
    e.hypothesis_path_on_proposed_edge_count,
    e.rep_on_research_concluded_edge_count,
    e.dec_path_on_archival_edge_count,
    e.unknown_evidence_ref_count,
    CASE
        WHEN e.h005_dch_rel_ref_count = 2
          AND e.dch_rel_candidate_count = 1
        THEN 1
        ELSE 0
    END AS h005_exception_count,
    (
        (SELECT count(DISTINCT path) FROM paths) = 1
        AND (SELECT count(*) FROM candidate_transition_counts WHERE transition_count = 3) = 10
        AND (SELECT count(*) FROM edge_candidate_counts WHERE candidate_count = 10) = 3
        AND e.hypothesis_path_on_proposed_edge_count = 10
        AND e.rep_on_research_concluded_edge_count = 10
        AND e.dec_path_on_archival_edge_count = 10
        AND e.unknown_evidence_ref_count = 0
        AND e.h005_dch_rel_ref_count = 2
        AND e.dch_rel_candidate_count = 1
    ) AS all_consistency_checks_pass
FROM evidence_alignment AS e;
