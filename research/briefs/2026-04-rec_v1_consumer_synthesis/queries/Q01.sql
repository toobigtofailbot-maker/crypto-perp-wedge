WITH pipeline_distribution AS (
    SELECT
        pipeline_version,
        COUNT(*) AS row_count
    FROM reconciliations
    GROUP BY pipeline_version
),
expectation_source_distribution AS (
    SELECT
        expectation_source_type,
        COUNT(*) AS row_count
    FROM reconciliations
    GROUP BY expectation_source_type
),
verdict_distribution AS (
    SELECT
        overall_verdict,
        COUNT(*) AS row_count
    FROM reconciliations
    GROUP BY overall_verdict
)
SELECT
    COUNT(*) AS rec_row_count,
    MIN(reconciliation_id) AS rec_id_min,
    MAX(reconciliation_id) AS rec_id_max,
    COUNT(DISTINCT outcome_id) AS source_ol_count,
    COUNT(DISTINCT candidate_id) AS candidate_count,
    (
        SELECT list(
            struct_pack(
                pipeline_version := pipeline_version,
                row_count := row_count
            )
            ORDER BY pipeline_version
        )
        FROM pipeline_distribution
    ) AS pipeline_version_distribution,
    (
        SELECT list(
            struct_pack(
                expectation_source_type := expectation_source_type,
                row_count := row_count
            )
            ORDER BY expectation_source_type
        )
        FROM expectation_source_distribution
    ) AS expectation_source_distribution,
    (
        SELECT list(
            struct_pack(
                overall_verdict := overall_verdict,
                row_count := row_count
            )
            ORDER BY overall_verdict
        )
        FROM verdict_distribution
    ) AS verdict_distribution,
    SUM(CASE WHEN expectation_source_type = 'd2_006_gates' THEN 1 ELSE 0 END) AS d2_fallback_count,
    SUM(CASE WHEN candidate_id = 'H-004' THEN 1 ELSE 0 END) AS h004_rec_row_count
FROM reconciliations
