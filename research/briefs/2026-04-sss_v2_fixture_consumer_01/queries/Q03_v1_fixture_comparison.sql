WITH v2_fixture AS (
    SELECT
        fixture_identity,
        COUNT(*) AS v2_row_count,
        SUM(observation_count) AS v2_total_observation_count,
        SUM(rate_denominator) AS v2_total_rate_denominator,
        SUM(match_count) AS v2_match_count,
        SUM(mismatch_count) AS v2_mismatch_count,
        SUM(abstention_count) AS v2_abstention_count,
        SUM(CASE WHEN observation_count < 10 THEN 1 ELSE 0 END) AS v2_below_floor_rows,
        SUM(CASE WHEN observation_count >= 10 THEN 1 ELSE 0 END) AS v2_above_floor_rows,
        SUM(CASE WHEN signal_outcome = 'INSUFFICIENT_EVIDENCE' THEN 1 ELSE 0 END) AS v2_insufficient_rows
    FROM v_shadow_signal_summaries_v2_overview
    WHERE shadow_signal_summary_id = 'SSS-0004'
    GROUP BY fixture_identity
),
v1_fixture AS (
    SELECT
        fixture_identity,
        COUNT(*) AS v1_row_count,
        COUNT(DISTINCT advisory_source) AS v1_advisory_source_count,
        COUNT(DISTINCT source_bucket_mapping_id) AS v1_source_bucket_mapping_count,
        COUNT(DISTINCT source_pre_gate_advisory_snapshot_id) AS v1_pre_gate_snapshot_count,
        SUM(observation_count) AS v1_total_observation_count,
        SUM(rate_denominator) AS v1_total_rate_denominator,
        SUM(match_count) AS v1_match_count,
        SUM(mismatch_count) AS v1_mismatch_count,
        SUM(abstention_count) AS v1_abstention_count,
        SUM(CASE WHEN observation_count < 10 THEN 1 ELSE 0 END) AS v1_below_floor_rows,
        SUM(CASE WHEN observation_count >= 10 THEN 1 ELSE 0 END) AS v1_above_floor_rows,
        SUM(CASE WHEN signal_outcome = 'INSUFFICIENT_EVIDENCE' THEN 1 ELSE 0 END) AS v1_insufficient_rows
    FROM v_shadow_signal_summaries_overview
    WHERE fixture_identity IN ('_02', 'canonical')
    GROUP BY fixture_identity
)
SELECT
    COALESCE(v2.fixture_identity, v1.fixture_identity) AS fixture_identity,
    'v2_dedicated_fixture_identity_instance' AS v2_structural_grain,
    'v1_fixture_identity_readout_over_broader_summary' AS v1_structural_grain,
    v2.v2_row_count,
    v1.v1_row_count,
    v1.v1_advisory_source_count,
    v1.v1_source_bucket_mapping_count,
    v1.v1_pre_gate_snapshot_count,
    v2.v2_total_observation_count,
    v1.v1_total_observation_count,
    v2.v2_total_rate_denominator,
    v1.v1_total_rate_denominator,
    v2.v2_match_count,
    v1.v1_match_count,
    v2.v2_mismatch_count,
    v1.v1_mismatch_count,
    v2.v2_abstention_count,
    v1.v1_abstention_count,
    v2.v2_above_floor_rows,
    v1.v1_above_floor_rows,
    v2.v2_below_floor_rows,
    v1.v1_below_floor_rows,
    v2.v2_insufficient_rows,
    v1.v1_insufficient_rows,
    COALESCE(v2.v2_above_floor_rows, 0) = 0
        AND COALESCE(v1.v1_above_floor_rows, 0) = 0 AS both_forms_fully_below_floor,
    COALESCE(v2.v2_total_observation_count, -1)
        = COALESCE(v1.v1_total_observation_count, -2) AS total_observation_count_matches,
    COALESCE(v2.v2_total_rate_denominator, -1)
        = COALESCE(v1.v1_total_rate_denominator, -2) AS total_rate_denominator_matches
FROM v2_fixture v2
FULL OUTER JOIN v1_fixture v1
  ON v1.fixture_identity = v2.fixture_identity
ORDER BY COALESCE(v2.fixture_identity, v1.fixture_identity);
