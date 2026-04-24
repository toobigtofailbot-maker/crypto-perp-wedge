WITH lineage_rows AS (
    SELECT
        advisory_source,
        source_bucket_mapping_id,
        source_pre_gate_advisory_snapshot_id,
        fixture_identity,
        observation_count,
        signal_outcome
    FROM v_shadow_signal_summaries_overview
)
SELECT
    advisory_source,
    source_bucket_mapping_id,
    source_pre_gate_advisory_snapshot_id,
    CONCAT(
        advisory_source,
        ' / ',
        source_bucket_mapping_id,
        ' / ',
        COALESCE(source_pre_gate_advisory_snapshot_id, 'null')
    ) AS lineage_key,
    MAX(CASE WHEN fixture_identity = 'canonical' THEN observation_count END) AS canonical_observation_count,
    MAX(CASE WHEN fixture_identity = 'canonical' THEN signal_outcome END) AS canonical_signal_outcome,
    MAX(CASE WHEN fixture_identity = '_02' THEN observation_count END) AS "_02_observation_count",
    MAX(CASE WHEN fixture_identity = '_02' THEN signal_outcome END) AS "_02_signal_outcome",
    CASE
        WHEN MAX(CASE WHEN fixture_identity = 'canonical' THEN signal_outcome END)
           = MAX(CASE WHEN fixture_identity = '_02' THEN signal_outcome END)
            THEN true
        ELSE false
    END AS signal_outcome_stable_within_lineage,
    MAX(CASE WHEN fixture_identity = '_02' THEN observation_count END)
    - MAX(CASE WHEN fixture_identity = 'canonical' THEN observation_count END) AS observation_count_delta
FROM lineage_rows
GROUP BY
    advisory_source,
    source_bucket_mapping_id,
    source_pre_gate_advisory_snapshot_id
ORDER BY
    advisory_source,
    source_bucket_mapping_id,
    source_pre_gate_advisory_snapshot_id;
