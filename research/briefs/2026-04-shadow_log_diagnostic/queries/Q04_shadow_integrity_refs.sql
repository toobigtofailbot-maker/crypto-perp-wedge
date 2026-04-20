SELECT
    issue_type,
    overlay_shadow_log_id,
    source_bucket_mapping_id,
    source_agent_output_id,
    source_field,
    expected_value,
    actual_value
FROM v_integrity_overlay_shadow_refs
ORDER BY
    issue_type,
    overlay_shadow_log_id,
    source_bucket_mapping_id,
    source_agent_output_id,
    source_field;
