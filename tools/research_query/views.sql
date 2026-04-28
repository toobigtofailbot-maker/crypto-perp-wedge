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

-- What Phase 9 lifecycle changes have been recorded?
-- Exposes one row per LCH artifact without expanding evidence or advisory references.
CREATE OR REPLACE VIEW v_lifecycle_change_overview AS
SELECT
    lifecycle_change_id,
    schema_version,
    candidate_id,
    from_state,
    to_state,
    transition_edge,
    decided_by,
    decided_at,
    supersedes_lch_id,
    COALESCE(retrospective_flag, false) AS retrospective_flag,
    COALESCE(fast_track_flag, false) AS fast_track_flag,
    list_count(evidence_artifact_refs) AS evidence_ref_count,
    list_count(linked_advisory_artifacts) AS linked_advisory_ref_count,
    list_count(strong_candidate_criteria_refs) AS strong_candidate_criteria_ref_count
FROM lifecycle_changes;

-- How many lifecycle transitions have been recorded per permitted edge?
CREATE OR REPLACE VIEW v_lifecycle_state_transitions AS
SELECT
    from_state,
    to_state,
    transition_edge,
    COUNT(*) AS transition_count
FROM lifecycle_changes
GROUP BY from_state, to_state, transition_edge;

-- Do all lifecycle_change candidate, supersession, and known-pattern artifact references resolve?
-- Repo-relative path existence remains validator-only because SQL has no repo filesystem authority.
-- Expected to be empty in a healthy repo state.
CREATE OR REPLACE VIEW v_integrity_lifecycle_change_refs AS
WITH lifecycle_refs AS (
    SELECT
        lifecycle_change_id,
        candidate_id,
        'evidence_artifact_refs' AS ref_kind,
        ref.ref_value
    FROM lifecycle_changes,
    UNNEST(evidence_artifact_refs) AS ref(ref_value)
    UNION ALL
    SELECT
        lifecycle_change_id,
        candidate_id,
        'linked_advisory_artifacts' AS ref_kind,
        ref.ref_value
    FROM lifecycle_changes,
    UNNEST(linked_advisory_artifacts) AS ref(ref_value)
),
known_ref_issues AS (
    SELECT
        'lifecycle_unknown_exp_ref' AS issue_type,
        l.lifecycle_change_id,
        l.candidate_id,
        l.ref_kind,
        l.ref_value
    FROM lifecycle_refs AS l
    LEFT JOIN exp_plans AS p
      ON l.ref_value = p.plan_id
    WHERE regexp_matches(l.ref_value, '^EXP-[0-9]{4}$')
      AND p.plan_id IS NULL
    UNION ALL
    SELECT
        'lifecycle_unknown_rep_ref' AS issue_type,
        l.lifecycle_change_id,
        l.candidate_id,
        l.ref_kind,
        l.ref_value
    FROM lifecycle_refs AS l
    LEFT JOIN exp_reports AS r
      ON l.ref_value = r.report_id
    WHERE regexp_matches(l.ref_value, '^REP-[0-9]{4}$')
      AND r.report_id IS NULL
    UNION ALL
    SELECT
        'lifecycle_unknown_dch_ref' AS issue_type,
        l.lifecycle_change_id,
        l.candidate_id,
        l.ref_kind,
        l.ref_value
    FROM lifecycle_refs AS l
    LEFT JOIN decision_changes AS d
      ON l.ref_value = d.decision_change_id
    WHERE regexp_matches(l.ref_value, '^DCH-[0-9]{4}$')
      AND d.decision_change_id IS NULL
    UNION ALL
    SELECT
        'lifecycle_unknown_rel_ref' AS issue_type,
        l.lifecycle_change_id,
        l.candidate_id,
        l.ref_kind,
        l.ref_value
    FROM lifecycle_refs AS l
    LEFT JOIN release_notes AS r
      ON l.ref_value = r.release_notes_id
    WHERE regexp_matches(l.ref_value, '^REL-[0-9]{4}$')
      AND r.release_notes_id IS NULL
    UNION ALL
    SELECT
        'lifecycle_unknown_aout_ref' AS issue_type,
        l.lifecycle_change_id,
        l.candidate_id,
        l.ref_kind,
        l.ref_value
    FROM lifecycle_refs AS l
    LEFT JOIN agent_outputs AS a
      ON l.ref_value = a.agent_output_id
    WHERE regexp_matches(l.ref_value, '^AOUT-[0-9]{4}$')
      AND a.agent_output_id IS NULL
    UNION ALL
    SELECT
        'lifecycle_unknown_mout_ref' AS issue_type,
        l.lifecycle_change_id,
        l.candidate_id,
        l.ref_kind,
        l.ref_value
    FROM lifecycle_refs AS l
    LEFT JOIN macro_window_agent_outputs AS m
      ON l.ref_value = m.macro_window_agent_output_id
    WHERE regexp_matches(l.ref_value, '^MOUT-[0-9]{4}$')
      AND m.macro_window_agent_output_id IS NULL
    UNION ALL
    SELECT
        'lifecycle_unknown_bmap_ref' AS issue_type,
        l.lifecycle_change_id,
        l.candidate_id,
        l.ref_kind,
        l.ref_value
    FROM lifecycle_refs AS l
    LEFT JOIN bucket_mappings AS b
      ON l.ref_value = b.bucket_mapping_id
    WHERE regexp_matches(l.ref_value, '^BMAP-[0-9]{4}$')
      AND b.bucket_mapping_id IS NULL
    UNION ALL
    SELECT
        'lifecycle_unknown_pgas_ref' AS issue_type,
        l.lifecycle_change_id,
        l.candidate_id,
        l.ref_kind,
        l.ref_value
    FROM lifecycle_refs AS l
    LEFT JOIN pre_gate_advisory_snapshots AS p
      ON l.ref_value = p.pre_gate_advisory_snapshot_id
    WHERE regexp_matches(l.ref_value, '^PGAS-[0-9]{4}$')
      AND p.pre_gate_advisory_snapshot_id IS NULL
    UNION ALL
    SELECT
        'lifecycle_unknown_osh_ref' AS issue_type,
        l.lifecycle_change_id,
        l.candidate_id,
        l.ref_kind,
        l.ref_value
    FROM lifecycle_refs AS l
    LEFT JOIN overlay_shadow_logs AS o
      ON l.ref_value = o.overlay_shadow_log_id
    WHERE regexp_matches(l.ref_value, '^OSH-[0-9]{4}$')
      AND o.overlay_shadow_log_id IS NULL
    UNION ALL
    SELECT
        'lifecycle_unknown_sss_ref' AS issue_type,
        l.lifecycle_change_id,
        l.candidate_id,
        l.ref_kind,
        l.ref_value
    FROM lifecycle_refs AS l
    LEFT JOIN shadow_signal_summaries AS s1
      ON l.ref_value = s1.shadow_signal_summary_id
    LEFT JOIN shadow_signal_summaries_v2 AS s2
      ON l.ref_value = s2.shadow_signal_summary_id
    WHERE regexp_matches(l.ref_value, '^SSS-[0-9]{4}$')
      AND s1.shadow_signal_summary_id IS NULL
      AND s2.shadow_signal_summary_id IS NULL
    UNION ALL
    SELECT
        'lifecycle_unknown_lch_ref' AS issue_type,
        l.lifecycle_change_id,
        l.candidate_id,
        l.ref_kind,
        l.ref_value
    FROM lifecycle_refs AS l
    LEFT JOIN lifecycle_changes AS prior
      ON l.ref_value = prior.lifecycle_change_id
    WHERE regexp_matches(l.ref_value, '^LCH-[0-9]{4}$')
      AND prior.lifecycle_change_id IS NULL
)
SELECT
    'lifecycle_unknown_candidate' AS issue_type,
    l.lifecycle_change_id,
    l.candidate_id,
    CAST(NULL AS VARCHAR) AS ref_kind,
    CAST(NULL AS VARCHAR) AS ref_value
FROM lifecycle_changes AS l
LEFT JOIN candidates AS c
  ON l.candidate_id = c.candidate_id
WHERE c.candidate_id IS NULL
UNION ALL
SELECT
    'lifecycle_unknown_supersedes' AS issue_type,
    l.lifecycle_change_id,
    l.candidate_id,
    'supersedes_lch_id' AS ref_kind,
    CAST(l.supersedes_lch_id AS VARCHAR) AS ref_value
FROM lifecycle_changes AS l
LEFT JOIN lifecycle_changes AS prior
  ON CAST(l.supersedes_lch_id AS VARCHAR) = prior.lifecycle_change_id
WHERE CAST(l.supersedes_lch_id AS VARCHAR) IS NOT NULL
  AND prior.lifecycle_change_id IS NULL
UNION ALL
SELECT *
FROM known_ref_issues;

