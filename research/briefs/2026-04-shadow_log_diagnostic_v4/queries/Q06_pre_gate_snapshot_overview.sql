SELECT
    pre_gate_advisory_snapshot_id,
    source_agent_output_id,
    source_bucket_mapping_id,
    source_macro_window_agent_output_id,
    mapped_bucket,
    size_multiplier,
    macro_window_flag,
    combination_rule_applied,
    combined_bucket,
    deterministic,
    advisory_only
FROM v_pre_gate_advisory_snapshots_overview
WHERE pre_gate_advisory_snapshot_id IN ('PGAS-0002', 'PGAS-0003')
ORDER BY pre_gate_advisory_snapshot_id;
