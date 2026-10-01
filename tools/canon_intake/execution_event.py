"""Read-only validation and derivation seams for canonical execution events."""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
from collections import Counter
from collections.abc import Iterable, Mapping
from datetime import datetime
from pathlib import Path
from typing import Any

from jsonschema import Draft7Validator, FormatChecker

from tools.canon_intake.dispatch_authorization import (
    DispatchAuthorizationError,
    repo_canonical_json_v1,
    validate_consumed_dispatch_record_for_historical_replay,
)

EXECUTION_ROOT = Path("research/queue/execution_events")
DISPATCH_ROOT = Path("research/queue/dispatch_records")
EXECUTION_SCHEMA = Path("research/schemas/canon_execution_event.schema.json")
EXECUTION_WRITER_INTEGRITY_ROOT = Path("research/canonical_crossing_audit")
EXECUTION_WRITER_INTEGRITY_SUFFIX = ".execution_writer_integrity.json"
EXECUTION_WRITER_INTEGRITY_SCHEMA_VERSION = "canon_execution_writer_integrity_visibility_v1"
EXECUTION_WRITER_VISIBILITY_MARKER_SCHEMA_VERSION = (
    "canon_execution_writer_integrity_visibility_marker_v1"
)
EXECUTION_WRITER_IDENTITY = "tools.canon_intake.execution_event_writer_v1"
EXECUTION_WRITER_COMBINED_UNCERTAINTY = "append_or_durability_and_lock_cleanup_uncertain"
EXECUTION_WRITER_MUTATION_RESERVED = "execution_event_mutation_reserved"
EXECUTION_WRITER_EVENT_DURABLE = "execution_event_durable_proven"
EXECUTION_WRITER_CLEANUP_SUCCEEDED = "append_lock_cleanup_succeeded_after_primary_uncertainty"
_EXECUTION_WRITER_MARKER_SUFFIXES = {
    EXECUTION_WRITER_MUTATION_RESERVED: ".execution_writer_visibility_reservation.json",
    EXECUTION_WRITER_EVENT_DURABLE: ".execution_writer_event_durable.json",
    EXECUTION_WRITER_CLEANUP_SUCCEEDED: ".execution_writer_cleanup_succeeded.json",
}
_EXECUTION_WRITER_INTEGRITY_NAME_RE = re.compile(
    r"^(RUN-[0-9]{8}-[A-Z0-9]{8})-([0-9]{6})" + re.escape(EXECUTION_WRITER_INTEGRITY_SUFFIX) + r"$"
)
_EXECUTION_WRITER_MARKER_NAME_RE = re.compile(
    r"^(RUN-[0-9]{8}-[A-Z0-9]{8})-([0-9]{6})("
    + "|".join(re.escape(value) for value in _EXECUTION_WRITER_MARKER_SUFFIXES.values())
    + r")$"
)
_EXECUTION_WRITER_INTEGRITY_KEYS = {
    "schema_version",
    "record_kind",
    "writer_identity",
    "dispatch_id",
    "dispatch_path",
    "run_id",
    "execution_event_stream_path",
    "event_id",
    "event_sequence_number",
    "primary_failure_phase",
    "primary_uncertainty_class",
    "event_durable",
    "stream_may_have_changed",
    "lock_cleanup_also_uncertain",
    "operator_inspection_required",
    "non_authority",
}
_EXECUTION_WRITER_MARKER_KEYS = {
    "schema_version",
    "record_kind",
    "writer_identity",
    "dispatch_id",
    "dispatch_path",
    "run_id",
    "execution_event_stream_path",
    "event_id",
    "event_sequence_number",
    "event_durable",
    "stream_file_sha256",
    "stream_byte_length",
    "lock_cleanup_succeeded_after_primary_uncertainty",
    "non_authority",
}

OUTCOME_REASONS = {
    "successful": "completed",
    "failed": "runner_failure",
    "invalid": "validation_failure",
    "excluded": "exclusion_rule",
    "errored": "execution_error",
    "aborted": "abort_condition",
    "filtered": "filter_rule",
    "data_unavailable": "data_missing",
}
OUTCOME_CATEGORIES = tuple(OUTCOME_REASONS)
ACCOUNTING_CATEGORIES = (*OUTCOME_CATEGORIES, "not_attempted")
TERMINAL_REASONS = {
    "run_completed": "completed_denominator_accounted",
    "run_failed_process_start": "runner_process_start_failed",
    "run_failed_midrun": "runner_failed_before_denominator_complete",
    "run_blocked": "fail_closed_stop_condition",
}
NON_AUTHORITY_DECLARATION = {
    "control_plane_history_only": True,
    "not_canonical_strategy_performance_evidence": True,
    "not_result_population_authority": True,
    "not_exp_replacement": True,
    "not_rep_replacement": True,
    "not_outcome_ledger_replacement": True,
    "not_recommendation_replacement": True,
    "not_decision_replacement": True,
    "not_ranking_authority": True,
    "not_recommendation_authority": True,
    "not_readiness_authority": True,
    "not_promotion_authority": True,
    "not_candidate_authority": True,
    "not_scheduler_authority": True,
    "not_runtime_authority": True,
    "not_paper_live_authority": True,
    "canonical_result_population_write_forbidden": True,
}


class ExecutionEventError(ValueError):
    """Execution-event or execution-stream validation failed closed."""


