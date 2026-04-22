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

-- What zero-override overlay shadow comparisons have been recorded?
-- Exposes one row per overlay_shadow_log artifact without creating execution influence.
CREATE OR REPLACE VIEW v_overlay_shadow_logs_overview AS
SELECT
    overlay_shadow_log_id,
    COALESCE(advisory_source, 'BMAP') AS advisory_source,
    source_bucket_mapping_id,
    source_pre_gate_advisory_snapshot_id,
    source_agent_output_id,
    observed_overlay_bucket,
    mapped_bucket,
    size_multiplier,
    comparison_result,
    override_applied,
    fail_open_preserved,
    advisory_only
FROM overlay_shadow_logs;

-- What is the latest overlay shadow comparison per source bucket mapping?
-- Uses observed_at as the primary ordering field and artifact ID as a stable tie-breaker.
CREATE OR REPLACE VIEW v_overlay_shadow_logs_latest AS
SELECT
    overlay_shadow_log_id,
    COALESCE(advisory_source, 'BMAP') AS advisory_source,
    source_bucket_mapping_id,
    source_pre_gate_advisory_snapshot_id,
    source_agent_output_id,
    observed_overlay_bucket,
    mapped_bucket,
    size_multiplier,
    comparison_result,
    override_applied,
    fail_open_preserved,
    advisory_only
FROM overlay_shadow_logs
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY COALESCE(advisory_source, 'BMAP'), source_bucket_mapping_id
    ORDER BY observed_at DESC, overlay_shadow_log_id DESC
) = 1;

-- Do all overlay_shadow_log references and copied source values resolve?
-- Returns unresolved references, source mismatches, or zero-override violations.
-- Expected to be empty in a healthy repo state.
CREATE OR REPLACE VIEW v_integrity_overlay_shadow_refs AS
SELECT
    'overlay_shadow_unknown_bucket_mapping' AS issue_type,
    o.overlay_shadow_log_id,
    COALESCE(o.advisory_source, 'BMAP') AS advisory_source,
    o.source_bucket_mapping_id,
    o.source_pre_gate_advisory_snapshot_id,
    o.source_agent_output_id,
    CAST(NULL AS VARCHAR) AS source_field,
    CAST(NULL AS VARCHAR) AS expected_value,
    CAST(NULL AS VARCHAR) AS actual_value
FROM overlay_shadow_logs AS o
LEFT JOIN bucket_mappings AS b
  ON o.source_bucket_mapping_id = b.bucket_mapping_id
WHERE b.bucket_mapping_id IS NULL
UNION ALL
SELECT
    'overlay_shadow_unknown_agent_output' AS issue_type,
    o.overlay_shadow_log_id,
    COALESCE(o.advisory_source, 'BMAP') AS advisory_source,
    o.source_bucket_mapping_id,
    o.source_pre_gate_advisory_snapshot_id,
    o.source_agent_output_id,
    CAST(NULL AS VARCHAR) AS source_field,
    CAST(NULL AS VARCHAR) AS expected_value,
    CAST(NULL AS VARCHAR) AS actual_value
FROM overlay_shadow_logs AS o
LEFT JOIN agent_outputs AS a
  ON o.source_agent_output_id = a.agent_output_id
WHERE a.agent_output_id IS NULL
UNION ALL
SELECT
    'overlay_shadow_source_agent_output_mismatch' AS issue_type,
    o.overlay_shadow_log_id,
    COALESCE(o.advisory_source, 'BMAP') AS advisory_source,
    o.source_bucket_mapping_id,
    o.source_pre_gate_advisory_snapshot_id,
    o.source_agent_output_id,
    'source_agent_output_id' AS source_field,
    b.source_agent_output_id AS expected_value,
    o.source_agent_output_id AS actual_value
FROM overlay_shadow_logs AS o
JOIN bucket_mappings AS b
  ON o.source_bucket_mapping_id = b.bucket_mapping_id
WHERE o.source_agent_output_id <> b.source_agent_output_id
UNION ALL
SELECT
    'overlay_shadow_mapped_bucket_mismatch' AS issue_type,
    o.overlay_shadow_log_id,
    COALESCE(o.advisory_source, 'BMAP') AS advisory_source,
    o.source_bucket_mapping_id,
    o.source_pre_gate_advisory_snapshot_id,
    o.source_agent_output_id,
    'mapped_bucket' AS source_field,
    b.mapped_bucket AS expected_value,
    o.mapped_bucket AS actual_value
