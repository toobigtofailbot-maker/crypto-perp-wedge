SELECT
    shadow_signal_summary_id,
    CASE
        WHEN shadow_signal_summary_id = 'SSS-0002' THEN 'advisory-source-only'
        WHEN shadow_signal_summary_id = 'SSS-0003' THEN 'advisory-lineage'
        WHEN shadow_signal_summary_id = 'SSS-0004' THEN 'fixture-identity'
    END AS axis_form,
    segmentation_axes,
    segmentation_axes_json,
    CASE
        WHEN shadow_signal_summary_id = 'SSS-0002' THEN 'advisory_source'
        WHEN shadow_signal_summary_id = 'SSS-0003' THEN 'advisory_source, source_bucket_mapping_id, source_pre_gate_advisory_snapshot_id'
        WHEN shadow_signal_summary_id = 'SSS-0004' THEN 'fixture_identity'
    END AS exposed_key_fields,
    COUNT(*) AS segment_count,
    SUM(observation_count) AS total_observation_count,
    SUM(rate_denominator) AS total_rate_denominator,
    COUNT(DISTINCT advisory_source) AS unique_advisory_source_count,
    COUNT(DISTINCT source_bucket_mapping_id) AS unique_source_bucket_mapping_count,
    COUNT(DISTINCT source_pre_gate_advisory_snapshot_id) AS unique_pre_gate_snapshot_count,
    COUNT(DISTINCT fixture_identity) AS unique_fixture_identity_count,
    SUM(match_count) AS total_match_count,
    SUM(mismatch_count) AS total_mismatch_count,
    SUM(abstention_count) AS total_abstention_count,
    SUM(CASE WHEN observation_count < 10 THEN 1 ELSE 0 END) AS below_floor_segment_count,
    SUM(CASE WHEN observation_count >= 10 THEN 1 ELSE 0 END) AS above_floor_segment_count
FROM v_shadow_signal_summaries_v2_overview
WHERE shadow_signal_summary_id IN ('SSS-0002', 'SSS-0003', 'SSS-0004')
GROUP BY
    shadow_signal_summary_id,
    segmentation_axes,
    segmentation_axes_json
ORDER BY shadow_signal_summary_id;
