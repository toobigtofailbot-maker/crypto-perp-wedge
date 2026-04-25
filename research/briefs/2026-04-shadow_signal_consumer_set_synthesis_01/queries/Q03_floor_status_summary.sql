WITH axis_partition_rates AS (
    SELECT
        'fixture_identity' AS comparison_axis,
        fixture_identity AS partition_key,
        SUM(observation_count) AS observation_count,
        SUM(rate_denominator) AS rate_denominator
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
        SUM(observation_count) AS observation_count,
        SUM(rate_denominator) AS rate_denominator
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
        SUM(observation_count) AS observation_count,
        SUM(rate_denominator) AS rate_denominator
    FROM v_shadow_signal_summaries_overview
    WHERE shadow_signal_summary_id = 'SSS-0001'
    GROUP BY advisory_source
)
SELECT
    comparison_axis,
    SUM(CASE WHEN observation_count >= 10 THEN 1 ELSE 0 END) AS partitions_at_or_above_floor,
    SUM(CASE WHEN observation_count < 10 THEN 1 ELSE 0 END) AS partitions_below_floor,
    SUM(CASE WHEN observation_count >= 10 AND rate_denominator > 0 THEN 1 ELSE 0 END) AS usable_rate_count,
    SUM(CASE WHEN observation_count < 10 OR rate_denominator = 0 THEN 1 ELSE 0 END) AS null_rate_count
FROM axis_partition_rates
GROUP BY comparison_axis
ORDER BY
    CASE comparison_axis
        WHEN 'fixture_identity' THEN 1
        WHEN 'lineage' THEN 2
        WHEN 'advisory_source' THEN 3
        ELSE 4
    END;