-- Do lifecycle transitions match the Phase 9 v1 transition graph local shape?
-- Historical proof of halted recovery to the immediately previous non-halted state remains deferred.
-- Expected to be empty in a healthy repo state.
CREATE OR REPLACE VIEW v_integrity_lifecycle_transition_graph AS
SELECT
    CASE
        WHEN from_state = 'archived' THEN 'lifecycle_archived_outbound_transition'
        WHEN transition_edge NOT IN (
            'proposed->in_research',
            'proposed->halted',
            'in_research->research_concluded',
            'in_research->halted',
            'research_concluded->paper_eligible',
            'research_concluded->archived',
            'research_concluded->halted',
            'paper_eligible->paper_active',
            'paper_eligible->archived',
            'paper_eligible->halted',
            'paper_active->paper_concluded',
            'paper_active->halted',
            'paper_active->archived',
            'paper_concluded->live_eligible',
            'paper_concluded->archived',
            'paper_concluded->halted',
            'live_eligible->live_active',
            'live_eligible->archived',
            'live_eligible->halted',
            'live_active->paper_concluded',
            'live_active->halted',
            'live_active->archived',
            'halted->archived',
            'halted->previous_non_halted_state'
        ) THEN 'lifecycle_unknown_transition_edge'
        ELSE 'lifecycle_transition_shape_mismatch'
    END AS issue_type,
    lifecycle_change_id,
    candidate_id,
    from_state,
    to_state,
    transition_edge
FROM lifecycle_changes
WHERE from_state = 'archived'
   OR transition_edge NOT IN (
       'proposed->in_research',
       'proposed->halted',
       'in_research->research_concluded',
       'in_research->halted',
       'research_concluded->paper_eligible',
       'research_concluded->archived',
       'research_concluded->halted',
       'paper_eligible->paper_active',
       'paper_eligible->archived',
       'paper_eligible->halted',
       'paper_active->paper_concluded',
       'paper_active->halted',
       'paper_active->archived',
       'paper_concluded->live_eligible',
       'paper_concluded->archived',
       'paper_concluded->halted',
       'live_eligible->live_active',
       'live_eligible->archived',
       'live_eligible->halted',
       'live_active->paper_concluded',
       'live_active->halted',
       'live_active->archived',
       'halted->archived',
       'halted->previous_non_halted_state'
   )
   OR (transition_edge = 'proposed->in_research' AND (from_state <> 'proposed' OR to_state <> 'in_research'))
   OR (transition_edge = 'proposed->halted' AND (from_state <> 'proposed' OR to_state <> 'halted'))
   OR (transition_edge = 'in_research->research_concluded' AND (from_state <> 'in_research' OR to_state <> 'research_concluded'))
   OR (transition_edge = 'in_research->halted' AND (from_state <> 'in_research' OR to_state <> 'halted'))
   OR (transition_edge = 'research_concluded->paper_eligible' AND (from_state <> 'research_concluded' OR to_state <> 'paper_eligible'))
   OR (transition_edge = 'research_concluded->archived' AND (from_state <> 'research_concluded' OR to_state <> 'archived'))
   OR (transition_edge = 'research_concluded->halted' AND (from_state <> 'research_concluded' OR to_state <> 'halted'))
   OR (transition_edge = 'paper_eligible->paper_active' AND (from_state <> 'paper_eligible' OR to_state <> 'paper_active'))
   OR (transition_edge = 'paper_eligible->archived' AND (from_state <> 'paper_eligible' OR to_state <> 'archived'))
   OR (transition_edge = 'paper_eligible->halted' AND (from_state <> 'paper_eligible' OR to_state <> 'halted'))
   OR (transition_edge = 'paper_active->paper_concluded' AND (from_state <> 'paper_active' OR to_state <> 'paper_concluded'))
   OR (transition_edge = 'paper_active->halted' AND (from_state <> 'paper_active' OR to_state <> 'halted'))
   OR (transition_edge = 'paper_active->archived' AND (from_state <> 'paper_active' OR to_state <> 'archived'))
   OR (transition_edge = 'paper_concluded->live_eligible' AND (from_state <> 'paper_concluded' OR to_state <> 'live_eligible'))
   OR (transition_edge = 'paper_concluded->archived' AND (from_state <> 'paper_concluded' OR to_state <> 'archived'))
   OR (transition_edge = 'paper_concluded->halted' AND (from_state <> 'paper_concluded' OR to_state <> 'halted'))
   OR (transition_edge = 'live_eligible->live_active' AND (from_state <> 'live_eligible' OR to_state <> 'live_active'))
   OR (transition_edge = 'live_eligible->archived' AND (from_state <> 'live_eligible' OR to_state <> 'archived'))
   OR (transition_edge = 'live_eligible->halted' AND (from_state <> 'live_eligible' OR to_state <> 'halted'))
   OR (transition_edge = 'live_active->paper_concluded' AND (from_state <> 'live_active' OR to_state <> 'paper_concluded'))
   OR (transition_edge = 'live_active->halted' AND (from_state <> 'live_active' OR to_state <> 'halted'))
   OR (transition_edge = 'live_active->archived' AND (from_state <> 'live_active' OR to_state <> 'archived'))
   OR (transition_edge = 'halted->archived' AND (from_state <> 'halted' OR to_state <> 'archived'))
   OR (
       transition_edge = 'halted->previous_non_halted_state'
       AND (
           from_state <> 'halted'
           OR to_state NOT IN (
               'proposed',
               'in_research',
               'research_concluded',
               'paper_eligible',
               'paper_active',
               'paper_concluded',
               'live_eligible',
               'live_active'
           )
       )
   );

-- Are lifecycle approval fields structurally complete for consequential transitions?
-- Expected to be empty in a healthy repo state.
CREATE OR REPLACE VIEW v_integrity_lifecycle_approval_completeness AS
SELECT
    'lifecycle_operational_transition_missing_evidence' AS issue_type,
    lifecycle_change_id,
    candidate_id,
    'evidence_artifact_refs' AS field_name
FROM lifecycle_changes
WHERE to_state IN ('paper_active', 'live_eligible', 'live_active')
  AND list_count(evidence_artifact_refs) = 0
UNION ALL
SELECT
    'lifecycle_halted_recovery_missing_evidence' AS issue_type,
    lifecycle_change_id,
    candidate_id,
    'evidence_artifact_refs' AS field_name
FROM lifecycle_changes
WHERE from_state = 'halted'
  AND to_state <> 'archived'
  AND list_count(evidence_artifact_refs) = 0
UNION ALL
SELECT
    'lifecycle_missing_risk_acknowledgment' AS issue_type,
    lifecycle_change_id,
    candidate_id,
    'risk_acknowledgment' AS field_name
FROM lifecycle_changes
WHERE risk_acknowledgment IS NULL
   OR trim(CAST(risk_acknowledgment AS VARCHAR)) = ''
UNION ALL
SELECT
    'lifecycle_missing_decided_by' AS issue_type,
    lifecycle_change_id,
    candidate_id,
    'decided_by' AS field_name
FROM lifecycle_changes
WHERE decided_by IS NULL
   OR trim(CAST(decided_by AS VARCHAR)) = ''
UNION ALL
SELECT
    'lifecycle_missing_decided_at' AS issue_type,
    lifecycle_change_id,
    candidate_id,
    'decided_at' AS field_name
FROM lifecycle_changes
WHERE decided_at IS NULL
   OR trim(CAST(decided_at AS VARCHAR)) = '';

-- Are lifecycle fast-track records structurally complete without encoding promotion policy?
-- Expected to be empty in a healthy repo state.
CREATE OR REPLACE VIEW v_integrity_lifecycle_fast_track_completeness AS
SELECT
    'lifecycle_fast_track_wrong_to_state' AS issue_type,
    lifecycle_change_id,
    candidate_id,
    'to_state' AS field_name
FROM lifecycle_changes
WHERE fast_track_flag IS TRUE
  AND to_state <> 'live_eligible'
UNION ALL
SELECT
    'lifecycle_fast_track_missing_strong_candidate_criteria' AS issue_type,
    lifecycle_change_id,
    candidate_id,
    'strong_candidate_criteria_refs' AS field_name
FROM lifecycle_changes
WHERE fast_track_flag IS TRUE
  AND list_count(strong_candidate_criteria_refs) = 0
UNION ALL
SELECT
    'lifecycle_fast_track_missing_evidence' AS issue_type,
    lifecycle_change_id,
    candidate_id,
    'evidence_artifact_refs' AS field_name
FROM lifecycle_changes
WHERE fast_track_flag IS TRUE
  AND list_count(evidence_artifact_refs) = 0
UNION ALL
SELECT
    'lifecycle_fast_track_missing_risk_acknowledgment' AS issue_type,
    lifecycle_change_id,
    candidate_id,
    'risk_acknowledgment' AS field_name
FROM lifecycle_changes
WHERE fast_track_flag IS TRUE
  AND (risk_acknowledgment IS NULL OR trim(CAST(risk_acknowledgment AS VARCHAR)) = '');

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

-- What committed shadow-signal summary segments have been recorded?
-- Flattens one row per segment from each committed summary artifact.
CREATE OR REPLACE VIEW v_shadow_signal_summaries_overview AS
SELECT
    s.shadow_signal_summary_id,
    s.generated_at,
    s.corpus_window.first_overlay_shadow_log_id AS first_overlay_shadow_log_id,
    s.corpus_window.last_overlay_shadow_log_id AS last_overlay_shadow_log_id,
    s.corpus_window.first_observed_at AS corpus_first_observed_at,
    s.corpus_window.last_observed_at AS corpus_last_observed_at,
    s.corpus_window.total_source_observation_count AS total_source_observation_count,
    s.derivation_method,
    segment.advisory_source AS advisory_source,
    segment.source_bucket_mapping_id AS source_bucket_mapping_id,
    segment.source_pre_gate_advisory_snapshot_id AS source_pre_gate_advisory_snapshot_id,
    segment.fixture_identity AS fixture_identity,
    segment.match_count AS match_count,
    segment.mismatch_count AS mismatch_count,
    segment.abstention_count AS abstention_count,
    segment.observation_count AS observation_count,
    segment.rate_denominator AS rate_denominator,
    segment.agreement_rate AS agreement_rate,
    segment.disagreement_rate AS disagreement_rate,
    segment.insufficient_evidence AS insufficient_evidence,
    segment.signal_outcome AS signal_outcome,
    segment.first_observed_at AS first_segment_observed_at,
    segment.last_observed_at AS last_segment_observed_at,
    s.deterministic,
    s.advisory_only
