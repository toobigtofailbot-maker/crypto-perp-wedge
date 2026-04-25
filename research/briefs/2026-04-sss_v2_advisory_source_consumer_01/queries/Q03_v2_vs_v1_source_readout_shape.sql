WITH v2_shape AS (
    SELECT
        s.shadow_signal_summary_id,
        s.schema_version,
        COUNT(*) AS source_count,
        COUNT(*) AS partition_row_count,
        MIN(s.advisory_source_is_first_class_segment_key) AS advisory_source_is_first_class_segment_key,
        'dedicated_v2_instance' AS evidence_source_kind,
        MIN(seg.observation_count < 10) AS any_below_floor,
        MAX(seg.observation_count < 10) AS all_below_floor
    FROM sss_v2_summary s
    JOIN sss_v2_segments seg
      ON seg.shadow_signal_summary_id = s.shadow_signal_summary_id
    GROUP BY s.shadow_signal_summary_id, s.schema_version
),
v1_shape AS (
    SELECT
        'SSS-0001' AS shadow_signal_summary_id,
        'v1_readout' AS schema_version,
        COUNT(*) AS source_count,
        COUNT(*) AS partition_row_count,
        false AS advisory_source_is_first_class_segment_key,
        'v1_readout_over_four_axis_instance' AS evidence_source_kind,
        MIN(observation_count < 10) AS any_below_floor,
        MAX(observation_count < 10) AS all_below_floor
    FROM wp7w_floor_status
)
SELECT
    v2.shadow_signal_summary_id AS v2_shadow_signal_summary_id,
    v2.schema_version AS v2_schema_version,
    v2.source_count AS v2_source_count,
    v2.partition_row_count AS v2_partition_row_count,
    v2.advisory_source_is_first_class_segment_key AS v2_advisory_source_is_first_class_segment_key,
    v2.evidence_source_kind AS v2_evidence_source_kind,
    v1.shadow_signal_summary_id AS v1_shadow_signal_summary_id,
    v1.schema_version AS v1_schema_version,
    v1.source_count AS v1_source_count,
    v1.partition_row_count AS v1_partition_row_count,
    v1.advisory_source_is_first_class_segment_key AS v1_advisory_source_is_first_class_segment_key,
    v1.evidence_source_kind AS v1_evidence_source_kind,
    (v2.any_below_floor <> v1.any_below_floor)
    OR (v2.all_below_floor <> v1.all_below_floor) AS floor_outcomes_differ
FROM v2_shape v2
CROSS JOIN v1_shape v1;
