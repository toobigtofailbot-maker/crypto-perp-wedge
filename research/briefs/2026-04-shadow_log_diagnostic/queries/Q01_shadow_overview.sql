SELECT
    overlay_shadow_log_id,
    source_bucket_mapping_id,
    source_agent_output_id,
    observed_overlay_bucket,
    mapped_bucket,
    size_multiplier,
    comparison_result,
    override_applied,
    fail_open_preserved,
    advisory_only
FROM v_overlay_shadow_logs_overview
ORDER BY overlay_shadow_log_id;
