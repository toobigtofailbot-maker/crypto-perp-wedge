SELECT
    shadow_signal_summary_id,
    schema_version,
    advisory_source,
    match_count,
    mismatch_count,
    abstention_count,
    observation_count,
    rate_denominator,
    agreement_rate,
    disagreement_rate,
    insufficient_evidence,
    signal_outcome,
    first_observed_at,
    last_observed_at
FROM sss_v2_segments
ORDER BY advisory_source;
