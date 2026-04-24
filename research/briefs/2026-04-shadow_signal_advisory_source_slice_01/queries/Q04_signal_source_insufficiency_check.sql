WITH source_rollup AS (
    SELECT
        advisory_source,
        SUM(match_count) AS total_match_count,
        SUM(mismatch_count) AS total_mismatch_count,
        SUM(observation_count) AS observation_count
    FROM v_shadow_signal_summaries_overview
    WHERE shadow_signal_summary_id = 'SSS-0001'
      AND advisory_source IN ('BMAP', 'PGAS')
    GROUP BY advisory_source
)
SELECT
    advisory_source,
    observation_count,
    10 AS floor_required,
    CASE
        WHEN observation_count < 10 THEN true
        ELSE false
    END AS insufficient_evidence,
    CASE
        WHEN observation_count < 10 THEN 'INSUFFICIENT_EVIDENCE'
        WHEN total_match_count > total_mismatch_count THEN 'AGREEMENT_SIGNAL'
        WHEN total_mismatch_count > total_match_count THEN 'DISAGREEMENT_SIGNAL'
        ELSE 'MIXED_SIGNAL'
    END AS signal_outcome
FROM source_rollup
ORDER BY advisory_source;
