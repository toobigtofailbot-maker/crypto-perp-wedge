"""Validate JSON lifecycle_change artifacts."""

from __future__ import annotations

import argparse
import json
import re
import sys
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


DEFAULT_LIFECYCLE_CHANGES_DIR = REPO_ROOT / "research" / "lifecycle_changes"
DEFAULT_EXPERIMENTS_DIR = REPO_ROOT / "research" / "experiments"
DEFAULT_DECISION_CHANGES_DIR = REPO_ROOT / "research" / "decision_changes"
DEFAULT_RELEASE_NOTES_DIR = REPO_ROOT / "research" / "release_notes"
DEFAULT_AGENT_OUTPUTS_DIR = REPO_ROOT / "research" / "agent_outputs"
DEFAULT_MACRO_WINDOW_AGENT_OUTPUTS_DIR = REPO_ROOT / "research" / "macro_window_agent_outputs"
DEFAULT_BUCKET_MAPPINGS_DIR = REPO_ROOT / "research" / "bucket_mappings"
DEFAULT_PRE_GATE_ADVISORY_SNAPSHOTS_DIR = REPO_ROOT / "research" / "pre_gate_advisory_snapshots"
DEFAULT_OVERLAY_SHADOW_LOGS_DIR = REPO_ROOT / "research" / "overlay_shadow_logs"
DEFAULT_SHADOW_SIGNAL_SUMMARIES_DIR = REPO_ROOT / "research" / "shadow_signal_summaries"
DEFAULT_SHADOW_SIGNAL_SUMMARIES_V2_DIR = REPO_ROOT / "research" / "shadow_signal_summaries_v2"
LIFECYCLE_CHANGE_SCHEMA_PATH = REPO_ROOT / "research" / "schemas" / "lifecycle_change.schema.json"

OPERATIONAL_TO_STATES = {"paper_active", "live_eligible", "live_active"}
NON_ARCHIVED_RECOVERY_STATES = {
    "proposed",
    "in_research",
    "research_concluded",
    "paper_eligible",
    "paper_active",
    "paper_concluded",
    "live_eligible",
    "live_active",
}
TRANSITION_EDGE_STATES = {
    "proposed->in_research": ("proposed", {"in_research"}),
    "proposed->halted": ("proposed", {"halted"}),
    "in_research->research_concluded": ("in_research", {"research_concluded"}),
    "in_research->halted": ("in_research", {"halted"}),
    "research_concluded->paper_eligible": ("research_concluded", {"paper_eligible"}),
    "research_concluded->archived": ("research_concluded", {"archived"}),
    "research_concluded->halted": ("research_concluded", {"halted"}),
    "paper_eligible->paper_active": ("paper_eligible", {"paper_active"}),
    "paper_eligible->archived": ("paper_eligible", {"archived"}),
    "paper_eligible->halted": ("paper_eligible", {"halted"}),
    "paper_active->paper_concluded": ("paper_active", {"paper_concluded"}),
    "paper_active->halted": ("paper_active", {"halted"}),
    "paper_active->archived": ("paper_active", {"archived"}),
    "paper_concluded->live_eligible": ("paper_concluded", {"live_eligible"}),
    "paper_concluded->archived": ("paper_concluded", {"archived"}),
    "paper_concluded->halted": ("paper_concluded", {"halted"}),
    "live_eligible->live_active": ("live_eligible", {"live_active"}),
    "live_eligible->archived": ("live_eligible", {"archived"}),
    "live_eligible->halted": ("live_eligible", {"halted"}),
    "live_active->paper_concluded": ("live_active", {"paper_concluded"}),
    "live_active->halted": ("live_active", {"halted"}),
    "live_active->archived": ("live_active", {"archived"}),
    "halted->archived": ("halted", {"archived"}),
    "halted->previous_non_halted_state": ("halted", NON_ARCHIVED_RECOVERY_STATES),
}
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
}


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


def _load_experiment_ids(experiments_dir: Path) -> tuple[set[str], set[str]]:
    plan_ids = _load_ids(experiments_dir, "*.plan.json", "plan_id")
    report_ids = _load_ids(experiments_dir, "*.report.json", "report_id")
    return plan_ids, report_ids


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


def _known_ref_family(ref_value: str) -> str | None:
    for family, pattern in KNOWN_REF_PATTERNS.items():
        if pattern.match(ref_value):
            return family
    return None


