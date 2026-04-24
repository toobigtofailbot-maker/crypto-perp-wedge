SELECT
    fixture_identity,
    COUNT(*) AS segment_count,
    SUM(CASE WHEN insufficient_evidence THEN 1 ELSE 0 END) AS insufficient_segment_count,
    SUM(CASE WHEN NOT insufficient_evidence THEN 1 ELSE 0 END) AS sufficient_segment_count,
    SUM(CASE WHEN signal_outcome = 'AGREEMENT_SIGNAL' THEN 1 ELSE 0 END) AS agreement_signal_count,
    SUM(CASE WHEN signal_outcome = 'DISAGREEMENT_SIGNAL' THEN 1 ELSE 0 END) AS disagreement_signal_count,
    SUM(CASE WHEN signal_outcome = 'MIXED_SIGNAL' THEN 1 ELSE 0 END) AS mixed_signal_count,
    SUM(observation_count) AS total_observation_count,
    SUM(rate_denominator) AS total_rate_denominator
FROM v_shadow_signal_summaries_overview
WHERE fixture_identity IN ('canonical', '_02')
GROUP BY fixture_identity
ORDER BY fixture_identity;