FROM shadow_signal_summaries AS s,
UNNEST(s.segments) AS segments(segment);

-- Does each committed shadow-signal summary still match the live committed corpus?
-- Returns rows only when summary metadata or segment derivation drifts from overlay_shadow_logs.
CREATE OR REPLACE VIEW v_integrity_shadow_signal_summary_derivation AS
WITH live_shadow_rows AS (
    SELECT
        overlay_shadow_log_id,
        CAST(observed_at AS TIMESTAMP) AS observed_at_ts,
        observed_at,
        comparison_result,
        COALESCE(advisory_source, 'BMAP') AS advisory_source,
        source_bucket_mapping_id,
        source_pre_gate_advisory_snapshot_id,
        CASE
            WHEN observation_source.snapshot_path = 'tests/fixtures/context_snapshot_sample.json'
             AND observation_source.config_path = 'configs/fmp_macro_flags.json'
                THEN 'canonical'
            WHEN observation_source.snapshot_path = 'tests/fixtures/context_snapshot_sample_02.json'
             AND observation_source.config_path = 'configs/fmp_macro_flags_02.json'
                THEN '_02'
            ELSE NULL
        END AS fixture_identity
    FROM overlay_shadow_logs
),
live_unknown_fixture_rows AS (
    SELECT
        overlay_shadow_log_id
    FROM live_shadow_rows
    WHERE fixture_identity IS NULL
),
expected_segments AS (
    SELECT
        advisory_source,
        source_bucket_mapping_id,
        source_pre_gate_advisory_snapshot_id,
        fixture_identity,
        SUM(CASE WHEN comparison_result = 'MATCH' THEN 1 ELSE 0 END) AS match_count,
        SUM(CASE WHEN comparison_result = 'MISMATCH' THEN 1 ELSE 0 END) AS mismatch_count,
        0 AS abstention_count,
        COUNT(*) AS observation_count,
        SUM(CASE WHEN comparison_result IN ('MATCH', 'MISMATCH') THEN 1 ELSE 0 END) AS rate_denominator,
        CASE
            WHEN COUNT(*) < 10 THEN NULL
            ELSE
                CAST(SUM(CASE WHEN comparison_result = 'MATCH' THEN 1 ELSE 0 END) AS DOUBLE)
                / NULLIF(SUM(CASE WHEN comparison_result IN ('MATCH', 'MISMATCH') THEN 1 ELSE 0 END), 0)
        END AS agreement_rate,
        CASE
            WHEN COUNT(*) < 10 THEN NULL
            ELSE
                CAST(SUM(CASE WHEN comparison_result = 'MISMATCH' THEN 1 ELSE 0 END) AS DOUBLE)
                / NULLIF(SUM(CASE WHEN comparison_result IN ('MATCH', 'MISMATCH') THEN 1 ELSE 0 END), 0)
        END AS disagreement_rate,
        CASE
            WHEN COUNT(*) < 10 THEN true
            ELSE false
        END AS insufficient_evidence,
        CASE
            WHEN COUNT(*) < 10 THEN 'INSUFFICIENT_EVIDENCE'
            WHEN SUM(CASE WHEN comparison_result = 'MATCH' THEN 1 ELSE 0 END)
               > SUM(CASE WHEN comparison_result = 'MISMATCH' THEN 1 ELSE 0 END)
                THEN 'AGREEMENT_SIGNAL'
            WHEN SUM(CASE WHEN comparison_result = 'MISMATCH' THEN 1 ELSE 0 END)
               > SUM(CASE WHEN comparison_result = 'MATCH' THEN 1 ELSE 0 END)
                THEN 'DISAGREEMENT_SIGNAL'
            ELSE 'MIXED_SIGNAL'
        END AS signal_outcome,
        strftime('%Y-%m-%dT%H:%M:%SZ', MIN(observed_at_ts)) AS first_observed_at,
        strftime('%Y-%m-%dT%H:%M:%SZ', MAX(observed_at_ts)) AS last_observed_at
    FROM live_shadow_rows
    WHERE fixture_identity IS NOT NULL
    GROUP BY
        advisory_source,
        source_bucket_mapping_id,
        source_pre_gate_advisory_snapshot_id,
        fixture_identity
),
expected_corpus_window AS (
    SELECT
        (
            SELECT overlay_shadow_log_id
            FROM live_shadow_rows
            ORDER BY observed_at_ts ASC, overlay_shadow_log_id ASC
            LIMIT 1
        ) AS first_overlay_shadow_log_id,
        (
            SELECT overlay_shadow_log_id
            FROM live_shadow_rows
            ORDER BY observed_at_ts DESC, overlay_shadow_log_id DESC
            LIMIT 1
        ) AS last_overlay_shadow_log_id,
        strftime('%Y-%m-%dT%H:%M:%SZ', MIN(observed_at_ts)) AS first_observed_at,
        strftime('%Y-%m-%dT%H:%M:%SZ', MAX(observed_at_ts)) AS last_observed_at,
        COUNT(*) AS total_source_observation_count
    FROM live_shadow_rows
),
actual_segments AS (
    SELECT
        s.shadow_signal_summary_id,
        segment.advisory_source AS advisory_source,
        segment.source_bucket_mapping_id AS source_bucket_mapping_id,
        segment.source_pre_gate_advisory_snapshot_id AS source_pre_gate_advisory_snapshot_id,
        segment.fixture_identity AS fixture_identity,
        segment.match_count AS match_count,
        segment.mismatch_count AS mismatch_count,
        segment.abstention_count AS abstention_count,
        segment.observation_count AS observation_count,
        segment.rate_denominator AS rate_denominator,
        CAST(segment.agreement_rate AS DOUBLE) AS agreement_rate,
        CAST(segment.disagreement_rate AS DOUBLE) AS disagreement_rate,
        segment.insufficient_evidence AS insufficient_evidence,
        segment.signal_outcome AS signal_outcome,
        segment.first_observed_at AS first_observed_at,
        segment.last_observed_at AS last_observed_at
    FROM shadow_signal_summaries AS s,
    UNNEST(s.segments) AS segments(segment)
),
segment_join AS (
    SELECT
        COALESCE(a.shadow_signal_summary_id, s.shadow_signal_summary_id) AS shadow_signal_summary_id,
        COALESCE(a.advisory_source, e.advisory_source) AS advisory_source,
        COALESCE(a.source_bucket_mapping_id, e.source_bucket_mapping_id) AS source_bucket_mapping_id,
        COALESCE(a.source_pre_gate_advisory_snapshot_id, e.source_pre_gate_advisory_snapshot_id) AS source_pre_gate_advisory_snapshot_id,
        COALESCE(a.fixture_identity, e.fixture_identity) AS fixture_identity,
        a.advisory_source AS actual_advisory_source,
        e.advisory_source AS expected_advisory_source,
        a.match_count AS actual_match_count,
        e.match_count AS expected_match_count,
        a.mismatch_count AS actual_mismatch_count,
        e.mismatch_count AS expected_mismatch_count,
        a.abstention_count AS actual_abstention_count,
        e.abstention_count AS expected_abstention_count,
        a.observation_count AS actual_observation_count,
        e.observation_count AS expected_observation_count,
        a.rate_denominator AS actual_rate_denominator,
        e.rate_denominator AS expected_rate_denominator,
        a.agreement_rate AS actual_agreement_rate,
        e.agreement_rate AS expected_agreement_rate,
        a.disagreement_rate AS actual_disagreement_rate,
        e.disagreement_rate AS expected_disagreement_rate,
        a.insufficient_evidence AS actual_insufficient_evidence,
        e.insufficient_evidence AS expected_insufficient_evidence,
        a.signal_outcome AS actual_signal_outcome,
        e.signal_outcome AS expected_signal_outcome,
        a.first_observed_at AS actual_first_observed_at,
        e.first_observed_at AS expected_first_observed_at,
        a.last_observed_at AS actual_last_observed_at,
        e.last_observed_at AS expected_last_observed_at
    FROM shadow_signal_summaries AS s
    LEFT JOIN actual_segments AS a
      ON a.shadow_signal_summary_id = s.shadow_signal_summary_id
    FULL OUTER JOIN expected_segments AS e
      ON a.advisory_source = e.advisory_source
     AND a.source_bucket_mapping_id = e.source_bucket_mapping_id
     AND a.source_pre_gate_advisory_snapshot_id IS NOT DISTINCT FROM e.source_pre_gate_advisory_snapshot_id
     AND a.fixture_identity = e.fixture_identity
),
metadata_issues AS (
    SELECT
        s.shadow_signal_summary_id,
        CAST(NULL AS VARCHAR) AS advisory_source,
        CAST(NULL AS VARCHAR) AS source_bucket_mapping_id,
        CAST(NULL AS VARCHAR) AS source_pre_gate_advisory_snapshot_id,
        CAST(NULL AS VARCHAR) AS fixture_identity,
        'shadow_signal_summary_unknown_fixture_identity' AS issue_type,
        string_agg(overlay_shadow_log_id, ', ' ORDER BY overlay_shadow_log_id) AS expected_value,
        'known fixture identities only' AS actual_value
    FROM shadow_signal_summaries AS s
    CROSS JOIN live_unknown_fixture_rows
    GROUP BY s.shadow_signal_summary_id
    UNION ALL
    SELECT
        shadow_signal_summary_id,
        NULL,
        NULL,
        NULL,
        NULL,
        'shadow_signal_summary_derivation_method_mismatch' AS issue_type,
        'shadow_signal_summary_option_a_floor_10_v1' AS expected_value,
        derivation_method AS actual_value
    FROM shadow_signal_summaries
    WHERE derivation_method <> 'shadow_signal_summary_option_a_floor_10_v1'
    UNION ALL
    SELECT
        shadow_signal_summary_id,
        NULL,
        NULL,
        NULL,
        NULL,
        'shadow_signal_summary_segmentation_axes_mismatch' AS issue_type,
        'advisory_source,source_bucket_mapping_id,source_pre_gate_advisory_snapshot_id,fixture_identity' AS expected_value,
        array_to_string(segmentation_axes, ',') AS actual_value
    FROM shadow_signal_summaries
    WHERE segmentation_axes IS DISTINCT FROM [
        'advisory_source',
        'source_bucket_mapping_id',
        'source_pre_gate_advisory_snapshot_id',
        'fixture_identity'
    ]
    UNION ALL
    SELECT
        shadow_signal_summary_id,
        NULL,
        NULL,
        NULL,
        NULL,
        'shadow_signal_summary_source_relation_mismatch' AS issue_type,
        'overlay_shadow_logs' AS expected_value,
        derivation_inputs.source_relation AS actual_value
    FROM shadow_signal_summaries
    WHERE derivation_inputs.source_relation <> 'overlay_shadow_logs'
    UNION ALL
    SELECT
        shadow_signal_summary_id,
        NULL,
        NULL,
        NULL,
        NULL,
        'shadow_signal_summary_source_family_mismatch' AS issue_type,
        'overlay_shadow_logs' AS expected_value,
        derivation_inputs.source_artifact_family AS actual_value
    FROM shadow_signal_summaries
    WHERE derivation_inputs.source_artifact_family <> 'overlay_shadow_logs'
    UNION ALL
    SELECT
        shadow_signal_summary_id,
        NULL,
        NULL,
        NULL,
        NULL,
        'shadow_signal_summary_fixture_identity_rule_mismatch' AS issue_type,
        'committed_overlay_input_pair_v1' AS expected_value,
        derivation_inputs.fixture_identity_rule AS actual_value
    FROM shadow_signal_summaries
    WHERE derivation_inputs.fixture_identity_rule <> 'committed_overlay_input_pair_v1'
    UNION ALL
    SELECT
        shadow_signal_summary_id,
        NULL,
        NULL,
        NULL,
        NULL,
        'shadow_signal_summary_rate_denominator_rule_mismatch' AS issue_type,
        'match_plus_mismatch' AS expected_value,
        derivation_inputs.rate_denominator_rule AS actual_value
    FROM shadow_signal_summaries
    WHERE derivation_inputs.rate_denominator_rule <> 'match_plus_mismatch'
    UNION ALL
    SELECT
        s.shadow_signal_summary_id,
        NULL,
        NULL,
        NULL,
        NULL,
        'shadow_signal_summary_generated_at_mismatch' AS issue_type,
        expected_corpus_window.last_observed_at AS expected_value,
        s.generated_at AS actual_value
    FROM shadow_signal_summaries AS s
    CROSS JOIN expected_corpus_window
    WHERE s.generated_at <> expected_corpus_window.last_observed_at
    UNION ALL
    SELECT
        s.shadow_signal_summary_id,
        NULL,
        NULL,
        NULL,
        NULL,
        'shadow_signal_summary_first_overlay_shadow_log_id_mismatch' AS issue_type,
        expected_corpus_window.first_overlay_shadow_log_id AS expected_value,
        s.corpus_window.first_overlay_shadow_log_id AS actual_value
    FROM shadow_signal_summaries AS s
    CROSS JOIN expected_corpus_window
    WHERE s.corpus_window.first_overlay_shadow_log_id <> expected_corpus_window.first_overlay_shadow_log_id
    UNION ALL
    SELECT
        s.shadow_signal_summary_id,
        NULL,
        NULL,
        NULL,
        NULL,
        'shadow_signal_summary_last_overlay_shadow_log_id_mismatch' AS issue_type,
        expected_corpus_window.last_overlay_shadow_log_id AS expected_value,
        s.corpus_window.last_overlay_shadow_log_id AS actual_value
    FROM shadow_signal_summaries AS s
    CROSS JOIN expected_corpus_window
    WHERE s.corpus_window.last_overlay_shadow_log_id <> expected_corpus_window.last_overlay_shadow_log_id
    UNION ALL
    SELECT
        s.shadow_signal_summary_id,
        NULL,
        NULL,
        NULL,
        NULL,
        'shadow_signal_summary_first_observed_at_mismatch' AS issue_type,
        expected_corpus_window.first_observed_at AS expected_value,
        s.corpus_window.first_observed_at AS actual_value
    FROM shadow_signal_summaries AS s
    CROSS JOIN expected_corpus_window
    WHERE s.corpus_window.first_observed_at <> expected_corpus_window.first_observed_at
    UNION ALL
    SELECT
        s.shadow_signal_summary_id,
        NULL,
        NULL,
        NULL,
        NULL,
        'shadow_signal_summary_last_observed_at_mismatch' AS issue_type,
        expected_corpus_window.last_observed_at AS expected_value,
        s.corpus_window.last_observed_at AS actual_value
    FROM shadow_signal_summaries AS s
    CROSS JOIN expected_corpus_window
    WHERE s.corpus_window.last_observed_at <> expected_corpus_window.last_observed_at
    UNION ALL
    SELECT
        s.shadow_signal_summary_id,
        NULL,
        NULL,
        NULL,
        NULL,
        'shadow_signal_summary_total_source_observation_count_mismatch' AS issue_type,
        CAST(expected_corpus_window.total_source_observation_count AS VARCHAR) AS expected_value,
        CAST(s.corpus_window.total_source_observation_count AS VARCHAR) AS actual_value
    FROM shadow_signal_summaries AS s
    CROSS JOIN expected_corpus_window
    WHERE s.corpus_window.total_source_observation_count <> expected_corpus_window.total_source_observation_count
    UNION ALL
    SELECT
        shadow_signal_summary_id,
        NULL,
        NULL,
        NULL,
        NULL,
        'shadow_signal_summary_not_deterministic' AS issue_type,
        'true' AS expected_value,
        CAST(deterministic AS VARCHAR) AS actual_value
    FROM shadow_signal_summaries
    WHERE deterministic IS DISTINCT FROM true
    UNION ALL
    SELECT
        shadow_signal_summary_id,
        NULL,
        NULL,
        NULL,
        NULL,
        'shadow_signal_summary_not_advisory_only' AS issue_type,
        'true' AS expected_value,
        CAST(advisory_only AS VARCHAR) AS actual_value
    FROM shadow_signal_summaries
    WHERE advisory_only IS DISTINCT FROM true
),
segment_presence_issues AS (
    SELECT
        shadow_signal_summary_id,
        advisory_source,
        source_bucket_mapping_id,
        source_pre_gate_advisory_snapshot_id,
        fixture_identity,
        'shadow_signal_summary_missing_segment' AS issue_type,
        'present' AS expected_value,
        'missing' AS actual_value
    FROM segment_join
    WHERE actual_advisory_source IS NULL
      AND expected_advisory_source IS NOT NULL
    UNION ALL
    SELECT
        shadow_signal_summary_id,
        advisory_source,
        source_bucket_mapping_id,
        source_pre_gate_advisory_snapshot_id,
        fixture_identity,
        'shadow_signal_summary_extra_segment' AS issue_type,
        'missing' AS expected_value,
        'present' AS actual_value
    FROM segment_join
    WHERE actual_advisory_source IS NOT NULL
      AND expected_advisory_source IS NULL
),
segment_value_issues AS (
    SELECT
        shadow_signal_summary_id,
        advisory_source,
        source_bucket_mapping_id,
        source_pre_gate_advisory_snapshot_id,
        fixture_identity,
        'shadow_signal_summary_match_count_mismatch' AS issue_type,
        CAST(expected_match_count AS VARCHAR) AS expected_value,
        CAST(actual_match_count AS VARCHAR) AS actual_value
    FROM segment_join
    WHERE expected_advisory_source IS NOT NULL
      AND actual_advisory_source IS NOT NULL
      AND actual_match_count IS DISTINCT FROM expected_match_count
    UNION ALL
    SELECT
        shadow_signal_summary_id,
        advisory_source,
        source_bucket_mapping_id,
        source_pre_gate_advisory_snapshot_id,
        fixture_identity,
        'shadow_signal_summary_mismatch_count_mismatch' AS issue_type,
        CAST(expected_mismatch_count AS VARCHAR) AS expected_value,
        CAST(actual_mismatch_count AS VARCHAR) AS actual_value
    FROM segment_join
    WHERE expected_advisory_source IS NOT NULL
      AND actual_advisory_source IS NOT NULL
      AND actual_mismatch_count IS DISTINCT FROM expected_mismatch_count
    UNION ALL
    SELECT
        shadow_signal_summary_id,
        advisory_source,
        source_bucket_mapping_id,
        source_pre_gate_advisory_snapshot_id,
        fixture_identity,
        'shadow_signal_summary_abstention_count_mismatch' AS issue_type,
        CAST(expected_abstention_count AS VARCHAR) AS expected_value,
        CAST(actual_abstention_count AS VARCHAR) AS actual_value
    FROM segment_join
    WHERE expected_advisory_source IS NOT NULL
      AND actual_advisory_source IS NOT NULL
      AND actual_abstention_count IS DISTINCT FROM expected_abstention_count
    UNION ALL
    SELECT
        shadow_signal_summary_id,
        advisory_source,
        source_bucket_mapping_id,
        source_pre_gate_advisory_snapshot_id,
        fixture_identity,
        'shadow_signal_summary_observation_count_mismatch' AS issue_type,
        CAST(expected_observation_count AS VARCHAR) AS expected_value,
        CAST(actual_observation_count AS VARCHAR) AS actual_value
    FROM segment_join
    WHERE expected_advisory_source IS NOT NULL
      AND actual_advisory_source IS NOT NULL
      AND actual_observation_count IS DISTINCT FROM expected_observation_count
    UNION ALL
    SELECT
        shadow_signal_summary_id,
        advisory_source,
        source_bucket_mapping_id,
        source_pre_gate_advisory_snapshot_id,
        fixture_identity,
        'shadow_signal_summary_rate_denominator_mismatch' AS issue_type,
        CAST(expected_rate_denominator AS VARCHAR) AS expected_value,
        CAST(actual_rate_denominator AS VARCHAR) AS actual_value
    FROM segment_join
    WHERE expected_advisory_source IS NOT NULL
      AND actual_advisory_source IS NOT NULL
      AND actual_rate_denominator IS DISTINCT FROM expected_rate_denominator
    UNION ALL
    SELECT
        shadow_signal_summary_id,
        advisory_source,
        source_bucket_mapping_id,
        source_pre_gate_advisory_snapshot_id,
        fixture_identity,
        'shadow_signal_summary_agreement_rate_mismatch' AS issue_type,
        CAST(expected_agreement_rate AS VARCHAR) AS expected_value,
        CAST(actual_agreement_rate AS VARCHAR) AS actual_value
    FROM segment_join
    WHERE expected_advisory_source IS NOT NULL
      AND actual_advisory_source IS NOT NULL
      AND actual_agreement_rate IS DISTINCT FROM expected_agreement_rate
    UNION ALL
    SELECT
        shadow_signal_summary_id,
        advisory_source,
        source_bucket_mapping_id,
        source_pre_gate_advisory_snapshot_id,
        fixture_identity,
        'shadow_signal_summary_disagreement_rate_mismatch' AS issue_type,
        CAST(expected_disagreement_rate AS VARCHAR) AS expected_value,
        CAST(actual_disagreement_rate AS VARCHAR) AS actual_value
    FROM segment_join
    WHERE expected_advisory_source IS NOT NULL
      AND actual_advisory_source IS NOT NULL
      AND actual_disagreement_rate IS DISTINCT FROM expected_disagreement_rate
    UNION ALL
    SELECT
        shadow_signal_summary_id,
        advisory_source,
        source_bucket_mapping_id,
        source_pre_gate_advisory_snapshot_id,
        fixture_identity,
        'shadow_signal_summary_insufficient_evidence_mismatch' AS issue_type,
        CAST(expected_insufficient_evidence AS VARCHAR) AS expected_value,
        CAST(actual_insufficient_evidence AS VARCHAR) AS actual_value
    FROM segment_join
    WHERE expected_advisory_source IS NOT NULL
      AND actual_advisory_source IS NOT NULL
      AND actual_insufficient_evidence IS DISTINCT FROM expected_insufficient_evidence
    UNION ALL
    SELECT
        shadow_signal_summary_id,
        advisory_source,
        source_bucket_mapping_id,
        source_pre_gate_advisory_snapshot_id,
        fixture_identity,
        'shadow_signal_summary_signal_outcome_mismatch' AS issue_type,
        expected_signal_outcome AS expected_value,
        actual_signal_outcome AS actual_value
    FROM segment_join
    WHERE expected_advisory_source IS NOT NULL
      AND actual_advisory_source IS NOT NULL
      AND actual_signal_outcome IS DISTINCT FROM expected_signal_outcome
    UNION ALL
    SELECT
        shadow_signal_summary_id,
        advisory_source,
        source_bucket_mapping_id,
        source_pre_gate_advisory_snapshot_id,
        fixture_identity,
        'shadow_signal_summary_first_observed_at_segment_mismatch' AS issue_type,
        expected_first_observed_at AS expected_value,
        actual_first_observed_at AS actual_value
    FROM segment_join
    WHERE expected_advisory_source IS NOT NULL
      AND actual_advisory_source IS NOT NULL
      AND actual_first_observed_at IS DISTINCT FROM expected_first_observed_at
    UNION ALL
    SELECT
        shadow_signal_summary_id,
        advisory_source,
        source_bucket_mapping_id,
        source_pre_gate_advisory_snapshot_id,
        fixture_identity,
        'shadow_signal_summary_last_observed_at_segment_mismatch' AS issue_type,
        expected_last_observed_at AS expected_value,
        actual_last_observed_at AS actual_value
    FROM segment_join
    WHERE expected_advisory_source IS NOT NULL
      AND actual_advisory_source IS NOT NULL
      AND actual_last_observed_at IS DISTINCT FROM expected_last_observed_at
)
SELECT *
FROM metadata_issues
UNION ALL
SELECT *
FROM segment_presence_issues
UNION ALL
SELECT *
FROM segment_value_issues;