def _digest(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def _lexical_absolute(path: Path) -> Path:
    return path if path.is_absolute() else Path.cwd() / path


def _is_link_or_reparse(path: Path) -> bool:
    if path.is_symlink():
        return True
    try:
        attributes = getattr(path.lstat(), "st_file_attributes", 0)
    except OSError:
        return False
    return bool(attributes & getattr(os.stat_result, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400))


def _resolve_root(repo_root: Path) -> Path:
    root = _lexical_absolute(Path(repo_root))
    if not root.is_dir() or _is_link_or_reparse(root):
        raise ExecutionEventError("repository root must be a regular directory")
    return root.resolve()


def _repo_path(root: Path, value: str | Path, label: str) -> Path:
    selected = Path(value)
    candidate = selected if selected.is_absolute() else root / selected
    lexical = _lexical_absolute(candidate)
    try:
        relative = lexical.relative_to(root)
    except ValueError as exc:
        raise ExecutionEventError(f"{label} escapes repository root") from exc
    if ".." in relative.parts:
        raise ExecutionEventError(f"{label} contains path traversal")
    current = root
    for component in relative.parts:
        current = current / component
        if os.path.lexists(os.fspath(current)) and _is_link_or_reparse(current):
            raise ExecutionEventError(f"{label} contains a symlink or reparse component")
    return lexical


def _schema_validator(root: Path) -> Draft7Validator:
    schema_path = _repo_path(root, EXECUTION_SCHEMA, "execution-event schema")
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ExecutionEventError("execution-event schema is unreadable") from exc
    Draft7Validator.check_schema(schema)
    return Draft7Validator(schema, format_checker=FormatChecker())


def _schema_check(
    root: Path,
    event: Mapping[str, Any],
    *,
    label: str = "execution event",
) -> None:
    errors = sorted(
        _schema_validator(root).iter_errors(event),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        rendered = "; ".join(
            (".".join(str(part) for part in error.absolute_path) or "<root>") + f": {error.message}"
            for error in errors
        )
        raise ExecutionEventError(f"{label} schema validation failed: {rendered}")


def _parse_timestamp(value: str, label: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value)
    except (AttributeError, ValueError) as exc:
        raise ExecutionEventError(f"{label} must be a valid date-time") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ExecutionEventError(f"{label} must be timezone-aware")
    return parsed


def serialize_execution_event(event: Mapping[str, Any]) -> bytes:
    """Return one canonical JSON object plus exactly one LF."""
    try:
        return repo_canonical_json_v1(event) + b"\n"
    except DispatchAuthorizationError as exc:
        raise ExecutionEventError(str(exc)) from exc


def execution_writer_integrity_record_name(
    *,
    run_id: str,
    event_sequence_number: int,
) -> str:
    """Return the immutable per-event execution-writer incident filename."""
    if (
        not isinstance(run_id, str)
        or not isinstance(event_sequence_number, int)
        or isinstance(event_sequence_number, bool)
        or event_sequence_number < 1
    ):
        raise ExecutionEventError("execution-writer integrity record identity is invalid")
    name = f"{run_id}-{event_sequence_number:06d}{EXECUTION_WRITER_INTEGRITY_SUFFIX}"
    if _EXECUTION_WRITER_INTEGRITY_NAME_RE.fullmatch(name) is None:
        raise ExecutionEventError("execution-writer integrity record identity is invalid")
    return name


def execution_writer_visibility_marker_name(
    *,
    run_id: str,
    event_sequence_number: int,
    record_kind: str,
) -> str:
    """Return one immutable execution-writer visibility marker filename."""
    suffix = _EXECUTION_WRITER_MARKER_SUFFIXES.get(record_kind)
    if (
        suffix is None
        or not isinstance(run_id, str)
        or not isinstance(event_sequence_number, int)
        or isinstance(event_sequence_number, bool)
        or event_sequence_number < 1
    ):
        raise ExecutionEventError("execution-writer visibility marker identity is invalid")
    name = f"{run_id}-{event_sequence_number:06d}{suffix}"
    if _EXECUTION_WRITER_MARKER_NAME_RE.fullmatch(name) is None:
        raise ExecutionEventError("execution-writer visibility marker identity is invalid")
    return name


def _validate_execution_writer_visibility_marker(
    record: Mapping[str, Any],
    *,
    expected_run_id: str,
    expected_sequence_number: int,
    expected_record_kind: str,
) -> dict[str, Any]:
    if not isinstance(record, Mapping) or set(record) != _EXECUTION_WRITER_MARKER_KEYS:
        raise ExecutionEventError("execution-writer visibility marker fields are invalid")
    if expected_record_kind not in _EXECUTION_WRITER_MARKER_SUFFIXES:
        raise ExecutionEventError("execution-writer visibility marker kind is invalid")
    expected = {
        "schema_version": EXECUTION_WRITER_VISIBILITY_MARKER_SCHEMA_VERSION,
        "record_kind": expected_record_kind,
        "writer_identity": EXECUTION_WRITER_IDENTITY,
        "run_id": expected_run_id,
        "event_id": f"EXEC-EVENT-{expected_run_id}-{expected_sequence_number:06d}",
        "event_sequence_number": expected_sequence_number,
        "non_authority": True,
    }
    for key, value in expected.items():
        if record.get(key) != value:
            raise ExecutionEventError(f"execution-writer visibility marker {key} is invalid")
    for key in ("dispatch_id", "dispatch_path", "execution_event_stream_path"):
        if not isinstance(record.get(key), str) or not record[key]:
            raise ExecutionEventError(f"execution-writer visibility marker {key} is invalid")
    if record["dispatch_path"] != (
        f"research/queue/dispatch_records/{record['dispatch_id']}.dispatch_record.json"
    ):
        raise ExecutionEventError("execution-writer visibility marker dispatch binding is invalid")
    if record["execution_event_stream_path"] != (
        f"research/queue/execution_events/{expected_run_id}.execution_events.jsonl"
    ):
        raise ExecutionEventError("execution-writer visibility marker stream binding is invalid")
    durable = expected_record_kind == EXECUTION_WRITER_EVENT_DURABLE
    cleanup_succeeded = expected_record_kind == EXECUTION_WRITER_CLEANUP_SUCCEEDED
    if record.get("event_durable") is not durable:
        raise ExecutionEventError("execution-writer visibility marker durability state is invalid")
    if record.get("lock_cleanup_succeeded_after_primary_uncertainty") is not cleanup_succeeded:
        raise ExecutionEventError("execution-writer visibility marker cleanup state is invalid")
    if durable:
        if (
            not isinstance(record.get("stream_file_sha256"), str)
            or re.fullmatch(r"sha256:[0-9a-f]{64}", record["stream_file_sha256"]) is None
            or not isinstance(record.get("stream_byte_length"), int)
            or isinstance(record["stream_byte_length"], bool)
            or record["stream_byte_length"] < 1
        ):
            raise ExecutionEventError("execution-writer visibility marker stream proof is invalid")
    elif (
        record.get("stream_file_sha256") is not None or record.get("stream_byte_length") is not None
    ):
        raise ExecutionEventError("execution-writer visibility marker stream proof is invalid")
    return dict(record)


def serialize_execution_writer_visibility_marker(record: Mapping[str, Any]) -> bytes:
    """Return one validated canonical immutable visibility marker."""
    try:
        sequence_number = record["event_sequence_number"]
        run_id = record["run_id"]
        record_kind = record["record_kind"]
    except (KeyError, TypeError) as exc:
        raise ExecutionEventError("execution-writer visibility marker identity is missing") from exc
    if not isinstance(sequence_number, int) or isinstance(sequence_number, bool):
        raise ExecutionEventError("execution-writer visibility marker sequence is invalid")
    validated = _validate_execution_writer_visibility_marker(
        record,
        expected_run_id=run_id,
        expected_sequence_number=sequence_number,
        expected_record_kind=record_kind,
    )
    try:
        return repo_canonical_json_v1(validated) + b"\n"
    except DispatchAuthorizationError as exc:
        raise ExecutionEventError(str(exc)) from exc


def _validate_execution_writer_integrity_record(
    record: Mapping[str, Any],
    *,
    expected_run_id: str,
    expected_sequence_number: int,
) -> dict[str, Any]:
    if not isinstance(record, Mapping):
        raise ExecutionEventError("execution-writer integrity record must be one object")
    if (
        not isinstance(expected_run_id, str)
        or not isinstance(expected_sequence_number, int)
        or isinstance(expected_sequence_number, bool)
        or expected_sequence_number < 1
    ):
        raise ExecutionEventError("execution-writer integrity record identity is invalid")
    if set(record) != _EXECUTION_WRITER_INTEGRITY_KEYS:
        raise ExecutionEventError("execution-writer integrity record fields are invalid")
    expected = {
        "schema_version": EXECUTION_WRITER_INTEGRITY_SCHEMA_VERSION,
        "record_kind": EXECUTION_WRITER_COMBINED_UNCERTAINTY,
        "writer_identity": EXECUTION_WRITER_IDENTITY,
        "run_id": expected_run_id,
        "event_id": (f"EXEC-EVENT-{expected_run_id}-{expected_sequence_number:06d}"),
        "event_sequence_number": expected_sequence_number,
        "primary_failure_phase": "append_or_durability",
        "primary_uncertainty_class": "append_or_durability_uncertain",
        "event_durable": False,
        "stream_may_have_changed": True,
        "lock_cleanup_also_uncertain": True,
        "operator_inspection_required": True,
        "non_authority": True,
    }
    for key, value in expected.items():
        if record.get(key) != value:
            raise ExecutionEventError(f"execution-writer integrity record {key} is invalid")
    for key in (
        "dispatch_id",
        "dispatch_path",
        "execution_event_stream_path",
    ):
        if not isinstance(record.get(key), str) or not record[key]:
            raise ExecutionEventError(f"execution-writer integrity record {key} is invalid")
    if record["dispatch_path"] != (
        f"research/queue/dispatch_records/{record['dispatch_id']}.dispatch_record.json"
    ):
        raise ExecutionEventError("execution-writer integrity record dispatch binding is invalid")
    if record["execution_event_stream_path"] != (
        f"research/queue/execution_events/{expected_run_id}.execution_events.jsonl"
    ):
        raise ExecutionEventError("execution-writer integrity record stream binding is invalid")
    return dict(record)


def serialize_execution_writer_integrity_record(
    record: Mapping[str, Any],
) -> bytes:
    """Return one validated canonical execution-writer incident record."""
    try:
        sequence_number = record["event_sequence_number"]
        run_id = record["run_id"]
    except (KeyError, TypeError) as exc:
        raise ExecutionEventError("execution-writer integrity record identity is missing") from exc
    if not isinstance(sequence_number, int) or isinstance(sequence_number, bool):
        raise ExecutionEventError("execution-writer integrity record sequence is invalid")
    validated = _validate_execution_writer_integrity_record(
        record,
        expected_run_id=run_id,
        expected_sequence_number=sequence_number,
    )
    try:
        return repo_canonical_json_v1(validated) + b"\n"
    except DispatchAuthorizationError as exc:
        raise ExecutionEventError(str(exc)) from exc


def _expected_bindings(
    dispatch: Mapping[str, Any],
    dispatch_file_sha256: str,
) -> dict[str, Any]:
    return {
        "dispatch_id": dispatch["dispatch_id"],
        "dispatch_record_path": dispatch["dispatch_record_path"],
        "dispatch_record_sha256": dispatch_file_sha256,
        "run_id": dispatch["run_binding"]["run_id"],
        "queue_item_id": dispatch["queue_binding"]["queue_item_id"],
    }


def _expected_budget(
    dispatch: Mapping[str, Any],
    *,
    actual: int,
) -> dict[str, Any]:
    return {**dispatch["budget"], "actual": actual}


def _validate_terminal(
    dispatch: Mapping[str, Any],
    terminal: Mapping[str, Any],
) -> None:
    state = terminal["terminal_state"]
    accounting = terminal["denominator_accounting"]
    budget = terminal["budget"]
    counts = accounting["outcome_counts"]
    planned = dispatch["denominator"]["planned"]
    attempts = accounting["attempts_recorded"]
    not_attempted = accounting["not_attempted"]
    population_sum = sum(counts[name] for name in ACCOUNTING_CATEGORIES)
    attempted_sum = sum(counts[name] for name in OUTCOME_CATEGORIES)
    if terminal["terminal_reason_code"] != TERMINAL_REASONS[state]:
        raise ExecutionEventError("terminal state/reason binding mismatch")
    if accounting["basis"] != dispatch["denominator"]["basis"]:
        raise ExecutionEventError("terminal denominator basis differs from dispatch")
    if accounting["planned"] != planned:
        raise ExecutionEventError("terminal planned denominator differs from dispatch")
    if accounting["population_accounted_total"] != planned:
        raise ExecutionEventError("terminal does not account for the full denominator")
    if population_sum != planned:
        raise ExecutionEventError("terminal outcome counts do not sum to planned")
    if attempted_sum != attempts:
        raise ExecutionEventError("terminal attempted outcome counts mismatch")
    if counts["not_attempted"] != not_attempted:
        raise ExecutionEventError("terminal not-attempted fields mismatch")
    if not_attempted != planned - attempts:
        raise ExecutionEventError("terminal unattempted remainder mismatch")
    if budget != _expected_budget(dispatch, actual=attempts):
        raise ExecutionEventError("terminal budget differs from dispatch/accounting")
    if state == "run_completed" and not (
        terminal["process_started"] and attempts == planned and not_attempted == 0
    ):
        raise ExecutionEventError("run_completed accounting is invalid")
    if state == "run_failed_process_start" and not (
        terminal["process_started"] is False and attempts == 0 and not_attempted == planned
    ):
        raise ExecutionEventError("process-start failure accounting is invalid")
    if state == "run_failed_midrun" and not (
        terminal["process_started"] and attempts < planned and not_attempted > 0
    ):
        raise ExecutionEventError("midrun failure accounting is invalid")
    if state == "run_blocked" and (
        (not terminal["process_started"] and attempts != 0) or attempts > planned
    ):
        raise ExecutionEventError("blocked-run process/accounting truth is invalid")


def validate_execution_event(
    *,
    repo_root: Path,
    dispatch: Mapping[str, Any],
    dispatch_file_sha256: str,
    event: Mapping[str, Any],
) -> dict[str, Any]:
    """Validate one event against exact immutable dispatch bindings."""
    root = _resolve_root(repo_root)
    if not isinstance(event, Mapping):
        raise ExecutionEventError("execution event must be one object")
    _schema_check(root, event)
    sequence = event["sequence_number"]
    run_id = dispatch["run_binding"]["run_id"]
    expected_event_id = f"EXEC-EVENT-{run_id}-{sequence:06d}"
    expected_stream = dispatch["run_binding"]["execution_event_stream_path"]
    if event["event_id"] != expected_event_id:
        raise ExecutionEventError("event ID/run/sequence binding mismatch")
    if event["bindings"] != _expected_bindings(dispatch, dispatch_file_sha256):
        raise ExecutionEventError("event bindings differ from exact dispatch")
    if event["stream_path"] != expected_stream:
        raise ExecutionEventError("event stream path differs from exact dispatch")
    _parse_timestamp(event["timestamp_utc"], "event timestamp")
    event_type = event["event_type"]
    if event_type == "run_start":
        start = event["run_start"]
        if sequence != 1:
            raise ExecutionEventError("run_start must have sequence 1")
        if start["planned_denominator"] != dispatch["denominator"]["planned"]:
            raise ExecutionEventError("run_start denominator differs from dispatch")
        if start["budget"] != _expected_budget(dispatch, actual=0):
            raise ExecutionEventError("run_start budget differs from dispatch")
        if start["seed"] != dispatch["execution_parameters"]["seed"]:
            raise ExecutionEventError("run_start seed differs from dispatch")
        if start["workers"] != dispatch["execution_parameters"]["workers"]:
            raise ExecutionEventError("run_start workers differ from dispatch")
        if start["automatic_retry"] != dispatch["execution_parameters"]["automatic_retry"]:
            raise ExecutionEventError("run_start retry posture differs from dispatch")
    elif event_type == "attempt_outcome":
        attempt = event["attempt_outcome"]
        if attempt["reason_code"] != OUTCOME_REASONS[attempt["outcome_category"]]:
            raise ExecutionEventError("attempt outcome/reason binding mismatch")
    else:
        _validate_terminal(dispatch, event["run_terminal"])
    canonical_raw = serialize_execution_event(event)
    return {
        "valid": True,
        "event": dict(event),
        "event_id": event["event_id"],
        "event_type": event_type,
        "sequence_number": sequence,
        "canonical_raw": canonical_raw,
        "canonical_sha256": _digest(canonical_raw),
        "non_authority": True,
    }


def derive_execution_event(
    *,
    repo_root: Path,
    dispatch: Mapping[str, Any],
    dispatch_file_sha256: str,
    event_type: str,
    sequence_number: int,
    timestamp_utc: str,
    actor: Mapping[str, Any],
    payload: Mapping[str, Any],
) -> dict[str, Any]:
    """Derive immutable bindings and validate one event-specific payload."""
    if event_type not in {"run_start", "attempt_outcome", "run_terminal"}:
        raise ExecutionEventError("event_type is outside the closed vocabulary")
    if not isinstance(payload, Mapping):
        raise ExecutionEventError("event payload must be one object")
    run_id = dispatch["run_binding"]["run_id"]
    event = {
        "schema_version": "canon_execution_event_v1",
        "event_id": f"EXEC-EVENT-{run_id}-{sequence_number:06d}",
        "event_type": event_type,
        "sequence_number": sequence_number,
        "timestamp_utc": timestamp_utc,
        "actor": dict(actor),
        "bindings": _expected_bindings(dispatch, dispatch_file_sha256),
        "stream_path": dispatch["run_binding"]["execution_event_stream_path"],
        event_type: dict(payload),
        "non_authority_declaration": dict(NON_AUTHORITY_DECLARATION),
    }
    validate_execution_event(
        repo_root=repo_root,
        dispatch=dispatch,
        dispatch_file_sha256=dispatch_file_sha256,
        event=event,
    )
    return event


def _decode_stream(
    *,
    root: Path,
    dispatch: Mapping[str, Any],
    dispatch_file_sha256: str,
    raw: bytes,
    label: str,
) -> list[dict[str, Any]]:
    if not raw:
        raise ExecutionEventError(f"{label} is empty")
    if not raw.endswith(b"\n"):
        raise ExecutionEventError(f"{label} has a partial tail")
    events: list[dict[str, Any]] = []
    for number, line in enumerate(raw.splitlines(), 1):
        try:
            event = json.loads(line.decode("utf-8"))
        except (UnicodeError, json.JSONDecodeError) as exc:
            raise ExecutionEventError(f"{label} is malformed at line {number}") from exc
        if not isinstance(event, dict):
            raise ExecutionEventError(f"{label} line {number} is not one JSON object")
        validation = validate_execution_event(
            repo_root=root,
            dispatch=dispatch,
            dispatch_file_sha256=dispatch_file_sha256,
            event=event,
        )
        if line + b"\n" != validation["canonical_raw"]:
            raise ExecutionEventError(f"{label} line {number} is not canonical JSON plus one LF")
        events.append(event)
    return events


def _validate_stream_semantics(
    dispatch: Mapping[str, Any],
    events: list[dict[str, Any]],
) -> str:
    if events[0]["event_type"] != "run_start":
        raise ExecutionEventError("run_start must be the unique first event")
    if any(event["event_type"] == "run_start" for event in events[1:]):
        raise ExecutionEventError("duplicate run_start event")
    sequences = [event["sequence_number"] for event in events]
    if sequences != list(range(1, len(events) + 1)):
        raise ExecutionEventError("execution-event sequence is not contiguous")
    event_ids = [event["event_id"] for event in events]
    if len(event_ids) != len(set(event_ids)):
        raise ExecutionEventError("execution-event ID collision")
    first_actor = events[0]["actor"]
    if any(event["actor"] != first_actor for event in events[1:]):
        raise ExecutionEventError("actor/tool identity changed within stream")
    terminals = [
        index for index, event in enumerate(events) if event["event_type"] == "run_terminal"
    ]
    if len(terminals) > 1:
        raise ExecutionEventError("execution stream contains multiple terminals")
    if terminals and terminals[0] != len(events) - 1:
        raise ExecutionEventError("execution event appears after terminal")
    attempts = [
        event["attempt_outcome"] for event in events if event["event_type"] == "attempt_outcome"
    ]
    if attempts and not events[0]["run_start"]["runner_process_started"]:
        raise ExecutionEventError("attempt exists although process did not start")
    if [attempt["attempt_number"] for attempt in attempts] != list(range(1, len(attempts) + 1)):
        raise ExecutionEventError("attempt numbers are not contiguous")
    variant_ids = [attempt["variant_id"] for attempt in attempts]
    if len(variant_ids) != len(set(variant_ids)):
        raise ExecutionEventError("variant ID recurs in execution stream")
    if len(attempts) > dispatch["denominator"]["planned"]:
        raise ExecutionEventError("attempt count exceeds planned denominator")
    if not terminals:
        return "in_progress"
    terminal = events[-1]["run_terminal"]
    if terminal["process_started"] != events[0]["run_start"]["runner_process_started"]:
        raise ExecutionEventError("start/terminal process-start truth mismatch")
    accounting = terminal["denominator_accounting"]
    if accounting["attempts_recorded"] != len(attempts):
        raise ExecutionEventError("terminal attempt count differs from stream")
    observed = Counter(attempt["outcome_category"] for attempt in attempts)
    for category in OUTCOME_CATEGORIES:
        if accounting["outcome_counts"][category] != observed[category]:
            raise ExecutionEventError(f"terminal {category} count differs from attempt history")
    return "terminal"


def _git(root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=root,
            capture_output=True,
            check=False,
        )
    except OSError as exc:
        raise ExecutionEventError("retained Git history is unavailable") from exc
    if check and result.returncode != 0:
        raise ExecutionEventError(
            "retained Git history command failed: "
            + " ".join(args)
            + ": "
            + result.stderr.decode("utf-8", errors="replace").strip()
        )
    return result


def _retained_stream_versions(root: Path) -> Iterable[tuple[str, bytes]]:
    if (
        _git(root, "rev-parse", "--is-inside-work-tree", check=False).stdout.decode().strip()
        != "true"
    ):
        raise ExecutionEventError("retained Git history is unavailable; validation fails closed")
    tracked_root = EXECUTION_ROOT.as_posix()
    commits = [
        value
        for value in _git(root, "log", "--all", "--format=%H", "--", tracked_root)
        .stdout.decode()
        .splitlines()
        if value
    ]
    seen: set[tuple[str, str]] = set()
    for commit in commits:
        paths = (
            _git(root, "ls-tree", "-r", "--name-only", commit, "--", tracked_root)
            .stdout.decode()
            .splitlines()
        )
        for path in paths:
            blob = _git(root, "rev-parse", f"{commit}:{path}").stdout.decode().strip()
            key = (path, blob)
            if key in seen:
                continue
            seen.add(key)
            raw = _git(root, "show", f"{commit}:{path}").stdout
            yield path, raw


def _identity_values(raw: bytes, label: str) -> list[dict[str, Any]]:
    if not raw or not raw.endswith(b"\n"):
        raise ExecutionEventError(f"{label} is empty or has a partial tail")
    values = []
    for number, line in enumerate(raw.splitlines(), 1):
        try:
            event = json.loads(line.decode("utf-8"))
        except (UnicodeError, json.JSONDecodeError) as exc:
            raise ExecutionEventError(f"{label} is malformed at line {number}") from exc
        if not isinstance(event, dict):
            raise ExecutionEventError(f"{label} line {number} is not one object")
        bindings = event.get("bindings", {})
        values.append(
            {
                "run_id": bindings.get("run_id"),
                "stream_path": event.get("stream_path"),
                "event_id": event.get("event_id"),
            }
        )
    return values


def validate_execution_stream_history(
    *,
    repo_root: Path,
    run_id: str,
    stream_path: str,
    current_raw: bytes | None,
) -> dict[str, Any]:
    """Prove current and retained stream versions form one append-only history."""
    root = _resolve_root(repo_root)
    documents: list[tuple[str, bytes, str]] = []
    current_root = _repo_path(root, EXECUTION_ROOT, "execution-event root")
    if current_root.exists():
        if not current_root.is_dir():
            raise ExecutionEventError("execution-event root is not a directory")
        for path in sorted(current_root.iterdir(), key=lambda value: value.name):
            if (
                _is_link_or_reparse(path)
                or not path.is_file()
                or not path.name.endswith(".execution_events.jsonl")
            ):
                raise ExecutionEventError(f"unexpected execution-event corpus entry: {path.name}")
            relative = path.relative_to(root).as_posix()
            documents.append((relative, path.read_bytes(), "current"))
    documents.extend(
        (path, raw, "retained_history") for path, raw in _retained_stream_versions(root)
    )
    target_versions: list[bytes] = []
    seen_documents: set[tuple[str, str]] = set()
    for path, raw, source_kind in documents:
        key = (path, _digest(raw))
        if key in seen_documents:
            continue
        seen_documents.add(key)
        identities = _identity_values(raw, f"{source_kind}:{path}")
        if path == stream_path:
            target_versions.append(raw)
            continue
        for identity in identities:
            if (
                identity["run_id"] == run_id
                or identity["stream_path"] == stream_path
                or (
                    isinstance(identity["event_id"], str)
                    and identity["event_id"].startswith(f"EXEC-EVENT-{run_id}-")
                )
            ):
                raise ExecutionEventError(f"execution identity collision in {source_kind}:{path}")
    if current_raw is None and target_versions:
        raise ExecutionEventError("retained history contains a deleted execution stream")
    if current_raw is not None:
        target_versions.append(current_raw)
        for version in target_versions:
            if not current_raw.startswith(version):
                raise ExecutionEventError(
                    "execution stream conflicts with retained append-only history"
                )
    return {
        "valid": True,
        "run_id": run_id,
        "stream_path": stream_path,
        "current_exists": current_raw is not None,
        "retained_version_count": len({_digest(raw) for raw in target_versions}),
        "non_authority": True,
    }


def _validated_dispatch(
    *,
    root: Path,
    dispatch_path: Path,
    reviewed_dispatch_whole_file_sha256: str,
) -> tuple[dict[str, Any], bytes, dict[str, Any]]:
    selected = _repo_path(root, dispatch_path, "dispatch record")
    if _is_link_or_reparse(selected) or not selected.is_file():
        raise ExecutionEventError("dispatch record must be a regular non-symlink file")
    raw = selected.read_bytes()
    if not isinstance(reviewed_dispatch_whole_file_sha256, str):
        raise ExecutionEventError("reviewed dispatch whole-file SHA-256 must be supplied")
    if _digest(raw) != reviewed_dispatch_whole_file_sha256:
        raise ExecutionEventError("dispatch bytes differ from reviewed SHA-256")
    try:
        validation = validate_consumed_dispatch_record_for_historical_replay(
            repo_root=root,
            dispatch_path=selected,
        )
    except DispatchAuthorizationError as exc:
        raise ExecutionEventError(str(exc)) from exc
    if validation["lifecycle_state"] != "consumed":
        raise ExecutionEventError("dispatch KDAUTH lifecycle is not exactly consumed")
    try:
        dispatch = json.loads(raw.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ExecutionEventError("dispatch record is unreadable") from exc
    return dispatch, raw, validation


def read_and_validate_execution_stream(
    *,
    repo_root: Path,
    dispatch_path: Path,
    reviewed_dispatch_whole_file_sha256: str,
    allow_missing: bool = False,
    require_terminal: bool = False,
    scan_retained_history: bool = True,
) -> dict[str, Any]:
    """Read and validate one authoritative stream against an exact dispatch."""
    root = _resolve_root(repo_root)
    dispatch, dispatch_raw, dispatch_validation = _validated_dispatch(
        root=root,
        dispatch_path=dispatch_path,
        reviewed_dispatch_whole_file_sha256=(reviewed_dispatch_whole_file_sha256),
    )
    stream_relative = dispatch["run_binding"]["execution_event_stream_path"]
    stream_path = _repo_path(root, stream_relative, "execution stream")
    if os.path.lexists(os.fspath(stream_path)):
        if _is_link_or_reparse(stream_path) or not stream_path.is_file():
            raise ExecutionEventError("execution stream must be a regular non-symlink file")
        raw: bytes | None = stream_path.read_bytes()
    else:
        raw = None
    if scan_retained_history:
        history = validate_execution_stream_history(
            repo_root=root,
            run_id=dispatch["run_binding"]["run_id"],
            stream_path=stream_relative,
            current_raw=raw,
        )
    else:
        history = None
    if raw is None:
        if not allow_missing:
            raise ExecutionEventError("authoritative execution stream is missing")
        if require_terminal:
            raise ExecutionEventError("terminal execution stream is required")
        return {
            "valid": True,
            "state": "missing",
            "events": [],
            "raw": None,
            "dispatch": dispatch,
            "dispatch_validation": dispatch_validation,
            "dispatch_file_sha256": _digest(dispatch_raw),
            "stream_path": stream_relative,
            "history_validation": history,
            "non_authority": True,
        }
    events = _decode_stream(
        root=root,
        dispatch=dispatch,
        dispatch_file_sha256=_digest(dispatch_raw),
        raw=raw,
        label="execution stream",
    )
    state = _validate_stream_semantics(dispatch, events)
    if require_terminal and state != "terminal":
        raise ExecutionEventError("execution stream is incomplete")
    return {
        "valid": True,
        "state": state,
        "events": events,
        "raw": raw,
        "stream_file_sha256": _digest(raw),
        "stream_byte_length": len(raw),
        "dispatch": dispatch,
        "dispatch_validation": dispatch_validation,
        "dispatch_file_sha256": _digest(dispatch_raw),
        "stream_path": stream_relative,
        "history_validation": history,
        "non_authority": True,
    }


def _finding(
    *,
    finding_type: str,
    dispatch_id: str | None,
    dispatch_path: str | None,
    run_id: str | None,
    stream_path: str | None,
    state: str,
    reason: str,
) -> dict[str, Any]:
    return {
        "finding_type": finding_type,
        "dispatch_id": dispatch_id,
        "dispatch_path": dispatch_path,
        "run_id": run_id,
        "execution_event_stream_path": stream_path,
        "stream_state": state,
        "reason": reason,
        "operator_inspection_required": True,
        "non_authority": True,
    }


def _execution_writer_uncertainty_findings(
    *,
    dispatch_id: str | None,
    dispatch_path: str | None,
    run_id: str,
    stream_path: str,
    record_path: str,
    malformed_reason: str | None = None,
) -> list[dict[str, Any]]:
    record_status = (
        f"durable incident record {record_path}"
        if malformed_reason is None
        else (f"matching durable incident record {record_path} is malformed: {malformed_reason}")
    )
    return [
        _finding(
            finding_type="execution_writer_append_or_durability_uncertain",
            dispatch_id=dispatch_id,
            dispatch_path=dispatch_path,
            run_id=run_id,
            stream_path=stream_path,
            state="integrity_critical",
            reason=(
                "primary append_or_durability uncertainty is preserved; "
                "event_durable=false and stream_may_have_changed=true; " + record_status
            ),
        ),
        _finding(
            finding_type="execution_writer_lock_cleanup_also_uncertain",
            dispatch_id=dispatch_id,
            dispatch_path=dispatch_path,
            run_id=run_id,
            stream_path=stream_path,
            state="integrity_critical",
            reason=(
                "lock cleanup is also uncertain and does not replace the "
                "primary append_or_durability uncertainty; " + record_status
            ),
        ),
    ]


def _execution_writer_reserved_uncertainty_findings(
    *,
    reservation: Mapping[str, Any] | None,
    run_id: str,
    sequence_number: int,
    reservation_path: str | None,
    durable_status: str,
    cleanup_status: str,
    cleanup_succeeded: bool,
) -> list[dict[str, Any]]:
    stream_path = f"research/queue/execution_events/{run_id}.execution_events.jsonl"
    dispatch_id = reservation.get("dispatch_id") if reservation is not None else None
    dispatch_path = reservation.get("dispatch_path") if reservation is not None else None
    if reservation is not None:
        stream_path = reservation["execution_event_stream_path"]
    marker = reservation_path or (
        f"execution-writer visibility marker identity {run_id}-{sequence_number:06d}"
    )
    findings = [
        _finding(
            finding_type="execution_writer_append_or_durability_uncertain",
            dispatch_id=dispatch_id,
            dispatch_path=dispatch_path,
            run_id=run_id,
            stream_path=stream_path,
            state="integrity_critical",
            reason=(
                f"immutable pre-mutation reservation {marker} is unresolved; "
                f"{durable_status}; primary append_or_durability uncertainty "
                "remains conservatively visible"
            ),
        )
    ]
    if not cleanup_succeeded:
        findings.append(
            _finding(
                finding_type="execution_writer_lock_cleanup_also_uncertain",
                dispatch_id=dispatch_id,
                dispatch_path=dispatch_path,
                run_id=run_id,
                stream_path=stream_path,
                state="integrity_critical",
                reason=(
                    "lock cleanup success is not durably proven and additive cleanup "
                    f"uncertainty cannot be excluded; {cleanup_status}; {marker} is "
                    "retained without repair"
                ),
            )
        )
    return findings


def _visibility_marker_bindings_match(
    left: Mapping[str, Any],
    right: Mapping[str, Any],
) -> bool:
    return all(
        left[key] == right[key]
        for key in (
            "writer_identity",
            "dispatch_id",
            "dispatch_path",
            "run_id",
            "execution_event_stream_path",
            "event_id",
            "event_sequence_number",
        )
    )


def _collect_execution_writer_integrity_findings(
    *,
    root: Path,
) -> list[dict[str, Any]]:
    audit_root = _repo_path(
        root,
        EXECUTION_WRITER_INTEGRITY_ROOT,
        "execution-writer integrity root",
    )
    if not audit_root.exists():
        return []
    if not audit_root.is_dir():
        raise ExecutionEventError("execution-writer integrity root is not a directory")
    findings: list[dict[str, Any]] = []
    final_incidents: set[tuple[str, int]] = set()
    for path in sorted(
        audit_root.glob(f"*{EXECUTION_WRITER_INTEGRITY_SUFFIX}"),
        key=lambda value: value.name,
    ):
        match = _EXECUTION_WRITER_INTEGRITY_NAME_RE.fullmatch(path.name)
        if match is None:
            continue
        run_id = match.group(1)
        sequence_number = int(match.group(2))
        final_incidents.add((run_id, sequence_number))
        record_path = path.relative_to(root).as_posix()
        stream_path = f"research/queue/execution_events/{run_id}.execution_events.jsonl"
        try:
            if _is_link_or_reparse(path) or not path.is_file():
                raise ExecutionEventError("record is not a regular non-symlink file")
            raw = path.read_bytes()
            record = json.loads(raw.decode("utf-8"))
            validated = _validate_execution_writer_integrity_record(
                record,
                expected_run_id=run_id,
                expected_sequence_number=sequence_number,
            )
            if serialize_execution_writer_integrity_record(validated) != raw:
                raise ExecutionEventError("record is not canonical")
        except (
            OSError,
            UnicodeError,
            json.JSONDecodeError,
            ExecutionEventError,
        ) as exc:
            findings.extend(
                _execution_writer_uncertainty_findings(
                    dispatch_id=None,
                    dispatch_path=None,
                    run_id=run_id,
                    stream_path=stream_path,
                    record_path=record_path,
                    malformed_reason=str(exc),
                )
            )
            continue
        findings.extend(
            _execution_writer_uncertainty_findings(
                dispatch_id=validated["dispatch_id"],
                dispatch_path=validated["dispatch_path"],
                run_id=validated["run_id"],
                stream_path=validated["execution_event_stream_path"],
                record_path=record_path,
            )
        )

    marker_records: dict[
        tuple[str, int],
        dict[str, tuple[dict[str, Any] | None, str | None, str]],
    ] = {}
    suffix_to_kind = {suffix: kind for kind, suffix in _EXECUTION_WRITER_MARKER_SUFFIXES.items()}
    for path in sorted(
        (
            candidate
            for suffix in _EXECUTION_WRITER_MARKER_SUFFIXES.values()
            for candidate in audit_root.glob(f"*{suffix}")
        ),
        key=lambda value: value.name,
    ):
        match = _EXECUTION_WRITER_MARKER_NAME_RE.fullmatch(path.name)
        if match is None:
            continue
        run_id = match.group(1)
        sequence_number = int(match.group(2))
        record_kind = suffix_to_kind[match.group(3)]
        record_path = path.relative_to(root).as_posix()
        validated: dict[str, Any] | None = None
        malformed_reason: str | None = None
        try:
            if _is_link_or_reparse(path) or not path.is_file():
                raise ExecutionEventError("marker is not a regular non-symlink file")
            raw = path.read_bytes()
            record = json.loads(raw.decode("utf-8"))
            validated = _validate_execution_writer_visibility_marker(
                record,
                expected_run_id=run_id,
                expected_sequence_number=sequence_number,
                expected_record_kind=record_kind,
            )
            if serialize_execution_writer_visibility_marker(validated) != raw:
                raise ExecutionEventError("marker is not canonical")
        except (
            OSError,
            UnicodeError,
            json.JSONDecodeError,
            ExecutionEventError,
        ) as exc:
            validated = None
            malformed_reason = str(exc)
        marker_records.setdefault((run_id, sequence_number), {})[record_kind] = (
            validated,
            malformed_reason,
            record_path,
        )

    for (run_id, sequence_number), records in sorted(marker_records.items()):
        if (run_id, sequence_number) in final_incidents:
            continue
        reservation_item = records.get(EXECUTION_WRITER_MUTATION_RESERVED)
        durable_item = records.get(EXECUTION_WRITER_EVENT_DURABLE)
        cleanup_item = records.get(EXECUTION_WRITER_CLEANUP_SUCCEEDED)
        reservation = reservation_item[0] if reservation_item is not None else None
        reservation_path = reservation_item[2] if reservation_item is not None else None
        reservation_malformed = reservation_item is None or reservation_item[1] is not None
        durable = durable_item[0] if durable_item is not None else None
        durable_matches = (
            not reservation_malformed
            and durable is not None
            and _visibility_marker_bindings_match(reservation, durable)
        )
        if durable_matches:
            continue
        cleanup = cleanup_item[0] if cleanup_item is not None else None
        cleanup_matches = (
            not reservation_malformed
            and cleanup is not None
            and _visibility_marker_bindings_match(reservation, cleanup)
        )
        if reservation_item is None:
            reservation_status = "pre-mutation reservation is absent"
        elif reservation_item[1] is not None:
            reservation_status = f"pre-mutation reservation is malformed: {reservation_item[1]}"
        else:
            reservation_status = "pre-mutation reservation is canonical"
        if durable_item is None:
            durable_status = "event-durable proof is absent"
        elif durable_item[1] is not None:
            durable_status = f"event-durable proof is malformed: {durable_item[1]}"
        else:
            durable_status = "event-durable proof does not match the reservation"
        if cleanup_item is None:
            cleanup_status = "cleanup-success proof is absent"
        elif cleanup_item[1] is not None:
            cleanup_status = f"cleanup-success proof is malformed: {cleanup_item[1]}"
        else:
            cleanup_status = "cleanup-success proof does not match the reservation"
        findings.extend(
            _execution_writer_reserved_uncertainty_findings(
                reservation=reservation,
                run_id=run_id,
                sequence_number=sequence_number,
                reservation_path=reservation_path,
                durable_status=f"{reservation_status}; {durable_status}",
                cleanup_status=cleanup_status,
                cleanup_succeeded=cleanup_matches,
            )
        )
    return findings


def _sorted_unique_findings(
    findings: Iterable[dict[str, Any]],
) -> list[dict[str, Any]]:
    unique = {
        (
            row["finding_type"],
            row["dispatch_id"],
            row["run_id"],
            row["execution_event_stream_path"],
            row["reason"],
        ): row
        for row in findings
    }
    return [
        unique[key]
        for key in sorted(
            unique,
            key=lambda value: tuple("" if part is None else part for part in value),
        )
    ]


def collect_execution_stream_integrity_findings(
    *,
    repo_root: Path,
) -> list[dict[str, Any]]:
    """Report stream failures and durable execution-writer uncertainty."""
    root = _resolve_root(repo_root)
    writer_findings = _collect_execution_writer_integrity_findings(root=root)
    findings: list[dict[str, Any]] = list(writer_findings)
    writer_finding_types = {row["finding_type"] for row in writer_findings}
    combined_writer_uncertainty_visible = {
        "execution_writer_append_or_durability_uncertain",
        "execution_writer_lock_cleanup_also_uncertain",
    } <= writer_finding_types
    bound_streams: set[str] = set()
    try:
        dispatch_root = _repo_path(root, DISPATCH_ROOT, "dispatch-record root")
    except ExecutionEventError:
        if combined_writer_uncertainty_visible:
            return _sorted_unique_findings(findings)
        raise
    if dispatch_root.exists():
        if not dispatch_root.is_dir():
            raise ExecutionEventError("dispatch-record root is not a directory")
        for path in sorted(
            dispatch_root.glob("*.dispatch_record.json"),
            key=lambda value: value.name,
        ):
            raw = path.read_bytes()
            try:
                dispatch = json.loads(raw.decode("utf-8"))
            except (UnicodeError, json.JSONDecodeError):
                continue
            if not isinstance(dispatch, dict):
                continue
            try:
                dispatch_validation = validate_consumed_dispatch_record_for_historical_replay(
                    repo_root=root,
                    dispatch_path=path,
                )
            except DispatchAuthorizationError:
                continue
            if dispatch_validation["lifecycle_state"] != "consumed":
                continue
            dispatch_id = dispatch.get("dispatch_id")
            run_id = dispatch.get("run_binding", {}).get("run_id")
            stream = dispatch.get("run_binding", {}).get("execution_event_stream_path")
            if isinstance(stream, str):
                bound_streams.add(stream)
            try:
                result = read_and_validate_execution_stream(
                    repo_root=root,
                    dispatch_path=path,
                    reviewed_dispatch_whole_file_sha256=_digest(raw),
                    allow_missing=True,
                    require_terminal=False,
                    scan_retained_history=True,
                )
            except ExecutionEventError as exc:
                findings.append(
                    _finding(
                        finding_type="execution_stream_malformed",
                        dispatch_id=dispatch_id,
                        dispatch_path=dispatch.get("dispatch_record_path"),
                        run_id=run_id,
                        stream_path=stream,
                        state="invalid",
                        reason=str(exc),
                    )
                )
                continue
            if result["state"] == "missing":
                findings.append(
                    _finding(
                        finding_type="execution_stream_missing",
                        dispatch_id=dispatch_id,
                        dispatch_path=dispatch["dispatch_record_path"],
                        run_id=run_id,
                        stream_path=stream,
                        state="missing",
                        reason="valid consumed dispatch has no execution stream",
                    )
                )
            elif result["state"] == "in_progress":
                findings.append(
                    _finding(
                        finding_type="execution_stream_incomplete",
                        dispatch_id=dispatch_id,
                        dispatch_path=dispatch["dispatch_record_path"],
                        run_id=run_id,
                        stream_path=stream,
                        state="in_progress",
                        reason="valid execution stream has no terminal event",
                    )
                )
    try:
        execution_root = _repo_path(root, EXECUTION_ROOT, "execution-event root")
    except ExecutionEventError:
        if combined_writer_uncertainty_visible:
            return _sorted_unique_findings(findings)
        raise
    if execution_root.exists():
        if not execution_root.is_dir():
            raise ExecutionEventError("execution-event root is not a directory")
        for path in sorted(
            execution_root.glob("*.execution_events.jsonl"),
            key=lambda value: value.name,
        ):
            relative = path.relative_to(root).as_posix()
            if relative not in bound_streams:
                findings.append(
                    _finding(
                        finding_type="execution_stream_unbound",
                        dispatch_id=None,
                        dispatch_path=None,
                        run_id=None,
                        stream_path=relative,
                        state="unbound",
                        reason=("execution stream has no current dispatch binding"),
                    )
                )
    current_paths = (
        {
            path.relative_to(root).as_posix()
            for path in execution_root.glob("*.execution_events.jsonl")
        }
        if execution_root.exists()
        else set()
    )
    retained_paths = {path for path, _ in _retained_stream_versions(root)}
    for path in sorted(retained_paths - current_paths):
        findings.append(
            _finding(
                finding_type="execution_stream_deleted_retained_history",
                dispatch_id=None,
                dispatch_path=None,
                run_id=None,
                stream_path=path,
                state="deleted",
                reason="retained execution stream is absent from current tree",
            )
        )
    return _sorted_unique_findings(findings)
