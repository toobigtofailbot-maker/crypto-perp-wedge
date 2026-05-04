WITH per_candidate AS (
    SELECT
        candidate_id,
        COUNT(*) AS outcome_entry_count,
        string_agg(outcome_id, ' | ' ORDER BY outcome_id) AS outcome_ids,
        string_agg(pipeline_version, ' | ' ORDER BY outcome_id) AS pipeline_versions,
        string_agg(derivation_record.source_artifact_id, ' | ' ORDER BY outcome_id) AS source_reps,
        string_agg(
            (
                SELECT string_agg(CAST(ref_value AS VARCHAR), ' + ' ORDER BY CAST(ref_value AS VARCHAR))
                FROM UNNEST(linked_artifacts) AS refs(ref_value)
                WHERE CAST(ref_value AS VARCHAR) LIKE 'EXP-%'
            ),
            ' | '
            ORDER BY outcome_id
        ) AS source_exps,
        string_agg(
            COALESCE(CAST(evaluation_window_start AS VARCHAR), 'null')
                || '..'
                || COALESCE(CAST(evaluation_window_end AS VARCHAR), 'null'),
            ' | '
            ORDER BY outcome_id
        ) AS evaluation_windows,
        string_agg(
            'sharpe=' || CAST(metrics.sharpe AS VARCHAR)
                || ', max_drawdown=' || CAST(metrics.max_drawdown AS VARCHAR)
                || ', n_obs=' || CAST(metrics.n_obs AS VARCHAR)
                || ', trades=' || CAST(metrics.trades AS VARCHAR),
            ' | '
            ORDER BY outcome_id
        ) AS key_metric_summary
    FROM outcome_ledgers
    GROUP BY candidate_id
)
SELECT
    candidate_id,
    outcome_entry_count,
    outcome_ids,
    pipeline_versions,
    source_reps,
    source_exps,
    evaluation_windows,
    key_metric_summary
FROM per_candidate
ORDER BY candidate_id;
