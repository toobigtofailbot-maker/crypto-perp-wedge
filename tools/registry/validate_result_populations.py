"""Validate non-executing result-population JSON artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Mapping

from jsonschema import Draft7Validator

from tools.registry.validate_data_feature_availability import (
    DEFAULT_CATALOG_PATH as DEFAULT_DATA_FEATURE_AVAILABILITY_CATALOG_PATH,
    DEFAULT_SCHEMA_PATH as DEFAULT_DATA_FEATURE_AVAILABILITY_SCHEMA_PATH,
    build_catalog_index,
    load_json as load_availability_json,
    validate_data_feature_availability,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RESULT_POPULATIONS_DIR = REPO_ROOT / "research" / "result_populations"
DEFAULT_RESULT_POPULATION_SCHEMA_PATH = (
    REPO_ROOT / "research" / "schemas" / "result_population.schema.json"
)
DEFAULT_STRATEGY_SPECS_DIR = REPO_ROOT / "research" / "strategy_specs"
DEFAULT_VARIANT_MANIFESTS_DIR = REPO_ROOT / "research" / "variant_manifests"
DEFAULT_SWEEP_PLANS_DIR = REPO_ROOT / "research" / "sweep_plans"
DEFAULT_STRATEGY_SPEC_SCHEMA_PATH = REPO_ROOT / "research" / "schemas" / "strategy_spec.schema.json"
DEFAULT_VARIANT_MANIFEST_SCHEMA_PATH = (
    REPO_ROOT / "research" / "schemas" / "variant_manifest.schema.json"
)
DEFAULT_SWEEP_PLAN_SCHEMA_PATH = REPO_ROOT / "research" / "schemas" / "sweep_plan.schema.json"
HASH_ALGORITHM = "sha256"
RESULT_POPULATION_HASH_SCOPE_VERSION = "result_population_identity_hash_scope_v1"
SIZING_METADATA_HASH_SCOPE_PATH = "sizing_metadata"
DATA_AVAILABILITY_CLAIM_HASH_SCOPE_PATH = "data_availability_claim"
OHLCV_DATA_FIELDS = {"open", "high", "low", "close", "volume"}
SIZING_MODES = {"fixed_order_size", "dynamic_equity_target_leverage"}
SIZING_EQUITY_BASES = {
    "not_applicable_fixed_order_size",
    "realized_available_equity_at_entry",
}
ENTRY_REFERENCE_PRICE_BASES = {
    "not_applicable_fixed_order_size",
    "next_bar_open_pre_fee_slippage",
}
OUTCOME_CATEGORIES = (
    "successful",
    "failed",
    "invalid",
    "excluded",
    "errored",
    "aborted",
    "filtered",
    "data_unavailable",
    "not_attempted",
)
LEDGER_EVENT_TYPES = {
    "created",
    "validated",
    "reviewed",
    "amendment_referenced",
    "supersession_referenced",
    "correction_referenced",
    "closed",
}
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
    "canonical_sweep_run",
    "gate_action",
    "promote",
    "promotion",
    "deploy",
    "live_enable",
    "paper_enable",
}
ALLOWED_RECORDING_KEYS = {
    "runner_code_ref",
    "repo_commit",
    "validation_run_logs",
    "actor_or_tool",
    "canonical_evidence_relationship",
}
NON_AUTHORITY_TRUE_FLAGS = {
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
}
REVIEW_NON_AUTHORITY_TRUE_FLAGS = {
    "not_approval",
    "not_recommendation",
    "not_readiness",
    "not_transition",
    "not_gate_satisfaction",
    "not_runtime_authority",
    "not_paper_live_authority",
}
AUDIT_ENVELOPE_TRUE_FLAGS = {
    "excluded_from_input_identity_hash",
    "excluded_from_result_population_identity_hash",
    "administrative_only",
}
AUDIT_ENVELOPE_FALSE_FLAGS = {"may_contain_scientific_content"}
DENOMINATOR_TRUE_FLAGS = {
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
}
ROW_MUTATION_TRUE_FLAGS = {
    "scientific_row_identity_immutable_after_commit",
    "corrections_require_append_only_event",
    "post_commit_in_place_mutation_forbidden",
    "post_hoc_cleanup_forbidden",
}
APPEND_ONLY_TRUE_FLAGS = {
    "ledger_required",
    "append_only",
    "post_commit_in_place_mutation_forbidden",
    "scientific_identity_mutation_forbidden_after_finalization",
    "corrections_require_append_only_event",
    "supersession_preserves_prior_result_population",
}
VALIDATION_SUMMARY_TRUE_FLAGS = {
    "validator_does_not_approve",
    "validator_does_not_recommend",
    "validator_does_not_rank",
    "validator_does_not_execute",
    "validator_does_not_contact_runtime",
}
AUTHORITY_KEY_TOKENS = {
    "approval",
    "approved",
    "recommendation",
    "ranking",
    "readiness",
    "transition",
    "gate_action",
    "runtime_action",
    "paper_action",
    "live_action",
}
AUDIT_SCIENTIFIC_KEY_TOKENS = {
    "metrics",
    "outcome",
    "denominator",
    "variant_result_rows",
    "strategy_spec_hash",
    "manifest_hash",
    "sweep_plan_hash",
    "data_slice_identity",
    "backtest_assumption",
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


def get_path_value(document: Mapping[str, Any], path: str) -> Any:
    current: Any = document
    for part in path.split("."):
        if not isinstance(current, Mapping) or part not in current:
            raise KeyError(path)
        current = current[part]
    return current


def _get_path(document: Mapping[str, Any], path: str) -> tuple[bool, Any]:
    try:
        return True, get_path_value(document, path)
    except KeyError:
        return False, None


def _hash_scope_payload(payload: Mapping[str, Any], scope: list[Any]) -> dict[str, Any] | None:
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


def _validate_true_flags(
    path: Path,
    payload: Mapping[str, Any],
    object_path: str,
    required_flags: set[str],
) -> list[str]:
    found, current = _get_path(payload, object_path)
    if not found or not isinstance(current, dict):
        return [f"{path}: {object_path} must be present as an object"]
    return [
        f"{path}: {object_path}.{flag} must be true"
        for flag in sorted(required_flags)
        if current.get(flag) is not True
    ]


def _validate_false_flags(
    path: Path,
    payload: Mapping[str, Any],
    object_path: str,
    required_flags: set[str],
) -> list[str]:
    found, current = _get_path(payload, object_path)
    if not found or not isinstance(current, dict):
        return [f"{path}: {object_path} must be present as an object"]
    return [
        f"{path}: {object_path}.{flag} must be false"
        for flag in sorted(required_flags)
        if current.get(flag) is not False
    ]


def _discover_by_id(
    directory: Path,
    pattern: str,
    id_field: str,
    wanted_id: str,
) -> tuple[Path | None, dict[str, Any] | None, str | None]:
    preferred_suffix = pattern.replace("*", "")
    preferred = directory / f"{wanted_id}{preferred_suffix}"
    candidates = [preferred] if preferred.exists() else []
    if directory.exists():
        candidates.extend(path for path in sorted(directory.rglob(pattern)) if path != preferred)

    for candidate in candidates:
        try:
            payload = load_json(candidate)
        except json.JSONDecodeError as exc:
            return candidate, None, f"{candidate}: invalid JSON: {exc}"
        except OSError as exc:
            return candidate, None, f"{candidate}: cannot read JSON: {exc}"
        if payload.get(id_field) == wanted_id:
            return candidate, payload, None
    return None, None, None


def _manifest_committed_count(payload: Mapping[str, Any]) -> int | None:
    found, value = _get_path(
        payload,
        "population_governance.declared_population.committed_population_count",
    )
    return value if found and isinstance(value, int) else None


def _manifest_variant_ids(payload: Mapping[str, Any]) -> set[str]:
    variants = payload.get("variant_assignments")
    if not isinstance(variants, list):
        return set()
    return {
        variant["variant_id"]
        for variant in variants
        if isinstance(variant, dict) and isinstance(variant.get("variant_id"), str)
    }


def _sweep_committed_count(payload: Mapping[str, Any]) -> int | None:
    found, value = _get_path(payload, "trial_accounting.committed_population_count")
    return value if found and isinstance(value, int) else None


def _sweep_selected_count(payload: Mapping[str, Any]) -> int | None:
    found, value = _get_path(payload, "trial_accounting.selected_variant_count")
    return value if found and isinstance(value, int) else None


def _sweep_identity_hash(payload: Mapping[str, Any]) -> str:
    found, value = _get_path(payload, "sweep_plan_identity_hash.hash")
    if found and isinstance(value, str):
        return value
    return sha256_prefixed(payload)


def _validate_filename_and_id(
    path: Path,
    payload: Mapping[str, Any],
    seen_ids: set[str],
    id_paths: dict[str, Path],
) -> list[str]:
    errors: list[str] = []
    result_population_id = payload.get("result_population_id")
    if not isinstance(result_population_id, str):
        return [f"{path}: missing valid result_population_id"]

    expected_name = f"{result_population_id}.result_population.json"
    if path.name != expected_name:
        errors.append(f"{path}: filename must be {expected_name}")
    if result_population_id in seen_ids:
        errors.append(
            f"{path}: duplicate result_population_id {result_population_id}; "
            f"first seen at {id_paths[result_population_id]}"
        )
    seen_ids.add(result_population_id)
    id_paths.setdefault(result_population_id, path)
    return errors


def _validate_closed_outcome_enum(path: Path, payload: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    counts = payload.get("outcome_category_counts")
    if isinstance(counts, dict):
        for category in OUTCOME_CATEGORIES:
            if category not in counts:
                errors.append(f"{path}: outcome_category_counts.{category} is required")
        for key in counts:
            if key not in {*OUTCOME_CATEGORIES, "counts_sum", "counts_sum_equals_committed_denominator"}:
                errors.append(f"{path}: outcome_category_counts has unsupported category/key {key!r}")

    rows = payload.get("variant_result_rows")
    if isinstance(rows, list):
        for index, row in enumerate(rows):
            if not isinstance(row, dict):
                continue
            outcome = row.get("outcome_category")
            if outcome not in OUTCOME_CATEGORIES:
                errors.append(
                    f"{path}: variant_result_rows.{index}.outcome_category invalid: {outcome!r}"
                )
    return errors


def _validate_identity_hash(
    path: Path,
    payload: Mapping[str, Any],
    object_path: str,
    require_hash: bool,
) -> list[str]:
    found, identity = _get_path(payload, object_path)
    if not found or not isinstance(identity, dict):
        return [f"{path}: {object_path} must be present as an object"]

    errors: list[str] = []
    if require_hash and identity.get("hash") is None:
        errors.append(f"{path}: {object_path}.hash must be non-null when status is not draft")
    if identity.get("hash_algorithm") != HASH_ALGORITHM:
        errors.append(f"{path}: {object_path}.hash_algorithm must be {HASH_ALGORITHM}")
    if identity.get("canonicalization") != "json_canonical_v1":
        errors.append(f"{path}: {object_path}.canonicalization must be json_canonical_v1")
    if object_path == "result_population_identity_hash" and (
        identity.get("hash_scope_version") != RESULT_POPULATION_HASH_SCOPE_VERSION
    ):
        errors.append(
            f"{path}: result_population_identity_hash.hash_scope_version must be "
            f"{RESULT_POPULATION_HASH_SCOPE_VERSION}"
        )
    if identity.get("audit_envelope_excluded") is not True:
        errors.append(f"{path}: {object_path}.audit_envelope_excluded must be true")
    if (
        identity.get("audit_envelope_exclusion_reason")
        != "administrative_audit_metadata_is_excluded_from_scientific_identity"
    ):
        errors.append(f"{path}: {object_path}.audit_envelope_exclusion_reason is invalid")

    scope = identity.get("hash_scope")
    if not isinstance(scope, list):
        return [*errors, f"{path}: {object_path}.hash_scope must be a list"]
    if "sizing_metadata" in payload and SIZING_METADATA_HASH_SCOPE_PATH not in scope:
        errors.append(
            f"{path}: {object_path}.hash_scope must include "
            f"{SIZING_METADATA_HASH_SCOPE_PATH} when sizing_metadata is present"
        )
    for item in scope:
        if isinstance(item, str) and (item == "audit_envelope" or item.startswith("audit_envelope.")):
            errors.append(f"{path}: {object_path}.hash_scope must exclude audit_envelope: {item}")

    scoped_payload = _hash_scope_payload(payload, scope)
    declared_hash = identity.get("hash")
    if scoped_payload is None:
        if require_hash:
            errors.append(f"{path}: {object_path}.hash_scope contains missing field")
        return errors
    if declared_hash is not None:
        computed_hash = sha256_prefixed(scoped_payload)
        if computed_hash != declared_hash:
            errors.append(
                f"{path}: {object_path}.hash mismatch: declared {declared_hash!r}, "
                f"computed {computed_hash}"
            )
    return errors


def _is_finite_positive_number(value: Any) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
        and value > 0
    )


def _validate_sizing_metadata(path: Path, payload: Mapping[str, Any]) -> list[str]:
    if "sizing_metadata" not in payload:
        return []

    sizing = payload.get("sizing_metadata")
    if not isinstance(sizing, dict):
        return [f"{path}: sizing_metadata must be an object when present"]

    errors: list[str] = []
    sizing_mode = sizing.get("sizing_mode")
    if sizing_mode not in SIZING_MODES:
        errors.append(f"{path}: sizing_metadata.sizing_mode invalid: {sizing_mode!r}")

    for field_name, allowed_values in (
        ("sizing_equity_basis", SIZING_EQUITY_BASES),
        ("entry_reference_price_basis", ENTRY_REFERENCE_PRICE_BASES),
    ):
        value = sizing.get(field_name)
        if value not in allowed_values:
            errors.append(f"{path}: sizing_metadata.{field_name} invalid: {value!r}")

    target_leverage = sizing.get("target_leverage")
    if sizing_mode == "dynamic_equity_target_leverage" and "target_leverage" not in sizing:
        errors.append(f"{path}: sizing_metadata.target_leverage is required for dynamic sizing")
    if "target_leverage" in sizing and not _is_finite_positive_number(target_leverage):
        errors.append(f"{path}: sizing_metadata.target_leverage must be finite positive")

    if "max_leverage_cap" in sizing and not _is_finite_positive_number(sizing.get("max_leverage_cap")):
        errors.append(f"{path}: sizing_metadata.max_leverage_cap must be finite positive")

    return errors


def _validate_audit_envelope(path: Path, payload: Mapping[str, Any]) -> list[str]:
    errors = _validate_true_flags(path, payload, "audit_envelope", AUDIT_ENVELOPE_TRUE_FLAGS)
    errors.extend(_validate_false_flags(path, payload, "audit_envelope", AUDIT_ENVELOPE_FALSE_FLAGS))
    found, audit = _get_path(payload, "audit_envelope")
    if not found or not isinstance(audit, dict):
        return errors

    for key_path, key in _walk_keys(audit, ["audit_envelope"]):
        if key.lower() in AUDIT_SCIENTIFIC_KEY_TOKENS:
            errors.append(f"{path}: audit_envelope field suggests scientific content: {key_path}")
    return errors


def _validate_parent_artifacts(
    path: Path,
    payload: Mapping[str, Any],
    strategy_specs_dir: Path,
    variant_manifests_dir: Path,
    sweep_plans_dir: Path,
) -> tuple[list[str], dict[str, Any] | None, dict[str, Any] | None, dict[str, Any] | None]:
    errors: list[str] = []
    strategy_spec: dict[str, Any] | None = None
    manifest: dict[str, Any] | None = None
    sweep_plan: dict[str, Any] | None = None

    parent_spec = payload.get("parent_strategy_spec")
    if isinstance(parent_spec, dict):
        if parent_spec.get("mismatch_policy") != "block":
            errors.append(f"{path}: parent_strategy_spec.mismatch_policy must be 'block'")
        if parent_spec.get("missing_parent_policy") != "block":
            errors.append(f"{path}: parent_strategy_spec.missing_parent_policy must be 'block'")
        spec_id = parent_spec.get("strategy_spec_id")
        if isinstance(spec_id, str) and strategy_specs_dir.exists():
            spec_path, strategy_spec, discovery_error = _discover_by_id(
                strategy_specs_dir,
                "*.strategy_spec.json",
                "strategy_spec_id",
                spec_id,
            )
            if discovery_error:
                errors.append(discovery_error)
            elif spec_path is None and parent_spec.get("missing_parent_policy") == "block":
                errors.append(f"{path}: parent Strategy Spec {spec_id} missing under {strategy_specs_dir}")
            elif strategy_spec is not None:
                if strategy_spec.get("strategy_spec_id") != spec_id:
                    errors.append(f"{path}: parent Strategy Spec file has mismatched strategy_spec_id")
                computed_hash = sha256_prefixed(strategy_spec)
                if computed_hash != parent_spec.get("strategy_spec_hash"):
                    errors.append(
                        f"{path}: parent_strategy_spec.strategy_spec_hash mismatch for "
                        f"{spec_id}: declared {parent_spec.get('strategy_spec_hash')!r}, "
                        f"computed {computed_hash}"
                    )

    parent_manifest = payload.get("parent_variant_manifest")
    if isinstance(parent_manifest, dict):
        if parent_manifest.get("mismatch_policy") != "block":
            errors.append(f"{path}: parent_variant_manifest.mismatch_policy must be 'block'")
        if parent_manifest.get("missing_manifest_policy") != "block":
            errors.append(f"{path}: parent_variant_manifest.missing_manifest_policy must be 'block'")
        manifest_id = parent_manifest.get("variant_manifest_id")
        if isinstance(manifest_id, str):
            manifest_path, manifest, discovery_error = _discover_by_id(
                variant_manifests_dir,
                "*.variant_manifest.json",
                "variant_manifest_id",
                manifest_id,
            )
            if discovery_error:
                errors.append(discovery_error)
            elif manifest_path is None:
                errors.append(f"{path}: parent variant manifest {manifest_id} missing")
            elif manifest is not None:
                manifest_hash = manifest.get("manifest_hash_pinning", {}).get("manifest_hash")
                if manifest.get("variant_manifest_id") != manifest_id:
                    errors.append(f"{path}: parent manifest file has mismatched variant_manifest_id")
                if parent_manifest.get("manifest_hash") != manifest_hash:
                    errors.append(
                        f"{path}: parent_variant_manifest.manifest_hash mismatch for "
                        f"{manifest_id}: declared {parent_manifest.get('manifest_hash')!r}, "
                        f"manifest {manifest_hash!r}"
                    )
                found, pre_registration_status = _get_path(
                    manifest,
                    "population_governance.pre_registration.pre_registration_status",
                )
                if not found or pre_registration_status != "frozen_for_sweep_planning":
                    errors.append(f"{path}: parent manifest must be frozen_for_sweep_planning")
                committed_count = _manifest_committed_count(manifest)
                if committed_count is not None and (
                    parent_manifest.get("committed_population_count") != committed_count
                ):
                    errors.append(
                        f"{path}: parent_variant_manifest.committed_population_count "
                        "must equal parent manifest committed count"
                    )

    parent_sweep = payload.get("parent_sweep_plan")
    if isinstance(parent_sweep, dict):
        if parent_sweep.get("mismatch_policy") != "block":
            errors.append(f"{path}: parent_sweep_plan.mismatch_policy must be 'block'")
        if parent_sweep.get("missing_sweep_plan_policy") != "block":
            errors.append(f"{path}: parent_sweep_plan.missing_sweep_plan_policy must be 'block'")
        sweep_id = parent_sweep.get("sweep_plan_id")
        if isinstance(sweep_id, str):
            sweep_path, sweep_plan, discovery_error = _discover_by_id(
                sweep_plans_dir,
                "*.sweep_plan.json",
                "sweep_plan_id",
                sweep_id,
            )
            if discovery_error:
                errors.append(discovery_error)
            elif sweep_path is None:
                errors.append(f"{path}: parent sweep plan {sweep_id} missing")
            elif sweep_plan is not None:
                if sweep_plan.get("sweep_plan_id") != sweep_id:
                    errors.append(f"{path}: parent sweep plan file has mismatched sweep_plan_id")
                found, sweep_manifest_id = _get_path(
                    sweep_plan,
                    "parent_variant_manifest.variant_manifest_id",
                )
                if found and parent_sweep.get("manifest_id") != sweep_manifest_id:
                    errors.append(
                        f"{path}: parent_sweep_plan.manifest_id must equal sweep plan parent "
                        "manifest ID"
                    )
                found, sweep_manifest_hash = _get_path(
                    sweep_plan,
                    "parent_variant_manifest.manifest_hash",
                )
                if found and parent_sweep.get("manifest_hash") != sweep_manifest_hash:
                    errors.append(
                        f"{path}: parent_sweep_plan.manifest_hash must equal sweep plan parent "
                        "manifest hash"
                    )
                committed_count = _sweep_committed_count(sweep_plan)
                if committed_count is not None and (
                    parent_sweep.get("committed_population_count") != committed_count
                ):
                    errors.append(
                        f"{path}: parent_sweep_plan.committed_population_count must equal "
                        "parent sweep plan committed count"
                    )
                selected_count = _sweep_selected_count(sweep_plan)
                if selected_count is not None and parent_sweep.get("selected_variant_count") != selected_count:
                    errors.append(
                        f"{path}: parent_sweep_plan.selected_variant_count must equal "
                        "parent sweep plan selected count"
                    )
                computed_sweep_hash = _sweep_identity_hash(sweep_plan)
                if parent_sweep.get("sweep_plan_identity_hash") != computed_sweep_hash:
                    errors.append(
                        f"{path}: parent_sweep_plan.sweep_plan_identity_hash mismatch: "
                        f"declared {parent_sweep.get('sweep_plan_identity_hash')!r}, "
                        f"computed {computed_sweep_hash}"
                    )

    lineage = payload.get("lineage")
    parent_chain = lineage.get("parent_hash_chain") if isinstance(lineage, dict) else None
    if isinstance(parent_chain, dict):
        if isinstance(parent_spec, dict) and (
            parent_chain.get("strategy_spec_hash") != parent_spec.get("strategy_spec_hash")
        ):
            errors.append(f"{path}: lineage.parent_hash_chain.strategy_spec_hash mismatch")
        if isinstance(parent_manifest, dict) and (
            parent_chain.get("variant_manifest_hash") != parent_manifest.get("manifest_hash")
        ):
            errors.append(f"{path}: lineage.parent_hash_chain.variant_manifest_hash mismatch")
        if isinstance(parent_sweep, dict) and (
            parent_chain.get("sweep_plan_identity_hash")
            != parent_sweep.get("sweep_plan_identity_hash")
        ):
            errors.append(f"{path}: lineage.parent_hash_chain.sweep_plan_identity_hash mismatch")
        input_hash = payload.get("input_identity_hash", {}).get("hash")
        if parent_chain.get("input_identity_hash") != input_hash:
            errors.append(f"{path}: lineage.parent_hash_chain.input_identity_hash mismatch")

    return errors, strategy_spec, manifest, sweep_plan


def _validate_denominator_integrity(
    path: Path,
    payload: Mapping[str, Any],
    manifest: Mapping[str, Any] | None,
    sweep_plan: Mapping[str, Any] | None,
) -> list[str]:
    errors: list[str] = []
    snapshot = payload.get("committed_denominator_snapshot")
    counts = payload.get("outcome_category_counts")
    rows = payload.get("variant_result_rows")
    parent_manifest = payload.get("parent_variant_manifest")
    parent_sweep = payload.get("parent_sweep_plan")
    if not isinstance(snapshot, dict) or not isinstance(counts, dict) or not isinstance(rows, list):
        return errors

    errors.extend(_validate_true_flags(path, payload, "committed_denominator_snapshot", DENOMINATOR_TRUE_FLAGS))
    committed_denominator = snapshot.get("committed_denominator")
    category_sum = sum(counts.get(category, 0) for category in OUTCOME_CATEGORIES)
    actual_row_count = len(rows)
    if counts.get("counts_sum") != category_sum:
        errors.append(f"{path}: outcome_category_counts.counts_sum must equal actual category sum")
    if snapshot.get("outcome_counts_sum") != category_sum:
        errors.append(f"{path}: committed_denominator_snapshot.outcome_counts_sum must equal actual category sum")
    if committed_denominator != category_sum:
        errors.append(f"{path}: outcome category counts must sum to committed denominator")
    if snapshot.get("result_row_count") != actual_row_count:
        errors.append(f"{path}: committed_denominator_snapshot.result_row_count must equal actual row count")
    if committed_denominator != actual_row_count:
        errors.append(f"{path}: result row count must equal committed denominator")
    if isinstance(parent_manifest, dict) and (
        committed_denominator != parent_manifest.get("committed_population_count")
    ):
        errors.append(f"{path}: committed denominator must equal parent manifest committed count")
    if isinstance(parent_sweep, dict) and (
        committed_denominator != parent_sweep.get("committed_population_count")
    ):
        errors.append(f"{path}: committed denominator must equal parent sweep plan committed count")
    if manifest is not None:
        manifest_count = _manifest_committed_count(manifest)
        if manifest_count is not None and committed_denominator != manifest_count:
            errors.append(f"{path}: committed denominator must equal parent manifest artifact count")
    if sweep_plan is not None:
        sweep_count = _sweep_committed_count(sweep_plan)
        if sweep_count is not None and committed_denominator != sweep_count:
            errors.append(f"{path}: committed denominator must equal parent sweep plan artifact count")

    actual_counts = {category: 0 for category in OUTCOME_CATEGORIES}
    for row in rows:
        if isinstance(row, dict) and row.get("outcome_category") in actual_counts:
            actual_counts[row["outcome_category"]] += 1
    for category, actual_count in actual_counts.items():
        if counts.get(category) != actual_count:
            errors.append(
                f"{path}: outcome_category_counts.{category} {counts.get(category)!r} "
                f"does not match result rows {actual_count}"
            )
    return errors


def _validate_complete_population(
    path: Path,
    payload: Mapping[str, Any],
    manifest: Mapping[str, Any] | None,
) -> list[str]:
    rows = payload.get("variant_result_rows")
    if not isinstance(rows, list):
        return []

    errors: list[str] = []
    row_ids: set[str] = set()
    variant_ids: set[str] = set()
    duplicate_row_ids: set[str] = set()
    duplicate_variant_ids: set[str] = set()
    result_population_id = payload.get("result_population_id")
    parent_manifest_id = payload.get("parent_variant_manifest", {}).get("variant_manifest_id")
    parent_sweep_id = payload.get("parent_sweep_plan", {}).get("sweep_plan_id")
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            continue
        row_id = row.get("row_id")
        variant_id = row.get("variant_id")
        if isinstance(row_id, str):
            if row_id in row_ids:
                duplicate_row_ids.add(row_id)
            row_ids.add(row_id)
            if isinstance(result_population_id, str) and not row_id.startswith(f"{result_population_id}-ROW-"):
                errors.append(f"{path}: variant_result_rows.{index}.row_id must align to result_population_id")
        if isinstance(variant_id, str):
            if variant_id in variant_ids:
                duplicate_variant_ids.add(variant_id)
            variant_ids.add(variant_id)
        lineage = row.get("lineage")
        if isinstance(lineage, dict):
            if lineage.get("parent_variant_id") != variant_id:
                errors.append(f"{path}: variant_result_rows.{index}.lineage.parent_variant_id mismatch")
            if lineage.get("parent_manifest_id") != parent_manifest_id:
                errors.append(f"{path}: variant_result_rows.{index}.lineage.parent_manifest_id mismatch")
            if lineage.get("parent_sweep_plan_id") != parent_sweep_id:
                errors.append(f"{path}: variant_result_rows.{index}.lineage.parent_sweep_plan_id mismatch")
    for row_id in sorted(duplicate_row_ids):
        errors.append(f"{path}: duplicate variant result row_id {row_id}")
    for variant_id in sorted(duplicate_variant_ids):
        errors.append(f"{path}: duplicate variant result variant_id {variant_id}")

    if manifest is not None:
        parent_ids = _manifest_variant_ids(manifest)
        for variant_id in sorted(variant_ids - parent_ids):
            errors.append(f"{path}: result row variant outside parent manifest: {variant_id}")
        for variant_id in sorted(parent_ids - variant_ids):
            errors.append(f"{path}: parent manifest variant missing result row: {variant_id}")
        manifest_count = _manifest_committed_count(manifest)
        if manifest_count is not None and len(rows) != manifest_count:
            errors.append(f"{path}: result row count differs from parent manifest committed count")
    return errors


def _validate_result_rows(path: Path, payload: Mapping[str, Any]) -> list[str]:
    rows = payload.get("variant_result_rows")
    if not isinstance(rows, list):
        return []

    errors: list[str] = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            continue
        row_path = f"variant_result_rows.{index}"
        for object_name, flag in (
            ("non_success", "counts_in_denominator"),
            ("error", "counts_in_denominator"),
            ("data_coverage", "counts_in_denominator"),
        ):
            child = row.get(object_name)
            if isinstance(child, dict) and child.get(flag) is not True:
                errors.append(f"{path}: {row_path}.{object_name}.{flag} must be true")
        row_mutation = row.get("row_mutation_policy")
        if isinstance(row_mutation, dict):
            for flag in ROW_MUTATION_TRUE_FLAGS:
                if row_mutation.get(flag) is not True:
                    errors.append(f"{path}: {row_path}.row_mutation_policy.{flag} must be true")
        outcome = row.get("outcome_category")
        if outcome != "successful":
            non_success = row.get("non_success")
            error = row.get("error")
            data_coverage = row.get("data_coverage")
            has_marker = False
            if isinstance(non_success, dict) and (
                non_success.get("reason") or non_success.get("rule_ref")
            ):
                has_marker = True
            if isinstance(error, dict) and (
                error.get("error_category") or error.get("error_message_class")
            ):
                has_marker = True
            if isinstance(data_coverage, dict) and data_coverage.get("data_slice_identity"):
                has_marker = True
            if not has_marker:
                errors.append(f"{path}: {row_path} non-success outcome requires a reason/error/data marker")
        metrics = row.get("metrics")
        if isinstance(metrics, dict):
            for metric_key in metrics:
                if metric_key.lower() in AUTHORITY_KEY_TOKENS:
                    errors.append(f"{path}: {row_path}.metrics has authority-like key {metric_key}")
    return errors


def _collect_strategy_data_ref_features(value: Any) -> set[str]:
    features: set[str] = set()
    if isinstance(value, Mapping):
        if value.get("operand_type") == "data_ref":
            field = value.get("field")
            if isinstance(field, str) and field not in OHLCV_DATA_FIELDS:
                features.add(field)
        for child in value.values():
            features.update(_collect_strategy_data_ref_features(child))
    elif isinstance(value, list):
        for child in value:
            features.update(_collect_strategy_data_ref_features(child))
    return features


def _collect_strategy_host_data_features(strategy_spec: Mapping[str, Any]) -> set[str]:
    timeframe_and_data = strategy_spec.get("timeframe_and_data")
    host_data_refs = (
        timeframe_and_data.get("host_data_refs")
        if isinstance(timeframe_and_data, Mapping)
        else None
    )
    if not isinstance(host_data_refs, list):
        return set()
    features: set[str] = set()
    for host_ref in host_data_refs:
        if not isinstance(host_ref, Mapping) or host_ref.get("stream") == "indicator_catalog":
            continue
        field = host_ref.get("field")
        if isinstance(field, str) and field not in OHLCV_DATA_FIELDS:
            features.add(field)
    return features


def _validate_data_availability_claim(
    path: Path,
    payload: Mapping[str, Any],
    strategy_spec: Mapping[str, Any] | None,
    catalog: Mapping[str, Any],
) -> list[str]:
    claim = payload.get("data_availability_claim")
    if claim is None:
        return []
    if not isinstance(claim, Mapping):
        return []

    errors: list[str] = []
    for identity_key in ("input_identity_hash", "result_population_identity_hash"):
        scope = payload.get(identity_key, {}).get("hash_scope")
        if isinstance(scope, list) and DATA_AVAILABILITY_CLAIM_HASH_SCOPE_PATH not in scope:
            errors.append(
                f"{path}: {identity_key}.hash_scope must include data_availability_claim when present"
            )

    if strategy_spec is None:
        errors.append(f"{path}: data_availability_claim requires a resolvable parent Strategy Spec")
        return errors

    referenced_features = _collect_strategy_data_ref_features(strategy_spec)
    referenced_features.update(_collect_strategy_host_data_features(strategy_spec))
    feature_sources = claim.get("feature_sources")
    overrides = claim.get("historical_dataset_overrides")
    if not isinstance(feature_sources, list) or not isinstance(overrides, list):
        return errors

    source_bindings: dict[str, Mapping[str, Any]] = {}
    for index, binding in enumerate(feature_sources):
        if not isinstance(binding, Mapping):
            continue
        feature = binding.get("feature_name")
        if not isinstance(feature, str):
            continue
        if feature in source_bindings:
            errors.append(
                f"{path}: data_availability_claim.feature_sources.{index} duplicates {feature}"
            )
        source_bindings[feature] = binding

    override_bindings: dict[str, Mapping[str, Any]] = {}
    for index, override in enumerate(overrides):
        if not isinstance(override, Mapping):
            continue
        feature = override.get("feature_name")
        if not isinstance(feature, str):
            continue
        if feature in override_bindings:
            errors.append(
                f"{path}: data_availability_claim.historical_dataset_overrides.{index} "
                f"duplicates {feature}"
            )
        override_bindings[feature] = override

    missing_bindings = sorted(referenced_features - source_bindings.keys())
    extra_bindings = sorted(source_bindings.keys() - referenced_features)
    extra_overrides = sorted(override_bindings.keys() - referenced_features)
    if missing_bindings:
        errors.append(
            f"{path}: full-history claim missing source bindings for: {', '.join(missing_bindings)}"
        )
    if extra_bindings:
        errors.append(
            f"{path}: full-history claim has unreferenced feature bindings: {', '.join(extra_bindings)}"
        )
    if extra_overrides:
        errors.append(
            f"{path}: full-history claim has unreferenced dataset overrides: "
            f"{', '.join(extra_overrides)}"
        )

    catalog_index = build_catalog_index(catalog)
    catalog_features = {
        key[0]
        for key in catalog_index
    }
    for feature in sorted(referenced_features):
        binding = source_bindings.get(feature)
        if binding is None:
            if feature not in catalog_features:
                errors.append(f"{path}: unknown data-derived feature availability label: {feature}")
            continue
        source_class = binding.get("source_class")
        entry = catalog_index.get((feature, source_class)) if isinstance(source_class, str) else None
        if entry is None:
            errors.append(
                f"{path}: unknown availability source binding for {feature}: {source_class!r}"
            )
            continue

        if entry.get("canonical_full_history_allowed") == "conditional":
            assertions = binding.get("condition_assertions")
            if not isinstance(assertions, list) or not assertions:
                errors.append(
                    f"{path}: conditional full-history source {feature}/{source_class} "
                    "requires condition_assertions"
                )

        if entry.get("coverage_class") == "FULL_HISTORY_PUBLIC_ARCHIVE":
            continue

        override = override_bindings.get(feature)
        if override is None:
            errors.append(
                f"{path}: {feature}/{source_class} is {entry.get('coverage_class')} and cannot "
                "support FULL_HISTORY without an explicit historical dataset override/provenance"
            )
            continue
        if entry.get("requires_vendor_or_captured_data") is True and override.get(
            "override_type"
        ) not in {"VENDOR_HISTORICAL_DATASET", "CAPTURED_HISTORICAL_DATASET"}:
            errors.append(
                f"{path}: {feature} requires a vendor or captured historical dataset override"
            )

    return errors


def _validate_append_only_ledger(path: Path, payload: Mapping[str, Any]) -> list[str]:
    errors = _validate_true_flags(path, payload, "append_only_ledger", APPEND_ONLY_TRUE_FLAGS)
    ledger = payload.get("append_only_ledger")
    status = payload.get("status")
    if not isinstance(ledger, dict):
        return errors
    if status != "draft" and not ledger.get("creation_event_ref"):
        errors.append(f"{path}: append_only_ledger.creation_event_ref is required when status is not draft")
    events = ledger.get("events")
    if not isinstance(events, list):
        return errors

    event_ids: set[str] = set()
    event_types: set[str] = set()
    for index, event in enumerate(events):
        if not isinstance(event, dict):
            continue
        event_id = event.get("event_id")
        event_type = event.get("event_type")
        if isinstance(event_id, str):
            if event_id in event_ids:
                errors.append(f"{path}: duplicate append_only_ledger.events event_id {event_id}")
            event_ids.add(event_id)
        if isinstance(event_type, str):
            event_types.add(event_type)
            if event_type not in LEDGER_EVENT_TYPES:
                errors.append(f"{path}: append_only_ledger.events.{index}.event_type invalid: {event_type}")
            if event_type.lower() in AUTHORITY_KEY_TOKENS:
                errors.append(f"{path}: append_only_ledger.events.{index}.event_type implies authority")
        for key_path, key in _walk_keys(event, ["append_only_ledger", "events", str(index)]):
            key_lower = key.lower()
            if key_lower in AUTHORITY_KEY_TOKENS:
                errors.append(f"{path}: append-only ledger event key implies authority: {key_path}")
    if "created" not in event_types:
        errors.append(f"{path}: append_only_ledger.events must include a created event")
    return errors


def _validate_non_authority(path: Path, payload: Mapping[str, Any]) -> list[str]:
    errors = _validate_true_flags(
        path,
        payload,
        "non_authority_declaration",
        NON_AUTHORITY_TRUE_FLAGS,
    )
    errors.extend(
        _validate_true_flags(
            path,
            payload,
            "review.non_authority_acknowledgement",
            REVIEW_NON_AUTHORITY_TRUE_FLAGS,
        )
    )
    found, declaration = _get_path(payload, "non_authority_declaration")
    if found and isinstance(declaration, dict) and (
        declaration.get("canonical_evidence_relationship") != "reference_only"
    ):
        errors.append(
            f"{path}: non_authority_declaration.canonical_evidence_relationship "
            "must be reference_only"
        )
    found, review = _get_path(payload, "review")
    if found and isinstance(review, dict):
        if review.get("review_status") == "approved":
            errors.append(f"{path}: review.review_status must not be approved")
        if review.get("review_scope") not in {"none", "research_visibility_only"}:
            errors.append(f"{path}: review.review_scope is outside allowed non-authority scopes")
    found, validation_summary = _get_path(payload, "validation_summary")
    if found and isinstance(validation_summary, dict):
        if validation_summary.get("validator_authority_boundary") != "evidence_only_no_approval_no_execution":
            errors.append(f"{path}: validation_summary.validator_authority_boundary is invalid")
        for flag in VALIDATION_SUMMARY_TRUE_FLAGS:
            if validation_summary.get(flag) is not True:
                errors.append(f"{path}: validation_summary.{flag} must be true")
    return errors


def _validate_forbidden_keys(path: Path, payload: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    for key_path, key in _walk_keys(payload, []):
        lower_key = key.lower()
        if lower_key in ALLOWED_RECORDING_KEYS:
            continue
        if lower_key in FORBIDDEN_EXECUTABLE_KEYS:
            errors.append(f"{path}: forbidden executable/authority key name at {key_path}: {key}")
    return errors


def validate_result_populations(
    result_populations_dir: Path = DEFAULT_RESULT_POPULATIONS_DIR,
    strategy_specs_dir: Path = DEFAULT_STRATEGY_SPECS_DIR,
    variant_manifests_dir: Path = DEFAULT_VARIANT_MANIFESTS_DIR,
    sweep_plans_dir: Path = DEFAULT_SWEEP_PLANS_DIR,
    result_population_schema_path: Path = DEFAULT_RESULT_POPULATION_SCHEMA_PATH,
    strategy_spec_schema_path: Path = DEFAULT_STRATEGY_SPEC_SCHEMA_PATH,
    variant_manifest_schema_path: Path = DEFAULT_VARIANT_MANIFEST_SCHEMA_PATH,
    sweep_plan_schema_path: Path = DEFAULT_SWEEP_PLAN_SCHEMA_PATH,
    repo_root: Path = REPO_ROOT,
    data_feature_availability_catalog_path: Path = DEFAULT_DATA_FEATURE_AVAILABILITY_CATALOG_PATH,
    data_feature_availability_schema_path: Path = DEFAULT_DATA_FEATURE_AVAILABILITY_SCHEMA_PATH,
) -> list[str]:
    """Return validation errors for result-population artifacts, or [] when valid."""

    del repo_root

    result_population_files = (
        sorted(result_populations_dir.rglob("*.result_population.json"))
        if result_populations_dir.exists()
        else []
    )
    if not result_population_files:
        return []

    availability_errors = validate_data_feature_availability(
        data_feature_availability_catalog_path,
        data_feature_availability_schema_path,
    )
    if availability_errors:
        return [f"data feature availability: {error}" for error in availability_errors]
    availability_catalog = load_availability_json(data_feature_availability_catalog_path)

    result_population_schema = load_json(result_population_schema_path)
    strategy_spec_schema = load_json(strategy_spec_schema_path)
    variant_manifest_schema = load_json(variant_manifest_schema_path)
    sweep_plan_schema = load_json(sweep_plan_schema_path)
    Draft7Validator.check_schema(result_population_schema)
    Draft7Validator.check_schema(strategy_spec_schema)
    Draft7Validator.check_schema(variant_manifest_schema)
    Draft7Validator.check_schema(sweep_plan_schema)
    result_population_validator = Draft7Validator(result_population_schema)

    errors: list[str] = []
    seen_ids: set[str] = set()
    id_paths: dict[str, Path] = {}

    for path in result_population_files:
        payload, file_errors = _validate_json_file(path, result_population_validator)
        errors.extend(file_errors)
        if payload is None:
            continue
        if file_errors:
            if isinstance(payload, dict):
                errors.extend(_validate_filename_and_id(path, payload, seen_ids, id_paths))
            continue

        errors.extend(_validate_filename_and_id(path, payload, seen_ids, id_paths))
        errors.extend(_validate_closed_outcome_enum(path, payload))
        require_hash = payload.get("status") != "draft"
        errors.extend(_validate_identity_hash(path, payload, "input_identity_hash", require_hash))
        errors.extend(
            _validate_identity_hash(
                path,
                payload,
                "result_population_identity_hash",
                require_hash,
            )
        )
        errors.extend(_validate_sizing_metadata(path, payload))
        errors.extend(_validate_audit_envelope(path, payload))
        parent_errors, strategy_spec, manifest, sweep_plan = _validate_parent_artifacts(
            path,
            payload,
            strategy_specs_dir,
            variant_manifests_dir,
            sweep_plans_dir,
        )
        errors.extend(parent_errors)
        errors.extend(_validate_denominator_integrity(path, payload, manifest, sweep_plan))
        errors.extend(_validate_complete_population(path, payload, manifest))
        errors.extend(_validate_result_rows(path, payload))
        errors.extend(
            _validate_data_availability_claim(path, payload, strategy_spec, availability_catalog)
        )
        errors.extend(_validate_append_only_ledger(path, payload))
        errors.extend(_validate_non_authority(path, payload))
        errors.extend(_validate_forbidden_keys(path, payload))

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--result-populations-dir", type=Path, default=DEFAULT_RESULT_POPULATIONS_DIR)
    parser.add_argument("--strategy-specs-dir", type=Path, default=DEFAULT_STRATEGY_SPECS_DIR)
    parser.add_argument("--variant-manifests-dir", type=Path, default=DEFAULT_VARIANT_MANIFESTS_DIR)
    parser.add_argument("--sweep-plans-dir", type=Path, default=DEFAULT_SWEEP_PLANS_DIR)
    parser.add_argument(
        "--result-population-schema",
        type=Path,
        default=DEFAULT_RESULT_POPULATION_SCHEMA_PATH,
    )
    parser.add_argument("--strategy-spec-schema", type=Path, default=DEFAULT_STRATEGY_SPEC_SCHEMA_PATH)
    parser.add_argument(
        "--variant-manifest-schema",
        type=Path,
        default=DEFAULT_VARIANT_MANIFEST_SCHEMA_PATH,
    )
    parser.add_argument("--sweep-plan-schema", type=Path, default=DEFAULT_SWEEP_PLAN_SCHEMA_PATH)
    parser.add_argument(
        "--data-feature-availability-catalog",
        type=Path,
        default=DEFAULT_DATA_FEATURE_AVAILABILITY_CATALOG_PATH,
    )
    parser.add_argument(
        "--data-feature-availability-schema",
        type=Path,
        default=DEFAULT_DATA_FEATURE_AVAILABILITY_SCHEMA_PATH,
    )
    args = parser.parse_args()

    errors = validate_result_populations(
        result_populations_dir=args.result_populations_dir,
        strategy_specs_dir=args.strategy_specs_dir,
        variant_manifests_dir=args.variant_manifests_dir,
        sweep_plans_dir=args.sweep_plans_dir,
        result_population_schema_path=args.result_population_schema,
        strategy_spec_schema_path=args.strategy_spec_schema,
        variant_manifest_schema_path=args.variant_manifest_schema,
        sweep_plan_schema_path=args.sweep_plan_schema,
        repo_root=REPO_ROOT,
        data_feature_availability_catalog_path=args.data_feature_availability_catalog,
        data_feature_availability_schema_path=args.data_feature_availability_schema,
    )
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    if not args.result_populations_dir.exists():
        print(f"OK: {args.result_populations_dir} does not exist; nothing to validate")
    else:
        print(f"OK: result-population artifacts under {args.result_populations_dir} validate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
