SELECT
    'three_single_axis_v2_consumers_complete_after_wp8g' AS observation_key,
    'After WP-8g, committed SSS v2 has bounded consumer coverage for advisory-source SSS-0002, advisory-lineage SSS-0003, and fixture-identity SSS-0004.' AS observation_statement

UNION ALL

SELECT
    'central_v2_query_layer_load_bearing_for_three_consumers' AS observation_key,
    'The fixture consumer uses v_shadow_signal_summaries_v2_overview and v_integrity_shadow_signal_summary_v2_derivation, matching the central-query-layer pattern established by WP-8e.' AS observation_statement

UNION ALL

SELECT
    'all_current_v2_segments_remain_below_floor' AS observation_key,
    'Across SSS-0002, SSS-0003, and SSS-0004, all eight current v2 single-axis segments remain below the locked floor of 10 observations with null usable rates.' AS observation_statement

UNION ALL

SELECT
    'corpus_growth_is_binding_constraint' AS observation_key,
    'The current committed shadow-log corpus covers OSH-0001 through OSH-0010, so stronger segment-level signal classifications remain constrained by floor-limited observation counts.' AS observation_statement

UNION ALL

SELECT
    'later_v2_synthesis_is_natural_after_wp8g' AS observation_key,
    'A later v2 synthesis brief becomes a natural future step after WP-8g, but this query records no recommendation, ranking, cadence, or scope commitment.' AS observation_statement

ORDER BY observation_key;
