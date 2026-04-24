WITH shadow_rows AS (
    SELECT
        overlay_shadow_log_id,
        observed_at,
        COALESCE(advisory_source, 'BMAP') AS advisory_source,
        source_bucket_mapping_id,
        source_pre_gate_advisory_snapshot_id,
        source_agent_output_id,
        CASE
            WHEN observation_source.snapshot_path = 'tests/fixtures/context_snapshot_sample.json'
             AND observation_source.config_path = 'configs/fmp_macro_flags.json'
                THEN 'canonical'
            WHEN observation_source.snapshot_path = 'tests/fixtures/context_snapshot_sample_02.json'
             AND observation_source.config_path = 'configs/fmp_macro_flags_02.json'
                THEN '_02'
            ELSE observation_source.snapshot_path || ' + ' || observation_source.config_path
        END AS fixture_identity,
        observation_source.snapshot_path AS snapshot_path,
        observation_source.config_path AS config_path,
        observed_overlay_bucket,
        mapped_bucket,
        size_multiplier,
        comparison_result
    FROM overlay_shadow_logs
)
SELECT
    overlay_shadow_log_id,
    strftime('%Y-%m-%dT%H:%M:%SZ', CAST(observed_at AS TIMESTAMP)) AS observed_at,
    advisory_source,
    source_bucket_mapping_id,
    source_pre_gate_advisory_snapshot_id,
    source_agent_output_id,
    fixture_identity,
    snapshot_path,
    config_path,
    observed_overlay_bucket,
    mapped_bucket,
    size_multiplier,
    comparison_result
FROM shadow_rows
ORDER BY
    advisory_source,
    source_bucket_mapping_id,
    source_pre_gate_advisory_snapshot_id,
    fixture_identity,
    observed_at,
    overlay_shadow_log_id;
