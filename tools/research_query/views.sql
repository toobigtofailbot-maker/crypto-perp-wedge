-- What candidates exist and where is their evidence?
-- Derives trial_id_count from the registry trial_ids list. Optional path/count fields remain null
-- for reserved slots.
CREATE OR REPLACE VIEW v_candidate_overview AS
SELECT
    candidate_id,
    name,
    status,
    overall_verdict,
    strategy_family,
    timeframe,
    free_parameter_count,
    pipeline_stage,
    hypothesis_md_path,
    decision_record_path,
    list_count(trial_ids) AS trial_id_count
FROM candidates;

-- Which candidates are concluded and therefore default candidates for comparison?
-- This intentionally excludes reserved/draft slots that do not have reports.
CREATE OR REPLACE VIEW v_concluded_candidates AS
SELECT *
FROM v_candidate_overview
WHERE status = 'CONCLUDED';

-- Which experiment plans have matching reports?
-- Joins reports to plans by plan_id and derives trial_id_count from report trial_ids.
CREATE OR REPLACE VIEW v_experiment_instances AS
SELECT
    p.candidate_id,
    p.plan_id,
    r.report_id,
    p.plan_type,
    r.execution_date,
    r.overall_verdict,
    list_count(r.trial_ids) AS trial_id_count
FROM exp_plans AS p
JOIN exp_reports AS r
  ON p.plan_id = r.plan_id;

-- What out-of-sample metrics are available per concluded candidate?
-- Uses repo-truth report fields: trades is exposed as oos_total_trades and
-- cost_drag_fraction as oos_cost_drag. Reserved slots without reports are excluded.
CREATE OR REPLACE VIEW v_oos_metrics_by_candidate AS
SELECT
    r.candidate_id,
    r.report_id,
    c.strategy_family,
    c.timeframe,
    r.metrics.out_of_sample.sharpe AS oos_sharpe,
    r.metrics.out_of_sample.max_drawdown AS oos_max_drawdown,
    r.metrics.out_of_sample.trades AS oos_total_trades,
    r.metrics.out_of_sample.cost_drag_fraction AS oos_cost_drag
FROM exp_reports AS r
JOIN candidates AS c
  ON r.candidate_id = c.candidate_id
WHERE c.status = 'CONCLUDED';

-- What in-sample metrics are available per concluded candidate?
-- Current report artifacts only carry IS Sharpe and provenance text, so this view
-- does not invent absent drawdown/trade/cost columns.
CREATE OR REPLACE VIEW v_is_metrics_by_candidate AS
SELECT
    r.candidate_id,
    r.report_id,
    c.strategy_family,
    c.timeframe,
    r.metrics.in_sample.sharpe AS is_sharpe,
    r.metrics.in_sample.source_field AS is_source_field,
    r.metrics.in_sample.window_convention AS is_window_convention
FROM exp_reports AS r
JOIN candidates AS c
  ON r.candidate_id = c.candidate_id
WHERE c.status = 'CONCLUDED';

-- Which promotion gates passed or failed across candidates?
-- Unnests the report gate_results array; threshold and observed remain soft typed
-- because artifact schema permits numeric, textual, or null values.
CREATE OR REPLACE VIEW v_gate_results_flat AS
SELECT
    r.candidate_id,
    r.report_id,
    gate.gate_id,
    gate.threshold,
    gate.observed,
    gate.pass
FROM exp_reports AS r,
UNNEST(r.gate_results) AS gates(gate);

-- Which strategy families and timeframes have been tried, and how did they resolve?
-- Verdict buckets are counted from the registry. n_inconclusive is retained for report
-- compatibility even though the current registry verdict enum has no INCONCLUSIVE value.
CREATE OR REPLACE VIEW v_candidate_by_family AS
SELECT
    strategy_family,
    timeframe,
    COUNT(*) AS n_candidates,
    SUM(CASE WHEN overall_verdict = 'NO-GO' THEN 1 ELSE 0 END) AS n_no_go,
    SUM(CASE WHEN overall_verdict = 'PASS' THEN 1 ELSE 0 END) AS n_pass,
    SUM(CASE WHEN overall_verdict = 'CONDITIONAL' THEN 1 ELSE 0 END) AS n_conditional,
    SUM(CASE WHEN overall_verdict = 'INCONCLUSIVE' THEN 1 ELSE 0 END) AS n_inconclusive
FROM candidates
GROUP BY strategy_family, timeframe;

-- Which information inputs have been used by each candidate?
-- Unnests information_inputs. Reserved slots with empty arrays contribute no rows.
CREATE OR REPLACE VIEW v_information_inputs AS
SELECT
    c.candidate_id,
    input.information_input
FROM candidates AS c,
UNNEST(c.information_inputs) AS input(information_input);

-- Are any plan/report pairings broken?
-- Returns EXP rows with no REP and REP rows that reference an unknown plan_id.
-- Expected to be empty in a healthy repo state.
CREATE OR REPLACE VIEW v_integrity_plan_report_pairs AS
SELECT
    'plan_without_report' AS issue_type,
    p.plan_id,
    p.candidate_id,
    NULL AS report_id
FROM exp_plans AS p
LEFT JOIN exp_reports AS r
  ON p.plan_id = r.plan_id
WHERE r.plan_id IS NULL
UNION ALL
SELECT
    'report_without_plan' AS issue_type,
    r.plan_id,
    r.candidate_id,
    r.report_id
FROM exp_reports AS r
LEFT JOIN exp_plans AS p
  ON r.plan_id = p.plan_id
WHERE p.plan_id IS NULL;

-- Do all EXP/REP candidate references resolve to the registry?
-- Returns unresolved candidate references from either artifact family.
-- Expected to be empty in a healthy repo state.
CREATE OR REPLACE VIEW v_integrity_candidate_refs AS
SELECT
    'plan_unknown_candidate' AS issue_type,
    p.candidate_id,
    p.plan_id,
    NULL AS report_id
FROM exp_plans AS p
LEFT JOIN candidates AS c
  ON p.candidate_id = c.candidate_id
WHERE c.candidate_id IS NULL
UNION ALL
SELECT
    'report_unknown_candidate' AS issue_type,
    r.candidate_id,
    r.plan_id,
    r.report_id
FROM exp_reports AS r
LEFT JOIN candidates AS c
  ON r.candidate_id = c.candidate_id
WHERE c.candidate_id IS NULL;
