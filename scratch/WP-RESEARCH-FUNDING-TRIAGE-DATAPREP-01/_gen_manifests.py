"""Generate variant manifests and sweep plans for WP-RESEARCH-FUNDING-TRIAGE-DATAPREP-01."""
import json
import os

FUNDING_LOOKBACKS = [2880, 8640, 17280]
TAIL_PAIRS = [(0.1, 0.9), (0.05, 0.95)]
EXIT_MODES = ["fixed_max_hold_only", "midline_reversion_or_max_hold"]
MAX_HOLDS = [16, 32, 96]

SPECS = [
    ("no_atr", "STRAT-SPEC-9601", "VM-9601", "SWEEP-PLAN-9601"),
    ("atr_20", "STRAT-SPEC-9602", "VM-9602", "SWEEP-PLAN-9602"),
    ("atr_30", "STRAT-SPEC-9603", "VM-9603", "SWEEP-PLAN-9603"),
]

BASE = "scratch/WP-RESEARCH-FUNDING-TRIAGE-DATAPREP-01/inputs"


def make_variant_id(fl, lo, hi, em, hold):
    lo_str = f"{int(lo * 100):02d}"
    hi_str = f"{int(hi * 100):02d}"
    exit_short = "fixed" if em == "fixed_max_hold_only" else "midline"
    return f"fl{fl}_tail{lo_str}_{hi_str}_exit{exit_short}_hold{hold}"


def make_variants():
    variants = []
    gen_order = 0
    for fl in FUNDING_LOOKBACKS:
        for lo, hi in TAIL_PAIRS:
            for em in EXIT_MODES:
                for hold in MAX_HOLDS:
                    gen_order += 1
                    vid = make_variant_id(fl, lo, hi, em, hold)
                    variants.append({
                        "variant_id": vid,
                        "assignment_status": "included",
                        "axis_refs": ["AXIS-001", "AXIS-002", "AXIS-003", "AXIS-004", "AXIS-005"],
                        "exclusion_rule_refs": [],
                        "invalid_combination_rule_refs": [],
                        "lineage": {"generated_by_rule": "frozen-manual-grid", "generation_order": gen_order},
                        "parameter_value_hash": None,
                        "parameter_values": {
                            "funding_lookback_bars": fl,
                            "lower_entry_percentile": lo,
                            "upper_entry_percentile": hi,
                            "exit_mode": em,
                            "max_hold_bars": hold,
                        },
                        "status_reason": None,
                    })
    assert len(variants) == 36
    return variants


