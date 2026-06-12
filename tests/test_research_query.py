import hashlib
import json
from pathlib import Path

import pytest

from tools.research_query import query_layer
from tools.research_query.query_layer import (
    EXPERIMENTS_DIR,
    REGISTRY_PATH,
    RESULT_POPULATIONS_DIR,
    SWEEP_PLANS_DIR,
    STRATEGY_SPECS_DIR,
    TRIAL_LOG_PATH,
    VARIANT_MANIFESTS_DIR,
    ReadOnlyQueryError,
    init_duckdb,
    list_views,
    run_named_view,
    run_sql,
)


REQUIRED_VIEWS = {
    "v_candidate_overview",
    "v_concluded_candidates",
    "v_experiment_instances",
    "v_oos_metrics_by_candidate",
    "v_is_metrics_by_candidate",
    "v_gate_results_flat",
    "v_candidate_by_family",
    "v_information_inputs",
    "v_integrity_plan_report_pairs",
    "v_integrity_candidate_refs",
    "v_strategy_spec_overview",
    "v_strategy_spec_parameters",
    "v_strategy_spec_condition_groups",
    "v_strategy_spec_backtest_assumptions",
    "v_integrity_strategy_spec_non_authority",
    "v_integrity_strategy_spec_bounds",
    "v_integrity_strategy_spec_hash_readiness",
    "v_variant_manifest_overview",
    "v_variant_manifest_population",
    "v_variant_manifest_parameter_axes",
    "v_variant_manifest_assignments",
    "v_variant_manifest_hash_pinning",
    "v_variant_manifest_supersession",
    "v_sweep_plan_overview",
    "v_sweep_plan_validation_methods",
    "v_sweep_plan_trial_accounting",
    "v_sweep_plan_result_capture_expectations",
    "v_result_population_overview",
    "v_result_population_parent_lineage",
    "v_result_population_denominator",
    "v_result_population_outcome_counts",
    "v_result_population_variant_rows",
    "v_result_population_error_summary",
    "v_result_population_data_coverage",
    "v_result_population_backtest_assumptions",
    "v_result_population_identity_audit",
    "v_result_population_append_only_ledger",
    "v_result_population_ledger_events",
    "v_result_population_non_authority",
    "v_result_population_execution_context",
    "v_integrity_variant_manifest_non_authority",
    "v_integrity_variant_manifest_denominator",
    "v_integrity_variant_manifest_hash_readiness",
    "v_integrity_variant_manifest_supersession",
    "v_integrity_sweep_plan_non_authority",
    "v_integrity_sweep_plan_denominator",
    "v_integrity_sweep_plan_parent_manifest",
    "v_integrity_sweep_plan_no_computation",
    "v_integrity_result_population_denominator_mismatch",
    "v_integrity_result_population_outcome_count_mismatch",
    "v_integrity_result_population_missing_variant_rows",
    "v_integrity_result_population_unknown_outcome_category",
    "v_integrity_result_population_audit_in_identity_scope",
    "v_integrity_result_population_non_authority_violation",
    "v_integrity_result_population_canonical_evidence_violation",
    "v_integrity_result_population_append_only_violation",
    "v_integrity_result_population_offline_boundary_violation",
    "v_integrity_result_population_canonical_write_violation",
    "v_integrity_result_population_authority_key_violation",
    "v_integrity_result_population_parent_hash_chain_mismatch",
}

EXPECTED_COLUMNS = {
    "v_candidate_overview": [
        "candidate_id",
        "name",
        "status",
        "overall_verdict",
        "strategy_family",
        "timeframe",
        "free_parameter_count",
        "pipeline_stage",
        "hypothesis_md_path",
        "decision_record_path",
        "trial_id_count",
    ],
    "v_experiment_instances": [
        "candidate_id",
        "plan_id",
        "report_id",
        "plan_type",
        "execution_date",
        "overall_verdict",
        "trial_id_count",
    ],
    "v_oos_metrics_by_candidate": [
        "candidate_id",
        "report_id",
        "strategy_family",
        "timeframe",
        "oos_sharpe",
        "oos_max_drawdown",
        "oos_total_trades",
        "oos_cost_drag",
    ],
    "v_is_metrics_by_candidate": [
        "candidate_id",
        "report_id",
        "strategy_family",
        "timeframe",
        "is_sharpe",
        "is_source_field",
        "is_window_convention",
    ],
    "v_gate_results_flat": [
        "candidate_id",
        "report_id",
        "gate_id",
        "threshold",
        "observed",
        "pass",
    ],
    "v_candidate_by_family": [
        "strategy_family",
        "timeframe",
        "n_candidates",
        "n_no_go",
        "n_pass",
        "n_conditional",
        "n_inconclusive",
    ],
    "v_information_inputs": [
        "candidate_id",
        "information_input",
    ],
    "v_strategy_spec_overview": [
        "strategy_spec_id",
        "title",
        "status",
        "source_type",
        "instrument_family",
        "market_type",
        "primary_timeframe",
        "direction",
        "free_parameter_count",
        "max_free_parameters",
        "max_condition_group_depth",
        "operator_depth_bound",
        "hash_status",
        "intended_for_variant_manifest",
        "approval_scope",
    ],
    "v_strategy_spec_parameters": [
        "strategy_spec_id",
        "parameter_name",
        "parameter_type",
        "role",
        "default_value",
        "range_min",
        "range_max",
        "range_step",
        "included_in_variant_generation",
        "rationale",
    ],
    "v_strategy_spec_condition_groups": [
        "strategy_spec_id",
        "section",
        "group_id",
        "group_role",
        "logic",
        "condition_count",
        "subgroup_count",
        "declared_depth",
    ],
    "v_strategy_spec_backtest_assumptions": [
        "strategy_spec_id",
        "fee_side_assumption",
        "exchange_constraints_disclosed",
        "funding_notional_mode",
        "slippage_model",
        "fill_mode",
        "order_size_assumption",
        "liquidity_capacity_assumption",
        "liquidation_mode",
        "maintenance_margin_assumption",
        "mark_price_source",
        "bar_path_assumption",
    ],
    "v_variant_manifest_overview": [
        "variant_manifest_id",
        "status",
        "parent_strategy_spec_id",
        "parent_strategy_spec_hash",
        "parent_strategy_spec_review_status",
        "committed_population_count",
        "declared_variant_count",
        "population_cap",
        "search_family_id",
        "search_family_method",
        "pre_registration_status",
        "manifest_hash",
        "hash_status",
        "approval_scope",
    ],
    "v_variant_manifest_population": [
        "variant_manifest_id",
        "committed_population_count",
        "declared_variant_count",
        "included_variant_count",
        "excluded_variant_count",
        "invalid_variant_count",
        "not_attempted_variant_count",
        "population_cap",
        "planned_trial_count",
        "trial_budget_denominator",
        "denominator_count",
        "denominator_basis",
        "denominator_type",
        "adaptive_search_used",
        "winner_only_review_forbidden",
        "executed_only_denominator_forbidden",
    ],
    "v_variant_manifest_parameter_axes": [
        "variant_manifest_id",
        "axis_id",
        "parameter_name",
        "parent_strategy_spec_parameter_ref",
        "parameter_type",
        "units",
        "axis_kind",
        "generator_method",
        "counts_toward_parent_free_parameter_cap",
        "is_declared_in_parent_strategy_spec",
    ],
    "v_variant_manifest_assignments": [
        "variant_manifest_id",
        "variant_id",
        "assignment_status",
        "parameter_value_hash",
        "axis_ref_count",
        "exclusion_rule_count",
        "invalid_combination_rule_count",
        "status_reason",
        "generated_by_rule",
        "generation_order",
    ],
    "v_sweep_plan_overview": [
        "sweep_plan_id",
        "status",
        "parent_variant_manifest_id",
        "parent_manifest_hash",
        "manifest_committed_population_count",
        "manifest_population_cap",
        "manifest_pre_registration_status",
        "selection_mode",
        "selected_variant_count",
        "excluded_variant_count",
        "approval_scope",
    ],
    "v_sweep_plan_validation_methods": [
        "sweep_plan_id",
        "backtest_enabled",
        "walk_forward_oos_enabled",
        "declares_chronological_separation",
        "robustness_enabled",
        "robustness_family_count",
        "dsr_psr_mintrl_enabled",
        "dsr_denominator_ref",
        "dsr_computation_deferred",
        "monte_carlo_enabled",
        "monte_carlo_computation_deferred",
        "declarative_intent_only",
        "no_runner_hooks",
        "no_formulas",
        "no_computation",
    ],
    "v_sweep_plan_trial_accounting": [
        "sweep_plan_id",
        "committed_population_count",
        "selected_variant_count",
        "executed_variant_count",
        "successful_variant_count",
        "failed_variant_count",
        "errored_variant_count",
        "aborted_variant_count",
        "filtered_variant_count",
        "data_unavailable_variant_count",
        "excluded_variant_count",
        "not_attempted_variant_count",
        "multiple_testing_denominator",
        "denominator_basis",
        "denominator_equals_committed_population_count",
        "executed_only_denominator_forbidden",
        "successful_only_denominator_forbidden",
    ],
    "v_sweep_plan_result_capture_expectations": [
        "sweep_plan_id",
        "result_population_expected",
        "expected_result_population_ref",
        "must_capture_successful",
        "must_capture_failed",
        "must_capture_invalid",
        "must_capture_excluded",
        "must_capture_errored",
        "must_capture_aborted",
        "must_capture_filtered",
        "must_capture_data_unavailable",
        "must_capture_not_attempted",
        "winner_only_retention_forbidden",
        "canonical_evidence_mapping_deferred",
    ],
    "v_result_population_overview": [
        "result_population_id",
        "schema_version",
        "status",
        "parent_strategy_spec_id",
        "parent_variant_manifest_id",
        "parent_sweep_plan_id",
        "committed_denominator",
        "result_row_count",
        "outcome_counts_sum",
        "execution_mode",
        "offline_only",
        "review_status",
        "review_scope",
    ],
    "v_result_population_variant_rows": [
        "result_population_id",
        "variant_id",
        "row_id",
        "outcome_category",
        "attempted",
        "pnl",
        "return_pct",
        "drawdown",
        "trade_count",
        "sharpe",
        "non_success_reason",
        "error_category",
        "data_slice_identity",
        "parent_variant_id",
        "parent_sweep_plan_id",
        "parent_manifest_id",
    ],
}


def _jsonl_row_count(path: Path) -> int:
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())


def _registry_candidate_ids() -> set[str]:
    return {
        json.loads(line)["candidate_id"]
        for line in REGISTRY_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    }


def _file_checksums(paths: list[Path]) -> dict[Path, str]:
    return {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}


def _valid_candidate_row(**overrides):
    row = {
        "candidate_id": "H-900",
        "name": "Fixture Candidate",
        "status": "DRAFT",
        "overall_verdict": "PENDING",
        "strategy_family": "fixture",
        "timeframe": "15m",
        "information_inputs": ["ohlcv_15m"],
        "free_parameter_count": 1,
        "hypothesis_md_path": "research/hypotheses/H-900/HYPOTHESIS.md",
        "decision_record_path": None,
        "trial_ids": [],
        "pipeline_stage": "pre_registered",
        "created_at": "2026-05-30",
        "updated_at": "2026-05-30",
        "differentiation_summary": "Fixture candidate.",
        "notes": "pytest fixture",
    }
    row.update(overrides)
    return row


def _valid_plan(plan_id="EXP-9000", candidate_id="H-900"):
    return {
        "plan_id": plan_id,
        "candidate_id": candidate_id,
        "plan_type": "baseline",
        "rationale": "Fixture plan.",
        "hypothesis_to_test": "Fixture hypothesis.",
        "success_criteria": {
            "gates": ["D2-006"],
            "additional_criteria": ["Fixture criterion"],
        },
        "evaluation_window": {
            "in_sample": {"start": None, "end": None},
            "out_of_sample": {"start": None, "end": None},
        },
        "parameters": {"lookback": 12},
        "data_requirements": ["binance_um_perp_BTCUSDT_15m"],
        "pre_registration_date": "2026-05-30",
        "author": "pytest",
        "human_approval_required": False,
    }


def _valid_report(report_id="REP-9000", plan_id="EXP-9000", candidate_id="H-900"):
    return {
        "report_id": report_id,
        "plan_id": plan_id,
        "candidate_id": candidate_id,
        "execution_date": "2026-05-30",
        "trial_ids": ["trial-fixture"],
        "metrics": {
            "in_sample": {
                "sharpe": 0.0,
                "source_field": "fixture",
                "window_convention": "fixture",
            },
            "out_of_sample": {
                "sharpe": 0.0,
                "max_drawdown": 0.0,
                "trades": 1,
                "cost_drag_fraction": 0.0,
            },
        },
        "gate_results": [
            {
                "gate_id": "D2-006-G1",
                "threshold": 1.0,
                "observed": 0.0,
                "pass": False,
            }
        ],
        "overall_verdict": "NO-GO",
        "observations": "Fixture report.",
        "next_step_recommendation": "archive",
        "diagnostic_findings": ["Fixture diagnostic."],
    }


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _operand(ref="close") -> dict:
    return {
        "operand_type": "data_ref",
        "ref": ref,
        "field": "close",
        "timeframe": "1h",
        "lookback": {"bars": 1},
    }


def _condition(condition_id: str = "COND-1") -> dict:
    return {
        "condition_id": condition_id,
        "condition_role": "required",
        "left_operand": _operand("close"),
        "operator": "gt",
        "right_operand": {
            "operand_type": "constant",
            "ref": 100.0,
            "field": None,
            "timeframe": None,
            "lookback": None,
        },
        "units": None,
        "notes": None,
    }


def _condition_group(group_id: str = "GROUP-1") -> dict:
    return {
        "group_id": group_id,
        "group_role": "required",
        "logic": "all",
        "conditions": [_condition()],
        "subgroups": [],
        "notes": None,
    }


