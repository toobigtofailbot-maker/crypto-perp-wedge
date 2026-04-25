SELECT
    advisory_source,
    observation_count,
    10 AS floor_required,
    observation_count < 10 AS below_floor,
    signal_outcome,
    CASE
        WHEN agreement_rate IS NULL OR disagreement_rate IS NULL THEN false
        ELSE true
    END AS usable_rates_available
FROM sss_v2_segments
ORDER BY advisory_source;