-- What committed shadow-signal summary v2 segments have been recorded?
-- Flattens one row per segment from each committed v2 summary artifact.
CREATE OR REPLACE VIEW v_shadow_signal_summaries_v2_overview AS
WITH flattened AS (
    SELECT
        s.shadow_signal_summary_id,
        s.schema_version,
        strftime('%Y-%m-%dT%H:%M:%SZ', CAST(s.generated_at AS TIMESTAMP)) AS generated_at,
        s.corpus_window.first_overlay_shadow_log_id AS first_overlay_shadow_log_id,
        s.corpus_window.last_overlay_shadow_log_id AS last_overlay_shadow_log_id,
        strftime(
            '%Y-%m-%dT%H:%M:%SZ',
            CAST(s.corpus_window.first_observed_at AS TIMESTAMP)
        ) AS corpus_first_observed_at,
        strftime(
            '%Y-%m-%dT%H:%M:%SZ',
            CAST(s.corpus_window.last_observed_at AS TIMESTAMP)
        ) AS corpus_last_observed_at,
        s.corpus_window.total_source_observation_count AS total_source_observation_count,
        s.derivation_method,
        array_to_string(s.segmentation_axes, ',') AS segmentation_axes,
        CAST(to_json(s.segmentation_axes) AS VARCHAR) AS segmentation_axes_json,
        to_json(segment) AS segment_json,
        s.deterministic,
        s.advisory_only
    FROM shadow_signal_summaries_v2 AS s,
    UNNEST(s.segments) AS segments(segment)
)
SELECT
    shadow_signal_summary_id,
    schema_version,
    generated_at,
    first_overlay_shadow_log_id,
    last_overlay_shadow_log_id,
    corpus_first_observed_at,
    corpus_last_observed_at,
    total_source_observation_count,
    derivation_method,
    segmentation_axes,
    segmentation_axes_json,
    json_extract_string(segment_json, '$.advisory_source') AS advisory_source,
    json_extract_string(segment_json, '$.source_bucket_mapping_id') AS source_bucket_mapping_id,
    json_extract_string(
        segment_json,
        '$.source_pre_gate_advisory_snapshot_id'
    ) AS source_pre_gate_advisory_snapshot_id,
    json_extract_string(segment_json, '$.fixture_identity') AS fixture_identity,
    CAST(json_extract(segment_json, '$.match_count') AS BIGINT) AS match_count,
    CAST(json_extract(segment_json, '$.mismatch_count') AS BIGINT) AS mismatch_count,
    CAST(json_extract(segment_json, '$.abstention_count') AS BIGINT) AS abstention_count,
    CAST(json_extract(segment_json, '$.observation_count') AS BIGINT) AS observation_count,
    CAST(json_extract(segment_json, '$.rate_denominator') AS BIGINT) AS rate_denominator,
    CAST(json_extract(segment_json, '$.agreement_rate') AS DOUBLE) AS agreement_rate,
    CAST(json_extract(segment_json, '$.disagreement_rate') AS DOUBLE) AS disagreement_rate,
    CAST(json_extract(segment_json, '$.insufficient_evidence') AS BOOLEAN) AS insufficient_evidence,
    json_extract_string(segment_json, '$.signal_outcome') AS signal_outcome,
    strftime(
        '%Y-%m-%dT%H:%M:%SZ',
        CAST(json_extract_string(segment_json, '$.first_observed_at') AS TIMESTAMP)
    ) AS first_segment_observed_at,
    strftime(
        '%Y-%m-%dT%H:%M:%SZ',
        CAST(json_extract_string(segment_json, '$.last_observed_at') AS TIMESTAMP)
    ) AS last_segment_observed_at,
    deterministic,
    advisory_only
