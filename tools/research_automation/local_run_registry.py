"""Local run registry helper for AUTO-12.

This module indexes explicit caller-provided local output roots only. It does
not call runners, create authoritative evidence, expose query surfaces, or
define a formal schema.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING, Any, Iterable, Mapping

from tools.research_automation.batch_run_summary_validation import (
    validate_local_batch_run_summary_file,
)

if TYPE_CHECKING:
    from tools.research_automation.local_run_registry_validation import LocalRunRegistryValidationReport


IMPLEMENTATION_ID = "wp_12m_auto_12_local_run_registry_v1"
PACKAGE_LABEL = "WP-12m / AUTO-12"
LOCAL_RUN_REGISTRY_FILE_NAME = "local_run_registry.json"
CHECKED_BOUNDARIES = (
    "local_only",
    "research_only",
    "non_authoritative",
    "no_committed_evidence_artifact",
    "explicit_caller_provided_source_roots_only",
    "registry_output_root_must_exist",
    "no_source_output_mutation",
    "no_runtime_paper_live_oms_risk_safe_mode_contact",
    "no_exchange_broker_order_scheduler_daemon_queue_watcher_trigger_contact",
    "no_config_dependency_schema_validator_query_layer_contact",
)

DRY_RUN_FILES = {
    "validation_report": "validation_report.json",
    "run_request": "run_request.json",
    "manifest": "manifest.json",
    "output_bundle": "output_bundle.json",
}
BATCH_RUN_FILES = {
    "local_batch_run_summary": "local_batch_run_summary.json",
    "local_batch_run_summary_validation": "local_batch_run_summary_validation.json",
    "batch_manifest": "batch_manifest.json",
    "batch_validation_report": "batch_validation_report.json",
}


@dataclass(frozen=True)
class LocalRunRegistryRecord:
    registry_record_id: str
    source_kind: str
    package_label: str
    implementation_id: str
    output_root: str
    relative_paths: Mapping[str, str]
    run_id: str
    batch_id: str
    candidate_id: str
    evaluation_purpose: str
    validation_passed: bool
    failure_reasons: tuple[str, ...]
    local_only: bool
    research_only: bool
    non_authoritative: bool
    creates_committed_evidence: bool
    protected_boundary_preserved: bool
    source_file_hashes: Mapping[str, str]
    notes: tuple[str, ...]


@dataclass(frozen=True)
class LocalRunRegistryResult:
    records: tuple[LocalRunRegistryRecord, ...]
    registry_file: Path | None
    written_files: Mapping[str, Path]
    failure_reasons: tuple[str, ...]
    registry_validation_report: LocalRunRegistryValidationReport | None
    local_only: bool
    research_only: bool
    non_authoritative: bool
    creates_committed_evidence: bool
    protected_boundary_preserved: bool


def _stable_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _stable_digest(payload: Any) -> str:
    return hashlib.sha256(_stable_json(payload).encode("utf-8")).hexdigest()


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _failure_result(failure_reasons: Iterable[str]) -> LocalRunRegistryResult:
    return LocalRunRegistryResult(
        records=(),
        registry_file=None,
        written_files={},
        failure_reasons=tuple(failure_reasons),
        registry_validation_report=None,
        local_only=True,
        research_only=True,
        non_authoritative=True,
        creates_committed_evidence=False,
        protected_boundary_preserved=False,
    )


def _is_local_relative_reference(value: Any) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    if "\\" in value or (len(value) >= 2 and value[1] == ":"):
        return False
    path = PurePosixPath(value)
    if path.is_absolute():
        return False
    return ".." not in path.parts


def _validate_path_reference(value: Any, label: str, failures: list[str]) -> None:
    if not _is_local_relative_reference(value):
        failures.append(f"{label} must be a non-empty local relative path without traversal")


def _validate_path_mapping(value: Any, label: str, failures: list[str]) -> None:
    if not isinstance(value, Mapping):
        failures.append(f"{label} must be a mapping")
        return
    for key, path_value in value.items():
        if not isinstance(key, str) or not key.strip():
            failures.append(f"{label} keys must be non-empty strings")
        _validate_path_reference(path_value, f"{label}.{key}", failures)


def _load_json(path: Path, label: str, failures: list[str]) -> Mapping[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        failures.append(f"{label} could not be read: {exc}")
        return None
    except json.JSONDecodeError as exc:
        failures.append(f"{label} contains invalid JSON: {exc.msg}")
        return None
    if not isinstance(payload, Mapping):
        failures.append(f"{label} JSON must be an object")
        return None
    return payload


def _file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _existing_named_files(source_root: Path, file_names: Mapping[str, str]) -> dict[str, Path]:
    return {
        key: source_root / file_name
        for key, file_name in file_names.items()
        if (source_root / file_name).is_file()
    }


def _relative_paths(paths: Mapping[str, Path], source_root: Path) -> dict[str, str]:
    return {
        key: path.resolve().relative_to(source_root.resolve()).as_posix()
        for key, path in sorted(paths.items())
    }


def _source_hashes(paths: Mapping[str, Path], source_root: Path) -> dict[str, str]:
    relative = _relative_paths(paths, source_root)
    return {key: _file_hash(paths[key]) for key in sorted(relative)}


def _require_marker(
    payload: Mapping[str, Any],
    field_name: str,
    expected: bool,
    label: str,
    failures: list[str],
) -> None:
    if payload.get(field_name) is not expected:
        failures.append(f"{label}.{field_name} must be {expected}")


def _require_common_markers(payload: Mapping[str, Any], label: str, failures: list[str]) -> None:
    _require_marker(payload, "local_only", True, label, failures)
    _require_marker(payload, "non_authoritative", True, label, failures)
    if "research_only" in payload:
        _require_marker(payload, "research_only", True, label, failures)
    if "creates_committed_evidence" in payload:
        _require_marker(payload, "creates_committed_evidence", False, label, failures)


def _string_field(payload: Mapping[str, Any] | None, field_name: str) -> str:
    if payload is None:
        return ""
    value = payload.get(field_name)
    return value if isinstance(value, str) else ""


def _record_id(
    source_kind: str,
    relevant_ids: Mapping[str, str],
    relative_paths: Mapping[str, str],
    source_file_hashes: Mapping[str, str],
) -> str:
    payload = {
        "implementation_id": IMPLEMENTATION_ID,
        "package_label": PACKAGE_LABEL,
        "source_kind": source_kind,
        "relevant_ids": dict(sorted(relevant_ids.items())),
        "relative_paths": dict(sorted(relative_paths.items())),
        "source_file_hashes": dict(sorted(source_file_hashes.items())),
    }
    return f"LRR-{_stable_digest(payload)[:16].upper()}"


def _index_dry_run(source_root: Path) -> tuple[LocalRunRegistryRecord | None, tuple[str, ...]]:
    failures: list[str] = []
    paths = _existing_named_files(source_root, DRY_RUN_FILES)
    validation_report = _load_json(paths["validation_report"], "validation_report.json", failures)
    run_request = _load_json(paths["run_request"], "run_request.json", failures) if "run_request" in paths else None
    manifest = _load_json(paths["manifest"], "manifest.json", failures) if "manifest" in paths else None
    output_bundle = _load_json(paths["output_bundle"], "output_bundle.json", failures) if "output_bundle" in paths else None

    for label, payload in (
        ("validation_report", validation_report),
        ("run_request", run_request),
        ("manifest", manifest),
        ("output_bundle", output_bundle),
    ):
        if payload is not None:
            _require_common_markers(payload, label, failures)

    if validation_report is not None:
        if "passed" not in validation_report:
            failures.append("validation_report missing required field: passed")
        if "failure_reasons" not in validation_report:
            failures.append("validation_report missing required field: failure_reasons")
        boundaries = validation_report.get("checked_boundaries")
        if not isinstance(boundaries, list) and not isinstance(boundaries, tuple):
            failures.append("validation_report.checked_boundaries must be a sequence")
        elif "no_committed_evidence_artifact" not in boundaries:
            failures.append("validation_report.checked_boundaries must include no_committed_evidence_artifact")

    if run_request is not None:
        for field_name in ("run_id", "candidate_id", "evaluation_purpose"):
            if not _string_field(run_request, field_name):
                failures.append(f"run_request missing required field: {field_name}")
    if manifest is not None:
        _validate_path_mapping(manifest.get("output_files"), "manifest.output_files", failures)
    if output_bundle is not None:
        _require_marker(output_bundle, "creates_committed_evidence", False, "output_bundle", failures)

    if failures:
        return None, tuple(failures)

    relative_paths = _relative_paths(paths, source_root)
    source_file_hashes = _source_hashes(paths, source_root)
    validation_passed = bool(validation_report and validation_report.get("passed") is True)
    run_id = _string_field(run_request, "run_id") or _string_field(validation_report, "run_id")
    candidate_id = _string_field(run_request, "candidate_id")
    evaluation_purpose = _string_field(run_request, "evaluation_purpose")
    failure_reasons_value = validation_report.get("failure_reasons") if validation_report else ()
    failure_reasons = tuple(str(item) for item in failure_reasons_value) if isinstance(failure_reasons_value, (list, tuple)) else ()
    record = LocalRunRegistryRecord(
        registry_record_id=_record_id(
            "local_dry_run",
            {"run_id": run_id, "candidate_id": candidate_id},
            relative_paths,
            source_file_hashes,
        ),
        source_kind="local_dry_run",
        package_label=PACKAGE_LABEL,
        implementation_id=IMPLEMENTATION_ID,
        output_root=str(source_root.resolve()),
        relative_paths=relative_paths,
        run_id=run_id,
        batch_id="",
        candidate_id=candidate_id,
        evaluation_purpose=evaluation_purpose,
        validation_passed=validation_passed,
        failure_reasons=failure_reasons,
        local_only=True,
        research_only=True,
        non_authoritative=True,
        creates_committed_evidence=False,
        protected_boundary_preserved=validation_passed,
        source_file_hashes=source_file_hashes,
        notes=("failed dry-run output indexed as local non-authoritative record",)
        if not validation_passed
        else (),
    )
    return record, ()


def _index_batch_run(source_root: Path) -> tuple[LocalRunRegistryRecord | None, tuple[str, ...]]:
    failures: list[str] = []
    paths = _existing_named_files(source_root, BATCH_RUN_FILES)
    summary_path = paths["local_batch_run_summary"]
    validation_path = paths["local_batch_run_summary_validation"]
    summary = _load_json(summary_path, "local_batch_run_summary.json", failures)
    validation_report = _load_json(validation_path, "local_batch_run_summary_validation.json", failures)
    batch_manifest = _load_json(paths["batch_manifest"], "batch_manifest.json", failures) if "batch_manifest" in paths else None
    batch_validation_report = (
        _load_json(paths["batch_validation_report"], "batch_validation_report.json", failures)
        if "batch_validation_report" in paths
        else None
    )

    for label, payload in (
        ("local_batch_run_summary", summary),
        ("local_batch_run_summary_validation", validation_report),
        ("batch_manifest", batch_manifest),
        ("batch_validation_report", batch_validation_report),
    ):
        if payload is not None:
            _require_common_markers(payload, label, failures)

    if validation_report is not None and validation_report.get("passed") is not True:
        failures.append("local_batch_run_summary_validation.passed must be True")

    helper_report = validate_local_batch_run_summary_file(summary_path)
    if not helper_report.passed:
        failures.extend(f"batch summary validation helper: {reason}" for reason in helper_report.failure_reasons)

    if summary is not None:
        for field_name in ("batch_id", "item_count", "failure_reasons", "item_results"):
            if field_name not in summary:
                failures.append(f"local_batch_run_summary missing required field: {field_name}")
        _validate_path_mapping(summary.get("manifest_files"), "local_batch_run_summary.manifest_files", failures)
        _validate_path_reference(summary.get("summary_file"), "local_batch_run_summary.summary_file", failures)
    if batch_manifest is not None:
        _validate_path_mapping(batch_manifest.get("output_files"), "batch_manifest.output_files", failures)

    if failures:
        return None, tuple(failures)

    relative_paths = _relative_paths(paths, source_root)
    source_file_hashes = _source_hashes(paths, source_root)
    item_results = summary.get("item_results", ()) if summary else ()
    first_item = item_results[0] if isinstance(item_results, list) and item_results and isinstance(item_results[0], Mapping) else {}
    failure_reasons_value = summary.get("failure_reasons") if summary else ()
    failure_reasons = tuple(str(item) for item in failure_reasons_value) if isinstance(failure_reasons_value, (list, tuple)) else ()
    notes = (
        f"item_count={summary.get('item_count')}",
        f"failed_item_count={summary.get('failed_item_count')}",
        f"blocked_item_count={summary.get('blocked_item_count')}",
    )
    record = LocalRunRegistryRecord(
        registry_record_id=_record_id(
            "local_batch_run",
            {"batch_id": _string_field(summary, "batch_id")},
            relative_paths,
            source_file_hashes,
        ),
        source_kind="local_batch_run",
        package_label=PACKAGE_LABEL,
        implementation_id=IMPLEMENTATION_ID,
        output_root=str(source_root.resolve()),
        relative_paths=relative_paths,
        run_id="",
        batch_id=_string_field(summary, "batch_id"),
        candidate_id="",
        evaluation_purpose=_string_field(first_item, "source_id"),
        validation_passed=True,
        failure_reasons=failure_reasons,
        local_only=True,
        research_only=True,
        non_authoritative=True,
        creates_committed_evidence=False,
        protected_boundary_preserved=bool(summary.get("protected_boundary_preserved")),
        source_file_hashes=source_file_hashes,
        notes=notes,
    )
    return record, ()


def _detect_source_kind(source_root: Path) -> tuple[str | None, tuple[str, ...]]:
    dry_run_signature = (source_root / DRY_RUN_FILES["validation_report"]).is_file()
    batch_signature = (
        (source_root / BATCH_RUN_FILES["local_batch_run_summary"]).is_file()
        and (source_root / BATCH_RUN_FILES["local_batch_run_summary_validation"]).is_file()
    )
    if dry_run_signature and batch_signature:
        return None, ("source root contains both dry-run and batch-run signatures",)
    if dry_run_signature:
        return "local_dry_run", ()
    if batch_signature:
        return "local_batch_run", ()
    return None, ("source root has no recognized local run signature",)


def _registry_payload(records: tuple[LocalRunRegistryRecord, ...]) -> dict[str, Any]:
    record_payloads = [asdict(record) for record in records]
    return {
        "implementation_id": IMPLEMENTATION_ID,
        "package_label": PACKAGE_LABEL,
        "record_count": len(records),
        "records": record_payloads,
        "failure_reasons": [],
        "local_only": True,
        "research_only": True,
        "non_authoritative": True,
        "creates_committed_evidence": False,
        "protected_boundary_preserved": all(record.protected_boundary_preserved for record in records),
        "checked_boundaries": CHECKED_BOUNDARIES,
    }


def build_local_run_registry(
    source_roots: Iterable[str | Path],
    registry_output_root: str | Path,
) -> LocalRunRegistryResult:
    """Build one local non-authoritative registry file from explicit roots."""

    registry_root = registry_output_root if isinstance(registry_output_root, Path) else Path(registry_output_root)
    if not registry_root.exists() or not registry_root.is_dir():
        return _failure_result(("registry_output_root must be an existing directory",))

    source_root_tuple = tuple(source_roots)
    if not source_root_tuple:
        return _failure_result(("source_roots must contain at least one source root",))

    records: list[LocalRunRegistryRecord] = []
    failures: list[str] = []
    for source_root_value in source_root_tuple:
        source_root = source_root_value if isinstance(source_root_value, Path) else Path(source_root_value)
        if not source_root.exists() or not source_root.is_dir():
            failures.append(f"{source_root}: source root must be an existing directory")
            continue

        source_kind, detection_failures = _detect_source_kind(source_root)
        if detection_failures:
            failures.extend(f"{source_root}: {reason}" for reason in detection_failures)
            continue
        if source_kind == "local_dry_run":
            record, index_failures = _index_dry_run(source_root)
        else:
            record, index_failures = _index_batch_run(source_root)
        if index_failures:
            failures.extend(f"{source_root}: {reason}" for reason in index_failures)
        elif record is not None:
            records.append(record)

    if failures:
        return _failure_result(failures)

    record_tuple = tuple(sorted(records, key=lambda record: record.registry_record_id))
    registry_payload = _registry_payload(record_tuple)
    from tools.research_automation.local_run_registry_validation import validate_local_run_registry

    registry_validation_report = validate_local_run_registry(registry_payload)
    if not registry_validation_report.passed:
        return LocalRunRegistryResult(
            records=record_tuple,
            registry_file=None,
            written_files={},
            failure_reasons=tuple(registry_validation_report.failure_reasons),
            registry_validation_report=registry_validation_report,
            local_only=True,
            research_only=True,
            non_authoritative=True,
            creates_committed_evidence=False,
            protected_boundary_preserved=False,
        )

    registry_file = registry_root / LOCAL_RUN_REGISTRY_FILE_NAME
    _write_json(registry_file, registry_payload)
    return LocalRunRegistryResult(
        records=record_tuple,
        registry_file=registry_file,
        written_files={"local_run_registry": registry_file},
        failure_reasons=(),
        registry_validation_report=registry_validation_report,
        local_only=True,
        research_only=True,
        non_authoritative=True,
        creates_committed_evidence=False,
        protected_boundary_preserved=all(record.protected_boundary_preserved for record in record_tuple),
    )
