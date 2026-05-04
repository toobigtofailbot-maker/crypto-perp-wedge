WITH corpus AS (
    SELECT
        o.outcome_id,
        o.candidate_id,
        o.outcome_kind,
        o.pipeline_version,
        c.strategy_family
    FROM outcome_ledgers AS o
    JOIN candidates AS c
      ON o.candidate_id = c.candidate_id
)
SELECT
    'per_candidate' AS consumer_axis,
    COUNT(DISTINCT candidate_id) AS represented_groups,
    COUNT(*) AS ol_row_count,
    COUNT(DISTINCT candidate_id) AS candidate_count,
    '10 OL-covered candidates; H-004 is the only two-entry candidate' AS key_structural_finding,
    'descriptive path inspection only; no ranking, recommendation, or OL-4 floor lowering' AS primary_boundary
FROM corpus
UNION ALL
SELECT
    'per_pipeline_version' AS consumer_axis,
    COUNT(DISTINCT pipeline_version) AS represented_groups,
    COUNT(*) AS ol_row_count,
    COUNT(DISTINCT candidate_id) AS candidate_count,
    '2 pipeline versions; H-004 is the only cross-pipeline candidate and only post_wp_5b row' AS key_structural_finding,
    'pipeline_version is disclosure only; no automatic comparability or performance comparison below OL-4' AS primary_boundary
FROM corpus
UNION ALL
SELECT
    'per_strategy_family' AS consumer_axis,
    COUNT(DISTINCT strategy_family) AS represented_groups,
    COUNT(*) AS ol_row_count,
    COUNT(DISTINCT candidate_id) AS candidate_count,
    '8 represented families; trend_following and momentum are current multi-entry families' AS key_structural_finding,
    'family grouping is descriptive only; no ranking, policy authority, or OL-4 floor lowering' AS primary_boundary
FROM corpus
ORDER BY consumer_axis
