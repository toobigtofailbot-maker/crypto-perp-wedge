WITH consumer_inventory AS (
    SELECT
        'fixture_identity' AS consumer_axis,
        '2026-04-shadow_signal_overlay_fixture_slice_01.md' AS brief_filename,
        'SSS-0001' AS summary_artifact_id,
        COUNT(DISTINCT fixture_identity) AS segment_partition_count,
        10 AS floor_required
    FROM v_shadow_signal_summaries_overview
    WHERE shadow_signal_summary_id = 'SSS-0001'

    UNION ALL

    SELECT
        'lineage' AS consumer_axis,
        '2026-04-shadow_signal_lineage_slice_01.md' AS brief_filename,
        'SSS-0001' AS summary_artifact_id,
        COUNT(*) AS segment_partition_count,
        10 AS floor_required
    FROM (
        SELECT
            advisory_source,
            source_bucket_mapping_id,
            source_pre_gate_advisory_snapshot_id
        FROM v_shadow_signal_summaries_overview
        WHERE shadow_signal_summary_id = 'SSS-0001'
        GROUP BY
            advisory_source,
            source_bucket_mapping_id,
            source_pre_gate_advisory_snapshot_id
    ) lineage_rows

    UNION ALL

    SELECT
        'advisory_source' AS consumer_axis,
        '2026-04-shadow_signal_advisory_source_slice_01.md' AS brief_filename,
        'SSS-0001' AS summary_artifact_id,
        COUNT(DISTINCT advisory_source) AS segment_partition_count,
        10 AS floor_required
    FROM v_shadow_signal_summaries_overview
    WHERE shadow_signal_summary_id = 'SSS-0001'
)
SELECT
    consumer_axis,
    brief_filename,
    summary_artifact_id,
    segment_partition_count,
    floor_required
FROM consumer_inventory
ORDER BY
    CASE consumer_axis
        WHEN 'fixture_identity' THEN 1
        WHEN 'lineage' THEN 2
        WHEN 'advisory_source' THEN 3
        ELSE 4
    END;
