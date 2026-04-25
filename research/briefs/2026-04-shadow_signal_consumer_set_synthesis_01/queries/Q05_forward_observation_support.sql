WITH summary_state AS (
    SELECT
        COUNT(DISTINCT shadow_signal_summary_id) AS committed_sss_instance_count,
        SUM(observation_count) AS total_observation_count
    FROM v_shadow_signal_summaries_overview
    WHERE shadow_signal_summary_id = 'SSS-0001'
),
axis_floor_state AS (
    SELECT
        'fixture_identity' AS comparison_axis,
        COUNT(*) AS partition_count,
        SUM(CASE WHEN observation_count >= 10 THEN 1 ELSE 0 END) AS partitions_at_or_above_floor
    FROM (
        SELECT fixture_identity, SUM(observation_count) AS observation_count
        FROM v_shadow_signal_summaries_overview
        WHERE shadow_signal_summary_id = 'SSS-0001'
        GROUP BY fixture_identity
    ) fixture_rows

    UNION ALL

    SELECT
        'lineage' AS comparison_axis,
        COUNT(*) AS partition_count,
        SUM(CASE WHEN observation_count >= 10 THEN 1 ELSE 0 END) AS partitions_at_or_above_floor
    FROM (
        SELECT
            advisory_source,
            source_bucket_mapping_id,
            source_pre_gate_advisory_snapshot_id,
            SUM(observation_count) AS observation_count
        FROM v_shadow_signal_summaries_overview
        WHERE shadow_signal_summary_id = 'SSS-0001'
        GROUP BY
            advisory_source,
            source_bucket_mapping_id,
            source_pre_gate_advisory_snapshot_id
    ) lineage_rows

    UNION ALL

    SELECT
        'advisory_source' AS comparison_axis,
        COUNT(*) AS partition_count,
        SUM(CASE WHEN observation_count >= 10 THEN 1 ELSE 0 END) AS partitions_at_or_above_floor
    FROM (
        SELECT advisory_source, SUM(observation_count) AS observation_count
        FROM v_shadow_signal_summaries_overview
        WHERE shadow_signal_summary_id = 'SSS-0001'
        GROUP BY advisory_source
    ) source_rows
),
axis_totals AS (
    SELECT
        COUNT(*) AS completed_consumer_count,
        SUM(partition_count) AS total_partition_count,
        SUM(partitions_at_or_above_floor) AS partitions_at_or_above_floor
    FROM axis_floor_state
)
SELECT
    'corpus_growth' AS observation_direction,
    completed_consumer_count,
    committed_sss_instance_count,
    total_partition_count,
    partitions_at_or_above_floor,
    total_observation_count,
    'All three completed single-axis consumers remain below the locked floor across 8 total realized partitions, so additional corpus growth would be required before stronger axis-level signal statements become available.' AS support_note
FROM axis_totals
CROSS JOIN summary_state

UNION ALL

SELECT
    'sss_v2_schema_evolution' AS observation_direction,
    completed_consumer_count,
    committed_sss_instance_count,
    total_partition_count,
    partitions_at_or_above_floor,
    total_observation_count,
    'The advisory-source consumer is an SSS-0001 readout rather than a first-class source-only summary instance, so any future source-only summary shape would require a different SSS schema or derivation contract.' AS support_note
FROM axis_totals
CROSS JOIN summary_state

UNION ALL

SELECT
    'sss_instance_cadence_mechanism' AS observation_direction,
    completed_consumer_count,
    committed_sss_instance_count,
    total_partition_count,
    partitions_at_or_above_floor,
    total_observation_count,
    'Repo truth contains one committed SSS instance only, so the current consumer set cannot describe multi-instance trend or cadence behavior without additional committed SSS windows.' AS support_note
FROM axis_totals
CROSS JOIN summary_state

UNION ALL

SELECT
    'different_consumer_family' AS observation_direction,
    completed_consumer_count,
    committed_sss_instance_count,
    total_partition_count,
    partitions_at_or_above_floor,
    total_observation_count,
    'The three completed consumers show that single-axis readouts are structurally consumable, but they do not expose cross-axis interactions, temporal trends, or rare-segment effects, which may motivate a different bounded consumer family later.' AS support_note
FROM axis_totals
CROSS JOIN summary_state

ORDER BY observation_direction;
