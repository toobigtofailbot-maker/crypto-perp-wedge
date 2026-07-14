"""Standalone Gate C-VP protected writer for one bounded planning approval."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any, BinaryIO, Mapping

from jsonschema import Draft7Validator, FormatChecker

from tools.canon_intake.queue_admission import (
    QueueAdmissionError,
    repo_canonical_json_v1 as _repo_canonical_json_v1,
)


WRITER_VERSION = "variant_planning_approval_writer_v1"
APPROVAL_SCHEMA = "strategy_spec_variant_planning_approval.schema.json"
AUDIT_SCHEMA = "strategy_spec_variant_planning_approval_audit.schema.json"
APPROVAL_ROOT = Path("research/strategy_spec_variant_planning_approvals")
AUDIT_PATH = Path(
    "research/strategy_spec_variant_planning_audit/variant_planning_approvals.jsonl"
)
LOCK_PATH = Path(
    "research/strategy_spec_variant_planning_audit/.variant_planning_approval.lock"
)
GATE_C_AUDIT_PATH = "research/canonical_crossing_audit/strategy_spec_writes.jsonl"
VARIANT_MANIFEST_ROOT = Path("research/variant_manifests")
APPROVAL_ID_RE = re.compile(r"^VPAPP-[0-9]{8}-[A-Z0-9]{8}$")
VARIANT_MANIFEST_ID_RE = re.compile(r"^VM-[0-9]{4}$")
SEARCH_FAMILY_ID_RE = re.compile(r"^SF-[A-Z0-9][A-Z0-9-]{2,126}[A-Z0-9]$")


class VariantPlanningApprovalError(ValueError):
    """Approval validation or protected write failed closed."""


class VariantPlanningApprovalIntegrityCriticalError(VariantPlanningApprovalError):
    """Manual inspection is required and automatic retry is forbidden."""


def _digest(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def repo_canonical_json_v1(value: Any) -> bytes:
    """Apply the existing locked repo-local canonical JSON contract."""
    try:
        return _repo_canonical_json_v1(value)
    except QueueAdmissionError as exc:
        raise VariantPlanningApprovalError(str(exc)) from exc


def contract_core_sha256(core: Any) -> str:
    return _digest(repo_canonical_json_v1(core))


def _lexical_absolute(path: Path) -> Path:
    return path if path.is_absolute() else Path.cwd() / path


def _reject_symlink_components(path: Path, label: str) -> Path:
    lexical = _lexical_absolute(path)
    for component in reversed([lexical, *lexical.parents]):
        if component.is_symlink():
            raise VariantPlanningApprovalError(
                f"{label} contains a symlinked path component: {component}"
            )
    return lexical


def _resolve_root(repo_root: Path) -> Path:
    lexical = _reject_symlink_components(repo_root, "repo root")
    if not lexical.is_dir():
        raise VariantPlanningApprovalError("repo root must be an existing directory")
    return lexical.resolve()


def _repo_path(root: Path, value: Any, label: str) -> Path:
    if not isinstance(value, str) or not value or "\\" in value:
        raise VariantPlanningApprovalError(f"{label} must be a repo-relative POSIX path")
    pure = PurePosixPath(value)
    if pure.is_absolute() or any(part in {"", ".", ".."} for part in pure.parts):
        raise VariantPlanningApprovalError(
            f"{label} must be a lexical repo-relative POSIX path without traversal"
        )
    lexical = root.joinpath(*pure.parts)
    _reject_symlink_components(lexical, label)
    resolved = lexical.resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise VariantPlanningApprovalError(f"{label} escapes the repository") from exc
    return resolved


def _load_object(
    path: Path, label: str, *, reject_floats: bool = False
) -> tuple[dict[str, Any], bytes]:
    lexical = _reject_symlink_components(path, label)
    if lexical.is_symlink() or not lexical.is_file():
        raise VariantPlanningApprovalError(f"{label} must be a regular non-symlink file")
    try:
        raw = lexical.read_bytes()
        value = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise VariantPlanningApprovalError(f"{label} is not readable UTF-8 JSON") from exc
    if not isinstance(value, dict):
        raise VariantPlanningApprovalError(f"{label} must be a JSON object")
    if reject_floats:
        repo_canonical_json_v1(value)
    return value, raw


def _validator(root: Path, schema_name: str) -> Draft7Validator:
    schema_path = root / "research/schemas" / schema_name
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise VariantPlanningApprovalError(
            f"protected schema is not readable JSON: {schema_name}"
        ) from exc
    return Draft7Validator(schema, format_checker=FormatChecker())


def _schema_check(root: Path, schema_name: str, value: Any, label: str) -> None:
    errors = sorted(_validator(root, schema_name).iter_errors(value), key=lambda e: list(e.path))
    if errors:
        location = ".".join(str(part) for part in errors[0].path)
        suffix = f" at {location}" if location else ""
        raise VariantPlanningApprovalError(
            f"{label} schema validation failed{suffix}: {errors[0].message}"
        )


def _parse_timestamp(value: Any, label: str) -> datetime:
    if not isinstance(value, str):
        raise VariantPlanningApprovalError(
            f"{label} must be a timezone-aware RFC3339 timestamp"
        )
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise VariantPlanningApprovalError(
            f"{label} must be a timezone-aware RFC3339 timestamp"
        ) from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise VariantPlanningApprovalError(f"{label} must be timezone-aware")
    return parsed


def _read_repo_object(
    root: Path, path_value: str, label: str
) -> tuple[dict[str, Any], bytes, Path]:
    path = _repo_path(root, path_value, label)
    value, raw = _load_object(path, label)
    return value, raw, path


def _validate_gate_c_reference(
    root: Path,
    reference: Mapping[str, Any],
    parent: Mapping[str, Any],
    parent_hash: str,
) -> dict[str, Any]:
    if reference.get("audit_path") != GATE_C_AUDIT_PATH:
        raise VariantPlanningApprovalError("Gate-C audit path mismatch")
    audit_path = _repo_path(root, GATE_C_AUDIT_PATH, "Gate-C audit path")
    if audit_path.is_symlink() or not audit_path.is_file():
        raise VariantPlanningApprovalError(
            "Gate-C audit must be a regular non-symlink file"
        )
    try:
        raw = audit_path.read_bytes()
    except OSError as exc:
        raise VariantPlanningApprovalError("Gate-C audit is unreadable") from exc
    if not raw or not raw.endswith(b"\n"):
        raise VariantPlanningApprovalError(
            "Gate-C audit must contain complete LF-terminated records"
        )
    lines = raw.splitlines(keepends=True)
    records: list[dict[str, Any]] = []
    for number, raw_line in enumerate(lines, 1):
        if not raw_line.endswith(b"\n"):
            raise VariantPlanningApprovalError(
                f"Gate-C audit line {number} lacks its required line feed"
            )
        try:
            record = json.loads(raw_line.decode("utf-8"))
        except (UnicodeError, json.JSONDecodeError) as exc:
            raise VariantPlanningApprovalError(
                f"Gate-C audit line {number} is invalid UTF-8 JSON"
            ) from exc
        if not isinstance(record, dict):
            raise VariantPlanningApprovalError(
                f"Gate-C audit line {number} is not a JSON object"
            )
        records.append(record)

    line_number = reference.get("line_number")
    if not isinstance(line_number, int) or isinstance(line_number, bool):
        raise VariantPlanningApprovalError("Gate-C audit line number is invalid")
    if line_number < 1 or line_number > len(lines):
        raise VariantPlanningApprovalError("Gate-C audit line does not exist")
    raw_line = lines[line_number - 1]
    if _digest(raw_line) != reference.get("raw_record_sha256"):
        raise VariantPlanningApprovalError("Gate-C raw audit-line hash mismatch")

    expected = {
        "schema_version": "gate_c_strategy_spec_write_audit_v1",
        "approval_id": reference.get("gate_c_approval_id"),
        "approved_by": "Karl",
        "strategy_spec_id": reference.get("strategy_spec_id"),
        "canonical_target_path": reference.get("canonical_target_path"),
        "approved_content_sha256": parent_hash,
        "validation_outcome": "passed_before_write",
        "no_queue_candidate_runtime_outputs": True,
    }
    record = records[line_number - 1]
    if any(record.get(key) != value for key, value in expected.items()):
        raise VariantPlanningApprovalError(
            "Gate-C audit approval/Spec/target/content binding mismatch"
        )
    matches = sum(
        1
        for candidate in records
        if all(candidate.get(key) == value for key, value in expected.items())
    )
    if matches != 1:
        raise VariantPlanningApprovalError(
            "Gate-C audit must contain exactly one matching approval/Spec/target record"
        )
    if parent.get("strategy_spec_id") != reference.get("strategy_spec_id"):
        raise VariantPlanningApprovalError("Gate-C Strategy Spec ID mismatch")
    return record


def _validate_contract_core(
    approval: Mapping[str, Any], parent: Mapping[str, Any], parent_hash: str
) -> None:
    canonical_parent = approval["canonical_parent"]
    core = approval["variant_manifest_contract_core"]
    expected_parent = {
        "strategy_spec_id": canonical_parent["strategy_spec_id"],
        "strategy_spec_path": canonical_parent["path"],
        "strategy_spec_sha256": parent_hash,
    }
    if any(core.get(key) != value for key, value in expected_parent.items()):
        raise VariantPlanningApprovalError(
            "variant-planning contract core parent identity/path/hash mismatch"
        )
    if parent.get("strategy_spec_id") != core.get("strategy_spec_id"):
        raise VariantPlanningApprovalError(
            "variant-planning contract core parent ID is stale"
        )
    vm_id = core["variant_manifest_id"]
    expected_vm_path = (
        VARIANT_MANIFEST_ROOT / f"{vm_id}.variant_manifest.json"
    ).as_posix()
    if core.get("variant_manifest_path") != expected_vm_path:
        raise VariantPlanningApprovalError(
            "Variant Manifest path is not derived from its identifier"
        )
    axes = core["ordered_parameter_axes"]
    names = [axis["name"] for axis in axes]
    if len(set(names)) != len(names):
        raise VariantPlanningApprovalError("parameter-axis names must be unique")
    population = 1
    for axis in axes:
        values = axis.get("integer_values", axis.get("milli_values"))
        if not isinstance(values, list) or not values:
            raise VariantPlanningApprovalError("parameter axis has no exact values")
        if any(not isinstance(value, int) or isinstance(value, bool) for value in values):
            raise VariantPlanningApprovalError(
                "parameter-axis values must be exact integers or scaled integers"
            )
        population *= len(values)
    committed = core["committed_population_count"]
    cap = core["population_cap"]
    if committed != population:
        raise VariantPlanningApprovalError(
            "committed population count does not equal the ordered-axis product"
        )
    if cap < committed:
        raise VariantPlanningApprovalError(
            "population cap is smaller than the committed population count"
        )
    actual_hash = contract_core_sha256(core)
    if approval.get("contract_core_sha256") != actual_hash:
        raise VariantPlanningApprovalError("contract-core SHA-256 mismatch")


def _derived_audit_record(
    approval: Mapping[str, Any], approval_raw: bytes
) -> dict[str, Any]:
    parent = approval["canonical_parent"]
    gate_c = parent["gate_c_audit"]
    core = approval["variant_manifest_contract_core"]
    approval_id = approval["approval_id"]
    return {
        "schema_version": "strategy_spec_variant_planning_approval_audit_v1",
        "audit_record_id": f"VPAUDIT-{approval_id}",
        "approval_id": approval_id,
        "approval_path": approval["approval_artifact_target_path"],
        "approval_file_sha256": _digest(approval_raw),
        "strategy_spec_id": parent["strategy_spec_id"],
        "strategy_spec_path": parent["path"],
        "strategy_spec_sha256": parent["sha256"],
        "gate_c_audit_path": gate_c["audit_path"],
        "gate_c_audit_line_number": gate_c["line_number"],
        "gate_c_raw_record_sha256": gate_c["raw_record_sha256"],
        "gate_c_approval_id": gate_c["gate_c_approval_id"],
        "variant_manifest_id": core["variant_manifest_id"],
        "variant_manifest_path": core["variant_manifest_path"],
        "search_family_id": core["search_family_id"],
        "contract_core_sha256": approval["contract_core_sha256"],
        "committed_population_count": core["committed_population_count"],
        "approved_at": approval["approved_at"],
        "writer_version": WRITER_VERSION,
        "validation_outcome": "passed_before_write",
        "no_gate_q": True,
        "no_queue_admission": True,
        "no_dispatch": True,
        "no_research_execution": True,
        "no_result_population": True,
        "no_candidate_action": True,
        "no_runtime_or_paper_live": True,
    }


def _validate_approval_file(
    root: Path, approval_path: Path, label: str
) -> dict[str, Any]:
    approval, approval_raw = _load_object(
        approval_path, label, reject_floats=True
    )
    _schema_check(root, APPROVAL_SCHEMA, approval, label)
    approval_id = approval["approval_id"]
    if not APPROVAL_ID_RE.fullmatch(approval_id):
        raise VariantPlanningApprovalError("approval identifier is malformed")
    target_rel = (
        APPROVAL_ROOT / f"{approval_id}.variant_planning_approval.json"
    ).as_posix()
    if approval["approval_artifact_target_path"] != target_rel:
        raise VariantPlanningApprovalError(
            "approval target path is not derived from its identifier"
        )
    _parse_timestamp(approval["approved_at"], "approved_at")

    parent_ref = approval["canonical_parent"]
    expected_parent_path = (
        Path("research/strategy_specs")
        / f"{parent_ref['strategy_spec_id']}.strategy_spec.json"
    ).as_posix()
    if parent_ref["path"] != expected_parent_path:
        raise VariantPlanningApprovalError(
            "canonical parent path is not derived from its identifier"
        )
    parent, parent_raw, _ = _read_repo_object(
        root, parent_ref["path"], "canonical parent Strategy Spec"
    )
    parent_hash = _digest(parent_raw)
    if parent_ref["sha256"] != parent_hash:
        raise VariantPlanningApprovalError("canonical parent Strategy Spec hash mismatch")
    if parent.get("strategy_spec_id") != parent_ref["strategy_spec_id"]:
        raise VariantPlanningApprovalError("canonical parent Strategy Spec ID mismatch")
    if parent.get("status") != parent_ref["embedded_status"]:
        raise VariantPlanningApprovalError("canonical parent embedded status mismatch")
    if parent.get("status") != "review_requested":
        raise VariantPlanningApprovalError(
            "standalone Gate C-VP requires a review_requested canonical parent"
        )
    gate_c_ref = parent_ref["gate_c_audit"]
    if (
        gate_c_ref["strategy_spec_id"] != parent_ref["strategy_spec_id"]
        or gate_c_ref["canonical_target_path"] != parent_ref["path"]
    ):
        raise VariantPlanningApprovalError(
            "Gate-C audit reference does not bind the canonical parent"
        )
    _validate_gate_c_reference(root, gate_c_ref, parent, parent_hash)
    _validate_contract_core(approval, parent, parent_hash)
    record = _derived_audit_record(approval, approval_raw)
    _schema_check(root, AUDIT_SCHEMA, record, "derived approval audit record")
    return {
        "approval": approval,
        "approval_raw": approval_raw,
        "approval_id": approval_id,
        "target_rel": target_rel,
        "record": record,
        "variant_manifest_id": record["variant_manifest_id"],
        "variant_manifest_path": record["variant_manifest_path"],
        "search_family_id": record["search_family_id"],
    }


def _read_historical_audit(root: Path, audit_path: Path) -> list[dict[str, Any]]:
    if not audit_path.exists():
        return []
    if audit_path.is_symlink() or not audit_path.is_file():
        raise VariantPlanningApprovalError(
            "variant-planning audit must be a regular non-symlink file"
        )
    try:
        raw = audit_path.read_bytes()
    except OSError as exc:
        raise VariantPlanningApprovalError(
            "existing variant-planning audit is unreadable"
        ) from exc
    if not raw:
        return []
    if not raw.endswith(b"\n"):
        raise VariantPlanningApprovalError(
            "existing variant-planning audit has a partial non-LF-terminated record"
        )
    records: list[dict[str, Any]] = []
    seen: dict[str, set[str]] = {
        "audit_record_id": set(),
        "approval_id": set(),
        "approval_path": set(),
        "variant_manifest_id": set(),
        "variant_manifest_path": set(),
        "search_family_id": set(),
    }
    for number, raw_line in enumerate(raw.splitlines(keepends=True), 1):
        if not raw_line.endswith(b"\n"):
            raise VariantPlanningApprovalError(
                f"existing variant-planning audit line {number} lacks LF"
            )
        try:
            record = json.loads(raw_line.decode("utf-8"))
        except (UnicodeError, json.JSONDecodeError) as exc:
            raise VariantPlanningApprovalError(
                f"existing variant-planning audit line {number} is invalid UTF-8 JSON"
            ) from exc
        if not isinstance(record, dict):
            raise VariantPlanningApprovalError(
                f"existing variant-planning audit line {number} is not an object"
            )
        if raw_line != repo_canonical_json_v1(record) + b"\n":
            raise VariantPlanningApprovalError(
                f"existing variant-planning audit line {number} is not canonical JSON plus one LF"
            )
        _schema_check(
            root,
            AUDIT_SCHEMA,
            record,
            f"existing variant-planning audit line {number}",
        )
        expected_path = (
            APPROVAL_ROOT
            / f"{record['approval_id']}.variant_planning_approval.json"
        ).as_posix()
        if (
            record["audit_record_id"] != f"VPAUDIT-{record['approval_id']}"
            or record["approval_path"] != expected_path
            or record["variant_manifest_path"]
            != (
                VARIANT_MANIFEST_ROOT
                / f"{record['variant_manifest_id']}.variant_manifest.json"
            ).as_posix()
            or record["strategy_spec_path"]
            != (
                Path("research/strategy_specs")
                / f"{record['strategy_spec_id']}.strategy_spec.json"
            ).as_posix()
        ):
            raise VariantPlanningApprovalError(
                f"existing variant-planning audit line {number} has inconsistent ID/path bindings"
            )
        for field, values in seen.items():
            value = record[field]
            if value in values:
                raise VariantPlanningApprovalError(
                    f"existing variant-planning audit contains duplicate {field}"
                )
            values.add(value)
        approval_path = _repo_path(
            root, record["approval_path"], f"historical approval line {number}"
        )
        historical = _validate_approval_file(
            root, approval_path, f"historical approval line {number}"
        )
        if historical["record"] != record:
            raise VariantPlanningApprovalError(
                f"historical audit line {number} disagrees with validated approval evidence"
            )
        records.append(record)
    return records


def _scan_approval_corpus(root: Path) -> list[dict[str, Any]]:
    directory = _repo_path(root, APPROVAL_ROOT.as_posix(), "approval corpus")
    if not directory.exists():
        return []
    if directory.is_symlink() or not directory.is_dir():
        raise VariantPlanningApprovalError(
            "approval corpus must be a regular non-symlink directory"
        )
    approvals: list[dict[str, Any]] = []
    seen: dict[str, set[str]] = {
        "approval_id": set(),
        "target_rel": set(),
        "variant_manifest_id": set(),
        "variant_manifest_path": set(),
        "search_family_id": set(),
    }
    for path in sorted(directory.iterdir(), key=lambda candidate: candidate.name):
        if (
            path.is_symlink()
            or not path.is_file()
            or not path.name.endswith(".variant_planning_approval.json")
        ):
            raise VariantPlanningApprovalError(
                f"unexpected entry in authoritative approval corpus: {path.name}"
            )
        bundle = _validate_approval_file(root, path, f"approval corpus {path.name}")
        expected = _repo_path(root, bundle["target_rel"], "approval corpus target")
        if path.resolve() != expected:
            raise VariantPlanningApprovalError(
                f"approval corpus file is not at its ID-derived path: {path.name}"
            )
        for field, values in seen.items():
            value = bundle[field]
            if value in values:
                raise VariantPlanningApprovalError(
                    f"approval corpus contains duplicate {field}"
                )
            values.add(value)
        approvals.append(bundle)
    return approvals


def _scan_variant_manifest_corpus(root: Path) -> list[dict[str, str]]:
    directory = _repo_path(root, VARIANT_MANIFEST_ROOT.as_posix(), "Variant Manifest corpus")
    if not directory.exists():
        return []
    if directory.is_symlink() or not directory.is_dir():
        raise VariantPlanningApprovalError(
            "Variant Manifest corpus must be a regular non-symlink directory"
        )
    manifests: list[dict[str, str]] = []
    seen_ids: set[str] = set()
    seen_paths: set[str] = set()
    seen_search_families: set[str] = set()
    for path in sorted(directory.glob("*.variant_manifest.json")):
        value, _ = _load_object(path, f"Variant Manifest corpus {path.name}")
        vm_id = value.get("variant_manifest_id")
        if not isinstance(vm_id, str) or not VARIANT_MANIFEST_ID_RE.fullmatch(vm_id):
            raise VariantPlanningApprovalError(
                f"Variant Manifest corpus has malformed identifier: {path.name}"
            )
        relative = (VARIANT_MANIFEST_ROOT / path.name).as_posix()
        expected = (
            VARIANT_MANIFEST_ROOT / f"{vm_id}.variant_manifest.json"
        ).as_posix()
        search_family = (
            value.get("population_governance", {})
            .get("multiple_testing_accounting", {})
            .get("search_family_id")
        )
        if (
            relative != expected
            or not isinstance(search_family, str)
            or not SEARCH_FAMILY_ID_RE.fullmatch(search_family)
        ):
            raise VariantPlanningApprovalError(
                f"Variant Manifest corpus has inconsistent path/search-family binding: {path.name}"
            )
        if vm_id in seen_ids or relative in seen_paths or search_family in seen_search_families:
            raise VariantPlanningApprovalError(
                "Variant Manifest corpus contains duplicate ID, path, or search family"
            )
        seen_ids.add(vm_id)
        seen_paths.add(relative)
        seen_search_families.add(search_family)
        manifests.append(
            {
                "variant_manifest_id": vm_id,
                "variant_manifest_path": relative,
                "search_family_id": search_family,
            }
        )
    return manifests


def _check_reuse(
    bundle: Mapping[str, Any],
    historical: list[dict[str, Any]],
    approvals: list[dict[str, Any]],
    manifests: list[dict[str, str]],
) -> None:
    collision_fields = (
        "approval_id",
        "variant_manifest_id",
        "variant_manifest_path",
        "search_family_id",
    )
    candidate_values = {field: bundle[field] for field in collision_fields}
    candidate_values["approval_path"] = bundle["target_rel"]
    for record in historical:
        for field, value in candidate_values.items():
            if record.get(field) == value:
                raise VariantPlanningApprovalError(
                    f"historical audit permanently reserves {field}: {value}"
                )
    for existing in approvals:
        existing_values = {
            "approval_id": existing["approval_id"],
            "approval_path": existing["target_rel"],
            "variant_manifest_id": existing["variant_manifest_id"],
            "variant_manifest_path": existing["variant_manifest_path"],
            "search_family_id": existing["search_family_id"],
        }
        for field, value in candidate_values.items():
            if existing_values.get(field) == value:
                raise VariantPlanningApprovalError(
                    f"approval corpus already reserves {field}: {value}"
                )
    for manifest in manifests:
        for field in (
            "variant_manifest_id",
            "variant_manifest_path",
            "search_family_id",
        ):
            if manifest[field] == candidate_values[field]:
                raise VariantPlanningApprovalError(
                    f"Variant Manifest corpus already reserves {field}: {candidate_values[field]}"
                )


def _validate_history_alignment(
    historical: list[dict[str, Any]], approvals: list[dict[str, Any]]
) -> None:
    history_by_id = {record["approval_id"]: record for record in historical}
    approvals_by_id = {bundle["approval_id"]: bundle for bundle in approvals}
    if history_by_id.keys() != approvals_by_id.keys():
        raise VariantPlanningApprovalError(
            "authoritative approval corpus and audit history disagree"
        )
    for approval_id, bundle in approvals_by_id.items():
        if bundle["record"] != history_by_id[approval_id]:
            raise VariantPlanningApprovalError(
                f"authoritative approval and audit evidence disagree for {approval_id}"
            )


def _validate_candidate(root: Path, approval_path: Path) -> dict[str, Any]:
    bundle = _validate_approval_file(root, approval_path, "proposed planning approval")
    target = _repo_path(root, bundle["target_rel"], "approval target")
    if target.exists() or target.is_symlink():
        raise VariantPlanningApprovalError(
            "approval target already exists; overwrite and duplicate submission are forbidden"
        )
    audit = _repo_path(root, AUDIT_PATH.as_posix(), "variant-planning audit path")
    historical = _read_historical_audit(root, audit)
    approvals = _scan_approval_corpus(root)
    manifests = _scan_variant_manifest_corpus(root)
    _validate_history_alignment(historical, approvals)
    _check_reuse(bundle, historical, approvals, manifests)
    return bundle


@contextmanager
def _crossing_lock(root: Path):
    path = _repo_path(root, LOCK_PATH.as_posix(), "variant-planning lock path")
    path.parent.mkdir(parents=True, exist_ok=True)
    _reject_symlink_components(path, "variant-planning lock path")
    state = {"crossing_committed": False}
    try:
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise VariantPlanningApprovalError(
            "variant-planning lock exists; stale locks require operator inspection"
        ) from exc
    try:
        os.write(fd, f"pid={os.getpid()}\n".encode("ascii"))
        os.fsync(fd)
        os.close(fd)
        fd = -1
        yield state
    finally:
        if fd >= 0:
            os.close(fd)
        try:
            path.unlink()
        except FileNotFoundError:
            pass
        except OSError as exc:
            if state["crossing_committed"]:
                raise VariantPlanningApprovalIntegrityCriticalError(
                    "approval and audit commit occurred but lock cleanup failed; "
                    "automatic retry is forbidden and operator inspection is required"
                ) from exc
            raise VariantPlanningApprovalIntegrityCriticalError(
                "variant-planning lock cleanup failed; operator inspection is required"
            ) from exc


def _open_audit(path: Path) -> tuple[BinaryIO, bool]:
    try:
        return path.open("x+b"), True
    except FileExistsError:
        return path.open("r+b"), False


def write_variant_planning_approval(
    *, repo_root: Path, approval_path: Path
) -> dict[str, Any]:
    root = _resolve_root(repo_root)
    _validate_candidate(root, approval_path)
    with _crossing_lock(root) as state:
        bundle = _validate_candidate(root, approval_path)
        target = _repo_path(root, bundle["target_rel"], "approval target")
        audit = _repo_path(root, AUDIT_PATH.as_posix(), "variant-planning audit path")
        target.parent.mkdir(parents=True, exist_ok=True)
        audit.parent.mkdir(parents=True, exist_ok=True)
        target = _repo_path(root, bundle["target_rel"], "approval target")
        audit = _repo_path(root, AUDIT_PATH.as_posix(), "variant-planning audit path")
        if target.exists() or target.is_symlink():
            raise VariantPlanningApprovalError(
                "approval target already exists; overwrite and duplicate submission are forbidden"
            )
        approval_raw = bundle["approval_raw"]
        record = bundle["record"]
        line = repo_canonical_json_v1(record) + b"\n"
        audit_handle: BinaryIO | None = None
        audit_created = False
        prior_length = 0
        target_created = False
        try:
            with target.open("xb") as output:
                target_created = True
                if output.write(approval_raw) != len(approval_raw):
                    raise OSError("partial approval write")
                output.flush()
                os.fsync(output.fileno())
            audit_handle, audit_created = _open_audit(audit)
            audit_handle.seek(0, os.SEEK_END)
            prior_length = audit_handle.tell()
            if audit_handle.write(line) != len(line):
                raise OSError("partial audit append")
            audit_handle.flush()
            os.fsync(audit_handle.fileno())
            audit_handle.close()
            state["crossing_committed"] = True
            return record
        except (OSError, ValueError) as exc:
            rollback_failures: list[str] = []
            if audit_handle is not None:
                try:
                    audit_handle.seek(prior_length)
                    audit_handle.truncate()
                    audit_handle.flush()
                    os.fsync(audit_handle.fileno())
                    audit_handle.close()
                    if audit_created and prior_length == 0:
                        audit.unlink()
                except (OSError, ValueError) as rollback_exc:
                    rollback_failures.append(f"audit rollback failed: {rollback_exc}")
            if target_created:
                try:
                    target.unlink()
                except (OSError, ValueError) as rollback_exc:
                    rollback_failures.append(f"approval rollback failed: {rollback_exc}")
            if rollback_failures:
                raise VariantPlanningApprovalIntegrityCriticalError(
                    "; ".join(rollback_failures) + "; automatic retry is forbidden"
                ) from exc
            raise VariantPlanningApprovalError(
                "approval/audit crossing failed and was rolled back"
            ) from exc


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--approval", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    try:
        record = write_variant_planning_approval(
            repo_root=args.repo_root, approval_path=args.approval
        )
    except VariantPlanningApprovalError as exc:
        parser.exit(2, f"Gate C-VP approval write stopped: {exc}\n")
    print(json.dumps(record, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
