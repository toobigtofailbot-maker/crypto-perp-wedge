SELECT
    issue_type,
    advisory_source,
    overlay_shadow_log_id,
    source_bucket_mapping_id,
    source_pre_gate_advisory_snapshot_id,
    source_agent_output_id,
    source_field,
    expected_value,
    actual_value
FROM v_overlay_shadow_override_audit
ORDER BY
    issue_type,
    advisory_source,
    overlay_shadow_log_id,
    source_bucket_mapping_id,
    source_pre_gate_advisory_snapshot_id,
    source_agent_output_id,
    source_field;
