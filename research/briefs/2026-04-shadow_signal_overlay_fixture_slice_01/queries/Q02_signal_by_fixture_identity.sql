SELECT
    fixture_identity,
    shadow_signal_summary_id,
    advisory_source,
    source_bucket_mapping_id,
    source_pre_gate_advisory_snapshot_id,
    match_count,
    mismatch_count,
    abstention_count,
    observation_count,
    rate_denominator,
    insufficient_evidence,
    signal_outcome
FROM v_shadow_signal_summaries_overview
WHERE fixture_identity IN ('canonical', '_02')
ORDER BY
    fixture_identity,
    advisory_source,
    source_bucket_mapping_id,
    source_pre_gate_advisory_snapshot_id;
