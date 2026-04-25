WITH axis_rows AS (
    SELECT
        'fixture_identity' AS comparison_axis,
        fixture_identity AS partition_key,
        SUM(CASE WHEN insufficient_evidence THEN 1 ELSE 0 END) AS insufficient_segments,
        SUM(CASE WHEN NOT insufficient_evidence THEN 1 ELSE 0 END) AS sufficient_segments,
        SUM(observation_count) AS total_observation_count,
        SUM(rate_denominator) AS total_rate_denominator
    FROM v_shadow_signal_summaries_overview
    WHERE shadow_signal_summary_id = 'SSS-0001'
    GROUP BY fixture_identity

    UNION ALL

    SELECT
        'lineage' AS comparison_axis,
        CONCAT(
            advisory_source,
            ' / ',
            source_bucket_mapping_id,
            ' / ',
            COALESCE(source_pre_gate_advisory_snapshot_id, 'null')
        ) AS partition_key,
        SUM(CASE WHEN insufficient_evidence THEN 1 ELSE 0 END) AS insufficient_segments,
        SUM(CASE WHEN NOT insufficient_evidence THEN 1 ELSE 0 END) AS sufficient_segments,
        SUM(observation_count) AS total_observation_count,
        SUM(rate_denominator) AS total_rate_denominator
    FROM v_shadow_signal_summaries_overview
    WHERE shadow_signal_summary_id = 'SSS-0001'
    GROUP BY
        advisory_source,
        source_bucket_mapping_id,
        source_pre_gate_advisory_snapshot_id

    UNION ALL

    SELECT
        'advisory_source' AS comparison_axis,
        advisory_source AS partition_key,
        SUM(CASE WHEN insufficient_evidence THEN 1 ELSE 0 END) AS insufficient_segments,
        SUM(CASE WHEN NOT insufficient_evidence THEN 1 ELSE 0 END) AS sufficient_segments,
        SUM(observation_count) AS total_observation_count,
        SUM(rate_denominator) AS total_rate_denominator
    FROM v_shadow_signal_summaries_overview
    WHERE shadow_signal_summary_id = 'SSS-0001'
    GROUP BY advisory_source
)
SELECT
    comparison_axis,
    COUNT(*) AS partition_row_count,
    SUM(CASE WHEN insufficient_segments > 0 THEN 1 ELSE 0 END) AS insufficient_partition_count,
    SUM(CASE WHEN sufficient_segments > 0 THEN 1 ELSE 0 END) AS sufficient_partition_count,
    SUM(total_observation_count) AS total_observation_count,
    SUM(total_rate_denominator) AS total_rate_denominator
FROM axis_rows
GROUP BY comparison_axis
ORDER BY
    CASE comparison_axis
        WHEN 'fixture_identity' THEN 1
        WHEN 'lineage' THEN 2
        WHEN 'advisory_source' THEN 3
        ELSE 4
    END;