FROM flattened;

-- Does each committed supported-form v2 summary match the live committed corpus?
-- Returns rows only when v2 summary metadata or supported segment derivation drifts.
CREATE OR REPLACE VIEW v_integrity_shadow_signal_summary_v2_derivation AS
WITH live_shadow_rows AS (
    SELECT
        overlay_shadow_log_id,
        CAST(observed_at AS TIMESTAMP) AS observed_at_ts,
        observed_at,
        comparison_result,
        COALESCE(advisory_source, 'BMAP') AS advisory_source,
        source_bucket_mapping_id,
        source_pre_gate_advisory_snapshot_id,
        CASE
            WHEN observation_source.snapshot_path = 'tests/fixtures/context_snapshot_sample.json'
             AND observation_source.config_path = 'configs/fmp_macro_flags.json'
                THEN 'canonical'
            WHEN observation_source.snapshot_path = 'tests/fixtures/context_snapshot_sample_02.json'
             AND observation_source.config_path = 'configs/fmp_macro_flags_02.json'
                THEN '_02'
            ELSE NULL
        END AS fixture_identity
    FROM overlay_shadow_logs
),
expected_segments AS (
    SELECT
        'advisory_source' AS segmentation_axes,
        advisory_source AS segment_key,
        advisory_source,
        CAST(NULL AS VARCHAR) AS source_bucket_mapping_id,
        CAST(NULL AS VARCHAR) AS source_pre_gate_advisory_snapshot_id,
        SUM(CASE WHEN comparison_result = 'MATCH' THEN 1 ELSE 0 END) AS match_count,
        SUM(CASE WHEN comparison_result = 'MISMATCH' THEN 1 ELSE 0 END) AS mismatch_count,
        SUM(
            CASE
                WHEN comparison_result NOT IN ('MATCH', 'MISMATCH')
                  OR comparison_result IS NULL
                    THEN 1
                ELSE 0
            END
        ) AS abstention_count,
        COUNT(*) AS observation_count,
        SUM(CASE WHEN comparison_result IN ('MATCH', 'MISMATCH') THEN 1 ELSE 0 END) AS rate_denominator,
        CASE
            WHEN COUNT(*) < 10 THEN NULL
            ELSE
                CAST(SUM(CASE WHEN comparison_result = 'MATCH' THEN 1 ELSE 0 END) AS DOUBLE)
                / NULLIF(SUM(CASE WHEN comparison_result IN ('MATCH', 'MISMATCH') THEN 1 ELSE 0 END), 0)
        END AS agreement_rate,
        CASE
            WHEN COUNT(*) < 10 THEN NULL
            ELSE
                CAST(SUM(CASE WHEN comparison_result = 'MISMATCH' THEN 1 ELSE 0 END) AS DOUBLE)
                / NULLIF(SUM(CASE WHEN comparison_result IN ('MATCH', 'MISMATCH') THEN 1 ELSE 0 END), 0)
        END AS disagreement_rate,
        CASE
            WHEN COUNT(*) < 10 THEN true
            ELSE false
        END AS insufficient_evidence,
        CASE
            WHEN COUNT(*) < 10 THEN 'INSUFFICIENT_EVIDENCE'
            WHEN SUM(CASE WHEN comparison_result = 'MATCH' THEN 1 ELSE 0 END)
               > SUM(CASE WHEN comparison_result = 'MISMATCH' THEN 1 ELSE 0 END)
                THEN 'AGREEMENT_SIGNAL'
            WHEN SUM(CASE WHEN comparison_result = 'MISMATCH' THEN 1 ELSE 0 END)
               > SUM(CASE WHEN comparison_result = 'MATCH' THEN 1 ELSE 0 END)
                THEN 'DISAGREEMENT_SIGNAL'
            ELSE 'MIXED_SIGNAL'
        END AS signal_outcome,
        strftime('%Y-%m-%dT%H:%M:%SZ', MIN(observed_at_ts)) AS first_observed_at,
        strftime('%Y-%m-%dT%H:%M:%SZ', MAX(observed_at_ts)) AS last_observed_at
    FROM live_shadow_rows
    GROUP BY advisory_source
    UNION ALL
    SELECT
        'advisory_source,source_bucket_mapping_id,source_pre_gate_advisory_snapshot_id'
            AS segmentation_axes,
        advisory_source || '|' || source_bucket_mapping_id || '|'
            || COALESCE(source_pre_gate_advisory_snapshot_id, '') AS segment_key,
        advisory_source,
        source_bucket_mapping_id,
        source_pre_gate_advisory_snapshot_id,
        SUM(CASE WHEN comparison_result = 'MATCH' THEN 1 ELSE 0 END) AS match_count,
        SUM(CASE WHEN comparison_result = 'MISMATCH' THEN 1 ELSE 0 END) AS mismatch_count,
        SUM(
            CASE
                WHEN comparison_result NOT IN ('MATCH', 'MISMATCH')
                  OR comparison_result IS NULL
                    THEN 1
                ELSE 0
            END
        ) AS abstention_count,
        COUNT(*) AS observation_count,
        SUM(CASE WHEN comparison_result IN ('MATCH', 'MISMATCH') THEN 1 ELSE 0 END) AS rate_denominator,
        CASE
            WHEN COUNT(*) < 10 THEN NULL
            ELSE
                CAST(SUM(CASE WHEN comparison_result = 'MATCH' THEN 1 ELSE 0 END) AS DOUBLE)
                / NULLIF(SUM(CASE WHEN comparison_result IN ('MATCH', 'MISMATCH') THEN 1 ELSE 0 END), 0)
        END AS agreement_rate,
        CASE
            WHEN COUNT(*) < 10 THEN NULL
            ELSE
                CAST(SUM(CASE WHEN comparison_result = 'MISMATCH' THEN 1 ELSE 0 END) AS DOUBLE)
                / NULLIF(SUM(CASE WHEN comparison_result IN ('MATCH', 'MISMATCH') THEN 1 ELSE 0 END), 0)
        END AS disagreement_rate,
        CASE
            WHEN COUNT(*) < 10 THEN true
            ELSE false
        END AS insufficient_evidence,
        CASE
            WHEN COUNT(*) < 10 THEN 'INSUFFICIENT_EVIDENCE'
            WHEN SUM(CASE WHEN comparison_result = 'MATCH' THEN 1 ELSE 0 END)
               > SUM(CASE WHEN comparison_result = 'MISMATCH' THEN 1 ELSE 0 END)
                THEN 'AGREEMENT_SIGNAL'
            WHEN SUM(CASE WHEN comparison_result = 'MISMATCH' THEN 1 ELSE 0 END)
               > SUM(CASE WHEN comparison_result = 'MATCH' THEN 1 ELSE 0 END)
                THEN 'DISAGREEMENT_SIGNAL'
            ELSE 'MIXED_SIGNAL'
        END AS signal_outcome,
        strftime('%Y-%m-%dT%H:%M:%SZ', MIN(observed_at_ts)) AS first_observed_at,
        strftime('%Y-%m-%dT%H:%M:%SZ', MAX(observed_at_ts)) AS last_observed_at
    FROM live_shadow_rows
    GROUP BY advisory_source, source_bucket_mapping_id, source_pre_gate_advisory_snapshot_id
    UNION ALL
    SELECT
        'fixture_identity' AS segmentation_axes,
        fixture_identity AS segment_key,
        CAST(NULL AS VARCHAR) AS advisory_source,
        CAST(NULL AS VARCHAR) AS source_bucket_mapping_id,
        CAST(NULL AS VARCHAR) AS source_pre_gate_advisory_snapshot_id,
        SUM(CASE WHEN comparison_result = 'MATCH' THEN 1 ELSE 0 END) AS match_count,
        SUM(CASE WHEN comparison_result = 'MISMATCH' THEN 1 ELSE 0 END) AS mismatch_count,
        SUM(
            CASE
                WHEN comparison_result NOT IN ('MATCH', 'MISMATCH')
                  OR comparison_result IS NULL
                    THEN 1
                ELSE 0
            END
        ) AS abstention_count,
        COUNT(*) AS observation_count,
        SUM(CASE WHEN comparison_result IN ('MATCH', 'MISMATCH') THEN 1 ELSE 0 END) AS rate_denominator,
        CASE
            WHEN COUNT(*) < 10 THEN NULL
            ELSE
                CAST(SUM(CASE WHEN comparison_result = 'MATCH' THEN 1 ELSE 0 END) AS DOUBLE)
                / NULLIF(SUM(CASE WHEN comparison_result IN ('MATCH', 'MISMATCH') THEN 1 ELSE 0 END), 0)
        END AS agreement_rate,
        CASE
            WHEN COUNT(*) < 10 THEN NULL
            ELSE
                CAST(SUM(CASE WHEN comparison_result = 'MISMATCH' THEN 1 ELSE 0 END) AS DOUBLE)
                / NULLIF(SUM(CASE WHEN comparison_result IN ('MATCH', 'MISMATCH') THEN 1 ELSE 0 END), 0)
        END AS disagreement_rate,
        CASE
            WHEN COUNT(*) < 10 THEN true
            ELSE false
        END AS insufficient_evidence,
        CASE
            WHEN COUNT(*) < 10 THEN 'INSUFFICIENT_EVIDENCE'
            WHEN SUM(CASE WHEN comparison_result = 'MATCH' THEN 1 ELSE 0 END)
               > SUM(CASE WHEN comparison_result = 'MISMATCH' THEN 1 ELSE 0 END)
                THEN 'AGREEMENT_SIGNAL'
            WHEN SUM(CASE WHEN comparison_result = 'MISMATCH' THEN 1 ELSE 0 END)
               > SUM(CASE WHEN comparison_result = 'MATCH' THEN 1 ELSE 0 END)
                THEN 'DISAGREEMENT_SIGNAL'
            ELSE 'MIXED_SIGNAL'
        END AS signal_outcome,
        strftime('%Y-%m-%dT%H:%M:%SZ', MIN(observed_at_ts)) AS first_observed_at,
        strftime('%Y-%m-%dT%H:%M:%SZ', MAX(observed_at_ts)) AS last_observed_at
    FROM live_shadow_rows
    WHERE fixture_identity IS NOT NULL
    GROUP BY fixture_identity
),
expected_corpus_window AS (
    SELECT
        (
            SELECT overlay_shadow_log_id
            FROM live_shadow_rows
            ORDER BY observed_at_ts ASC, overlay_shadow_log_id ASC
            LIMIT 1
        ) AS first_overlay_shadow_log_id,
        (
            SELECT overlay_shadow_log_id
            FROM live_shadow_rows
            ORDER BY observed_at_ts DESC, overlay_shadow_log_id DESC
            LIMIT 1
        ) AS last_overlay_shadow_log_id,
        strftime('%Y-%m-%dT%H:%M:%SZ', MIN(observed_at_ts)) AS first_observed_at,
        strftime('%Y-%m-%dT%H:%M:%SZ', MAX(observed_at_ts)) AS last_observed_at,
        COUNT(*) AS total_source_observation_count
    FROM live_shadow_rows
),
supported_summaries AS (
    SELECT *
    FROM shadow_signal_summaries_v2
    WHERE segmentation_axes IS NOT DISTINCT FROM ['advisory_source']
       OR segmentation_axes IS NOT DISTINCT FROM [
           'advisory_source',
           'source_bucket_mapping_id',
           'source_pre_gate_advisory_snapshot_id'
       ]
       OR segmentation_axes IS NOT DISTINCT FROM ['fixture_identity']
),
expected_for_summaries AS (
    SELECT
        s.shadow_signal_summary_id,
        e.segmentation_axes,
        e.segment_key,
        e.advisory_source,
        e.source_bucket_mapping_id,
        e.source_pre_gate_advisory_snapshot_id,
        e.match_count,
        e.mismatch_count,
        e.abstention_count,
        e.observation_count,
        e.rate_denominator,
        e.agreement_rate,
        e.disagreement_rate,
        e.insufficient_evidence,
        e.signal_outcome,
        e.first_observed_at,
        e.last_observed_at
    FROM supported_summaries AS s
    JOIN expected_segments AS e
      ON array_to_string(s.segmentation_axes, ',') = e.segmentation_axes
),
actual_segments AS (
    SELECT
        shadow_signal_summary_id,
        segmentation_axes,
        CASE
            WHEN segmentation_axes = 'advisory_source'
                THEN advisory_source
            WHEN segmentation_axes = 'advisory_source,source_bucket_mapping_id,source_pre_gate_advisory_snapshot_id'
                THEN advisory_source || '|' || source_bucket_mapping_id || '|'
                    || COALESCE(source_pre_gate_advisory_snapshot_id, '')
            WHEN segmentation_axes = 'fixture_identity'
                THEN fixture_identity
            ELSE NULL
        END AS segment_key,
        advisory_source,
        source_bucket_mapping_id,
        source_pre_gate_advisory_snapshot_id,
        match_count,
        mismatch_count,
        abstention_count,
        observation_count,
        rate_denominator,
        agreement_rate,
        disagreement_rate,
        insufficient_evidence,
        signal_outcome,
        first_segment_observed_at AS first_observed_at,
        last_segment_observed_at AS last_observed_at
    FROM v_shadow_signal_summaries_v2_overview
    WHERE segmentation_axes IN (
        'advisory_source',
        'advisory_source,source_bucket_mapping_id,source_pre_gate_advisory_snapshot_id',
        'fixture_identity'
    )
),
segment_join AS (
    SELECT
        COALESCE(a.shadow_signal_summary_id, e.shadow_signal_summary_id) AS shadow_signal_summary_id,
        COALESCE(a.segment_key, e.segment_key) AS advisory_source,
        a.segment_key AS actual_segment_key,
        e.segment_key AS expected_segment_key,
        a.match_count AS actual_match_count,
        e.match_count AS expected_match_count,
        a.mismatch_count AS actual_mismatch_count,
        e.mismatch_count AS expected_mismatch_count,
        a.abstention_count AS actual_abstention_count,
        e.abstention_count AS expected_abstention_count,
        a.observation_count AS actual_observation_count,
        e.observation_count AS expected_observation_count,
        a.rate_denominator AS actual_rate_denominator,
        e.rate_denominator AS expected_rate_denominator,
        a.agreement_rate AS actual_agreement_rate,
        e.agreement_rate AS expected_agreement_rate,
        a.disagreement_rate AS actual_disagreement_rate,
        e.disagreement_rate AS expected_disagreement_rate,
        a.insufficient_evidence AS actual_insufficient_evidence,
        e.insufficient_evidence AS expected_insufficient_evidence,
        a.signal_outcome AS actual_signal_outcome,
        e.signal_outcome AS expected_signal_outcome,
        a.first_observed_at AS actual_first_observed_at,
        e.first_observed_at AS expected_first_observed_at,
        a.last_observed_at AS actual_last_observed_at,
        e.last_observed_at AS expected_last_observed_at
    FROM expected_for_summaries AS e
    FULL OUTER JOIN actual_segments AS a
      ON a.shadow_signal_summary_id = e.shadow_signal_summary_id
     AND a.segmentation_axes = e.segmentation_axes
     AND a.segment_key = e.segment_key
),
metadata_issues AS (
    SELECT
        shadow_signal_summary_id,
        CAST(NULL AS VARCHAR) AS advisory_source,
        'shadow_signal_summary_v2_unsupported_segmentation_axes' AS issue_type,
        'advisory_source|advisory_source,source_bucket_mapping_id,source_pre_gate_advisory_snapshot_id|fixture_identity'
            AS expected_value,
        array_to_string(segmentation_axes, ',') AS actual_value
    FROM shadow_signal_summaries_v2
    WHERE segmentation_axes IS DISTINCT FROM ['advisory_source']
      AND segmentation_axes IS DISTINCT FROM [
          'advisory_source',
          'source_bucket_mapping_id',
          'source_pre_gate_advisory_snapshot_id'
      ]
      AND segmentation_axes IS DISTINCT FROM ['fixture_identity']
    UNION ALL
    SELECT
        shadow_signal_summary_id,
        NULL,
        'shadow_signal_summary_v2_schema_version_mismatch' AS issue_type,
        'v2' AS expected_value,
        schema_version AS actual_value
    FROM shadow_signal_summaries_v2
    WHERE schema_version <> 'v2'
    UNION ALL
    SELECT
        shadow_signal_summary_id,
        NULL,
        'shadow_signal_summary_v2_derivation_method_mismatch' AS issue_type,
        'shadow_signal_summary_option_a_floor_10_v1' AS expected_value,
        derivation_method AS actual_value
    FROM shadow_signal_summaries_v2
    WHERE derivation_method <> 'shadow_signal_summary_option_a_floor_10_v1'
    UNION ALL
    SELECT
        shadow_signal_summary_id,
        NULL,
        'shadow_signal_summary_v2_source_relation_mismatch' AS issue_type,
        'overlay_shadow_logs' AS expected_value,
        derivation_inputs.source_relation AS actual_value
    FROM shadow_signal_summaries_v2
    WHERE derivation_inputs.source_relation <> 'overlay_shadow_logs'
    UNION ALL
    SELECT
        shadow_signal_summary_id,
        NULL,
        'shadow_signal_summary_v2_source_family_mismatch' AS issue_type,
        'overlay_shadow_logs' AS expected_value,
        derivation_inputs.source_artifact_family AS actual_value
    FROM shadow_signal_summaries_v2
    WHERE derivation_inputs.source_artifact_family <> 'overlay_shadow_logs'
    UNION ALL
    SELECT
        shadow_signal_summary_id,
        NULL,
        'shadow_signal_summary_v2_fixture_identity_rule_mismatch' AS issue_type,
        'committed_overlay_input_pair_v1' AS expected_value,
        derivation_inputs.fixture_identity_rule AS actual_value
    FROM shadow_signal_summaries_v2
    WHERE derivation_inputs.fixture_identity_rule <> 'committed_overlay_input_pair_v1'
    UNION ALL
    SELECT
        shadow_signal_summary_id,
        NULL,
        'shadow_signal_summary_v2_rate_denominator_rule_mismatch' AS issue_type,
        'match_plus_mismatch' AS expected_value,
        derivation_inputs.rate_denominator_rule AS actual_value
    FROM shadow_signal_summaries_v2
    WHERE derivation_inputs.rate_denominator_rule <> 'match_plus_mismatch'
    UNION ALL
    SELECT
        s.shadow_signal_summary_id,
        NULL,
        'shadow_signal_summary_v2_generated_at_mismatch' AS issue_type,
        expected_corpus_window.last_observed_at AS expected_value,
        s.generated_at AS actual_value
    FROM shadow_signal_summaries_v2 AS s
    CROSS JOIN expected_corpus_window
    WHERE s.generated_at <> expected_corpus_window.last_observed_at
    UNION ALL
    SELECT
        s.shadow_signal_summary_id,
        NULL,
        'shadow_signal_summary_v2_first_overlay_shadow_log_id_mismatch' AS issue_type,
        expected_corpus_window.first_overlay_shadow_log_id AS expected_value,
        s.corpus_window.first_overlay_shadow_log_id AS actual_value
    FROM shadow_signal_summaries_v2 AS s
    CROSS JOIN expected_corpus_window
    WHERE s.corpus_window.first_overlay_shadow_log_id <> expected_corpus_window.first_overlay_shadow_log_id
    UNION ALL
    SELECT
        s.shadow_signal_summary_id,
        NULL,
        'shadow_signal_summary_v2_last_overlay_shadow_log_id_mismatch' AS issue_type,
        expected_corpus_window.last_overlay_shadow_log_id AS expected_value,
        s.corpus_window.last_overlay_shadow_log_id AS actual_value
    FROM shadow_signal_summaries_v2 AS s
    CROSS JOIN expected_corpus_window
    WHERE s.corpus_window.last_overlay_shadow_log_id <> expected_corpus_window.last_overlay_shadow_log_id
    UNION ALL
    SELECT
        s.shadow_signal_summary_id,
        NULL,
        'shadow_signal_summary_v2_first_observed_at_mismatch' AS issue_type,
        expected_corpus_window.first_observed_at AS expected_value,
        s.corpus_window.first_observed_at AS actual_value
    FROM shadow_signal_summaries_v2 AS s
    CROSS JOIN expected_corpus_window
    WHERE s.corpus_window.first_observed_at <> expected_corpus_window.first_observed_at
    UNION ALL
    SELECT
        s.shadow_signal_summary_id,
        NULL,
        'shadow_signal_summary_v2_last_observed_at_mismatch' AS issue_type,
        expected_corpus_window.last_observed_at AS expected_value,
        s.corpus_window.last_observed_at AS actual_value
    FROM shadow_signal_summaries_v2 AS s
    CROSS JOIN expected_corpus_window
    WHERE s.corpus_window.last_observed_at <> expected_corpus_window.last_observed_at
    UNION ALL
    SELECT
        s.shadow_signal_summary_id,
        NULL,
        'shadow_signal_summary_v2_total_source_observation_count_mismatch' AS issue_type,
        CAST(expected_corpus_window.total_source_observation_count AS VARCHAR) AS expected_value,
        CAST(s.corpus_window.total_source_observation_count AS VARCHAR) AS actual_value
    FROM shadow_signal_summaries_v2 AS s
    CROSS JOIN expected_corpus_window
    WHERE s.corpus_window.total_source_observation_count <> expected_corpus_window.total_source_observation_count
    UNION ALL
    SELECT
        shadow_signal_summary_id,
        NULL,
        'shadow_signal_summary_v2_not_deterministic' AS issue_type,
        'true' AS expected_value,
        CAST(deterministic AS VARCHAR) AS actual_value
    FROM shadow_signal_summaries_v2
    WHERE deterministic IS DISTINCT FROM true
    UNION ALL
    SELECT
        shadow_signal_summary_id,
        NULL,
        'shadow_signal_summary_v2_not_advisory_only' AS issue_type,
        'true' AS expected_value,
        CAST(advisory_only AS VARCHAR) AS actual_value
    FROM shadow_signal_summaries_v2
    WHERE advisory_only IS DISTINCT FROM true
),
segment_presence_issues AS (
    SELECT
        shadow_signal_summary_id,
        advisory_source,
        'shadow_signal_summary_v2_missing_segment' AS issue_type,
        'present' AS expected_value,
        'missing' AS actual_value
    FROM segment_join
    WHERE actual_segment_key IS NULL
      AND expected_segment_key IS NOT NULL
    UNION ALL
    SELECT
        shadow_signal_summary_id,
        advisory_source,
        'shadow_signal_summary_v2_extra_segment' AS issue_type,
        'missing' AS expected_value,
        'present' AS actual_value
    FROM segment_join
    WHERE actual_segment_key IS NOT NULL
      AND expected_segment_key IS NULL
),
segment_value_issues AS (
    SELECT
        shadow_signal_summary_id,
        advisory_source,
        'shadow_signal_summary_v2_match_count_mismatch' AS issue_type,
        CAST(expected_match_count AS VARCHAR) AS expected_value,
        CAST(actual_match_count AS VARCHAR) AS actual_value
    FROM segment_join
    WHERE expected_segment_key IS NOT NULL
      AND actual_segment_key IS NOT NULL
      AND actual_match_count IS DISTINCT FROM expected_match_count
    UNION ALL
    SELECT
        shadow_signal_summary_id,
        advisory_source,
        'shadow_signal_summary_v2_mismatch_count_mismatch' AS issue_type,
        CAST(expected_mismatch_count AS VARCHAR) AS expected_value,
        CAST(actual_mismatch_count AS VARCHAR) AS actual_value
    FROM segment_join
    WHERE expected_segment_key IS NOT NULL
      AND actual_segment_key IS NOT NULL
      AND actual_mismatch_count IS DISTINCT FROM expected_mismatch_count
    UNION ALL
    SELECT
        shadow_signal_summary_id,
        advisory_source,
        'shadow_signal_summary_v2_abstention_count_mismatch' AS issue_type,
        CAST(expected_abstention_count AS VARCHAR) AS expected_value,
        CAST(actual_abstention_count AS VARCHAR) AS actual_value
    FROM segment_join
    WHERE expected_segment_key IS NOT NULL
      AND actual_segment_key IS NOT NULL
      AND actual_abstention_count IS DISTINCT FROM expected_abstention_count
    UNION ALL
    SELECT
        shadow_signal_summary_id,
        advisory_source,
        'shadow_signal_summary_v2_observation_count_mismatch' AS issue_type,
        CAST(expected_observation_count AS VARCHAR) AS expected_value,
        CAST(actual_observation_count AS VARCHAR) AS actual_value
    FROM segment_join
    WHERE expected_segment_key IS NOT NULL
      AND actual_segment_key IS NOT NULL
      AND actual_observation_count IS DISTINCT FROM expected_observation_count
    UNION ALL
    SELECT
        shadow_signal_summary_id,
        advisory_source,
        'shadow_signal_summary_v2_rate_denominator_mismatch' AS issue_type,
        CAST(expected_rate_denominator AS VARCHAR) AS expected_value,
        CAST(actual_rate_denominator AS VARCHAR) AS actual_value
    FROM segment_join
    WHERE expected_segment_key IS NOT NULL
      AND actual_segment_key IS NOT NULL
      AND actual_rate_denominator IS DISTINCT FROM expected_rate_denominator
    UNION ALL
    SELECT
        shadow_signal_summary_id,
        advisory_source,
        'shadow_signal_summary_v2_agreement_rate_mismatch' AS issue_type,
        CAST(expected_agreement_rate AS VARCHAR) AS expected_value,
        CAST(actual_agreement_rate AS VARCHAR) AS actual_value
    FROM segment_join
    WHERE expected_segment_key IS NOT NULL
      AND actual_segment_key IS NOT NULL
      AND actual_agreement_rate IS DISTINCT FROM expected_agreement_rate
    UNION ALL
    SELECT
        shadow_signal_summary_id,
        advisory_source,
        'shadow_signal_summary_v2_disagreement_rate_mismatch' AS issue_type,
        CAST(expected_disagreement_rate AS VARCHAR) AS expected_value,
        CAST(actual_disagreement_rate AS VARCHAR) AS actual_value
    FROM segment_join
    WHERE expected_segment_key IS NOT NULL
      AND actual_segment_key IS NOT NULL
      AND actual_disagreement_rate IS DISTINCT FROM expected_disagreement_rate
    UNION ALL
    SELECT
        shadow_signal_summary_id,
        advisory_source,
        'shadow_signal_summary_v2_insufficient_evidence_mismatch' AS issue_type,
        CAST(expected_insufficient_evidence AS VARCHAR) AS expected_value,
        CAST(actual_insufficient_evidence AS VARCHAR) AS actual_value
    FROM segment_join
    WHERE expected_segment_key IS NOT NULL
      AND actual_segment_key IS NOT NULL
      AND actual_insufficient_evidence IS DISTINCT FROM expected_insufficient_evidence
    UNION ALL
    SELECT
        shadow_signal_summary_id,
        advisory_source,
        'shadow_signal_summary_v2_signal_outcome_mismatch' AS issue_type,
        expected_signal_outcome AS expected_value,
        actual_signal_outcome AS actual_value
    FROM segment_join
    WHERE expected_segment_key IS NOT NULL
      AND actual_segment_key IS NOT NULL
      AND actual_signal_outcome IS DISTINCT FROM expected_signal_outcome
    UNION ALL
    SELECT
        shadow_signal_summary_id,
        advisory_source,
        'shadow_signal_summary_v2_first_observed_at_segment_mismatch' AS issue_type,
        expected_first_observed_at AS expected_value,
        actual_first_observed_at AS actual_value
    FROM segment_join
    WHERE expected_segment_key IS NOT NULL
      AND actual_segment_key IS NOT NULL
      AND actual_first_observed_at IS DISTINCT FROM expected_first_observed_at
    UNION ALL
    SELECT
        shadow_signal_summary_id,
        advisory_source,
        'shadow_signal_summary_v2_last_observed_at_segment_mismatch' AS issue_type,
        expected_last_observed_at AS expected_value,
        actual_last_observed_at AS actual_value
    FROM segment_join
    WHERE expected_segment_key IS NOT NULL
      AND actual_segment_key IS NOT NULL
      AND actual_last_observed_at IS DISTINCT FROM expected_last_observed_at
)
SELECT *
FROM metadata_issues
UNION ALL
SELECT *
FROM segment_presence_issues
UNION ALL
SELECT *
FROM segment_value_issues;

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
