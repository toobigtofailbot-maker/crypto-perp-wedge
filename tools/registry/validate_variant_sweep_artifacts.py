"""Validate non-executing variant manifest and sweep plan JSON artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
from decimal import Decimal
from pathlib import Path
from typing import Any

from jsonschema import Draft7Validator


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_VARIANT_MANIFESTS_DIR = REPO_ROOT / "research" / "variant_manifests"
DEFAULT_SWEEP_PLANS_DIR = REPO_ROOT / "research" / "sweep_plans"
DEFAULT_STRATEGY_SPECS_DIR = REPO_ROOT / "research" / "strategy_specs"
DEFAULT_VARIANT_MANIFEST_SCHEMA_PATH = (
    REPO_ROOT / "research" / "schemas" / "variant_manifest.schema.json"
)
DEFAULT_SWEEP_PLAN_SCHEMA_PATH = REPO_ROOT / "research" / "schemas" / "sweep_plan.schema.json"
DEFAULT_STRATEGY_SPEC_SCHEMA_PATH = (
    REPO_ROOT / "research" / "schemas" / "strategy_spec.schema.json"
)
HASH_ALGORITHM = "sha256"
VARIANT_MANIFEST_HASH_SCOPE_VERSION = "variant_manifest_hash_scope_v1"
MAX_PARAMETER_AXES = 5
VALUE_PARAMETER_REF_KEY = "parameter_ref"
FORBIDDEN_EXECUTABLE_KEYS = {
    "expression",
    "formula",
    "code",
    "script",
    "eval",
    "function",
    "callback",
    "lambda",
    "sql",
    "shell",
    "python",
    "javascript",
    "url",
    "file_path",
    "command",
    "runtime_action",
    "order_instruction",
    "broker_instruction",
    "exchange_instruction",
    "live_action",
    "paper_action",
    "readiness_update",
    "transition_trigger",
    "approval_action",
    "ranking_score",
    "recommendation",
    "runner_command",
    "sweep_execution",
    "result_computation",
}
NON_EXECUTION_TRUE_FLAGS = {
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
}
REVIEW_NON_AUTHORITY_TRUE_FLAGS = {
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
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def sha256_prefixed(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def _format_schema_error(error: Any) -> str:
    location = ".".join(str(part) for part in error.absolute_path)
    if location:
        return f"{location}: {error.message}"
    return error.message


def _validate_json_file(
    path: Path,
    validator: Draft7Validator,
) -> tuple[dict[str, Any] | None, list[str]]:
    try:
        payload = load_json(path)
    except json.JSONDecodeError as exc:
        return None, [f"{path}: invalid JSON: {exc}"]

    errors = [
        f"{path}: {_format_schema_error(schema_error)}"
        for schema_error in sorted(validator.iter_errors(payload), key=lambda err: list(err.path))
    ]
    return payload, errors


def _path_label(parts: list[str]) -> str:
    return ".".join(parts)


def _get_path(payload: dict[str, Any], dotted_path: str) -> tuple[bool, Any]:
    current: Any = payload
    for part in dotted_path.split("."):
        if not isinstance(current, dict) or part not in current:
            return False, None
        current = current[part]
    return True, current


def _hash_scope_payload(payload: dict[str, Any], scope: list[Any]) -> dict[str, Any] | None:
    scoped: dict[str, Any] = {}
    for raw_path in scope:
        if not isinstance(raw_path, str):
            return None
        found, value = _get_path(payload, raw_path)
        if not found:
            return None
        scoped[raw_path] = value
    return scoped


def _walk_keys(value: Any, path_parts: list[str]) -> list[tuple[str, str]]:
    keys: list[tuple[str, str]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            key_path = _path_label([*path_parts, str(key)])
            keys.append((key_path, str(key)))
            keys.extend(_walk_keys(child, [*path_parts, str(key)]))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            keys.extend(_walk_keys(child, [*path_parts, str(index)]))
    return keys


def _validate_forbidden_keys(path: Path, payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for key_path, key in _walk_keys(payload, []):
        if key.lower() in FORBIDDEN_EXECUTABLE_KEYS:
            errors.append(f"{path}: forbidden executable key name at {key_path}: {key}")
    return errors


def _validate_true_flags(
    path: Path,
    payload: dict[str, Any],
    object_path: str,
    required_flags: set[str],
) -> list[str]:
    current: Any = payload
    for part in object_path.split("."):
        if not isinstance(current, dict):
            return [f"{path}: {object_path} must be present as an object"]
        current = current.get(part)
    if not isinstance(current, dict):
        return [f"{path}: {object_path} must be present as an object"]

    return [
        f"{path}: {object_path}.{flag} must be true"
        for flag in sorted(required_flags)
        if current.get(flag) is not True
    ]


def _validate_non_authority_flags(path: Path, payload: dict[str, Any]) -> list[str]:
    errors = _validate_true_flags(
        path,
        payload,
        "non_execution_declaration",
        NON_EXECUTION_TRUE_FLAGS,
    )
    errors.extend(
        _validate_true_flags(
            path,
            payload,
            "review.non_authority_acknowledgement",
            REVIEW_NON_AUTHORITY_TRUE_FLAGS,
        )
    )
    return errors


def _discover_by_id(
    directory: Path,
    pattern: str,
    id_field: str,
    wanted_id: str,
) -> Path | None:
    preferred_suffix = pattern.replace("*", "")
    preferred = directory / f"{wanted_id}{preferred_suffix}"
    if preferred.exists():
        return preferred
    if not directory.exists():
        return None
    for path in sorted(directory.rglob(pattern)):
        try:
            payload = load_json(path)
        except (json.JSONDecodeError, OSError):
            continue
        if payload.get(id_field) == wanted_id:
            return path
    return None


def _validate_parent_strategy_spec_hash(
    path: Path,
    payload: dict[str, Any],
    strategy_specs_dir: Path,
) -> list[str]:
    parent = payload.get("parent_strategy_spec")
    if not isinstance(parent, dict):
        return []

    errors: list[str] = []
    strategy_spec_id = parent.get("strategy_spec_id")
    declared_hash = parent.get("strategy_spec_hash")
    if parent.get("mismatch_policy") != "block":
        errors.append(f"{path}: parent_strategy_spec.mismatch_policy must be 'block'")
    if parent.get("missing_parent_policy") != "block":
        errors.append(f"{path}: parent_strategy_spec.missing_parent_policy must be 'block'")

    if not isinstance(strategy_spec_id, str) or not strategy_specs_dir.exists():
        return errors

    parent_path = _discover_by_id(
        strategy_specs_dir,
        "*.strategy_spec.json",
        "strategy_spec_id",
        strategy_spec_id,
    )
    if parent_path is None:
        if parent.get("missing_parent_policy") == "block":
            errors.append(
                f"{path}: parent Strategy Spec {strategy_spec_id} missing under "
                f"{strategy_specs_dir}"
            )
        return errors

    try:
        parent_payload = load_json(parent_path)
    except json.JSONDecodeError as exc:
        errors.append(f"{parent_path}: invalid JSON: {exc}")
        return errors

    if parent_payload.get("strategy_spec_id") != strategy_spec_id:
        errors.append(
            f"{path}: parent Strategy Spec file {parent_path} has mismatched "
            f"strategy_spec_id {parent_payload.get('strategy_spec_id')!r}"
        )
        return errors

    computed_hash = sha256_prefixed(parent_payload)
    if computed_hash != declared_hash:
        errors.append(
            f"{path}: parent_strategy_spec.strategy_spec_hash mismatch for "
            f"{strategy_spec_id}: declared {declared_hash!r}, computed {computed_hash}"
        )
    return errors


def _exact_scaled_milli(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    decimal_value = Decimal(value) if isinstance(value, int) else value
    if not isinstance(decimal_value, Decimal) or not decimal_value.is_finite():
        return None
    scaled = decimal_value * 1000
    if scaled != scaled.to_integral_value():
        return None
    return int(scaled)


def _derive_variant_planning_contract_core(
    payload: dict[str, Any],
    *,
    parent_path: str,
    parent_file_sha256: str,
) -> tuple[dict[str, Any] | None, str | None]:
    axes = payload.get("parameter_axes")
    if not isinstance(axes, list) or not axes:
        return None, "external planning approval requires at least one parameter axis"
    ordered_axes: list[dict[str, Any]] = []
    for index, axis in enumerate(axes):
        if not isinstance(axis, dict):
            return None, f"parameter_axes.{index} must be an object"
        name = axis.get("parameter_name")
        values = axis.get("allowed_values")
        parameter_type = axis.get("parameter_type")
        if not isinstance(name, str) or not isinstance(values, list) or not values:
            return None, f"parameter_axes.{index} lacks an exact name/value set"
        if parameter_type == "integer":
            if any(not isinstance(value, int) or isinstance(value, bool) for value in values):
                return None, f"parameter_axes.{index} integer values are not exact JSON integers"
            ordered_axes.append({"name": name, "integer_values": values})
        elif parameter_type == "number":
            scaled = [_exact_scaled_milli(value) for value in values]
            if any(value is None for value in scaled):
                return None, f"parameter_axes.{index} number values are not exact to milli scale"
            ordered_axes.append({"name": name, "milli_values": scaled})
        else:
            return None, f"parameter_axes.{index} has unsupported external-approval type {parameter_type!r}"

    parent = payload.get("parent_strategy_spec", {})
    governance = payload.get("population_governance", {})
    cap = governance.get("population_cap", {})
    declared = governance.get("declared_population", {})
    trial_budget = governance.get("trial_budget", {})
    multiple_testing = governance.get("multiple_testing_accounting", {})
    preregistration = governance.get("pre_registration", {})
    vm_id = payload.get("variant_manifest_id")
    core = {
        "strategy_spec_id": parent.get("strategy_spec_id"),
        "strategy_spec_path": parent_path,
        "strategy_spec_sha256": parent_file_sha256,
        "variant_manifest_id": vm_id,
        "variant_manifest_path": f"research/variant_manifests/{vm_id}.variant_manifest.json",
        "search_family_id": multiple_testing.get("search_family_id"),
        "ordered_parameter_axes": ordered_axes,
        "population_cap": cap.get("max_variants"),
        "committed_population_count": declared.get("committed_population_count"),
        "denominator_basis": trial_budget.get("denominator_basis"),
        "adaptive_search": multiple_testing.get("adaptive_search_used"),
        "post_hoc_mutation_forbidden": preregistration.get("post_result_mutation_forbidden"),
        "authority": "one_bounded_variant_manifest_preparation_only",
    }
    return core, None


def _validate_variant_planning_approval(
    path: Path,
    payload: dict[str, Any],
    strategy_specs_dir: Path,
    repo_root: Path,
) -> list[str]:
    parent = payload.get("parent_strategy_spec")
    if not isinstance(parent, dict):
        return []
    spec_id = parent.get("strategy_spec_id")
    if not isinstance(spec_id, str):
        return []
    parent_path = _discover_by_id(
        strategy_specs_dir, "*.strategy_spec.json", "strategy_spec_id", spec_id
    )
    if parent_path is None:
        return []
    try:
        parent_payload = load_json(parent_path)
        parent_raw = parent_path.read_bytes()
    except (json.JSONDecodeError, OSError):
        return []

    evidence = payload.get("variant_planning_approval")
    root = repo_root.resolve()
    authoritative_vm = root / "research" / "variant_manifests" / path.name
    authoritative_match = False
    if authoritative_vm.is_file() and not authoritative_vm.is_symlink():
        try:
            authoritative_match = load_json(authoritative_vm) == payload
        except (json.JSONDecodeError, OSError):
            authoritative_match = False
    if not authoritative_match and evidence is None:
        # Workbench/scratch copies carry no canonical authority. Preserve their
        # existing structural validation while reserving approval semantics for
        # the authoritative VM corpus and exact copies replayed against it.
        return []
    status = parent_payload.get("status")
    review_scope = parent_payload.get("review", {}).get("approval_scope")
    if status == "approved_for_variant_planning":
        errors = []
        if review_scope != "variant_planning_only":
            errors.append(
                f"{path}: embedded-approved parent requires review.approval_scope='variant_planning_only'"
            )
        if evidence is not None:
            errors.append(
                f"{path}: embedded-approved parent must not include external variant-planning approval evidence"
            )
        return errors
    if status != "review_requested":
        return [
            f"{path}: parent status {status!r} cannot support the literal approved_for_variant_planning claim"
        ]
    if not isinstance(evidence, dict):
        return [
            f"{path}: review_requested parent requires external variant-planning approval evidence"
        ]

    errors: list[str] = []
    try:
        from tools.canon_intake import variant_planning_approval as approval_contract

        approval_id = evidence.get("approval_id")
        expected_rel = (
            approval_contract.APPROVAL_ROOT
            / f"{approval_id}.variant_planning_approval.json"
        ).as_posix()
        if evidence.get("path") != expected_rel:
            raise approval_contract.VariantPlanningApprovalError(
                "VM approval path is not authoritative and ID-derived"
            )
        approval_path = approval_contract._repo_path(
            root, evidence.get("path"), "VM variant-planning approval path"
        )
        expected_path = root.joinpath(*approval_contract.APPROVAL_ROOT.parts) / (
            f"{approval_id}.variant_planning_approval.json"
        )
        if approval_path != expected_path:
            raise approval_contract.VariantPlanningApprovalError(
                "VM approval file is outside the authoritative approval directory"
            )
        bundle = approval_contract._validate_approval_file(
            root, approval_path, "VM variant-planning approval"
        )
        if bundle["approval_id"] != approval_id:
            raise approval_contract.VariantPlanningApprovalError("VM approval ID mismatch")
        approval_file_sha256 = "sha256:" + hashlib.sha256(bundle["approval_raw"]).hexdigest()
        if evidence.get("sha256") != approval_file_sha256:
            raise approval_contract.VariantPlanningApprovalError("VM approval whole-file hash mismatch")
        if evidence.get("contract_core_sha256") != bundle["approval"].get(
            "contract_core_sha256"
        ):
            raise approval_contract.VariantPlanningApprovalError("VM approval contract-core hash mismatch")
        if evidence.get("evidence_mode") != "external_append_only_approval":
            raise approval_contract.VariantPlanningApprovalError("VM approval evidence mode mismatch")

        canonical_parent_rel = f"research/strategy_specs/{spec_id}.strategy_spec.json"
        if parent.get("strategy_spec_ref") != canonical_parent_rel:
            raise approval_contract.VariantPlanningApprovalError(
                "external VM parent Strategy Spec reference is not canonical"
            )
        if bundle["approval"]["canonical_parent"]["path"] != canonical_parent_rel:
            raise approval_contract.VariantPlanningApprovalError(
                "approval parent path does not match the VM parent"
            )

        if path.name != f"{payload.get('variant_manifest_id')}.variant_manifest.json":
            raise approval_contract.VariantPlanningApprovalError(
                "external VM filename is not derived from its identifier"
            )
        if not authoritative_vm.is_file() or authoritative_vm.is_symlink():
            raise approval_contract.VariantPlanningApprovalError(
                "external VM must exist at its authoritative non-symlink path"
            )
        authoritative_payload = load_json(authoritative_vm)
        if authoritative_payload != payload:
            raise approval_contract.VariantPlanningApprovalError(
                "validated VM bytes do not match the authoritative VM"
            )
        exact_payload = json.loads(
            authoritative_vm.read_text(encoding="utf-8"), parse_float=Decimal
        )
        derived_core, derivation_error = _derive_variant_planning_contract_core(
            exact_payload,
            parent_path=canonical_parent_rel,
            parent_file_sha256="sha256:" + hashlib.sha256(parent_raw).hexdigest(),
        )
        if derivation_error:
            raise approval_contract.VariantPlanningApprovalError(derivation_error)
        if derived_core != bundle["approval"].get("variant_manifest_contract_core"):
            raise approval_contract.VariantPlanningApprovalError(
                "VM-derived planning contract core does not exactly match the approval"
            )
        if approval_contract.contract_core_sha256(derived_core) != evidence.get(
            "contract_core_sha256"
        ):
            raise approval_contract.VariantPlanningApprovalError(
                "VM-derived planning contract-core hash mismatch"
            )

        audit_path = approval_contract._repo_path(
            root, approval_contract.AUDIT_PATH.as_posix(), "variant-planning audit path"
        )
        historical = approval_contract._read_historical_audit(root, audit_path)
        approvals = approval_contract._scan_approval_corpus(root)
        approval_contract._validate_history_alignment(historical, approvals)
        matches = [record for record in historical if record.get("approval_id") == approval_id]
        if len(matches) != 1 or matches[0] != bundle["record"]:
            raise approval_contract.VariantPlanningApprovalError(
                "variant-planning audit must contain one unique matching approval record"
            )
        approval_matches = [item for item in approvals if item["approval_id"] == approval_id]
        if len(approval_matches) != 1:
            raise approval_contract.VariantPlanningApprovalError(
                "authoritative approval corpus must contain one matching approval"
            )
        manifests = approval_contract._scan_variant_manifest_corpus(root)
        vm_rel = f"research/variant_manifests/{payload.get('variant_manifest_id')}.variant_manifest.json"
        family = (
            payload.get("population_governance", {})
            .get("multiple_testing_accounting", {})
            .get("search_family_id")
        )
        vm_matches = [
            item
            for item in manifests
            if item["variant_manifest_id"] == payload.get("variant_manifest_id")
            and item["variant_manifest_path"] == vm_rel
            and item["search_family_id"] == family
        ]
        if len(vm_matches) != 1:
            raise approval_contract.VariantPlanningApprovalError(
                "approval/VM/path/search-family single-use binding is not unique"
            )
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        errors.append(f"{path}: external variant-planning approval invalid: {exc}")
    return errors


def _collect_value_parameter_refs(value: Any) -> set[str]:
    refs: set[str] = set()
    if isinstance(value, dict):
        if set(value) == {VALUE_PARAMETER_REF_KEY} and isinstance(value.get(VALUE_PARAMETER_REF_KEY), str):
            refs.add(value[VALUE_PARAMETER_REF_KEY])
        if set(value) == {"bars_parameter_ref"} and isinstance(value.get("bars_parameter_ref"), str):
            refs.add(value["bars_parameter_ref"])
        for child in value.values():
            refs.update(_collect_value_parameter_refs(child))
    elif isinstance(value, list):
        for child in value:
            refs.update(_collect_value_parameter_refs(child))
    return refs


def _validate_manifest_bound_parameter_axes(
    path: Path,
    payload: dict[str, Any],
    strategy_specs_dir: Path,
) -> list[str]:
    parent = payload.get("parent_strategy_spec")
    if not isinstance(parent, dict):
        return []
    strategy_spec_id = parent.get("strategy_spec_id")
    if not isinstance(strategy_spec_id, str) or not strategy_specs_dir.exists():
        return []
    parent_path = _discover_by_id(
        strategy_specs_dir,
        "*.strategy_spec.json",
        "strategy_spec_id",
        strategy_spec_id,
    )
    if parent_path is None:
        return []
    try:
        parent_payload = load_json(parent_path)
    except json.JSONDecodeError:
        return []

    bound_refs = _collect_value_parameter_refs(parent_payload)
    if not bound_refs:
        return []
    axes = payload.get("parameter_axes")
    axis_parameters = {
        axis.get("parameter_name")
        for axis in axes
        if isinstance(axis, dict)
    } if isinstance(axes, list) else set()
    errors: list[str] = []
    for parameter_name in sorted(bound_refs - axis_parameters):
        errors.append(
            f"{path}: parent Strategy Spec parameter_ref {parameter_name!r} must be present "
            "in parameter_axes before sweep planning"
        )
    return errors


def _validate_manifest_hash(path: Path, payload: dict[str, Any]) -> list[str]:
    hash_pinning = payload.get("manifest_hash_pinning")
    governance = payload.get("population_governance")
    if not isinstance(hash_pinning, dict) or not isinstance(governance, dict):
        return []

    errors: list[str] = []
    pre_registration = governance.get("pre_registration")
    hash_status = hash_pinning.get("hash_status")
    manifest_hash = hash_pinning.get("manifest_hash")

    if isinstance(pre_registration, dict) and (
        pre_registration.get("pre_registration_status") == "frozen_for_sweep_planning"
    ):
        if hash_status != "computed":
            errors.append(
                f"{path}: frozen manifest requires manifest_hash_pinning.hash_status='computed'"
            )
        if manifest_hash is None:
            errors.append(f"{path}: frozen manifest requires manifest_hash_pinning.manifest_hash")
        if hash_pinning.get("frozen_at") is None:
            errors.append(f"{path}: frozen manifest requires manifest_hash_pinning.frozen_at")

    if hash_status != "computed":
        return errors

    if manifest_hash is None:
        errors.append(f"{path}: computed manifest requires manifest_hash_pinning.manifest_hash")
        return errors
    if hash_pinning.get("hash_algorithm") != HASH_ALGORITHM:
        errors.append(f"{path}: manifest_hash_pinning.hash_algorithm must be {HASH_ALGORITHM}")
    if hash_pinning.get("canonicalization") != "json_canonical_v1":
        errors.append(
            f"{path}: manifest_hash_pinning.canonicalization must be json_canonical_v1"
        )
    if hash_pinning.get("hash_scope_version") != VARIANT_MANIFEST_HASH_SCOPE_VERSION:
        errors.append(
            f"{path}: manifest_hash_pinning.hash_scope_version must be "
            f"{VARIANT_MANIFEST_HASH_SCOPE_VERSION}"
        )

    scope = hash_pinning.get("hash_scope")
    if not isinstance(scope, list):
        errors.append(f"{path}: manifest_hash_pinning.hash_scope must be a list")
        return errors
    scoped_payload = _hash_scope_payload(payload, scope)
    if scoped_payload is None:
        errors.append(f"{path}: manifest_hash_pinning.hash_scope contains missing field")
        return errors

    computed_hash = sha256_prefixed(scoped_payload)
    if computed_hash != manifest_hash:
        errors.append(
            f"{path}: manifest_hash_pinning.manifest_hash mismatch: declared "
            f"{manifest_hash!r}, computed {computed_hash}"
        )
    return errors


def _validate_manifest_amendment(path: Path, payload: dict[str, Any]) -> list[str]:
    amendment = payload.get("amendment_and_supersession")
    if not isinstance(amendment, dict):
        return []

    errors: list[str] = []
    if amendment.get("associated_results_state") == "associated_results_exist":
        if amendment.get("amendment_mode") != "closed_after_results":
            errors.append(
                f"{path}: manifest with associated results must use amendment_mode "
                "closed_after_results"
            )
        if amendment.get("supersession_allowed") is not False:
            errors.append(
                f"{path}: manifest with associated results requires "
                "supersession_allowed=false"
            )
        if amendment.get("supersedes") is not None:
            errors.append(f"{path}: manifest with associated results cannot supersede")

    expected = {
        "post_result_change": False,
        "close_only_after_results": True,
        "preserve_prior_manifest_required": True,
        "fresh_denominator_required": True,
        "does_not_inherit_prior_results": True,
    }
    for key, expected_value in expected.items():
        if amendment.get(key) is not expected_value:
            errors.append(f"{path}: amendment_and_supersession.{key} must be {expected_value}")

    if amendment.get("amendment_mode") == "supersedes_prior_manifest":
        if amendment.get("associated_results_state") != "no_associated_results":
            errors.append(
                f"{path}: supersession requires associated_results_state=no_associated_results"
            )
        if amendment.get("supersession_allowed") is not True:
            errors.append(f"{path}: supersession requires supersession_allowed=true")
        if amendment.get("supersedes") is None:
            errors.append(f"{path}: supersession requires supersedes")
        lineage = amendment.get("supersession_lineage")
        if not isinstance(lineage, list) or not lineage:
            errors.append(f"{path}: supersession requires non-empty supersession_lineage")
        else:
            for index, entry in enumerate(lineage):
                if not isinstance(entry, dict):
                    continue
                if entry.get("prior_manifest_preserved_immutably") is not True:
                    errors.append(
                        f"{path}: amendment_and_supersession.supersession_lineage."
                        f"{index}.prior_manifest_preserved_immutably must be true"
                    )
                if not entry.get("supersession_reason"):
                    errors.append(
                        f"{path}: amendment_and_supersession.supersession_lineage."
                        f"{index}.supersession_reason must be non-empty"
                    )
        if not amendment.get("amendment_reason"):
            errors.append(f"{path}: supersession requires amendment_reason")

    return errors


def _validate_manifest_population(path: Path, payload: dict[str, Any]) -> list[str]:
    governance = payload.get("population_governance")
    variants = payload.get("variant_assignments")
    if not isinstance(governance, dict) or not isinstance(variants, list):
        return []

    errors: list[str] = []
    cap = governance.get("population_cap")
    declared = governance.get("declared_population")
    trial_budget = governance.get("trial_budget")
    accounting = governance.get("multiple_testing_accounting")
    if not all(isinstance(item, dict) for item in (cap, declared, trial_budget, accounting)):
        return errors

    committed_count = declared["committed_population_count"]
    declared_count = declared["declared_variant_count"]
    if committed_count != declared_count:
        errors.append(
            f"{path}: committed_population_count must equal declared_variant_count"
        )
    if committed_count != len(variants):
        errors.append(
            f"{path}: committed_population_count {committed_count} must equal "
            f"len(variant_assignments) {len(variants)}"
        )
    if declared_count > cap["max_variants"]:
        errors.append(f"{path}: declared_variant_count exceeds population_cap.max_variants")

    counted_status = {
        "included": "included_variant_count",
        "excluded": "excluded_variant_count",
        "invalid": "invalid_variant_count",
        "not_attempted": "not_attempted_variant_count",
    }
    declared_breakdown_total = sum(declared[key] for key in counted_status.values())
    if declared_breakdown_total != declared_count:
        errors.append(f"{path}: declared population status breakdown must equal declared count")
    actual_counts = {status: 0 for status in counted_status}
    for variant in variants:
        if isinstance(variant, dict) and variant.get("assignment_status") in actual_counts:
            actual_counts[variant["assignment_status"]] += 1
    for status, field in counted_status.items():
        if actual_counts[status] != declared[field]:
            errors.append(
                f"{path}: {field} {declared[field]} does not match variant_assignments "
                f"{actual_counts[status]}"
            )

    if trial_budget.get("trial_budget_denominator") != committed_count:
        errors.append(f"{path}: trial_budget.trial_budget_denominator must equal committed count")
    if trial_budget.get("denominator_count") != committed_count:
        errors.append(f"{path}: trial_budget.denominator_count must equal committed count")
    if trial_budget.get("denominator_basis") != "committed_pre_registered_population_count":
        errors.append(
            f"{path}: trial_budget.denominator_basis must be "
            "committed_pre_registered_population_count"
        )
    for key, value in trial_budget.items():
        if key.startswith("denominator_includes_") and value is not True:
            errors.append(f"{path}: trial_budget.{key} must be true")
    if trial_budget.get("executed_only_denominator_forbidden") is not True:
        errors.append(f"{path}: trial_budget.executed_only_denominator_forbidden must be true")

    if accounting.get("denominator_type") != "committed_pre_registered_population":
        errors.append(
            f"{path}: multiple_testing_accounting.denominator_type must be "
            "committed_pre_registered_population"
        )
    if accounting.get("all_trials_visible_required") is not True:
        errors.append(f"{path}: multiple_testing_accounting.all_trials_visible_required must be true")
    if accounting.get("winner_only_review_forbidden") is not True:
        errors.append(
            f"{path}: multiple_testing_accounting.winner_only_review_forbidden must be true"
        )
    if accounting.get("adaptive_search_used") is not False:
        errors.append(f"{path}: multiple_testing_accounting.adaptive_search_used must be false")
    if accounting.get("adaptive_search_authorization_ref") is not None:
        errors.append(
            f"{path}: multiple_testing_accounting.adaptive_search_authorization_ref must be null"
        )
    if cap.get("cap_exception_authorized") is not False:
        errors.append(f"{path}: population_cap.cap_exception_authorized must be false")
    if cap.get("cap_exception_ref") is not None:
        errors.append(f"{path}: population_cap.cap_exception_ref must be null")
    return errors


def _validate_value_against_axis(path: Path, axis: dict[str, Any], value: Any) -> list[str]:
    errors: list[str] = []
    parameter_type = axis.get("parameter_type")
    parameter_name = axis.get("parameter_name")
    if parameter_type == "integer" and not isinstance(value, int):
        errors.append(f"{path}: parameter {parameter_name} must be integer")
    if parameter_type == "number" and not isinstance(value, (int, float)):
        errors.append(f"{path}: parameter {parameter_name} must be number")
    if parameter_type == "boolean" and not isinstance(value, bool):
        errors.append(f"{path}: parameter {parameter_name} must be boolean")
    if parameter_type == "enum" and not isinstance(value, str):
        errors.append(f"{path}: parameter {parameter_name} must be string enum value")

    allowed_values = axis.get("allowed_values")
    if isinstance(allowed_values, list) and allowed_values and value not in allowed_values:
        errors.append(f"{path}: parameter {parameter_name} value {value!r} outside allowed_values")

    parameter_range = axis.get("range")
    if isinstance(parameter_range, dict) and isinstance(value, (int, float)):
        minimum = parameter_range.get("min")
        maximum = parameter_range.get("max")
        if minimum is not None:
            if parameter_range.get("inclusive_min") and value < minimum:
                errors.append(f"{path}: parameter {parameter_name} value {value!r} below min")
            if not parameter_range.get("inclusive_min") and value <= minimum:
                errors.append(f"{path}: parameter {parameter_name} value {value!r} below/equal min")
        if maximum is not None:
            if parameter_range.get("inclusive_max") and value > maximum:
                errors.append(f"{path}: parameter {parameter_name} value {value!r} above max")
            if not parameter_range.get("inclusive_max") and value >= maximum:
                errors.append(f"{path}: parameter {parameter_name} value {value!r} above/equal max")
    return errors


def _validate_manifest_assignments(path: Path, payload: dict[str, Any]) -> list[str]:
    axes = payload.get("parameter_axes")
    variants = payload.get("variant_assignments")
    if not isinstance(axes, list) or not isinstance(variants, list):
        return []

    errors: list[str] = []
    if len(axes) > MAX_PARAMETER_AXES:
        errors.append(f"{path}: parameter_axes exceeds {MAX_PARAMETER_AXES}")

    axis_ids: set[str] = set()
    axis_by_id: dict[str, dict[str, Any]] = {}
    axis_by_parameter: dict[str, dict[str, Any]] = {}
    for index, axis in enumerate(axes):
        if not isinstance(axis, dict):
            continue
        axis_id = axis.get("axis_id")
        parameter_name = axis.get("parameter_name")
        if axis.get("counts_toward_parent_free_parameter_cap") is not True:
            errors.append(f"{path}: parameter_axes.{index}.counts_toward_parent_free_parameter_cap must be true")
        if axis.get("is_declared_in_parent_strategy_spec") is not True:
            errors.append(f"{path}: parameter_axes.{index}.is_declared_in_parent_strategy_spec must be true")
        if axis.get("generator_method") not in {"manual_grid", "constrained_random"}:
            errors.append(f"{path}: parameter_axes.{index}.generator_method is invalid")
        if isinstance(axis_id, str):
            if axis_id in axis_ids:
                errors.append(f"{path}: duplicate axis_id {axis_id}")
            axis_ids.add(axis_id)
            axis_by_id[axis_id] = axis
        if isinstance(parameter_name, str):
            axis_by_parameter[parameter_name] = axis

    variant_ids: set[str] = set()
    for index, variant in enumerate(variants):
        if not isinstance(variant, dict):
            continue
        variant_id = variant.get("variant_id")
        if isinstance(variant_id, str):
            if variant_id in variant_ids:
                errors.append(f"{path}: duplicate variant_id {variant_id}")
            variant_ids.add(variant_id)
        axis_refs = variant.get("axis_refs")
        if isinstance(axis_refs, list):
            for axis_ref in axis_refs:
                if axis_ref not in axis_by_id:
                    errors.append(
                        f"{path}: variant_assignments.{index}.axis_refs references "
                        f"undeclared axis {axis_ref!r}"
                    )
        parameter_values = variant.get("parameter_values")
        if not isinstance(parameter_values, dict):
            continue
        extra_parameters = set(parameter_values) - set(axis_by_parameter)
        for parameter_name in sorted(extra_parameters):
            errors.append(
                f"{path}: variant_assignments.{index}.parameter_values has undeclared "
                f"parameter {parameter_name}"
            )
        missing_parameters = set(axis_by_parameter) - set(parameter_values)
        for parameter_name in sorted(missing_parameters):
            errors.append(
                f"{path}: variant_assignments.{index}.parameter_values missing "
                f"parameter {parameter_name}"
            )
        for parameter_name, value in parameter_values.items():
            axis = axis_by_parameter.get(parameter_name)
            if axis is not None:
                errors.extend(_validate_value_against_axis(path, axis, value))
    return errors


def _manifest_committed_count(payload: dict[str, Any]) -> int | None:
    found, value = _get_path(
        payload,
        "population_governance.declared_population.committed_population_count",
    )
    if found and isinstance(value, int):
        return value
    return None


def _manifest_cap(payload: dict[str, Any]) -> int | None:
    found, value = _get_path(payload, "population_governance.population_cap.max_variants")
    if found and isinstance(value, int):
        return value
    return None


def _manifest_included_variant_ids(payload: dict[str, Any]) -> set[str]:
    variants = payload.get("variant_assignments")
    if not isinstance(variants, list):
        return set()
    return {
        variant["variant_id"]
        for variant in variants
        if isinstance(variant, dict)
        and isinstance(variant.get("variant_id"), str)
        and variant.get("assignment_status") == "included"
    }


def _validate_sweep_parent_manifest(
    path: Path,
    payload: dict[str, Any],
    manifest_by_id: dict[str, dict[str, Any]],
    manifest_path_by_id: dict[str, Path],
    variant_manifests_dir: Path,
) -> list[str]:
    parent = payload.get("parent_variant_manifest")
    if not isinstance(parent, dict):
        return []

    errors: list[str] = []
    manifest_id = parent.get("variant_manifest_id")
    if parent.get("mismatch_policy") != "block":
        errors.append(f"{path}: parent_variant_manifest.mismatch_policy must be 'block'")
    if parent.get("missing_manifest_policy") != "block":
        errors.append(f"{path}: parent_variant_manifest.missing_manifest_policy must be 'block'")
    if parent.get("one_manifest_only") is not True:
        errors.append(f"{path}: parent_variant_manifest.one_manifest_only must be true")
    if not isinstance(manifest_id, str):
        return errors

    if not variant_manifests_dir.exists():
        errors.append(
            f"{path}: sweep plan requires parent variant manifest corpus under "
            f"{variant_manifests_dir}"
        )
        return errors
    parent_manifest = manifest_by_id.get(manifest_id)
    if parent_manifest is None:
        errors.append(f"{path}: parent variant manifest {manifest_id} missing")
        return errors

    manifest_hash = parent_manifest.get("manifest_hash_pinning", {}).get("manifest_hash")
    if manifest_hash and parent.get("manifest_hash") != manifest_hash:
        errors.append(
            f"{path}: parent_variant_manifest.manifest_hash mismatch for {manifest_id}: "
            f"declared {parent.get('manifest_hash')!r}, manifest {manifest_hash}"
        )
    if parent_manifest.get("variant_manifest_id") != manifest_id:
        errors.append(
            f"{path}: parent manifest file {manifest_path_by_id[manifest_id]} has mismatched ID"
        )
    found, pre_registration_status = _get_path(
        parent_manifest,
        "population_governance.pre_registration.pre_registration_status",
    )
    if not found or pre_registration_status != "frozen_for_sweep_planning":
        errors.append(
            f"{path}: parent manifest must be frozen_for_sweep_planning before sweep plan"
        )

    committed_count = _manifest_committed_count(parent_manifest)
    cap = _manifest_cap(parent_manifest)
    if committed_count is not None:
        if parent.get("manifest_committed_population_count") != committed_count:
            errors.append(
                f"{path}: parent_variant_manifest.manifest_committed_population_count "
                "must equal parent manifest committed count"
            )
        if payload.get("trial_accounting", {}).get("committed_population_count") != committed_count:
            errors.append(
                f"{path}: trial_accounting.committed_population_count must equal "
                "parent manifest committed count"
            )
    if cap is not None and parent.get("manifest_population_cap") != cap:
        errors.append(
            f"{path}: parent_variant_manifest.manifest_population_cap must equal "
            "parent manifest cap"
        )
    return errors


def _validate_sweep_amendment(path: Path, payload: dict[str, Any]) -> list[str]:
    amendment = payload.get("amendment_and_supersession")
    if not isinstance(amendment, dict):
        return []

    errors: list[str] = []
    if amendment.get("associated_results_state") == "associated_results_exist":
        if amendment.get("amendment_mode") != "closed_after_results":
            errors.append(
                f"{path}: sweep plan with associated results must use "
                "amendment_mode closed_after_results"
            )
        if amendment.get("supersession_allowed") is not False:
            errors.append(
                f"{path}: sweep plan with associated results requires "
                "supersession_allowed=false"
            )
        if amendment.get("supersedes") is not None:
            errors.append(f"{path}: sweep plan with associated results cannot supersede")

    expected = {
        "post_result_change": False,
        "close_only_after_results": True,
        "preserve_prior_sweep_plan_required": True,
        "does_not_modify_parent_manifest": True,
        "does_not_modify_manifest_denominator": True,
    }
    for key, expected_value in expected.items():
        if amendment.get(key) is not expected_value:
            errors.append(f"{path}: amendment_and_supersession.{key} must be {expected_value}")
    return errors


def _validate_sweep_trial_accounting(
    path: Path,
    payload: dict[str, Any],
    parent_manifest: dict[str, Any] | None,
) -> list[str]:
    accounting = payload.get("trial_accounting")
    if not isinstance(accounting, dict):
        return []

    errors: list[str] = []
    committed_count = accounting.get("committed_population_count")
    if accounting.get("multiple_testing_denominator") != committed_count:
        errors.append(
            f"{path}: trial_accounting.multiple_testing_denominator must equal "
            "committed_population_count"
        )
    if accounting.get("denominator_basis") != "committed_pre_registered_population_count":
        errors.append(
            f"{path}: trial_accounting.denominator_basis must be "
            "committed_pre_registered_population_count"
        )
    for key in (
        "denominator_equals_committed_population_count",
        "executed_only_denominator_forbidden",
        "successful_only_denominator_forbidden",
        "failed_variants_remain_in_denominator",
        "excluded_variants_remain_in_denominator",
        "invalid_variants_remain_in_denominator",
        "errored_variants_remain_in_denominator",
        "aborted_variants_remain_in_denominator",
        "filtered_variants_remain_in_denominator",
        "data_unavailable_variants_remain_in_denominator",
        "not_attempted_variants_remain_in_denominator",
    ):
        if accounting.get(key) is not True:
            errors.append(f"{path}: trial_accounting.{key} must be true")
    if parent_manifest is not None:
        parent_count = _manifest_committed_count(parent_manifest)
        if parent_count is not None and committed_count != parent_count:
            errors.append(
                f"{path}: trial_accounting.committed_population_count must equal "
                "parent manifest committed count"
            )
    return errors


def _validate_sweep_integrity(
    path: Path,
    payload: dict[str, Any],
    parent_manifest: dict[str, Any] | None,
) -> list[str]:
    errors: list[str] = []
    methods = payload.get("validation_methods")
    if isinstance(methods, dict):
        for key in ("declarative_intent_only", "no_runner_hooks", "no_formulas", "no_computation"):
            if methods.get(key) is not True:
                errors.append(f"{path}: validation_methods.{key} must be true")
        for method_name in ("dsr_psr_mintrl_accounting", "monte_carlo"):
            method = methods.get(method_name)
            if isinstance(method, dict) and method.get("computation_deferred") is not True:
                errors.append(
                    f"{path}: validation_methods.{method_name}.computation_deferred must be true"
                )

    selection = payload.get("test_selection")
    if isinstance(selection, dict):
        for key in (
            "declared_before_results",
            "post_hoc_addition_forbidden",
            "outside_manifest_variants_forbidden",
        ):
            if selection.get(key) is not True:
                errors.append(f"{path}: test_selection.{key} must be true")
        if parent_manifest is not None:
            parent_ids = {
                variant["variant_id"]
                for variant in parent_manifest.get("variant_assignments", [])
                if isinstance(variant, dict) and isinstance(variant.get("variant_id"), str)
            }
            selected_ids = set(selection.get("selected_variant_ids", []))
            excluded_ids = set(selection.get("excluded_variant_ids", []))
            for variant_id in sorted((selected_ids | excluded_ids) - parent_ids):
                errors.append(f"{path}: test_selection references variant outside manifest: {variant_id}")
            if selection.get("selection_mode") == "all_manifest_variants":
                included_ids = _manifest_included_variant_ids(parent_manifest)
                if selected_ids != included_ids:
                    errors.append(
                        f"{path}: all_manifest_variants requires selected_variant_ids to "
                        "match parent included variants"
                    )

    capture = payload.get("result_capture_expectations")
    if isinstance(capture, dict):
        for key, value in capture.items():
            if key.startswith("must_capture_") and value is not True:
                errors.append(f"{path}: result_capture_expectations.{key} must be true")
        if capture.get("winner_only_retention_forbidden") is not True:
            errors.append(
                f"{path}: result_capture_expectations.winner_only_retention_forbidden "
                "must be true"
            )
    return errors


def validate_variant_sweep_artifacts(
    variant_manifests_dir: Path = DEFAULT_VARIANT_MANIFESTS_DIR,
    sweep_plans_dir: Path = DEFAULT_SWEEP_PLANS_DIR,
    strategy_specs_dir: Path = DEFAULT_STRATEGY_SPECS_DIR,
    variant_manifest_schema_path: Path = DEFAULT_VARIANT_MANIFEST_SCHEMA_PATH,
    sweep_plan_schema_path: Path = DEFAULT_SWEEP_PLAN_SCHEMA_PATH,
    strategy_spec_schema_path: Path = DEFAULT_STRATEGY_SPEC_SCHEMA_PATH,
    repo_root: Path = REPO_ROOT,
) -> list[str]:
    """Return validation errors for variant/sweep artifacts, or [] when valid."""

    variant_files = (
        sorted(variant_manifests_dir.rglob("*.variant_manifest.json"))
        if variant_manifests_dir.exists()
        else []
    )
    sweep_files = (
        sorted(sweep_plans_dir.rglob("*.sweep_plan.json")) if sweep_plans_dir.exists() else []
    )
    if not variant_files and not sweep_files:
        return []

    variant_manifest_schema = load_json(variant_manifest_schema_path)
    sweep_plan_schema = load_json(sweep_plan_schema_path)
    strategy_spec_schema = load_json(strategy_spec_schema_path)
    Draft7Validator.check_schema(variant_manifest_schema)
    Draft7Validator.check_schema(sweep_plan_schema)
    Draft7Validator.check_schema(strategy_spec_schema)
    variant_validator = Draft7Validator(variant_manifest_schema)
    sweep_validator = Draft7Validator(sweep_plan_schema)

    errors: list[str] = []
    manifest_by_id: dict[str, dict[str, Any]] = {}
    manifest_path_by_id: dict[str, Path] = {}
    known_manifest_ids: set[str] = set()

    for path in variant_files:
        payload, file_errors = _validate_json_file(path, variant_validator)
        errors.extend(file_errors)
        if payload is None:
            continue
        if file_errors:
            continue

        variant_manifest_id = payload.get("variant_manifest_id")
        if isinstance(variant_manifest_id, str):
            expected_name = f"{variant_manifest_id}.variant_manifest.json"
            if path.name != expected_name:
                errors.append(f"{path}: filename must be {expected_name}")
            if variant_manifest_id in known_manifest_ids:
                errors.append(
                    f"{path}: duplicate variant_manifest_id {variant_manifest_id}; "
                    f"first seen at {manifest_path_by_id[variant_manifest_id]}"
                )
            known_manifest_ids.add(variant_manifest_id)
            manifest_by_id.setdefault(variant_manifest_id, payload)
            manifest_path_by_id.setdefault(variant_manifest_id, path)
        else:
            errors.append(f"{path}: missing valid variant_manifest_id")

        errors.extend(_validate_parent_strategy_spec_hash(path, payload, strategy_specs_dir))
        errors.extend(
            _validate_variant_planning_approval(path, payload, strategy_specs_dir, repo_root)
        )
        errors.extend(_validate_manifest_bound_parameter_axes(path, payload, strategy_specs_dir))
        errors.extend(_validate_manifest_hash(path, payload))
        errors.extend(_validate_manifest_amendment(path, payload))
        errors.extend(_validate_manifest_population(path, payload))
        errors.extend(_validate_manifest_assignments(path, payload))
        errors.extend(_validate_forbidden_keys(path, payload))
        errors.extend(_validate_non_authority_flags(path, payload))

    known_sweep_ids: set[str] = set()
    sweep_path_by_id: dict[str, Path] = {}
    for path in sweep_files:
        payload, file_errors = _validate_json_file(path, sweep_validator)
        errors.extend(file_errors)
        if payload is None:
            continue
        if file_errors:
            continue

        sweep_plan_id = payload.get("sweep_plan_id")
        if isinstance(sweep_plan_id, str):
            expected_name = f"{sweep_plan_id}.sweep_plan.json"
            if path.name != expected_name:
                errors.append(f"{path}: filename must be {expected_name}")
            if sweep_plan_id in known_sweep_ids:
                errors.append(
                    f"{path}: duplicate sweep_plan_id {sweep_plan_id}; "
                    f"first seen at {sweep_path_by_id[sweep_plan_id]}"
                )
            known_sweep_ids.add(sweep_plan_id)
            sweep_path_by_id.setdefault(sweep_plan_id, path)
        else:
            errors.append(f"{path}: missing valid sweep_plan_id")

        parent_id = payload.get("parent_variant_manifest", {}).get("variant_manifest_id")
        parent_manifest = manifest_by_id.get(parent_id) if isinstance(parent_id, str) else None
        errors.extend(
            _validate_sweep_parent_manifest(
                path,
                payload,
                manifest_by_id,
                manifest_path_by_id,
                variant_manifests_dir,
            )
        )
        errors.extend(_validate_sweep_amendment(path, payload))
        errors.extend(_validate_sweep_trial_accounting(path, payload, parent_manifest))
        errors.extend(_validate_sweep_integrity(path, payload, parent_manifest))
        errors.extend(_validate_forbidden_keys(path, payload))
        errors.extend(_validate_non_authority_flags(path, payload))

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--variant-manifests-dir", type=Path, default=DEFAULT_VARIANT_MANIFESTS_DIR)
    parser.add_argument("--sweep-plans-dir", type=Path, default=DEFAULT_SWEEP_PLANS_DIR)
    parser.add_argument("--strategy-specs-dir", type=Path, default=DEFAULT_STRATEGY_SPECS_DIR)
    parser.add_argument(
        "--variant-manifest-schema",
        type=Path,
        default=DEFAULT_VARIANT_MANIFEST_SCHEMA_PATH,
    )
    parser.add_argument("--sweep-plan-schema", type=Path, default=DEFAULT_SWEEP_PLAN_SCHEMA_PATH)
    parser.add_argument("--strategy-spec-schema", type=Path, default=DEFAULT_STRATEGY_SPEC_SCHEMA_PATH)
    args = parser.parse_args()

    errors = validate_variant_sweep_artifacts(
        variant_manifests_dir=args.variant_manifests_dir,
        sweep_plans_dir=args.sweep_plans_dir,
        strategy_specs_dir=args.strategy_specs_dir,
        variant_manifest_schema_path=args.variant_manifest_schema,
        sweep_plan_schema_path=args.sweep_plan_schema,
        strategy_spec_schema_path=args.strategy_spec_schema,
        repo_root=REPO_ROOT,
    )
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    if not args.variant_manifests_dir.exists() and not args.sweep_plans_dir.exists():
        print(
            "OK: variant manifest and sweep plan directories do not exist; "
            "nothing to validate"
        )
    else:
        print(
            "OK: variant manifest and sweep plan artifacts under "
            f"{args.variant_manifests_dir} / {args.sweep_plans_dir} validate"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
