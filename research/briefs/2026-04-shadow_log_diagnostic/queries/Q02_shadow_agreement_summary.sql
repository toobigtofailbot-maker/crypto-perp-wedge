SELECT
    comparison_result,
    entry_count,
    match_count,
    mismatch_count,
    override_true_count,
    first_observed_at,
    last_observed_at
FROM v_overlay_shadow_agreement_summary
ORDER BY comparison_result;