FROM overlay_shadow_logs AS o
JOIN bucket_mappings AS b
  ON o.source_bucket_mapping_id = b.bucket_mapping_id
WHERE COALESCE(o.advisory_source, 'BMAP') <> 'PGAS'
  AND o.mapped_bucket <> b.mapped_bucket
UNION ALL
SELECT
    'overlay_shadow_size_multiplier_mismatch' AS issue_type,
    o.overlay_shadow_log_id,
    COALESCE(o.advisory_source, 'BMAP') AS advisory_source,
    o.source_bucket_mapping_id,
    o.source_pre_gate_advisory_snapshot_id,
    o.source_agent_output_id,
    'size_multiplier' AS source_field,
    CAST(b.size_multiplier AS VARCHAR) AS expected_value,
    CAST(o.size_multiplier AS VARCHAR) AS actual_value
FROM overlay_shadow_logs AS o
JOIN bucket_mappings AS b
  ON o.source_bucket_mapping_id = b.bucket_mapping_id
WHERE COALESCE(o.advisory_source, 'BMAP') <> 'PGAS'
  AND o.size_multiplier <> b.size_multiplier
UNION ALL
SELECT
    'overlay_shadow_unknown_pre_gate_advisory_snapshot' AS issue_type,
    o.overlay_shadow_log_id,
    COALESCE(o.advisory_source, 'BMAP') AS advisory_source,
    o.source_bucket_mapping_id,
    o.source_pre_gate_advisory_snapshot_id,
    o.source_agent_output_id,
    CAST(NULL AS VARCHAR) AS source_field,
    CAST(NULL AS VARCHAR) AS expected_value,
    CAST(NULL AS VARCHAR) AS actual_value
FROM overlay_shadow_logs AS o
LEFT JOIN pre_gate_advisory_snapshots AS p
  ON o.source_pre_gate_advisory_snapshot_id = p.pre_gate_advisory_snapshot_id
WHERE COALESCE(o.advisory_source, 'BMAP') = 'PGAS'
  AND p.pre_gate_advisory_snapshot_id IS NULL
UNION ALL
SELECT
    'overlay_shadow_pre_gate_source_bucket_mapping_mismatch' AS issue_type,
    o.overlay_shadow_log_id,
    COALESCE(o.advisory_source, 'BMAP') AS advisory_source,
    o.source_bucket_mapping_id,
    o.source_pre_gate_advisory_snapshot_id,
    o.source_agent_output_id,
    'source_bucket_mapping_id' AS source_field,
    p.source_bucket_mapping_id AS expected_value,
    o.source_bucket_mapping_id AS actual_value
FROM overlay_shadow_logs AS o
JOIN pre_gate_advisory_snapshots AS p
  ON o.source_pre_gate_advisory_snapshot_id = p.pre_gate_advisory_snapshot_id
WHERE COALESCE(o.advisory_source, 'BMAP') = 'PGAS'
  AND o.source_bucket_mapping_id <> p.source_bucket_mapping_id
UNION ALL
SELECT
    'overlay_shadow_pre_gate_source_agent_output_mismatch' AS issue_type,
    o.overlay_shadow_log_id,
    COALESCE(o.advisory_source, 'BMAP') AS advisory_source,
    o.source_bucket_mapping_id,
    o.source_pre_gate_advisory_snapshot_id,
    o.source_agent_output_id,
    'source_agent_output_id' AS source_field,
    p.source_agent_output_id AS expected_value,
    o.source_agent_output_id AS actual_value
FROM overlay_shadow_logs AS o
JOIN pre_gate_advisory_snapshots AS p
  ON o.source_pre_gate_advisory_snapshot_id = p.pre_gate_advisory_snapshot_id
WHERE COALESCE(o.advisory_source, 'BMAP') = 'PGAS'
  AND o.source_agent_output_id <> p.source_agent_output_id