def make_vm(risk_state, spec_id, vm_id):
    spec_path = f"{BASE}/{risk_state}/strategy_spec.json"
    variants = make_variants()
    selected_ids = [v["variant_id"] for v in variants]
    return {
        "schema_version": "v1",
        "variant_manifest_id": vm_id,
        "non_canonical": True,
        "stage": "stage_1_triage_input_prep_only",
        "execution_authorized": False,
        "risk_control_state": risk_state,
        "amendment_and_supersession": {
            "amendment_mode": "none",
            "amendment_reason": None,
            "associated_results_state": "no_associated_results",
            "close_only_after_results": True,
            "does_not_inherit_prior_results": True,
            "fresh_denominator_required": True,
            "post_result_change": False,
            "preserve_prior_manifest_required": True,
            "supersedes": None,
            "supersession_allowed": False,
            "supersession_lineage": [],
        },
        "exclusion_rules": [],
        "invalid_combination_rules": [],
        "lineage": {
            "audit_notes": [
                f"Scratch-only funding-riskmanaged triage input: risk_control_state={risk_state}.",
                "Signal axes frozen from H-FUNDING-RATE-POSITIONING-FADE-01.",
                "Funding payments remain off; price-P&L signal test.",
                "All 36 denominator rows visible per risk state.",
                "Karl sign-off required before Stage-1 execution.",
                "exit_mode is encoded as VM axis; at execution, decompose to two 18-row runner invocations.",
            ],
            "created_at": "2026-06-27T00:00:00Z",
            "hash_refs": [],
            "parent_refs": [{"ref_hash": None, "ref_id": spec_id, "ref_path": spec_path, "ref_type": "strategy_spec"}],
            "source_refs": [{"ref_hash": None, "ref_id": "H-FUNDING-FADE-RISKMANAGED-01", "ref_path": "docs/research/H_FUNDING_FADE_RISKMANAGED_TRIAGE_PREGATE.md", "ref_type": "hypothesis"}],
            "updated_at": "2026-06-27T00:00:00Z",
        },
        "manifest_hash_pinning": {
            "canonicalization": "json_canonical_v1",
            "frozen_at": "2026-06-27T00:00:00Z",
            "hash_algorithm": "sha256",
            "hash_scope": ["schema_version", "variant_manifest_id", "parent_strategy_spec.strategy_spec_id", "population_governance", "parameter_axes", "variant_assignments"],
            "hash_scope_version": "variant_manifest_hash_scope_v1",
            "hash_status": "not_computed",
            "manifest_hash": None,
            "post_result_mutation_forbidden": True,
            "pre_sweep_freeze_required": True,
        },
        "non_execution_declaration": {
            "not_candidate_approval": True, "not_executable": True, "not_exp_approval": True,
            "not_gate_authority": True, "not_paper_live_authority": True, "not_ranking_authority": True,
            "not_readiness_authority": True, "not_recommendation_authority": True, "not_result_authority": True,
            "not_runner_authority": True, "not_runtime_authority": True, "not_sweep_authority": True,
            "not_transition_authority": True, "planning_surface_only": True,
        },
        "parameter_axes": [
            {
                "axis_id": "AXIS-001", "axis_kind": "free_parameter", "parameter_name": "funding_lookback_bars",
                "parameter_type": "integer", "allowed_values": [2880, 8640, 17280], "generator_method": "manual_grid",
                "counts_toward_parent_free_parameter_cap": True, "is_declared_in_parent_strategy_spec": True,
                "invalid_combination_rule_refs": [],
                "notes": "Frozen H-FUNDING-RATE-POSITIONING-FADE-01 axis. 2880=30d, 8640=90d, 17280=180d.",
                "parent_strategy_spec_parameter_ref": "free_parameters.parameters.funding_lookback_bars",
                "range": {"inclusive_max": True, "inclusive_min": True, "max": 17280, "min": 2880, "step": 5760}, "units": "bars",
            },
            {
                "axis_id": "AXIS-002", "axis_kind": "free_parameter", "parameter_name": "lower_entry_percentile",
                "parameter_type": "number", "allowed_values": [0.05, 0.1], "generator_method": "manual_grid",
                "counts_toward_parent_free_parameter_cap": True, "is_declared_in_parent_strategy_spec": True,
                "invalid_combination_rule_refs": [],
                "notes": "Frozen H-FUNDING-RATE-POSITIONING-FADE-01 axis.",
                "parent_strategy_spec_parameter_ref": "free_parameters.parameters.lower_entry_percentile",
                "range": {"inclusive_max": True, "inclusive_min": True, "max": 0.1, "min": 0.05, "step": 0.05}, "units": "ratio",
            },
            {
                "axis_id": "AXIS-003", "axis_kind": "free_parameter", "parameter_name": "upper_entry_percentile",
                "parameter_type": "number", "allowed_values": [0.9, 0.95], "generator_method": "manual_grid",
                "counts_toward_parent_free_parameter_cap": True, "is_declared_in_parent_strategy_spec": True,
                "invalid_combination_rule_refs": [],
                "notes": "Frozen H-FUNDING-RATE-POSITIONING-FADE-01 axis.",
                "parent_strategy_spec_parameter_ref": "free_parameters.parameters.upper_entry_percentile",
                "range": {"inclusive_max": True, "inclusive_min": True, "max": 0.95, "min": 0.9, "step": 0.05}, "units": "ratio",
            },
            {
                "axis_id": "AXIS-004", "axis_kind": "free_parameter", "parameter_name": "exit_mode",
                "parameter_type": "enum", "allowed_values": ["fixed_max_hold_only", "midline_reversion_or_max_hold"],
                "generator_method": "manual_grid",
                "counts_toward_parent_free_parameter_cap": True, "is_declared_in_parent_strategy_spec": True,
                "invalid_combination_rule_refs": [],
                "notes": "Frozen H-FUNDING-RATE-POSITIONING-FADE-01 axis. Decompose to two runner invocations at execution.",
                "parent_strategy_spec_parameter_ref": "free_parameters.parameters.exit_mode",
                "range": None, "units": None,
            },
            {
                "axis_id": "AXIS-005", "axis_kind": "free_parameter", "parameter_name": "max_hold_bars",
                "parameter_type": "integer", "allowed_values": [16, 32, 96], "generator_method": "manual_grid",
                "counts_toward_parent_free_parameter_cap": True, "is_declared_in_parent_strategy_spec": True,
                "invalid_combination_rule_refs": [],
                "notes": "Frozen H-FUNDING-RATE-POSITIONING-FADE-01 axis.",
                "parent_strategy_spec_parameter_ref": "free_parameters.parameters.max_hold_bars",
                "range": {"inclusive_max": True, "inclusive_min": True, "max": 96, "min": 16, "step": 16}, "units": "bars",
            },
        ],
        "parent_strategy_spec": {
            "does_not_mutate_parent_strategy_spec": True,
            "hash_algorithm": "sha256", "hash_scope_version": "strategy_spec_hash_scope_v1",
            "mismatch_policy": "block", "missing_parent_policy": "block",
            "strategy_spec_hash": None, "strategy_spec_id": spec_id, "strategy_spec_ref": spec_path,
            "strategy_spec_review_status": "approved_for_variant_planning", "strategy_spec_schema_version": "v1",
        },
        "population_governance": {
            "declared_population": {
                "committed_population_count": 36, "declared_variant_count": 36,
                "excluded_variant_count": 0, "included_variant_count": 36,
                "invalid_variant_count": 0, "not_attempted_variant_count": 0,
            },
            "multiple_testing_accounting": {
                "adaptive_search_authorization_ref": None, "adaptive_search_used": False,
                "all_trials_visible_required": True, "denominator_required": True,
                "denominator_type": "committed_pre_registered_population",
                "search_family_id": f"SF-FUNDING-FADE-RISKMANAGED-{risk_state.upper()}-0001",
                "search_family_method": "manual_grid", "winner_only_review_forbidden": True,
            },
            "population_cap": {
                "cap_basis": "manual_grid", "cap_exception_authorized": False, "cap_exception_ref": None,
                "cap_source": "human_declared", "max_variants": 36,
            },
            "pre_registration": {
                "allowed_change_mode": "supersede_before_results_only", "freeze_required_before_sweep": True,
                "post_hoc_addition_forbidden": True, "post_result_mutation_forbidden": True,
                "pre_registered": True, "pre_registration_scope": "full_variant_population",
                "pre_registration_status": "frozen_for_sweep_planning",
            },
            "trial_budget": {
                "denominator_basis": "committed_pre_registered_population_count", "denominator_count": 36,
                "denominator_includes_aborted": True, "denominator_includes_data_unavailable": True,
                "denominator_includes_errored": True, "denominator_includes_excluded": True,
                "denominator_includes_failed": True, "denominator_includes_filtered": True,
                "denominator_includes_invalid": True, "denominator_includes_not_attempted": True,
                "executed_only_denominator_forbidden": True, "planned_trial_count": 36, "trial_budget_denominator": 36,
            },
        },
        "review": {
            "approval_scope": "sweep_planning_only", "human_review_required": True,
            "non_authority_acknowledgement": {
                "not_candidate_approval": True, "not_exp_approval": True, "not_gate_satisfaction": True,
                "not_paper_live_authority": True, "not_ranking_authority": True, "not_readiness_authority": True,
                "not_recommendation_authority": True, "not_result_authority": True, "not_runner_authority": True,
                "not_runtime_authority": True, "not_sweep_authority": True, "not_transition_authority": True,
            },
            "review_notes": [
                f"Scratch-only triage input prep artifact for risk_control_state={risk_state}.",
                "Karl sign-off required before Stage-1 execution.",
                "No crossing, candidate, promotion, paper, live, or runtime authority.",
            ],
            "reviewed_at": None, "reviewer": None,
        },
        "status": "approved_for_sweep_planning",
        "variant_assignments": variants,
    }


