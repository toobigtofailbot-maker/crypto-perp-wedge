WITH shadow_rows AS (
    SELECT
        COALESCE(advisory_source, 'BMAP') AS advisory_source,
        comparison_result,
        override_applied,
        observed_at,
        CASE
            WHEN observation_source.snapshot_path = 'tests/fixtures/context_snapshot_sample.json'
             AND observation_source.config_path = 'configs/fmp_macro_flags.json'
                THEN 'canonical'
            WHEN observation_source.snapshot_path = 'tests/fixtures/context_snapshot_sample_02.json'
             AND observation_source.config_path = 'configs/fmp_macro_flags_02.json'
                THEN '_02'
            ELSE observation_source.snapshot_path || ' + ' || observation_source.config_path
        END AS fixture_identity
    FROM overlay_shadow_logs
)
SELECT
    advisory_source,
    fixture_identity,
    comparison_result,
    COUNT(*) AS entry_count,
    SUM(CASE WHEN comparison_result = 'MATCH' THEN 1 ELSE 0 END) AS match_count,
    SUM(CASE WHEN comparison_result = 'MISMATCH' THEN 1 ELSE 0 END) AS mismatch_count,
    SUM(CASE WHEN override_applied IS TRUE THEN 1 ELSE 0 END) AS override_true_count,
    strftime('%Y-%m-%dT%H:%M:%SZ', MIN(CAST(observed_at AS TIMESTAMP))) AS first_observed_at,
    strftime('%Y-%m-%dT%H:%M:%SZ', MAX(CAST(observed_at AS TIMESTAMP))) AS last_observed_at
FROM shadow_rows
GROUP BY advisory_source, fixture_identity, comparison_result
ORDER BY advisory_source, fixture_identity, comparison_result;
