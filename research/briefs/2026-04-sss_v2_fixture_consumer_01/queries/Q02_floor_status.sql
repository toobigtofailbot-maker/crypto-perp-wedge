SELECT
    shadow_signal_summary_id,
    COUNT(*) AS segment_count,
    SUM(CASE WHEN observation_count >= 10 THEN 1 ELSE 0 END) AS above_floor_segment_count,
    SUM(CASE WHEN observation_count < 10 THEN 1 ELSE 0 END) AS below_floor_segment_count,
    SUM(CASE WHEN agreement_rate IS NULL AND disagreement_rate IS NULL THEN 1 ELSE 0 END) AS null_rate_segment_count,
    SUM(CASE WHEN insufficient_evidence THEN 1 ELSE 0 END) AS insufficient_evidence_segment_count,
    SUM(CASE WHEN signal_outcome = 'INSUFFICIENT_EVIDENCE' THEN 1 ELSE 0 END) AS insufficient_signal_outcome_count,
    MIN(observation_count) AS min_observation_count,
    MAX(observation_count) AS max_observation_count,
    10 AS floor_required,
    SUM(CASE WHEN observation_count >= 10 THEN 1 ELSE 0 END) = 0 AS all_segments_below_floor
FROM v_shadow_signal_summaries_v2_overview
WHERE shadow_signal_summary_id = 'SSS-0004'
GROUP BY shadow_signal_summary_id;
