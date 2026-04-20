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

-- What human approval gate decisions have been recorded?
-- Derives report_id_count from the decision report_ids list. Current zero-instance
-- state returns no rows until decision_change artifacts are authored.
CREATE OR REPLACE VIEW v_decision_changes_overview AS
SELECT
    decision_change_id,
    candidate_id,
    decision,
    stage_transition.from_stage AS from_stage,
    stage_transition.to_stage AS to_stage,
    decided_by,
    decided_at,
    supersedes_decision_id,
    list_count(report_ids) AS report_id_count
FROM decision_changes;

-- What release notes have been recorded for approved stage transitions?
-- Exposes one row per release_notes artifact without expanding monitoring details.
CREATE OR REPLACE VIEW v_release_notes_overview AS
SELECT
    release_notes_id,
    decision_change_id,
    candidate_id,
    released_at,
    released_by,
    effective_stage
FROM release_notes;

-- Which decision changes have release notes, and which remain unreleased?
-- Left-joins release notes to decision changes so decisions without a release remain visible.
CREATE OR REPLACE VIEW v_stage_transitions AS
SELECT
    d.decision_change_id,
    d.candidate_id,
    d.decision,
    d.stage_transition.from_stage AS from_stage,
    d.stage_transition.to_stage AS to_stage,
    d.decided_at,
    r.release_notes_id,
    r.released_at,
    r.effective_stage
FROM decision_changes AS d
LEFT JOIN release_notes AS r
  ON d.decision_change_id = r.decision_change_id;

-- Do all decision_change references resolve to existing structured artifacts?
-- Returns unresolved candidate, report, or superseded decision references.
-- Expected to be empty in a healthy repo state.
CREATE OR REPLACE VIEW v_integrity_decision_refs AS
SELECT
    'decision_unknown_candidate' AS issue_type,
    d.decision_change_id,
    d.candidate_id,
    CAST(NULL AS VARCHAR) AS report_id,
    CAST(NULL AS VARCHAR) AS supersedes_decision_id
FROM decision_changes AS d
LEFT JOIN candidates AS c
  ON d.candidate_id = c.candidate_id
WHERE c.candidate_id IS NULL
UNION ALL
SELECT
    'decision_unknown_report' AS issue_type,
    d.decision_change_id,
    d.candidate_id,
    reports.report_id,
    CAST(NULL AS VARCHAR) AS supersedes_decision_id
FROM decision_changes AS d,
UNNEST(d.report_ids) AS reports(report_id)
LEFT JOIN exp_reports AS r
  ON reports.report_id = r.report_id
WHERE r.report_id IS NULL
UNION ALL
SELECT
    'decision_unknown_supersedes' AS issue_type,
    d.decision_change_id,
    d.candidate_id,
    CAST(NULL AS VARCHAR) AS report_id,
    CAST(d.supersedes_decision_id AS VARCHAR) AS supersedes_decision_id
FROM decision_changes AS d
LEFT JOIN decision_changes AS prior
  ON CAST(d.supersedes_decision_id AS VARCHAR) = prior.decision_change_id
WHERE CAST(d.supersedes_decision_id AS VARCHAR) IS NOT NULL
  AND prior.decision_change_id IS NULL;

-- Do all release_notes references match their approving decision_change artifact?
-- Returns unresolved decision references, candidate mismatches, or effective-stage mismatches.
-- Expected to be empty in a healthy repo state.
CREATE OR REPLACE VIEW v_integrity_release_refs AS
SELECT
    'release_unknown_decision' AS issue_type,
    r.release_notes_id,
    r.decision_change_id,
    r.candidate_id AS release_candidate_id,
    NULL AS decision_candidate_id,
    r.effective_stage,
    NULL AS decision_to_stage
FROM release_notes AS r
LEFT JOIN decision_changes AS d
  ON r.decision_change_id = d.decision_change_id
WHERE d.decision_change_id IS NULL
UNION ALL
SELECT
    'release_candidate_mismatch' AS issue_type,
    r.release_notes_id,
    r.decision_change_id,
    r.candidate_id AS release_candidate_id,
    d.candidate_id AS decision_candidate_id,
    r.effective_stage,
    d.stage_transition.to_stage AS decision_to_stage
FROM release_notes AS r
JOIN decision_changes AS d
  ON r.decision_change_id = d.decision_change_id
WHERE r.candidate_id <> d.candidate_id
UNION ALL
SELECT
    'release_stage_mismatch' AS issue_type,
    r.release_notes_id,
    r.decision_change_id,
    r.candidate_id AS release_candidate_id,
    d.candidate_id AS decision_candidate_id,
    r.effective_stage,
    d.stage_transition.to_stage AS decision_to_stage
FROM release_notes AS r
JOIN decision_changes AS d
  ON r.decision_change_id = d.decision_change_id
WHERE r.effective_stage <> d.stage_transition.to_stage;

-- What deterministic advisory agent outputs have been recorded?
-- Exposes one row per agent_output artifact without expanding input references.
CREATE OR REPLACE VIEW v_agent_outputs_overview AS
SELECT
    agent_output_id,
    agent_type,
    generated_at,
    as_of_timestamp,
    setup_score,
    confidence,
    deterministic
FROM agent_outputs;

-- What is the latest deterministic advisory output per agent family?
-- Uses generated_at as the primary ordering field and artifact ID as a stable tie-breaker.
CREATE OR REPLACE VIEW v_agent_outputs_latest AS
SELECT
    agent_output_id,
    agent_type,
    generated_at,
    as_of_timestamp,
    setup_score,
    confidence,
    deterministic
FROM agent_outputs
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY agent_type
    ORDER BY generated_at DESC, agent_output_id DESC
) = 1;

