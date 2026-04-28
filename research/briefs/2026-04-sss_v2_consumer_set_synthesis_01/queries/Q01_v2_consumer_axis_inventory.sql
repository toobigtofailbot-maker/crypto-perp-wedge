WITH consumer_axes AS (
    SELECT
        'advisory-source' AS consumer_axis,
        'WP-8b' AS consumed_by_package,
        '2026-04-sss_v2_advisory_source_consumer_01.md' AS consumer_brief,
        'SSS-0002' AS shadow_signal_summary_id,
        'advisory-source-only' AS axis_form

    UNION ALL

    SELECT
        'advisory-lineage' AS consumer_axis,
        'WP-8e' AS consumed_by_package,
        '2026-04-sss_v2_advisory_lineage_consumer_01.md' AS consumer_brief,
        'SSS-0003' AS shadow_signal_summary_id,
        'advisory-lineage' AS axis_form

    UNION ALL

    SELECT
        'fixture-identity' AS consumer_axis,
        'WP-8g' AS consumed_by_package,
        '2026-04-sss_v2_fixture_consumer_01.md' AS consumer_brief,
        'SSS-0004' AS shadow_signal_summary_id,
        'fixture-identity' AS axis_form
),
summary_rows AS (
    SELECT
        shadow_signal_summary_id,
        schema_version,
        generated_at,
        first_overlay_shadow_log_id,
        last_overlay_shadow_log_id,
        corpus_first_observed_at,
        corpus_last_observed_at,
        total_source_observation_count,
        derivation_method,
        segmentation_axes,
        segmentation_axes_json,
        COUNT(*) AS segment_count,
        SUM(observation_count) AS total_segment_observation_count,
        SUM(rate_denominator) AS total_rate_denominator,
        SUM(CASE WHEN observation_count >= 10 THEN 1 ELSE 0 END) AS above_floor_segment_count,
        SUM(CASE WHEN observation_count < 10 THEN 1 ELSE 0 END) AS below_floor_segment_count,
        SUM(CASE WHEN agreement_rate IS NULL AND disagreement_rate IS NULL THEN 1 ELSE 0 END) AS null_rate_segment_count,
        SUM(CASE WHEN signal_outcome = 'INSUFFICIENT_EVIDENCE' THEN 1 ELSE 0 END) AS insufficient_evidence_segment_count
    FROM v_shadow_signal_summaries_v2_overview
    WHERE shadow_signal_summary_id IN ('SSS-0002', 'SSS-0003', 'SSS-0004')
    GROUP BY
        shadow_signal_summary_id,
        schema_version,
        generated_at,
        first_overlay_shadow_log_id,
        last_overlay_shadow_log_id,
        corpus_first_observed_at,
        corpus_last_observed_at,
        total_source_observation_count,
        derivation_method,
        segmentation_axes,
        segmentation_axes_json
)
SELECT
    c.consumer_axis,
    c.axis_form,
    c.consumed_by_package,
    c.consumer_brief,
    s.shadow_signal_summary_id,
    s.schema_version,
    s.generated_at,
    s.first_overlay_shadow_log_id,
    s.last_overlay_shadow_log_id,
    s.corpus_first_observed_at,
    s.corpus_last_observed_at,
    s.total_source_observation_count,
    s.derivation_method,
    s.segmentation_axes,
    s.segmentation_axes_json,
    s.segment_count,
    s.total_segment_observation_count,
    s.total_rate_denominator,
    s.above_floor_segment_count,
    s.below_floor_segment_count,
    s.null_rate_segment_count,
    s.insufficient_evidence_segment_count
FROM summary_rows s
JOIN consumer_axes c
    ON s.shadow_signal_summary_id = c.shadow_signal_summary_id
ORDER BY s.shadow_signal_summary_id;