def _strategy_parameter(name: str = "lookback") -> dict:
    return {
        "name": name,
        "label": None,
        "description": None,
        "type": "integer",
        "units": "bars",
        "default": 20,
        "range": {
            "min": 5,
            "max": 50,
            "step": 5,
            "inclusive_min": True,
            "inclusive_max": True,
        },
        "allowed_values": [],
        "is_free_parameter": True,
        "included_in_variant_generation": True,
        "role": "entry",
        "rationale": "Pytest fixture parameter.",
        "constraints": [],
    }


def _true_flags(*names: str) -> dict:
    return {name: True for name in names}


def _valid_strategy_spec(strategy_spec_id: str = "STRAT-SPEC-9001") -> dict:
    return {
        "schema_version": "v1",
        "strategy_spec_id": strategy_spec_id,
        "title": "Pytest Strategy Spec",
        "short_name": "pytest-spec",
        "status": "draft",
        "non_execution_declaration": _true_flags(
            "human_review_surface_only",
            "not_executable",
            "not_runtime_authority",
            "not_paper_live_authority",
            "not_gate_authority",
            "not_candidate_approval",
            "not_exp_approval",
            "not_sweep_authority",
            "not_ranking_authority",
            "not_recommendation_authority",
            "not_readiness_authority",
            "not_transition_authority",
        ),
        "provenance": {
            "source_type": "manual_idea",
            "source_refs": ["pytest-fixture"],
            "prepared_by": "pytest",
            "created_at": "2026-06-01T00:00:00Z",
            "updated_at": "2026-06-01T00:00:00Z",
            "rationale": "Pytest fixture.",
            "source_constraints": [],
            "unresolved_claims": [],
        },
        "instruments": {
            "symbols": ["BTCUSDT"],
            "instrument_family": "crypto_perp",
            "venue_assumption": "Binance USDT-M",
            "market_type": "perpetual",
            "directions_allowed": ["long"],
            "leverage_assumption": None,
            "exchange_constraint_refs": [],
            "blockers": [],
        },
        "timeframe_and_data": {
            "primary_timeframe": "1h",
            "confirmation_timeframes": [],
            "host_data_refs": [
                {
                    "stream": "ohlcv",
                    "timeframe": "1h",
                    "field": "close",
                    "availability": "required",
                }
            ],
            "gap_handling_assumption": None,
            "missing_data_blockers": [],
        },
        "entry_logic": {
            "direction": "long",
            "groups": [_condition_group()],
            "notes": None,
        },
        "exit_logic": {
            "groups": [_condition_group("EXIT-GROUP-1")],
            "max_holding_period": {"enabled": False, "bars": None},
            "notes": None,
        },
        "risk_model": {
            "sizing_intent": "review_only",
            "exposure_limits": [],
            "stop_distance": None,
            "target_distance": None,
            "leverage_visibility": None,
            "liquidation_sensitivity_notes": None,
        },
        "filters": {
            "groups": [_condition_group("FILTER-GROUP-1")],
            "none_declared": False,
        },
        "free_parameters": {
            "max_free_parameters": 5,
            "counting_rule": (
                "parameters contains only entries where is_free_parameter=true; "
                "maxItems 5 enforces the D2-006-style MVP free-parameter cap"
            ),
            "parameters": [_strategy_parameter()],
            "no_free_parameters_declared": False,
        },
        "constraints": {
            "invalid_parameter_combinations": [],
            "unavailable_data_blockers": [],
            "deferred_pattern_blockers": [],
            "none_declared": True,
        },
        "review": {
            "human_review_required": True,
            "reviewer": None,
            "reviewed_at": None,
            "review_notes": [],
            "approval_scope": "none",
            "non_authority_acknowledgement": _true_flags(
                "not_candidate_approval",
                "not_exp_approval",
                "not_sweep_authority",
                "not_ranking_authority",
                "not_recommendation_authority",
                "not_readiness_authority",
                "not_transition_authority",
                "not_runtime_authority",
                "not_paper_live_authority",
                "not_gate_satisfaction",
            ),
        },
        "lineage": {
            "parent_refs": [],
            "supersedes": [],
            "amendment_of": None,
        },
        "hash_pinning": {
            "canonical_spec_hash": None,
            "hash_algorithm": None,
            "hash_scope_version": None,
            "hash_scope": [],
            "hash_status": "not_computed",
        },
        "pre_registration_support": {
            "intended_for_variant_manifest": False,
            "variant_manifest_ref": None,
            "frozen_snapshot_ref": None,
        },
        "backtest_realism_assumptions": {
            "fee_side_assumption": "maker_taker_visible",
            "exchange_constraints_disclosed": True,
            "funding_notional_mode": "unspecified",
            "slippage_model": "unspecified",
            "fill_mode": "unspecified",
            "order_size_assumption": "fixture size only",
            "liquidity_capacity_assumption": "fixture capacity only",
            "liquidation_mode": "unspecified",
            "maintenance_margin_assumption": None,
            "mark_price_source": "unspecified",
            "bar_path_assumption": "unspecified",
        },
        "max_condition_group_depth": 3,
    }


def _valid_variant_manifest(variant_manifest_id: str = "VM-9001") -> dict:
    return {
        "schema_version": "v1",
        "variant_manifest_id": variant_manifest_id,
        "status": "approved_for_sweep_planning",
        "non_execution_declaration": _true_flags(
            "planning_surface_only",
            "not_executable",
            "not_runner_authority",
            "not_sweep_authority",
            "not_result_authority",
            "not_candidate_approval",
            "not_exp_approval",
            "not_ranking_authority",
            "not_recommendation_authority",
            "not_readiness_authority",
            "not_transition_authority",
            "not_runtime_authority",
            "not_paper_live_authority",
            "not_gate_authority",
        ),
        "parent_strategy_spec": {
            "strategy_spec_id": "STRAT-SPEC-9001",
            "strategy_spec_schema_version": "v1",
            "strategy_spec_hash": "sha256:" + "1" * 64,
            "hash_algorithm": "sha256",
            "hash_scope_version": "strategy_spec_hash_scope_v1",
            "strategy_spec_review_status": "approved_for_variant_planning",
            "strategy_spec_ref": None,
            "mismatch_policy": "block",
            "missing_parent_policy": "block",
            "does_not_mutate_parent_strategy_spec": True,
        },
        "population_governance": {
            "population_cap": {
                "max_variants": 2,
                "cap_basis": "manual_grid",
                "cap_source": "human_declared",
                "cap_exception_authorized": False,
                "cap_exception_ref": None,
            },
            "declared_population": {
                "committed_population_count": 2,
                "declared_variant_count": 2,
                "included_variant_count": 2,
                "excluded_variant_count": 0,
                "invalid_variant_count": 0,
                "not_attempted_variant_count": 0,
            },
            "trial_budget": {
                "planned_trial_count": 2,
                "trial_budget_denominator": 2,
                "denominator_basis": "committed_pre_registered_population_count",
                "denominator_count": 2,
                "denominator_includes_failed": True,
                "denominator_includes_excluded": True,
                "denominator_includes_invalid": True,
                "denominator_includes_errored": True,
                "denominator_includes_aborted": True,
                "denominator_includes_filtered": True,
                "denominator_includes_data_unavailable": True,
                "denominator_includes_not_attempted": True,
                "executed_only_denominator_forbidden": True,
            },
            "multiple_testing_accounting": {
                "denominator_required": True,
                "denominator_type": "committed_pre_registered_population",
                "search_family_id": "SF-9001",
                "search_family_method": "manual_grid",
                "adaptive_search_used": False,
                "adaptive_search_authorization_ref": None,
                "all_trials_visible_required": True,
                "winner_only_review_forbidden": True,
            },
            "pre_registration": {
                "pre_registered": True,
                "pre_registration_status": "frozen_for_sweep_planning",
                "pre_registration_scope": "full_variant_population",
                "freeze_required_before_sweep": True,
                "post_hoc_addition_forbidden": True,
                "post_result_mutation_forbidden": True,
                "allowed_change_mode": "supersede_before_results_only",
            },
        },
        "parameter_axes": [
            {
                "axis_id": "AXIS-001",
                "parameter_name": "lookback",
                "parent_strategy_spec_parameter_ref": "free_parameters.parameters.lookback",
                "parameter_type": "integer",
                "units": "bars",
                "axis_kind": "free_parameter",
                "generator_method": "manual_grid",
                "allowed_values": [10, 20],
                "range": {
                    "min": 10,
                    "max": 20,
                    "step": 10,
                    "inclusive_min": True,
                    "inclusive_max": True,
                },
                "counts_toward_parent_free_parameter_cap": True,
                "is_declared_in_parent_strategy_spec": True,
                "invalid_combination_rule_refs": [],
                "notes": None,
            }
        ],
        "invalid_combination_rules": [],
        "exclusion_rules": [],
        "variant_assignments": [
            {
                "variant_id": "VAR-900001",
                "assignment_status": "included",
                "parameter_values": {"lookback": 10},
                "parameter_value_hash": "sha256:" + "2" * 64,
                "axis_refs": ["AXIS-001"],
                "exclusion_rule_refs": [],
                "invalid_combination_rule_refs": [],
                "status_reason": None,
                "lineage": {"generated_by_rule": "manual-grid", "generation_order": 1},
            },
            {
                "variant_id": "VAR-900002",
                "assignment_status": "included",
                "parameter_values": {"lookback": 20},
                "parameter_value_hash": "sha256:" + "3" * 64,
                "axis_refs": ["AXIS-001"],
                "exclusion_rule_refs": [],
                "invalid_combination_rule_refs": [],
                "status_reason": None,
                "lineage": {"generated_by_rule": "manual-grid", "generation_order": 2},
            },
        ],
        "manifest_hash_pinning": {
            "manifest_hash": "sha256:" + "4" * 64,
            "hash_algorithm": "sha256",
            "canonicalization": "json_canonical_v1",
            "hash_scope_version": "variant_manifest_hash_scope_v1",
            "hash_scope": [
                "schema_version",
                "variant_manifest_id",
                "parent_strategy_spec.strategy_spec_id",
                "parent_strategy_spec.strategy_spec_hash",
                "population_governance",
                "parameter_axes",
                "invalid_combination_rules",
                "exclusion_rules",
                "variant_assignments",
            ],
            "hash_status": "computed",
            "frozen_at": "2026-06-01T00:00:00Z",
            "pre_sweep_freeze_required": True,
            "post_result_mutation_forbidden": True,
        },
        "amendment_and_supersession": {
            "amendment_mode": "none",
            "supersedes": None,
            "supersession_lineage": [],
            "amendment_reason": None,
            "associated_results_state": "no_associated_results",
            "supersession_allowed": False,
            "close_only_after_results": True,
            "post_result_change": False,
            "preserve_prior_manifest_required": True,
            "fresh_denominator_required": True,
            "does_not_inherit_prior_results": True,
        },
        "lineage": {
            "parent_refs": [],
            "source_refs": [],
            "created_at": "2026-06-01T00:00:00Z",
            "updated_at": "2026-06-01T00:00:00Z",
            "audit_notes": [],
            "hash_refs": [],
        },
        "review": {
            "human_review_required": True,
            "reviewer": None,
            "reviewed_at": None,
            "review_notes": [],
            "approval_scope": "sweep_planning_only",
            "non_authority_acknowledgement": _true_flags(
                "not_candidate_approval",
                "not_exp_approval",
                "not_sweep_authority",
                "not_runner_authority",
                "not_result_authority",
                "not_ranking_authority",
                "not_recommendation_authority",
                "not_readiness_authority",
                "not_transition_authority",
                "not_runtime_authority",
                "not_paper_live_authority",
                "not_gate_satisfaction",
            ),
        },
    }


