-- Outcome-ledger / reconciliation distribution including H-012 exact segment count.
WITH outcome_summary AS (
    SELECT
        'outcome_ledger_segment' AS row_type,
        candidate_id,
        outcome_kind,
        pipeline_version,
        NULL AS expectation_source_type,
        outcome_count AS artifact_count,
        NULL AS overall_verdicts
    FROM v_outcome_ledger_candidate_pipeline_summary
),
reconciliation_summary AS (
    SELECT
        'reconciliation_segment' AS row_type,
        candidate_id,
        outcome_kind,
        pipeline_version,
        expectation_source_type,
        reconciliation_count AS artifact_count,
        array_to_string(overall_verdicts, ', ') AS overall_verdicts
    FROM v_reconciliation_candidate_pipeline_summary
)
SELECT *
FROM outcome_summary
UNION ALL
SELECT *
FROM reconciliation_summary
ORDER BY row_type, candidate_id, outcome_kind, pipeline_version, expectation_source_type;