UNION ALL
SELECT
    'overlay_shadow_pre_gate_combined_bucket_mismatch' AS issue_type,
    o.overlay_shadow_log_id,
    COALESCE(o.advisory_source, 'BMAP') AS advisory_source,
    o.source_bucket_mapping_id,
    o.source_pre_gate_advisory_snapshot_id,
    o.source_agent_output_id,
    'mapped_bucket' AS source_field,
    p.combined_bucket AS expected_value,
    o.mapped_bucket AS actual_value
FROM overlay_shadow_logs AS o
JOIN pre_gate_advisory_snapshots AS p
  ON o.source_pre_gate_advisory_snapshot_id = p.pre_gate_advisory_snapshot_id
WHERE COALESCE(o.advisory_source, 'BMAP') = 'PGAS'
  AND o.mapped_bucket IS DISTINCT FROM p.combined_bucket
UNION ALL
SELECT
    'overlay_shadow_pre_gate_size_multiplier_mismatch' AS issue_type,
    o.overlay_shadow_log_id,
    COALESCE(o.advisory_source, 'BMAP') AS advisory_source,
    o.source_bucket_mapping_id,
    o.source_pre_gate_advisory_snapshot_id,
    o.source_agent_output_id,
    'size_multiplier' AS source_field,
    CASE
        WHEN p.combined_bucket = 'ALLOW' THEN '1.0'
        WHEN p.combined_bucket = 'ALLOW_REDUCED' THEN '0.5'
        WHEN p.combined_bucket = 'BLOCK' THEN '0.0'
        ELSE 'ALLOW|ALLOW_REDUCED|BLOCK'
    END AS expected_value,
    CAST(o.size_multiplier AS VARCHAR) AS actual_value
FROM overlay_shadow_logs AS o
JOIN pre_gate_advisory_snapshots AS p
  ON o.source_pre_gate_advisory_snapshot_id = p.pre_gate_advisory_snapshot_id
WHERE COALESCE(o.advisory_source, 'BMAP') = 'PGAS'
  AND o.size_multiplier IS DISTINCT FROM CASE
      WHEN p.combined_bucket = 'ALLOW' THEN 1.0
      WHEN p.combined_bucket = 'ALLOW_REDUCED' THEN 0.5
      WHEN p.combined_bucket = 'BLOCK' THEN 0.0
      ELSE NULL
  END
UNION ALL
SELECT
    'overlay_shadow_comparison_result_mismatch' AS issue_type,
    overlay_shadow_log_id,
    COALESCE(advisory_source, 'BMAP') AS advisory_source,
    source_bucket_mapping_id,
    source_pre_gate_advisory_snapshot_id,
    source_agent_output_id,
    'comparison_result' AS source_field,
    CASE
        WHEN observed_overlay_bucket = mapped_bucket THEN 'MATCH'
        ELSE 'MISMATCH'
    END AS expected_value,
    comparison_result AS actual_value
FROM overlay_shadow_logs
WHERE comparison_result <> CASE
    WHEN observed_overlay_bucket = mapped_bucket THEN 'MATCH'
    ELSE 'MISMATCH'
END
UNION ALL
SELECT
    'overlay_shadow_override_applied' AS issue_type,
    overlay_shadow_log_id,
    COALESCE(advisory_source, 'BMAP') AS advisory_source,
    source_bucket_mapping_id,
    source_pre_gate_advisory_snapshot_id,
    source_agent_output_id,
    'override_applied' AS source_field,
    'false' AS expected_value,
    CAST(override_applied AS VARCHAR) AS actual_value
FROM overlay_shadow_logs
WHERE override_applied IS DISTINCT FROM false
UNION ALL
SELECT
    'overlay_shadow_fail_open_not_preserved' AS issue_type,
    overlay_shadow_log_id,
    COALESCE(advisory_source, 'BMAP') AS advisory_source,
    source_bucket_mapping_id,
    source_pre_gate_advisory_snapshot_id,
    source_agent_output_id,
    'fail_open_preserved' AS source_field,
    'true' AS expected_value,
    CAST(fail_open_preserved AS VARCHAR) AS actual_value
FROM overlay_shadow_logs
WHERE fail_open_preserved IS DISTINCT FROM true
UNION ALL
SELECT
    'overlay_shadow_not_advisory_only' AS issue_type,
    overlay_shadow_log_id,
    COALESCE(advisory_source, 'BMAP') AS advisory_source,
    source_bucket_mapping_id,
    source_pre_gate_advisory_snapshot_id,
    source_agent_output_id,
    'advisory_only' AS source_field,
    'true' AS expected_value,
    CAST(advisory_only AS VARCHAR) AS actual_value
