WITH base_rows AS (
    SELECT
        advisory_source,
        source_bucket_mapping_id,
        source_pre_gate_advisory_snapshot_id,
        fixture_identity,
        insufficient_evidence,
        observation_count,
        rate_denominator
    FROM v_shadow_signal_summaries_overview
    WHERE shadow_signal_summary_id = 'SSS-0001'
      AND advisory_source IN ('BMAP', 'PGAS')
),
axis_rows AS (
    SELECT
        'source' AS comparison_axis,
        advisory_source AS comparison_key,
        COUNT(*) AS segment_count,
        SUM(CASE WHEN insufficient_evidence THEN 1 ELSE 0 END) AS insufficient_segment_count,
        SUM(CASE WHEN NOT insufficient_evidence THEN 1 ELSE 0 END) AS sufficient_segment_count,
        SUM(observation_count) AS total_observation_count,
        SUM(rate_denominator) AS total_rate_denominator
    FROM base_rows
    GROUP BY advisory_source

    UNION ALL

    SELECT
        'fixture_identity' AS comparison_axis,
        fixture_identity AS comparison_key,
        COUNT(*) AS segment_count,
        SUM(CASE WHEN insufficient_evidence THEN 1 ELSE 0 END) AS insufficient_segment_count,
        SUM(CASE WHEN NOT insufficient_evidence THEN 1 ELSE 0 END) AS sufficient_segment_count,
        SUM(observation_count) AS total_observation_count,
        SUM(rate_denominator) AS total_rate_denominator
    FROM base_rows
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
        ) AS comparison_key,
        COUNT(*) AS segment_count,
        SUM(CASE WHEN insufficient_evidence THEN 1 ELSE 0 END) AS insufficient_segment_count,
        SUM(CASE WHEN NOT insufficient_evidence THEN 1 ELSE 0 END) AS sufficient_segment_count,
        SUM(observation_count) AS total_observation_count,
        SUM(rate_denominator) AS total_rate_denominator
    FROM base_rows
    GROUP BY
        advisory_source,
        source_bucket_mapping_id,
        source_pre_gate_advisory_snapshot_id
)
SELECT
    comparison_axis,
    comparison_key,
    segment_count,
    insufficient_segment_count,
    sufficient_segment_count,
    total_observation_count,
    total_rate_denominator,
    'Advisory-source slice is a readout over SSS-0001, not a source-only SSS instance.' AS constraint_note
FROM axis_rows
ORDER BY
    CASE comparison_axis
        WHEN 'source' THEN 1
        WHEN 'fixture_identity' THEN 2
        WHEN 'lineage' THEN 3
        ELSE 4
    END,
    comparison_key;
