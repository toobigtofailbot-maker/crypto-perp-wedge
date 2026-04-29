WITH evidence_refs AS (
    SELECT
        candidate_id,
        lifecycle_change_id,
        unnest(evidence_artifact_refs) AS evidence_ref
    FROM lifecycle_changes
),
classified_refs AS (
    SELECT
        candidate_id,
        lifecycle_change_id,
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
    candidate_id,
    sum(CASE WHEN evidence_type = 'hypothesis_path' THEN 1 ELSE 0 END) AS hypothesis_path_count,
    sum(CASE WHEN evidence_type = 'REP' THEN 1 ELSE 0 END) AS rep_count,
    sum(CASE WHEN evidence_type = 'DEC_path' THEN 1 ELSE 0 END) AS dec_path_count,
    sum(CASE WHEN evidence_type = 'DCH' THEN 1 ELSE 0 END) AS dch_count,
    sum(CASE WHEN evidence_type = 'REL' THEN 1 ELSE 0 END) AS rel_count,
    sum(CASE WHEN evidence_type = 'other' THEN 1 ELSE 0 END) AS other_count,
    string_agg(evidence_ref, ' | ' ORDER BY lifecycle_change_id, evidence_ref) AS evidence_refs,
    string_agg(
        CASE
            WHEN candidate_id = 'H-005' AND evidence_type IN ('DEC_path', 'DCH', 'REL')
            THEN evidence_ref
            ELSE NULL
        END,
        ' | '
        ORDER BY lifecycle_change_id, evidence_ref
    ) AS h005_archival_exception_refs
FROM classified_refs
GROUP BY candidate_id
ORDER BY candidate_id;