def _valid_sweep_plan(manifest: dict, sweep_plan_id: str = "SWEEP-PLAN-9001") -> dict:
    manifest_hash = manifest["manifest_hash_pinning"]["manifest_hash"]
    return {
        "schema_version": "v1",
        "sweep_plan_id": sweep_plan_id,
        "status": "approved_for_offline_run_planning",
        "non_execution_declaration": _true_flags(
            "planning_surface_only",
            "not_executable",
            "not_runner_authority",
            "not_sweep_authority",
            "not_result_authority",
            "not_candidate_approval",
            "not_exp_approval",
            "not_ranking_authority",
            "not_recommendation_authority",
            "not_readiness_authority",
            "not_transition_authority",
            "not_runtime_authority",
            "not_paper_live_authority",
            "not_gate_authority",
        ),
        "parent_variant_manifest": {
            "variant_manifest_id": manifest["variant_manifest_id"],
            "variant_manifest_schema_version": "v1",
            "manifest_hash": manifest_hash,
            "hash_algorithm": "sha256",
            "manifest_population_count": 2,
            "manifest_committed_population_count": 2,
            "manifest_population_cap": 2,
            "manifest_pre_registration_status": "frozen_for_sweep_planning",
            "mismatch_policy": "block",
            "missing_manifest_policy": "block",
            "one_manifest_only": True,
        },
        "test_selection": {
            "selection_mode": "all_manifest_variants",
            "selected_variant_ids": ["VAR-900001", "VAR-900002"],
            "excluded_variant_ids": [],
            "subset_selection_rule": None,
            "declared_before_results": True,
            "post_hoc_addition_forbidden": True,
            "outside_manifest_variants_forbidden": True,
        },
        "validation_methods": {
            "backtest": {"enabled": True, "method_ref": None, "notes": None},
            "walk_forward_oos": {
                "enabled": True,
                "method_ref": None,
                "declares_chronological_separation": True,
                "notes": None,
            },
            "robustness": {
                "enabled": False,
                "method_ref": None,
                "families_declared": [],
                "notes": None,
            },
            "dsr_psr_mintrl_accounting": {
                "enabled": True,
                "denominator_ref": "committed_population_count",
                "computation_deferred": True,
                "notes": None,
            },
            "monte_carlo": {
                "enabled": False,
                "method_ref": None,
                "computation_deferred": True,
                "notes": None,
            },
            "declarative_intent_only": True,
            "no_runner_hooks": True,
            "no_formulas": True,
            "no_computation": True,
        },
        "data_and_timeframe_assumptions": {
            "primary_timeframe": "1h",
            "confirmation_timeframes": [],
            "data_refs": [
                {
                    "stream": "ohlcv",
                    "timeframe": "1h",
                    "field": "close",
                    "availability": "required",
                }
            ],
            "missing_data_posture": "block_if_missing",
            "gap_handling_assumption": None,
        },
        "realism_assumptions": {
            "fee_side_assumption": None,
            "exchange_constraints_disclosed": False,
            "funding_notional_mode": "unspecified",
            "slippage_model": "unspecified",
            "fill_mode": "unspecified",
            "order_size_assumption": None,
            "liquidity_capacity_assumption": None,
            "liquidation_mode": "unspecified",
            "maintenance_margin_assumption": None,
            "mark_price_source": "unspecified",
            "bar_path_assumption": "unspecified",
            "declarations_only": True,
        },
        "result_capture_expectations": {
            "result_population_expected": True,
            "expected_result_population_ref": None,
            "must_capture_successful": True,
            "must_capture_failed": True,
            "must_capture_invalid": True,
            "must_capture_excluded": True,
            "must_capture_errored": True,
            "must_capture_aborted": True,
            "must_capture_filtered": True,
            "must_capture_data_unavailable": True,
            "must_capture_not_attempted": True,
            "winner_only_retention_forbidden": True,
            "canonical_evidence_mapping_deferred": True,
        },
        "trial_accounting": {
            "committed_population_count": 2,
            "selected_variant_count": 2,
            "executed_variant_count": 0,
            "successful_variant_count": 0,
            "failed_variant_count": 0,
            "errored_variant_count": 0,
            "aborted_variant_count": 0,
            "filtered_variant_count": 0,
            "data_unavailable_variant_count": 0,
            "excluded_variant_count": 0,
            "not_attempted_variant_count": 2,
            "multiple_testing_denominator": 2,
            "denominator_basis": "committed_pre_registered_population_count",
            "denominator_equals_committed_population_count": True,
            "executed_only_denominator_forbidden": True,
            "successful_only_denominator_forbidden": True,
            "failed_variants_remain_in_denominator": True,
            "excluded_variants_remain_in_denominator": True,
            "invalid_variants_remain_in_denominator": True,
            "errored_variants_remain_in_denominator": True,
            "aborted_variants_remain_in_denominator": True,
            "filtered_variants_remain_in_denominator": True,
            "data_unavailable_variants_remain_in_denominator": True,
            "not_attempted_variants_remain_in_denominator": True,
        },
        "lineage": {
            "parent_manifest_ref": {
                "ref_type": "variant_manifest",
                "ref_id": manifest["variant_manifest_id"],
                "ref_path": None,
                "ref_hash": manifest_hash,
            },
            "parent_strategy_spec_ref": {
                "ref_type": "strategy_spec",
                "ref_id": "STRAT-SPEC-9001",
                "ref_path": None,
                "ref_hash": manifest["parent_strategy_spec"]["strategy_spec_hash"],
            },
            "search_family_id": "SF-9001",
            "source_refs": [],
            "created_at": "2026-06-01T00:00:00Z",
            "updated_at": "2026-06-01T00:00:00Z",
            "audit_notes": [],
        },
        "review": {
            "human_review_required": True,
            "reviewer": None,
            "reviewed_at": None,
            "review_notes": [],
            "approval_scope": "offline_run_planning_only",
            "non_authority_acknowledgement": _true_flags(
                "not_candidate_approval",
                "not_exp_approval",
                "not_runner_authority",
                "not_sweep_authority",
                "not_result_authority",
                "not_ranking_authority",
                "not_recommendation_authority",
                "not_readiness_authority",
                "not_transition_authority",
                "not_runtime_authority",
                "not_paper_live_authority",
                "not_gate_satisfaction",
            ),
        },
        "amendment_and_supersession": {
            "amendment_mode": "none",
            "supersedes": None,
            "supersession_lineage": [],
            "amendment_reason": None,
            "associated_results_state": "no_associated_results",
            "supersession_allowed": False,
            "close_only_after_results": True,
            "post_result_change": False,
            "preserve_prior_sweep_plan_required": True,
            "does_not_modify_parent_manifest": True,
            "does_not_modify_manifest_denominator": True,
        },
    }


def _valid_result_population(result_population_id: str = "RP-9001") -> dict:
    strategy_hash = "sha256:" + "1" * 64
    manifest_hash = "sha256:" + "4" * 64
    sweep_hash = "sha256:" + "5" * 64
    input_hash = "sha256:" + "6" * 64
    result_hash = "sha256:" + "7" * 64
    rows = [
        _result_population_row(result_population_id, 1, "VAR-900001", "successful"),
        _result_population_row(result_population_id, 2, "VAR-900002", "failed"),
    ]
    return {
        "schema_version": "v1",
        "result_population_id": result_population_id,
        "status": "generated",
        "non_authority_declaration": {
            **_true_flags(
                "not_executable",
                "not_runner_authority",
                "not_sweep_authority",
                "not_result_authority",
                "not_candidate_approval",
                "not_exp_approval",
                "not_ranking_authority",
                "not_recommendation_authority",
                "not_readiness_authority",
                "not_transition_authority",
                "not_runtime_authority",
                "not_paper_live_authority",
                "not_gate_authority",
                "not_canonical_evidence_replacement",
                "not_trial_log_replacement",
                "not_outcome_ledger_replacement",
                "not_reconciliation_authority",
                "not_decision_authority",
                "not_exp_replacement",
                "not_rep_replacement",
                "not_ol_replacement",
                "not_rec_replacement",
                "not_dec_replacement",
            ),
            "canonical_evidence_relationship": "reference_only",
        },
        "parent_strategy_spec": {
            "strategy_spec_id": "STRAT-SPEC-9001",
            "strategy_spec_schema_version": "v1",
            "strategy_spec_hash": strategy_hash,
            "hash_algorithm": "sha256",
            "hash_scope_version": "strategy_spec_hash_scope_v1",
            "strategy_spec_ref": None,
            "mismatch_policy": "block",
            "missing_parent_policy": "block",
        },
        "parent_variant_manifest": {
            "variant_manifest_id": "VM-9001",
            "variant_manifest_schema_version": "v1",
            "manifest_hash": manifest_hash,
            "hash_algorithm": "sha256",
            "hash_scope_version": "variant_manifest_hash_scope_v1",
            "manifest_ref": None,
            "manifest_pre_registration_status": "frozen_for_sweep_planning",
            "committed_population_count": 2,
            "mismatch_policy": "block",
            "missing_manifest_policy": "block",
        },
        "parent_sweep_plan": {
            "sweep_plan_id": "SWEEP-PLAN-9001",
            "sweep_plan_schema_version": "v1",
            "sweep_plan_identity_hash": sweep_hash,
            "hash_algorithm": "sha256",
            "hash_scope_version": "sweep_plan_identity_hash_scope_v1",
            "sweep_plan_ref": None,
            "manifest_id": "VM-9001",
            "manifest_hash": manifest_hash,
            "committed_population_count": 2,
            "selected_variant_count": 2,
            "mismatch_policy": "block",
            "missing_sweep_plan_policy": "block",
        },
        "execution_context": {
            "runner_id": "offline-research-runner",
            "runner_version": "pytest-manual",
            "runner_code_ref": "manual_pytest_fixture",
            "repo_commit": "pytest",
            "environment_summary": ["pytest"],
            "dependency_summary": ["duckdb"],
            "determinism_seed": 7,
            "execution_mode": "offline_research",
            "offline_only": True,
            "no_runtime_contact": True,
            "no_paper_live_contact": True,
            "no_broker_exchange_order_contact": True,
            "no_protected_path_contact": True,
        },
        "input_identity_hash": {
            "hash": input_hash,
            "hash_algorithm": "sha256",
            "canonicalization": "json_canonical_v1",
            "hash_scope_version": "input_identity_hash_scope_v1",
            "hash_scope": [
                "parent_strategy_spec.strategy_spec_hash",
                "parent_variant_manifest.manifest_hash",
                "parent_sweep_plan.sweep_plan_identity_hash",
            ],
            "audit_envelope_excluded": True,
            "audit_envelope_exclusion_reason": (
                "administrative_audit_metadata_is_excluded_from_scientific_identity"
            ),
        },
        "result_population_identity_hash": {
            "hash": result_hash,
            "hash_algorithm": "sha256",
            "canonicalization": "json_canonical_v1",
            "hash_scope_version": "result_population_identity_hash_scope_v1",
            "hash_scope": [
                "parent_strategy_spec.strategy_spec_hash",
                "parent_variant_manifest.manifest_hash",
                "parent_sweep_plan.sweep_plan_identity_hash",
                "variant_result_rows",
            ],
            "audit_envelope_excluded": True,
            "audit_envelope_exclusion_reason": (
                "administrative_audit_metadata_is_excluded_from_scientific_identity"
            ),
        },
        "audit_envelope": {
            "excluded_from_input_identity_hash": True,
            "excluded_from_result_population_identity_hash": True,
            "may_contain_scientific_content": False,
            "administrative_only": True,
            "created_at": "2026-06-01T00:00:00Z",
            "created_by": "pytest",
            "review_notes": [],
            "operator_notes": [],
            "validation_run_logs": [],
            "administrative_lineage": [],
        },
        "committed_denominator_snapshot": {
            "denominator_basis": "committed_pre_registered_population_count",
            "parent_manifest_committed_population_count": 2,
            "parent_sweep_plan_committed_population_count": 2,
            "selected_variant_count": 2,
            "result_row_count": 2,
            "outcome_counts_sum": 2,
            "committed_denominator": 2,
            **_true_flags(
                "denominator_equals_parent_manifest_committed_population_count",
                "denominator_equals_parent_sweep_plan_committed_population_count",
                "outcome_counts_sum_equals_committed_denominator",
                "result_row_count_equals_committed_denominator",
                "executed_only_denominator_forbidden",
                "successful_only_denominator_forbidden",
                "winner_only_retention_forbidden",
                "post_hoc_cleanup_forbidden",
                "failed_variants_remain_in_denominator",
                "invalid_variants_remain_in_denominator",
                "excluded_variants_remain_in_denominator",
                "errored_variants_remain_in_denominator",
                "aborted_variants_remain_in_denominator",
                "filtered_variants_remain_in_denominator",
                "data_unavailable_variants_remain_in_denominator",
                "not_attempted_variants_remain_in_denominator",
            ),
        },
        "variant_result_rows": rows,
        "outcome_category_counts": {
            "successful": 1,
            "failed": 1,
            "invalid": 0,
            "excluded": 0,
            "errored": 0,
            "aborted": 0,
            "filtered": 0,
            "data_unavailable": 0,
            "not_attempted": 0,
            "counts_sum": 2,
            "counts_sum_equals_committed_denominator": True,
        },
        "append_only_ledger": {
            "ledger_required": True,
            "append_only": True,
            "post_commit_in_place_mutation_forbidden": True,
            "scientific_identity_mutation_forbidden_after_finalization": True,
            "corrections_require_append_only_event": True,
            "supersession_preserves_prior_result_population": True,
            "creation_event_ref": f"{result_population_id}-EVENT-001",
            "events": [
                {
                    "event_id": f"{result_population_id}-EVENT-001",
                    "event_type": "created",
                    "event_timestamp": "2026-06-01T00:00:00Z",
                    "actor_or_tool": "pytest",
                    "related_artifact_refs": [],
                    "notes": ["manual temporary fixture"],
                }
            ],
        },
        "validation_summary": {
            "schema_validation_status": "passed",
            "validator_status": "passed",
            "validator_version": "pytest",
            "validator_identity": "manual_pytest_fixture",
            "validation_timestamp": "2026-06-01T00:00:00Z",
            "blocking_errors": [],
            "non_blocking_warnings": [],
            "validator_authority_boundary": "evidence_only_no_approval_no_execution",
            "validator_does_not_approve": True,
            "validator_does_not_recommend": True,
            "validator_does_not_rank": True,
            "validator_does_not_execute": True,
            "validator_does_not_contact_runtime": True,
        },
        "error_summary": {
            "failed": 1,
            "errored": 0,
            "aborted": 0,
            "filtered": 0,
            "data_unavailable": 0,
            "not_attempted": 0,
            "invalid": 0,
            "excluded": 0,
            "all_error_categories_counted_in_denominator": True,
            "error_rows_preserved": True,
        },
        "data_coverage_summary": {
            "data_catalog_ref": "pytest",
            "data_slice_identity": "pytest-slice",
            "timeframe": "1h",
            "data_stream": "ohlcv",
            "missing_data_policy": "block_if_missing",
            "irreparable_gap_count": 0,
            "data_unavailable_count": 0,
            "data_coverage_notes": [],
        },
        "backtest_assumption_summary": {
            "fee_side_assumption": "taker_entry_taker_exit",
            "exchange_constraint_disclosure": "true",
            "funding_notional": "entry_price",
            "slippage_model": "fixed_bps",
            "fill_mode": "complete",
            "order_size_assumption": "fixed_1_contract",
            "liquidity_capacity_assumption": "fixture capacity",
            "liquidation_mode": "zero_equity",
            "maintenance_margin_assumption": None,
            "mark_price_source": "close",
            "bar_path_assumption": "next_open_close_mark",
            "records_assumptions_only": True,
        },
        "lineage": {
            "strategy_spec_id": "STRAT-SPEC-9001",
            "variant_manifest_id": "VM-9001",
            "sweep_plan_id": "SWEEP-PLAN-9001",
            "result_population_id": result_population_id,
            "parent_hash_chain": {
                "strategy_spec_hash": strategy_hash,
                "variant_manifest_hash": manifest_hash,
                "sweep_plan_identity_hash": sweep_hash,
                "input_identity_hash": input_hash,
            },
            "created_from_validated_inputs": True,
            "complete_population_lineage_preserved": True,
        },
        "review": {
            "review_status": "not_reviewed",
            "review_scope": "none",
            "review_notes": [],
            "non_authority_acknowledgement": _true_flags(
                "not_approval",
                "not_recommendation",
                "not_readiness",
                "not_transition",
                "not_gate_satisfaction",
                "not_runtime_authority",
                "not_paper_live_authority",
            ),
        },
    }


