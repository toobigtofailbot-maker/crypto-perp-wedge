"""Validate candidate lifecycle registry artifacts."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from jsonschema import Draft7Validator


REPO_ROOT = Path(__file__).resolve().parents[2]
CANDIDATE_LIFECYCLE_REGISTRY_SCHEMA_PATH = (
    REPO_ROOT / "research" / "schemas" / "candidate_lifecycle_registry.schema.json"
)
DEFAULT_CANDIDATE_REGISTRY_FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "candidate_lifecycle_registry"

NON_AUTHORITY_FLAGS = {
    "not_candidate_approval",
    "not_paper_live_authority",
    "not_runtime_authority",
    "not_promotion_authority",
    "not_trading_recommendation",
    "not_broker_exchange_authority",
    "not_capital_authority",
}
ALLOWED_TRANSITIONS = {
    "proposed": {"validated_research", "rejected", "retired"},
    "validated_research": {"paper_candidate", "rejected", "retired", "proposed"},
    "paper_candidate": {"paper_running", "demoted", "rejected", "retired"},
    "paper_running": {"promoted_live", "demoted", "rejected", "retired", "paper_candidate"},
    "promoted_live": {"demoted", "retired", "paper_candidate", "rejected"},
    "rejected": {"proposed", "retired"},
    "demoted": {"validated_research", "paper_candidate", "rejected", "retired"},
    "retired": {"proposed"},
}
EVIDENCE_REQUIRED_TO_STATES = {"rejected", "demoted"}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _format_schema_error(error: Any) -> str:
    location = ".".join(str(part) for part in error.absolute_path)
    if location:
        return f"{location}: {error.message}"
    return error.message


def _validate_json_file(path: Path, validator: Draft7Validator) -> tuple[dict[str, Any] | None, list[str]]:
    try:
        payload = load_json(path)
    except json.JSONDecodeError as exc:
        return None, [f"{path}: invalid JSON: {exc}"]

    errors = [
        f"{path}: {_format_schema_error(schema_error)}"
        for schema_error in sorted(validator.iter_errors(payload), key=lambda err: list(err.path))
    ]
    return payload, errors


def _registry_files(registry_dir: Path) -> list[Path]:
    if not registry_dir.exists():
        return []
    return sorted(registry_dir.rglob("*.candidate_lifecycle_registry.json"))


def _parse_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _non_authority_errors(path: Path, label: str, declaration: Any) -> list[str]:
    if not isinstance(declaration, dict):
        return []
    errors: list[str] = []
    for flag in sorted(NON_AUTHORITY_FLAGS):
        if declaration.get(flag) is not True:
            errors.append(f"{path}: {label} forbidden authority flag is not true: {flag}")
    return errors


def _has_artifact_type(links: Any, artifact_type: str) -> bool:
    return isinstance(links, list) and any(
        isinstance(link, dict) and link.get("artifact_type") == artifact_type for link in links
    )


def _validate_registry_semantics(path: Path, payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    errors.extend(_non_authority_errors(path, "registry", payload.get("non_authority_declaration")))

    candidates = payload.get("candidates")
    ledger = payload.get("append_only_ledger")
    if not isinstance(candidates, list) or not isinstance(ledger, list):
        return errors

    candidate_ids: set[str] = set()
    candidate_by_id: dict[str, dict[str, Any]] = {}
    for candidate in candidates:
        if not isinstance(candidate, dict):
            continue
        candidate_id = candidate.get("candidate_id")
        if not isinstance(candidate_id, str):
            continue
        if candidate_id in candidate_ids:
            errors.append(f"{path}: duplicate candidate_id {candidate_id}")
        candidate_ids.add(candidate_id)
        candidate_by_id[candidate_id] = candidate
        errors.extend(_non_authority_errors(path, f"candidate {candidate_id}", candidate.get("non_authority_declaration")))

    event_ids: set[str] = set()
    events_by_candidate: dict[str, list[dict[str, Any]]] = {}
    for event in ledger:
        if not isinstance(event, dict):
            continue
        event_id = event.get("event_id")
        candidate_id = event.get("candidate_id")
        if isinstance(event_id, str):
            if event_id in event_ids:
                errors.append(f"{path}: duplicate event_id {event_id}")
            event_ids.add(event_id)
        if isinstance(candidate_id, str):
            if candidate_id not in candidate_ids:
                errors.append(f"{path}: event {event_id} references unknown candidate_id {candidate_id}")
            events_by_candidate.setdefault(candidate_id, []).append(event)
        errors.extend(_non_authority_errors(path, f"event {event_id}", event.get("non_authority_declaration")))

    for candidate_id, candidate in candidate_by_id.items():
        lifecycle_event_refs = candidate.get("lifecycle_event_refs", [])
        if isinstance(lifecycle_event_refs, list):
            for event_ref in lifecycle_event_refs:
                if event_ref not in event_ids:
                    errors.append(f"{path}: candidate {candidate_id} references unknown lifecycle event {event_ref}")

        candidate_events = events_by_candidate.get(candidate_id, [])
        if not candidate_events:
            errors.append(f"{path}: candidate {candidate_id} has no append_only_ledger events")
            continue

        sorted_events = sorted(candidate_events, key=lambda event: event.get("event_sequence", 0))
        seen_sequences: set[int] = set()
        previous_timestamp: datetime | None = None
        previous_status: str | None = None
        saw_rejected = False

        for expected_sequence, event in enumerate(sorted_events, 1):
            event_id = event.get("event_id")
            event_sequence = event.get("event_sequence")
            if event_sequence in seen_sequences:
                errors.append(f"{path}: candidate {candidate_id} duplicate event_sequence {event_sequence}")
            if event_sequence != expected_sequence:
                errors.append(
                    f"{path}: candidate {candidate_id} event {event_id} has event_sequence "
                    f"{event_sequence}; expected {expected_sequence}"
                )
            if isinstance(event_sequence, int):
                seen_sequences.add(event_sequence)

            timestamp = _parse_timestamp(event.get("timestamp_utc"))
            if previous_timestamp is not None and timestamp is not None and timestamp < previous_timestamp:
                errors.append(f"{path}: candidate {candidate_id} event {event_id} timestamp moves backward")
            if timestamp is not None:
                previous_timestamp = timestamp

            from_status = event.get("from_status")
            to_status = event.get("to_status")
            if expected_sequence == 1:
                if from_status is not None or to_status != "proposed":
                    errors.append(
                        f"{path}: candidate {candidate_id} first event must move null->proposed; "
                        f"found {from_status}->{to_status}"
                    )
            else:
                if from_status != previous_status:
                    errors.append(
                        f"{path}: candidate {candidate_id} event {event_id} from_status {from_status} "
                        f"does not match previous status {previous_status}"
                    )
                allowed_to_states = ALLOWED_TRANSITIONS.get(str(from_status), set())
                if to_status not in allowed_to_states:
                    errors.append(
                        f"{path}: candidate {candidate_id} forbidden transition {from_status}->{to_status}"
                    )

            related_evidence_links = event.get("related_evidence_links")
            if to_status in EVIDENCE_REQUIRED_TO_STATES and not related_evidence_links:
                errors.append(f"{path}: candidate {candidate_id} {to_status} event {event_id} requires evidence links")

            if to_status == "promoted_live":
                if not _has_artifact_type(related_evidence_links, "paper_shadow"):
                    errors.append(
                        f"{path}: candidate {candidate_id} promoted_live event {event_id} "
                        "requires paper_shadow evidence"
                    )
                if not _has_artifact_type(related_evidence_links, "live_approval"):
                    errors.append(
                        f"{path}: candidate {candidate_id} promoted_live event {event_id} "
                        "requires live_approval evidence"
                    )

            if to_status == "paper_running" and from_status != "paper_candidate":
                errors.append(
                    f"{path}: candidate {candidate_id} paper_running event {event_id} "
                    "requires prior paper_candidate status"
                )
            if to_status == "promoted_live" and from_status != "paper_running":
                errors.append(
                    f"{path}: candidate {candidate_id} promoted_live event {event_id} "
                    "requires prior paper_running status"
                )

            saw_rejected = saw_rejected or to_status == "rejected"
            previous_status = to_status if isinstance(to_status, str) else previous_status

        candidate_status = candidate.get("candidate_status")
        if previous_status is not None and candidate_status != previous_status:
            errors.append(
                f"{path}: candidate {candidate_id} candidate_status {candidate_status} "
                f"does not match latest ledger status {previous_status}"
            )
        if candidate_status == "promoted_live" and saw_rejected:
            errors.append(f"{path}: candidate {candidate_id} cannot be both rejected and promoted_live")

    return errors


def validate_candidate_registries(
    registry_dir: Path = DEFAULT_CANDIDATE_REGISTRY_FIXTURE_DIR,
    schema_path: Path = CANDIDATE_LIFECYCLE_REGISTRY_SCHEMA_PATH,
) -> list[str]:
    """Return validation errors for candidate lifecycle registry artifacts."""

    if not schema_path.exists():
        return [f"schema file not found: {schema_path}"]

    schema = load_json(schema_path)
    Draft7Validator.check_schema(schema)
    validator = Draft7Validator(schema)

    registry_files = _registry_files(registry_dir)
    if not registry_files:
        return []

    errors: list[str] = []
    for path in registry_files:
        payload, file_errors = _validate_json_file(path, validator)
        errors.extend(file_errors)
        if payload is None or file_errors:
            continue
        errors.extend(_validate_registry_semantics(path, payload))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry-dir", type=Path, default=DEFAULT_CANDIDATE_REGISTRY_FIXTURE_DIR)
    parser.add_argument("--schema", type=Path, default=CANDIDATE_LIFECYCLE_REGISTRY_SCHEMA_PATH)
    args = parser.parse_args()

    errors = validate_candidate_registries(
        registry_dir=args.registry_dir,
        schema_path=args.schema,
    )
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    if not args.registry_dir.exists():
        print(f"OK: {args.registry_dir} does not exist; nothing to validate")
    else:
        print(f"OK: candidate lifecycle registry artifacts under {args.registry_dir} validate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
