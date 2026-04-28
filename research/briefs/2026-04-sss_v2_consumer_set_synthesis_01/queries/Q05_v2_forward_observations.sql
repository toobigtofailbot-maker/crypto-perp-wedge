SELECT
    observation_direction,
    support_characterization,
    scope_boundary
FROM (
    SELECT
        'cross_version_synthesis' AS observation_direction,
        'Structurally possible because the repo now has committed v1 and v2 consumer-set records over bounded SSS artifacts.' AS support_characterization,
        'Observation only; this package does not perform cross-version synthesis.' AS scope_boundary

    UNION ALL

    SELECT
        'sss_v2_stability_lock' AS observation_direction,
        'Structurally supportable after three committed v2 single-axis consumers and this synthesis record, while preserving the distinction between structure and signal sufficiency.' AS support_characterization,
        'Observation only; this package does not create a stability-lock artifact.' AS scope_boundary

    UNION ALL

    SELECT
        'sss_v3_schema_evolution' AS observation_direction,
        'Later schema evolution could target cross-axis or temporal forms because the current v2 set is intentionally single-axis and one-window.' AS support_characterization,
        'Observation only; this package does not design or scope v3.' AS scope_boundary

    UNION ALL

    SELECT
        'corpus_growth' AS observation_direction,
        'The dominant evidence constraint is current corpus size n=10; all eight consumed v2 single-axis segments remain below floor.' AS support_characterization,
        'Observation only; this package does not create corpus-growth machinery or cadence.' AS scope_boundary
) observation_rows
ORDER BY observation_direction;
