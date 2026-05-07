WITH lifecycle_coverage AS (
    SELECT
        candidate_id,
        COUNT(*) AS lifecycle_change_count,
        list_sort(list_distinct(list(transition_edge))) AS lifecycle_transition_edges
    FROM v_lifecycle_change_overview
    GROUP BY candidate_id
),
ol_coverage AS (
    SELECT
        candidate_id,
        COUNT(*) AS ol_row_count,
        list_sort(list_distinct(list(outcome_kind))) AS ol_outcome_kinds,
        list_sort(list_distinct(list(pipeline_version))) AS ol_pipeline_versions
    FROM v_outcome_ledger_overview
    GROUP BY candidate_id
),
rec_coverage AS (
    SELECT
        candidate_id,
        COUNT(*) AS rec_row_count,
        list_sort(list_distinct(list(outcome_kind))) AS rec_outcome_kinds,
        list_sort(list_distinct(list(pipeline_version))) AS rec_pipeline_versions,
        list_sort(list_distinct(list(expectation_source_type))) AS rec_expectation_source_types
    FROM v_reconciliation_overview
    GROUP BY candidate_id
)
SELECT
    c.candidate_id,
    true AS registry_present,
    c.status AS registry_status,
    c.pipeline_stage AS registry_pipeline_stage,
    c.strategy_family,
    c.timeframe,
    COALESCE(l.lifecycle_change_count, 0) AS lifecycle_change_count,
    COALESCE(l.lifecycle_change_count, 0) > 0 AS lifecycle_coverage_present,
    l.lifecycle_transition_edges,
    COALESCE(o.ol_row_count, 0) AS ol_row_count,
    COALESCE(o.ol_row_count, 0) > 0 AS ol_coverage_present,
    o.ol_outcome_kinds,
    o.ol_pipeline_versions,
    COALESCE(r.rec_row_count, 0) AS rec_row_count,
    COALESCE(r.rec_row_count, 0) > 0 AS rec_coverage_present,
    r.rec_outcome_kinds,
    r.rec_pipeline_versions,
    r.rec_expectation_source_types,
    (
        COALESCE(o.ol_row_count, 0) = 0
        OR COALESCE(r.rec_row_count, 0) = 0
    ) AS registry_present_but_missing_ol_or_rec_coverage
FROM v_candidate_overview AS c
LEFT JOIN lifecycle_coverage AS l
  ON c.candidate_id = l.candidate_id
LEFT JOIN ol_coverage AS o
  ON c.candidate_id = o.candidate_id
LEFT JOIN rec_coverage AS r
  ON c.candidate_id = r.candidate_id
ORDER BY c.candidate_id
