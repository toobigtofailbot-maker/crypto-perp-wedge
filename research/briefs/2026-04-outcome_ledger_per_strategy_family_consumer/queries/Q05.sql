SELECT
    c.strategy_family,
    o.candidate_id,
    o.outcome_kind,
    o.pipeline_version,
    COUNT(*) AS window_count,
    3 AS inference_floor,
    CASE
        WHEN COUNT(*) < 3 THEN 'INSUFFICIENT_EVIDENCE'
        ELSE 'FLOOR_MET'
    END AS floor_status,
    CASE
        WHEN COUNT(*) < 3 THEN 'single-window factual observation only'
        ELSE 'cross-window inference permitted by floor only; still no family ranking in WP-9r'
    END AS allowed_claim_type
FROM outcome_ledgers AS o
JOIN candidates AS c
  ON o.candidate_id = c.candidate_id
GROUP BY c.strategy_family, o.candidate_id, o.outcome_kind, o.pipeline_version
ORDER BY
    c.strategy_family,
    o.candidate_id,
    o.outcome_kind,
    CASE o.pipeline_version
        WHEN 'pre_wp_5b' THEN 1
        WHEN 'post_wp_5b' THEN 2
        ELSE 3
    END,
    o.pipeline_version