FROM overlay_shadow_logs
WHERE advisory_only IS DISTINCT FROM true;

-- What agreement/disagreement signal has accumulated across overlay shadow logs?
-- Aggregates by comparison class only; individual row details remain in baseline views.
CREATE OR REPLACE VIEW v_overlay_shadow_agreement_summary AS
SELECT
    COALESCE(advisory_source, 'BMAP') AS advisory_source,
    comparison_result,
    COUNT(*) AS entry_count,
    SUM(CASE WHEN comparison_result = 'MATCH' THEN 1 ELSE 0 END) AS match_count,
    SUM(CASE WHEN comparison_result = 'MISMATCH' THEN 1 ELSE 0 END) AS mismatch_count,
    SUM(CASE WHEN override_applied IS TRUE THEN 1 ELSE 0 END) AS override_true_count,
    strftime('%Y-%m-%dT%H:%M:%SZ', MIN(CAST(observed_at AS TIMESTAMP))) AS first_observed_at,
    strftime('%Y-%m-%dT%H:%M:%SZ', MAX(CAST(observed_at AS TIMESTAMP))) AS last_observed_at
FROM overlay_shadow_logs
GROUP BY COALESCE(advisory_source, 'BMAP'), comparison_result;

-- Are any overlay shadow logs drifting away from strict zero-override behavior?
-- Expected to be empty in a healthy advisory-only shadow state.
CREATE OR REPLACE VIEW v_overlay_shadow_override_audit AS
SELECT
    'overlay_shadow_override_applied' AS issue_type,
    overlay_shadow_log_id,
    COALESCE(advisory_source, 'BMAP') AS advisory_source,
    source_bucket_mapping_id,
    source_pre_gate_advisory_snapshot_id,
    source_agent_output_id,
    'override_applied' AS source_field,
    'false' AS expected_value,
    CAST(override_applied AS VARCHAR) AS actual_value
FROM overlay_shadow_logs
WHERE override_applied IS DISTINCT FROM false
UNION ALL
SELECT
    'overlay_shadow_fail_open_not_preserved' AS issue_type,
    overlay_shadow_log_id,
    COALESCE(advisory_source, 'BMAP') AS advisory_source,
    source_bucket_mapping_id,
    source_pre_gate_advisory_snapshot_id,
    source_agent_output_id,
    'fail_open_preserved' AS source_field,
    'true' AS expected_value,
    CAST(fail_open_preserved AS VARCHAR) AS actual_value
FROM overlay_shadow_logs
WHERE fail_open_preserved IS DISTINCT FROM true
UNION ALL
SELECT
    'overlay_shadow_not_advisory_only' AS issue_type,
    overlay_shadow_log_id,
    COALESCE(advisory_source, 'BMAP') AS advisory_source,
    source_bucket_mapping_id,
    source_pre_gate_advisory_snapshot_id,
    source_agent_output_id,
    'advisory_only' AS source_field,
    'true' AS expected_value,
    CAST(advisory_only AS VARCHAR) AS actual_value
FROM overlay_shadow_logs
WHERE advisory_only IS DISTINCT FROM true;

-- What macro-window advisory outputs have been recorded?
-- Exposes one row per macro_window_agent_output artifact without expanding fixture checks.
CREATE OR REPLACE VIEW v_macro_window_agent_outputs_overview AS
SELECT
    macro_window_agent_output_id,
    macro_window_flag,
    event_class,
    event_name,
    deterministic,
    advisory_only
FROM macro_window_agent_outputs;

-- What is the latest macro-window advisory output?
-- Uses generated_at as the primary ordering field and artifact ID as a stable tie-breaker.
CREATE OR REPLACE VIEW v_macro_window_agent_outputs_latest AS
SELECT
    macro_window_agent_output_id,
    generated_at,
    as_of_timestamp,
    macro_window_flag,
    event_class,
    event_name,
    deterministic,
    advisory_only
FROM macro_window_agent_outputs
QUALIFY ROW_NUMBER() OVER (
    ORDER BY generated_at DESC, macro_window_agent_output_id DESC
) = 1;