def make_sweep_plan(risk_state, spec_id, vm_id, sp_id):
    spec_path = f"{BASE}/{risk_state}/strategy_spec.json"
    vm_path = f"{BASE}/{risk_state}/variant_manifest.json"
    variants = make_variants()
    selected_ids = [v["variant_id"] for v in variants]
    return {
        "schema_version": "v1",
        "sweep_plan_id": sp_id,
        "non_canonical": True,
        "stage": "stage_1_triage_input_prep_only",
        "execution_authorized": False,
        "risk_control_state": risk_state,
        "evaluation_window": {
            "evaluation_start": "2024-01-01T00:00:00Z",
            "evaluation_end": "2025-01-01T00:00:00Z",
            "evaluation_end_semantics": "exclusive",
            "warmup_start_no_later_than": "2023-07-05T00:00:00Z",
            "runner_flags": "--evaluation-start 2024-01-01T00:00:00Z --evaluation-end 2025-01-01T00:00:00Z",
        },
        "amendment_and_supersession": {
            "amendment_mode": "none", "amendment_reason": None,
            "associated_results_state": "no_associated_results", "close_only_after_results": True,
            "does_not_modify_manifest_denominator": True, "does_not_modify_parent_manifest": True,
            "post_result_change": False, "preserve_prior_sweep_plan_required": True,
            "supersedes": None, "supersession_allowed": False, "supersession_lineage": [],
        },
        "data_and_timeframe_assumptions": {
            "confirmation_timeframes": [],
            "data_refs": [
                {"availability": "required", "field": "open", "stream": "ohlcv", "timeframe": "15m"},
                {"availability": "required", "field": "high", "stream": "ohlcv", "timeframe": "15m"},
                {"availability": "required", "field": "low", "stream": "ohlcv", "timeframe": "15m"},
                {"availability": "required", "field": "close", "stream": "ohlcv", "timeframe": "15m"},
                {"availability": "required", "field": "volume", "stream": "ohlcv", "timeframe": "15m"},
                {"availability": "required", "field": "funding_rate", "stream": "funding", "timeframe": "15m"},
            ],
            "gap_handling_assumption": "Use existing BTCUSDT 15m D4A catalog/slice facts and existing gap policy; no silent interpolation.",
            "missing_data_posture": "block_if_missing",
            "primary_timeframe": "15m",
            "runner_consumable_csv": "data/processed/d4a/binance_um_perp_BTCUSDT_15m_2020-01-01_2026-04-11_d4a_normalized_with_funding_rate.csv",
            "runner_consumable_csv_status": "materialized_local_ignored",
        },
        "lineage": {
            "audit_notes": [
                f"Scratch-only sweep plan for risk_control_state={risk_state}.",
                "Funding P&L is not wired; funding_cost_mode remains off.",
                f"Combined per-state denominator is 36 rows.",
                "Karl sign-off required before Stage-1 execution.",
            ],
            "created_at": "2026-06-27T00:00:00Z",
            "parent_manifest_ref": {"ref_hash": None, "ref_id": vm_id, "ref_path": vm_path, "ref_type": "variant_manifest"},
            "parent_strategy_spec_ref": {"ref_hash": None, "ref_id": spec_id, "ref_path": spec_path, "ref_type": "strategy_spec"},
            "search_family_id": f"SF-FUNDING-FADE-RISKMANAGED-{risk_state.upper()}-0001",
            "source_refs": [{"ref_hash": None, "ref_id": "H-FUNDING-FADE-RISKMANAGED-01", "ref_path": "docs/research/H_FUNDING_FADE_RISKMANAGED_TRIAGE_PREGATE.md", "ref_type": "hypothesis"}],
            "updated_at": "2026-06-27T00:00:00Z",
        },
        "non_execution_declaration": {
            "not_candidate_approval": True, "not_executable": True, "not_exp_approval": True,
            "not_gate_authority": True, "not_paper_live_authority": True, "not_ranking_authority": True,
            "not_readiness_authority": True, "not_recommendation_authority": True, "not_result_authority": True,
            "not_runner_authority": True, "not_runtime_authority": True, "not_sweep_authority": True,
            "not_transition_authority": True, "planning_surface_only": True,
        },
        "parent_variant_manifest": {
            "hash_algorithm": "sha256",
            "manifest_committed_population_count": 36,
            "manifest_hash": None,
            "manifest_population_cap": 36,
            "manifest_population_count": 36,
            "manifest_pre_registration_status": "frozen_for_sweep_planning",
            "mismatch_policy": "block",
            "missing_manifest_policy": "block",
            "one_manifest_only": True,
            "variant_manifest_id": vm_id,
            "variant_manifest_schema_version": "v1",
        },
        "realism_assumptions": {
            "bar_path_assumption": "next_open_close_mark",
            "declarations_only": True,
            "exchange_constraints_disclosed": True,
            "fee_side_assumption": "taker_entry_taker_exit",
            "fill_mode": "complete",
            "funding_notional_mode": "entry_price",
            "liquidation_mode": "zero_equity",
            "liquidity_capacity_assumption": None,
            "maintenance_margin_assumption": None,
            "mark_price_source": "close",
            "order_size_assumption": "offline runner: dynamic_equity_target_leverage at target_leverage=1.0; execution not yet authorized",
            "slippage_model": "fixed_bps",
        },
        "result_capture_expectations": {
            "canonical_evidence_mapping_deferred": True,
            "expected_result_population_ref": None,
            "must_capture_aborted": True, "must_capture_data_unavailable": True,
            "must_capture_errored": True, "must_capture_excluded": True,
            "must_capture_failed": True, "must_capture_filtered": True,
            "must_capture_invalid": True, "must_capture_not_attempted": True,
            "must_capture_successful": True, "result_population_expected": True,
            "winner_only_retention_forbidden": True,
        },
        "review": {
            "approval_scope": "offline_run_planning_only",
            "human_review_required": True,
            "non_authority_acknowledgement": {
                "not_candidate_approval": True, "not_exp_approval": True, "not_gate_satisfaction": True,
                "not_paper_live_authority": True, "not_ranking_authority": True, "not_readiness_authority": True,
                "not_recommendation_authority": True, "not_result_authority": True, "not_runner_authority": True,
                "not_runtime_authority": True, "not_sweep_authority": True, "not_transition_authority": True,
            },
            "review_notes": ["Human review required; no candidate or crossing authority.", "Karl sign-off required before Stage-1 execution."],
            "reviewed_at": None, "reviewer": None,
        },
        "status": "approved_for_offline_run_planning",
        "test_selection": {
            "declared_before_results": True,
            "excluded_variant_ids": [],
            "outside_manifest_variants_forbidden": True,
            "post_hoc_addition_forbidden": True,
            "selected_variant_ids": selected_ids,
            "selection_mode": "all_manifest_variants",
            "subset_selection_rule": None,
        },
        "trial_accounting": {
            "aborted_variant_count": 0, "aborted_variants_remain_in_denominator": True,
            "committed_population_count": 36,
            "data_unavailable_variant_count": 0, "data_unavailable_variants_remain_in_denominator": True,
            "denominator_basis": "committed_pre_registered_population_count",
            "denominator_equals_committed_population_count": True,
            "errored_variant_count": 0, "errored_variants_remain_in_denominator": True,
            "excluded_variant_count": 0, "excluded_variants_remain_in_denominator": True,
            "executed_only_denominator_forbidden": True,
            "executed_variant_count": 0,
            "failed_variant_count": 0, "failed_variants_remain_in_denominator": True,
            "filtered_variant_count": 0, "filtered_variants_remain_in_denominator": True,
            "invalid_variants_remain_in_denominator": True,
            "multiple_testing_denominator": 36,
            "not_attempted_variant_count": 36, "not_attempted_variants_remain_in_denominator": True,
            "selected_variant_count": 36,
            "successful_only_denominator_forbidden": True, "successful_variant_count": 0,
        },
        "validation_methods": {
            "backtest": {
                "enabled": True, "method_ref": None,
                "notes": f"Price-P&L funding-rate signal test; risk_control_state={risk_state}; costs enabled by runner convention. Evaluation window 2024-01-01 to 2025-01-01 (exclusive). Warmup prefix from 2023-07-05.",
            },
            "declarative_intent_only": True,
            "dsr_psr_mintrl_accounting": {
                "computation_deferred": True, "denominator_ref": "committed_population_count",
                "enabled": True, "notes": f"36-row {risk_state} slice of the combined 108-row denominator.",
            },
            "monte_carlo": {"computation_deferred": True, "enabled": False, "method_ref": None, "notes": None},
            "no_computation": True, "no_formulas": True, "no_runner_hooks": True,
            "robustness": {"enabled": False, "families_declared": [], "method_ref": None, "notes": None},
            "walk_forward_oos": {
                "declares_chronological_separation": False, "enabled": False, "method_ref": None,
                "notes": "Walk-forward is a possible next step only if Stage-1 results satisfy stop/go criteria.",
            },
        },
    }


for risk_state, spec_id, vm_id, sp_id in SPECS:
    vm_path = f"{BASE}/{risk_state}/variant_manifest.json"
    sp_path = f"{BASE}/{risk_state}/sweep_plan.json"
    vm = make_vm(risk_state, spec_id, vm_id)
    sp = make_sweep_plan(risk_state, spec_id, vm_id, sp_id)
    with open(vm_path, "w") as f:
        json.dump(vm, f, indent=2)
    with open(sp_path, "w") as f:
        json.dump(sp, f, indent=2)
    print(f"Written VM: {vm_path} ({len(vm['variant_assignments'])} variants)")
    print(f"Written SP: {sp_path} ({len(sp['test_selection']['selected_variant_ids'])} selected)")

print("Done.")
