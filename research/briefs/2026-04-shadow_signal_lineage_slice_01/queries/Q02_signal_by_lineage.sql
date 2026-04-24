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
    fixture_identity,
    shadow_signal_summary_id,
    match_count,
    mismatch_count,
    abstention_count,
    observation_count,
    rate_denominator,
    insufficient_evidence,
    signal_outcome
FROM v_shadow_signal_summaries_overview
ORDER BY
    advisory_source,
    source_bucket_mapping_id,
    source_pre_gate_advisory_snapshot_id,
    fixture_identity;
