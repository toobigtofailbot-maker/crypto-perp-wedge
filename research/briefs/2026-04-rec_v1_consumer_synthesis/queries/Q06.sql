WITH corpus_checks AS (
    SELECT
        COUNT(*) AS rec_row_count,
        COUNT(DISTINCT outcome_id) AS source_ol_count,
        COUNT(DISTINCT candidate_id) AS candidate_count,
        SUM(CASE WHEN candidate_id = 'H-004' THEN 1 ELSE 0 END) AS h004_row_count,
        SUM(CASE WHEN expectation_source_type = 'exp_success_criteria' THEN 1 ELSE 0 END) AS exp_success_criteria_count,
        SUM(CASE WHEN expectation_source_type = 'd2_006_gates' THEN 1 ELSE 0 END) AS d2_006_gates_count
    FROM reconciliations
),
claim_rows AS (
    SELECT 'supported_descriptive' AS claim_class, 'REC corpus inventory' AS claim, 'supported by REC row count and ID range' AS basis
    UNION ALL SELECT 'supported_descriptive', 'REC-to-OL mapping inspection', 'supported by one REC outcome_id mapping per row'
    UNION ALL SELECT 'supported_descriptive', 'per-candidate REC path inspection', 'supported by candidate_id and pipeline_version segmentation'
    UNION ALL SELECT 'supported_descriptive', 'verdict distribution inspection', 'supported by overall_verdict counts only'
    UNION ALL SELECT 'supported_descriptive', 'expectation-source distribution inspection', 'supported by expectation_source_type counts only'
    UNION ALL SELECT 'supported_descriptive', 'H-004 split inspection', 'supported as separate pre_wp_5b and post_wp_5b REC rows'
    UNION ALL SELECT 'supported_descriptive', 'REC-5 floor marking', 'supported by candidate_id / outcome_kind / pipeline_version / expectation_source_type counts'
    UNION ALL SELECT 'supported_descriptive', 'comparison-surface inspection limited to deterministic mapped metrics and preserved qualitative/gate-reference criteria', 'supported by existing REC comparison and expectation arrays'
    UNION ALL SELECT 'unsupported_future_dependent', 'promotion/demotion policy', 'requires later explicit policy package'
    UNION ALL SELECT 'unsupported_future_dependent', 'candidate recommendation', 'requires later explicit decision package'
    UNION ALL SELECT 'unsupported_future_dependent', 'ranking', 'requires later explicit ranking/evidence package'
    UNION ALL SELECT 'unsupported_future_dependent', 'paper/live readiness', 'requires later explicit paper/live package'
    UNION ALL SELECT 'unsupported_future_dependent', 'evidence-quality scoring', 'requires later explicit scoring package'
    UNION ALL SELECT 'unsupported_future_dependent', 'strategy-family performance conclusion', 'requires later sufficient-evidence package'
    UNION ALL SELECT 'unsupported_future_dependent', 'pipeline-version performance comparison', 'requires later sufficient-evidence package'
    UNION ALL SELECT 'unsupported_future_dependent', 'cross-window inference', 'blocked below REC-5 floor'
    UNION ALL SELECT 'unsupported_future_dependent', 'runtime/deployment authority', 'outside REC v1 consumer authority'
    UNION ALL SELECT 'unsupported_future_dependent', 'OMS/risk/safe-mode/execution authority', 'outside REC v1 consumer authority'
    UNION ALL SELECT 'unsupported_future_dependent', 'protected-path authority', 'outside REC v1 consumer authority'
)
SELECT
    c.claim_class,
    c.claim,
    c.basis,
    checks.rec_row_count,
    checks.source_ol_count,
    checks.candidate_count,
    checks.h004_row_count,
    checks.exp_success_criteria_count,
    checks.d2_006_gates_count
FROM claim_rows AS c
CROSS JOIN corpus_checks AS checks
ORDER BY c.claim_class, c.claim
