SELECT
    overall_verdict,
    COUNT(*) AS reconciliation_count,
    list_sort(list(reconciliation_id)) AS reconciliation_ids,
    list_sort(list_distinct(list(candidate_id))) AS candidate_ids,
    list_sort(list_distinct(list(pipeline_version))) AS pipeline_versions,
    list_sort(list_distinct(list(expectation_source_type))) AS expectation_source_types
FROM reconciliations
GROUP BY overall_verdict
ORDER BY overall_verdict
