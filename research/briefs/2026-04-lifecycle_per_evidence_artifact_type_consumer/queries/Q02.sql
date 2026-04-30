WITH evidence_refs AS (
    SELECT
        l.lifecycle_change_id,
        l.candidate_id,
        CASE l.transition_edge
            WHEN 'proposed->in_research' THEN 1
            WHEN 'in_research->research_concluded' THEN 2
            WHEN 'research_concluded->archived' THEN 3
            ELSE 99
        END AS transition_order,
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
)
SELECT
    evidence_artifact_type,
    count(*) AS ref_count,
    count(DISTINCT candidate_id) AS distinct_candidate_count,
    count(DISTINCT lifecycle_change_id) AS distinct_lch_count,
    count(DISTINCT transition_edge) AS transition_edge_coverage_count,
    string_agg(DISTINCT transition_edge, ' | ' ORDER BY transition_edge) AS transition_edges,
    string_agg(DISTINCT candidate_id, ' | ' ORDER BY candidate_id) AS candidate_ids,
    string_agg(DISTINCT evidence_ref, ' | ' ORDER BY evidence_ref) AS evidence_refs,
    CASE
        WHEN evidence_artifact_type IN ('hypothesis_path', 'rep', 'dec_path')
          AND count(DISTINCT candidate_id) = 10
          AND count(*) = 10
        THEN 'full_candidate_coverage_for_current_retrospective_corpus'
        WHEN evidence_artifact_type IN ('dch', 'rel')
          AND count(DISTINCT candidate_id) = 1
          AND string_agg(DISTINCT candidate_id, ' | ' ORDER BY candidate_id) = 'H-005'
        THEN 'h005_archival_cross_family_exception_only'
        WHEN evidence_artifact_type = 'other'
        THEN 'unknown_evidence_ref_type'
        ELSE 'non_uniform_current_corpus_coverage'
    END AS coverage_interpretation
FROM classified_refs
GROUP BY evidence_artifact_type
ORDER BY
    CASE evidence_artifact_type
        WHEN 'hypothesis_path' THEN 1
        WHEN 'rep' THEN 2
        WHEN 'dec_path' THEN 3
        WHEN 'dch' THEN 4
        WHEN 'rel' THEN 5
        ELSE 99
    END;