def _known_ref_ids(
    *,
    lifecycle_change_ids: set[str],
    experiments_dir: Path,
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
    plan_ids, report_ids = _load_experiment_ids(experiments_dir)
    return {
        "EXP": plan_ids,
        "REP": report_ids,
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
        "LCH": lifecycle_change_ids,
    }


def _is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _is_non_empty_list(value: Any) -> bool:
    return isinstance(value, list) and len(value) > 0


def _validate_transition_shape(path: Path, payload: dict[str, Any]) -> list[str]:
    transition_edge = payload.get("transition_edge")
    from_state = payload.get("from_state")
    to_state = payload.get("to_state")
    expected = TRANSITION_EDGE_STATES.get(transition_edge)
    if expected is None:
        return [f"{path}: transition_edge is not permitted: {transition_edge}"]
    expected_from, expected_to_states = expected
    if from_state != expected_from or to_state not in expected_to_states:
        return [
            f"{path}: transition_edge {transition_edge} does not match "
            f"from_state/to_state {from_state}->{to_state}"
        ]
    return []


def _validate_refs(
    *,
    path: Path,
    field_name: str,
    values: Any,
    known_ids: dict[str, set[str]],
    repo_root: Path,
) -> list[str]:
    errors: list[str] = []
    if not isinstance(values, list):
        return errors
    for ref_value in values:
        if not isinstance(ref_value, str):
            continue
        family = _known_ref_family(ref_value)
        if family is not None:
            if ref_value not in known_ids.get(family, set()):
                errors.append(f"{path}: {field_name} unresolved {family} reference: {ref_value}")
            continue

        ref_path = _resolve_repo_path(repo_root, ref_value)
        if ref_path is None:
            errors.append(f"{path}: {field_name} invalid repo-relative path reference: {ref_value}")
        elif not ref_path.exists():
            errors.append(f"{path}: {field_name} repo-relative path does not exist: {ref_value}")
    return errors


def validate_lifecycle_changes(
    lifecycle_changes_dir: Path = DEFAULT_LIFECYCLE_CHANGES_DIR,
    registry_path: Path = DEFAULT_REGISTRY_PATH,
    experiments_dir: Path = DEFAULT_EXPERIMENTS_DIR,
    decision_changes_dir: Path = DEFAULT_DECISION_CHANGES_DIR,
    release_notes_dir: Path = DEFAULT_RELEASE_NOTES_DIR,
    agent_outputs_dir: Path = DEFAULT_AGENT_OUTPUTS_DIR,
    macro_window_agent_outputs_dir: Path = DEFAULT_MACRO_WINDOW_AGENT_OUTPUTS_DIR,
    bucket_mappings_dir: Path = DEFAULT_BUCKET_MAPPINGS_DIR,
    pre_gate_advisory_snapshots_dir: Path = DEFAULT_PRE_GATE_ADVISORY_SNAPSHOTS_DIR,
    overlay_shadow_logs_dir: Path = DEFAULT_OVERLAY_SHADOW_LOGS_DIR,
    shadow_signal_summaries_dir: Path = DEFAULT_SHADOW_SIGNAL_SUMMARIES_DIR,
    shadow_signal_summaries_v2_dir: Path = DEFAULT_SHADOW_SIGNAL_SUMMARIES_V2_DIR,
    schema_path: Path = LIFECYCLE_CHANGE_SCHEMA_PATH,
    repo_root: Path = REPO_ROOT,
) -> list[str]:
    """Return validation errors for lifecycle_change artifacts, or [] when valid."""

    schema = load_json(schema_path)
    Draft7Validator.check_schema(schema)
    validator = Draft7Validator(schema)

    if not lifecycle_changes_dir.exists():
        return []

    lifecycle_files = sorted(lifecycle_changes_dir.rglob("*.lifecycle_change.json"))
    if not lifecycle_files:
        return []

    errors: list[str] = []
    candidate_ids = load_candidate_ids(registry_path)
    payloads: list[tuple[Path, dict[str, Any]]] = []
    known_lifecycle_change_ids: set[str] = set()
    id_paths: dict[str, Path] = {}

    for path in lifecycle_files:
        payload, file_errors = _validate_json_file(path, validator)
        errors.extend(file_errors)
        if payload is None:
            continue
        payloads.append((path, payload))

        lifecycle_change_id = payload.get("lifecycle_change_id")
        if isinstance(lifecycle_change_id, str):
            expected_name = f"{lifecycle_change_id}.lifecycle_change.json"
            if path.name != expected_name:
                errors.append(f"{path}: filename must be {expected_name}")
            if lifecycle_change_id in known_lifecycle_change_ids:
                errors.append(
                    f"{path}: duplicate lifecycle_change_id {lifecycle_change_id}; "
                    f"first seen at {id_paths[lifecycle_change_id]}"
                )
            known_lifecycle_change_ids.add(lifecycle_change_id)
            id_paths.setdefault(lifecycle_change_id, path)
        else:
            errors.append(f"{path}: missing valid lifecycle_change_id")

    known_ids = _known_ref_ids(
        lifecycle_change_ids=known_lifecycle_change_ids,
        experiments_dir=experiments_dir,
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
        lifecycle_change_id = payload.get("lifecycle_change_id")
        candidate_id = payload.get("candidate_id")
        if candidate_id not in candidate_ids:
            errors.append(f"{path}: candidate_id not found in registry: {candidate_id}")

        supersedes_lch_id = payload.get("supersedes_lch_id")
        if supersedes_lch_id is not None:
            if supersedes_lch_id == lifecycle_change_id:
                errors.append(f"{path}: supersedes_lch_id cannot reference itself: {supersedes_lch_id}")
            elif supersedes_lch_id not in known_lifecycle_change_ids:
                errors.append(
                    f"{path}: supersedes_lch_id not found in discovered lifecycle changes: "
                    f"{supersedes_lch_id}"
                )

        errors.extend(_validate_transition_shape(path, payload))

        to_state = payload.get("to_state")
        from_state = payload.get("from_state")
        evidence_refs = payload.get("evidence_artifact_refs")
        risk_acknowledgment = payload.get("risk_acknowledgment")
        is_recovery = from_state == "halted" and to_state != "archived"
        if to_state in OPERATIONAL_TO_STATES or is_recovery:
            if not _is_non_empty_list(evidence_refs):
                errors.append(f"{path}: operational lifecycle transition requires evidence_artifact_refs")
            if not _is_non_empty_string(risk_acknowledgment):
                errors.append(f"{path}: operational lifecycle transition requires risk_acknowledgment")

        if payload.get("retrospective_flag") is True and not _is_non_empty_string(
            payload.get("retrospective_disclosure")
        ):
            errors.append(f"{path}: retrospective_flag=true requires retrospective_disclosure")

        if payload.get("fast_track_flag") is True:
            if to_state != "live_eligible":
                errors.append(f"{path}: fast_track_flag=true requires to_state live_eligible")
            if not _is_non_empty_list(payload.get("strong_candidate_criteria_refs")):
                errors.append(f"{path}: fast_track_flag=true requires strong_candidate_criteria_refs")
            if not _is_non_empty_list(evidence_refs):
                errors.append(f"{path}: fast_track_flag=true requires evidence_artifact_refs")
            if not _is_non_empty_string(risk_acknowledgment):
                errors.append(f"{path}: fast_track_flag=true requires risk_acknowledgment")

        errors.extend(
            _validate_refs(
                path=path,
                field_name="evidence_artifact_refs",
                values=evidence_refs,
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
            )
        )
        errors.extend(
            _validate_refs(
                path=path,
                field_name="strong_candidate_criteria_refs",
                values=payload.get("strong_candidate_criteria_refs"),
                known_ids=known_ids,
                repo_root=repo_root,
            )
        )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lifecycle-changes-dir", type=Path, default=DEFAULT_LIFECYCLE_CHANGES_DIR)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY_PATH)
    parser.add_argument("--schema", type=Path, default=LIFECYCLE_CHANGE_SCHEMA_PATH)
    args = parser.parse_args()

    errors = validate_lifecycle_changes(
        lifecycle_changes_dir=args.lifecycle_changes_dir,
        registry_path=args.registry,
        schema_path=args.schema,
    )
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    if not args.lifecycle_changes_dir.exists():
        print(f"OK: {args.lifecycle_changes_dir} does not exist; nothing to validate")
    else:
        print(f"OK: lifecycle_change artifacts under {args.lifecycle_changes_dir} validate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
