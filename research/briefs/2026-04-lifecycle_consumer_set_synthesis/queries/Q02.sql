WITH corpus AS (
    SELECT
        count(*) AS lch_row_count,
        count(DISTINCT candidate_id) AS candidate_count,
        count(DISTINCT transition_edge) AS transition_edge_count
    FROM lifecycle_changes
),
edge_counts AS (
    SELECT
        min(edge_candidate_count) AS min_candidates_per_edge,
        max(edge_candidate_count) AS max_candidates_per_edge
    FROM (
        SELECT
            transition_edge,
            count(DISTINCT candidate_id) AS edge_candidate_count
        FROM lifecycle_changes
        GROUP BY transition_edge
    )
),
paths AS (
    SELECT
        count(DISTINCT path) AS distinct_path_count
    FROM (
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
    )
),
evidence_refs AS (
    SELECT
        CAST(ref.ref_value AS VARCHAR) AS evidence_ref
    FROM lifecycle_changes AS l,
    UNNEST(l.evidence_artifact_refs) AS ref(ref_value)
),
classified_refs AS (
    SELECT
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
evidence_summary AS (
    SELECT
        count(*) AS evidence_ref_count,
        count(DISTINCT evidence_artifact_type) FILTER (WHERE evidence_artifact_type <> 'other') AS evidence_artifact_type_count,
        count(*) FILTER (WHERE evidence_artifact_type = 'other') AS unknown_evidence_ref_count
    FROM classified_refs
),
axis_metadata AS (
    SELECT *
    FROM (
        VALUES
            (
                'per_candidate_path',
                'research/briefs/2026-04-lifecycle_per_candidate_consumer.md',
                'research/briefs/2026-04-lifecycle_per_candidate_consumer/',
                'candidate lifecycle path',
                '10 candidates; 1 uniform retrospective path',
                'current corpus has no future-flow, paper/live, fast-track, halted, or recovery paths',
                false
            ),
            (
                'per_transition_edge',
                'research/briefs/2026-04-lifecycle_per_transition_edge_consumer.md',
                'research/briefs/2026-04-lifecycle_per_transition_edge_consumer/',
                'transition edge',
                '3 edges; 10 rows on each edge',
                'edge timing is retrospective artifact timestamp gap only',
                false
            ),
            (
                'per_evidence_artifact_type',
                'research/briefs/2026-04-lifecycle_per_evidence_artifact_type_consumer.md',
                'research/briefs/2026-04-lifecycle_per_evidence_artifact_type_consumer/',
                'evidence artifact type',
                '5 evidence artifact types; 32 evidence refs; 0 unknown refs',
                'evidence lineage is descriptive and does not rank evidence or candidates',
                false
            )
    ) AS t(
        consumer_axis,
        source_brief_path,
        query_bundle_path,
        axis_unit,
        key_finding,
        main_limitation,
        policy_inference_supported
    )
)
SELECT
    m.consumer_axis,
    m.source_brief_path,
    m.query_bundle_path,
    m.axis_unit,
    CASE
        WHEN m.consumer_axis = 'per_candidate_path' THEN c.candidate_count
        WHEN m.consumer_axis = 'per_transition_edge' THEN c.transition_edge_count
        WHEN m.consumer_axis = 'per_evidence_artifact_type' THEN e.evidence_artifact_type_count
    END AS primary_entity_count,
    CASE
        WHEN m.consumer_axis = 'per_candidate_path' THEN p.distinct_path_count
        WHEN m.consumer_axis = 'per_transition_edge' THEN edge_counts.min_candidates_per_edge
        WHEN m.consumer_axis = 'per_evidence_artifact_type' THEN e.evidence_ref_count
    END AS secondary_current_count,
    m.key_finding,
    m.main_limitation,
    m.policy_inference_supported,
    c.lch_row_count,
    e.unknown_evidence_ref_count
FROM axis_metadata AS m
CROSS JOIN corpus AS c
CROSS JOIN paths AS p
CROSS JOIN edge_counts
CROSS JOIN evidence_summary AS e
ORDER BY
    CASE m.consumer_axis
        WHEN 'per_candidate_path' THEN 1
        WHEN 'per_transition_edge' THEN 2
        WHEN 'per_evidence_artifact_type' THEN 3
        ELSE 99
    END;
