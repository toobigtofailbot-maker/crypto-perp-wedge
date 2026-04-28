WITH v2_single_axis_rows AS (
    SELECT *
    FROM v_shadow_signal_summaries_v2_overview
    WHERE shadow_signal_summary_id IN ('SSS-0002', 'SSS-0003', 'SSS-0004')
)
SELECT
    'SSS v2 consumed single-axis set' AS synthesis_set,
    COUNT(DISTINCT shadow_signal_summary_id) AS consumed_summary_count,
    COUNT(*) AS total_segments,
    SUM(CASE WHEN observation_count >= 10 THEN 1 ELSE 0 END) AS above_floor_segments,
    SUM(CASE WHEN observation_count < 10 THEN 1 ELSE 0 END) AS below_floor_segments,
    SUM(CASE WHEN agreement_rate IS NULL AND disagreement_rate IS NULL THEN 1 ELSE 0 END) AS null_rate_segments,
    SUM(CASE WHEN signal_outcome = 'INSUFFICIENT_EVIDENCE' THEN 1 ELSE 0 END) AS insufficient_evidence_segments,
    SUM(observation_count) AS total_segment_observation_count,
    MIN(total_source_observation_count) AS min_corpus_observation_count,
    MAX(total_source_observation_count) AS max_corpus_observation_count,
    10 AS floor_required
FROM v2_single_axis_rows;