-- Are macro_window_agent_output fixture references and advisory flags consistent?
-- Returns missing fixture, hash mismatch, deterministic/advisory violations, or rule mismatch.
-- Expected to be empty in a healthy repo state.
CREATE OR REPLACE VIEW v_integrity_macro_window_agent_output_refs AS
SELECT
    'macro_window_missing_fixture' AS issue_type,
    m.macro_window_agent_output_id,
    m.source_fixture_path,
    'source_fixture_path' AS source_field,
    'exists' AS expected_value,
    CAST(c.source_fixture_exists AS VARCHAR) AS actual_value
FROM macro_window_agent_outputs AS m
LEFT JOIN macro_window_agent_output_fixture_checks AS c
  ON m.macro_window_agent_output_id = c.macro_window_agent_output_id
WHERE c.source_fixture_exists IS DISTINCT FROM true
UNION ALL
SELECT
    'macro_window_source_hash_mismatch' AS issue_type,
    m.macro_window_agent_output_id,
    m.source_fixture_path,
    'source_fixture_sha256' AS source_field,
    m.source_fixture_sha256 AS expected_value,
    c.actual_source_fixture_sha256 AS actual_value
FROM macro_window_agent_outputs AS m
JOIN macro_window_agent_output_fixture_checks AS c
  ON m.macro_window_agent_output_id = c.macro_window_agent_output_id
WHERE c.source_fixture_exists IS TRUE
  AND m.source_fixture_sha256 <> c.actual_source_fixture_sha256
UNION ALL
SELECT
    'macro_window_not_deterministic' AS issue_type,
    macro_window_agent_output_id,
    source_fixture_path,
    'deterministic' AS source_field,
    'true' AS expected_value,
    CAST(deterministic AS VARCHAR) AS actual_value
FROM macro_window_agent_outputs
WHERE deterministic IS DISTINCT FROM true
UNION ALL
SELECT
    'macro_window_not_advisory_only' AS issue_type,
    macro_window_agent_output_id,
    source_fixture_path,
    'advisory_only' AS source_field,
    'true' AS expected_value,
    CAST(advisory_only AS VARCHAR) AS actual_value
FROM macro_window_agent_outputs
WHERE advisory_only IS DISTINCT FROM true
UNION ALL
SELECT
    'macro_window_flag_rule_mismatch' AS issue_type,
    m.macro_window_agent_output_id,
    m.source_fixture_path,
    'macro_window_flag' AS source_field,
    CAST(c.expected_macro_window_flag AS VARCHAR) AS expected_value,
    CAST(m.macro_window_flag AS VARCHAR) AS actual_value
FROM macro_window_agent_outputs AS m
JOIN macro_window_agent_output_fixture_checks AS c
  ON m.macro_window_agent_output_id = c.macro_window_agent_output_id
WHERE c.expected_macro_window_flag IS NOT NULL
  AND m.macro_window_flag IS DISTINCT FROM c.expected_macro_window_flag;

-- What pre-gate advisory snapshots have been recorded?
-- Exposes one row per pre_gate_advisory_snapshot artifact, including applied rule state.
CREATE OR REPLACE VIEW v_pre_gate_advisory_snapshots_overview AS
SELECT
    pre_gate_advisory_snapshot_id,
    source_agent_output_id,
    source_bucket_mapping_id,
    source_macro_window_agent_output_id,
    mapped_bucket,
    size_multiplier,
    macro_window_flag,
    combination_rule_applied,
    combined_bucket,
    deterministic,
    advisory_only
FROM pre_gate_advisory_snapshots;

-- What is the latest pre-gate advisory snapshot?
-- Uses generated_at as the primary ordering field and artifact ID as a stable tie-breaker.
CREATE OR REPLACE VIEW v_pre_gate_advisory_snapshots_latest AS
SELECT
    pre_gate_advisory_snapshot_id,
    generated_at,
    as_of_timestamp,
    source_agent_output_id,
    source_bucket_mapping_id,
    source_macro_window_agent_output_id,
    setup_score,
    confidence,
    mapped_bucket,
    size_multiplier,
    macro_window_flag,
    deterministic,
    advisory_only,
    combination_rule_applied,
    combined_bucket
FROM pre_gate_advisory_snapshots
QUALIFY ROW_NUMBER() OVER (
    ORDER BY generated_at DESC, pre_gate_advisory_snapshot_id DESC
) = 1;

