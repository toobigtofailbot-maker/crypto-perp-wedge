WITH evidence_refs AS (
    SELECT
        l.lifecycle_change_id,
        l.candidate_id,
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
    'integrity_and_boundary_snapshot' AS summary_scope,
    (SELECT count(*) FROM v_integrity_lifecycle_change_refs) AS lifecycle_change_ref_integrity_count,
    (SELECT count(*) FROM v_integrity_lifecycle_transition_graph) AS lifecycle_transition_graph_integrity_count,
    (SELECT count(*) FROM v_integrity_lifecycle_approval_completeness) AS lifecycle_approval_completeness_integrity_count,
    (SELECT count(*) FROM v_integrity_lifecycle_fast_track_completeness) AS lifecycle_fast_track_completeness_integrity_count,
    (SELECT count(*) FROM lifecycle_changes WHERE fast_track_flag = true) AS fast_track_true_count,
    (SELECT count(*) FROM lifecycle_changes WHERE retrospective_flag IS DISTINCT FROM true) AS non_retrospective_count,
    (SELECT sum(list_count(linked_advisory_artifacts)) FROM lifecycle_changes) AS linked_advisory_ref_count,
    (SELECT sum(list_count(strong_candidate_criteria_refs)) FROM lifecycle_changes) AS strong_candidate_criteria_ref_count,
    (SELECT count(*) FROM lifecycle_changes) AS lch_row_count,
    (SELECT count(*) FROM classified_refs) AS evidence_ref_count,
    (SELECT count(DISTINCT evidence_artifact_type) FROM classified_refs WHERE evidence_artifact_type <> 'other') AS evidence_artifact_type_count,
    (SELECT count(*) FROM classified_refs WHERE evidence_artifact_type = 'other') AS unknown_evidence_type_count;
