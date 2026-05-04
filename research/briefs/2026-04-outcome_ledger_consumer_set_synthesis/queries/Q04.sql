WITH segments AS (
    SELECT
        candidate_id,
        outcome_kind,
        pipeline_version,
        COUNT(*) AS window_count
    FROM outcome_ledgers
    GROUP BY candidate_id, outcome_kind, pipeline_version
)
SELECT
    COUNT(*) AS total_segments,
    SUM(CASE WHEN window_count < 3 THEN 1 ELSE 0 END) AS below_floor_segments,
    SUM(CASE WHEN window_count >= 3 THEN 1 ELSE 0 END) AS at_or_above_floor_segments,
    'n >= 3 per candidate / outcome_kind / pipeline_version before cross-window inference' AS inference_floor,
    CASE
        WHEN SUM(CASE WHEN window_count >= 3 THEN 1 ELSE 0 END) = 0
            THEN 'INSUFFICIENT_EVIDENCE for every current segment'
        ELSE 'one or more segments meet the floor'
    END AS floor_status_summary,
    'consumer grouping by candidate, pipeline version, or strategy family does not lower OL-4; no retrospective special-case lowering' AS grouping_boundary
FROM segments