-- Do all pre_gate_advisory_snapshot references and copied source values resolve?
-- Returns missing sources, copied-value mismatches, timestamp-derivation mismatches, or rule violations.
-- Expected to be empty in a healthy repo state.
CREATE OR REPLACE VIEW v_integrity_pre_gate_advisory_snapshot_refs AS
SELECT
    'pre_gate_snapshot_unknown_agent_output' AS issue_type,
    p.pre_gate_advisory_snapshot_id,
    p.source_agent_output_id,
    p.source_bucket_mapping_id,
    p.source_macro_window_agent_output_id,
    CAST(NULL AS VARCHAR) AS source_field,
    CAST(NULL AS VARCHAR) AS expected_value,
    CAST(NULL AS VARCHAR) AS actual_value
FROM pre_gate_advisory_snapshots AS p
LEFT JOIN agent_outputs AS a
  ON p.source_agent_output_id = a.agent_output_id
WHERE a.agent_output_id IS NULL
UNION ALL
SELECT
    'pre_gate_snapshot_unknown_bucket_mapping' AS issue_type,
    p.pre_gate_advisory_snapshot_id,
    p.source_agent_output_id,
    p.source_bucket_mapping_id,
    p.source_macro_window_agent_output_id,
    CAST(NULL AS VARCHAR) AS source_field,
    CAST(NULL AS VARCHAR) AS expected_value,
    CAST(NULL AS VARCHAR) AS actual_value
FROM pre_gate_advisory_snapshots AS p
LEFT JOIN bucket_mappings AS b
  ON p.source_bucket_mapping_id = b.bucket_mapping_id
WHERE b.bucket_mapping_id IS NULL
UNION ALL
SELECT
    'pre_gate_snapshot_unknown_macro_window_agent_output' AS issue_type,
    p.pre_gate_advisory_snapshot_id,
    p.source_agent_output_id,
    p.source_bucket_mapping_id,
    p.source_macro_window_agent_output_id,
    CAST(NULL AS VARCHAR) AS source_field,
    CAST(NULL AS VARCHAR) AS expected_value,
    CAST(NULL AS VARCHAR) AS actual_value
FROM pre_gate_advisory_snapshots AS p
LEFT JOIN macro_window_agent_outputs AS m
  ON p.source_macro_window_agent_output_id = m.macro_window_agent_output_id
WHERE m.macro_window_agent_output_id IS NULL
UNION ALL
SELECT
    'pre_gate_snapshot_source_agent_output_mismatch' AS issue_type,
    p.pre_gate_advisory_snapshot_id,
    p.source_agent_output_id,
    p.source_bucket_mapping_id,
    p.source_macro_window_agent_output_id,
    'source_agent_output_id' AS source_field,
    b.source_agent_output_id AS expected_value,
    p.source_agent_output_id AS actual_value
FROM pre_gate_advisory_snapshots AS p
JOIN bucket_mappings AS b
  ON p.source_bucket_mapping_id = b.bucket_mapping_id
WHERE p.source_agent_output_id <> b.source_agent_output_id
UNION ALL
SELECT
    'pre_gate_snapshot_setup_score_mismatch' AS issue_type,
    p.pre_gate_advisory_snapshot_id,
    p.source_agent_output_id,
    p.source_bucket_mapping_id,
    p.source_macro_window_agent_output_id,
    'setup_score' AS source_field,
    CAST(a.setup_score AS VARCHAR) AS expected_value,
    CAST(p.setup_score AS VARCHAR) AS actual_value
FROM pre_gate_advisory_snapshots AS p
JOIN agent_outputs AS a
  ON p.source_agent_output_id = a.agent_output_id
WHERE p.setup_score <> a.setup_score
UNION ALL
SELECT
    'pre_gate_snapshot_confidence_mismatch' AS issue_type,
    p.pre_gate_advisory_snapshot_id,
    p.source_agent_output_id,
    p.source_bucket_mapping_id,
    p.source_macro_window_agent_output_id,
    'confidence' AS source_field,
    CAST(a.confidence AS VARCHAR) AS expected_value,
    CAST(p.confidence AS VARCHAR) AS actual_value
FROM pre_gate_advisory_snapshots AS p
JOIN agent_outputs AS a
  ON p.source_agent_output_id = a.agent_output_id