def _result_population_row(
    result_population_id: str,
    row_number: int,
    variant_id: str,
    outcome: str,
) -> dict:
    successful = outcome == "successful"
    return {
        "variant_id": variant_id,
        "row_id": f"{result_population_id}-ROW-{row_number:06d}",
        "row_identity_hash": "sha256:" + f"{row_number}".zfill(64),
        "assignment_hash": "sha256:" + f"{row_number + 10}".zfill(64),
        "assignment_ref": None,
        "outcome_category": outcome,
        "attempted": True,
        "metrics": {
            "pnl": 10.0 if successful else None,
            "return_pct": 0.01 if successful else None,
            "drawdown": 0.02 if successful else None,
            "trade_count": 1 if successful else None,
            "win_rate": 1.0 if successful else None,
            "sharpe": 1.1 if successful else None,
            "fees": 1.0 if successful else None,
            "funding": 0.0 if successful else None,
            "slippage": 0.5 if successful else None,
            "exposure": 1.0 if successful else None,
        },
        "non_success": {
            "reason": None if successful else "fixture failure",
            "rule_ref": None,
            "declared_before_results": None if successful else True,
            "counts_in_denominator": True,
        },
        "error": {
            "error_category": None if successful else "strategy_underperformance",
            "error_message_class": None,
            "is_infrastructure_error": None if successful else False,
            "is_strategy_underperformance": None if successful else True,
            "counts_in_denominator": True,
        },
        "data_coverage": {
            "data_catalog_ref": "pytest",
            "data_slice_identity": "pytest-slice",
            "timeframe": "1h",
            "data_stream": "ohlcv",
            "missing_data_policy": "block_if_missing",
            "irreparable_gap": False,
            "counts_in_denominator": True,
        },
        "backtest_assumption_ref": "backtest_assumption_summary",
        "lineage": {
            "parent_variant_id": variant_id,
            "parent_variant_assignment_hash": "sha256:" + f"{row_number + 10}".zfill(64),
            "parent_variant_assignment_ref": None,
            "parent_sweep_plan_id": "SWEEP-PLAN-9001",
            "parent_manifest_id": "VM-9001",
        },
        "row_mutation_policy": _true_flags(
            "scientific_row_identity_immutable_after_commit",
            "corrections_require_append_only_event",
            "post_commit_in_place_mutation_forbidden",
            "post_hoc_cleanup_forbidden",
        ),
    }


def _init_temp_query_layer(
    monkeypatch,
    tmp_path,
    candidates,
    plans,
    reports,
    strategy_specs=None,
    variant_manifests=None,
    sweep_plans=None,
    result_populations=None,
):
    registry_path = tmp_path / "research" / "candidate_registry.jsonl"
    trial_log_path = tmp_path / "research" / "trial_log.jsonl"
    experiments_dir = tmp_path / "research" / "experiments"
    strategy_specs_dir = tmp_path / "research" / "strategy_specs"
    variant_manifests_dir = tmp_path / "research" / "variant_manifests"
    sweep_plans_dir = tmp_path / "research" / "sweep_plans"
    result_populations_dir = tmp_path / "research" / "result_populations"

    registry_path.parent.mkdir(parents=True, exist_ok=True)
    registry_path.write_text(
        "\n".join(json.dumps(candidate) for candidate in candidates) + "\n",
        encoding="utf-8",
    )
    trial_log_path.write_text(json.dumps({"trial_id": "trial-fixture"}) + "\n", encoding="utf-8")

    for plan in plans:
        _write_json(experiments_dir / f"{plan['plan_id']}.plan.json", plan)
    for report in reports:
        _write_json(experiments_dir / f"{report['report_id']}.report.json", report)
    for strategy_spec in strategy_specs or []:
        _write_json(
            strategy_specs_dir / f"{strategy_spec['strategy_spec_id']}.strategy_spec.json",
            strategy_spec,
        )
    for variant_manifest in variant_manifests or []:
        _write_json(
            variant_manifests_dir
            / f"{variant_manifest['variant_manifest_id']}.variant_manifest.json",
            variant_manifest,
        )
    for sweep_plan in sweep_plans or []:
        _write_json(
            sweep_plans_dir / f"{sweep_plan['sweep_plan_id']}.sweep_plan.json",
            sweep_plan,
        )
    for result_population in result_populations or []:
        _write_json(
            result_populations_dir
            / f"{result_population['result_population_id']}.result_population.json",
            result_population,
        )

    monkeypatch.setattr(query_layer, "REGISTRY_PATH", registry_path)
    monkeypatch.setattr(query_layer, "TRIAL_LOG_PATH", trial_log_path)
    monkeypatch.setattr(query_layer, "EXPERIMENTS_DIR", experiments_dir)
    monkeypatch.setattr(query_layer, "STRATEGY_SPECS_DIR", strategy_specs_dir)
    monkeypatch.setattr(query_layer, "VARIANT_MANIFESTS_DIR", variant_manifests_dir)
    monkeypatch.setattr(query_layer, "SWEEP_PLANS_DIR", sweep_plans_dir)
    monkeypatch.setattr(query_layer, "RESULT_POPULATIONS_DIR", result_populations_dir)

    return init_duckdb()


@pytest.fixture()
def conn():
    connection = init_duckdb()
    try:
        yield connection
    finally:
        connection.close()


def test_init_succeeds():
    connection = init_duckdb()
    connection.close()


def test_candidate_row_count(conn):
    expected_count = _jsonl_row_count(REGISTRY_PATH)

    actual_count = conn.execute("SELECT COUNT(*) FROM candidates").fetchone()[0]

    assert actual_count == expected_count


def test_experiment_plan_count(conn):
    expected_count = len(list(EXPERIMENTS_DIR.glob("EXP-*.plan.json")))

    actual_count = conn.execute("SELECT COUNT(*) FROM exp_plans").fetchone()[0]

    assert actual_count == expected_count


def test_experiment_report_count(conn):
    expected_count = len(list(EXPERIMENTS_DIR.glob("REP-*.report.json")))

    actual_count = conn.execute("SELECT COUNT(*) FROM exp_reports").fetchone()[0]

    assert actual_count == expected_count


def test_named_views_present(conn):
    view_names = set(list_views(conn))

    assert REQUIRED_VIEWS <= view_names
    for view_name in REQUIRED_VIEWS:
        conn.execute(f'SELECT * FROM "{view_name}" LIMIT 1').fetchall()


def test_named_views_return_expected_columns(conn):
    for view_name, expected_columns in EXPECTED_COLUMNS.items():
        rows = conn.execute(f'SELECT * FROM "{view_name}" LIMIT 0')
        actual_columns = [description[0] for description in rows.description]

        assert actual_columns == expected_columns


def test_candidate_overview_contains_all_registered_candidates(conn):
    expected_candidate_ids = _registry_candidate_ids()

    rows = conn.execute("SELECT candidate_id FROM v_candidate_overview").fetchall()
    actual_candidate_ids = {row[0] for row in rows}

    assert actual_candidate_ids == expected_candidate_ids


def test_oos_metrics_only_concluded(conn):
    non_concluded_count = conn.execute(
        """
        SELECT COUNT(*)
        FROM v_oos_metrics_by_candidate AS metrics
        JOIN candidates AS candidates
          ON metrics.candidate_id = candidates.candidate_id
        WHERE candidates.status <> 'CONCLUDED'
        """
    ).fetchone()[0]

    assert non_concluded_count == 0


def test_integrity_plan_report_pairs_empty_under_healthy_state(conn):
    rows = conn.execute("SELECT * FROM v_integrity_plan_report_pairs").fetchall()

    assert rows == []


def test_integrity_plan_report_pairs_allows_valid_pre_execution_plan(monkeypatch, tmp_path):
    candidate = _valid_candidate_row(candidate_id="H-012")
    plan = _valid_plan(plan_id="EXP-9012", candidate_id="H-012")
    report = _valid_report(report_id="REP-9000", plan_id="EXP-9001", candidate_id="H-012")

    connection = _init_temp_query_layer(monkeypatch, tmp_path, [candidate], [plan], [report])
    try:
        rows = connection.execute("SELECT * FROM v_integrity_plan_report_pairs").fetchall()

        assert ("plan_without_report", "EXP-9012", "H-012", None) not in rows
    finally:
        connection.close()


def test_integrity_plan_report_pairs_flags_unknown_candidate_without_report(monkeypatch, tmp_path):
    candidate = _valid_candidate_row(candidate_id="H-900")
    plan = _valid_plan(plan_id="EXP-9000", candidate_id="H-999")
    report = _valid_report(report_id="REP-9000", plan_id="EXP-9001", candidate_id="H-900")

    connection = _init_temp_query_layer(monkeypatch, tmp_path, [candidate], [plan], [report])
    try:
        rows = connection.execute(
            """
            SELECT issue_type, plan_id, candidate_id, report_id
            FROM v_integrity_plan_report_pairs
            WHERE issue_type = 'plan_without_report'
            """
        ).fetchall()

        assert rows == [("plan_without_report", "EXP-9000", "H-999", None)]
    finally:
        connection.close()


def test_integrity_plan_report_pairs_flags_concluded_candidate_without_report(monkeypatch, tmp_path):
    candidate = _valid_candidate_row(
        candidate_id="H-901",
        status="CONCLUDED",
        overall_verdict="NO-GO",
        pipeline_stage="baseline_tested",
        trial_ids=["trial-fixture"],
        decision_record_path="research/decisions/DEC-9001.md",
    )
    plan = _valid_plan(plan_id="EXP-9001", candidate_id="H-901")
    report = _valid_report(report_id="REP-9001", plan_id="EXP-9002", candidate_id="H-901")

    connection = _init_temp_query_layer(monkeypatch, tmp_path, [candidate], [plan], [report])
    try:
        rows = connection.execute(
            """
            SELECT issue_type, plan_id, candidate_id, report_id
            FROM v_integrity_plan_report_pairs
            WHERE issue_type = 'plan_without_report'
            """
        ).fetchall()

        assert rows == [("plan_without_report", "EXP-9001", "H-901", None)]
    finally:
        connection.close()


def test_integrity_plan_report_pairs_flags_candidate_with_trial_ids(monkeypatch, tmp_path):
    candidate = _valid_candidate_row(candidate_id="H-902", trial_ids=["trial-fixture"])
    plan = _valid_plan(plan_id="EXP-9002", candidate_id="H-902")
    report = _valid_report(report_id="REP-9002", plan_id="EXP-9003", candidate_id="H-902")

    connection = _init_temp_query_layer(monkeypatch, tmp_path, [candidate], [plan], [report])
    try:
        rows = connection.execute(
            """
            SELECT issue_type, plan_id, candidate_id, report_id
            FROM v_integrity_plan_report_pairs
            WHERE issue_type = 'plan_without_report'
            """
        ).fetchall()

        assert rows == [("plan_without_report", "EXP-9002", "H-902", None)]
    finally:
        connection.close()


def test_integrity_plan_report_pairs_flags_candidate_with_decision_record(monkeypatch, tmp_path):
    candidate = _valid_candidate_row(
        candidate_id="H-903",
        decision_record_path="research/decisions/DEC-9003.md",
    )
    plan = _valid_plan(plan_id="EXP-9003", candidate_id="H-903")
    report = _valid_report(report_id="REP-9003", plan_id="EXP-9004", candidate_id="H-903")

    connection = _init_temp_query_layer(monkeypatch, tmp_path, [candidate], [plan], [report])
    try:
        rows = connection.execute(
            """
            SELECT issue_type, plan_id, candidate_id, report_id
            FROM v_integrity_plan_report_pairs
            WHERE issue_type = 'plan_without_report'
            """
        ).fetchall()

        assert rows == [("plan_without_report", "EXP-9003", "H-903", None)]
    finally:
        connection.close()


def test_integrity_plan_report_pairs_preserves_report_without_plan(monkeypatch, tmp_path):
    candidate = _valid_candidate_row(candidate_id="H-904")
    plan = _valid_plan(plan_id="EXP-9004", candidate_id="H-904")
    report = _valid_report(report_id="REP-9004", plan_id="EXP-9999", candidate_id="H-904")

    connection = _init_temp_query_layer(monkeypatch, tmp_path, [candidate], [plan], [report])
    try:
        rows = connection.execute(
            """
            SELECT issue_type, plan_id, candidate_id, report_id
            FROM v_integrity_plan_report_pairs
            WHERE issue_type = 'report_without_plan'
            """
        ).fetchall()

        assert rows == [("report_without_plan", "EXP-9999", "H-904", "REP-9004")]
    finally:
        connection.close()


