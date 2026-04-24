WITH shadow_rows AS (
    SELECT
        overlay_shadow_log_id,
        observed_at,
        COALESCE(advisory_source, 'BMAP') AS advisory_source,
        source_bucket_mapping_id,
        source_pre_gate_advisory_snapshot_id,
        observed_overlay_bucket,
        mapped_bucket,
        comparison_result,
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
),
fixture_counts AS (
    SELECT
        advisory_source,
        source_bucket_mapping_id,
        source_pre_gate_advisory_snapshot_id,
        SUM(CASE WHEN fixture_identity = 'canonical' THEN 1 ELSE 0 END) AS canonical_entry_count,
        SUM(CASE WHEN fixture_identity = '_02' THEN 1 ELSE 0 END) AS fixture_02_entry_count
    FROM shadow_rows
    GROUP BY
        advisory_source,
        source_bucket_mapping_id,
        source_pre_gate_advisory_snapshot_id
),
latest_by_fixture AS (
    SELECT
        advisory_source,
        source_bucket_mapping_id,
        source_pre_gate_advisory_snapshot_id,
        fixture_identity,
        overlay_shadow_log_id,
        observed_at,
        observed_overlay_bucket,
        mapped_bucket,
        comparison_result
    FROM shadow_rows
    QUALIFY ROW_NUMBER() OVER (
        PARTITION BY
            advisory_source,
            source_bucket_mapping_id,
            COALESCE(source_pre_gate_advisory_snapshot_id, '__NONE__'),
            fixture_identity
        ORDER BY CAST(observed_at AS TIMESTAMP) DESC, overlay_shadow_log_id DESC
    ) = 1
),
latest_overall AS (
    SELECT
        advisory_source,
        source_bucket_mapping_id,
        source_pre_gate_advisory_snapshot_id,
        fixture_identity,
        overlay_shadow_log_id
    FROM shadow_rows
    QUALIFY ROW_NUMBER() OVER (
        PARTITION BY
            advisory_source,
            source_bucket_mapping_id,
            COALESCE(source_pre_gate_advisory_snapshot_id, '__NONE__')
        ORDER BY CAST(observed_at AS TIMESTAMP) DESC, overlay_shadow_log_id DESC
    ) = 1
)
SELECT
    c.advisory_source,
    c.source_bucket_mapping_id,
    c.source_pre_gate_advisory_snapshot_id,
    c.canonical_entry_count,
    c.fixture_02_entry_count,
    canon.overlay_shadow_log_id AS canonical_latest_overlay_shadow_log_id,
    strftime('%Y-%m-%dT%H:%M:%SZ', CAST(canon.observed_at AS TIMESTAMP)) AS canonical_latest_observed_at,
    canon.comparison_result AS canonical_latest_comparison_result,
    canon.observed_overlay_bucket AS canonical_latest_observed_overlay_bucket,
    canon.mapped_bucket AS canonical_latest_mapped_bucket,
    fixture02.overlay_shadow_log_id AS fixture_02_latest_overlay_shadow_log_id,
    strftime('%Y-%m-%dT%H:%M:%SZ', CAST(fixture02.observed_at AS TIMESTAMP)) AS fixture_02_latest_observed_at,
    fixture02.comparison_result AS fixture_02_latest_comparison_result,
    fixture02.observed_overlay_bucket AS fixture_02_latest_observed_overlay_bucket,
    fixture02.mapped_bucket AS fixture_02_latest_mapped_bucket,
    overall.overlay_shadow_log_id AS latest_overall_overlay_shadow_log_id,
    overall.fixture_identity AS latest_overall_fixture_identity,
    CASE
        WHEN canon.comparison_result IS NOT NULL
         AND fixture02.comparison_result IS NOT NULL
         AND canon.comparison_result = fixture02.comparison_result
            THEN true
        ELSE false
    END AS comparison_stable_across_fixture_identity
FROM fixture_counts AS c
LEFT JOIN latest_by_fixture AS canon
    ON canon.advisory_source = c.advisory_source
   AND canon.source_bucket_mapping_id = c.source_bucket_mapping_id
   AND canon.source_pre_gate_advisory_snapshot_id IS NOT DISTINCT FROM c.source_pre_gate_advisory_snapshot_id
   AND canon.fixture_identity = 'canonical'
LEFT JOIN latest_by_fixture AS fixture02
    ON fixture02.advisory_source = c.advisory_source
   AND fixture02.source_bucket_mapping_id = c.source_bucket_mapping_id
   AND fixture02.source_pre_gate_advisory_snapshot_id IS NOT DISTINCT FROM c.source_pre_gate_advisory_snapshot_id
   AND fixture02.fixture_identity = '_02'
LEFT JOIN latest_overall AS overall
    ON overall.advisory_source = c.advisory_source
   AND overall.source_bucket_mapping_id = c.source_bucket_mapping_id
   AND overall.source_pre_gate_advisory_snapshot_id IS NOT DISTINCT FROM c.source_pre_gate_advisory_snapshot_id
ORDER BY
    c.advisory_source,
    c.source_bucket_mapping_id,
    c.source_pre_gate_advisory_snapshot_id;
