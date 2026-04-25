SELECT
    shadow_signal_summary_id,
    schema_version,
    generated_at,
    first_overlay_shadow_log_id,
    last_overlay_shadow_log_id,
    corpus_first_observed_at,
    corpus_last_observed_at,
    total_source_observation_count,
    derivation_method,
    segmentation_axes,
    segmentation_axes_json,
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
    match_count,
    mismatch_count,
    abstention_count,
    observation_count,
    rate_denominator,
    agreement_rate,
    disagreement_rate,
    10 AS floor_required,
    observation_count < 10 AS below_floor,
    insufficient_evidence,
    signal_outcome,
    first_segment_observed_at,
    last_segment_observed_at,
    deterministic,
    advisory_only
FROM v_shadow_signal_summaries_v2_overview
WHERE shadow_signal_summary_id = 'SSS-0003'
ORDER BY
    advisory_source,
    source_bucket_mapping_id,
    COALESCE(source_pre_gate_advisory_snapshot_id, 'null');
