SELECT
    limit_key,
    limit_statement,
    support_status
FROM (
    SELECT
        'no_cross_axis_interactions' AS limit_key,
        'The completed v2 consumers are single-axis reads over SSS-0002, SSS-0003, and SSS-0004; they do not test cross-axis interaction effects.' AS limit_statement,
        'structural limit of current consumer set' AS support_status

    UNION ALL

    SELECT
        'no_temporal_trends' AS limit_key,
        'The three committed v2 instances share one corpus window over OSH-0001 through OSH-0010, so the set does not demonstrate temporal trend behavior.' AS limit_statement,
        'structural limit of current corpus window' AS support_status

    UNION ALL

    SELECT
        'rare_segments_not_reviewable' AS limit_key,
        'Every consumed v2 single-axis segment remains below the floor of 10 observations, so rare-segment effects are not reviewable from current evidence.' AS limit_statement,
        'floor-limited evidence state' AS support_status

    UNION ALL

    SELECT
        'no_agreement_rate_inference' AS limit_key,
        'All consumed v2 single-axis segments have null agreement and disagreement rates with INSUFFICIENT_EVIDENCE outcomes, so agreement-rate inference is unsupported.' AS limit_statement,
        'floor-limited evidence state' AS support_status

    UNION ALL

    SELECT
        'structural_coverage_only' AS limit_key,
        'The set demonstrates central-query-layer consumption over three committed v2 axes, not sufficient signal evidence.' AS limit_statement,
        'positive structural finding with evidence limit' AS support_status
) limit_rows
ORDER BY limit_key;
