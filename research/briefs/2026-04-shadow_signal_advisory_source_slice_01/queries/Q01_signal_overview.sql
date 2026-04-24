SELECT
    shadow_signal_summary_id,
    advisory_source,
    source_bucket_mapping_id,
    source_pre_gate_advisory_snapshot_id,
    fixture_identity,
    match_count,
    mismatch_count,
    abstention_count,
    observation_count,
    rate_denominator,
    insufficient_evidence,
    signal_outcome,
    first_segment_observed_at,
    last_segment_observed_at
FROM v_shadow_signal_summaries_overview
WHERE shadow_signal_summary_id = 'SSS-0001'
  AND advisory_source IN ('BMAP', 'PGAS')
ORDER BY
    advisory_source,
    source_bucket_mapping_id,
    source_pre_gate_advisory_snapshot_id,
    fixture_identity;
