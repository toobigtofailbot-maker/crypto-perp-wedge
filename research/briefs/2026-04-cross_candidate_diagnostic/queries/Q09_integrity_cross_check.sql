SELECT
    'v_integrity_plan_report_pairs' AS integrity_view,
    issue_type,
    candidate_id,
    plan_id,
    report_id
FROM v_integrity_plan_report_pairs
UNION ALL
SELECT
    'v_integrity_candidate_refs' AS integrity_view,
    issue_type,
    candidate_id,
    plan_id,
    report_id
FROM v_integrity_candidate_refs
ORDER BY integrity_view, issue_type, candidate_id, plan_id, report_id;
