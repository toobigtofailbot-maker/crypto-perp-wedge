SELECT
    advisory_source,
    source_bucket_mapping_id,
    source_pre_gate_advisory_snapshot_id,
    fixture_identity,
    observation_count,
    10 AS floor_required,
    insufficient_evidence,
    signal_outcome
FROM v_shadow_signal_summaries_overview
WHERE fixture_identity IN ('canonical', '_02')
ORDER BY
    advisory_source,
    source_bucket_mapping_id,
    source_pre_gate_advisory_snapshot_id,
    fixture_identity;
