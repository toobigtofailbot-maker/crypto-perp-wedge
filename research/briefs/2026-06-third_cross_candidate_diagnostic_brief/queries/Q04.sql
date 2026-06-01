-- D2-006 gate failure/pass pattern across experiment reports including REP-0032.
WITH gate_counts AS (
    SELECT
        gate_id,
        COUNT(*) AS gate_result_rows,
        COUNT(*) FILTER (WHERE pass) AS pass_count,
        COUNT(*) FILTER (WHERE NOT pass) AS fail_count,
        COUNT(DISTINCT candidate_id) AS distinct_candidates,
        string_agg(DISTINCT candidate_id, ', ' ORDER BY candidate_id) AS candidate_ids
    FROM v_gate_results_flat
    WHERE gate_id LIKE 'D2-006%'
    GROUP BY gate_id
),
h012_gate_counts AS (
    SELECT
        candidate_id,
        report_id,
        COUNT(*) AS gate_result_rows,
        COUNT(*) FILTER (WHERE pass) AS pass_count,
        COUNT(*) FILTER (WHERE NOT pass) AS fail_count
    FROM v_gate_results_flat
    WHERE candidate_id = 'H-012'
      AND gate_id LIKE 'D2-006%'
    GROUP BY candidate_id, report_id
)
SELECT
    'all_reports_gate_pattern' AS row_type,
    gate_id,
    gate_result_rows,
    pass_count,
    fail_count,
    distinct_candidates,
    candidate_ids,
    NULL AS candidate_id,
    NULL AS report_id
FROM gate_counts
UNION ALL
SELECT
    'h012_report_gate_summary' AS row_type,
    NULL AS gate_id,
    gate_result_rows,
    pass_count,
    fail_count,
    NULL AS distinct_candidates,
    NULL AS candidate_ids,
    candidate_id,
    report_id
FROM h012_gate_counts
ORDER BY row_type, gate_id, candidate_id;
