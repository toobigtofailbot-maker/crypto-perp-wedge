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
    transition_order,
    transition_edge,
    sum(CASE WHEN evidence_artifact_type = 'hypothesis_path' THEN 1 ELSE 0 END) AS hypothesis_path_count,
    sum(CASE WHEN evidence_artifact_type = 'rep' THEN 1 ELSE 0 END) AS rep_count,
    sum(CASE WHEN evidence_artifact_type = 'dec_path' THEN 1 ELSE 0 END) AS dec_path_count,
    sum(CASE WHEN evidence_artifact_type = 'dch' THEN 1 ELSE 0 END) AS dch_count,
    sum(CASE WHEN evidence_artifact_type = 'rel' THEN 1 ELSE 0 END) AS rel_count,
    sum(CASE WHEN evidence_artifact_type = 'other' THEN 1 ELSE 0 END) AS other_count,
    count(*) AS total_evidence_ref_count,
    string_agg(DISTINCT evidence_artifact_type, ' | ' ORDER BY evidence_artifact_type) AS evidence_artifact_types,
    string_agg(evidence_ref, ' | ' ORDER BY candidate_id, lifecycle_change_id, evidence_ref) AS evidence_refs,
    CASE
        WHEN transition_edge = 'proposed->in_research'
          AND sum(CASE WHEN evidence_artifact_type = 'hypothesis_path' THEN 1 ELSE 0 END) = count(*)
        THEN false
        WHEN transition_edge = 'in_research->research_concluded'
          AND sum(CASE WHEN evidence_artifact_type = 'rep' THEN 1 ELSE 0 END) = count(*)
        THEN false
        WHEN transition_edge = 'research_concluded->archived'
          AND sum(CASE WHEN evidence_artifact_type IN ('dec_path', 'dch', 'rel') THEN 1 ELSE 0 END) = count(*)
        THEN false
        ELSE true
    END AS has_unexpected_evidence_type_for_edge
FROM classified_refs
GROUP BY transition_order, transition_edge
ORDER BY transition_order, transition_edge;
