SELECT
    'central_v2_query_layer_load_bearing' AS observation_key,
    'WP-8e consumes SSS-0003 through v_shadow_signal_summaries_v2_overview and checks v_integrity_shadow_signal_summary_v2_derivation; the package does not use local temporary SSS v2 relations.' AS observation_statement

UNION ALL

SELECT
    'current_v2_segments_remain_below_floor' AS observation_key,
    'SSS-0002 and SSS-0003 are visible through the central v2 overview, and every current v2 segment remains below the locked floor of 10 observations with null usable rates.' AS observation_statement

UNION ALL

SELECT
    'corpus_growth_is_binding_constraint' AS observation_key,
    'The current committed shadow-log corpus covers OSH-0001 through OSH-0010, so stronger segment-level signal classifications remain constrained by floor-limited observation counts.' AS observation_statement

UNION ALL

SELECT
    'possible_later_v2_fixture_instance' AS observation_key,
    'A later overlay-input-fixture v2 instance remains a descriptive future direction only if separately scoped, authored, and validated.' AS observation_statement

UNION ALL

SELECT
    'possible_later_third_consumer_or_synthesis' AS observation_key,
    'A third bounded v2 consumer or later v2 synthesis may become useful after additional committed v2 evidence, but this query records no ranking, recommendation, cadence, or scope commitment.' AS observation_statement

ORDER BY observation_key;