def test_current_integrity_views_empty_under_pre_execution_refinement(conn):
    view_names = [
        row[0]
        for row in conn.execute(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'main'
              AND table_type = 'VIEW'
              AND table_name LIKE 'v_integrity\\_%' ESCAPE '\\'
            ORDER BY table_name
            """
        ).fetchall()
    ]

    assert view_names
    for view_name in view_names:
        assert conn.execute(f'SELECT * FROM "{view_name}"').fetchall() == []


def test_integrity_candidate_refs_empty_under_healthy_state(conn):
    rows = conn.execute("SELECT * FROM v_integrity_candidate_refs").fetchall()

    assert rows == []


def test_strategy_spec_relation_first_instance_repo_state(conn):
    rows = conn.execute("SELECT strategy_spec_id FROM strategy_specs ORDER BY strategy_spec_id").fetchall()

    assert rows == [("STRAT-SPEC-0001",), ("STRAT-SPEC-0002",)]


def test_strategy_spec_views_expose_first_instance_repo_state(conn):
    overview = conn.execute(
        """
        SELECT strategy_spec_id, instrument_family, market_type, primary_timeframe,
               direction, free_parameter_count, max_free_parameters, hash_status,
               intended_for_variant_manifest, approval_scope
        FROM v_strategy_spec_overview
        ORDER BY strategy_spec_id
        """
    ).fetchall()
    parameters = conn.execute(
        """
        SELECT strategy_spec_id, parameter_name, parameter_type, role, range_min,
               range_max, range_step, included_in_variant_generation
        FROM v_strategy_spec_parameters
        ORDER BY strategy_spec_id, parameter_name
        """
    ).fetchall()
    condition_groups = conn.execute(
        """
        SELECT strategy_spec_id, section, group_id, condition_count, subgroup_count,
               declared_depth
        FROM v_strategy_spec_condition_groups
        ORDER BY strategy_spec_id, section, group_id
        """
    ).fetchall()
    assumptions = conn.execute(
        """
        SELECT strategy_spec_id, fee_side_assumption, exchange_constraints_disclosed,
               funding_notional_mode, slippage_model, fill_mode
        FROM v_strategy_spec_backtest_assumptions
        ORDER BY strategy_spec_id
        """
    ).fetchall()

    assert overview == [
        (
            "STRAT-SPEC-0001",
            "crypto_perp",
            "perpetual",
            "15m",
            "long",
            1,
            5,
            "computed",
            True,
            "variant_planning_only",
        ),
        (
            "STRAT-SPEC-0002",
            "crypto_perp",
            "perpetual",
            "15m",
            "both",
            2,
            5,
            "computed",
            True,
            "variant_planning_only",
        )
    ]
    assert parameters == [
        (
            "STRAT-SPEC-0001",
            "entry_distance_threshold",
            "number",
            "entry",
            0.005,
            0.05,
            0.005,
            True,
        ),
        (
            "STRAT-SPEC-0002",
            "band_threshold",
            "number",
            "entry",
            0.0025,
            0.02,
            0.0025,
            True,
        ),
        (
            "STRAT-SPEC-0002",
            "sma_lookback_bars",
            "integer",
            "entry",
            20.0,
            50.0,
            30.0,
            True,
        )
    ]
    assert condition_groups == [
        ("STRAT-SPEC-0001", "entry_logic", "ENTRY-GROUP-0001", 1, 0, 1),
        ("STRAT-SPEC-0001", "exit_logic", "EXIT-GROUP-0001", 1, 0, 1),
        ("STRAT-SPEC-0001", "filters", "FILTER-TYPING-NO-OP-0001", 0, 0, 1),
        ("STRAT-SPEC-0002", "entry_logic", "ENTRY-GROUP-LONG-0001", 1, 0, 1),
        ("STRAT-SPEC-0002", "entry_logic", "ENTRY-GROUP-SHORT-0001", 1, 0, 1),
        ("STRAT-SPEC-0002", "exit_logic", "EXIT-GROUP-LONG-0001", 1, 0, 1),
        ("STRAT-SPEC-0002", "exit_logic", "EXIT-GROUP-SHORT-0001", 1, 0, 1),
        ("STRAT-SPEC-0002", "filters", "FILTER-TYPING-NO-OP-0002", 0, 0, 1),
    ]
    assert assumptions == [
        (
            "STRAT-SPEC-0001",
            "taker_entry_taker_exit",
            True,
            "entry_price",
            "fixed_bps",
            "complete",
        ),
        (
            "STRAT-SPEC-0002",
            "taker_entry_taker_exit",
            True,
            "entry_price",
            "fixed_bps",
            "complete",
        )
    ]


def test_strategy_spec_integrity_views_empty_under_current_zero_instance_state(conn):
    for view_name in [
        "v_integrity_strategy_spec_non_authority",
        "v_integrity_strategy_spec_bounds",
        "v_integrity_strategy_spec_hash_readiness",
    ]:
        assert conn.execute(f'SELECT * FROM "{view_name}"').fetchall() == []


def test_temp_strategy_spec_appears_in_read_only_views(monkeypatch, tmp_path):
    candidate = _valid_candidate_row()
    plan = _valid_plan()
    report = _valid_report()
    strategy_spec = _valid_strategy_spec()

    connection = _init_temp_query_layer(
        monkeypatch,
        tmp_path,
        [candidate],
        [plan],
        [report],
        strategy_specs=[strategy_spec],
    )
    try:
        overview = connection.execute(
            """
            SELECT strategy_spec_id, instrument_family, market_type, primary_timeframe,
                   direction, free_parameter_count, max_free_parameters, hash_status,
                   intended_for_variant_manifest, approval_scope
            FROM v_strategy_spec_overview
            """
        ).fetchall()
        parameters = connection.execute(
            """
            SELECT strategy_spec_id, parameter_name, parameter_type, role, range_min,
                   range_max, range_step, included_in_variant_generation
            FROM v_strategy_spec_parameters
            """
        ).fetchall()
        condition_groups = connection.execute(
            """
            SELECT strategy_spec_id, section, group_id, condition_count, subgroup_count,
                   declared_depth
            FROM v_strategy_spec_condition_groups
            ORDER BY section, group_id
            """
        ).fetchall()
        assumptions = connection.execute(
            """
            SELECT strategy_spec_id, fee_side_assumption, exchange_constraints_disclosed,
                   order_size_assumption, liquidity_capacity_assumption
            FROM v_strategy_spec_backtest_assumptions
            """
        ).fetchall()

        assert overview == [
            (
                "STRAT-SPEC-9001",
                "crypto_perp",
                "perpetual",
                "1h",
                "long",
                1,
                5,
                "not_computed",
                False,
                "none",
            )
        ]
        assert parameters == [
            ("STRAT-SPEC-9001", "lookback", "integer", "entry", 5.0, 50.0, 5.0, True)
        ]
        assert condition_groups == [
            ("STRAT-SPEC-9001", "entry_logic", "GROUP-1", 1, 0, 1),
            ("STRAT-SPEC-9001", "exit_logic", "EXIT-GROUP-1", 1, 0, 1),
            ("STRAT-SPEC-9001", "filters", "FILTER-GROUP-1", 1, 0, 1),
        ]
        assert assumptions == [
            (
                "STRAT-SPEC-9001",
                "maker_taker_visible",
                True,
                "fixture size only",
                "fixture capacity only",
            )
        ]
    finally:
        connection.close()


def test_strategy_spec_non_authority_integrity_flags_visible_violation(monkeypatch, tmp_path):
    strategy_spec = _valid_strategy_spec()
    strategy_spec["non_execution_declaration"]["not_runtime_authority"] = False
    strategy_spec["review"]["non_authority_acknowledgement"]["not_recommendation_authority"] = False

    connection = _init_temp_query_layer(
        monkeypatch,
        tmp_path,
        [_valid_candidate_row()],
        [_valid_plan()],
        [_valid_report()],
        strategy_specs=[strategy_spec],
    )
    try:
        rows = connection.execute(
            """
            SELECT strategy_spec_id, source_field, expected_value, actual_value
            FROM v_integrity_strategy_spec_non_authority
            ORDER BY source_field
            """
        ).fetchall()

        assert rows == [
            (
                "STRAT-SPEC-9001",
                "non_execution_declaration.not_runtime_authority",
                "true",
                "false",
            ),
            (
                "STRAT-SPEC-9001",
                "review.non_authority_acknowledgement.not_recommendation_authority",
                "true",
                "false",
            ),
        ]
    finally:
        connection.close()


def test_strategy_spec_bounds_integrity_flags_visible_violation(monkeypatch, tmp_path):
    strategy_spec = _valid_strategy_spec()
    strategy_spec["max_condition_group_depth"] = 4
    strategy_spec["free_parameters"]["max_free_parameters"] = 6
    strategy_spec["free_parameters"]["parameters"] = [
        _strategy_parameter(f"p{i}") for i in range(6)
    ]

    connection = _init_temp_query_layer(
        monkeypatch,
        tmp_path,
        [_valid_candidate_row()],
        [_valid_plan()],
        [_valid_report()],
        strategy_specs=[strategy_spec],
    )
    try:
        rows = connection.execute(
            """
            SELECT strategy_spec_id, source_field, expected_value, actual_value
            FROM v_integrity_strategy_spec_bounds
            ORDER BY source_field
            """
        ).fetchall()

        assert rows == [
            ("STRAT-SPEC-9001", "free_parameters.max_free_parameters", "5", "6"),
            ("STRAT-SPEC-9001", "free_parameters.parameters.count", "<=5", "6"),
            ("STRAT-SPEC-9001", "max_condition_group_depth", "3", "4"),
        ]
    finally:
        connection.close()


def test_strategy_spec_hash_readiness_integrity_flags_visible_violation(monkeypatch, tmp_path):
    missing_hash = _valid_strategy_spec("STRAT-SPEC-9001")
    missing_hash["hash_pinning"]["hash_status"] = "computed"
    missing_hash["hash_pinning"]["canonical_spec_hash"] = None

    prereg_without_hash = _valid_strategy_spec("STRAT-SPEC-9002")
    prereg_without_hash["pre_registration_support"]["intended_for_variant_manifest"] = True
    prereg_without_hash["hash_pinning"]["hash_status"] = "not_computed"

    connection = _init_temp_query_layer(
        monkeypatch,
        tmp_path,
        [_valid_candidate_row()],
        [_valid_plan()],
        [_valid_report()],
        strategy_specs=[missing_hash, prereg_without_hash],
    )
    try:
        rows = connection.execute(
            """
            SELECT strategy_spec_id, source_field, expected_value, actual_value
            FROM v_integrity_strategy_spec_hash_readiness
            ORDER BY strategy_spec_id, source_field
            """
        ).fetchall()

        assert rows == [
            (
                "STRAT-SPEC-9001",
                "hash_pinning.canonical_spec_hash",
                "non-empty when hash_status=computed",
                None,
            ),
            (
                "STRAT-SPEC-9002",
                "hash_pinning.hash_status",
                "computed when intended_for_variant_manifest=true",
                "not_computed",
            ),
        ]
    finally:
        connection.close()


def test_querying_strategy_spec_views_does_not_modify_research_files(conn):
    strategy_spec_files = sorted(STRATEGY_SPECS_DIR.glob("*.json")) if STRATEGY_SPECS_DIR.exists() else []
    research_files = [
        REGISTRY_PATH,
        TRIAL_LOG_PATH,
        *sorted(EXPERIMENTS_DIR.glob("*.json")),
        *strategy_spec_files,
    ]
    before = _file_checksums(research_files)

    for view_name in [
        "v_strategy_spec_overview",
        "v_strategy_spec_parameters",
        "v_strategy_spec_condition_groups",
        "v_strategy_spec_backtest_assumptions",
        "v_integrity_strategy_spec_non_authority",
        "v_integrity_strategy_spec_bounds",
        "v_integrity_strategy_spec_hash_readiness",
    ]:
        run_named_view(conn, view_name)

    after = _file_checksums(research_files)

    assert after == before


def test_variant_sweep_relations_first_instance_repo_state(conn):
    assert conn.execute(
        "SELECT variant_manifest_id FROM variant_manifests ORDER BY variant_manifest_id"
    ).fetchall() == [("VM-0001",), ("VM-0002",)]
    assert conn.execute("SELECT sweep_plan_id FROM sweep_plans ORDER BY sweep_plan_id").fetchall() == [
        ("SWEEP-PLAN-0001",),
        ("SWEEP-PLAN-0002",),
    ]


def test_variant_sweep_views_expose_first_instance_repo_state(conn):
    manifest_overview = conn.execute(
        """
        SELECT variant_manifest_id, parent_strategy_spec_id, committed_population_count,
               declared_variant_count, population_cap, search_family_id,
               pre_registration_status, hash_status, approval_scope
        FROM v_variant_manifest_overview
        ORDER BY variant_manifest_id
        """
    ).fetchall()
    manifest_population = conn.execute(
        """
        SELECT variant_manifest_id, included_variant_count, planned_trial_count,
               trial_budget_denominator, denominator_count, denominator_basis,
               denominator_type, adaptive_search_used, winner_only_review_forbidden,
               executed_only_denominator_forbidden
        FROM v_variant_manifest_population
        ORDER BY variant_manifest_id
        """
    ).fetchall()
    manifest_axes = conn.execute(
        """
        SELECT variant_manifest_id, axis_id, parameter_name, parameter_type,
               units, generator_method, counts_toward_parent_free_parameter_cap
        FROM v_variant_manifest_parameter_axes
        ORDER BY variant_manifest_id, axis_id
        """
    ).fetchall()
    manifest_assignments = conn.execute(
        """
        SELECT variant_manifest_id, variant_id, assignment_status, axis_ref_count,
               exclusion_rule_count, invalid_combination_rule_count, generated_by_rule,
               generation_order
        FROM v_variant_manifest_assignments
        ORDER BY variant_manifest_id, variant_id
        """
    ).fetchall()
    sweep_overview = conn.execute(
        """
        SELECT sweep_plan_id, parent_variant_manifest_id,
               manifest_committed_population_count, manifest_population_cap,
               manifest_pre_registration_status, selection_mode,
               selected_variant_count, excluded_variant_count, approval_scope
        FROM v_sweep_plan_overview
        ORDER BY sweep_plan_id
        """
    ).fetchall()
    sweep_accounting = conn.execute(
        """
        SELECT sweep_plan_id, committed_population_count, selected_variant_count,
               executed_variant_count, not_attempted_variant_count,
               multiple_testing_denominator, denominator_basis,
               denominator_equals_committed_population_count,
               executed_only_denominator_forbidden, successful_only_denominator_forbidden
        FROM v_sweep_plan_trial_accounting
        ORDER BY sweep_plan_id
        """
    ).fetchall()
    result_capture = conn.execute(
        """
        SELECT sweep_plan_id, result_population_expected, expected_result_population_ref,
               winner_only_retention_forbidden, canonical_evidence_mapping_deferred
        FROM v_sweep_plan_result_capture_expectations
        ORDER BY sweep_plan_id
        """
    ).fetchall()

    assert manifest_overview == [
        (
            "VM-0001",
            "STRAT-SPEC-0001",
            7,
            7,
            7,
            "SF-SMA-DISTANCE-15M-0001",
            "frozen_for_sweep_planning",
            "computed",
            "sweep_planning_only",
        ),
        (
            "VM-0002",
            "STRAT-SPEC-0002",
            10,
            10,
            10,
            "SF-BOTHDIR-SMA-BAND-15M-0001",
            "frozen_for_sweep_planning",
            "computed",
            "sweep_planning_only",
        )
    ]
    assert manifest_population == [
        (
            "VM-0001",
            7,
            7,
            7,
            7,
            "committed_pre_registered_population_count",
            "committed_pre_registered_population",
            False,
            True,
            True,
        ),
        (
            "VM-0002",
            10,
            10,
            10,
            10,
            "committed_pre_registered_population_count",
            "committed_pre_registered_population",
            False,
            True,
            True,
        )
    ]
    assert manifest_axes == [
        (
            "VM-0001",
            "AXIS-001",
            "entry_distance_threshold",
            "number",
            "ratio",
            "manual_grid",
            True,
        ),
        (
            "VM-0002",
            "AXIS-001",
            "sma_lookback_bars",
            "integer",
            "bars",
            "manual_grid",
            True,
        ),
        (
            "VM-0002",
            "AXIS-002",
            "band_threshold",
            "number",
            "ratio",
            "manual_grid",
            True,
        )
    ]
    assert manifest_assignments == [
        ("VM-0001", "VAR-000001", "included", 1, 0, 0, "manual-grid", 1),
        ("VM-0001", "VAR-000002", "included", 1, 0, 0, "manual-grid", 2),
        ("VM-0001", "VAR-000003", "included", 1, 0, 0, "manual-grid", 3),
        ("VM-0001", "VAR-000004", "included", 1, 0, 0, "manual-grid", 4),
        ("VM-0001", "VAR-000005", "included", 1, 0, 0, "manual-grid", 5),
        ("VM-0001", "VAR-000006", "included", 1, 0, 0, "manual-grid", 6),
        ("VM-0001", "VAR-000007", "included", 1, 0, 0, "manual-grid", 7),
        ("VM-0002", "VAR-000001", "included", 2, 0, 0, "manual-grid", 1),
        ("VM-0002", "VAR-000002", "included", 2, 0, 0, "manual-grid", 2),
        ("VM-0002", "VAR-000003", "included", 2, 0, 0, "manual-grid", 3),
        ("VM-0002", "VAR-000004", "included", 2, 0, 0, "manual-grid", 4),
        ("VM-0002", "VAR-000005", "included", 2, 0, 0, "manual-grid", 5),
        ("VM-0002", "VAR-000006", "included", 2, 0, 0, "manual-grid", 6),
        ("VM-0002", "VAR-000007", "included", 2, 0, 0, "manual-grid", 7),
        ("VM-0002", "VAR-000008", "included", 2, 0, 0, "manual-grid", 8),
        ("VM-0002", "VAR-000009", "included", 2, 0, 0, "manual-grid", 9),
        ("VM-0002", "VAR-000010", "included", 2, 0, 0, "manual-grid", 10),
    ]
    assert sweep_overview == [
        (
            "SWEEP-PLAN-0001",
            "VM-0001",
            7,
            7,
            "frozen_for_sweep_planning",
            "all_manifest_variants",
            7,
            0,
            "offline_run_planning_only",
        ),
        (
            "SWEEP-PLAN-0002",
            "VM-0002",
            10,
            10,
            "frozen_for_sweep_planning",
            "all_manifest_variants",
            10,
            0,
            "offline_run_planning_only",
        )
    ]
    assert sweep_accounting == [
        (
            "SWEEP-PLAN-0001",
            7,
            7,
            0,
            7,
            7,
            "committed_pre_registered_population_count",
            True,
            True,
            True,
        ),
        (
            "SWEEP-PLAN-0002",
            10,
            10,
            0,
            10,
            10,
            "committed_pre_registered_population_count",
            True,
            True,
            True,
        )
    ]
    assert result_capture == [
        ("SWEEP-PLAN-0001", True, None, True, True),
        ("SWEEP-PLAN-0002", True, None, True, True),
    ]


def test_first_canonical_15m_result_population_views_under_first_parent_instances(conn):
    assert conn.execute("SELECT COUNT(*) FROM result_populations").fetchone()[0] == 3

    overview = conn.execute(
        """
        SELECT result_population_id, parent_strategy_spec_id,
               parent_variant_manifest_id, parent_sweep_plan_id,
               committed_denominator, result_row_count, outcome_counts_sum,
               execution_mode, offline_only
        FROM v_result_population_overview
        ORDER BY result_population_id
        """
    ).fetchall()
    lineage = conn.execute(
        """
        SELECT result_population_id, parent_strategy_spec_id,
               parent_variant_manifest_id, parent_sweep_plan_id,
               complete_population_lineage_preserved
        FROM v_result_population_parent_lineage
        ORDER BY result_population_id
        """
    ).fetchall()
    denominator = conn.execute(
        """
        SELECT result_population_id, committed_denominator, result_row_count,
               outcome_counts_sum, executed_only_denominator_forbidden,
               successful_only_denominator_forbidden, winner_only_retention_forbidden
        FROM v_result_population_denominator
        ORDER BY result_population_id
        """
    ).fetchall()
    counts = conn.execute(
        """
        SELECT result_population_id, successful, failed, invalid, excluded,
               errored, aborted, filtered, data_unavailable, not_attempted,
               counts_sum, counts_sum_equals_committed_denominator
        FROM v_result_population_outcome_counts
        ORDER BY result_population_id
        """
    ).fetchall()
    rows = conn.execute(
        """
        SELECT result_population_id, variant_id, outcome_category, attempted,
               data_slice_identity, parent_sweep_plan_id, parent_manifest_id
        FROM v_result_population_variant_rows
        ORDER BY result_population_id, variant_id
        """
    ).fetchall()
    coverage = conn.execute(
        """
        SELECT result_population_id, data_catalog_ref, data_slice_identity,
               timeframe, data_stream, missing_data_policy
        FROM v_result_population_data_coverage
        ORDER BY result_population_id
        """
    ).fetchall()
    execution_context = conn.execute(
        """
        SELECT result_population_id, runner_code_ref, determinism_seed,
               execution_mode, offline_only, no_runtime_contact,
               no_paper_live_contact, no_broker_exchange_order_contact,
               no_protected_path_contact
        FROM v_result_population_execution_context
        ORDER BY result_population_id
        """
    ).fetchall()
    non_authority = conn.execute(
        """
        SELECT result_population_id, not_runtime_authority, not_paper_live_authority,
               canonical_evidence_relationship, review_not_approval
        FROM v_result_population_non_authority
        ORDER BY result_population_id
        """
    ).fetchall()

    assert overview == [
        (
            "RP-2134",
            "STRAT-SPEC-0001",
            "VM-0001",
            "SWEEP-PLAN-0001",
            7,
            7,
            7,
            "offline_research",
            True,
        ),
        (
            "RP-4492",
            "STRAT-SPEC-0001",
            "VM-0001",
            "SWEEP-PLAN-0001",
            7,
            7,
            7,
            "offline_research",
            True,
        ),
        (
            "RP-6688",
            "STRAT-SPEC-0002",
            "VM-0002",
            "SWEEP-PLAN-0002",
            10,
            10,
            10,
            "offline_research",
            True,
        ),
    ]
    assert lineage == [
        ("RP-2134", "STRAT-SPEC-0001", "VM-0001", "SWEEP-PLAN-0001", True),
        ("RP-4492", "STRAT-SPEC-0001", "VM-0001", "SWEEP-PLAN-0001", True),
        ("RP-6688", "STRAT-SPEC-0002", "VM-0002", "SWEEP-PLAN-0002", True),
    ]
    assert denominator == [
        ("RP-2134", 7, 7, 7, True, True, True),
        ("RP-4492", 7, 7, 7, True, True, True),
        ("RP-6688", 10, 10, 10, True, True, True),
    ]
    assert counts == [
        ("RP-2134", 7, 0, 0, 0, 0, 0, 0, 0, 0, 7, True),
        ("RP-4492", 7, 0, 0, 0, 0, 0, 0, 0, 0, 7, True),
        ("RP-6688", 10, 0, 0, 0, 0, 0, 0, 0, 0, 10, True),
    ]
    assert rows == [
        (
            "RP-2134",
            f"VAR-{index:06d}",
            "successful",
            True,
            "csv_fixture:sha256:90c38fd1fe4f2e86ee0a2ad1a4efaca4af7fde0f8f5bc75d8b1cfe54c16dabd0",
            "SWEEP-PLAN-0001",
            "VM-0001",
        )
        for index in range(1, 8)
    ] + [
        (
            "RP-4492",
            f"VAR-{index:06d}",
            "successful",
            True,
            "binance_usdtm_btcusdt_ohlcv_15m:sha256:3daace53d727599b4cf5cc9d27ac2a3d53997bbf5b8401470097934e776bd664",
            "SWEEP-PLAN-0001",
            "VM-0001",
        )
        for index in range(1, 8)
    ] + [
        (
            "RP-6688",
            f"VAR-{index:06d}",
            "successful",
            True,
            "binance_usdtm_btcusdt_ohlcv_15m:sha256:3daace53d727599b4cf5cc9d27ac2a3d53997bbf5b8401470097934e776bd664",
            "SWEEP-PLAN-0002",
            "VM-0002",
        )
        for index in range(1, 11)
    ]
    assert coverage == [
        (
            "RP-2134",
            "15m_ohlcv_test_fixture_offline_only",
            "csv_fixture:sha256:90c38fd1fe4f2e86ee0a2ad1a4efaca4af7fde0f8f5bc75d8b1cfe54c16dabd0",
            "15m",
            "ohlcv",
            "block_if_missing",
        ),
        (
            "RP-4492",
            "binance_usdtm_btcusdt_ohlcv_15m.offline_local.15m.20200101T000000Z.20260411T234500Z.sha256_3daace53d727599b",
            "binance_usdtm_btcusdt_ohlcv_15m:sha256:3daace53d727599b4cf5cc9d27ac2a3d53997bbf5b8401470097934e776bd664",
            "15m",
            "ohlcv",
            "block_if_missing",
        ),
        (
            "RP-6688",
            "binance_usdtm_btcusdt_ohlcv_15m.offline_local.15m.20200101T000000Z.20260411T234500Z.sha256_3daace53d727599b",
            "binance_usdtm_btcusdt_ohlcv_15m:sha256:3daace53d727599b4cf5cc9d27ac2a3d53997bbf5b8401470097934e776bd664",
            "15m",
            "ohlcv",
            "block_if_missing",
        ),
    ]
    assert execution_context == [
        (
            "RP-2134",
            "tools.research_runner.run_offline_sweep",
            7,
            "offline_research",
            True,
            True,
            True,
            True,
            True,
        ),
        (
            "RP-4492",
            "tools.research_runner.run_offline_sweep",
            190,
            "offline_research",
            True,
            True,
            True,
            True,
            True,
        ),
        (
            "RP-6688",
            "tools.research_runner.run_offline_sweep",
            190,
            "offline_research",
            True,
            True,
            True,
            True,
            True,
        ),
    ]
    assert non_authority == [
        ("RP-2134", True, True, "reference_only", True),
        ("RP-4492", True, True, "reference_only", True),
        ("RP-6688", True, True, "reference_only", True),
    ]


def test_variant_sweep_integrity_views_empty_under_current_zero_instance_state(conn):
    for view_name in [
        "v_integrity_variant_manifest_non_authority",
        "v_integrity_variant_manifest_denominator",
        "v_integrity_variant_manifest_hash_readiness",
        "v_integrity_variant_manifest_supersession",
        "v_integrity_sweep_plan_non_authority",
        "v_integrity_sweep_plan_denominator",
        "v_integrity_sweep_plan_parent_manifest",
        "v_integrity_sweep_plan_no_computation",
    ]:
        assert conn.execute(f'SELECT * FROM "{view_name}"').fetchall() == []


def test_temp_variant_manifest_appears_in_read_only_views(monkeypatch, tmp_path):
    manifest = _valid_variant_manifest()

    connection = _init_temp_query_layer(
        monkeypatch,
        tmp_path,
        [_valid_candidate_row()],
        [_valid_plan()],
        [_valid_report()],
        variant_manifests=[manifest],
    )
    try:
        overview = connection.execute(
            """
            SELECT variant_manifest_id, parent_strategy_spec_id, committed_population_count,
                   declared_variant_count, population_cap, search_family_id,
                   pre_registration_status, hash_status, approval_scope
            FROM v_variant_manifest_overview
            """
        ).fetchall()
        population = connection.execute(
            """
            SELECT variant_manifest_id, included_variant_count, planned_trial_count,
                   trial_budget_denominator, denominator_count, denominator_basis,
                   denominator_type, adaptive_search_used, winner_only_review_forbidden,
                   executed_only_denominator_forbidden
            FROM v_variant_manifest_population
            """
        ).fetchall()
        axes = connection.execute(
            """
            SELECT variant_manifest_id, axis_id, parameter_name, parameter_type,
                   units, generator_method, counts_toward_parent_free_parameter_cap
            FROM v_variant_manifest_parameter_axes
            """
        ).fetchall()
        assignments = connection.execute(
            """
            SELECT variant_manifest_id, variant_id, assignment_status, axis_ref_count,
                   exclusion_rule_count, invalid_combination_rule_count, generated_by_rule,
                   generation_order
            FROM v_variant_manifest_assignments
            ORDER BY variant_id
            """
        ).fetchall()
        hash_pinning = connection.execute(
            """
            SELECT variant_manifest_id, hash_algorithm, canonicalization,
                   hash_scope_version, hash_scope_count, hash_status,
                   pre_sweep_freeze_required, post_result_mutation_forbidden
            FROM v_variant_manifest_hash_pinning
            """
        ).fetchall()
        supersession = connection.execute(
            """
            SELECT variant_manifest_id, amendment_mode, associated_results_state,
                   supersession_allowed, post_result_change, close_only_after_results,
                   preserve_prior_manifest_required, fresh_denominator_required,
                   does_not_inherit_prior_results, supersession_lineage_count
            FROM v_variant_manifest_supersession
            """
        ).fetchall()

        assert overview == [
            (
                "VM-9001",
                "STRAT-SPEC-9001",
                2,
                2,
                2,
                "SF-9001",
                "frozen_for_sweep_planning",
                "computed",
                "sweep_planning_only",
            )
        ]
        assert population == [
            (
                "VM-9001",
                2,
                2,
                2,
                2,
                "committed_pre_registered_population_count",
                "committed_pre_registered_population",
                False,
                True,
                True,
            )
        ]
        assert axes == [
            ("VM-9001", "AXIS-001", "lookback", "integer", "bars", "manual_grid", True)
        ]
        assert assignments == [
            ("VM-9001", "VAR-900001", "included", 1, 0, 0, "manual-grid", 1),
            ("VM-9001", "VAR-900002", "included", 1, 0, 0, "manual-grid", 2),
        ]
        assert hash_pinning == [
            (
                "VM-9001",
                "sha256",
                "json_canonical_v1",
                "variant_manifest_hash_scope_v1",
                9,
                "computed",
                True,
                True,
            )
        ]
        assert supersession == [
            ("VM-9001", "none", "no_associated_results", False, False, True, True, True, True, 0)
        ]
    finally:
        connection.close()


def test_temp_sweep_plan_appears_in_read_only_views(monkeypatch, tmp_path):
    manifest = _valid_variant_manifest()
    sweep_plan = _valid_sweep_plan(manifest)

    connection = _init_temp_query_layer(
        monkeypatch,
        tmp_path,
        [_valid_candidate_row()],
        [_valid_plan()],
        [_valid_report()],
        variant_manifests=[manifest],
        sweep_plans=[sweep_plan],
    )
    try:
        overview = connection.execute(
            """
            SELECT sweep_plan_id, parent_variant_manifest_id,
                   manifest_committed_population_count, manifest_population_cap,
                   manifest_pre_registration_status, selection_mode,
                   selected_variant_count, excluded_variant_count, approval_scope
            FROM v_sweep_plan_overview
            """
        ).fetchall()
        methods = connection.execute(
            """
            SELECT sweep_plan_id, backtest_enabled, walk_forward_oos_enabled,
                   declares_chronological_separation, robustness_enabled,
                   robustness_family_count, dsr_psr_mintrl_enabled,
                   dsr_denominator_ref, dsr_computation_deferred,
                   monte_carlo_enabled, monte_carlo_computation_deferred,
                   declarative_intent_only, no_runner_hooks, no_formulas, no_computation
            FROM v_sweep_plan_validation_methods
            """
        ).fetchall()
        accounting = connection.execute(
            """
            SELECT sweep_plan_id, committed_population_count, selected_variant_count,
                   executed_variant_count, successful_variant_count, failed_variant_count,
                   errored_variant_count, aborted_variant_count, filtered_variant_count,
                   data_unavailable_variant_count, excluded_variant_count,
                   not_attempted_variant_count, multiple_testing_denominator,
                   denominator_basis, denominator_equals_committed_population_count,
                   executed_only_denominator_forbidden, successful_only_denominator_forbidden
            FROM v_sweep_plan_trial_accounting
            """
        ).fetchall()
        capture = connection.execute(
            """
            SELECT sweep_plan_id, result_population_expected,
                   expected_result_population_ref, must_capture_successful,
                   must_capture_failed, must_capture_invalid, must_capture_excluded,
                   must_capture_errored, must_capture_aborted, must_capture_filtered,
                   must_capture_data_unavailable, must_capture_not_attempted,
                   winner_only_retention_forbidden, canonical_evidence_mapping_deferred
            FROM v_sweep_plan_result_capture_expectations
            """
        ).fetchall()

        assert overview == [
            (
                "SWEEP-PLAN-9001",
                "VM-9001",
                2,
                2,
                "frozen_for_sweep_planning",
                "all_manifest_variants",
                2,
                0,
                "offline_run_planning_only",
            )
        ]
        assert methods == [
            (
                "SWEEP-PLAN-9001",
                True,
                True,
                True,
                False,
                0,
                True,
                "committed_population_count",
                True,
                False,
                True,
                True,
                True,
                True,
                True,
            )
        ]
        assert accounting == [
            (
                "SWEEP-PLAN-9001",
                2,
                2,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                2,
                2,
                "committed_pre_registered_population_count",
                True,
                True,
                True,
            )
        ]
        assert capture == [
            (
                "SWEEP-PLAN-9001",
                True,
                None,
                True,
                True,
                True,
                True,
                True,
                True,
                True,
                True,
                True,
                True,
                True,
            )
        ]
    finally:
        connection.close()


def test_variant_manifest_denominator_integrity_flags_violation(monkeypatch, tmp_path):
    manifest = _valid_variant_manifest()
    manifest["population_governance"]["trial_budget"]["denominator_count"] = 1

    connection = _init_temp_query_layer(
        monkeypatch,
        tmp_path,
        [_valid_candidate_row()],
        [_valid_plan()],
        [_valid_report()],
        variant_manifests=[manifest],
    )
    try:
        rows = connection.execute(
            """
            SELECT variant_manifest_id, source_field, expected_value, actual_value
            FROM v_integrity_variant_manifest_denominator
            WHERE source_field = 'trial_budget.denominator_count'
            """
        ).fetchall()

        assert rows == [("VM-9001", "trial_budget.denominator_count", "2", "1")]
    finally:
        connection.close()


def test_variant_manifest_supersession_integrity_flags_violation(monkeypatch, tmp_path):
    manifest = _valid_variant_manifest()
    manifest["amendment_and_supersession"]["associated_results_state"] = (
        "associated_results_exist"
    )
    manifest["amendment_and_supersession"]["amendment_mode"] = "supersedes_prior_manifest"
    manifest["amendment_and_supersession"]["supersession_allowed"] = True
    manifest["amendment_and_supersession"]["supersedes"] = {
        "variant_manifest_id": "VM-9002",
        "manifest_hash": "sha256:" + "5" * 64,
        "reason": "fixture",
        "superseded_at": "2026-06-01T00:00:00Z",
    }

    connection = _init_temp_query_layer(
        monkeypatch,
        tmp_path,
        [_valid_candidate_row()],
        [_valid_plan()],
        [_valid_report()],
        variant_manifests=[manifest],
    )
    try:
        source_fields = {
            row[0]
            for row in connection.execute(
                """
                SELECT source_field
                FROM v_integrity_variant_manifest_supersession
                """
            ).fetchall()
        }

        assert "amendment_and_supersession.amendment_mode" in source_fields
        assert "amendment_and_supersession.supersession_allowed" in source_fields
        assert "amendment_and_supersession.supersedes" in source_fields
    finally:
        connection.close()


def test_variant_manifest_hash_readiness_integrity_flags_violation(monkeypatch, tmp_path):
    manifest = _valid_variant_manifest()
    manifest["manifest_hash_pinning"]["hash_status"] = "not_computed"
    manifest["manifest_hash_pinning"]["manifest_hash"] = None
    manifest["manifest_hash_pinning"]["frozen_at"] = None

    connection = _init_temp_query_layer(
        monkeypatch,
        tmp_path,
        [_valid_candidate_row()],
        [_valid_plan()],
        [_valid_report()],
        variant_manifests=[manifest],
    )
    try:
        source_fields = {
            row[0]
            for row in connection.execute(
                """
                SELECT source_field
                FROM v_integrity_variant_manifest_hash_readiness
                """
            ).fetchall()
        }

        assert "manifest_hash_pinning.hash_status" in source_fields
        assert "manifest_hash_pinning.manifest_hash" in source_fields
        assert "manifest_hash_pinning.frozen_at" in source_fields
    finally:
        connection.close()


def test_sweep_plan_denominator_integrity_flags_violation(monkeypatch, tmp_path):
    manifest = _valid_variant_manifest()
    sweep_plan = _valid_sweep_plan(manifest)
    sweep_plan["trial_accounting"]["multiple_testing_denominator"] = 1
    sweep_plan["trial_accounting"]["executed_only_denominator_forbidden"] = False

    connection = _init_temp_query_layer(
        monkeypatch,
        tmp_path,
        [_valid_candidate_row()],
        [_valid_plan()],
        [_valid_report()],
        variant_manifests=[manifest],
        sweep_plans=[sweep_plan],
    )
    try:
        source_fields = {
            row[0]
            for row in connection.execute(
                """
                SELECT source_field
                FROM v_integrity_sweep_plan_denominator
                """
            ).fetchall()
        }

        assert "trial_accounting.multiple_testing_denominator" in source_fields
        assert "trial_accounting.executed_only_denominator_forbidden" in source_fields
    finally:
        connection.close()


def test_sweep_plan_no_computation_integrity_flags_violation(monkeypatch, tmp_path):
    manifest = _valid_variant_manifest()
    sweep_plan = _valid_sweep_plan(manifest)
    sweep_plan["validation_methods"]["no_runner_hooks"] = False
    sweep_plan["validation_methods"]["monte_carlo"]["enabled"] = True
    sweep_plan["validation_methods"]["monte_carlo"]["computation_deferred"] = False

    connection = _init_temp_query_layer(
        monkeypatch,
        tmp_path,
        [_valid_candidate_row()],
        [_valid_plan()],
        [_valid_report()],
        variant_manifests=[manifest],
        sweep_plans=[sweep_plan],
    )
    try:
        source_fields = {
            row[0]
            for row in connection.execute(
                """
                SELECT source_field
                FROM v_integrity_sweep_plan_no_computation
                """
            ).fetchall()
        }

        assert "validation_methods.no_runner_hooks" in source_fields
        assert "validation_methods.monte_carlo.computation_deferred" in source_fields
    finally:
        connection.close()


def test_result_population_relation_empty_without_directory(monkeypatch, tmp_path):
    connection = _init_temp_query_layer(
        monkeypatch,
        tmp_path,
        [_valid_candidate_row()],
        [_valid_plan()],
        [_valid_report()],
    )
    try:
        assert not (tmp_path / "research" / "result_populations").exists()
        assert connection.execute("SELECT * FROM result_populations").fetchall() == []
        for view_name in [
            "v_result_population_overview",
            "v_result_population_parent_lineage",
            "v_result_population_denominator",
            "v_result_population_outcome_counts",
            "v_result_population_variant_rows",
            "v_result_population_error_summary",
            "v_result_population_data_coverage",
            "v_result_population_backtest_assumptions",
            "v_result_population_identity_audit",
            "v_result_population_append_only_ledger",
            "v_result_population_ledger_events",
            "v_result_population_non_authority",
            "v_result_population_execution_context",
            "v_integrity_result_population_denominator_mismatch",
            "v_integrity_result_population_outcome_count_mismatch",
            "v_integrity_result_population_missing_variant_rows",
            "v_integrity_result_population_unknown_outcome_category",
            "v_integrity_result_population_audit_in_identity_scope",
            "v_integrity_result_population_non_authority_violation",
            "v_integrity_result_population_canonical_evidence_violation",
            "v_integrity_result_population_append_only_violation",
            "v_integrity_result_population_offline_boundary_violation",
            "v_integrity_result_population_canonical_write_violation",
            "v_integrity_result_population_authority_key_violation",
            "v_integrity_result_population_parent_hash_chain_mismatch",
        ]:
            assert connection.execute(f'SELECT * FROM "{view_name}"').fetchall() == []
        assert not (tmp_path / "research" / "result_populations").exists()
    finally:
        connection.close()


def test_temp_result_population_appears_in_read_only_views(monkeypatch, tmp_path):
    result_population = _valid_result_population()

    connection = _init_temp_query_layer(
        monkeypatch,
        tmp_path,
        [_valid_candidate_row()],
        [_valid_plan()],
        [_valid_report()],
        result_populations=[result_population],
    )
    try:
        overview = connection.execute(
            """
            SELECT result_population_id, parent_strategy_spec_id,
                   parent_variant_manifest_id, parent_sweep_plan_id,
                   committed_denominator, result_row_count, outcome_counts_sum,
                   execution_mode, offline_only, review_scope
            FROM v_result_population_overview
            """
        ).fetchall()
        rows = connection.execute(
            """
            SELECT variant_id, outcome_category, attempted, parent_sweep_plan_id,
                   parent_manifest_id
            FROM v_result_population_variant_rows
            ORDER BY row_id
            """
        ).fetchall()
        ledger = connection.execute(
            """
            SELECT result_population_id, append_only, creation_event_ref, event_count
            FROM v_result_population_append_only_ledger
            """
        ).fetchall()

        assert overview == [
            (
                "RP-9001",
                "STRAT-SPEC-9001",
                "VM-9001",
                "SWEEP-PLAN-9001",
                2,
                2,
                2,
                "offline_research",
                True,
                "none",
            )
        ]
        assert rows == [
            ("VAR-900001", "successful", True, "SWEEP-PLAN-9001", "VM-9001"),
            ("VAR-900002", "failed", True, "SWEEP-PLAN-9001", "VM-9001"),
        ]
        assert ledger == [("RP-9001", True, "RP-9001-EVENT-001", 1)]
    finally:
        connection.close()


def test_result_population_integrity_views_clean_for_valid_temp_fixture(monkeypatch, tmp_path):
    connection = _init_temp_query_layer(
        monkeypatch,
        tmp_path,
        [_valid_candidate_row()],
        [_valid_plan()],
        [_valid_report()],
        result_populations=[_valid_result_population()],
    )
    try:
        for view_name in [
            "v_integrity_result_population_denominator_mismatch",
            "v_integrity_result_population_outcome_count_mismatch",
            "v_integrity_result_population_missing_variant_rows",
            "v_integrity_result_population_unknown_outcome_category",
            "v_integrity_result_population_audit_in_identity_scope",
            "v_integrity_result_population_non_authority_violation",
            "v_integrity_result_population_canonical_evidence_violation",
            "v_integrity_result_population_append_only_violation",
            "v_integrity_result_population_offline_boundary_violation",
            "v_integrity_result_population_canonical_write_violation",
            "v_integrity_result_population_authority_key_violation",
            "v_integrity_result_population_parent_hash_chain_mismatch",
        ]:
            assert connection.execute(f'SELECT * FROM "{view_name}"').fetchall() == []
    finally:
        connection.close()


def test_result_population_denominator_mismatch_integrity_flags_violation(monkeypatch, tmp_path):
    result_population = _valid_result_population()
    result_population["committed_denominator_snapshot"]["committed_denominator"] = 3

    connection = _init_temp_query_layer(
        monkeypatch,
        tmp_path,
        [_valid_candidate_row()],
        [_valid_plan()],
        [_valid_report()],
        result_populations=[result_population],
    )
    try:
        source_fields = {
            row[0]
            for row in connection.execute(
                """
                SELECT source_field
                FROM v_integrity_result_population_denominator_mismatch
                """
            ).fetchall()
        }

        assert "committed_denominator_snapshot.result_row_count" in source_fields
        assert "committed_denominator_snapshot.outcome_counts_sum" in source_fields
    finally:
        connection.close()


def test_result_population_unknown_outcome_category_integrity_flags_violation(
    monkeypatch, tmp_path
):
    result_population = _valid_result_population()
    result_population["variant_result_rows"][1]["outcome_category"] = "winner"

    connection = _init_temp_query_layer(
        monkeypatch,
        tmp_path,
        [_valid_candidate_row()],
        [_valid_plan()],
        [_valid_report()],
        result_populations=[result_population],
    )
    try:
        rows = connection.execute(
            """
            SELECT row_id, variant_id, outcome_category
            FROM v_integrity_result_population_unknown_outcome_category
            """
        ).fetchall()

        assert rows == [("RP-9001-ROW-000002", "VAR-900002", "winner")]
    finally:
        connection.close()


def test_result_population_audit_identity_scope_integrity_flags_violation(
    monkeypatch, tmp_path
):
    result_population = _valid_result_population()
    result_population["result_population_identity_hash"]["hash_scope"].append("audit_envelope")

    connection = _init_temp_query_layer(
        monkeypatch,
        tmp_path,
        [_valid_candidate_row()],
        [_valid_plan()],
        [_valid_report()],
        result_populations=[result_population],
    )
    try:
        rows = connection.execute(
            """
            SELECT source_field, scope_item
            FROM v_integrity_result_population_audit_in_identity_scope
            """
        ).fetchall()

        assert rows == [("result_population_identity_hash.hash_scope", "audit_envelope")]
    finally:
        connection.close()


def test_result_population_non_authority_integrity_flags_violation(monkeypatch, tmp_path):
    result_population = _valid_result_population()
    result_population["non_authority_declaration"]["not_recommendation_authority"] = False
    result_population["review"]["non_authority_acknowledgement"]["not_approval"] = False

    connection = _init_temp_query_layer(
        monkeypatch,
        tmp_path,
        [_valid_candidate_row()],
        [_valid_plan()],
        [_valid_report()],
        result_populations=[result_population],
    )
    try:
        source_fields = {
            row[0]
            for row in connection.execute(
                """
                SELECT source_field
                FROM v_integrity_result_population_non_authority_violation
                """
            ).fetchall()
        }

        assert "non_authority_declaration.not_recommendation_authority" in source_fields
        assert "review.non_authority_acknowledgement.not_approval" in source_fields
    finally:
        connection.close()


def test_result_population_append_only_integrity_flags_violation(monkeypatch, tmp_path):
    result_population = _valid_result_population()
    result_population["append_only_ledger"]["append_only"] = False
    result_population["append_only_ledger"]["events"][0]["event_type"] = "reviewed"

    connection = _init_temp_query_layer(
        monkeypatch,
        tmp_path,
        [_valid_candidate_row()],
        [_valid_plan()],
        [_valid_report()],
        result_populations=[result_population],
    )
    try:
        source_fields = {
            row[0]
            for row in connection.execute(
                """
                SELECT source_field
                FROM v_integrity_result_population_append_only_violation
                """
            ).fetchall()
        }

        assert "append_only_ledger.append_only" in source_fields
        assert "append_only_ledger.events" in source_fields
    finally:
        connection.close()


def test_result_population_offline_boundary_integrity_flags_violation(monkeypatch, tmp_path):
    result_population = _valid_result_population()
    result_population["execution_context"]["offline_only"] = False
    result_population["execution_context"]["no_runtime_contact"] = False

    connection = _init_temp_query_layer(
        monkeypatch,
        tmp_path,
        [_valid_candidate_row()],
        [_valid_plan()],
        [_valid_report()],
        result_populations=[result_population],
    )
    try:
        source_fields = {
            row[0]
            for row in connection.execute(
                """
                SELECT source_field
                FROM v_integrity_result_population_offline_boundary_violation
                """
            ).fetchall()
        }

        assert "execution_context.offline_only" in source_fields
        assert "execution_context.no_runtime_contact" in source_fields
    finally:
        connection.close()


def test_result_population_canonical_write_integrity_flags_violation(monkeypatch, tmp_path):
    result_population = _valid_result_population()
    result_population["audit_envelope"]["operator_notes"] = [
        "output_dir=research/result_populations"
    ]

    connection = _init_temp_query_layer(
        monkeypatch,
        tmp_path,
        [_valid_candidate_row()],
        [_valid_plan()],
        [_valid_report()],
        result_populations=[result_population],
    )
    try:
        rows = connection.execute(
            """
            SELECT result_population_id
            FROM v_integrity_result_population_canonical_write_violation
            """
        ).fetchall()

        assert rows == [("RP-9001",)]
    finally:
        connection.close()


def test_result_population_authority_key_integrity_flags_violation(monkeypatch, tmp_path):
    result_population = _valid_result_population()
    result_population["audit_envelope"]["operator_notes"] = ["ranking_score=1.0"]

    connection = _init_temp_query_layer(
        monkeypatch,
        tmp_path,
        [_valid_candidate_row()],
        [_valid_plan()],
        [_valid_report()],
        result_populations=[result_population],
    )
    try:
        rows = connection.execute(
            """
            SELECT source_field
            FROM v_integrity_result_population_authority_key_violation
            """
        ).fetchall()

        assert rows == [("ranking_score",)]
    finally:
        connection.close()


def test_result_population_parent_hash_chain_integrity_flags_violation(monkeypatch, tmp_path):
    result_population = _valid_result_population()
    result_population["lineage"]["parent_hash_chain"]["variant_manifest_hash"] = (
        "sha256:" + "0" * 64
    )

    connection = _init_temp_query_layer(
        monkeypatch,
        tmp_path,
        [_valid_candidate_row()],
        [_valid_plan()],
        [_valid_report()],
        result_populations=[result_population],
    )
    try:
        rows = connection.execute(
            """
            SELECT source_field
            FROM v_integrity_result_population_parent_hash_chain_mismatch
            """
        ).fetchall()

        assert rows == [("lineage.parent_hash_chain.variant_manifest_hash",)]
    finally:
        connection.close()


def test_querying_result_population_views_does_not_modify_or_create_repo_corpus(conn):
    result_population_files = (
        sorted(RESULT_POPULATIONS_DIR.glob("*.json")) if RESULT_POPULATIONS_DIR.exists() else []
    )
    research_files = [
        REGISTRY_PATH,
        TRIAL_LOG_PATH,
        *sorted(EXPERIMENTS_DIR.glob("*.json")),
        *result_population_files,
    ]
    before = _file_checksums(research_files)
    corpus_existed_before = RESULT_POPULATIONS_DIR.exists()

    for view_name in [
        "v_result_population_overview",
        "v_result_population_parent_lineage",
        "v_result_population_denominator",
        "v_result_population_outcome_counts",
        "v_result_population_variant_rows",
        "v_result_population_error_summary",
        "v_result_population_data_coverage",
        "v_result_population_backtest_assumptions",
        "v_result_population_identity_audit",
        "v_result_population_append_only_ledger",
        "v_result_population_ledger_events",
        "v_result_population_non_authority",
        "v_result_population_execution_context",
        "v_integrity_result_population_denominator_mismatch",
        "v_integrity_result_population_outcome_count_mismatch",
        "v_integrity_result_population_missing_variant_rows",
        "v_integrity_result_population_unknown_outcome_category",
        "v_integrity_result_population_audit_in_identity_scope",
        "v_integrity_result_population_non_authority_violation",
        "v_integrity_result_population_canonical_evidence_violation",
        "v_integrity_result_population_append_only_violation",
        "v_integrity_result_population_offline_boundary_violation",
        "v_integrity_result_population_canonical_write_violation",
        "v_integrity_result_population_authority_key_violation",
        "v_integrity_result_population_parent_hash_chain_mismatch",
    ]:
        run_named_view(conn, view_name)

    after = _file_checksums(research_files)

    assert after == before
    assert RESULT_POPULATIONS_DIR.exists() is corpus_existed_before


def test_query_layer_does_not_import_or_run_offline_runner():
    source = (query_layer.REPO_ROOT / "tools" / "research_query" / "query_layer.py").read_text(
        encoding="utf-8"
    )

    assert "tools.research_runner" not in source
    assert "run_offline_sweep" not in source


def test_querying_variant_sweep_views_does_not_modify_research_files(conn):
    variant_manifest_files = (
        sorted(VARIANT_MANIFESTS_DIR.glob("*.json")) if VARIANT_MANIFESTS_DIR.exists() else []
    )
    sweep_plan_files = sorted(SWEEP_PLANS_DIR.glob("*.json")) if SWEEP_PLANS_DIR.exists() else []
    research_files = [
        REGISTRY_PATH,
        TRIAL_LOG_PATH,
        *sorted(EXPERIMENTS_DIR.glob("*.json")),
        *variant_manifest_files,
        *sweep_plan_files,
    ]
    before = _file_checksums(research_files)

    for view_name in [
        "v_variant_manifest_overview",
        "v_variant_manifest_population",
        "v_variant_manifest_parameter_axes",
        "v_variant_manifest_assignments",
        "v_variant_manifest_hash_pinning",
        "v_variant_manifest_supersession",
        "v_sweep_plan_overview",
        "v_sweep_plan_validation_methods",
        "v_sweep_plan_trial_accounting",
        "v_sweep_plan_result_capture_expectations",
        "v_integrity_variant_manifest_non_authority",
        "v_integrity_variant_manifest_denominator",
        "v_integrity_variant_manifest_hash_readiness",
        "v_integrity_variant_manifest_supersession",
        "v_integrity_sweep_plan_non_authority",
        "v_integrity_sweep_plan_denominator",
        "v_integrity_sweep_plan_parent_manifest",
        "v_integrity_sweep_plan_no_computation",
    ]:
        run_named_view(conn, view_name)

    after = _file_checksums(research_files)

    assert after == before


def test_report_trial_ids_resolve_to_trial_log(conn):
    missing_trial_count = conn.execute(
        """
        SELECT COUNT(*)
        FROM exp_reports AS reports,
        UNNEST(reports.trial_ids) AS report_trial_ids(trial_id)
        LEFT JOIN trial_log AS trials
          ON report_trial_ids.trial_id = trials.trial_id
        WHERE trials.trial_id IS NULL
        """
    ).fetchone()[0]

    assert missing_trial_count == 0


def test_read_only_guard_rejects_insert(conn):
    with pytest.raises(ReadOnlyQueryError):
        run_sql(conn, "INSERT INTO candidates VALUES (1)")


def test_read_only_guard_rejects_delete(conn):
    with pytest.raises(ReadOnlyQueryError):
        run_sql(conn, "DELETE FROM candidates")


def test_read_only_guard_rejects_create(conn):
    with pytest.raises(ReadOnlyQueryError):
        run_sql(conn, "CREATE TABLE scratch AS SELECT 1 AS x")


def test_read_only_guard_rejects_external_file_reads(conn):
    with pytest.raises(ReadOnlyQueryError):
        run_sql(conn, "SELECT * FROM read_json_auto('research/candidate_registry.jsonl')")


def test_read_only_guard_rejects_pragma(conn):
    with pytest.raises(ReadOnlyQueryError):
        run_sql(conn, "PRAGMA show_tables")


def test_read_only_guard_rejects_call(conn):
    with pytest.raises(ReadOnlyQueryError):
        run_sql(conn, "CALL something()")


def test_read_only_guard_rejects_multi_statement_select_then_drop(conn):
    with pytest.raises(ReadOnlyQueryError):
        run_sql(conn, "SELECT 1 AS x; DROP VIEW candidates")


def test_read_only_guard_rejects_multi_statement_with_trailing_write(conn):
    with pytest.raises(ReadOnlyQueryError):
        run_sql(conn, "WITH t AS (SELECT 1 AS x) SELECT * FROM t; DELETE FROM exp_plans")


def test_read_only_guard_accepts_select(conn):
    rows = run_sql(conn, "SELECT 1 AS x")

    assert rows == [{"x": 1}]


def test_read_only_guard_accepts_with_select(conn):
    rows = run_sql(conn, "WITH t AS (SELECT 1 AS x) SELECT * FROM t")

    assert rows == [{"x": 1}]


def test_no_research_files_modified(conn):
    research_files = [
        REGISTRY_PATH,
        TRIAL_LOG_PATH,
        *sorted(EXPERIMENTS_DIR.glob("*.json")),
    ]
    before = _file_checksums(research_files)

    for view_name in list_views(conn):
        run_named_view(conn, view_name)
    run_sql(conn, "SELECT COUNT(*) AS n FROM candidates")
    run_sql(conn, "SELECT candidate_id FROM v_candidate_overview ORDER BY candidate_id")

    after = _file_checksums(research_files)

    assert after == before