-- Are agent_output input references structurally well formed?
-- Filesystem existence and sha256 equality are enforced by validate_agent_outputs.py.
-- Expected to be empty in a healthy repo state.
CREATE OR REPLACE VIEW v_integrity_agent_output_refs AS
SELECT
    'agent_output_missing_input_ref' AS issue_type,
    agent_output_id,
    CAST(NULL AS VARCHAR) AS input_path,
    CAST(NULL AS VARCHAR) AS input_sha256,
    CAST(NULL AS VARCHAR) AS input_role
FROM agent_outputs
WHERE list_count(input_data_refs) = 0
UNION ALL
SELECT
    'agent_output_malformed_input_ref' AS issue_type,
    a.agent_output_id,
    input_ref.path AS input_path,
    input_ref.sha256 AS input_sha256,
    input_ref.role AS input_role
FROM agent_outputs AS a,
UNNEST(a.input_data_refs) AS refs(input_ref)
WHERE input_ref.path IS NULL
   OR input_ref.path = ''
   OR regexp_matches(input_ref.path, '(^/|^[A-Za-z]:|\\.\\.)')
   OR input_ref.sha256 IS NULL
   OR NOT regexp_matches(input_ref.sha256, '^[0-9a-f]{64}$')
   OR input_ref.role IS NULL
   OR input_ref.role <> 'fixture_market_snapshot';

-- What deterministic advisory bucket mappings have been recorded?
-- Exposes one row per bucket_mapping artifact without creating overlay contact.
CREATE OR REPLACE VIEW v_bucket_mappings_overview AS
SELECT
    bucket_mapping_id,
    source_agent_output_id,
    agent_type,
    mapped_bucket,
    size_multiplier,
    source_setup_score,
    source_confidence,
    deterministic,
    advisory_only
FROM bucket_mappings;

-- What is the latest deterministic advisory bucket mapping per agent family?
-- Uses generated_at as the primary ordering field and artifact ID as a stable tie-breaker.
CREATE OR REPLACE VIEW v_bucket_mappings_latest AS
SELECT
    bucket_mapping_id,
    source_agent_output_id,
    agent_type,
    mapped_bucket,
    size_multiplier,
    source_setup_score,
    source_confidence,
    deterministic,
    advisory_only
FROM bucket_mappings
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY agent_type
    ORDER BY generated_at DESC, bucket_mapping_id DESC
) = 1;

-- Do all bucket_mapping references and copied source values resolve?
-- Filesystem source existence is also enforced by validate_bucket_mappings.py.
-- Expected to be empty in a healthy repo state.
CREATE OR REPLACE VIEW v_integrity_bucket_mapping_refs AS
SELECT
    'bucket_mapping_unknown_agent_output' AS issue_type,
    b.bucket_mapping_id,
    b.source_agent_output_id,
    CAST(NULL AS VARCHAR) AS source_field,
    CAST(NULL AS VARCHAR) AS expected_value,
    CAST(NULL AS VARCHAR) AS actual_value
FROM bucket_mappings AS b
LEFT JOIN agent_outputs AS a
  ON b.source_agent_output_id = a.agent_output_id
WHERE a.agent_output_id IS NULL
UNION ALL
SELECT
    'bucket_mapping_agent_type_mismatch' AS issue_type,
    b.bucket_mapping_id,
    b.source_agent_output_id,
    'agent_type' AS source_field,
    a.agent_type AS expected_value,
    b.agent_type AS actual_value
FROM bucket_mappings AS b
JOIN agent_outputs AS a
  ON b.source_agent_output_id = a.agent_output_id
WHERE b.agent_type <> a.agent_type
UNION ALL
SELECT
    'bucket_mapping_setup_score_mismatch' AS issue_type,
    b.bucket_mapping_id,
    b.source_agent_output_id,
    'source_setup_score' AS source_field,
    CAST(a.setup_score AS VARCHAR) AS expected_value,
    CAST(b.source_setup_score AS VARCHAR) AS actual_value
FROM bucket_mappings AS b
JOIN agent_outputs AS a
  ON b.source_agent_output_id = a.agent_output_id
WHERE b.source_setup_score <> a.setup_score
UNION ALL
SELECT
    'bucket_mapping_confidence_mismatch' AS issue_type,
    b.bucket_mapping_id,
    b.source_agent_output_id,
    'source_confidence' AS source_field,
    CAST(a.confidence AS VARCHAR) AS expected_value,
    CAST(b.source_confidence AS VARCHAR) AS actual_value
FROM bucket_mappings AS b
JOIN agent_outputs AS a
  ON b.source_agent_output_id = a.agent_output_id
WHERE b.source_confidence <> a.confidence
UNION ALL
SELECT
    'bucket_mapping_illegal_multiplier_pair' AS issue_type,
    bucket_mapping_id,
    source_agent_output_id,
    'mapped_bucket_size_multiplier' AS source_field,
    CASE
        WHEN mapped_bucket = 'ALLOW' THEN '1.0'
        WHEN mapped_bucket = 'ALLOW_REDUCED' THEN '0.5'
        WHEN mapped_bucket = 'BLOCK' THEN '0.0'
        ELSE 'ALLOW|ALLOW_REDUCED|BLOCK'
    END AS expected_value,
    CAST(size_multiplier AS VARCHAR) AS actual_value
FROM bucket_mappings
WHERE (mapped_bucket = 'ALLOW' AND size_multiplier <> 1.0)
   OR (mapped_bucket = 'ALLOW_REDUCED' AND size_multiplier <> 0.5)
   OR (mapped_bucket = 'BLOCK' AND size_multiplier <> 0.0)
   OR mapped_bucket NOT IN ('ALLOW', 'ALLOW_REDUCED', 'BLOCK');
