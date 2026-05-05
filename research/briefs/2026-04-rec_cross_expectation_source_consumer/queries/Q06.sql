WITH corpus_checks AS (
    SELECT
        COUNT(*) AS rec_row_count,
        MIN(reconciliation_id) AS rec_id_min,
        MAX(reconciliation_id) AS rec_id_max,
        COUNT(DISTINCT outcome_id) AS source_ol_count,
        COUNT(DISTINCT candidate_id) AS candidate_count,
        SUM(CASE WHEN expectation_source_type = 'exp_success_criteria' THEN 1 ELSE 0 END)
            AS exp_success_criteria_count,
        SUM(CASE WHEN expectation_source_type = 'd2_006_gates' THEN 1 ELSE 0 END)
            AS d2_006_gates_count
    FROM reconciliations
),
claim_rows AS (
    SELECT 'supported_descriptive' AS claim_class, 'corpus inventory' AS claim, 'supported by REC row count and ID range' AS basis
    UNION ALL SELECT 'supported_descriptive', 'expectation-source coverage', 'supported by expectation_source_type counts'
    UNION ALL SELECT 'supported_descriptive', 'REC-to-OL mapping', 'supported by side-by-side outcome_id mapping'
    UNION ALL SELECT 'supported_descriptive', 'per-candidate cross-source inspection', 'supported by candidate_id / outcome_kind / pipeline_version segmentation'
    UNION ALL SELECT 'supported_descriptive', 'H-004 split inspection', 'supported as separate pre_wp_5b and post_wp_5b rows under both expectation sources'
    UNION ALL SELECT 'supported_descriptive', 'D2 comparison-surface exception inspection', 'supported by extracted and compared metric surfaces'
    UNION ALL SELECT 'supported_descriptive', 'REC-5 below-floor marking', 'supported by expectation-source-specific reconciliation_count values'
    UNION ALL SELECT 'unsupported_future_dependent', 'policy', 'requires later explicit policy package'
    UNION ALL SELECT 'unsupported_future_dependent', 'promotion/demotion', 'requires later explicit promotion or demotion package'
    UNION ALL SELECT 'unsupported_future_dependent', 'ranking/recommendation', 'requires later explicit ranking or recommendation package'
    UNION ALL SELECT 'unsupported_future_dependent', 'paper/live readiness', 'requires later explicit paper/live package'
    UNION ALL SELECT 'unsupported_future_dependent', 'evidence-quality scoring', 'requires later explicit scoring package'
    UNION ALL SELECT 'unsupported_future_dependent', 'strategy-family performance conclusion', 'blocked by descriptive scope and REC-5 floor'
    UNION ALL SELECT 'unsupported_future_dependent', 'pipeline-version performance comparison', 'blocked by descriptive scope and REC-5 floor'
    UNION ALL SELECT 'unsupported_future_dependent', 'cross-window inference', 'blocked below REC-5 floor'
    UNION ALL SELECT 'unsupported_future_dependent', 'runtime/deployment authority', 'outside REC consumer authority'
    UNION ALL SELECT 'unsupported_future_dependent', 'OMS/risk/safe-mode/execution authority', 'outside REC consumer authority'
    UNION ALL SELECT 'unsupported_future_dependent', 'protected-path authority', 'outside REC consumer authority'
)
SELECT
    c.claim_class,
    c.claim,
    c.basis,
    checks.rec_row_count,
    checks.rec_id_min,
    checks.rec_id_max,
    checks.source_ol_count,
    checks.candidate_count,
    checks.exp_success_criteria_count,
    checks.d2_006_gates_count
FROM claim_rows AS c
CROSS JOIN corpus_checks AS checks
ORDER BY c.claim_class, c.claim
