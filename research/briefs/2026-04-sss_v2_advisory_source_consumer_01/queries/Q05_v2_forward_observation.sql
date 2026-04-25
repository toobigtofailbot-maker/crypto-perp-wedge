SELECT
    'corpus_growth_floor_crossing' AS observation_direction,
    'Both realized v2 source segments remain below the locked floor of 10 observations, so stronger source-level signal statements would require corpus growth or later floor-crossing evidence.' AS support_note

UNION ALL

SELECT
    'cross_v2_instance_synthesis_after_more_consumers' AS observation_direction,
    'Repo truth contains one committed v2 instance and this first v2 consumer only, so cross-v2-instance synthesis would require additional committed v2 instances and their own bounded consumers first.' AS support_note

UNION ALL

SELECT
    'further_single_axis_v2_instances' AS observation_direction,
    'The committed v2 schema already permits other coherent single-axis forms, so further single-axis v2 instances remain a descriptive future direction once separately authored and validated.' AS support_note

UNION ALL

SELECT
    'possible_future_v2_query_layer_package' AS observation_direction,
    'This bundle uses local temporary DuckDB relations because the current central query layer exposes only v1 SSS content, so a later additive v2 query-layer package is a possible observation-only direction.' AS support_note

ORDER BY observation_direction;
