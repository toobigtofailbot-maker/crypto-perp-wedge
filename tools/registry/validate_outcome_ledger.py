"""Validate JSON outcome_ledger artifacts."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, datetime, time, timezone
from pathlib import Path
from typing import Any

from jsonschema import Draft7Validator

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.registry.validate_registry import (
    DEFAULT_REGISTRY_PATH,
    load_registry_rows,
)


DEFAULT_OUTCOME_LEDGERS_DIR = REPO_ROOT / "research" / "outcome_ledgers"
DEFAULT_EXPERIMENTS_DIR = REPO_ROOT / "research" / "experiments"
DEFAULT_LIFECYCLE_CHANGES_DIR = REPO_ROOT / "research" / "lifecycle_changes"
DEFAULT_DECISION_CHANGES_DIR = REPO_ROOT / "research" / "decision_changes"
DEFAULT_RELEASE_NOTES_DIR = REPO_ROOT / "research" / "release_notes"
DEFAULT_AGENT_OUTPUTS_DIR = REPO_ROOT / "research" / "agent_outputs"
DEFAULT_MACRO_WINDOW_AGENT_OUTPUTS_DIR = REPO_ROOT / "research" / "macro_window_agent_outputs"
DEFAULT_BUCKET_MAPPINGS_DIR = REPO_ROOT / "research" / "bucket_mappings"
DEFAULT_PRE_GATE_ADVISORY_SNAPSHOTS_DIR = REPO_ROOT / "research" / "pre_gate_advisory_snapshots"
DEFAULT_OVERLAY_SHADOW_LOGS_DIR = REPO_ROOT / "research" / "overlay_shadow_logs"
DEFAULT_SHADOW_SIGNAL_SUMMARIES_DIR = REPO_ROOT / "research" / "shadow_signal_summaries"
DEFAULT_SHADOW_SIGNAL_SUMMARIES_V2_DIR = REPO_ROOT / "research" / "shadow_signal_summaries_v2"
OUTCOME_LEDGER_SCHEMA_PATH = REPO_ROOT / "research" / "schemas" / "outcome_ledger.schema.json"

KNOWN_REF_PATTERNS = {
    "EXP": re.compile(r"^EXP-[0-9]{4}$"),
    "REP": re.compile(r"^REP-[0-9]{4}$"),
    "DCH": re.compile(r"^DCH-[0-9]{4}$"),
    "REL": re.compile(r"^REL-[0-9]{4}$"),
    "PGAS": re.compile(r"^PGAS-[0-9]{4}$"),
    "AOUT": re.compile(r"^AOUT-[0-9]{4}$"),
    "MOUT": re.compile(r"^MOUT-[0-9]{4}$"),
    "BMAP": re.compile(r"^BMAP-[0-9]{4}$"),
    "OSH": re.compile(r"^OSH-[0-9]{4}$"),
    "SSS": re.compile(r"^SSS-[0-9]{4}$"),
    "LCH": re.compile(r"^LCH-[0-9]{4}$"),
    "OL": re.compile(r"^OL-[0-9]{4}$"),
}
ADVISORY_REF_FAMILIES = {"AOUT", "MOUT", "BMAP", "PGAS", "OSH", "SSS"}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_candidate_ids(registry_path: Path = DEFAULT_REGISTRY_PATH) -> set[str]:
    return {
        row["candidate_id"]
        for _, row in load_registry_rows(registry_path)
        if isinstance(row.get("candidate_id"), str)
    }


def _format_schema_error(error: Any) -> str:
    location = ".".join(str(part) for part in error.absolute_path)
    if location:
        return f"{location}: {error.message}"
    return error.message


def _validate_json_file(path: Path, validator: Draft7Validator) -> tuple[dict[str, Any] | None, list[str]]:
    errors: list[str] = []
    try:
        payload = load_json(path)
    except json.JSONDecodeError as exc:
        return None, [f"{path}: invalid JSON: {exc}"]

    for schema_error in sorted(validator.iter_errors(payload), key=lambda err: list(err.path)):
        errors.append(f"{path}: {_format_schema_error(schema_error)}")
    return payload, errors


def _load_ids(directory: Path, glob_pattern: str, id_field: str) -> set[str]:
    ids: set[str] = set()
    if not directory.exists():
        return ids
    for path in sorted(directory.rglob(glob_pattern)):
        try:
            payload = load_json(path)
        except json.JSONDecodeError:
            continue
        artifact_id = payload.get(id_field)
        if isinstance(artifact_id, str):
            ids.add(artifact_id)
    return ids


def _load_report_paths(experiments_dir: Path, repo_root: Path) -> dict[str, Path]:
    report_paths: dict[str, Path] = {}
    if not experiments_dir.exists():
        return report_paths
    for path in sorted(experiments_dir.rglob("REP-*.report.json")):
        try:
            payload = load_json(path)
        except json.JSONDecodeError:
            continue
        report_id = payload.get("report_id")
        if isinstance(report_id, str):
            report_paths[report_id] = path.resolve()
    return report_paths


def _known_ref_family(ref_value: str) -> str | None:
    for family, pattern in KNOWN_REF_PATTERNS.items():
        if pattern.match(ref_value):
            return family
    return None


def _resolve_repo_path(repo_root: Path, ref_value: str) -> Path | None:
    candidate = Path(ref_value)
    if candidate.is_absolute() or ".." in candidate.parts:
        return None
    resolved = (repo_root / candidate).resolve()
    try:
        resolved.relative_to(repo_root.resolve())
    except ValueError:
        return None
    return resolved


def _known_ref_ids(
    *,
    outcome_ledger_ids: set[str],
    experiments_dir: Path,
    lifecycle_changes_dir: Path,
    decision_changes_dir: Path,
    release_notes_dir: Path,
    agent_outputs_dir: Path,
    macro_window_agent_outputs_dir: Path,
    bucket_mappings_dir: Path,
    pre_gate_advisory_snapshots_dir: Path,
    overlay_shadow_logs_dir: Path,
    shadow_signal_summaries_dir: Path,
    shadow_signal_summaries_v2_dir: Path,
) -> dict[str, set[str]]:
    return {
        "EXP": _load_ids(experiments_dir, "EXP-*.plan.json", "plan_id"),
        "REP": _load_ids(experiments_dir, "REP-*.report.json", "report_id"),
        "DCH": _load_ids(decision_changes_dir, "*.decision_change.json", "decision_change_id"),
        "REL": _load_ids(release_notes_dir, "*.release_notes.json", "release_notes_id"),
        "PGAS": _load_ids(
            pre_gate_advisory_snapshots_dir,
            "*.pre_gate_advisory_snapshot.json",
            "pre_gate_advisory_snapshot_id",
        ),
        "AOUT": _load_ids(agent_outputs_dir, "*.agent_output.json", "agent_output_id"),
        "MOUT": _load_ids(
            macro_window_agent_outputs_dir,
            "*.macro_window_agent_output.json",
            "macro_window_agent_output_id",
        ),
        "BMAP": _load_ids(bucket_mappings_dir, "*.bucket_mapping.json", "bucket_mapping_id"),
        "OSH": _load_ids(overlay_shadow_logs_dir, "*.overlay_shadow_log.json", "overlay_shadow_log_id"),
        "SSS": _load_ids(
            shadow_signal_summaries_dir,
            "*.shadow_signal_summary.json",
            "shadow_signal_summary_id",
        )
        | _load_ids(
            shadow_signal_summaries_v2_dir,
            "*.shadow_signal_summary.json",
            "shadow_signal_summary_id",
        ),
        "LCH": _load_ids(lifecycle_changes_dir, "*.lifecycle_change.json", "lifecycle_change_id"),
        "OL": outcome_ledger_ids,
    }


def _parse_datetime(value: Any, *, require_timezone: bool) -> datetime | None:
    if not isinstance(value, str):
        return None
    normalized = value.replace("Z", "+00:00")
    try:
        parsed_datetime = datetime.fromisoformat(normalized)
    except ValueError:
        try:
            parsed_date = date.fromisoformat(value)
        except ValueError:
            return None
        if require_timezone:
            return None
        return datetime.combine(parsed_date, time.min, tzinfo=timezone.utc)
    if require_timezone and parsed_datetime.tzinfo is None:
        return None
    if parsed_datetime.tzinfo is None:
        return parsed_datetime.replace(tzinfo=timezone.utc)
    return parsed_datetime


def _validate_window_pair(path: Path, start_value: Any, end_value: Any, field_prefix: str) -> list[str]:
    if start_value is None and end_value is None:
        return []
    if start_value is None or end_value is None:
        return [f"{path}: {field_prefix} window must have both start and end or both null"]

    start = _parse_datetime(start_value, require_timezone=False)
    end = _parse_datetime(end_value, require_timezone=False)
    errors: list[str] = []
    if start is None:
        errors.append(f"{path}: {field_prefix} window start is not parseable: {start_value}")
    if end is None:
        errors.append(f"{path}: {field_prefix} window end is not parseable: {end_value}")
    if start is not None and end is not None and end < start:
        errors.append(f"{path}: {field_prefix} window end is before start: {end_value} < {start_value}")
    return errors


def _validate_refs(
    *,
    path: Path,
    field_name: str,
    values: Any,
    known_ids: dict[str, set[str]],
    repo_root: Path,
    allowed_families: set[str] | None = None,
) -> list[str]:
    errors: list[str] = []
    if not isinstance(values, list):
        return errors
    for ref_value in values:
        if not isinstance(ref_value, str):
            continue
        family = _known_ref_family(ref_value)
        if family is not None:
            if allowed_families is not None and family not in allowed_families:
                errors.append(f"{path}: {field_name} unsupported {family} reference: {ref_value}")
            elif ref_value not in known_ids.get(family, set()):
                errors.append(f"{path}: {field_name} unresolved {family} reference: {ref_value}")
            continue

        ref_path = _resolve_repo_path(repo_root, ref_value)
        if ref_path is None:
            errors.append(f"{path}: {field_name} invalid repo-relative path reference: {ref_value}")
        elif not ref_path.exists():
            errors.append(f"{path}: {field_name} repo-relative path does not exist: {ref_value}")
    return errors


def validate_outcome_ledgers(
    outcome_ledgers_dir: Path = DEFAULT_OUTCOME_LEDGERS_DIR,
    registry_path: Path = DEFAULT_REGISTRY_PATH,
    experiments_dir: Path = DEFAULT_EXPERIMENTS_DIR,
    lifecycle_changes_dir: Path = DEFAULT_LIFECYCLE_CHANGES_DIR,
    decision_changes_dir: Path = DEFAULT_DECISION_CHANGES_DIR,
    release_notes_dir: Path = DEFAULT_RELEASE_NOTES_DIR,
    agent_outputs_dir: Path = DEFAULT_AGENT_OUTPUTS_DIR,
    macro_window_agent_outputs_dir: Path = DEFAULT_MACRO_WINDOW_AGENT_OUTPUTS_DIR,
    bucket_mappings_dir: Path = DEFAULT_BUCKET_MAPPINGS_DIR,
    pre_gate_advisory_snapshots_dir: Path = DEFAULT_PRE_GATE_ADVISORY_SNAPSHOTS_DIR,
    overlay_shadow_logs_dir: Path = DEFAULT_OVERLAY_SHADOW_LOGS_DIR,
    shadow_signal_summaries_dir: Path = DEFAULT_SHADOW_SIGNAL_SUMMARIES_DIR,
    shadow_signal_summaries_v2_dir: Path = DEFAULT_SHADOW_SIGNAL_SUMMARIES_V2_DIR,
    schema_path: Path = OUTCOME_LEDGER_SCHEMA_PATH,
    repo_root: Path = REPO_ROOT,
) -> list[str]:
    """Return validation errors for outcome_ledger artifacts, or [] when valid."""

    schema = load_json(schema_path)
    Draft7Validator.check_schema(schema)
    validator = Draft7Validator(schema)

    if not outcome_ledgers_dir.exists():
        return []

    outcome_files = sorted(outcome_ledgers_dir.rglob("*.outcome_ledger.json"))
    if not outcome_files:
        return []

    errors: list[str] = []
    candidate_ids = load_candidate_ids(registry_path)
    report_paths = _load_report_paths(experiments_dir, repo_root)
    payloads: list[tuple[Path, dict[str, Any]]] = []
    known_outcome_ids: set[str] = set()
    id_paths: dict[str, Path] = {}

    for path in outcome_files:
        payload, file_errors = _validate_json_file(path, validator)
        errors.extend(file_errors)
        if payload is None:
            continue
        payloads.append((path, payload))

        outcome_id = payload.get("outcome_id")
        if isinstance(outcome_id, str):
            expected_name = f"{outcome_id}.outcome_ledger.json"
            if path.name != expected_name:
                errors.append(f"{path}: filename must be {expected_name}")
            if outcome_id in known_outcome_ids:
                errors.append(
                    f"{path}: duplicate outcome_id {outcome_id}; first seen at {id_paths[outcome_id]}"
                )
            known_outcome_ids.add(outcome_id)
            id_paths.setdefault(outcome_id, path)
        else:
            errors.append(f"{path}: missing valid outcome_id")

    known_ids = _known_ref_ids(
        outcome_ledger_ids=known_outcome_ids,
        experiments_dir=experiments_dir,
        lifecycle_changes_dir=lifecycle_changes_dir,
        decision_changes_dir=decision_changes_dir,
        release_notes_dir=release_notes_dir,
        agent_outputs_dir=agent_outputs_dir,
        macro_window_agent_outputs_dir=macro_window_agent_outputs_dir,
        bucket_mappings_dir=bucket_mappings_dir,
        pre_gate_advisory_snapshots_dir=pre_gate_advisory_snapshots_dir,
        overlay_shadow_logs_dir=overlay_shadow_logs_dir,
        shadow_signal_summaries_dir=shadow_signal_summaries_dir,
        shadow_signal_summaries_v2_dir=shadow_signal_summaries_v2_dir,
    )

    for path, payload in payloads:
        candidate_id = payload.get("candidate_id")
        if candidate_id not in candidate_ids:
            errors.append(f"{path}: candidate_id not found in registry: {candidate_id}")

        derivation_record = payload.get("derivation_record")
        if isinstance(derivation_record, dict):
            derivation_timestamp = derivation_record.get("derivation_timestamp")
            if _parse_datetime(derivation_timestamp, require_timezone=True) is None:
                errors.append(
                    f"{path}: derivation_record.derivation_timestamp is not timezone-qualified: "
                    f"{derivation_timestamp}"
                )

            source_artifact_id = derivation_record.get("source_artifact_id")
            source_artifact_path = derivation_record.get("source_artifact_path")
            source_method = derivation_record.get("derivation_method")
            report_path = report_paths.get(source_artifact_id)
            if report_path is None:
                errors.append(f"{path}: source_artifact_id not found in discovered reports: {source_artifact_id}")
            if source_method == "from_rep_artifact":
                resolved_path = (
                    _resolve_repo_path(repo_root, source_artifact_path)
                    if isinstance(source_artifact_path, str)
                    else None
                )
                if resolved_path is None:
                    errors.append(f"{path}: source_artifact_path invalid repo-relative path: {source_artifact_path}")
                elif not resolved_path.exists():
                    errors.append(f"{path}: source_artifact_path does not exist: {source_artifact_path}")
                elif report_path is not None and resolved_path != report_path:
                    errors.append(
                        f"{path}: source_artifact_path {source_artifact_path} does not match "
                        f"source_artifact_id {source_artifact_id}"
                    )

        data_provenance = payload.get("data_provenance")
        errors.extend(
            _validate_window_pair(
                path,
                payload.get("evaluation_window_start"),
                payload.get("evaluation_window_end"),
                "evaluation",
            )
        )
        if isinstance(data_provenance, dict):
            errors.extend(
                _validate_window_pair(
                    path,
                    data_provenance.get("source_data_window_start"),
                    data_provenance.get("source_data_window_end"),
                    "source_data",
                )
            )

        errors.extend(
            _validate_refs(
                path=path,
                field_name="linked_artifacts",
                values=payload.get("linked_artifacts"),
                known_ids=known_ids,
                repo_root=repo_root,
            )
        )
        errors.extend(
            _validate_refs(
                path=path,
                field_name="linked_advisory_artifacts",
                values=payload.get("linked_advisory_artifacts"),
                known_ids=known_ids,
                repo_root=repo_root,
                allowed_families=ADVISORY_REF_FAMILIES,
            )
        )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outcome-ledgers-dir", type=Path, default=DEFAULT_OUTCOME_LEDGERS_DIR)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY_PATH)
    parser.add_argument("--schema", type=Path, default=OUTCOME_LEDGER_SCHEMA_PATH)
    args = parser.parse_args()

    errors = validate_outcome_ledgers(
        outcome_ledgers_dir=args.outcome_ledgers_dir,
        registry_path=args.registry,
        schema_path=args.schema,
    )
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    if not args.outcome_ledgers_dir.exists():
        print(f"OK: {args.outcome_ledgers_dir} does not exist; nothing to validate")
    else:
        print(f"OK: outcome_ledger artifacts under {args.outcome_ledgers_dir} validate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
