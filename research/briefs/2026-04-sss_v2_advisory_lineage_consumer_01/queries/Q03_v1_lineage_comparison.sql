WITH v2_lineage AS (
    SELECT
        advisory_source,
        source_bucket_mapping_id,
        source_pre_gate_advisory_snapshot_id,
        CONCAT(
            advisory_source,
            ' / ',
            source_bucket_mapping_id,
            ' / ',
            COALESCE(source_pre_gate_advisory_snapshot_id, 'null')
        ) AS lineage_key,
        COUNT(*) AS v2_row_count,
        SUM(observation_count) AS v2_total_observation_count,
        SUM(CASE WHEN observation_count < 10 THEN 1 ELSE 0 END) AS v2_below_floor_rows,
        SUM(CASE WHEN observation_count >= 10 THEN 1 ELSE 0 END) AS v2_above_floor_rows,
        SUM(CASE WHEN signal_outcome = 'INSUFFICIENT_EVIDENCE' THEN 1 ELSE 0 END) AS v2_insufficient_rows
    FROM v_shadow_signal_summaries_v2_overview
    WHERE shadow_signal_summary_id = 'SSS-0003'
    GROUP BY
        advisory_source,
        source_bucket_mapping_id,
        source_pre_gate_advisory_snapshot_id
),
v1_lineage AS (
    SELECT
        advisory_source,
        source_bucket_mapping_id,
        source_pre_gate_advisory_snapshot_id,
        CONCAT(
            advisory_source,
            ' / ',
            source_bucket_mapping_id,
            ' / ',
            COALESCE(source_pre_gate_advisory_snapshot_id, 'null')
        ) AS lineage_key,
        COUNT(*) AS v1_row_count,
        COUNT(DISTINCT fixture_identity) AS v1_fixture_identity_count,
        SUM(observation_count) AS v1_total_observation_count,
        SUM(CASE WHEN observation_count < 10 THEN 1 ELSE 0 END) AS v1_below_floor_rows,
        SUM(CASE WHEN observation_count >= 10 THEN 1 ELSE 0 END) AS v1_above_floor_rows,
        SUM(CASE WHEN signal_outcome = 'INSUFFICIENT_EVIDENCE' THEN 1 ELSE 0 END) AS v1_insufficient_rows
    FROM v_shadow_signal_summaries_overview
    GROUP BY
        advisory_source,
        source_bucket_mapping_id,
        source_pre_gate_advisory_snapshot_id
)
SELECT
    COALESCE(v2.advisory_source, v1.advisory_source) AS advisory_source,
    COALESCE(v2.source_bucket_mapping_id, v1.source_bucket_mapping_id) AS source_bucket_mapping_id,
    COALESCE(
        v2.source_pre_gate_advisory_snapshot_id,
        v1.source_pre_gate_advisory_snapshot_id
    ) AS source_pre_gate_advisory_snapshot_id,
    COALESCE(v2.lineage_key, v1.lineage_key) AS lineage_key,
    'v2_dedicated_lineage_instance' AS v2_structural_grain,
    'v1_fixture_split_lineage_readout' AS v1_structural_grain,
    v2.v2_row_count,
    v1.v1_row_count,
    v1.v1_fixture_identity_count,
    v2.v2_total_observation_count,
    v1.v1_total_observation_count,
    v2.v2_above_floor_rows,
    v1.v1_above_floor_rows,
    v2.v2_below_floor_rows,
    v1.v1_below_floor_rows,
    v2.v2_insufficient_rows,
    v1.v1_insufficient_rows,
    COALESCE(v2.v2_above_floor_rows, 0) = 0
        AND COALESCE(v1.v1_above_floor_rows, 0) = 0 AS both_forms_fully_below_floor,
    COALESCE(v2.v2_total_observation_count, -1)
        = COALESCE(v1.v1_total_observation_count, -2) AS total_observation_count_matches
FROM v2_lineage v2
FULL OUTER JOIN v1_lineage v1
  ON v1.advisory_source = v2.advisory_source
 AND v1.source_bucket_mapping_id = v2.source_bucket_mapping_id
 AND COALESCE(v1.source_pre_gate_advisory_snapshot_id, 'null')
     = COALESCE(v2.source_pre_gate_advisory_snapshot_id, 'null')
ORDER BY
    COALESCE(v2.advisory_source, v1.advisory_source),
    COALESCE(v2.source_bucket_mapping_id, v1.source_bucket_mapping_id),
    COALESCE(
        v2.source_pre_gate_advisory_snapshot_id,
        v1.source_pre_gate_advisory_snapshot_id,
        'null'
    );
