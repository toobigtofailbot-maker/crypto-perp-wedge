"""Repo-native draft VM/Sweep authoring pilot from an explicit parameter space."""

from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
import math
import re
import sys
from pathlib import Path
from typing import Any

from tools.registry.validate_strategy_specs import validate_strategy_specs
from tools.registry.validate_variant_sweep_artifacts import (
    _hash_scope_payload,
    sha256_prefixed,
    validate_variant_sweep_artifacts,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
PACKAGE_ID = "EXT-WORKFLOW-HYPEROPT-PILOT-01"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "scratch" / PACKAGE_ID
DEFAULT_PARAMETER_SPACE_PATH = DEFAULT_OUTPUT_DIR / "parameter_space.json"
DEFAULT_SOURCE_STRATEGY_SPEC = (
    REPO_ROOT / "research" / "strategy_specs" / "STRAT-SPEC-0003.strategy_spec.json"
)
GENERATION_TIMESTAMP = "2026-06-19T00:00:00Z"
MAX_AXES = 5
MAX_VARIANTS = 500

NON_CANONICAL_LABELS = [
    "DRAFT WORKFLOW PILOT OUTPUT",
    "NOT CANONICAL RESULT POPULATION",
    "NOT STRATEGY / VM / SWEEP AUTHORITY UNLESS VALIDATED AND EXPLICITLY ADOPTED",
    "NOT CANDIDATE EVIDENCE AUTHORITY",
    "NOT SCREEN-GATE AUTHORITY",
    "NOT PROMOTION / READINESS AUTHORITY",
    "NOT PAPER / LIVE / RUNTIME AUTHORITY",
]


class WorkflowHyperoptPilotError(RuntimeError):
    """Raised when the workflow pilot cannot generate safely."""


def _load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise WorkflowHyperoptPilotError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise WorkflowHyperoptPilotError(f"JSON root must be an object: {path}")
    return payload


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def _sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _sha256_payload(payload: Any) -> str:
    data = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode(
        "utf-8"
    )
    return _sha256_bytes(data)


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _portable_report_path(path: Path | None) -> str | None:
    if path is None:
        return None
    resolved = path.resolve()
    try:
        return resolved.relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return f"external:{path.name}"


def _true_flags(*names: str) -> dict[str, bool]:
    return {name: True for name in names}


def default_parameter_space() -> dict[str, Any]:
    return {
        "package_id": PACKAGE_ID,
        "materialization_kind": "repo_native_vm_sweep_parameter_space_v1",
        "source_strategy_spec_ref": "research/strategy_specs/STRAT-SPEC-0003.strategy_spec.json",
        "generated_strategy_spec_id": "STRAT-SPEC-9001",
        "generated_variant_manifest_id": "VM-9001",
        "generated_sweep_plan_id": "SWEEP-PLAN-9001",
        "search_family_id": "SF-EXT-WORKFLOW-HYPEROPT-PILOT-9001",
        "created_at": GENERATION_TIMESTAMP,
        "axis_order": [
            "center_lookback_bars",
            "vol_lookback_bars",
            "trend_lookback_bars",
        ],
        "parameters": [
            {
                "name": "center_lookback_bars",
                "type": "integer",
                "units": "bars",
                "values": [50, 60, 70, 80, 90, 100],
                "description": "SMA centerline lookback draft grid.",
                "rationale": "Dense authoring demo within the source Strategy Spec's declared bounds.",
                "bounds": {"min": 50, "max": 100, "inclusive_min": True, "inclusive_max": True},
            },
            {
                "name": "vol_lookback_bars",
                "type": "integer",
                "units": "bars",
                "values": [30, 35, 40, 45, 50],
                "description": "STDDEV scale lookback draft grid.",
                "rationale": "Dense authoring demo within the source Strategy Spec's declared bounds.",
                "bounds": {"min": 30, "max": 50, "inclusive_min": True, "inclusive_max": True},
            },
            {
                "name": "trend_lookback_bars",
                "type": "integer",
                "units": "bars",
                "values": [100, 125, 150, 175, 200],
                "description": "Trend SMA lookback draft grid.",
                "rationale": "Dense authoring demo within the source Strategy Spec's declared bounds.",
                "bounds": {"min": 100, "max": 200, "inclusive_min": True, "inclusive_max": True},
            },
        ],
        "authority": {
            "scratch_only": True,
            "canonical_strategy_spec_mutation": False,
            "canonical_variant_manifest_mutation": False,
            "canonical_sweep_plan_mutation": False,
            "screen_gate_authority": False,
            "promotion_readiness_authority": False,
            "runtime_authority": False,
        },
    }


def _ensure_default_parameter_space(path: Path) -> None:
    if path.exists():
        return
    if path.resolve() != DEFAULT_PARAMETER_SPACE_PATH.resolve():
        raise WorkflowHyperoptPilotError(f"parameter-space file does not exist: {path}")
    _write_json(path, default_parameter_space())


def _validate_identifier(value: Any, pattern: str, label: str) -> str:
    if not isinstance(value, str) or re.fullmatch(pattern, value) is None:
        raise WorkflowHyperoptPilotError(f"{label} must match {pattern}: {value!r}")
    return value


def _jsonable_key(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _validate_parameter_space(payload: dict[str, Any]) -> dict[str, Any]:
    if payload.get("materialization_kind") != "repo_native_vm_sweep_parameter_space_v1":
        raise WorkflowHyperoptPilotError("unsupported materialization_kind")
    if payload.get("package_id") != PACKAGE_ID:
        raise WorkflowHyperoptPilotError(f"package_id must be {PACKAGE_ID}")

    parameters = payload.get("parameters")
    axis_order = payload.get("axis_order")
    if not isinstance(parameters, list) or not parameters:
        raise WorkflowHyperoptPilotError("parameters must be a non-empty array")
    if len(parameters) > MAX_AXES:
        raise WorkflowHyperoptPilotError(f"parameters exceeds max axis count {MAX_AXES}")
    if not isinstance(axis_order, list) or any(not isinstance(name, str) for name in axis_order):
        raise WorkflowHyperoptPilotError("axis_order must be an array of parameter names")

    by_name: dict[str, dict[str, Any]] = {}
    for parameter in parameters:
        if not isinstance(parameter, dict):
            raise WorkflowHyperoptPilotError("parameters entries must be objects")
        name = parameter.get("name")
        if not isinstance(name, str) or not name or "." in name:
            raise WorkflowHyperoptPilotError("parameter names must be non-empty unambiguous strings")
        if name in by_name:
            raise WorkflowHyperoptPilotError(f"duplicate parameter name: {name}")
        values = parameter.get("values")
        if not isinstance(values, list) or not values:
            raise WorkflowHyperoptPilotError(f"parameter {name} values must be a non-empty array")
        seen_values: set[str] = set()
        for value in values:
            key = _jsonable_key(value)
            if key in seen_values:
                raise WorkflowHyperoptPilotError(f"parameter {name} contains duplicate values")
            seen_values.add(key)
            _validate_value_type(name, parameter.get("type"), value)
            _validate_value_bounds(name, parameter.get("bounds"), value)
        by_name[name] = parameter

    if tuple(axis_order) != tuple(by_name):
        if set(axis_order) != set(by_name):
            raise WorkflowHyperoptPilotError("axis_order must contain exactly the parameter names")
        ordered_parameters = [by_name[name] for name in axis_order]
    else:
        ordered_parameters = parameters

    count = math.prod(len(parameter["values"]) for parameter in ordered_parameters)
    if count <= 0:
        raise WorkflowHyperoptPilotError("parameter grid must contain at least one point")
    if count > MAX_VARIANTS:
        raise WorkflowHyperoptPilotError(f"parameter grid exceeds max variant count {MAX_VARIANTS}")

    normalized = copy.deepcopy(payload)
    normalized["parameters"] = ordered_parameters
    normalized["generated_strategy_spec_id"] = _validate_identifier(
        payload.get("generated_strategy_spec_id"),
        r"STRAT-SPEC-[0-9]{4}",
        "generated_strategy_spec_id",
    )
    normalized["generated_variant_manifest_id"] = _validate_identifier(
        payload.get("generated_variant_manifest_id"),
        r"VM-[0-9]{4}",
        "generated_variant_manifest_id",
    )
    normalized["generated_sweep_plan_id"] = _validate_identifier(
        payload.get("generated_sweep_plan_id"),
        r"SWEEP-PLAN-[0-9]{4}",
        "generated_sweep_plan_id",
    )
    if not isinstance(payload.get("search_family_id"), str) or not payload["search_family_id"]:
        raise WorkflowHyperoptPilotError("search_family_id must be a non-empty string")
    return normalized


def _validate_value_type(name: str, parameter_type: Any, value: Any) -> None:
    if parameter_type == "integer" and (isinstance(value, bool) or not isinstance(value, int)):
        raise WorkflowHyperoptPilotError(f"parameter {name} values must be integers")
    if parameter_type == "number" and (
        isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value)
    ):
        raise WorkflowHyperoptPilotError(f"parameter {name} values must be finite numbers")
    if parameter_type == "boolean" and not isinstance(value, bool):
        raise WorkflowHyperoptPilotError(f"parameter {name} values must be booleans")
    if parameter_type == "enum" and not isinstance(value, str):
        raise WorkflowHyperoptPilotError(f"parameter {name} values must be strings")
    if parameter_type not in {"integer", "number", "boolean", "enum"}:
        raise WorkflowHyperoptPilotError(f"parameter {name} has unsupported type {parameter_type!r}")


def _validate_value_bounds(name: str, bounds: Any, value: Any) -> None:
    if not isinstance(bounds, dict) or not isinstance(value, (int, float)) or isinstance(value, bool):
        return
    minimum = bounds.get("min")
    maximum = bounds.get("max")
    if minimum is not None:
        if bounds.get("inclusive_min", True) and value < minimum:
            raise WorkflowHyperoptPilotError(f"parameter {name} value {value!r} below min")
        if not bounds.get("inclusive_min", True) and value <= minimum:
            raise WorkflowHyperoptPilotError(f"parameter {name} value {value!r} below/equal min")
    if maximum is not None:
        if bounds.get("inclusive_max", True) and value > maximum:
            raise WorkflowHyperoptPilotError(f"parameter {name} value {value!r} above max")
        if not bounds.get("inclusive_max", True) and value >= maximum:
            raise WorkflowHyperoptPilotError(f"parameter {name} value {value!r} above/equal max")


def _source_spec_path(parameter_space: dict[str, Any]) -> Path:
    ref = parameter_space.get("source_strategy_spec_ref")
    if not isinstance(ref, str) or not ref:
        raise WorkflowHyperoptPilotError("source_strategy_spec_ref must be a non-empty repo path")
    if re.match(r"^[A-Za-z]:[\\/]", ref) or ref.startswith(("/", "\\")) or ".." in ref.replace("\\", "/").split("/"):
        raise WorkflowHyperoptPilotError("source_strategy_spec_ref must be repo-relative")
    path = REPO_ROOT / ref
    if not path.exists():
        raise WorkflowHyperoptPilotError(f"source Strategy Spec not found: {ref}")
    return path


def _parameter_step(values: list[Any]) -> Any:
    if len(values) < 2 or not all(isinstance(value, (int, float)) for value in values):
        return None
    ordered = sorted(values)
    diffs = [ordered[index + 1] - ordered[index] for index in range(len(ordered) - 1)]
    return min(diffs) if diffs else None


def _parameter_range(parameter: dict[str, Any]) -> dict[str, Any] | None:
    values = parameter["values"]
    if not all(isinstance(value, (int, float)) for value in values):
        return None
    bounds = parameter.get("bounds") if isinstance(parameter.get("bounds"), dict) else {}
    return {
        "min": min(values) if bounds.get("min") is None else bounds["min"],
        "max": max(values) if bounds.get("max") is None else bounds["max"],
        "step": _parameter_step(values),
        "inclusive_min": bool(bounds.get("inclusive_min", True)),
        "inclusive_max": bool(bounds.get("inclusive_max", True)),
    }


def _update_parent_strategy_spec(
    source_spec: dict[str, Any],
    source_path: Path,
    parameter_space: dict[str, Any],
) -> dict[str, Any]:
    parent = copy.deepcopy(source_spec)
    parent["strategy_spec_id"] = parameter_space["generated_strategy_spec_id"]
    parent["title"] = "Scratch Workflow Pilot Parent Strategy Spec Snapshot"
    parent["short_name"] = "scratch-workflow-hyperopt-pilot-parent"
    parent["status"] = "approved_for_variant_planning"
    parent["provenance"] = {
        "source_type": "prior_spec",
        "source_refs": [
            _portable_report_path(source_path),
            "docs/status_entries/EXT-WORKFLOW-HYPEROPT-PILOT-01.md",
        ],
        "prepared_by": "Codex",
        "created_at": GENERATION_TIMESTAMP,
        "updated_at": GENERATION_TIMESTAMP,
        "rationale": (
            "Scratch-only parent snapshot for validator-backed large-grid VM/Sweep "
            "authoring. This snapshot does not mutate or supersede the source Strategy Spec."
        ),
        "source_constraints": NON_CANONICAL_LABELS,
        "unresolved_claims": [
            "Scratch artifacts require explicit future adoption before any canonical use."
        ],
    }
    parameter_by_name = {
        parameter["name"]: parameter
        for parameter in parameter_space["parameters"]
        if isinstance(parameter.get("name"), str)
    }
    free_parameters = parent.get("free_parameters", {})
    source_parameters = free_parameters.get("parameters", [])
    updated_parameters: list[dict[str, Any]] = []
    for source_parameter in source_parameters:
        if not isinstance(source_parameter, dict):
            continue
        parameter_name = source_parameter.get("name")
        if parameter_name not in parameter_by_name:
            continue
        parameter_spec = parameter_by_name[parameter_name]
        updated = copy.deepcopy(source_parameter)
        updated["default"] = parameter_spec["values"][0]
        updated["range"] = _parameter_range(parameter_spec)
        updated["allowed_values"] = parameter_spec["values"]
        updated["included_in_variant_generation"] = True
        updated["rationale"] = parameter_spec.get("rationale") or updated.get("rationale")
        updated_parameters.append(updated)
    missing = set(parameter_by_name) - {parameter.get("name") for parameter in updated_parameters}
    if missing:
        raise WorkflowHyperoptPilotError(
            "parameter-space names missing from source Strategy Spec free_parameters: "
            + ", ".join(sorted(missing))
        )
    free_parameters["parameters"] = updated_parameters
    free_parameters["no_free_parameters_declared"] = False
    parent["free_parameters"] = free_parameters
    parent["pre_registration_support"] = {
        "intended_for_variant_manifest": True,
        "variant_manifest_ref": parameter_space["generated_variant_manifest_id"],
        "frozen_snapshot_ref": None,
    }
    parent["lineage"] = {
        "parent_refs": [
            {
                "ref_type": "prior_strategy_spec",
                "ref_id": source_spec.get("strategy_spec_id"),
                "ref_path": _portable_report_path(source_path),
                "ref_hash": _sha256_payload(source_spec),
            }
        ],
        "supersedes": [],
        "amendment_of": None,
    }
    parent["hash_pinning"] = {
        "canonical_spec_hash": None,
        "hash_algorithm": None,
        "hash_scope_version": None,
        "hash_scope": [],
        "hash_status": "not_computed",
    }
    return parent


def _expand_grid(parameter_space: dict[str, Any]) -> list[dict[str, Any]]:
    names = [parameter["name"] for parameter in parameter_space["parameters"]]
    values = [parameter["values"] for parameter in parameter_space["parameters"]]
    rows = []
    for combination in itertools.product(*values):
        rows.append(dict(zip(names, combination, strict=True)))
    return rows


def _build_parameter_axes(parameter_space: dict[str, Any]) -> list[dict[str, Any]]:
    axes: list[dict[str, Any]] = []
    for index, parameter in enumerate(parameter_space["parameters"], start=1):
        name = parameter["name"]
        axes.append(
            {
                "axis_id": f"AXIS-{index:03d}",
                "parameter_name": name,
                "parent_strategy_spec_parameter_ref": f"free_parameters.parameters.{name}",
                "parameter_type": parameter["type"],
                "units": parameter.get("units"),
                "axis_kind": "free_parameter",
                "generator_method": "manual_grid",
                "allowed_values": parameter["values"],
                "range": _parameter_range(parameter),
                "counts_toward_parent_free_parameter_cap": True,
                "is_declared_in_parent_strategy_spec": True,
                "invalid_combination_rule_refs": [],
                "notes": parameter.get("description"),
            }
        )
    return axes


def _build_variant_assignments(parameter_space: dict[str, Any]) -> list[dict[str, Any]]:
    axis_refs = [f"AXIS-{index:03d}" for index, _ in enumerate(parameter_space["parameters"], start=1)]
    assignments: list[dict[str, Any]] = []
    for index, parameter_values in enumerate(_expand_grid(parameter_space), start=1):
        assignments.append(
            {
                "variant_id": f"VAR-{index:06d}",
                "assignment_status": "included",
                "parameter_values": parameter_values,
                "parameter_value_hash": sha256_prefixed(parameter_values),
                "axis_refs": axis_refs,
                "exclusion_rule_refs": [],
                "invalid_combination_rule_refs": [],
                "status_reason": None,
                "lineage": {
                    "generated_by_rule": "repo-native-workflow-pilot-manual-grid",
                    "generation_order": index,
                },
            }
        )
    return assignments


def _build_variant_manifest(
    parameter_space: dict[str, Any],
    parent_spec: dict[str, Any],
    parent_spec_path: Path,
) -> dict[str, Any]:
    assignments = _build_variant_assignments(parameter_space)
    variant_count = len(assignments)
    strategy_hash = _sha256_payload(parent_spec)
    payload: dict[str, Any] = {
        "schema_version": "v1",
        "variant_manifest_id": parameter_space["generated_variant_manifest_id"],
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
            "strategy_spec_id": parent_spec["strategy_spec_id"],
            "strategy_spec_schema_version": parent_spec["schema_version"],
            "strategy_spec_hash": strategy_hash,
            "hash_algorithm": "sha256",
            "hash_scope_version": "strategy_spec_hash_scope_v1",
            "strategy_spec_review_status": "approved_for_variant_planning",
            "strategy_spec_ref": _portable_report_path(parent_spec_path),
            "mismatch_policy": "block",
            "missing_parent_policy": "block",
            "does_not_mutate_parent_strategy_spec": True,
        },
        "population_governance": {
            "population_cap": {
                "max_variants": variant_count,
                "cap_basis": "manual_grid",
                "cap_source": "human_declared",
                "cap_exception_authorized": False,
                "cap_exception_ref": None,
            },
            "declared_population": {
                "committed_population_count": variant_count,
                "declared_variant_count": variant_count,
                "included_variant_count": variant_count,
                "excluded_variant_count": 0,
                "invalid_variant_count": 0,
                "not_attempted_variant_count": 0,
            },
            "trial_budget": {
                "planned_trial_count": variant_count,
                "trial_budget_denominator": variant_count,
                "denominator_basis": "committed_pre_registered_population_count",
                "denominator_count": variant_count,
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
                "search_family_id": parameter_space["search_family_id"],
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
        "parameter_axes": _build_parameter_axes(parameter_space),
        "invalid_combination_rules": [],
        "exclusion_rules": [],
        "variant_assignments": assignments,
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
            "frozen_at": GENERATION_TIMESTAMP,
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
            "parent_refs": [
                {
                    "ref_type": "strategy_spec",
                    "ref_id": parent_spec["strategy_spec_id"],
                    "ref_path": _portable_report_path(parent_spec_path),
                    "ref_hash": strategy_hash,
                }
            ],
            "source_refs": [
                {
                    "ref_type": "manual_review",
                    "ref_id": PACKAGE_ID,
                    "ref_path": f"docs/status_entries/{PACKAGE_ID}.md",
                    "ref_hash": None,
                }
            ],
            "created_at": GENERATION_TIMESTAMP,
            "updated_at": GENERATION_TIMESTAMP,
            "audit_notes": [
                *NON_CANONICAL_LABELS,
                "Generated from an explicit deterministic Cartesian grid; no adaptive search is used.",
                "Scratch placement prevents this artifact from becoming canonical VM authority.",
            ],
            "hash_refs": [strategy_hash],
        },
        "review": {
            "human_review_required": True,
            "reviewer": None,
            "reviewed_at": None,
            "review_notes": [
                "Scratch workflow pilot artifact only; explicit future adoption is required before canonical use.",
                "No sweep execution, result population write, ranking, gate, or promotion authority is created.",
            ],
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
    if scoped_payload is None:
        raise WorkflowHyperoptPilotError("manifest hash scope contains missing field")
    payload["manifest_hash_pinning"]["manifest_hash"] = sha256_prefixed(scoped_payload)
    payload["lineage"]["hash_refs"].append(payload["manifest_hash_pinning"]["manifest_hash"])
    return payload


def _sweep_data_refs(parent_spec: dict[str, Any]) -> list[dict[str, Any]]:
    refs = parent_spec.get("timeframe_and_data", {}).get("host_data_refs", [])
    if not isinstance(refs, list):
        return []
    return [
        ref
        for ref in copy.deepcopy(refs)
        if isinstance(ref, dict) and ref.get("stream") == "ohlcv"
    ]


def _build_sweep_plan(
    parameter_space: dict[str, Any],
    parent_spec: dict[str, Any],
    parent_spec_path: Path,
    manifest: dict[str, Any],
    manifest_path: Path,
) -> dict[str, Any]:
    variant_ids = [assignment["variant_id"] for assignment in manifest["variant_assignments"]]
    variant_count = len(variant_ids)
    manifest_hash = manifest["manifest_hash_pinning"]["manifest_hash"]
    strategy_hash = manifest["parent_strategy_spec"]["strategy_spec_hash"]
    realism = copy.deepcopy(parent_spec.get("backtest_realism_assumptions", {}))
    realism["declarations_only"] = True
    return {
        "schema_version": "v1",
        "sweep_plan_id": parameter_space["generated_sweep_plan_id"],
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
            "variant_manifest_schema_version": manifest["schema_version"],
            "manifest_hash": manifest_hash,
            "hash_algorithm": "sha256",
            "manifest_population_count": variant_count,
            "manifest_committed_population_count": variant_count,
            "manifest_population_cap": variant_count,
            "manifest_pre_registration_status": "frozen_for_sweep_planning",
            "mismatch_policy": "block",
            "missing_manifest_policy": "block",
            "one_manifest_only": True,
        },
        "test_selection": {
            "selection_mode": "all_manifest_variants",
            "selected_variant_ids": variant_ids,
            "excluded_variant_ids": [],
            "subset_selection_rule": None,
            "declared_before_results": True,
            "post_hoc_addition_forbidden": True,
            "outside_manifest_variants_forbidden": True,
        },
        "validation_methods": {
            "backtest": {"enabled": True, "method_ref": None, "notes": "Planning declaration only."},
            "walk_forward_oos": {
                "enabled": False,
                "method_ref": None,
                "declares_chronological_separation": False,
                "notes": "Not performed by this workflow authoring pilot.",
            },
            "robustness": {
                "enabled": False,
                "method_ref": None,
                "families_declared": [],
                "notes": "Robustness remains separately gated.",
            },
            "dsr_psr_mintrl_accounting": {
                "enabled": True,
                "denominator_ref": "committed_population_count",
                "computation_deferred": True,
                "notes": "Denominator is the full generated scratch population.",
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
            "primary_timeframe": parent_spec["timeframe_and_data"]["primary_timeframe"],
            "confirmation_timeframes": parent_spec["timeframe_and_data"].get(
                "confirmation_timeframes", []
            ),
            "data_refs": _sweep_data_refs(parent_spec),
            "missing_data_posture": "block_if_missing",
            "gap_handling_assumption": parent_spec["timeframe_and_data"].get(
                "gap_handling_assumption"
            ),
        },
        "realism_assumptions": realism,
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
            "committed_population_count": variant_count,
            "selected_variant_count": variant_count,
            "executed_variant_count": 0,
            "successful_variant_count": 0,
            "failed_variant_count": 0,
            "errored_variant_count": 0,
            "aborted_variant_count": 0,
            "filtered_variant_count": 0,
            "data_unavailable_variant_count": 0,
            "excluded_variant_count": 0,
            "not_attempted_variant_count": variant_count,
            "multiple_testing_denominator": variant_count,
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
                "ref_path": _portable_report_path(manifest_path),
                "ref_hash": manifest_hash,
            },
            "parent_strategy_spec_ref": {
                "ref_type": "strategy_spec",
                "ref_id": parent_spec["strategy_spec_id"],
                "ref_path": _portable_report_path(parent_spec_path),
                "ref_hash": strategy_hash,
            },
            "search_family_id": parameter_space["search_family_id"],
            "source_refs": [
                {
                    "ref_type": "manual_review",
                    "ref_id": PACKAGE_ID,
                    "ref_path": f"docs/status_entries/{PACKAGE_ID}.md",
                    "ref_hash": None,
                }
            ],
            "created_at": GENERATION_TIMESTAMP,
            "updated_at": GENERATION_TIMESTAMP,
            "audit_notes": [
                *NON_CANONICAL_LABELS,
                "All generated variants are selected only as a scratch planning denominator.",
                "This plan contains no runner hooks and no computation.",
            ],
        },
        "review": {
            "human_review_required": True,
            "reviewer": None,
            "reviewed_at": None,
            "review_notes": [
                "Scratch workflow pilot artifact only; explicit future adoption is required before canonical use.",
                "No run, result population, ranking, gate, or promotion authority is created.",
            ],
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


def _artifact_paths(output_dir: Path, parameter_space: dict[str, Any]) -> dict[str, Path]:
    return {
        "strategy_spec": output_dir
        / "generated_strategy_specs"
        / f"{parameter_space['generated_strategy_spec_id']}.strategy_spec.json",
        "variant_manifest": output_dir
        / "generated_variant_manifests"
        / f"{parameter_space['generated_variant_manifest_id']}.variant_manifest.json",
        "sweep_plan": output_dir
        / "generated_sweep_plans"
        / f"{parameter_space['generated_sweep_plan_id']}.sweep_plan.json",
        "report_json": output_dir / "workflow_hyperopt_report.json",
        "report_md": output_dir / "workflow_hyperopt_report.md",
        "checksums": output_dir / "generated_artifacts.sha256",
    }


def build_artifacts(
    parameter_space_path: Path = DEFAULT_PARAMETER_SPACE_PATH,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    _ensure_default_parameter_space(parameter_space_path)
    parameter_space = _validate_parameter_space(_load_json(parameter_space_path))
    source_path = _source_spec_path(parameter_space)
    source_spec = _load_json(source_path)
    parent_spec = _update_parent_strategy_spec(source_spec, source_path, parameter_space)
    placeholder_path = DEFAULT_OUTPUT_DIR / "generated_strategy_specs" / (
        f"{parameter_space['generated_strategy_spec_id']}.strategy_spec.json"
    )
    manifest = _build_variant_manifest(parameter_space, parent_spec, placeholder_path)
    manifest_path = DEFAULT_OUTPUT_DIR / "generated_variant_manifests" / (
        f"{parameter_space['generated_variant_manifest_id']}.variant_manifest.json"
    )
    sweep = _build_sweep_plan(parameter_space, parent_spec, placeholder_path, manifest, manifest_path)
    return parameter_space, parent_spec, manifest, sweep


def _validation_summary(paths: dict[str, Path]) -> dict[str, Any]:
    strategy_errors = validate_strategy_specs(strategy_specs_dir=paths["strategy_spec"].parent)
    variant_sweep_errors = validate_variant_sweep_artifacts(
        variant_manifests_dir=paths["variant_manifest"].parent,
        sweep_plans_dir=paths["sweep_plan"].parent,
        strategy_specs_dir=paths["strategy_spec"].parent,
    )
    return {
        "strategy_spec_validator": {
            "command": (
                "python -m tools.registry.validate_strategy_specs "
                f"--strategy-specs-dir {_portable_report_path(paths['strategy_spec'].parent)}"
            ),
            "passed": not strategy_errors,
            "errors": strategy_errors,
        },
        "variant_sweep_validator": {
            "command": (
                "python -m tools.registry.validate_variant_sweep_artifacts "
                f"--variant-manifests-dir {_portable_report_path(paths['variant_manifest'].parent)} "
                f"--sweep-plans-dir {_portable_report_path(paths['sweep_plan'].parent)} "
                f"--strategy-specs-dir {_portable_report_path(paths['strategy_spec'].parent)}"
            ),
            "passed": not variant_sweep_errors,
            "errors": variant_sweep_errors,
        },
    }


def _report(
    parameter_space_path: Path,
    paths: dict[str, Path],
    parameter_space: dict[str, Any],
    parent_spec: dict[str, Any],
    manifest: dict[str, Any],
    sweep: dict[str, Any],
    validation: dict[str, Any],
) -> dict[str, Any]:
    artifact_payload = {
        "parameter_space": parameter_space,
        "strategy_spec": parent_spec,
        "variant_manifest": manifest,
        "sweep_plan": sweep,
    }
    generated_artifacts = {
        "parameter_space": {
            "path": _portable_report_path(parameter_space_path),
            "checksum": _sha256_file(parameter_space_path),
        },
        "strategy_spec": {
            "path": _portable_report_path(paths["strategy_spec"]),
            "checksum": _sha256_file(paths["strategy_spec"]),
        },
        "variant_manifest": {
            "path": _portable_report_path(paths["variant_manifest"]),
            "checksum": _sha256_file(paths["variant_manifest"]),
        },
        "sweep_plan": {
            "path": _portable_report_path(paths["sweep_plan"]),
            "checksum": _sha256_file(paths["sweep_plan"]),
        },
    }
    report: dict[str, Any] = {
        "labels": NON_CANONICAL_LABELS,
        "package_id": PACKAGE_ID,
        "materialization_kind": parameter_space["materialization_kind"],
        "source_strategy_spec_ref": parameter_space["source_strategy_spec_ref"],
        "generated_strategy_spec_id": parent_spec["strategy_spec_id"],
        "generated_variant_manifest_id": manifest["variant_manifest_id"],
        "generated_sweep_plan_id": sweep["sweep_plan_id"],
        "generated_variant_count": len(manifest["variant_assignments"]),
        "axis_order": parameter_space["axis_order"],
        "axis_count": len(parameter_space["parameters"]),
        "deterministic_ordering": "axis_order_then_itertools_product_left_to_right",
        "seed_used": None,
        "generated_artifacts": generated_artifacts,
        "deterministic_artifact_checksum": _sha256_payload(artifact_payload),
        "validator_authority": validation,
        "external_source_posture": {
            "freqtrade_source_inspection": "not_inspected_no_network_needed",
            "qlib_source_inspection": "not_inspected_no_network_needed",
            "repo_native_concepts_only": True,
            "external_dependency_added": False,
            "external_runtime_tool_invoked": False,
        },
        "experiment_tracking_concept": {
            "status": "docs_only_concept_in_report",
            "concept": (
                "Future non-canonical trial indexes could group parameter-space specs, "
                "generated draft artifacts, validator results, and later run evidence by "
                "search_family_id without ranking or promotion authority."
            ),
            "canonical_trial_log_mutated": False,
            "candidate_ranking_authority": False,
        },
        "boundary_statement": {
            "canonical_result_population_write": False,
            "canonical_strategy_spec_mutation": False,
            "canonical_variant_manifest_mutation": False,
            "canonical_sweep_plan_mutation": False,
            "screen_gate_authority_created": False,
            "promotion_readiness_authority_created": False,
            "candidate_evidence_authority_created": False,
            "runner_backtester_changed": False,
            "runtime_paper_live_touched": False,
            "oms_risk_reconciliation_credentials_order_paths_touched": False,
        },
        "decision_recommendation": "ADOPT_AS_WORKFLOW_ACCELERATOR",
        "broader_adoption_taxonomy": "adopt",
        "next_gated_wp_suggestion": (
            "Narrow design for promoting scratch-generated draft VM/Sweep artifacts into "
            "canonical pre-registration only after explicit human ID assignment and validator gates."
        ),
    }
    report["output_checksum"] = _sha256_payload(report)
    return report


def _markdown_report(report: dict[str, Any]) -> str:
    lines = [
        f"# {PACKAGE_ID} Scratch Workflow Hyperopt Report",
        "",
        *[f"- {label}" for label in NON_CANONICAL_LABELS],
        "",
        f"Recommendation: `{report['decision_recommendation']}`",
        f"Generated variants: `{report['generated_variant_count']}`",
        f"Deterministic checksum: `{report['deterministic_artifact_checksum']}`",
        f"Output checksum: `{report['output_checksum']}`",
        "",
        "## Generated Artifacts",
        "",
    ]
    for name, artifact in report["generated_artifacts"].items():
        lines.append(f"- {name}: `{artifact['path']}` / `{artifact['checksum']}`")
    lines.extend(
        [
            "",
            "## Validator Authority",
            "",
        ]
    )
    for name, validator in report["validator_authority"].items():
        lines.append(f"- {name}: `{'PASS' if validator['passed'] else 'FAIL'}`")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- Scratch-only Strategy Spec snapshot, Variant Manifest, and Sweep Plan artifacts.",
            "- No canonical Strategy Spec, Variant Manifest, Sweep Plan, Result Population, trial log, runner, backtester, runtime, paper, or live path is changed.",
            "- No optimizer, ranking, screen-gate, promotion, readiness, or candidate-evidence authority is created.",
            "",
        ]
    )
    return "\n".join(lines)


def run_pilot(
    *,
    parameter_space_path: Path = DEFAULT_PARAMETER_SPACE_PATH,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
) -> dict[str, Any]:
    _ensure_default_parameter_space(parameter_space_path)
    parameter_space, parent_spec, manifest, sweep = build_artifacts(parameter_space_path)
    paths = _artifact_paths(output_dir, parameter_space)
    paths["strategy_spec"].parent.mkdir(parents=True, exist_ok=True)
    paths["variant_manifest"].parent.mkdir(parents=True, exist_ok=True)
    paths["sweep_plan"].parent.mkdir(parents=True, exist_ok=True)

    # Rebuild path-bearing payloads when output_dir is caller-provided.
    manifest = _build_variant_manifest(parameter_space, parent_spec, paths["strategy_spec"])
    sweep = _build_sweep_plan(parameter_space, parent_spec, paths["strategy_spec"], manifest, paths["variant_manifest"])

    _write_json(paths["strategy_spec"], parent_spec)
    _write_json(paths["variant_manifest"], manifest)
    _write_json(paths["sweep_plan"], sweep)
    validation = _validation_summary(paths)
    report = _report(
        parameter_space_path,
        paths,
        parameter_space,
        parent_spec,
        manifest,
        sweep,
        validation,
    )
    _write_json(paths["report_json"], report)
    paths["report_md"].write_text(_markdown_report(report), encoding="utf-8")
    paths["checksums"].write_text(
        "\n".join(
            f"{artifact['checksum']}  {artifact['path']}"
            for artifact in report["generated_artifacts"].values()
        )
        + "\n",
        encoding="utf-8",
    )
    return report


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parameter-space", type=Path, default=DEFAULT_PARAMETER_SPACE_PATH)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        report = run_pilot(parameter_space_path=args.parameter_space, output_dir=args.output_dir)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(
        json.dumps(
            {
                "package_id": PACKAGE_ID,
                "generated_variant_count": report["generated_variant_count"],
                "generated_variant_manifest_id": report["generated_variant_manifest_id"],
                "generated_sweep_plan_id": report["generated_sweep_plan_id"],
                "deterministic_artifact_checksum": report["deterministic_artifact_checksum"],
                "strategy_spec_validator_passed": report["validator_authority"][
                    "strategy_spec_validator"
                ]["passed"],
                "variant_sweep_validator_passed": report["validator_authority"][
                    "variant_sweep_validator"
                ]["passed"],
                "recommendation": report["decision_recommendation"],
                "output_checksum": report["output_checksum"],
                "output_dir": _portable_report_path(args.output_dir),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
