"""Offline fail-closed validation for exact single-use dispatch authorizations.

This module is read-only.  It never creates an authorization, appends an audit
event, creates a dispatch, or invokes a runner.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import subprocess
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Literal, Mapping

from jsonschema import Draft7Validator, FormatChecker

from tools.canon_intake.queue_admission import (
    QueueAdmissionError,
    approval_core_sha256,
    repo_canonical_json_v1 as _repo_canonical_json_v1,
)
from tools.data.register_binance_usdtm_1d_lineage import (
    CADENCE_MS as CANONICAL_1D_CADENCE_MS,
    DATASET_ID as CANONICAL_1D_DATASET_ID,
    REQUIRED_COLUMNS as CANONICAL_1D_SOURCE_COLUMNS,
    SNAPSHOT_VERSION as CANONICAL_1D_SNAPSHOT_VERSION,
    build_lineage as build_1d_lineage,
    canonical_json_bytes as canonical_1d_catalog_bytes,
)
from tools.registry.validate_variant_sweep_artifacts import (
    canonical_json_bytes as strategy_spec_canonical_json_bytes,
)


APPROVAL_SCHEMA = "canon_dispatch_authorization.schema.json"
AUDIT_SCHEMA = "canon_dispatch_authorization_audit_event.schema.json"
DISPATCH_SCHEMA = "canon_dispatch_record.schema.json"
APPROVAL_ROOT = Path("research/queue/dispatch_authorizations")
AUDIT_PATH = Path(
    "research/queue/dispatch_authorization_audit/"
    "dispatch_authorization_events.jsonl"
)
DISPATCH_ROOT = Path("research/queue/dispatch_records")
EXECUTION_ROOT = Path("research/queue/execution_events")
APPROVAL_STATEMENT = (
    "Karl approves one single-use offline research dispatch for the exact queue "
    "item, dispatch ID, run ID, immutable dispatch manifest, lineage, dataset, "
    "funding identity, runner, budget, and output targets bound by this artifact, "
    "and grants no downstream authority."
)
AUTHORIZATION_ID_RE = re.compile(r"^KDAUTH-[A-Z0-9]+-R[0-9]+-[0-9]{4}$")
H004_AUTHORIZATION_ID_RE = re.compile(r"^KDAUTH-H004-R2-[0-9]{4}$")
H004_QUEUE_ITEM_ID = "QI-20260717-H004R2B1"
H004_GATE_Q_ID = "GATE-Q-H004-R2-04B-0001"
H004_LINEAGE_IDS = {
    "strategy_spec": "STRAT-SPEC-0007",
    "external_content_readiness": "SS-ECR-STRAT-SPEC-0007",
    "variant_planning_approval": "VPAPP-20260715-H004R201",
    "variant_manifest": "VM-0007",
    "sweep_plan": "SWEEP-PLAN-0007",
}
H004_1D_CATALOG_PATH = (
    "research/data_slices/binance_usdtm_btcusdt_1d/"
    "binance_usdtm_btcusdt_1d_20200101_20260411.catalog_slice.json"
)
H004_1D_DATA_PATH = (
    "data/processed/"
    "binance_um_perp_BTCUSDT_1d_2020-01-01_2026-04-11_2026-04-12T1655Z.parquet"
)
CANONICAL_1D_VALIDATOR_PATH = "tools/data/register_binance_usdtm_1d_lineage.py"
H004_FUNDING_PROVENANCE_PATH = (
    "research/data_provenance/funding/"
    "binance_usdtm_btcusdt_funding_events_20190910t080000z_"
    "20260412t160000z_sha256_5f0da7478ccf3514.funding_provenance.json"
)
H004_FUNDING_DATA_PATH = (
    "data/processed/"
    "binance_um_perp_BTCUSDT_funding_8h_2019-09-10_2026-04-12_"
    "2026-04-12T1655Z.parquet"
)
H004_RUNNER_MODULE = "tools.research_runner.run_offline_sweep"
H004_RUNNER_PATH = "tools/research_runner/run_offline_sweep.py"
H004_RUNNER_VERSION = "wp-s2c-190-build-test-v1"
SCRATCH_OUTPUT_ROOT_RE = re.compile(
    r"^scratch/(?:(?!\.{1,2}/)[A-Za-z0-9._-]+/)+$"
)
FRESH_COLLISION_CHECK = "fresh_collision_check"
COMMITTED_CROSSING_PROOF = "committed_crossing_proof"
ReservationHistoryPolicy = Literal[
    "fresh_collision_check",
    "committed_crossing_proof",
]


class DispatchAuthorizationError(ValueError):
    """Authorization or lifecycle validation failed closed."""


def _digest(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def repo_canonical_json_v1(value: Any) -> bytes:
    try:
        return _repo_canonical_json_v1(value)
    except QueueAdmissionError as exc:
        raise DispatchAuthorizationError(str(exc)) from exc


def authorization_core_sha256(core: Any) -> str:
    return _digest(repo_canonical_json_v1(core))


def serialize_dispatch_authorization(value: Any) -> bytes:
    """Return the exact deterministic KDAUTH whole-file serialization."""
    repo_canonical_json_v1(value)
    return (
        json.dumps(
            value,
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def _lexical_absolute(path: Path) -> Path:
    return path if path.is_absolute() else Path.cwd() / path


def _lexical_entry_exists(path: Path) -> bool:
    return os.path.lexists(path)


def _is_link_or_reparse(path: Path) -> bool:
    try:
        metadata = os.lstat(path)
    except OSError:
        return False
    if stat.S_ISLNK(metadata.st_mode):
        return True
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    file_attributes = getattr(metadata, "st_file_attributes", 0)
    return bool(reparse_flag and file_attributes & reparse_flag)


def _reject_symlink_components(path: Path, label: str) -> Path:
    lexical = _lexical_absolute(path)
    for component in reversed([lexical, *lexical.parents]):
        if _lexical_entry_exists(component) and _is_link_or_reparse(component):
            raise DispatchAuthorizationError(
                f"{label} contains a symlinked or reparse-point path component: "
                f"{component}"
            )
    return lexical


def _resolve_root(repo_root: Path) -> Path:
    lexical = _reject_symlink_components(repo_root, "repo root")
    if not lexical.is_dir():
        raise DispatchAuthorizationError("repo root must be an existing directory")
    return lexical.resolve()


def _repo_path(root: Path, value: Any, label: str) -> Path:
    if not isinstance(value, str) or not value or "\\" in value:
        raise DispatchAuthorizationError(
            f"{label} must be a repo-relative POSIX path"
        )
    pure = PurePosixPath(value)
    if pure.is_absolute() or any(part in {"", ".", ".."} for part in pure.parts):
        raise DispatchAuthorizationError(
            f"{label} must be a lexical repo-relative POSIX path without traversal"
        )
    lexical = root.joinpath(*pure.parts)
    _reject_symlink_components(lexical, label)
    resolved = lexical.resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise DispatchAuthorizationError(f"{label} escapes the repository") from exc
    return resolved


def _scratch_directory_path(root: Path, value: Any, label: str) -> Path:
    if not isinstance(value, str) or SCRATCH_OUTPUT_ROOT_RE.fullmatch(value) is None:
        raise DispatchAuthorizationError(
            f"{label} must be a lexical scratch directory path without "
            "traversal, empty or dot components, backslashes, or absolute form"
        )
    parts = value[:-1].split("/")
    scratch_lexical = root / "scratch"
    lexical = root.joinpath(*parts)
    _reject_symlink_components(lexical, label)

    resolved_scratch = scratch_lexical.resolve()
    if resolved_scratch != scratch_lexical:
        raise DispatchAuthorizationError(
            f"{label} scratch root is a symlink or junction"
        )
    resolved = lexical.resolve()
    try:
        resolved.relative_to(resolved_scratch)
    except ValueError as exc:
        raise DispatchAuthorizationError(
            f"{label} escapes the repository scratch directory"
        ) from exc
    if lexical.exists() and not lexical.is_dir():
        raise DispatchAuthorizationError(
            f"{label} must resolve to a directory when it already exists"
        )
    return resolved


def _schema_validator(root: Path, schema_name: str) -> Draft7Validator:
    schema_path = root / "research/schemas" / schema_name
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise DispatchAuthorizationError(
            f"protected schema is not readable JSON: {schema_name}"
        ) from exc
    Draft7Validator.check_schema(schema)
    return Draft7Validator(schema, format_checker=FormatChecker())


def _schema_check(
    root: Path, schema_name: str, value: Any, label: str
) -> None:
    errors = sorted(
        _schema_validator(root, schema_name).iter_errors(value),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        location = ".".join(str(part) for part in errors[0].absolute_path)
        suffix = f" at {location}" if location else ""
        raise DispatchAuthorizationError(
            f"{label} schema validation failed{suffix}: {errors[0].message}"
        )


def _parse_timestamp(value: Any, label: str) -> datetime:
    if not isinstance(value, str):
        raise DispatchAuthorizationError(
            f"{label} must be a timezone-aware RFC3339 timestamp"
        )
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise DispatchAuthorizationError(
            f"{label} must be a timezone-aware RFC3339 timestamp"
        ) from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise DispatchAuthorizationError(f"{label} must be timezone-aware")
    return parsed


def _read_bytes(path: Path, label: str) -> bytes:
    lexical = _reject_symlink_components(path, label)
    if lexical.is_symlink() or not lexical.is_file():
        raise DispatchAuthorizationError(
            f"{label} must be a regular non-symlink file"
        )
    try:
        return lexical.read_bytes()
    except OSError as exc:
        raise DispatchAuthorizationError(f"{label} is unreadable") from exc


def _decode_object(raw: bytes, label: str) -> dict[str, Any]:
    if raw.startswith(b"\xef\xbb\xbf"):
        raise DispatchAuthorizationError(f"{label} must not contain a UTF-8 BOM")
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise DispatchAuthorizationError(
            f"{label} is not readable UTF-8 JSON"
        ) from exc
    if not isinstance(value, dict):
        raise DispatchAuthorizationError(f"{label} must be a JSON object")
    return value


def _load_json_ref(
    root: Path,
    path_value: str,
    expected_hash: str,
    expected_length: int,
    label: str,
) -> tuple[dict[str, Any], bytes, Path]:
    path = _repo_path(root, path_value, f"{label}.path")
    raw = _read_bytes(path, label)
    if _digest(raw) != expected_hash:
        raise DispatchAuthorizationError(f"{label} whole-file hash mismatch")
    if len(raw) != expected_length:
        raise DispatchAuthorizationError(f"{label} byte-length mismatch")
    return _decode_object(raw, label), raw, path


def _load_raw_ref(
    root: Path,
    path_value: str,
    expected_hash: str,
    expected_length: int,
    label: str,
) -> tuple[bytes, Path]:
    path = _repo_path(root, path_value, f"{label}.path")
    raw = _read_bytes(path, label)
    if _digest(raw) != expected_hash:
        raise DispatchAuthorizationError(f"{label} whole-file hash mismatch")
    if len(raw) != expected_length:
        raise DispatchAuthorizationError(f"{label} byte-length mismatch")
    return raw, path


def _load_authorization(
    root: Path,
    authorization_path: Path,
    *,
    require_authoritative_path: bool = True,
) -> tuple[dict[str, Any], bytes, str]:
    path = _reject_symlink_components(authorization_path, "dispatch authorization")
    raw = _read_bytes(path, "dispatch authorization")
    if b"\r" in raw:
        raise DispatchAuthorizationError(
            "dispatch authorization must use LF, not CR or CRLF"
        )
    if not raw.endswith(b"\n") or raw.endswith(b"\n\n"):
        raise DispatchAuthorizationError(
            "dispatch authorization must end with exactly one LF"
        )
    value = _decode_object(raw, "dispatch authorization")
    if raw != serialize_dispatch_authorization(value):
        raise DispatchAuthorizationError(
            "dispatch authorization is not deterministic sorted two-space JSON "
            "plus exactly one LF"
        )
    _schema_check(root, APPROVAL_SCHEMA, value, "dispatch authorization")
    authorization_id = value["authorization_id"]
    if not AUTHORIZATION_ID_RE.fullmatch(authorization_id):
        raise DispatchAuthorizationError("authorization identifier is malformed")
    expected_rel = (
        APPROVAL_ROOT
        / f"{authorization_id}.dispatch_authorization.json"
    ).as_posix()
    if value["authorization_artifact_target_path"] != expected_rel:
        raise DispatchAuthorizationError(
            "authorization target path is not derived from its identifier"
        )
    expected_path = _repo_path(root, expected_rel, "authorization target path")
    if require_authoritative_path and path.resolve() != expected_path:
        raise DispatchAuthorizationError(
            "dispatch authorization is not at its authoritative ID-derived path"
        )
    _parse_timestamp(value["approved_at"], "approved_at")
    if value["approval_statement"] != APPROVAL_STATEMENT:
        raise DispatchAuthorizationError("approval statement mismatch")
    if value["authority_flags"] != value["authorization_core"]["authority_flags"]:
        raise DispatchAuthorizationError(
            "top-level and authorization-core authority flags differ"
        )
    actual_core_hash = authorization_core_sha256(value["authorization_core"])
    if value["authorization_core_sha256"] != actual_core_hash:
        raise DispatchAuthorizationError("authorization-core SHA-256 mismatch")
    return value, raw, expected_rel


def _require_equal(label: str, *values: Any) -> None:
    if not values or any(value != values[0] for value in values[1:]):
        raise DispatchAuthorizationError(f"{label} mismatch")


def _validate_h004_contract(authorization: Mapping[str, Any]) -> None:
    if not H004_AUTHORIZATION_ID_RE.fullmatch(authorization["authorization_id"]):
        return
    core = authorization["authorization_core"]
    queue = core["queue_binding"]
    _require_equal("H-004 queue item", H004_QUEUE_ITEM_ID, queue["queue_item_id"])
    _require_equal(
        "H-004 Gate-Q approval",
        H004_GATE_Q_ID,
        queue["gate_q"]["approval_id"],
        core["lineage"]["gate_q"]["approval_id"],
    )
    for name, artifact_id in H004_LINEAGE_IDS.items():
        _require_equal(
            f"H-004 {name} identity",
            artifact_id,
            core["lineage"][name]["artifact_id"],
        )
    _require_equal(
        "H-004 committed denominator and attempt budget",
        81,
        core["denominator"]["planned"],
        core["denominator"]["variant_manifest_value"],
        core["denominator"]["sweep_plan_value"],
        core["budget"]["upper_bound"],
    )
    dataset = core["dataset"]
    _require_equal(
        "H-004 canonical 1d catalog",
        H004_1D_CATALOG_PATH,
        dataset["catalog_path"],
    )
    _require_equal(
        "H-004 canonical 1d data",
        H004_1D_DATA_PATH,
        dataset["data_path"],
    )
    funding = core["funding"]
    _require_equal(
        "H-004 funding provenance",
        H004_FUNDING_PROVENANCE_PATH,
        funding["provenance_artifact_path"],
    )
    _require_equal(
        "H-004 funding data",
        H004_FUNDING_DATA_PATH,
        funding["funding_data_path"],
    )
    runner = core["runner"]
    _require_equal("H-004 runner module", H004_RUNNER_MODULE, runner["module"])
    _require_equal("H-004 runner source", H004_RUNNER_PATH, runner["source_path"])
    _require_equal("H-004 runner version", H004_RUNNER_VERSION, runner["version"])


def _validate_queue_and_gate(root: Path, core: Mapping[str, Any]) -> None:
    queue = core["queue_binding"]
    expected_queue_path = (
        Path("research/queue/admissions")
        / f"{queue['queue_item_id']}.queue_item.json"
    ).as_posix()
    if queue["path"] != expected_queue_path:
        raise DispatchAuthorizationError("queue item ID/path mismatch")
    item, item_raw, _ = _load_json_ref(
        root,
        queue["path"],
        queue["whole_file_sha256"],
        queue["byte_length"],
        "queue item",
    )
    _require_equal("queue item identity", queue["queue_item_id"], item.get("queue_item_id"))
    _require_equal("queue state", queue["required_state"], item.get("status"))

    gate_ref = queue["gate_q"]
    expected_gate_path = (
        Path("research/queue/gate_q_approvals")
        / f"{gate_ref['approval_id']}.gate_q_approval.json"
    ).as_posix()
    if gate_ref["path"] != expected_gate_path:
        raise DispatchAuthorizationError("Gate-Q ID/path mismatch")
    gate, gate_raw, _ = _load_json_ref(
        root,
        gate_ref["path"],
        gate_ref["whole_file_sha256"],
        gate_ref["byte_length"],
        "Gate-Q approval",
    )
    _require_equal("Gate-Q identity", gate_ref["approval_id"], gate.get("approval_id"))
    if gate.get("approval_artifact_target_path") != gate_ref["path"]:
        raise DispatchAuthorizationError("Gate-Q authoritative path mismatch")
    try:
        computed_gate_core = approval_core_sha256(gate)
    except QueueAdmissionError as exc:
        raise DispatchAuthorizationError(
            f"Gate-Q core is not canonicalizable: {exc}"
        ) from exc
    _require_equal(
        "Gate-Q core hash",
        gate_ref["core_sha256"],
        gate.get("approval_core_sha256"),
        computed_gate_core,
    )
    proposed = gate.get("proposed_queue_item", {})
    _require_equal(
        "Gate-Q queue item ID", queue["queue_item_id"], proposed.get("queue_item_id")
    )
    _require_equal("Gate-Q queue path", queue["path"], proposed.get("target_path"))
    _require_equal(
        "Gate-Q queue bytes", _digest(item_raw), proposed.get("bytes_sha256")
    )
    item_gate = item.get("gate_q", {})
    _require_equal(
        "queue/Gate-Q relationship",
        gate_ref["approval_id"],
        item_gate.get("approval_id"),
    )
    _require_equal(
        "queue/Gate-Q core relationship",
        gate_ref["core_sha256"],
        item_gate.get("approval_core_sha256"),
    )
    if _digest(gate_raw) != gate_ref["whole_file_sha256"]:
        raise DispatchAuthorizationError("Gate-Q raw bytes changed during validation")


def _validate_crossing_identities(core: Mapping[str, Any]) -> None:
    crossing = core["crossing_identities"]
    expected_dispatch = (
        f"research/queue/dispatch_records/{crossing['dispatch_id']}"
        ".dispatch_record.json"
    )
    expected_stream = (
        f"research/queue/execution_events/{crossing['run_id']}"
        ".execution_events.jsonl"
    )
    _require_equal(
        "dispatch ID/path", expected_dispatch, crossing["dispatch_record_path"]
    )
    _require_equal(
        "run ID/execution stream", expected_stream, crossing["execution_event_stream_path"]
    )


def _validate_dispatch_manifest_reference(
    root: Path, core: Mapping[str, Any]
) -> dict[str, Any]:
    from tools.canon_intake.dispatch_manifest import (
        DispatchManifestError,
        MANIFEST_ROOT,
        validate_dispatch_manifest,
        validate_manifest_authorization_binding,
    )

    manifest_ref = core["dispatch_manifest"]
    manifest_id = manifest_ref["manifest_id"]
    manifest_path = (
        MANIFEST_ROOT / f"{manifest_id}.dispatch_manifest.json"
    )
    try:
        validation = validate_dispatch_manifest(
            repo_root=root,
            manifest_path=root / manifest_path,
            expected_whole_file_sha256=manifest_ref[
                "whole_file_sha256"
            ],
            expected_byte_length=manifest_ref["byte_length"],
            require_authoritative_path=True,
            validate_references=False,
        )
        validate_manifest_authorization_binding(
            validation["manifest"], core
        )
    except DispatchManifestError as exc:
        raise DispatchAuthorizationError(str(exc)) from exc
    return validation


def _validate_lineage(root: Path, core: Mapping[str, Any]) -> None:
    lineage = core["lineage"]
    spec_ref = lineage["strategy_spec"]
    expected_spec_path = (
        f"research/strategy_specs/{spec_ref['artifact_id']}.strategy_spec.json"
    )
    _require_equal("Strategy Spec ID/path", expected_spec_path, spec_ref["path"])
    spec, spec_raw, _ = _load_json_ref(
        root,
        spec_ref["path"],
        spec_ref["whole_file_sha256"],
        spec_ref["byte_length"],
        "Strategy Spec",
    )
    _require_equal(
        "Strategy Spec identity", spec_ref["artifact_id"], spec.get("strategy_spec_id")
    )
    spec_canonical = _digest(strategy_spec_canonical_json_bytes(spec))
    _require_equal(
        "Strategy Spec canonical hash",
        spec_ref["content_canonical_sha256"],
        spec_canonical,
    )

    readiness_ref = lineage["external_content_readiness"]
    expected_readiness_path = (
        "research/strategy_spec_external_content_readiness/"
        f"{readiness_ref['artifact_id']}.external_content_readiness.json"
    )
    _require_equal(
        "readiness ID/path", expected_readiness_path, readiness_ref["path"]
    )
    readiness, _, _ = _load_json_ref(
        root,
        readiness_ref["path"],
        readiness_ref["whole_file_sha256"],
        readiness_ref["byte_length"],
        "external-content readiness fact",
    )
    _require_equal(
        "readiness identity", readiness_ref["artifact_id"], readiness.get("fact_id")
    )
    _require_equal(
        "readiness authoritative path",
        readiness_ref["path"],
        readiness.get("fact_path"),
    )
    readiness_spec = readiness.get("strategy_spec", {})
    _require_equal(
        "readiness Strategy Spec ID",
        spec_ref["artifact_id"],
        readiness_spec.get("strategy_spec_id"),
    )
    _require_equal(
        "readiness Strategy Spec path",
        spec_ref["path"],
        readiness_spec.get("path"),
    )
    binding = readiness.get("content_binding", {})
    _require_equal(
        "readiness raw Strategy Spec hash",
        _digest(spec_raw),
        readiness_ref["strategy_spec_raw_sha256"],
        binding.get("raw_file_sha256"),
    )
    _require_equal(
        "readiness canonical Strategy Spec hash",
        spec_canonical,
        readiness_ref["strategy_spec_canonical_sha256"],
        binding.get("full_repo_canonical_json_sha256"),
    )
    _require_equal(
        "readiness Strategy Spec byte length",
        len(spec_raw),
        binding.get("raw_byte_length"),
    )
    if readiness.get("readiness_state") != "external_content_ready":
        raise DispatchAuthorizationError("external-content readiness is not ready")

    vp_ref = lineage["variant_planning_approval"]
    expected_vp_path = (
        "research/strategy_spec_variant_planning_approvals/"
        f"{vp_ref['artifact_id']}.variant_planning_approval.json"
    )
    _require_equal("variant-planning ID/path", expected_vp_path, vp_ref["path"])
    vp, _, _ = _load_json_ref(
        root,
        vp_ref["path"],
        vp_ref["whole_file_sha256"],
        vp_ref["byte_length"],
        "variant-planning approval",
    )
    _require_equal(
        "variant-planning approval ID", vp_ref["artifact_id"], vp.get("approval_id")
    )
    _require_equal(
        "variant-planning authoritative path",
        vp_ref["path"],
        vp.get("approval_artifact_target_path"),
    )
    _require_equal(
        "variant-planning core hash",
        vp_ref["core_sha256"],
        vp.get("contract_core_sha256"),
    )

    vm_ref = lineage["variant_manifest"]
    expected_vm_path = (
        f"research/variant_manifests/{vm_ref['artifact_id']}.variant_manifest.json"
    )
    _require_equal("Variant Manifest ID/path", expected_vm_path, vm_ref["path"])
    vm, _, _ = _load_json_ref(
        root,
        vm_ref["path"],
        vm_ref["whole_file_sha256"],
        vm_ref["byte_length"],
        "Variant Manifest",
    )
    _require_equal("Variant Manifest ID", vm_ref["artifact_id"], vm.get("variant_manifest_id"))
    _require_equal(
        "Variant Manifest Strategy Spec",
        spec_ref["artifact_id"],
        vm.get("parent_strategy_spec", {}).get("strategy_spec_id"),
    )
    vm_planning = vm.get("variant_planning_approval", {})
    _require_equal(
        "Variant Manifest planning approval",
        vp_ref["artifact_id"],
        vm_planning.get("approval_id"),
    )
    _require_equal(
        "Variant Manifest planning hash",
        vp_ref["whole_file_sha256"],
        vm_planning.get("sha256"),
    )
    vm_count = (
        vm.get("population_governance", {})
        .get("declared_population", {})
        .get("committed_population_count")
    )
    _require_equal(
        "Variant Manifest denominator",
        core["denominator"]["variant_manifest_value"],
        vm_count,
    )

    sweep_ref = lineage["sweep_plan"]
    expected_sweep_path = (
        f"research/sweep_plans/{sweep_ref['artifact_id']}.sweep_plan.json"
    )
    _require_equal("Sweep Plan ID/path", expected_sweep_path, sweep_ref["path"])
    sweep, _, _ = _load_json_ref(
        root,
        sweep_ref["path"],
        sweep_ref["whole_file_sha256"],
        sweep_ref["byte_length"],
        "Sweep Plan",
    )
    _require_equal("Sweep Plan ID", sweep_ref["artifact_id"], sweep.get("sweep_plan_id"))
    _require_equal(
        "Sweep Plan Variant Manifest",
        vm_ref["artifact_id"],
        sweep.get("parent_variant_manifest", {}).get("variant_manifest_id"),
    )
    sweep_parent = sweep.get("parent_variant_manifest", {})
    _require_equal(
        "Sweep Plan denominator",
        core["denominator"]["sweep_plan_value"],
        sweep_parent.get("manifest_committed_population_count"),
    )

    gate_lineage = lineage["gate_q"]
    gate_queue = core["queue_binding"]["gate_q"]
    if gate_lineage != gate_queue:
        raise DispatchAuthorizationError("lineage and queue Gate-Q bindings differ")

    gate, _, _ = _load_json_ref(
        root,
        gate_lineage["path"],
        gate_lineage["whole_file_sha256"],
        gate_lineage["byte_length"],
        "lineage Gate-Q approval",
    )
    refs = gate.get("artifact_refs", {})
    expected = (
        ("strategy_spec", spec_ref),
        ("variant_manifest", vm_ref),
        ("sweep_plan", sweep_ref),
    )
    for name, reference in expected:
        gate_reference = refs.get(name, {})
        _require_equal(
            f"Gate-Q {name} path", reference["path"], gate_reference.get("path")
        )
        _require_equal(
            f"Gate-Q {name} hash",
            reference["whole_file_sha256"],
            gate_reference.get("sha256"),
        )
    gate_vp = refs.get("variant_planning_approval", {})
    _require_equal(
        "Gate-Q variant-planning ID",
        vp_ref["artifact_id"],
        gate_vp.get("approval_id"),
    )
    _require_equal(
        "Gate-Q variant-planning hash",
        vp_ref["whole_file_sha256"],
        gate_vp.get("sha256"),
    )


def _validate_dataset(root: Path, core: Mapping[str, Any]) -> None:
    dataset = core["dataset"]
    catalog, catalog_raw, _ = _load_json_ref(
        root,
        dataset["catalog_path"],
        dataset["catalog_sha256"],
        dataset["catalog_byte_length"],
        "1d dataset catalog",
    )
    data_raw, data_path = _load_raw_ref(
        root,
        dataset["data_path"],
        dataset["data_sha256"],
        dataset["data_byte_length"],
        "1d dataset",
    )
    validator_raw, _ = _load_raw_ref(
        root,
        dataset["validator_path"],
        dataset["validator_sha256"],
        dataset["validator_byte_length"],
        "canonical 1d lineage validator",
    )
    _require_equal(
        "canonical 1d validator path",
        CANONICAL_1D_VALIDATOR_PATH,
        dataset["validator_path"],
    )
    _require_equal("dataset ID", dataset["dataset_id"], catalog.get("dataset_id"))
    _require_equal(
        "dataset snapshot", dataset["snapshot_version"], catalog.get("snapshot_version")
    )
    _require_equal("dataset path", dataset["data_path"], catalog.get("path"))
    _require_equal("dataset raw hash", dataset["data_sha256"], catalog.get("sha256"))
    _require_equal("dataset market", dataset["market"], catalog.get("market"))
    _require_equal("dataset timeframe", dataset["timeframe"], catalog.get("timeframe"))
    _require_equal(
        "dataset catalog status",
        dataset["catalog_status"],
        catalog.get("catalog_status"),
    )
    coverage = catalog.get("coverage", {})
    _require_equal("dataset row count", dataset["row_count"], coverage.get("row_count"))
    _require_equal(
        "dataset coverage start",
        dataset["coverage_start_utc"],
        coverage.get("start_open_utc"),
    )
    catalog_end = coverage.get("end_close_utc", coverage.get("end_utc"))
    _require_equal("dataset coverage end", dataset["coverage_end_utc"], catalog_end)
    findings = catalog.get("findings", {})
    _require_equal(
        "dataset duplicate count",
        dataset["duplicate_count"],
        findings.get("duplicate_row_count"),
    )
    _require_equal("dataset gap count", dataset["gap_count"], findings.get("gap_count"))
    _require_equal(
        "dataset missing-bar count",
        dataset["missing_bar_count"],
        findings.get("missing_bar_count"),
    )
    _require_equal(
        "dataset incomplete-window count",
        dataset["open_or_incomplete_bar_count"],
        findings.get("open_or_incomplete_bar_count"),
    )
    if catalog.get("unresolved_policy") != "reject":
        raise DispatchAuthorizationError(
            "canonical 1d catalog unresolved policy is not reject"
        )
    source = catalog.get("source", {})
    if source.get("method") != (
        "existing local public archive snapshot; no fetch performed by this package"
    ):
        raise DispatchAuthorizationError(
            "canonical 1d catalog source is not the direct public snapshot"
        )
    if source.get("credentials_used") is not False:
        raise DispatchAuthorizationError(
            "canonical 1d catalog source is not credential-free"
        )
    _require_equal(
        "canonical 1d cadence",
        CANONICAL_1D_CADENCE_MS,
        dataset["cadence_ms"],
    )
    columns_identity = _digest(
        repo_canonical_json_v1(CANONICAL_1D_SOURCE_COLUMNS)
    )
    _require_equal(
        "canonical 1d columns identity",
        columns_identity,
        dataset["columns_schema_identity"],
    )
    try:
        rebuilt_catalog = build_1d_lineage(
            data_path,
            logical_path=dataset["data_path"],
            expected_sha256=dataset["data_sha256"].removeprefix("sha256:"),
        )
    except Exception as exc:
        raise DispatchAuthorizationError(
            f"canonical 1d lineage validation failed: {exc}"
        ) from exc
    if canonical_1d_catalog_bytes(rebuilt_catalog) != catalog_raw:
        raise DispatchAuthorizationError(
            "canonical 1d catalog does not match rebuilt source lineage"
        )
    validation_identity = _digest(
        repo_canonical_json_v1(
            {
                "catalog_sha256": dataset["catalog_sha256"],
                "validator_path": dataset["validator_path"],
                "validator_sha256": dataset["validator_sha256"],
                "catalog_matches_rebuilt_lineage": True,
            }
        )
    )
    _require_equal(
        "canonical 1d validation identity",
        validation_identity,
        dataset["validation_identity"],
    )
    gate_q_dataset = catalog.get("gate_q_dataset")
    if isinstance(gate_q_dataset, dict):
        for field in (
            "dataset_id",
            "snapshot_version",
            "path",
            "sha256",
            "market",
            "timeframe",
        ):
            dataset_field = {
                "path": "data_path",
                "sha256": "data_sha256",
            }.get(field, field)
            _require_equal(
                f"dataset Gate-Q {field}",
                dataset[dataset_field],
                gate_q_dataset.get(field),
            )
    if not data_raw:
        raise DispatchAuthorizationError("1d dataset is empty")
    if not validator_raw:
        raise DispatchAuthorizationError("canonical 1d validator is empty")


def _validate_funding(root: Path, core: Mapping[str, Any]) -> None:
    funding = core["funding"]
    provenance, _, _ = _load_json_ref(
        root,
        funding["provenance_artifact_path"],
        funding["provenance_artifact_sha256"],
        funding["provenance_artifact_byte_length"],
        "funding provenance",
    )
    data_raw, _ = _load_raw_ref(
        root,
        funding["funding_data_path"],
        funding["funding_data_sha256"],
        funding["funding_data_byte_length"],
        "funding data",
    )
    _require_equal(
        "funding mode", funding["funding_mode"], provenance.get("intended_funding_mode")
    )
    _require_equal(
        "funding series ID",
        funding["funding_series_id"],
        provenance.get("funding_series_id"),
    )
    artifact = provenance.get("provenance_artifact", {})
    _require_equal(
        "funding provenance ID",
        funding["provenance_artifact_id"],
        artifact.get("artifact_id"),
    )
    _require_equal(
        "funding provenance path",
        funding["provenance_artifact_path"],
        artifact.get("path"),
    )
    identity = provenance.get("file_identity", {})
    _require_equal(
        "funding data path",
        funding["funding_data_path"],
        identity.get("source_data_path"),
    )
    _require_equal(
        "funding data hash", funding["funding_data_sha256"], identity.get("raw_sha256")
    )
    _require_equal(
        "funding data byte length",
        funding["funding_data_byte_length"],
        identity.get("byte_length"),
    )
    _require_equal("funding row count", funding["row_count"], identity.get("row_count"))
    coverage = provenance.get("coverage", {})
    _require_equal(
        "funding coverage start",
        funding["coverage_start_utc"],
        coverage.get("start_utc"),
    )
    _require_equal(
        "funding coverage end", funding["coverage_end_utc"], coverage.get("end_utc")
    )
    timestamp = provenance.get("event_fields", {}).get("timestamp", {})
    rate = provenance.get("event_fields", {}).get("funding_rate", {})
    alignment = provenance.get("alignment", {})
    _require_equal(
        "funding timestamp semantics",
        funding["timestamp_semantics"],
        timestamp.get("semantics"),
    )
    _require_equal("funding rate units", funding["rate_units"], rate.get("units"))
    _require_equal(
        "funding boundary rule",
        funding["boundary_rule_id"],
        alignment.get("boundary_rule_id"),
    )
    policies = provenance.get("policies", {})
    for key in ("backfill", "interpolation", "zero_substitution"):
        if policies.get(key) != "forbidden":
            raise DispatchAuthorizationError(
                f"funding provenance does not forbid {key}"
            )
    if policies.get("forward_fill") != "forbidden":
        raise DispatchAuthorizationError("funding provenance does not forbid fill")
    if not data_raw:
        raise DispatchAuthorizationError("funding data is empty")


def _validate_runner(root: Path, core: Mapping[str, Any]) -> None:
    runner = core["runner"]
    expected_source_path = runner["module"].replace(".", "/") + ".py"
    _require_equal(
        "runner module/source path", expected_source_path, runner["source_path"]
    )
    raw, _ = _load_raw_ref(
        root,
        runner["source_path"],
        runner["source_sha256"],
        runner["source_byte_length"],
        "runner source",
    )
    try:
        text = raw.decode("utf-8")
    except UnicodeError as exc:
        raise DispatchAuthorizationError("runner source must be UTF-8") from exc
    if not text.strip():
        raise DispatchAuthorizationError("runner source is empty")
    if runner["version"] not in text:
        raise DispatchAuthorizationError(
            "runner version/tool identity is not present in the bound source"
        )
    if "src/runtime" in runner["source_path"] or "private" in runner["source_path"]:
        raise DispatchAuthorizationError("runner source is in a forbidden path")


def _validate_denominator_budget_and_outputs(
    root: Path, core: Mapping[str, Any]
) -> None:
    denominator = core["denominator"]
    budget = core["budget"]
    vm_count = (
        denominator["variant_manifest_value"]
    )
    sweep_count = denominator["sweep_plan_value"]
    values = {
        denominator["planned"],
        vm_count,
        sweep_count,
        budget["upper_bound"],
    }
    if len(values) != 1:
        raise DispatchAuthorizationError("denominator/budget mismatch")
    crossing = core["crossing_identities"]
    _require_equal(
        "output execution stream",
        crossing["execution_event_stream_path"],
        core["output_targets"]["execution_event_stream_path"],
    )
    _scratch_directory_path(
        root,
        core["output_targets"]["scratch_output_root"],
        "output_targets.scratch_output_root",
    )


def _validate_dispatch_authorization_audit_raw(
    root: Path,
    audit_raw: bytes,
) -> list[tuple[dict[str, Any], bytes]]:
    if not audit_raw or not audit_raw.endswith(b"\n"):
        raise DispatchAuthorizationError(
            "dispatch-authorization audit is empty or has a partial tail"
        )
    events_by_authorization: dict[str, list[dict[str, Any]]] = {}
    seen_event_ids: set[str] = set()
    rows: list[tuple[dict[str, Any], bytes]] = []
    for number, raw_line in enumerate(audit_raw.splitlines(keepends=True), 1):
        if not raw_line.endswith(b"\n"):
            raise DispatchAuthorizationError(f"audit line {number} lacks LF")
        try:
            event = json.loads(raw_line.decode("utf-8"))
        except (UnicodeError, json.JSONDecodeError) as exc:
            raise DispatchAuthorizationError(
                f"audit line {number} is invalid UTF-8 JSON"
            ) from exc
        if not isinstance(event, dict):
            raise DispatchAuthorizationError(f"audit line {number} is not an object")
        if raw_line != repo_canonical_json_v1(event) + b"\n":
            raise DispatchAuthorizationError(
                f"audit line {number} is not canonical JSON plus one LF"
            )
        _schema_check(root, AUDIT_SCHEMA, event, f"audit line {number}")
        expected_event_id = (
            f"KDAUTH-EVENT-{event['authorization_id']}-"
            f"{event['sequence_number']:06d}"
        )
        if event["event_id"] != expected_event_id:
            raise DispatchAuthorizationError("audit event ID/sequence mismatch")
        if event["event_id"] in seen_event_ids:
            raise DispatchAuthorizationError("audit contains a duplicate event ID")
        seen_event_ids.add(event["event_id"])
        _parse_timestamp(event["occurred_at"], f"audit line {number}.occurred_at")
        if event["event_payload"]["event_kind"] != event["event_type"]:
            raise DispatchAuthorizationError("audit event/payload kind mismatch")
        events_by_authorization.setdefault(event["authorization_id"], []).append(event)
        rows.append((event, raw_line))

    for grouped_id, grouped_events in events_by_authorization.items():
        terminal = False
        grouped_bindings = {
            field: grouped_events[0][field]
            for field in (
                "authorization_path",
                "authorization_file_sha256",
                "authorization_byte_length",
                "authorization_core_sha256",
                "authorization_core_hash_scope",
                "queue_item_id",
                "dispatch_id",
                "run_id",
            )
        }
        expected_grouped_path = (
            APPROVAL_ROOT
            / f"{grouped_id}.dispatch_authorization.json"
        ).as_posix()
        if grouped_bindings["authorization_path"] != expected_grouped_path:
            raise DispatchAuthorizationError(
                f"audit authorization ID/path mismatch for {grouped_id}"
            )
        for index, event in enumerate(grouped_events, 1):
            for field, expected in grouped_bindings.items():
                if event[field] != expected:
                    raise DispatchAuthorizationError(
                        f"audit {field} changes within lifecycle for {grouped_id}"
                    )
            if event["sequence_number"] != index:
                raise DispatchAuthorizationError(
                    f"audit sequence is not contiguous for {grouped_id}"
                )
            if index == 1 and event["event_type"] != "authorization_created":
                raise DispatchAuthorizationError(
                    f"authorization_created must be first for {grouped_id}"
                )
            if index > 1 and event["event_type"] == "authorization_created":
                raise DispatchAuthorizationError(
                    f"authorization_created occurs more than once for {grouped_id}"
                )
            if terminal:
                raise DispatchAuthorizationError(
                    f"audit contains an event after terminal state for {grouped_id}"
                )
            if event["event_type"] in {
                "authorization_superseded",
                "authorization_revoked",
                "authorization_consumed",
            }:
                terminal = True
            if event["event_type"] == "authorization_superseded":
                payload = event["event_payload"]
                if payload["new_authorization_id"] == grouped_id:
                    raise DispatchAuthorizationError(
                        "supersession must reference a different authorization ID"
                    )
                expected_new_path = (
                    APPROVAL_ROOT
                    / (
                        f"{payload['new_authorization_id']}"
                        ".dispatch_authorization.json"
                    )
                ).as_posix()
                if payload["new_authorization_path"] != expected_new_path:
                    raise DispatchAuthorizationError(
                        "supersession target path is not derived from its new ID"
                    )
    return rows


def read_and_validate_dispatch_authorization_audit(
    *,
    repo_root: Path,
    audit_path: Path | None = None,
    allow_missing: bool = False,
) -> tuple[list[tuple[dict[str, Any], bytes]], int]:
    """Read and validate the complete authoritative KDAUTH lifecycle audit."""
    root = _resolve_root(repo_root)
    canonical_audit = _repo_path(
        root, AUDIT_PATH.as_posix(), "dispatch-authorization audit path"
    )
    if audit_path is not None:
        supplied_audit = _reject_symlink_components(
            audit_path, "dispatch-authorization audit path"
        ).resolve()
        if supplied_audit != canonical_audit:
            raise DispatchAuthorizationError(
                "dispatch-authorization audit is not at the canonical path"
            )
    if not canonical_audit.exists():
        if allow_missing:
            return [], 0
        raise DispatchAuthorizationError(
            "dispatch-authorization audit must be a regular non-symlink file"
        )
    audit_raw = _read_bytes(canonical_audit, "dispatch-authorization audit")
    return (
        _validate_dispatch_authorization_audit_raw(root, audit_raw),
        len(audit_raw),
    )


def validate_dispatch_authorization_audit_append_candidate(
    *,
    repo_root: Path,
    event: Mapping[str, Any],
    allow_missing_audit: bool = False,
) -> dict[str, Any]:
    """Validate one proposed canonical append against the complete audit."""
    root = _resolve_root(repo_root)
    rows, prior_length = read_and_validate_dispatch_authorization_audit(
        repo_root=root,
        allow_missing=allow_missing_audit,
    )
    del rows
    audit_path = _repo_path(
        root, AUDIT_PATH.as_posix(), "dispatch-authorization audit path"
    )
    prior_raw = (
        _read_bytes(audit_path, "dispatch-authorization audit")
        if audit_path.exists()
        else b""
    )
    if len(prior_raw) != prior_length:
        raise DispatchAuthorizationError(
            "dispatch-authorization audit changed during append validation"
        )
    if not isinstance(event, Mapping):
        raise DispatchAuthorizationError(
            "dispatch-authorization audit event must be a mapping"
        )
    materialized = dict(event)
    line = repo_canonical_json_v1(materialized) + b"\n"
    _validate_dispatch_authorization_audit_raw(root, prior_raw + line)
    return {
        "valid": True,
        "prior_byte_length": prior_length,
        "prior_raw_sha256": _digest(prior_raw),
        "raw_line": line,
        "raw_line_sha256": _digest(line),
        "raw_line_byte_length": len(line),
        "non_authority": True,
    }


def _audit_events(
    root: Path,
    authorization: Mapping[str, Any],
    raw: bytes,
    audit_path: Path,
) -> tuple[list[dict[str, Any]], str]:
    audit_rows, _ = read_and_validate_dispatch_authorization_audit(
        repo_root=root,
        audit_path=audit_path,
    )
    authorization_id = authorization["authorization_id"]
    core = authorization["authorization_core"]
    crossing = core["crossing_identities"]
    queue_id = core["queue_binding"]["queue_item_id"]
    expected_common = {
        "authorization_id": authorization_id,
        "authorization_path": authorization["authorization_artifact_target_path"],
        "authorization_file_sha256": _digest(raw),
        "authorization_byte_length": len(raw),
        "authorization_core_sha256": authorization["authorization_core_sha256"],
        "authorization_core_hash_scope": "dispatch_authorization_core_v1",
        "queue_item_id": queue_id,
        "dispatch_id": crossing["dispatch_id"],
        "run_id": crossing["run_id"],
    }

    events = [
        event
        for event, _ in audit_rows
        if event["authorization_id"] == authorization_id
    ]
    if not events or events[0]["event_type"] != "authorization_created":
        raise DispatchAuthorizationError("audit lacks its creation event")
    for event in events:
        for field, expected in expected_common.items():
            if event.get(field) != expected:
                raise DispatchAuthorizationError(
                    f"audit {field} binding mismatch for {authorization_id}"
                )
    state = events[-1]["event_type"].removeprefix("authorization_")
    return events, state


def _iter_current_control_documents(root: Path) -> Iterable[tuple[str, bytes]]:
    for relative_root, suffix in (
        (APPROVAL_ROOT, ".dispatch_authorization.json"),
        (DISPATCH_ROOT, ".dispatch_record.json"),
        (EXECUTION_ROOT, ".execution_events.jsonl"),
    ):
        directory = _repo_path(root, relative_root.as_posix(), "control-plane corpus")
        if not directory.exists():
            continue
        if directory.is_symlink() or not directory.is_dir():
            raise DispatchAuthorizationError(
                f"{relative_root.as_posix()} is not a regular directory"
            )
        for path in sorted(directory.iterdir(), key=lambda candidate: candidate.name):
            if path.is_symlink() or not path.is_file() or not path.name.endswith(suffix):
                raise DispatchAuthorizationError(
                    f"unexpected control-plane corpus entry: {path.name}"
                )
            yield path.relative_to(root).as_posix(), _read_bytes(path, path.name)
    audit = _repo_path(root, AUDIT_PATH.as_posix(), "authorization audit")
    if audit.exists():
        yield AUDIT_PATH.as_posix(), _read_bytes(audit, "authorization audit")


def _git(root: Path, *args: str, check: bool = True) -> str:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )
    except OSError as exc:
        raise DispatchAuthorizationError("git history is unavailable") from exc
    if check and result.returncode != 0:
        raise DispatchAuthorizationError(
            f"git history command failed: {' '.join(args)}: {result.stderr.strip()}"
        )
    return result.stdout


def _history_documents(root: Path) -> Iterable[tuple[str, bytes]]:
    if _git(root, "rev-parse", "--is-inside-work-tree", check=False).strip() != "true":
        raise DispatchAuthorizationError(
            "retained Git history is unavailable; validation fails closed"
        )
    tracked_roots = (
        APPROVAL_ROOT.as_posix(),
        AUDIT_PATH.as_posix(),
        DISPATCH_ROOT.as_posix(),
        EXECUTION_ROOT.as_posix(),
    )
    commits = [
        line
        for line in _git(
            root, "log", "--all", "--format=%H", "--", *tracked_roots
        ).splitlines()
        if line
    ]
    seen: set[tuple[str, str]] = set()
    for commit in commits:
        paths = _git(
            root,
            "ls-tree",
            "-r",
            "--name-only",
            commit,
            "--",
            *tracked_roots,
        ).splitlines()
        for path in paths:
            blob_id = _git(root, "rev-parse", f"{commit}:{path}").strip()
            key = (path, blob_id)
            if key in seen:
                continue
            seen.add(key)
            try:
                raw = subprocess.run(
                    ["git", "show", f"{commit}:{path}"],
                    cwd=root,
                    capture_output=True,
                    check=True,
                ).stdout
            except (OSError, subprocess.CalledProcessError) as exc:
                raise DispatchAuthorizationError(
                    f"retained history is unreadable at {commit}:{path}"
                ) from exc
            yield path, raw


def _consumption_bindings(path: str, raw: bytes) -> list[dict[str, Any]]:
    values: list[dict[str, Any]] = []
    if path.endswith(".dispatch_record.json"):
        try:
            record = json.loads(raw.decode("utf-8"))
        except (UnicodeError, json.JSONDecodeError) as exc:
            raise DispatchAuthorizationError(
                f"dispatch history is malformed: {path}"
            ) from exc
        if not isinstance(record, dict):
            raise DispatchAuthorizationError(f"dispatch history is not an object: {path}")
        authorization = record.get("dispatch_authorization", {})
        values.append(
            {
                "source": path,
                "authorization_id": authorization.get("authorization_id"),
                "authorization_path": authorization.get("source_path"),
                "authorization_file_sha256": authorization.get("source_sha256"),
                "queue_item_id": record.get("queue_binding", {}).get("queue_item_id"),
                "dispatch_id": record.get("dispatch_id"),
                "run_id": record.get("run_binding", {}).get("run_id"),
                "dispatch_path": record.get("dispatch_record_path"),
                "stream_path": record.get("run_binding", {}).get(
                    "execution_event_stream_path"
                ),
            }
        )
    elif path.endswith(".execution_events.jsonl"):
        if raw and not raw.endswith(b"\n"):
            raise DispatchAuthorizationError(
                f"execution history has a partial tail: {path}"
            )
        for number, line in enumerate(raw.splitlines(), 1):
            try:
                event = json.loads(line.decode("utf-8"))
            except (UnicodeError, json.JSONDecodeError) as exc:
                raise DispatchAuthorizationError(
                    f"execution history is malformed: {path}:{number}"
                ) from exc
            bindings = event.get("bindings", {}) if isinstance(event, dict) else {}
            values.append(
                {
                    "source": f"{path}:{number}",
                    "authorization_id": None,
                    "authorization_path": None,
                    "authorization_file_sha256": None,
                    "queue_item_id": bindings.get("queue_item_id"),
                    "dispatch_id": bindings.get("dispatch_id"),
                    "run_id": bindings.get("run_id"),
                    "dispatch_path": bindings.get("dispatch_record_path"),
                    "stream_path": event.get("stream_path")
                    if isinstance(event, dict)
                    else None,
                }
            )
    elif path == AUDIT_PATH.as_posix():
        if raw and not raw.endswith(b"\n"):
            raise DispatchAuthorizationError(
                "retained authorization audit has a partial tail"
            )
        for number, line in enumerate(raw.splitlines(), 1):
            try:
                event = json.loads(line.decode("utf-8"))
            except (UnicodeError, json.JSONDecodeError) as exc:
                raise DispatchAuthorizationError(
                    f"retained authorization audit is malformed at line {number}"
                ) from exc
            if isinstance(event, dict):
                values.append(
                    {
                        "source": f"{path}:{number}",
                        "event_type": event.get("event_type"),
                        "authorization_id": event.get("authorization_id"),
                        "authorization_path": event.get("authorization_path"),
                        "authorization_file_sha256": event.get(
                            "authorization_file_sha256"
                        ),
                        "queue_item_id": event.get("queue_item_id"),
                        "dispatch_id": event.get("dispatch_id"),
                        "run_id": event.get("run_id"),
                        "dispatch_path": event.get("event_payload", {}).get(
                            "dispatch_record_path"
                        ),
                        "stream_path": None,
                    }
                )
    return values


def _validate_single_use(
    root: Path,
    authorization: Mapping[str, Any],
    authorization_raw: bytes,
    *,
    reservation_history_policy: ReservationHistoryPolicy,
    allowed_dispatch_record: tuple[str, str] | None = None,
) -> None:
    core = authorization["authorization_core"]
    crossing = core["crossing_identities"]
    expected = {
        "authorization_id": authorization["authorization_id"],
        "authorization_path": authorization["authorization_artifact_target_path"],
        "authorization_file_sha256": _digest(authorization_raw),
        "queue_item_id": core["queue_binding"]["queue_item_id"],
        "dispatch_id": crossing["dispatch_id"],
        "run_id": crossing["run_id"],
        "dispatch_path": crossing["dispatch_record_path"],
        "stream_path": crossing["execution_event_stream_path"],
    }
    sources: list[tuple[str, bytes]] = list(_iter_current_control_documents(root))
    sources.extend(_history_documents(root))
    seen_sources: set[tuple[str, str]] = set()
    for path, raw in sources:
        key = (path, _digest(raw))
        if key in seen_sources:
            continue
        seen_sources.add(key)
        if path.endswith(".dispatch_authorization.json"):
            try:
                historical = json.loads(raw.decode("utf-8"))
            except (UnicodeError, json.JSONDecodeError) as exc:
                raise DispatchAuthorizationError(
                    f"retained authorization is malformed: {path}"
                ) from exc
            if not isinstance(historical, dict):
                raise DispatchAuthorizationError(
                    f"retained authorization is not an object: {path}"
                )
            if historical.get("authorization_id") == expected["authorization_id"]:
                if raw != authorization_raw:
                    raise DispatchAuthorizationError(
                        "authorization ID has conflicting retained bytes"
                    )
                if path != authorization["authorization_artifact_target_path"]:
                    raise DispatchAuthorizationError(
                        "authorization ID has conflicting retained path"
                    )
            elif isinstance(historical.get("authorization_core"), dict):
                historical_crossing = historical["authorization_core"].get(
                    "crossing_identities", {}
                )
                historical_values = {
                    "authorization_path": historical.get(
                        "authorization_artifact_target_path"
                    ),
                    "authorization_file_sha256": _digest(raw),
                    "queue_item_id": historical["authorization_core"]
                    .get("queue_binding", {})
                    .get("queue_item_id"),
                    "dispatch_id": historical_crossing.get("dispatch_id"),
                    "run_id": historical_crossing.get("run_id"),
                    "dispatch_path": historical_crossing.get(
                        "dispatch_record_path"
                    ),
                    "stream_path": historical_crossing.get(
                        "execution_event_stream_path"
                    ),
                }
                collisions = [
                    field
                    for field, value in historical_values.items()
                    if value is not None and expected.get(field) == value
                ]
                if collisions:
                    raise DispatchAuthorizationError(
                        f"another authorization reserves single-use identities in "
                        f"{path}: {', '.join(collisions)}"
                    )
            continue
        for binding in _consumption_bindings(path, raw):
            if (
                binding.get("event_type") == "authorization_created"
                and binding.get("authorization_id") == expected["authorization_id"]
            ):
                creation_fields = (
                    "authorization_path",
                    "authorization_file_sha256",
                    "queue_item_id",
                    "dispatch_id",
                    "run_id",
                )
                if any(
                    binding.get(field) != expected[field]
                    for field in creation_fields
                ):
                    raise DispatchAuthorizationError(
                        "authorization creation history conflicts with current bytes"
                    )
                continue
            if (
                allowed_dispatch_record is not None
                and path == allowed_dispatch_record[0]
                and _digest(raw) == allowed_dispatch_record[1]
                and all(
                    binding.get(field) == expected[field]
                    for field in (
                        "authorization_id",
                        "authorization_path",
                        "authorization_file_sha256",
                        "queue_item_id",
                        "dispatch_id",
                        "run_id",
                        "dispatch_path",
                        "stream_path",
                    )
                )
            ):
                continue
            collisions = [
                field
                for field, value in expected.items()
                if value is not None and binding.get(field) == value
            ]
            if collisions:
                raise DispatchAuthorizationError(
                    f"single-use identity already consumed in {binding['source']}: "
                    + ", ".join(collisions)
                )

    # The crossing-reservation ledger is a separate authoritative burn surface.
    # Precreation requires zero colliding attempts.  An active, already-created
    # KDAUTH instead requires its one exact committed attempt.  Every other
    # collision, including an unresolved, rolled-back, integrity-critical,
    # deleted, or retained-only attempt, fails closed and prevents reuse.
    from tools.canon_intake.dispatch_authorization_reservation import (
        DispatchAuthorizationReservationError,
        scan_dispatch_authorization_reservations,
    )

    try:
        reservations = scan_dispatch_authorization_reservations(
            repo_root=root,
            include_retained_history=True,
        )
    except DispatchAuthorizationReservationError as exc:
        raise DispatchAuthorizationError(
            f"crossing reservation history is invalid: {exc}"
        ) from exc
    reservation_expected = {
        "authorization_id": expected["authorization_id"],
        "authorization_target_path": expected["authorization_path"],
        "reviewed_whole_file_sha256": expected[
            "authorization_file_sha256"
        ],
        "authorization_core_sha256": authorization[
            "authorization_core_sha256"
        ],
        "queue_item_id": expected["queue_item_id"],
        "dispatch_id": expected["dispatch_id"],
        "dispatch_record_path": expected["dispatch_path"],
        "run_id": expected["run_id"],
        "execution_event_stream_path": expected["stream_path"],
    }
    reservation_bindings: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for reservation in reservations:
        first = reservation["events"][0]
        reservation_values = {
            "authorization_id": first["authorization_binding"][
                "authorization_id"
            ],
            "authorization_target_path": first["authorization_binding"][
                "authorization_target_path"
            ],
            "reviewed_whole_file_sha256": first[
                "reviewed_content_binding"
            ]["reviewed_whole_file_sha256"],
            "authorization_core_sha256": first["authorization_binding"][
                "authorization_core_sha256"
            ],
            "queue_item_id": first["queue_binding"]["queue_item_id"],
            "dispatch_id": first["dispatch_binding"]["dispatch_id"],
            "dispatch_record_path": first["dispatch_binding"][
                "dispatch_record_path"
            ],
            "run_id": first["run_binding"]["run_id"],
            "execution_event_stream_path": first["run_binding"][
                "execution_event_stream_path"
            ],
        }
        reservation_bindings.append((reservation, reservation_values))

    if reservation_history_policy == FRESH_COLLISION_CHECK:
        for reservation, reservation_values in reservation_bindings:
            collisions = [
                field
                for field, value in reservation_expected.items()
                if reservation_values.get(field) == value
            ]
            if collisions:
                first = reservation["events"][0]
                raise DispatchAuthorizationError(
                    "crossing reservation permanently consumes single-use "
                    f"identities in {first['reservation_stream_path']}: "
                    + ", ".join(collisions)
                )
        return
    if reservation_history_policy != COMMITTED_CROSSING_PROOF:
        raise DispatchAuthorizationError(
            "unknown crossing reservation history validation policy"
        )

    matching_committed_attempts: list[dict[str, Any]] = []
    for reservation, reservation_values in reservation_bindings:
        if (
            reservation["terminal_outcome"] == "crossing_committed"
            and reservation_values == reservation_expected
            and reservation["findings"] == []
        ):
            matching_committed_attempts.append(reservation)
    if len(matching_committed_attempts) != 1:
        raise DispatchAuthorizationError(
            "exactly one logical committed crossing reservation matching the "
            "KDAUTH and authorization_created event is required"
        )
    matching_committed = matching_committed_attempts[0]
    for reservation, reservation_values in reservation_bindings:
        first = reservation["events"][0]
        collisions = [
            field
            for field, value in reservation_expected.items()
            if reservation_values.get(field) == value
        ]
        if not collisions:
            continue
        if (
            reservation is matching_committed
            and reservation_values == reservation_expected
        ):
            continue
        raise DispatchAuthorizationError(
            "crossing reservation permanently consumes single-use identities "
            f"in {first['reservation_stream_path']}: "
            + ", ".join(collisions)
        )


def _validate_dispatch_authorization_file(
    *,
    root: Path,
    authorization_path: Path,
    audit_path: Path | None = None,
    expected_whole_file_sha256: str | None = None,
    expected_byte_length: int | None = None,
    require_audit: bool = True,
    scan_history: bool = True,
    require_authoritative_path: bool = True,
    allowed_dispatch_record: tuple[str, str] | None = None,
) -> dict[str, Any]:
    authorization, raw, relative_path = _load_authorization(
        root,
        authorization_path,
        require_authoritative_path=require_authoritative_path,
    )
    whole_hash = _digest(raw)
    if (
        expected_whole_file_sha256 is not None
        and expected_whole_file_sha256 != whole_hash
    ):
        raise DispatchAuthorizationError("expected whole-file SHA-256 mismatch")
    if expected_byte_length is not None and expected_byte_length != len(raw):
        raise DispatchAuthorizationError("expected byte length mismatch")

    core = authorization["authorization_core"]
    _validate_h004_contract(authorization)
    _validate_queue_and_gate(root, core)
    _validate_crossing_identities(core)
    _validate_dispatch_manifest_reference(root, core)
    _validate_lineage(root, core)
    _validate_dataset(root, core)
    _validate_funding(root, core)
    _validate_runner(root, core)
    _validate_denominator_budget_and_outputs(root, core)

    lifecycle_state = "not_recorded"
    if require_audit:
        canonical_audit = _repo_path(
            root, AUDIT_PATH.as_posix(), "dispatch-authorization audit path"
        )
        if audit_path is not None:
            supplied_audit = _reject_symlink_components(
                audit_path, "dispatch-authorization audit path"
            ).resolve()
            if supplied_audit != canonical_audit:
                raise DispatchAuthorizationError(
                    "dispatch-authorization audit is not at the canonical path"
                )
        selected_audit = canonical_audit
        _, lifecycle_state = _audit_events(
            root, authorization, raw, selected_audit
        )
        if lifecycle_state != "created":
            raise DispatchAuthorizationError(
                f"authorization is not consumable: lifecycle state is {lifecycle_state}"
            )
    if scan_history:
        reservation_history_policy: ReservationHistoryPolicy = (
            COMMITTED_CROSSING_PROOF
            if require_audit
            else FRESH_COLLISION_CHECK
        )
        _validate_single_use(
            root,
            authorization,
            raw,
            reservation_history_policy=reservation_history_policy,
            allowed_dispatch_record=allowed_dispatch_record,
        )

    crossing = core["crossing_identities"]
    return {
        "valid": True,
        "authorization_id": authorization["authorization_id"],
        "authorization_path": relative_path,
        "whole_file_sha256": whole_hash,
        "byte_length": len(raw),
        "authorization_core_sha256": authorization[
            "authorization_core_sha256"
        ],
        "queue_item_id": core["queue_binding"]["queue_item_id"],
        "dispatch_id": crossing["dispatch_id"],
        "run_id": crossing["run_id"],
        "lifecycle_state": lifecycle_state,
        "freshness": "content_bound_exact_equality_only",
        "non_authority": {
            "does_not_create_authorization": True,
            "does_not_create_dispatch": True,
            "does_not_invoke_runner": True,
            "does_not_create_result_population": True,
        },
    }


def validate_dispatch_authorization_candidate(
    *,
    repo_root: Path,
    proposal_path: Path,
    expected_whole_file_sha256: str | None = None,
    expected_byte_length: int | None = None,
) -> dict[str, Any]:
    """Validate exact review-path bytes before any protected crossing mutation."""
    root = _resolve_root(repo_root)
    result = _validate_dispatch_authorization_file(
        root=root,
        authorization_path=proposal_path,
        expected_whole_file_sha256=expected_whole_file_sha256,
        expected_byte_length=expected_byte_length,
        require_audit=False,
        scan_history=True,
        require_authoritative_path=False,
    )
    target = _repo_path(
        root,
        result["authorization_path"],
        "authorization target path",
    )
    if _lexical_entry_exists(target):
        raise DispatchAuthorizationError(
            "authorization target path is not absent for precreation review"
        )
    return {
        **result,
        "proposal_path": str(
            _reject_symlink_components(proposal_path, "dispatch authorization")
            .resolve()
        ),
        "target_absence_proven": True,
    }


def validate_dispatch_authorization(
    *,
    repo_root: Path,
    authorization_path: Path,
    audit_path: Path | None = None,
    expected_whole_file_sha256: str | None = None,
    expected_byte_length: int | None = None,
    require_audit: bool = True,
    scan_history: bool = True,
) -> dict[str, Any]:
    """Validate one authoritative KDAUTH and return non-authoritative facts."""
    root = _resolve_root(repo_root)
    return _validate_dispatch_authorization_file(
        root=root,
        authorization_path=authorization_path,
        audit_path=audit_path,
        expected_whole_file_sha256=expected_whole_file_sha256,
        expected_byte_length=expected_byte_length,
        require_audit=require_audit,
        scan_history=scan_history,
        require_authoritative_path=True,
    )


def _require_mapping_equal(
    label: str,
    actual: Mapping[str, Any],
    expected: Mapping[str, Any],
) -> None:
    mismatches = [
        field
        for field, value in expected.items()
        if actual.get(field) != value
    ]
    if mismatches:
        raise DispatchAuthorizationError(
            f"{label} mismatch: {', '.join(mismatches)}"
        )


def _require_exact_committed_crossing(
    root: Path,
    authorization: Mapping[str, Any],
    authorization_raw: bytes,
) -> None:
    from tools.canon_intake.dispatch_authorization_reservation import (
        DispatchAuthorizationReservationError,
        scan_dispatch_authorization_reservations,
    )

    core = authorization["authorization_core"]
    crossing = core["crossing_identities"]
    expected = {
        "authorization_id": authorization["authorization_id"],
        "authorization_target_path": authorization[
            "authorization_artifact_target_path"
        ],
        "reviewed_whole_file_sha256": _digest(authorization_raw),
        "authorization_core_sha256": authorization[
            "authorization_core_sha256"
        ],
        "queue_item_id": core["queue_binding"]["queue_item_id"],
        "dispatch_id": crossing["dispatch_id"],
        "dispatch_record_path": crossing["dispatch_record_path"],
        "run_id": crossing["run_id"],
        "execution_event_stream_path": crossing[
            "execution_event_stream_path"
        ],
    }
    try:
        reservations = scan_dispatch_authorization_reservations(
            repo_root=root,
            include_retained_history=True,
        )
    except DispatchAuthorizationReservationError as exc:
        raise DispatchAuthorizationError(
            f"crossing reservation history is invalid: {exc}"
        ) from exc
    matches: list[dict[str, Any]] = []
    for reservation in reservations:
        initial = reservation["events"][0]
        values = {
            "authorization_id": initial["authorization_binding"][
                "authorization_id"
            ],
            "authorization_target_path": initial["authorization_binding"][
                "authorization_target_path"
            ],
            "reviewed_whole_file_sha256": initial[
                "reviewed_content_binding"
            ]["reviewed_whole_file_sha256"],
            "authorization_core_sha256": initial["authorization_binding"][
                "authorization_core_sha256"
            ],
            "queue_item_id": initial["queue_binding"]["queue_item_id"],
            "dispatch_id": initial["dispatch_binding"]["dispatch_id"],
            "dispatch_record_path": initial["dispatch_binding"][
                "dispatch_record_path"
            ],
            "run_id": initial["run_binding"]["run_id"],
            "execution_event_stream_path": initial["run_binding"][
                "execution_event_stream_path"
            ],
        }
        collisions = [
            field
            for field, value in expected.items()
            if values.get(field) == value
        ]
        if values == expected:
            if (
                reservation["terminal_outcome"] == "crossing_committed"
                and reservation["findings"] == []
            ):
                matches.append(reservation)
                continue
        if collisions:
            raise DispatchAuthorizationError(
                "crossing reservation permanently consumes single-use identities "
                f"in {initial['reservation_stream_path']}: "
                + ", ".join(collisions)
            )
    if len(matches) != 1:
        raise DispatchAuthorizationError(
            "exactly one logical committed crossing reservation matching the "
            "KDAUTH and authorization_created event is required"
        )


def validate_dispatch_record_for_authorization(
    *,
    repo_root: Path,
    dispatch_path: Path,
    authorization_path: Path | None = None,
) -> dict[str, Any]:
    """Validate one durable dispatch against its exact KDAUTH and lifecycle."""
    root = _resolve_root(repo_root)
    dispatch_lexical = _reject_symlink_components(
        dispatch_path, "dispatch record"
    )
    dispatch_raw = _read_bytes(dispatch_lexical, "dispatch record")
    dispatch = _decode_object(dispatch_raw, "dispatch record")
    if dispatch_raw != serialize_dispatch_authorization(dispatch):
        raise DispatchAuthorizationError(
            "dispatch record is not canonical sorted two-space JSON plus one LF"
        )
    _schema_check(root, DISPATCH_SCHEMA, dispatch, "dispatch record")

    dispatch_id = dispatch["dispatch_id"]
    expected_dispatch_rel = (
        DISPATCH_ROOT / f"{dispatch_id}.dispatch_record.json"
    ).as_posix()
    if dispatch["dispatch_record_path"] != expected_dispatch_rel:
        raise DispatchAuthorizationError(
            "dispatch record ID/path mismatch"
        )
    expected_dispatch_path = _repo_path(
        root, expected_dispatch_rel, "dispatch record path"
    )
    if dispatch_lexical.resolve() != expected_dispatch_path:
        raise DispatchAuthorizationError(
            "dispatch record is not at its authoritative ID-derived path"
        )
    created_at = _parse_timestamp(dispatch["created_at"], "dispatch.created_at")
    if (
        created_at.astimezone(timezone.utc).strftime("%Y%m%d")
        != dispatch_id.split("-")[1]
    ):
        raise DispatchAuthorizationError(
            "dispatch ID date does not equal created_at UTC date"
        )

    authorization_ref = dispatch["dispatch_authorization"]
    selected_authorization_path = (
        authorization_path
        if authorization_path is not None
        else _repo_path(
            root,
            authorization_ref["source_path"],
            "dispatch authorization source path",
        )
    )
    authorization, authorization_raw, authorization_rel = _load_authorization(
        root,
        selected_authorization_path,
        require_authoritative_path=True,
    )
    _validate_h004_contract(authorization)
    core = authorization["authorization_core"]
    _validate_queue_and_gate(root, core)
    _validate_crossing_identities(core)
    manifest_validation = _validate_dispatch_manifest_reference(root, core)
    _validate_lineage(root, core)
    _validate_dataset(root, core)
    _validate_funding(root, core)
    _validate_runner(root, core)
    _validate_denominator_budget_and_outputs(root, core)
    events, lifecycle_state = _audit_events(
        root,
        authorization,
        authorization_raw,
        _repo_path(root, AUDIT_PATH.as_posix(), "dispatch-authorization audit"),
    )
    _require_exact_committed_crossing(root, authorization, authorization_raw)

    crossing = core["crossing_identities"]
    queue = core["queue_binding"]
    gate = queue["gate_q"]
    _require_mapping_equal(
        "dispatch/KDAUTH authorization",
        authorization_ref,
        {
            "authorization_id": authorization["authorization_id"],
            "source_path": authorization_rel,
            "source_sha256": _digest(authorization_raw),
            "source_byte_length": len(authorization_raw),
            "authorization_core_sha256": authorization[
                "authorization_core_sha256"
            ],
            "authorization_core_hash_scope":
                "dispatch_authorization_core_v1",
            "authorization_core_canonicalization":
                "repo_canonical_json_v1",
            "authorized_by": authorization["approved_by"],
            "authorized_at": authorization["approved_at"],
            "authorization_scope": authorization["authorization_scope"],
            "authorized_queue_item_id": queue["queue_item_id"],
            "authorized_dispatch_id": crossing["dispatch_id"],
            "authorized_run_id": crossing["run_id"],
            "exact_content_and_target_only": True,
            "content_bound_freshness": True,
            "single_use_authorization_id": True,
            "no_downstream_authority": True,
        },
    )
    _require_mapping_equal(
        "dispatch/KDAUTH queue",
        dispatch["queue_binding"],
        {
            "queue_item_id": queue["queue_item_id"],
            "path": queue["path"],
            "raw_sha256": queue["whole_file_sha256"],
            "admission_status": queue["required_state"],
        },
    )
    _require_mapping_equal(
        "dispatch/KDAUTH Gate-Q",
        dispatch["gate_q_binding"],
        {
            "approval_id": gate["approval_id"],
            "path": gate["path"],
            "file_sha256": gate["whole_file_sha256"],
            "approval_core_sha256": gate["core_sha256"],
            "approval_core_hash_scope": gate["core_hash_scope"],
            "approval_core_canonicalization": gate[
                "core_canonicalization"
            ],
        },
    )
    _require_mapping_equal(
        "dispatch/KDAUTH run",
        dispatch["run_binding"],
        {
            "run_id": crossing["run_id"],
            "execution_event_stream_path": crossing[
                "execution_event_stream_path"
            ],
        },
    )
    _require_mapping_equal(
        "dispatch/KDAUTH runner",
        dispatch["runner_binding"],
        {
            field: core["runner"][field]
            for field in (
                "invocation_kind",
                "module",
                "source_path",
                "version",
                "source_sha256",
            )
        },
    )
    for field in ("strategy_spec", "variant_manifest", "sweep_plan"):
        source = core["lineage"][field]
        _require_mapping_equal(
            f"dispatch/KDAUTH artifact {field}",
            dispatch["artifact_bindings"][field],
            {
                "artifact_id": source["artifact_id"],
                "path": source["path"],
                "sha256": source["whole_file_sha256"],
            },
        )
    dataset = core["dataset"]
    _require_mapping_equal(
        "dispatch/KDAUTH dataset",
        dispatch["dataset_binding"],
        {
            "dataset_id": dataset["dataset_id"],
            "snapshot_version": dataset["snapshot_version"],
            "path": dataset["data_path"],
            "sha256": dataset["data_sha256"],
            "market": dataset["market"],
            "timeframe": dataset["timeframe"],
            "unresolved_policy": "reject",
        },
    )
    for field in ("denominator", "budget", "execution_parameters"):
        if dispatch[field] != core[field]:
            raise DispatchAuthorizationError(
                f"dispatch/KDAUTH {field} mismatch"
            )
    if dispatch["dispatch_id"] != crossing["dispatch_id"]:
        raise DispatchAuthorizationError("dispatch/KDAUTH dispatch ID mismatch")
    if (
        dispatch["output_targets"]["execution_event_stream_path"]
        != crossing["execution_event_stream_path"]
    ):
        raise DispatchAuthorizationError(
            "dispatch/KDAUTH execution output mismatch"
        )
    scratch_root = _scratch_directory_path(
        root,
        core["output_targets"]["scratch_output_root"],
        "authorized scratch output root",
    )
    scratch_run_directory = _scratch_directory_path(
        root,
        dispatch["output_targets"]["scratch_run_directory"],
        "dispatch scratch run directory",
    )
    provisional_result_paths = [
        _repo_path(
            root,
            value,
            f"dispatch provisional result path {index}",
        )
        for index, value in enumerate(
            dispatch["output_targets"]["provisional_result_paths"], 1
        )
    ]
    _repo_path(
        root,
        dispatch["output_targets"]["execution_event_stream_path"],
        "dispatch execution-event stream path",
    )
    selected_outputs = [("scratch_run_directory", scratch_run_directory)]
    selected_outputs.extend(
        (
            f"provisional_result_paths[{index}]",
            selected,
        )
        for index, selected in enumerate(provisional_result_paths)
    )
    for field, selected in selected_outputs:
        try:
            selected.relative_to(scratch_root)
        except ValueError as exc:
            raise DispatchAuthorizationError(
                f"dispatch output {field} escapes the authorized scratch root"
            ) from exc

    from tools.canon_intake.dispatch_manifest import (
        DispatchManifestError,
        derive_dispatch_record,
    )

    try:
        derived = derive_dispatch_record(
            manifest=manifest_validation["manifest"],
            manifest_raw=manifest_validation["raw"],
            authorization=authorization,
            authorization_raw=authorization_raw,
        )
    except DispatchManifestError as exc:
        raise DispatchAuthorizationError(str(exc)) from exc
    if dispatch != derived:
        raise DispatchAuthorizationError(
            "dispatch record differs from the deterministic manifest derivation"
        )
    if dispatch_raw != serialize_dispatch_authorization(derived):
        raise DispatchAuthorizationError(
            "dispatch record bytes differ from the deterministic manifest derivation"
        )

    return {
        "valid": True,
        "dispatch_id": dispatch_id,
        "dispatch_path": expected_dispatch_rel,
        "dispatch_file_sha256": _digest(dispatch_raw),
        "dispatch_byte_length": len(dispatch_raw),
        "authorization_id": authorization["authorization_id"],
        "authorization_path": authorization_rel,
        "authorization_whole_file_sha256": _digest(authorization_raw),
        "authorization_core_sha256": authorization[
            "authorization_core_sha256"
        ],
        "queue_item_id": queue["queue_item_id"],
        "run_id": crossing["run_id"],
        "lifecycle_state": lifecycle_state,
        "lifecycle_events": events,
        "audit_path": AUDIT_PATH.as_posix(),
        "non_authority": True,
    }


def validate_dispatch_authorization_for_consumption(
    *,
    repo_root: Path,
    authorization_path: Path,
    dispatch_path: Path,
) -> dict[str, Any]:
    """Validate active KDAUTH history while allowing its one exact dispatch."""
    root = _resolve_root(repo_root)
    dispatch = validate_dispatch_record_for_authorization(
        repo_root=root,
        dispatch_path=dispatch_path,
        authorization_path=authorization_path,
    )
    authorization = _validate_dispatch_authorization_file(
        root=root,
        authorization_path=authorization_path,
        require_audit=True,
        scan_history=True,
        require_authoritative_path=True,
        allowed_dispatch_record=(
            dispatch["dispatch_path"],
            dispatch["dispatch_file_sha256"],
        ),
    )
    return {
        **authorization,
        "dispatch_validation": dispatch,
    }


def collect_dispatch_without_consumption_findings(
    *,
    repo_root: Path,
) -> list[dict[str, Any]]:
    """Collect valid dispatches lacking their exact consumed lifecycle event."""
    root = _resolve_root(repo_root)
    dispatch_root = _repo_path(
        root, DISPATCH_ROOT.as_posix(), "dispatch-record root"
    )
    if not dispatch_root.exists():
        return []
    findings: list[dict[str, Any]] = []
    for path in sorted(dispatch_root.glob("*.dispatch_record.json")):
        try:
            result = validate_dispatch_record_for_authorization(
                repo_root=root,
                dispatch_path=path,
            )
        except DispatchAuthorizationError:
            continue
        if result["lifecycle_state"] not in {"created", "consumed"}:
            continue
        exact_consumption = any(
            event["event_type"] == "authorization_consumed"
            and event["authorization_id"] == result["authorization_id"]
            and event["authorization_path"] == result["authorization_path"]
            and event["authorization_file_sha256"]
            == result["authorization_whole_file_sha256"]
            and event["authorization_core_sha256"]
            == result["authorization_core_sha256"]
            and event["queue_item_id"] == result["queue_item_id"]
            and event["dispatch_id"] == result["dispatch_id"]
            and event["run_id"] == result["run_id"]
            and event["event_payload"]["dispatch_record_path"]
            == result["dispatch_path"]
            and event["event_payload"]["consumption_is_permanent"] is True
            for event in result["lifecycle_events"]
        )
        if exact_consumption:
            continue
        findings.append(
            {
                "authorization_id": result["authorization_id"],
                "authorization_path": result["authorization_path"],
                "authorization_whole_file_sha256": result[
                    "authorization_whole_file_sha256"
                ],
                "authorization_core_sha256": result[
                    "authorization_core_sha256"
                ],
                "dispatch_id": result["dispatch_id"],
                "dispatch_path": result["dispatch_path"],
                "run_id": result["run_id"],
                "queue_item_id": result["queue_item_id"],
                "lifecycle_state": result["lifecycle_state"],
                "audit_path": result["audit_path"],
                "reason":
                    "valid_dispatch_exists_without_exact_authorization_consumed",
                "non_authority": True,
            }
        )
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--authorization", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--audit", type=Path)
    parser.add_argument("--expected-sha256")
    parser.add_argument("--expected-byte-length", type=int)
    parser.add_argument(
        "--precreation-review",
        action="store_true",
        help="Validate exact content without requiring a lifecycle audit event.",
    )
    args = parser.parse_args()
    try:
        result = validate_dispatch_authorization(
            repo_root=args.repo_root,
            authorization_path=args.authorization,
            audit_path=args.audit,
            expected_whole_file_sha256=args.expected_sha256,
            expected_byte_length=args.expected_byte_length,
            require_audit=not args.precreation_review,
        )
    except DispatchAuthorizationError as exc:
        parser.exit(2, f"dispatch authorization validation stopped: {exc}\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
