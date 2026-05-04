SELECT
    candidate_id,
    outcome_kind,
    pipeline_version,
    COUNT(*) AS window_count,
    3 AS inference_floor,
    CASE
        WHEN COUNT(*) >= 3 THEN 'SUFFICIENT_FOR_CROSS_WINDOW_INFERENCE'
        ELSE 'INSUFFICIENT_EVIDENCE'
    END AS floor_status,
    CASE
        WHEN COUNT(*) >= 3 THEN 'cross-window inference permitted by OL-4'
        ELSE 'single-window factual observation only'
    END AS allowed_claim_type
FROM outcome_ledgers
GROUP BY candidate_id, outcome_kind, pipeline_version
ORDER BY candidate_id, outcome_kind, pipeline_version;