WHERE p.confidence <> a.confidence
UNION ALL
SELECT
    'pre_gate_snapshot_mapped_bucket_mismatch' AS issue_type,
    p.pre_gate_advisory_snapshot_id,
    p.source_agent_output_id,
    p.source_bucket_mapping_id,
    p.source_macro_window_agent_output_id,
    'mapped_bucket' AS source_field,
    b.mapped_bucket AS expected_value,
    p.mapped_bucket AS actual_value
FROM pre_gate_advisory_snapshots AS p
JOIN bucket_mappings AS b
  ON p.source_bucket_mapping_id = b.bucket_mapping_id
WHERE p.mapped_bucket <> b.mapped_bucket
UNION ALL
SELECT
    'pre_gate_snapshot_size_multiplier_mismatch' AS issue_type,
    p.pre_gate_advisory_snapshot_id,
    p.source_agent_output_id,
    p.source_bucket_mapping_id,
    p.source_macro_window_agent_output_id,
    'size_multiplier' AS source_field,
    CAST(b.size_multiplier AS VARCHAR) AS expected_value,
    CAST(p.size_multiplier AS VARCHAR) AS actual_value
FROM pre_gate_advisory_snapshots AS p
JOIN bucket_mappings AS b
  ON p.source_bucket_mapping_id = b.bucket_mapping_id
WHERE p.size_multiplier <> b.size_multiplier
UNION ALL
SELECT
    'pre_gate_snapshot_macro_window_flag_mismatch' AS issue_type,
    p.pre_gate_advisory_snapshot_id,
    p.source_agent_output_id,
    p.source_bucket_mapping_id,
    p.source_macro_window_agent_output_id,
    'macro_window_flag' AS source_field,
    CAST(m.macro_window_flag AS VARCHAR) AS expected_value,
    CAST(p.macro_window_flag AS VARCHAR) AS actual_value
FROM pre_gate_advisory_snapshots AS p
JOIN macro_window_agent_outputs AS m
  ON p.source_macro_window_agent_output_id = m.macro_window_agent_output_id
WHERE p.macro_window_flag IS DISTINCT FROM m.macro_window_flag
UNION ALL
SELECT
    'pre_gate_snapshot_generated_at_mismatch' AS issue_type,
    p.pre_gate_advisory_snapshot_id,
    p.source_agent_output_id,
    p.source_bucket_mapping_id,
    p.source_macro_window_agent_output_id,
    'generated_at' AS source_field,
    strftime(
        '%Y-%m-%dT%H:%M:%SZ',
        GREATEST(
            CAST(a.generated_at AS TIMESTAMP),
            CAST(b.generated_at AS TIMESTAMP),
            CAST(m.generated_at AS TIMESTAMP)
        )
    ) AS expected_value,
    p.generated_at AS actual_value
FROM pre_gate_advisory_snapshots AS p
JOIN agent_outputs AS a
  ON p.source_agent_output_id = a.agent_output_id
JOIN bucket_mappings AS b
  ON p.source_bucket_mapping_id = b.bucket_mapping_id
JOIN macro_window_agent_outputs AS m
  ON p.source_macro_window_agent_output_id = m.macro_window_agent_output_id
WHERE p.generated_at <> strftime(
    '%Y-%m-%dT%H:%M:%SZ',
    GREATEST(
        CAST(a.generated_at AS TIMESTAMP),
        CAST(b.generated_at AS TIMESTAMP),
        CAST(m.generated_at AS TIMESTAMP)
    )
)
UNION ALL
SELECT
    'pre_gate_snapshot_as_of_timestamp_mismatch' AS issue_type,
    p.pre_gate_advisory_snapshot_id,
    p.source_agent_output_id,
    p.source_bucket_mapping_id,
    p.source_macro_window_agent_output_id,
    'as_of_timestamp' AS source_field,
    strftime(
        '%Y-%m-%dT%H:%M:%SZ',
        GREATEST(
            CAST(a.as_of_timestamp AS TIMESTAMP),
            CAST(b.as_of_timestamp AS TIMESTAMP),
            CAST(m.as_of_timestamp AS TIMESTAMP)
        )
    ) AS expected_value,
    p.as_of_timestamp AS actual_value
