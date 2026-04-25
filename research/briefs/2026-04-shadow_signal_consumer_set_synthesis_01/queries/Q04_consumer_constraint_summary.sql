SELECT
    comparison_axis,
    consumes_existing_sss_instance,
    creates_new_sss_instance,
    constraint_note
FROM (
    SELECT
        'fixture_identity' AS comparison_axis,
        true AS consumes_existing_sss_instance,
        false AS creates_new_sss_instance,
        'Consumes existing SSS-0001 segments grouped by fixture identity only; does not add cross-axis interaction claims.' AS constraint_note

    UNION ALL

    SELECT
        'lineage' AS comparison_axis,
        true AS consumes_existing_sss_instance,
        false AS creates_new_sss_instance,
        'Consumes existing SSS-0001 segments grouped by realized advisory lineage only; does not add temporal or cross-axis interpretation.' AS constraint_note

    UNION ALL

    SELECT
        'advisory_source' AS comparison_axis,
        true AS consumes_existing_sss_instance,
        false AS creates_new_sss_instance,
        'Consumes existing SSS-0001 as an advisory-source readout, not as a new advisory-source-only SSS instance.' AS constraint_note
) constraint_rows
ORDER BY
    CASE comparison_axis
        WHEN 'fixture_identity' THEN 1
        WHEN 'lineage' THEN 2
        WHEN 'advisory_source' THEN 3
        ELSE 4
    END;
