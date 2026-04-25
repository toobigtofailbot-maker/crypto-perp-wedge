SELECT
    shadow_signal_summary_id,
    schema_version,
    generated_at,
    first_overlay_shadow_log_id,
    last_overlay_shadow_log_id,
    corpus_first_observed_at,
    corpus_last_observed_at,
    total_source_observation_count,
    segmentation_axes,
    segmentation_axes_json,
    COUNT(*) AS segment_count,
    COUNT(DISTINCT advisory_source) AS advisory_source_count,
    COUNT(DISTINCT source_bucket_mapping_id) AS source_bucket_mapping_count,
    COUNT(DISTINCT source_pre_gate_advisory_snapshot_id) AS pre_gate_snapshot_count,
    SUM(observation_count) AS total_segment_observation_count,
    SUM(CASE WHEN observation_count < 10 THEN 1 ELSE 0 END) AS below_floor_segment_count,
    SUM(CASE WHEN observation_count >= 10 THEN 1 ELSE 0 END) AS above_floor_segment_count,
    SUM(CASE WHEN signal_outcome = 'INSUFFICIENT_EVIDENCE' THEN 1 ELSE 0 END) AS insufficient_signal_outcome_count,
    SUM(CASE WHEN agreement_rate IS NULL AND disagreement_rate IS NULL THEN 1 ELSE 0 END) AS null_rate_segment_count
FROM v_shadow_signal_summaries_v2_overview
WHERE shadow_signal_summary_id IN ('SSS-0002', 'SSS-0003')
GROUP BY
    shadow_signal_summary_id,
    schema_version,
    generated_at,
    first_overlay_shadow_log_id,
    last_overlay_shadow_log_id,
    corpus_first_observed_at,
    corpus_last_observed_at,
    total_source_observation_count,
    segmentation_axes,
    segmentation_axes_json
ORDER BY shadow_signal_summary_id;
