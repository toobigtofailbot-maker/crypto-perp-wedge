WITH evidence_refs AS (
    SELECT
        transition_edge,
        unnest(evidence_artifact_refs) AS evidence_ref
    FROM lifecycle_changes
),
classified_refs AS (
    SELECT
        transition_edge,
        evidence_ref,
        CASE
            WHEN evidence_ref LIKE 'research/hypotheses/%/HYPOTHESIS.md' THEN 'hypothesis_path'
            WHEN evidence_ref LIKE 'REP-%' THEN 'REP'
            WHEN evidence_ref LIKE 'research/decisions/DEC-%.md' THEN 'DEC_path'
            WHEN evidence_ref LIKE 'DCH-%' THEN 'DCH'
            WHEN evidence_ref LIKE 'REL-%' THEN 'REL'
            ELSE 'other'
        END AS evidence_type
    FROM evidence_refs
)
SELECT
    transition_edge,
    sum(CASE WHEN evidence_type = 'hypothesis_path' THEN 1 ELSE 0 END) AS hypothesis_path_count,
    sum(CASE WHEN evidence_type = 'REP' THEN 1 ELSE 0 END) AS rep_count,
    sum(CASE WHEN evidence_type = 'DEC_path' THEN 1 ELSE 0 END) AS dec_path_count,
    sum(CASE WHEN evidence_type = 'DCH' THEN 1 ELSE 0 END) AS dch_count,
    sum(CASE WHEN evidence_type = 'REL' THEN 1 ELSE 0 END) AS rel_count,
    sum(CASE WHEN evidence_type = 'other' THEN 1 ELSE 0 END) AS other_count,
    string_agg(evidence_ref, ' | ' ORDER BY evidence_ref) AS evidence_refs,
    string_agg(
        CASE
            WHEN evidence_ref IN ('research/decisions/DEC-0005.md', 'DCH-0001', 'REL-0001')
            THEN evidence_ref
            ELSE NULL
        END,
        ' | '
        ORDER BY evidence_ref
    ) AS h005_archival_exception_refs
FROM classified_refs
GROUP BY transition_edge
ORDER BY
    CASE transition_edge
        WHEN 'proposed->in_research' THEN 1
        WHEN 'in_research->research_concluded' THEN 2
        WHEN 'research_concluded->archived' THEN 3
        ELSE 99
    END;
