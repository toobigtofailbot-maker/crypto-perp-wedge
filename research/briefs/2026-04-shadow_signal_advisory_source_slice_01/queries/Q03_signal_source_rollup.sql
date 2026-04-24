WITH source_rollup AS (
    SELECT
        advisory_source,
        COUNT(*) AS segment_count,
        SUM(CASE WHEN insufficient_evidence THEN 1 ELSE 0 END) AS insufficient_segment_count,
        SUM(CASE WHEN NOT insufficient_evidence THEN 1 ELSE 0 END) AS sufficient_segment_count,
        SUM(CASE WHEN signal_outcome = 'AGREEMENT_SIGNAL' THEN 1 ELSE 0 END) AS agreement_signal_count,
        SUM(CASE WHEN signal_outcome = 'DISAGREEMENT_SIGNAL' THEN 1 ELSE 0 END) AS disagreement_signal_count,
        SUM(CASE WHEN signal_outcome = 'MIXED_SIGNAL' THEN 1 ELSE 0 END) AS mixed_signal_count,
        SUM(match_count) AS total_match_count,
        SUM(mismatch_count) AS total_mismatch_count,
        SUM(abstention_count) AS total_abstention_count,
        SUM(observation_count) AS total_observation_count,
        SUM(rate_denominator) AS total_rate_denominator
    FROM v_shadow_signal_summaries_overview
    WHERE shadow_signal_summary_id = 'SSS-0001'
      AND advisory_source IN ('BMAP', 'PGAS')
    GROUP BY advisory_source
)
SELECT
    advisory_source,
    segment_count,
    insufficient_segment_count,
    sufficient_segment_count,
    agreement_signal_count,
    disagreement_signal_count,
    mixed_signal_count,
    total_observation_count,
    total_rate_denominator,
    CASE
        WHEN total_observation_count >= 10 AND total_rate_denominator > 0
            THEN ROUND(CAST(total_match_count AS DOUBLE) / total_rate_denominator, 6)
        ELSE NULL
    END AS agreement_rate,
    CASE
        WHEN total_observation_count >= 10 AND total_rate_denominator > 0
            THEN ROUND(CAST(total_mismatch_count AS DOUBLE) / total_rate_denominator, 6)
        ELSE NULL
    END AS disagreement_rate
FROM source_rollup
ORDER BY advisory_source;