FROM pre_gate_advisory_snapshots AS p
JOIN agent_outputs AS a
  ON p.source_agent_output_id = a.agent_output_id
JOIN bucket_mappings AS b
  ON p.source_bucket_mapping_id = b.bucket_mapping_id
JOIN macro_window_agent_outputs AS m
  ON p.source_macro_window_agent_output_id = m.macro_window_agent_output_id
WHERE p.as_of_timestamp <> strftime(
    '%Y-%m-%dT%H:%M:%SZ',
    GREATEST(
        CAST(a.as_of_timestamp AS TIMESTAMP),
        CAST(b.as_of_timestamp AS TIMESTAMP),
        CAST(m.as_of_timestamp AS TIMESTAMP)
    )
)
UNION ALL
SELECT
    'pre_gate_snapshot_not_deterministic' AS issue_type,
    pre_gate_advisory_snapshot_id,
    source_agent_output_id,
    source_bucket_mapping_id,
    source_macro_window_agent_output_id,
    'deterministic' AS source_field,
    'true' AS expected_value,
    CAST(deterministic AS VARCHAR) AS actual_value
FROM pre_gate_advisory_snapshots
WHERE deterministic IS DISTINCT FROM true
UNION ALL
SELECT
    'pre_gate_snapshot_not_advisory_only' AS issue_type,
    pre_gate_advisory_snapshot_id,
    source_agent_output_id,
    source_bucket_mapping_id,
    source_macro_window_agent_output_id,
    'advisory_only' AS source_field,
    'true' AS expected_value,
    CAST(advisory_only AS VARCHAR) AS actual_value
FROM pre_gate_advisory_snapshots
WHERE advisory_only IS DISTINCT FROM true
UNION ALL
SELECT
    'pre_gate_snapshot_invalid_combination_rule' AS issue_type,
    pre_gate_advisory_snapshot_id,
    source_agent_output_id,
    source_bucket_mapping_id,
    source_macro_window_agent_output_id,
    'combination_rule_applied' AS source_field,
    'NONE_BUNDLE_ONLY|MACRO_AWARE_FLOOR' AS expected_value,
    combination_rule_applied AS actual_value
FROM pre_gate_advisory_snapshots
WHERE combination_rule_applied IS NULL
   OR combination_rule_applied NOT IN ('NONE_BUNDLE_ONLY', 'MACRO_AWARE_FLOOR')
UNION ALL
SELECT
    'pre_gate_snapshot_unexpected_combined_bucket' AS issue_type,
    pre_gate_advisory_snapshot_id,
    source_agent_output_id,
    source_bucket_mapping_id,
    source_macro_window_agent_output_id,
    'combined_bucket' AS source_field,
    CAST(NULL AS VARCHAR) AS expected_value,
    combined_bucket AS actual_value
FROM pre_gate_advisory_snapshots
WHERE combination_rule_applied = 'NONE_BUNDLE_ONLY'
  AND combined_bucket IS NOT NULL
UNION ALL
SELECT
    'pre_gate_snapshot_combined_bucket_mismatch' AS issue_type,
    p.pre_gate_advisory_snapshot_id,
    p.source_agent_output_id,
    p.source_bucket_mapping_id,
    p.source_macro_window_agent_output_id,
    'combined_bucket' AS source_field,
    CASE
        WHEN m.macro_window_flag IS DISTINCT FROM true THEN b.mapped_bucket
        WHEN b.mapped_bucket = 'ALLOW' THEN 'ALLOW_REDUCED'
        ELSE b.mapped_bucket
    END AS expected_value,
    p.combined_bucket AS actual_value
FROM pre_gate_advisory_snapshots AS p
JOIN bucket_mappings AS b
  ON p.source_bucket_mapping_id = b.bucket_mapping_id
JOIN macro_window_agent_outputs AS m
  ON p.source_macro_window_agent_output_id = m.macro_window_agent_output_id
WHERE p.combination_rule_applied = 'MACRO_AWARE_FLOOR'
  AND p.combined_bucket IS DISTINCT FROM CASE
      WHEN m.macro_window_flag IS DISTINCT FROM true THEN b.mapped_bucket
      WHEN b.mapped_bucket = 'ALLOW' THEN 'ALLOW_REDUCED'
      ELSE b.mapped_bucket
  END;
