WITH evidence_refs AS (
    SELECT
        CAST(ref.ref_value AS VARCHAR) AS evidence_ref
    FROM lifecycle_changes AS l,
    UNNEST(l.evidence_artifact_refs) AS ref(ref_value)
),
classified_refs AS (
    SELECT
        evidence_ref,
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
    'current_lifecycle_corpus_synthesis_inventory' AS inventory_scope,
    (SELECT count(*) FROM lifecycle_changes) AS lch_row_count,
    (SELECT count(DISTINCT candidate_id) FROM lifecycle_changes) AS candidate_count,
    (SELECT count(DISTINCT transition_edge) FROM lifecycle_changes) AS transition_edge_count,
    (SELECT count(*) FROM evidence_refs) AS evidence_ref_count,
    (SELECT count(DISTINCT evidence_artifact_type) FROM classified_refs WHERE evidence_artifact_type <> 'other') AS evidence_artifact_type_count,
    (SELECT count(*) FROM lifecycle_changes WHERE fast_track_flag = true) AS fast_track_count,
    (SELECT count(*) FROM lifecycle_changes WHERE retrospective_flag IS DISTINCT FROM true) AS non_retrospective_count,
    (SELECT sum(list_count(linked_advisory_artifacts)) FROM lifecycle_changes) AS linked_advisory_ref_count,
    (SELECT sum(list_count(strong_candidate_criteria_refs)) FROM lifecycle_changes) AS strong_candidate_criteria_ref_count,
    (SELECT count(*) FROM classified_refs WHERE evidence_artifact_type = 'other') AS unknown_evidence_ref_count;
