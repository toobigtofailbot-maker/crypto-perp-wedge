import copy
import hashlib
import json
import shutil
import sys
from pathlib import Path

import pytest
from jsonschema import Draft7Validator

from tests.test_validate_strategy_specs import (
    _base_strategy_spec,
    _lookback_parameter,
    _online_primitives,
    _threshold_parameter,
)
from tools.registry.validate_variant_sweep_artifacts import (
    DEFAULT_STRATEGY_SPEC_SCHEMA_PATH,
    DEFAULT_SWEEP_PLAN_SCHEMA_PATH,
    DEFAULT_VARIANT_MANIFEST_SCHEMA_PATH,
    _hash_scope_payload,
    main,
    sha256_prefixed,
    validate_variant_sweep_artifacts,
)
from tools.canon_intake import variant_planning_approval as approval_writer


REPO_ROOT = Path(__file__).resolve().parents[1]


def _load_schema(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _base_strategy_spec_for_variant(strategy_spec_id: str = "STRAT-SPEC-9001") -> dict:
    payload = _base_strategy_spec(strategy_spec_id)
    payload["status"] = "approved_for_variant_planning"
    payload["review"]["approval_scope"] = "variant_planning_only"
    payload["free_parameters"] = {
        "max_free_parameters": 5,
        "counting_rule": (
            "parameters contains only entries where is_free_parameter=true; "
            "maxItems 5 enforces the D2-006-style MVP free-parameter cap"
        ),
        "parameters": [
            {
                "name": "lookback",
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
        ],
        "no_free_parameters_declared": False,
    }
    payload["pre_registration_support"]["intended_for_variant_manifest"] = True
    return payload


def _true_flags(*names: str) -> dict:
    return {name: True for name in names}


def _base_variant_manifest(parent_hash: str) -> dict:
    payload = {
        "schema_version": "v1",
        "variant_manifest_id": "VM-0001",
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
            "strategy_spec_hash": parent_hash,
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
                "variant_id": "VAR-000001",
                "assignment_status": "included",
                "parameter_values": {"lookback": 10},
                "parameter_value_hash": None,
                "axis_refs": ["AXIS-001"],
                "exclusion_rule_refs": [],
                "invalid_combination_rule_refs": [],
                "status_reason": None,
                "lineage": {"generated_by_rule": "manual-grid", "generation_order": 1},
            },
            {
                "variant_id": "VAR-000002",
                "assignment_status": "included",
                "parameter_values": {"lookback": 20},
                "parameter_value_hash": None,
                "axis_refs": ["AXIS-001"],
                "exclusion_rule_refs": [],
                "invalid_combination_rule_refs": [],
                "status_reason": None,
                "lineage": {"generated_by_rule": "manual-grid", "generation_order": 2},
            },
        ],
        "manifest_hash_pinning": {
            "manifest_hash": None,
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
    scoped_payload = _hash_scope_payload(payload, payload["manifest_hash_pinning"]["hash_scope"])
    payload["manifest_hash_pinning"]["manifest_hash"] = sha256_prefixed(scoped_payload)
    return payload


def _base_sweep_plan(manifest: dict) -> dict:
    manifest_hash = manifest["manifest_hash_pinning"]["manifest_hash"]
    return {
        "schema_version": "v1",
        "sweep_plan_id": "SWEEP-PLAN-0001",
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
            "variant_manifest_id": "VM-0001",
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
            "selected_variant_ids": ["VAR-000001", "VAR-000002"],
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
                "ref_id": "VM-0001",
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


def _fixture_paths(tmp_path: Path) -> tuple[Path, Path, Path]:
    root = tmp_path / "research"
    return root / "strategy_specs", root / "variant_manifests", root / "sweep_plans"


def _write_valid_fixture(tmp_path: Path) -> tuple[dict, dict, dict, Path, Path, Path]:
    strategy_specs_dir, variant_manifests_dir, sweep_plans_dir = _fixture_paths(tmp_path)
    strategy_spec = _base_strategy_spec_for_variant()
    strategy_hash = sha256_prefixed(strategy_spec)
    manifest = _base_variant_manifest(strategy_hash)
    sweep = _base_sweep_plan(manifest)
    _write_json(strategy_specs_dir / "STRAT-SPEC-9001.strategy_spec.json", strategy_spec)
    _write_json(variant_manifests_dir / "VM-0001.variant_manifest.json", manifest)
    _write_json(sweep_plans_dir / "SWEEP-PLAN-0001.sweep_plan.json", sweep)
    return strategy_spec, manifest, sweep, strategy_specs_dir, variant_manifests_dir, sweep_plans_dir


def _validate(tmp_path: Path) -> list[str]:
    strategy_specs_dir, variant_manifests_dir, sweep_plans_dir = _fixture_paths(tmp_path)
    return validate_variant_sweep_artifacts(
        variant_manifests_dir=variant_manifests_dir,
        sweep_plans_dir=sweep_plans_dir,
        strategy_specs_dir=strategy_specs_dir,
        repo_root=tmp_path,
    )


def _rehash_manifest(manifest: dict) -> None:
    scoped = _hash_scope_payload(
        manifest, manifest["manifest_hash_pinning"]["hash_scope"]
    )
    manifest["manifest_hash_pinning"]["manifest_hash"] = sha256_prefixed(scoped)


def _approval_flags() -> dict:
    flags = {
        name: False
        for name in (
            "authorizes_strategy_spec_mutation",
            "authorizes_gate_c",
            "authorizes_gate_q",
            "authorizes_queue_admission",
            "authorizes_dispatch",
            "authorizes_research_execution",
            "authorizes_result_population",
            "authorizes_candidate_lifecycle",
            "authorizes_ranking",
            "authorizes_recommendation",
            "authorizes_promotion_readiness",
            "authorizes_scheduler_autonomy",
            "authorizes_notifications",
            "authorizes_runtime",
            "authorizes_paper_live",
            "authorizes_oms_risk_reconciliation",
        )
    }
    flags.update(
        {
            "authorizes_variant_manifest_preparation": True,
            "authorizes_one_manifest_only": True,
        }
    )
    return flags


def _write_external_fixture(tmp_path: Path, gate_c_extras: dict | None = None):
    spec, manifest, sweep, specs, vms, sweeps = _write_valid_fixture(tmp_path)
    shutil.copytree(
        REPO_ROOT / "research/schemas",
        tmp_path / "research/schemas",
        dirs_exist_ok=True,
    )
    spec["status"] = "review_requested"
    spec["review"]["approval_scope"] = "none"
    spec_path = specs / "STRAT-SPEC-9001.strategy_spec.json"
    _write_json(spec_path, spec)
    parent_raw = spec_path.read_bytes()
    manifest["parent_strategy_spec"]["strategy_spec_hash"] = sha256_prefixed(spec)
    manifest["parent_strategy_spec"]["strategy_spec_ref"] = (
        "research/strategy_specs/STRAT-SPEC-9001.strategy_spec.json"
    )
    second_axis = copy.deepcopy(manifest["parameter_axes"][0])
    second_axis.update(
        {
            "axis_id": "AXIS-002",
            "parameter_name": "threshold",
            "parent_strategy_spec_parameter_ref": "free_parameters.parameters.threshold",
            "allowed_values": [1, 2],
            "range": {
                "min": 1,
                "max": 2,
                "step": 1,
                "inclusive_min": True,
                "inclusive_max": True,
            },
        }
    )
    manifest["parameter_axes"].append(second_axis)
    manifest["variant_assignments"] = []
    generation = 0
    for lookback in (10, 20):
        for threshold in (1, 2):
            generation += 1
            manifest["variant_assignments"].append(
                {
                    "variant_id": f"VAR-{generation:06d}",
                    "assignment_status": "included",
                    "parameter_values": {
                        "lookback": lookback,
                        "threshold": threshold,
                    },
                    "parameter_value_hash": None,
                    "axis_refs": ["AXIS-001", "AXIS-002"],
                    "exclusion_rule_refs": [],
                    "invalid_combination_rule_refs": [],
                    "status_reason": None,
                    "lineage": {
                        "generated_by_rule": "manual-grid",
                        "generation_order": generation,
                    },
                }
            )
    governance = manifest["population_governance"]
    governance["population_cap"]["max_variants"] = 4
    governance["declared_population"]["committed_population_count"] = 4
    governance["declared_population"]["declared_variant_count"] = 4
    governance["declared_population"]["included_variant_count"] = 4
    governance["trial_budget"]["planned_trial_count"] = 4
    governance["trial_budget"]["trial_budget_denominator"] = 4
    governance["trial_budget"]["denominator_count"] = 4
    _rehash_manifest(manifest)
    sweep = _base_sweep_plan(manifest)
    sweep["parent_variant_manifest"]["manifest_population_count"] = 4
    sweep["parent_variant_manifest"]["manifest_committed_population_count"] = 4
    sweep["parent_variant_manifest"]["manifest_population_cap"] = 4
    sweep["test_selection"]["selected_variant_ids"] = [
        f"VAR-{index:06d}" for index in range(1, 5)
    ]
    sweep["trial_accounting"]["committed_population_count"] = 4
    sweep["trial_accounting"]["selected_variant_count"] = 4
    sweep["trial_accounting"]["not_attempted_variant_count"] = 4
    sweep["trial_accounting"]["multiple_testing_denominator"] = 4
    vm_path = vms / "VM-0001.variant_manifest.json"
    sweep_path = sweeps / "SWEEP-PLAN-0001.sweep_plan.json"
    vm_path.unlink()
    sweep_path.unlink()

    gate_record = {
        "schema_version": "gate_c_strategy_spec_write_audit_v1",
        "approval_id": "GATE-C-TEST",
        "approved_by": "Karl",
        "strategy_spec_id": "STRAT-SPEC-9001",
        "canonical_target_path": (
            "research/strategy_specs/STRAT-SPEC-9001.strategy_spec.json"
        ),
        "approved_content_sha256": "sha256:"
        + hashlib.sha256(parent_raw).hexdigest(),
        "validation_outcome": "passed_before_write",
        "no_queue_candidate_runtime_outputs": True,
    }
    gate_record.update(gate_c_extras or {})
    gate_raw = approval_writer.repo_canonical_json_v1(gate_record) + b"\n"
    gate_path = tmp_path / approval_writer.GATE_C_AUDIT_PATH
    gate_path.parent.mkdir(parents=True, exist_ok=True)
    gate_path.write_bytes(gate_raw)
    core = {
        "strategy_spec_id": "STRAT-SPEC-9001",
        "strategy_spec_path": (
            "research/strategy_specs/STRAT-SPEC-9001.strategy_spec.json"
        ),
        "strategy_spec_sha256": "sha256:" + hashlib.sha256(parent_raw).hexdigest(),
        "variant_manifest_id": "VM-0001",
        "variant_manifest_path": "research/variant_manifests/VM-0001.variant_manifest.json",
        "search_family_id": "SF-9001",
        "ordered_parameter_axes": [
            {"name": "lookback", "integer_values": [10, 20]},
            {"name": "threshold", "integer_values": [1, 2]},
        ],
        "population_cap": 4,
        "committed_population_count": 4,
        "denominator_basis": "committed_pre_registered_population_count",
        "adaptive_search": False,
        "post_hoc_mutation_forbidden": True,
        "authority": "one_bounded_variant_manifest_preparation_only",
    }
    approval_id = "VPAPP-20260714-TEST0001"
    approval_rel = (
        "research/strategy_spec_variant_planning_approvals/"
        f"{approval_id}.variant_planning_approval.json"
    )
    approval = {
        "schema_version": "strategy_spec_variant_planning_approval_v1",
        "approval_id": approval_id,
        "approval_artifact_target_path": approval_rel,
        "approved_by": "Karl",
        "approved_at": "2026-07-14T12:00:00-05:00",
        "approval_scope": "one_bounded_variant_manifest_preparation",
        "exact_content_and_target_only": True,
        "append_only": True,
        "single_use_approval_id": True,
        "canonical_parent": {
            "strategy_spec_id": "STRAT-SPEC-9001",
            "path": "research/strategy_specs/STRAT-SPEC-9001.strategy_spec.json",
            "sha256": "sha256:" + hashlib.sha256(parent_raw).hexdigest(),
            "embedded_status": "review_requested",
            "gate_c_audit": {
                "audit_path": approval_writer.GATE_C_AUDIT_PATH,
                "line_number": 1,
                "raw_record_sha256": "sha256:" + hashlib.sha256(gate_raw).hexdigest(),
                "gate_c_approval_id": "GATE-C-TEST",
                "strategy_spec_id": "STRAT-SPEC-9001",
                "canonical_target_path": (
                    "research/strategy_specs/STRAT-SPEC-9001.strategy_spec.json"
                ),
            },
        },
        "variant_manifest_contract_core": core,
        "contract_core_sha256": approval_writer.contract_core_sha256(core),
        "contract_core_hash_scope": "variant_planning_contract_core_v1",
        "contract_core_canonicalization": "repo_canonical_json_v1",
        "amendment_revocation_policy": (
            "supersede_with_new_approval_before_manifest_creation"
        ),
        "reuse_policy": "reject_all_identifier_path_and_search_family_reuse",
        "overwrite_forbidden": True,
        "authority_flags": _approval_flags(),
    }
    proposal = tmp_path / "scratch/proposed.variant_planning_approval.json"
    _write_json(proposal, approval)
    approval_writer.write_variant_planning_approval(
        repo_root=tmp_path, approval_path=proposal
    )
    approval_path = tmp_path / approval_rel
    manifest["variant_planning_approval"] = {
        "approval_id": approval_id,
        "path": approval_rel,
        "sha256": "sha256:" + hashlib.sha256(approval_path.read_bytes()).hexdigest(),
        "contract_core_sha256": approval["contract_core_sha256"],
        "evidence_mode": "external_append_only_approval",
    }
    _write_json(vm_path, manifest)
    _write_json(sweep_path, sweep)
    return spec, manifest, sweep, specs, vms, sweeps, approval_path


def _validate_external(tmp_path: Path) -> list[str]:
    specs, vms, sweeps = _fixture_paths(tmp_path)
    return validate_variant_sweep_artifacts(
        variant_manifests_dir=vms,
        sweep_plans_dir=sweeps,
        strategy_specs_dir=specs,
        variant_manifest_schema_path=tmp_path
        / "research/schemas/variant_manifest.schema.json",
        sweep_plan_schema_path=tmp_path / "research/schemas/sweep_plan.schema.json",
        strategy_spec_schema_path=tmp_path
        / "research/schemas/strategy_spec.schema.json",
        repo_root=tmp_path,
    )


def test_all_six_canonical_legacy_bundles_validate_without_external_evidence():
    before = {
        path: hashlib.sha256(path.read_bytes()).hexdigest()
        for directory, pattern in (
            (REPO_ROOT / "research/strategy_specs", "*.strategy_spec.json"),
            (REPO_ROOT / "research/variant_manifests", "*.variant_manifest.json"),
            (REPO_ROOT / "research/sweep_plans", "*.sweep_plan.json"),
        )
        for path in directory.glob(pattern)
    }
    assert validate_variant_sweep_artifacts() == []
    legacy_manifests = [
        REPO_ROOT
        / "research/variant_manifests"
        / f"VM-{index:04d}.variant_manifest.json"
        for index in range(1, 7)
    ]
    legacy_sweeps = [
        REPO_ROOT
        / "research/sweep_plans"
        / f"SWEEP-PLAN-{index:04d}.sweep_plan.json"
        for index in range(1, 7)
    ]
    assert all(path.is_file() for path in legacy_manifests + legacy_sweeps)
    assert all(
        "variant_planning_approval" not in json.loads(path.read_text(encoding="utf-8"))
        for path in legacy_manifests
    )
    assert before == {
        path: hashlib.sha256(path.read_bytes()).hexdigest() for path in before
    }


def test_review_requested_parent_with_exact_external_approval_validates(tmp_path):
    _write_external_fixture(tmp_path)
    assert _validate_external(tmp_path) == []


def test_review_requested_parent_without_external_approval_rejects(tmp_path):
    spec, manifest, _, _, vms, _, _ = _write_external_fixture(tmp_path)
    del spec
    manifest.pop("variant_planning_approval")
    _write_json(vms / "VM-0001.variant_manifest.json", manifest)
    assert any("requires external" in error for error in _validate_external(tmp_path))


def test_embedded_approved_parent_with_external_object_rejects(tmp_path):
    _, manifest, _, _, vms, _ = _write_valid_fixture(tmp_path)
    manifest["variant_planning_approval"] = {
        "approval_id": "VPAPP-20260714-TEST0001",
        "path": (
            "research/strategy_spec_variant_planning_approvals/"
            "VPAPP-20260714-TEST0001.variant_planning_approval.json"
        ),
        "sha256": "sha256:" + "0" * 64,
        "contract_core_sha256": "sha256:" + "1" * 64,
        "evidence_mode": "external_append_only_approval",
    }
    _write_json(vms / "VM-0001.variant_manifest.json", manifest)
    assert any("must not include external" in error for error in _validate(tmp_path))


def test_unsupported_parent_status_cannot_claim_planning_approval(tmp_path):
    spec, _, _, specs, _, _ = _write_valid_fixture(tmp_path)
    spec["status"] = "draft"
    _write_json(specs / "STRAT-SPEC-9001.strategy_spec.json", spec)
    assert any("cannot support the literal" in error for error in _validate(tmp_path))


@pytest.mark.parametrize(
    "field,value,match",
    [
        ("approval_id", "VPAPP-20260714-WRONG001", "path|ID|matching"),
        ("sha256", "sha256:" + "0" * 64, "whole-file hash"),
        ("contract_core_sha256", "sha256:" + "1" * 64, "contract-core hash"),
        ("evidence_mode", "legacy", "external_append|evidence mode"),
    ],
)
def test_external_approval_reference_mismatches_reject(tmp_path, field, value, match):
    _, manifest, _, _, vms, _, _ = _write_external_fixture(tmp_path)
    manifest["variant_planning_approval"][field] = value
    _write_json(vms / "VM-0001.variant_manifest.json", manifest)
    assert any(
        any(token.lower() in error.lower() for token in match.split("|"))
        for error in _validate_external(tmp_path)
    )


@pytest.mark.parametrize(
    "mutation,match",
    [
        (lambda vm: vm["parameter_axes"].reverse(), "contract core"),
        (
            lambda vm: vm["parameter_axes"][0].__setitem__("parameter_name", "other"),
            "contract core",
        ),
        (
            lambda vm: vm["parameter_axes"][0].__setitem__("allowed_values", [10, 30]),
            "contract core",
        ),
        (
            lambda vm: vm["population_governance"]["population_cap"].__setitem__(
                "max_variants", 3
            ),
            "contract core",
        ),
        (
            lambda vm: vm["population_governance"]["multiple_testing_accounting"].__setitem__(
                "adaptive_search_used", True
            ),
            "contract core",
        ),
        (
            lambda vm: vm["population_governance"]["pre_registration"].__setitem__(
                "post_result_mutation_forbidden", False
            ),
            "contract core",
        ),
    ],
)
def test_external_vm_contract_mutations_reject(tmp_path, mutation, match):
    _, manifest, _, _, vms, _, _ = _write_external_fixture(tmp_path)
    mutation(manifest)
    _rehash_manifest(manifest)
    _write_json(vms / "VM-0001.variant_manifest.json", manifest)
    errors = _validate_external(tmp_path)
    assert errors


def test_external_number_outside_exact_milli_scale_rejects(tmp_path):
    _, manifest, _, _, vms, _, _ = _write_external_fixture(tmp_path)
    axis = manifest["parameter_axes"][0]
    axis["parameter_type"] = "number"
    axis["allowed_values"] = [1.0001, 2.0]
    manifest["variant_assignments"][0]["parameter_values"] = {"lookback": 1.0001}
    manifest["variant_assignments"][1]["parameter_values"] = {"lookback": 2.0}
    _rehash_manifest(manifest)
    _write_json(vms / "VM-0001.variant_manifest.json", manifest)
    assert any("milli scale" in error for error in _validate_external(tmp_path))


def test_missing_or_duplicate_variant_planning_audit_rejects(tmp_path):
    _write_external_fixture(tmp_path)
    audit = tmp_path / approval_writer.AUDIT_PATH
    line = audit.read_bytes()
    audit.unlink()
    assert any("audit" in error for error in _validate_external(tmp_path))
    audit.parent.mkdir(parents=True, exist_ok=True)
    audit.write_bytes(line + line)
    assert any("duplicate" in error for error in _validate_external(tmp_path))


def test_external_approval_path_traversal_rejects(tmp_path):
    _, manifest, _, _, vms, _, _ = _write_external_fixture(tmp_path)
    manifest["variant_planning_approval"]["path"] = (
        "../strategy_spec_variant_planning_approvals/"
        "VPAPP-20260714-TEST0001.variant_planning_approval.json"
    )
    _write_json(vms / "VM-0001.variant_manifest.json", manifest)
    assert _validate_external(tmp_path)


def test_external_approval_symlink_component_rejects_without_os_symlink(
    tmp_path, monkeypatch
):
    _, _, _, _, _, _, approval_path = _write_external_fixture(tmp_path)
    original = Path.is_symlink

    def simulated_symlink(path):
        if path == approval_path.parent:
            return True
        return original(path)

    monkeypatch.setattr(Path, "is_symlink", simulated_symlink)
    assert any("symlink" in error for error in _validate_external(tmp_path))


def test_stale_gate_c_raw_line_rejects_external_vm(tmp_path):
    _write_external_fixture(tmp_path)
    gate_c = tmp_path / approval_writer.GATE_C_AUDIT_PATH
    gate_c.write_bytes(gate_c.read_bytes().replace(b'"approved_by":"Karl"', b'"approved_by":"Other"'))
    assert any("Gate-C" in error for error in _validate_external(tmp_path))


def test_reused_external_vm_search_family_rejects(tmp_path):
    _, manifest, _, _, vms, _, _ = _write_external_fixture(tmp_path)
    duplicate = copy.deepcopy(manifest)
    duplicate["variant_manifest_id"] = "VM-0002"
    _rehash_manifest(duplicate)
    _write_json(vms / "VM-0002.variant_manifest.json", duplicate)
    assert any(
        "duplicate" in error or "single-use" in error
        for error in _validate_external(tmp_path)
    )


def test_variant_and_sweep_schemas_meta_valid():
    Draft7Validator.check_schema(_load_schema(DEFAULT_VARIANT_MANIFEST_SCHEMA_PATH))
    Draft7Validator.check_schema(_load_schema(DEFAULT_SWEEP_PLAN_SCHEMA_PATH))
    Draft7Validator.check_schema(_load_schema(DEFAULT_STRATEGY_SPEC_SCHEMA_PATH))


def test_validator_noops_when_directories_missing(tmp_path):
    errors = validate_variant_sweep_artifacts(
        variant_manifests_dir=tmp_path / "missing_vm",
        sweep_plans_dir=tmp_path / "missing_sweep",
        strategy_specs_dir=tmp_path / "missing_specs",
    )

    assert errors == []


def test_validator_noops_when_directories_empty(tmp_path):
    strategy_specs_dir, variant_manifests_dir, sweep_plans_dir = _fixture_paths(tmp_path)
    variant_manifests_dir.mkdir(parents=True)
    sweep_plans_dir.mkdir(parents=True)

    errors = validate_variant_sweep_artifacts(
        variant_manifests_dir=variant_manifests_dir,
        sweep_plans_dir=sweep_plans_dir,
        strategy_specs_dir=strategy_specs_dir,
    )

    assert errors == []


def test_valid_parent_manifest_and_sweep_plan_pass(tmp_path):
    _write_valid_fixture(tmp_path)

    assert _validate(tmp_path) == []


def test_manifest_must_include_axis_for_parent_strategy_value_parameter_ref(tmp_path):
    strategy_specs_dir, variant_manifests_dir, sweep_plans_dir = _fixture_paths(tmp_path)
    strategy_spec = _base_strategy_spec_for_variant()
    strategy_spec["online_ohlcv_primitives"] = _online_primitives()
    strategy_spec["online_ohlcv_primitives"]["candle_shapes"][0]["upper_wick_pct"]["value"] = {
        "parameter_ref": "wick_threshold"
    }
    strategy_spec["free_parameters"]["parameters"].append(
        _threshold_parameter(name="wick_threshold", allowed_values=[0.05, 0.10])
    )
    strategy_hash = sha256_prefixed(strategy_spec)
    manifest = _base_variant_manifest(strategy_hash)
    manifest["parent_strategy_spec"]["strategy_spec_hash"] = strategy_hash
    sweep = _base_sweep_plan(manifest)
    _write_json(strategy_specs_dir / "STRAT-SPEC-9001.strategy_spec.json", strategy_spec)
    _write_json(variant_manifests_dir / "VM-0001.variant_manifest.json", manifest)
    _write_json(sweep_plans_dir / "SWEEP-PLAN-0001.sweep_plan.json", sweep)

    errors = _validate(tmp_path)

    assert any("parameter_ref 'wick_threshold' must be present in parameter_axes" in error for error in errors)


def test_manifest_must_include_axis_for_max_hold_parameter_ref(tmp_path):
    strategy_specs_dir, variant_manifests_dir, sweep_plans_dir = _fixture_paths(tmp_path)
    strategy_spec = _base_strategy_spec_for_variant()
    strategy_spec["exit_logic"]["max_holding_period"] = {
        "enabled": True,
        "bars": {"parameter_ref": "max_hold_bars"},
    }
    max_hold = _lookback_parameter(
        name="max_hold_bars",
        default=16,
        range_value={
            "min": 16,
            "max": 96,
            "step": 16,
            "inclusive_min": True,
            "inclusive_max": True,
        },
        allowed_values=[16, 32, 96],
    )
    max_hold["role"] = "exit"
    strategy_spec["free_parameters"]["parameters"].append(max_hold)
    strategy_hash = sha256_prefixed(strategy_spec)
    manifest = _base_variant_manifest(strategy_hash)
    sweep = _base_sweep_plan(manifest)
    _write_json(strategy_specs_dir / "STRAT-SPEC-9001.strategy_spec.json", strategy_spec)
    _write_json(variant_manifests_dir / "VM-0001.variant_manifest.json", manifest)
    _write_json(sweep_plans_dir / "SWEEP-PLAN-0001.sweep_plan.json", sweep)

    errors = _validate(tmp_path)

    assert any("parameter_ref 'max_hold_bars' must be present in parameter_axes" in error for error in errors)


def test_manifest_accepts_axis_for_parent_strategy_value_parameter_ref(tmp_path):
    strategy_specs_dir, variant_manifests_dir, sweep_plans_dir = _fixture_paths(tmp_path)
    strategy_spec = _base_strategy_spec_for_variant()
    strategy_spec["online_ohlcv_primitives"] = _online_primitives()
    strategy_spec["online_ohlcv_primitives"]["candle_shapes"][0]["upper_wick_pct"]["value"] = {
        "parameter_ref": "wick_threshold"
    }
    strategy_spec["free_parameters"]["parameters"].append(
        _threshold_parameter(name="wick_threshold", allowed_values=[0.05, 0.10])
    )
    strategy_hash = sha256_prefixed(strategy_spec)
    manifest = _base_variant_manifest(strategy_hash)
    manifest["parent_strategy_spec"]["strategy_spec_hash"] = strategy_hash
    manifest["parameter_axes"].append(
        {
            "axis_id": "AXIS-002",
            "parameter_name": "wick_threshold",
            "parent_strategy_spec_parameter_ref": "free_parameters.parameters.wick_threshold",
            "parameter_type": "number",
            "units": "ratio",
            "axis_kind": "free_parameter",
            "generator_method": "manual_grid",
            "allowed_values": [0.05, 0.10],
            "range": {
                "min": 0.05,
                "max": 0.10,
                "step": 0.05,
                "inclusive_min": True,
                "inclusive_max": True,
            },
            "counts_toward_parent_free_parameter_cap": True,
            "is_declared_in_parent_strategy_spec": True,
            "invalid_combination_rule_refs": [],
            "notes": None,
        }
    )
    for index, variant in enumerate(manifest["variant_assignments"]):
        variant["parameter_values"]["wick_threshold"] = [0.05, 0.10][index]
        variant["axis_refs"].append("AXIS-002")
    manifest["manifest_hash_pinning"]["manifest_hash"] = sha256_prefixed(
        _hash_scope_payload(manifest, manifest["manifest_hash_pinning"]["hash_scope"])
    )
    sweep = _base_sweep_plan(manifest)
    _write_json(strategy_specs_dir / "STRAT-SPEC-9001.strategy_spec.json", strategy_spec)
    _write_json(variant_manifests_dir / "VM-0001.variant_manifest.json", manifest)
    _write_json(sweep_plans_dir / "SWEEP-PLAN-0001.sweep_plan.json", sweep)

    assert _validate(tmp_path) == []


def test_invalid_manifest_json_fails(tmp_path):
    _write_valid_fixture(tmp_path)
    _, variant_manifests_dir, _ = _fixture_paths(tmp_path)
    (variant_manifests_dir / "VM-0001.variant_manifest.json").write_text("{", encoding="utf-8")

    assert any("invalid JSON" in error for error in _validate(tmp_path))


def test_invalid_sweep_plan_json_fails(tmp_path):
    _write_valid_fixture(tmp_path)
    _, _, sweep_plans_dir = _fixture_paths(tmp_path)
    (sweep_plans_dir / "SWEEP-PLAN-0001.sweep_plan.json").write_text("{", encoding="utf-8")

    assert any("invalid JSON" in error for error in _validate(tmp_path))


def test_missing_required_schema_field_fails(tmp_path):
    _, manifest, _, _, variant_manifests_dir, _ = _write_valid_fixture(tmp_path)
    del manifest["review"]
    _write_json(variant_manifests_dir / "VM-0001.variant_manifest.json", manifest)

    assert any("review" in error for error in _validate(tmp_path))


def test_missing_nested_committed_population_count_returns_errors_without_raising(tmp_path):
    _, manifest, _, _, variant_manifests_dir, _ = _write_valid_fixture(tmp_path)
    del manifest["population_governance"]["declared_population"]["committed_population_count"]
    _write_json(variant_manifests_dir / "VM-0001.variant_manifest.json", manifest)

    errors = _validate(tmp_path)

    assert errors
    assert any("committed_population_count" in error for error in errors)


def test_missing_nested_population_cap_returns_errors_without_raising(tmp_path):
    _, manifest, _, _, variant_manifests_dir, _ = _write_valid_fixture(tmp_path)
    del manifest["population_governance"]["population_cap"]["max_variants"]
    _write_json(variant_manifests_dir / "VM-0001.variant_manifest.json", manifest)

    errors = _validate(tmp_path)

    assert errors
    assert any("max_variants" in error for error in errors)


def test_missing_nested_sweep_committed_population_count_returns_errors_without_raising(tmp_path):
    _, _, sweep, _, _, sweep_plans_dir = _write_valid_fixture(tmp_path)
    del sweep["trial_accounting"]["committed_population_count"]
    _write_json(sweep_plans_dir / "SWEEP-PLAN-0001.sweep_plan.json", sweep)

    errors = _validate(tmp_path)

    assert errors
    assert any("committed_population_count" in error for error in errors)


def test_manifest_filename_id_mismatch_fails(tmp_path):
    _, manifest, _, _, variant_manifests_dir, _ = _write_valid_fixture(tmp_path)
    (variant_manifests_dir / "VM-0001.variant_manifest.json").unlink()
    _write_json(variant_manifests_dir / "VM-9999.variant_manifest.json", manifest)

    assert any("filename must be VM-0001.variant_manifest.json" in error for error in _validate(tmp_path))


def test_sweep_filename_id_mismatch_fails(tmp_path):
    _, _, sweep, _, _, sweep_plans_dir = _write_valid_fixture(tmp_path)
    (sweep_plans_dir / "SWEEP-PLAN-0001.sweep_plan.json").unlink()
    _write_json(sweep_plans_dir / "SWEEP-PLAN-9999.sweep_plan.json", sweep)

    assert any("filename must be SWEEP-PLAN-0001.sweep_plan.json" in error for error in _validate(tmp_path))


def test_duplicate_manifest_ids_fail(tmp_path):
    _, manifest, _, _, variant_manifests_dir, _ = _write_valid_fixture(tmp_path)
    _write_json(variant_manifests_dir / "nested" / "VM-0001.variant_manifest.json", manifest)

    assert any("duplicate variant_manifest_id VM-0001" in error for error in _validate(tmp_path))


def test_duplicate_sweep_plan_ids_fail(tmp_path):
    _, _, sweep, _, _, sweep_plans_dir = _write_valid_fixture(tmp_path)
    _write_json(sweep_plans_dir / "nested" / "SWEEP-PLAN-0001.sweep_plan.json", sweep)

    assert any("duplicate sweep_plan_id SWEEP-PLAN-0001" in error for error in _validate(tmp_path))


def test_parent_strategy_spec_hash_mismatch_fails(tmp_path):
    _, manifest, _, _, variant_manifests_dir, _ = _write_valid_fixture(tmp_path)
    manifest["parent_strategy_spec"]["strategy_spec_hash"] = "sha256:" + "0" * 64
    _write_json(variant_manifests_dir / "VM-0001.variant_manifest.json", manifest)

    assert any("parent_strategy_spec.strategy_spec_hash mismatch" in error for error in _validate(tmp_path))


def test_manifest_computed_hash_mismatch_fails(tmp_path):
    _, manifest, _, _, variant_manifests_dir, _ = _write_valid_fixture(tmp_path)
    manifest["manifest_hash_pinning"]["manifest_hash"] = "sha256:" + "1" * 64
    _write_json(variant_manifests_dir / "VM-0001.variant_manifest.json", manifest)

    assert any("manifest_hash_pinning.manifest_hash mismatch" in error for error in _validate(tmp_path))


def test_sweep_parent_manifest_hash_mismatch_fails(tmp_path):
    _, _, sweep, _, _, sweep_plans_dir = _write_valid_fixture(tmp_path)
    sweep["parent_variant_manifest"]["manifest_hash"] = "sha256:" + "2" * 64
    _write_json(sweep_plans_dir / "SWEEP-PLAN-0001.sweep_plan.json", sweep)

    assert any("parent_variant_manifest.manifest_hash mismatch" in error for error in _validate(tmp_path))


def test_frozen_manifest_missing_computed_hash_or_timestamp_fails(tmp_path):
    _, manifest, _, _, variant_manifests_dir, _ = _write_valid_fixture(tmp_path)
    manifest["manifest_hash_pinning"]["hash_status"] = "not_computed"
    manifest["manifest_hash_pinning"]["manifest_hash"] = None
    manifest["manifest_hash_pinning"]["frozen_at"] = None
    _write_json(variant_manifests_dir / "VM-0001.variant_manifest.json", manifest)

    errors = _validate(tmp_path)
    assert any("hash_status='computed'" in error for error in errors)
    assert any("requires manifest_hash_pinning.frozen_at" in error for error in errors)


def test_supersession_after_associated_results_fails_for_manifest(tmp_path):
    _, manifest, _, _, variant_manifests_dir, _ = _write_valid_fixture(tmp_path)
    manifest["amendment_and_supersession"]["associated_results_state"] = "associated_results_exist"
    manifest["amendment_and_supersession"]["amendment_mode"] = "supersedes_prior_manifest"
    manifest["amendment_and_supersession"]["supersession_allowed"] = True
    manifest["amendment_and_supersession"]["supersedes"] = {
        "variant_manifest_id": "VM-0002",
        "manifest_hash": "sha256:" + "3" * 64,
        "reason": "fixture",
        "superseded_at": "2026-06-01T00:00:00Z",
    }
    _write_json(variant_manifests_dir / "VM-0001.variant_manifest.json", manifest)

    errors = _validate(tmp_path)

    assert errors
    assert any("amendment_mode" in error for error in errors)


def test_supersession_after_associated_results_fails_for_sweep_plan(tmp_path):
    _, _, sweep, _, _, sweep_plans_dir = _write_valid_fixture(tmp_path)
    sweep["amendment_and_supersession"]["associated_results_state"] = "associated_results_exist"
    sweep["amendment_and_supersession"]["amendment_mode"] = "supersedes_prior_sweep_plan"
    sweep["amendment_and_supersession"]["supersession_allowed"] = True
    sweep["amendment_and_supersession"]["supersedes"] = {
        "sweep_plan_id": "SWEEP-PLAN-0002",
        "sweep_plan_hash": "sha256:" + "4" * 64,
        "reason": "fixture",
        "superseded_at": "2026-06-01T00:00:00Z",
    }
    _write_json(sweep_plans_dir / "SWEEP-PLAN-0001.sweep_plan.json", sweep)

    errors = _validate(tmp_path)

    assert errors
    assert any("amendment_mode" in error for error in errors)


def test_supersession_without_append_only_lineage_or_reason_fails(tmp_path):
    _, manifest, _, _, variant_manifests_dir, _ = _write_valid_fixture(tmp_path)
    manifest["amendment_and_supersession"]["amendment_mode"] = "supersedes_prior_manifest"
    manifest["amendment_and_supersession"]["supersession_allowed"] = True
    manifest["amendment_and_supersession"]["supersedes"] = {
        "variant_manifest_id": "VM-0002",
        "manifest_hash": "sha256:" + "5" * 64,
        "reason": "fixture",
        "superseded_at": "2026-06-01T00:00:00Z",
    }
    _write_json(variant_manifests_dir / "VM-0001.variant_manifest.json", manifest)

    assert any("non-empty supersession_lineage" in error for error in _validate(tmp_path))


def test_manifest_committed_population_denominator_mismatch_fails(tmp_path):
    _, manifest, _, _, variant_manifests_dir, _ = _write_valid_fixture(tmp_path)
    manifest["population_governance"]["trial_budget"]["denominator_count"] = 1
    _write_json(variant_manifests_dir / "VM-0001.variant_manifest.json", manifest)

    assert any("trial_budget.denominator_count" in error for error in _validate(tmp_path))


def test_sweep_committed_denominator_mismatch_fails(tmp_path):
    _, _, sweep, _, _, sweep_plans_dir = _write_valid_fixture(tmp_path)
    sweep["trial_accounting"]["multiple_testing_denominator"] = 1
    _write_json(sweep_plans_dir / "SWEEP-PLAN-0001.sweep_plan.json", sweep)

    assert any("multiple_testing_denominator" in error for error in _validate(tmp_path))


def test_executed_only_or_successful_only_denominator_posture_fails(tmp_path):
    _, _, sweep, _, _, sweep_plans_dir = _write_valid_fixture(tmp_path)
    sweep["trial_accounting"]["executed_only_denominator_forbidden"] = False
    sweep["trial_accounting"]["successful_only_denominator_forbidden"] = False
    _write_json(sweep_plans_dir / "SWEEP-PLAN-0001.sweep_plan.json", sweep)

    errors = _validate(tmp_path)
    assert any("executed_only_denominator_forbidden" in error for error in errors)
    assert any("successful_only_denominator_forbidden" in error for error in errors)


def test_count_breakdown_mismatch_fails(tmp_path):
    _, manifest, _, _, variant_manifests_dir, _ = _write_valid_fixture(tmp_path)
    manifest["population_governance"]["declared_population"]["included_variant_count"] = 1
    _write_json(variant_manifests_dir / "VM-0001.variant_manifest.json", manifest)

    assert any("included_variant_count" in error for error in _validate(tmp_path))


def test_declared_count_exceeding_finite_cap_fails(tmp_path):
    _, manifest, _, _, variant_manifests_dir, _ = _write_valid_fixture(tmp_path)
    manifest["population_governance"]["population_cap"]["max_variants"] = 1
    _write_json(variant_manifests_dir / "VM-0001.variant_manifest.json", manifest)

    assert any("exceeds population_cap.max_variants" in error for error in _validate(tmp_path))


def test_more_than_five_parameter_axes_fails(tmp_path):
    _, manifest, _, _, variant_manifests_dir, _ = _write_valid_fixture(tmp_path)
    for index in range(2, 7):
        axis = copy.deepcopy(manifest["parameter_axes"][0])
        axis["axis_id"] = f"AXIS-00{index}"
        axis["parameter_name"] = f"param_{index}"
        manifest["parameter_axes"].append(axis)
        for variant in manifest["variant_assignments"]:
            variant["axis_refs"].append(axis["axis_id"])
            variant["parameter_values"][axis["parameter_name"]] = 10
    _write_json(variant_manifests_dir / "VM-0001.variant_manifest.json", manifest)

    assert any("parameter_axes" in error for error in _validate(tmp_path))


def test_adaptive_search_flag_true_fails(tmp_path):
    _, manifest, _, _, variant_manifests_dir, _ = _write_valid_fixture(tmp_path)
    manifest["population_governance"]["multiple_testing_accounting"]["adaptive_search_used"] = True
    _write_json(variant_manifests_dir / "VM-0001.variant_manifest.json", manifest)

    assert any("adaptive_search_used" in error for error in _validate(tmp_path))


def test_cap_exception_flag_true_fails(tmp_path):
    _, manifest, _, _, variant_manifests_dir, _ = _write_valid_fixture(tmp_path)
    manifest["population_governance"]["population_cap"]["cap_exception_authorized"] = True
    _write_json(variant_manifests_dir / "VM-0001.variant_manifest.json", manifest)

    assert any("cap_exception_authorized" in error for error in _validate(tmp_path))


def test_duplicate_axis_id_fails(tmp_path):
    _, manifest, _, _, variant_manifests_dir, _ = _write_valid_fixture(tmp_path)
    axis = copy.deepcopy(manifest["parameter_axes"][0])
    axis["parameter_name"] = "second_lookback"
    manifest["parameter_axes"].append(axis)
    _write_json(variant_manifests_dir / "VM-0001.variant_manifest.json", manifest)

    assert any("duplicate axis_id" in error for error in _validate(tmp_path))


def test_duplicate_variant_id_fails(tmp_path):
    _, manifest, _, _, variant_manifests_dir, _ = _write_valid_fixture(tmp_path)
    manifest["variant_assignments"][1]["variant_id"] = "VAR-000001"
    _write_json(variant_manifests_dir / "VM-0001.variant_manifest.json", manifest)

    assert any("duplicate variant_id VAR-000001" in error for error in _validate(tmp_path))


def test_variant_assignment_referencing_undeclared_axis_fails(tmp_path):
    _, manifest, _, _, variant_manifests_dir, _ = _write_valid_fixture(tmp_path)
    manifest["variant_assignments"][0]["axis_refs"] = ["AXIS-999"]
    _write_json(variant_manifests_dir / "VM-0001.variant_manifest.json", manifest)

    assert any("undeclared axis" in error for error in _validate(tmp_path))


def test_variant_assignment_parameter_outside_allowed_range_fails(tmp_path):
    _, manifest, _, _, variant_manifests_dir, _ = _write_valid_fixture(tmp_path)
    manifest["variant_assignments"][0]["parameter_values"]["lookback"] = 99
    _write_json(variant_manifests_dir / "VM-0001.variant_manifest.json", manifest)

    assert any("outside allowed_values" in error for error in _validate(tmp_path))


def test_sweep_selected_variant_outside_parent_manifest_fails(tmp_path):
    _, _, sweep, _, _, sweep_plans_dir = _write_valid_fixture(tmp_path)
    sweep["test_selection"]["selected_variant_ids"] = ["VAR-000001", "VAR-999999"]
    _write_json(sweep_plans_dir / "SWEEP-PLAN-0001.sweep_plan.json", sweep)

    assert any("outside manifest" in error for error in _validate(tmp_path))


def test_validation_method_runner_or_computation_flag_false_fails(tmp_path):
    _, _, sweep, _, _, sweep_plans_dir = _write_valid_fixture(tmp_path)
    sweep["validation_methods"]["no_runner_hooks"] = False
    sweep["validation_methods"]["monte_carlo"]["computation_deferred"] = False
    _write_json(sweep_plans_dir / "SWEEP-PLAN-0001.sweep_plan.json", sweep)

    errors = _validate(tmp_path)
    assert any("no_runner_hooks" in error for error in errors)
    assert any("computation_deferred" in error for error in errors)


def test_result_capture_winner_only_retention_posture_fails(tmp_path):
    _, _, sweep, _, _, sweep_plans_dir = _write_valid_fixture(tmp_path)
    sweep["result_capture_expectations"]["winner_only_retention_forbidden"] = False
    _write_json(sweep_plans_dir / "SWEEP-PLAN-0001.sweep_plan.json", sweep)

    assert any("winner_only_retention_forbidden" in error for error in _validate(tmp_path))


def test_forbidden_executable_key_fails(tmp_path):
    _, manifest, _, _, variant_manifests_dir, _ = _write_valid_fixture(tmp_path)
    manifest["code"] = "print('unsafe')"
    _write_json(variant_manifests_dir / "VM-0001.variant_manifest.json", manifest)

    errors = _validate(tmp_path)

    assert errors
    assert any("Additional properties are not allowed" in error for error in errors)


def test_non_authority_flag_false_fails(tmp_path):
    _, manifest, _, _, variant_manifests_dir, _ = _write_valid_fixture(tmp_path)
    manifest["non_execution_declaration"]["not_runtime_authority"] = False
    _write_json(variant_manifests_dir / "VM-0001.variant_manifest.json", manifest)

    assert any("not_runtime_authority" in error for error in _validate(tmp_path))


def test_cli_returns_success_for_clean_temp_fixtures(tmp_path, monkeypatch):
    _write_valid_fixture(tmp_path)
    strategy_specs_dir, variant_manifests_dir, sweep_plans_dir = _fixture_paths(tmp_path)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "validate_variant_sweep_artifacts",
            "--variant-manifests-dir",
            str(variant_manifests_dir),
            "--sweep-plans-dir",
            str(sweep_plans_dir),
            "--strategy-specs-dir",
            str(strategy_specs_dir),
        ],
    )

    assert main() == 0


def test_cli_returns_failure_for_invalid_temp_fixtures(tmp_path, monkeypatch):
    _, manifest, _, _, variant_manifests_dir, _ = _write_valid_fixture(tmp_path)
    manifest["manifest_hash_pinning"]["manifest_hash"] = "sha256:" + "6" * 64
    _write_json(variant_manifests_dir / "VM-0001.variant_manifest.json", manifest)
    strategy_specs_dir, _, sweep_plans_dir = _fixture_paths(tmp_path)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "validate_variant_sweep_artifacts",
            "--variant-manifests-dir",
            str(variant_manifests_dir),
            "--sweep-plans-dir",
            str(sweep_plans_dir),
            "--strategy-specs-dir",
            str(strategy_specs_dir),
        ],
    )

    assert main() == 1
