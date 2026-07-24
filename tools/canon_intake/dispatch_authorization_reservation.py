"""Protected pre-mutation KDAUTH crossing-reservation ledger.

The ledger is append-only control-plane integrity history.  It does not create
or approve a KDAUTH, mutate the KDAUTH lifecycle audit, create a dispatch or
execution event, or invoke a runner.
"""

from __future__ import annotations

import errno
import hashlib
import json
import os
import stat
import subprocess
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping

from jsonschema import Draft7Validator, FormatChecker

from tools.canon_intake.queue_admission import (
    QueueAdmissionError,
    repo_canonical_json_v1 as _repo_canonical_json_v1,
)


SCHEMA_NAME = (
    "canon_dispatch_authorization_crossing_reservation_event.schema.json"
)
SCHEMA_VERSION = (
    "canon_dispatch_authorization_crossing_reservation_event_v1"
)
WRITER_IDENTITY = "dispatch_authorization_reservation_v1"
RESERVATION_ROOT = Path(
    "research/queue/dispatch_authorization_reservations"
)
AUTHORIZATION_ROOT = Path("research/queue/dispatch_authorizations")
AUDIT_PATH = Path(
    "research/queue/dispatch_authorization_audit/"
    "dispatch_authorization_events.jsonl"
)
CROSSING_LOCK_PATH = Path(
    "research/queue/dispatch_authorization_audit/"
    ".dispatch_authorization.lock"
)

TERMINAL_EVENT_TYPES = {
    "crossing_committed",
    "crossing_rolled_back_clean",
    "crossing_integrity_critical",
}
COMMON_BINDING_FIELDS = (
    "schema_version",
    "attempt_id",
    "reservation_stream_path",
    "authorization_binding",
    "dispatch_binding",
    "run_binding",
    "queue_binding",
    "reviewed_content_binding",
    "reserved_at",
    "actor",
    "writer_identity",
    "identities_permanently_reserved",
    "automatic_retry_with_same_identities_forbidden",
    "non_authority_declaration",
)
FINDING_REASON_CODES = {
    "crossing_integrity_critical": "recorded_integrity_critical",
    "attempt_reserved_without_terminal": "terminal_missing",
    "authorization_created_without_prior_crossing_reservation":
        "prior_reservation_missing_or_late",
    "crossing_committed_without_exact_authorization_created":
        "exact_creation_binding_missing",
    "reservation_terminal_binding_mismatch":
        "terminal_common_binding_mismatch",
    "reservation_duplicate_or_invalid_sequence":
        "invalid_sequence_or_stream",
    "reservation_identity_collision_across_attempts":
        "protected_identity_collision_across_distinct_attempts",
}
BINARY_FLAG = getattr(os, "O_BINARY", 0)


class DispatchAuthorizationReservationError(ValueError):
    """Reservation validation or a proven pre-publication action failed."""


class DispatchAuthorizationReservationIntegrityCriticalError(
    DispatchAuthorizationReservationError
):
    """A published or appended authoritative stream may require inspection."""


def _digest(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def repo_canonical_json_v1(value: Any) -> bytes:
    try:
        return _repo_canonical_json_v1(value)
    except QueueAdmissionError as exc:
        raise DispatchAuthorizationReservationError(str(exc)) from exc


def _lexical_absolute(path: Path) -> Path:
    return path if path.is_absolute() else Path.cwd() / path


def _lexical_entry_exists(path: Path) -> bool:
    return os.path.lexists(os.fspath(path))


def _is_reparse_point(path: Path) -> bool:
    try:
        metadata = os.lstat(path)
    except (FileNotFoundError, NotADirectoryError):
        return False
    except OSError as exc:
        raise DispatchAuthorizationReservationError(
            f"path entry metadata is unreadable: {path}"
        ) from exc
    attributes = getattr(metadata, "st_file_attributes", 0)
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    return bool(attributes & reparse_flag)


def _is_link_or_reparse(path: Path) -> bool:
    return path.is_symlink() or _is_reparse_point(path)


def _reject_symlink_components(path: Path, label: str) -> Path:
    lexical = _lexical_absolute(path)
    for component in reversed([lexical, *lexical.parents]):
        if _is_link_or_reparse(component):
            raise DispatchAuthorizationReservationError(
                f"{label} contains a symlink or reparse-point component: "
                f"{component}"
            )
    return lexical


def _resolve_root(repo_root: Path) -> Path:
    lexical = _reject_symlink_components(repo_root, "repo root")
    if not lexical.is_dir():
        raise DispatchAuthorizationReservationError(
            "repo root must be an existing directory"
        )
    return lexical.resolve()


def _repo_path(root: Path, value: str, label: str) -> Path:
    if not isinstance(value, str) or not value or "\\" in value:
        raise DispatchAuthorizationReservationError(
            f"{label} must be a repo-relative POSIX path"
        )
    raw_parts = value.split("/")
    pure = PurePosixPath(value)
    if (
        pure.is_absolute()
        or (raw_parts and len(raw_parts[0]) >= 2 and raw_parts[0][1] == ":")
        or any(part in {"", ".", ".."} for part in raw_parts)
    ):
        raise DispatchAuthorizationReservationError(
            f"{label} must not contain traversal, dot, or empty components"
        )
    lexical = root.joinpath(*pure.parts)
    _reject_symlink_components(lexical, label)
    resolved = lexical.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise DispatchAuthorizationReservationError(
            f"{label} escapes the repository"
        ) from exc
    return lexical


def _schema_validator(root: Path) -> Draft7Validator:
    schema_path = root / "research/schemas" / SCHEMA_NAME
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise DispatchAuthorizationReservationError(
            f"protected schema is unreadable: {SCHEMA_NAME}"
        ) from exc
    Draft7Validator.check_schema(schema)
    return Draft7Validator(schema, format_checker=FormatChecker())


def _schema_check(root: Path, event: Mapping[str, Any]) -> None:
    errors = sorted(
        _schema_validator(root).iter_errors(event),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        location = ".".join(
            str(part) for part in errors[0].absolute_path
        )
        suffix = f" at {location}" if location else ""
        raise DispatchAuthorizationReservationError(
            f"reservation event schema validation failed{suffix}: "
            f"{errors[0].message}"
        )


def _parse_timestamp(value: Any, label: str) -> datetime:
    if not isinstance(value, str):
        raise DispatchAuthorizationReservationError(
            f"{label} must be a timezone-aware RFC3339 timestamp"
        )
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise DispatchAuthorizationReservationError(
            f"{label} must be a timezone-aware RFC3339 timestamp"
        ) from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise DispatchAuthorizationReservationError(
            f"{label} must be timezone-aware"
        )
    return parsed


def _expected_reservation_path(attempt_id: str) -> str:
    return (
        RESERVATION_ROOT
        / f"{attempt_id}.crossing_reservation.jsonl"
    ).as_posix()


def _validate_event(root: Path, event: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(event, Mapping):
        raise DispatchAuthorizationReservationError(
            "reservation event must be a mapping"
        )
    materialized = dict(event)
    _schema_check(root, materialized)
    attempt_id = materialized["attempt_id"]
    sequence = materialized["sequence_number"]
    expected_event_id = f"{attempt_id}-{sequence:06d}"
    if materialized["event_id"] != expected_event_id:
        raise DispatchAuthorizationReservationError(
            "reservation event ID/sequence mismatch"
        )
    expected_path = _expected_reservation_path(attempt_id)
    if materialized["reservation_stream_path"] != expected_path:
        raise DispatchAuthorizationReservationError(
            "reservation stream path is not derived from the attempt ID"
        )
    reserved_at = _parse_timestamp(
        materialized["reserved_at"], "reserved_at"
    )
    occurred_at = _parse_timestamp(
        materialized["occurred_at"], "occurred_at"
    )
    attempt_date = attempt_id.split("-")[2]
    if reserved_at.astimezone(timezone.utc).strftime("%Y%m%d") != attempt_date:
        raise DispatchAuthorizationReservationError(
            "attempt ID date does not equal the UTC reserved_at date"
        )
    if occurred_at < reserved_at:
        raise DispatchAuthorizationReservationError(
            "occurred_at must not precede reserved_at"
        )
    if materialized["writer_identity"] != WRITER_IDENTITY:
        raise DispatchAuthorizationReservationError(
            "writer_identity does not equal the protected writer version"
        )
    authorization = materialized["authorization_binding"]
    authorization_id = authorization["authorization_id"]
    expected_authorization_path = (
        AUTHORIZATION_ROOT
        / f"{authorization_id}.dispatch_authorization.json"
    ).as_posix()
    if authorization["authorization_target_path"] != expected_authorization_path:
        raise DispatchAuthorizationReservationError(
            "authorization target path is not derived from authorization ID"
        )
    dispatch = materialized["dispatch_binding"]
    expected_dispatch_path = (
        Path("research/queue/dispatch_records")
        / f"{dispatch['dispatch_id']}.dispatch_record.json"
    ).as_posix()
    if dispatch["dispatch_record_path"] != expected_dispatch_path:
        raise DispatchAuthorizationReservationError(
            "dispatch record path is not derived from dispatch ID"
        )
    run = materialized["run_binding"]
    expected_execution_path = (
        Path("research/queue/execution_events")
        / f"{run['run_id']}.execution_events.jsonl"
    ).as_posix()
    if run["execution_event_stream_path"] != expected_execution_path:
        raise DispatchAuthorizationReservationError(
            "execution stream path is not derived from run ID"
        )
    if materialized["queue_binding"]["authorization_id"] != authorization_id:
        raise DispatchAuthorizationReservationError(
            "queue/authorization pair does not match authorization binding"
        )
    event_type = materialized["event_type"]
    if event_type == "attempt_reserved" and sequence != 1:
        raise DispatchAuthorizationReservationError(
            "attempt_reserved must use sequence 1"
        )
    if event_type in TERMINAL_EVENT_TYPES and sequence != 2:
        raise DispatchAuthorizationReservationError(
            "terminal event must use sequence 2"
        )
    if event_type in TERMINAL_EVENT_TYPES:
        if materialized["event_payload"]["terminal_outcome"] != event_type:
            raise DispatchAuthorizationReservationError(
                "terminal event type/payload mismatch"
            )
    return materialized


def _read_stream_bytes(path: Path, label: str) -> bytes:
    lexical = _reject_symlink_components(path, label)
    if lexical.is_symlink() or not lexical.is_file():
        raise DispatchAuthorizationReservationError(
            f"{label} must be a regular non-symlink file"
        )
    try:
        return lexical.read_bytes()
    except OSError as exc:
        raise DispatchAuthorizationReservationError(
            f"{label} is unreadable"
        ) from exc


def _parse_stream(
    root: Path,
    raw: bytes,
    expected_path: str,
) -> list[dict[str, Any]]:
    if raw.startswith(b"\xef\xbb\xbf"):
        raise DispatchAuthorizationReservationError(
            "reservation stream must not contain a UTF-8 BOM"
        )
    if b"\r" in raw:
        raise DispatchAuthorizationReservationError(
            "reservation stream must use LF, not CR or CRLF"
        )
    if not raw or not raw.endswith(b"\n"):
        raise DispatchAuthorizationReservationError(
            "reservation stream is empty or has a partial tail"
        )
    raw_lines = raw.splitlines(keepends=True)
    if len(raw_lines) not in {1, 2}:
        raise DispatchAuthorizationReservationError(
            "reservation stream must contain exactly one or two lines"
        )
    events: list[dict[str, Any]] = []
    for number, raw_line in enumerate(raw_lines, 1):
        if raw_line == b"\n":
            raise DispatchAuthorizationReservationError(
                "reservation stream contains a blank line"
            )
        try:
            event = json.loads(raw_line[:-1].decode("utf-8"))
        except (UnicodeError, json.JSONDecodeError) as exc:
            raise DispatchAuthorizationReservationError(
                f"reservation line {number} is invalid UTF-8 JSON"
            ) from exc
        if not isinstance(event, dict):
            raise DispatchAuthorizationReservationError(
                f"reservation line {number} is not an object"
            )
        if raw_line != repo_canonical_json_v1(event) + b"\n":
            raise DispatchAuthorizationReservationError(
                f"reservation line {number} is not canonical JSON plus one LF"
            )
        event = _validate_event(root, event)
        if event["reservation_stream_path"] != expected_path:
            raise DispatchAuthorizationReservationError(
                "reservation event path differs from authoritative file path"
            )
        events.append(event)
    first = events[0]
    if first["event_type"] != "attempt_reserved":
        raise DispatchAuthorizationReservationError(
            "reservation stream must begin with attempt_reserved"
        )
    if len(events) == 2:
        terminal = events[1]
        if terminal["event_type"] not in TERMINAL_EVENT_TYPES:
            raise DispatchAuthorizationReservationError(
                "reservation sequence 2 must be a terminal"
            )
        for field in COMMON_BINDING_FIELDS:
            if terminal[field] != first[field]:
                raise DispatchAuthorizationReservationError(
                    f"terminal common binding mismatch: {field}"
                )
        if _parse_timestamp(
            terminal["occurred_at"], "terminal.occurred_at"
        ) < _parse_timestamp(first["occurred_at"], "initial.occurred_at"):
            raise DispatchAuthorizationReservationError(
                "terminal occurred_at must not precede initial occurred_at"
            )
    return events


def _read_audit_lines(root: Path) -> list[tuple[dict[str, Any], bytes]]:
    audit_path = _repo_path(root, AUDIT_PATH.as_posix(), "lifecycle audit")
    if not audit_path.exists():
        return []
    raw = _read_stream_bytes(audit_path, "lifecycle audit")
    if raw and not raw.endswith(b"\n"):
        raise DispatchAuthorizationReservationError(
            "lifecycle audit has a partial tail"
        )
    rows: list[tuple[dict[str, Any], bytes]] = []
    for number, raw_line in enumerate(raw.splitlines(keepends=True), 1):
        try:
            event = json.loads(raw_line[:-1].decode("utf-8"))
        except (UnicodeError, json.JSONDecodeError) as exc:
            raise DispatchAuthorizationReservationError(
                f"lifecycle audit line {number} is malformed"
            ) from exc
        if not isinstance(event, dict):
            raise DispatchAuthorizationReservationError(
                f"lifecycle audit line {number} is not an object"
            )
        if raw_line != repo_canonical_json_v1(event) + b"\n":
            raise DispatchAuthorizationReservationError(
                f"lifecycle audit line {number} is not canonical"
            )
        rows.append((event, raw_line))
    return rows


def _validate_committed_cross_surface(
    root: Path,
    initial: Mapping[str, Any],
    terminal: Mapping[str, Any],
) -> None:
    from tools.canon_intake.dispatch_authorization import (
        DispatchAuthorizationError,
        authorization_core_sha256,
        validate_dispatch_authorization,
    )

    authorization_binding = initial["authorization_binding"]
    reviewed = initial["reviewed_content_binding"]
    authorization_path = _repo_path(
        root,
        authorization_binding["authorization_target_path"],
        "reserved KDAUTH target",
    )
    try:
        validation = validate_dispatch_authorization(
            repo_root=root,
            authorization_path=authorization_path,
            require_audit=True,
            scan_history=False,
        )
    except DispatchAuthorizationError as exc:
        raise DispatchAuthorizationReservationError(
            f"committed KDAUTH does not validate: {exc}"
        ) from exc
    raw = _read_stream_bytes(authorization_path, "committed KDAUTH")
    try:
        authorization = json.loads(raw.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise DispatchAuthorizationReservationError(
            "committed KDAUTH is malformed"
        ) from exc
    if authorization.get("approved_by") != initial["actor"]:
        raise DispatchAuthorizationReservationError(
            "reservation actor does not equal KDAUTH approved_by"
        )
    expected_values = {
        "authorization_id": authorization_binding["authorization_id"],
        "authorization_path": authorization_binding[
            "authorization_target_path"
        ],
        "whole_file_sha256": reviewed["reviewed_whole_file_sha256"],
        "byte_length": reviewed["reviewed_byte_length"],
        "authorization_core_sha256": authorization_binding[
            "authorization_core_sha256"
        ],
    }
    for field, expected in expected_values.items():
        if validation[field] != expected:
            raise DispatchAuthorizationReservationError(
                f"committed KDAUTH reservation mismatch: {field}"
            )
    if authorization_core_sha256(
        authorization["authorization_core"]
    ) != authorization_binding["authorization_core_sha256"]:
        raise DispatchAuthorizationReservationError(
            "committed KDAUTH core hash mismatch"
        )
    payload = terminal["event_payload"]
    terminal_values = {
        "resulting_authorization_path":
            authorization_binding["authorization_target_path"],
        "resulting_authorization_whole_file_sha256": _digest(raw),
        "resulting_authorization_byte_length": len(raw),
        "resulting_authorization_core_sha256":
            authorization_binding["authorization_core_sha256"],
        "lifecycle_audit_path": AUDIT_PATH.as_posix(),
    }
    for field, expected in terminal_values.items():
        if payload[field] != expected:
            raise DispatchAuthorizationReservationError(
                f"committed terminal result mismatch: {field}"
            )
    creation_rows = [
        (event, raw_line)
        for event, raw_line in _read_audit_lines(root)
        if event.get("event_type") == "authorization_created"
        and event.get("authorization_id")
        == authorization_binding["authorization_id"]
    ]
    if len(creation_rows) != 1:
        raise DispatchAuthorizationReservationError(
            "exactly one matching authorization_created event is required"
        )
    creation, raw_line = creation_rows[0]
    expected_creation = {
        "authorization_path": authorization_binding[
            "authorization_target_path"
        ],
        "authorization_file_sha256": reviewed[
            "reviewed_whole_file_sha256"
        ],
        "authorization_byte_length": reviewed["reviewed_byte_length"],
        "authorization_core_sha256": authorization_binding[
            "authorization_core_sha256"
        ],
        "queue_item_id": initial["queue_binding"]["queue_item_id"],
        "dispatch_id": initial["dispatch_binding"]["dispatch_id"],
        "run_id": initial["run_binding"]["run_id"],
    }
    for field, expected in expected_creation.items():
        if creation.get(field) != expected:
            raise DispatchAuthorizationReservationError(
                f"authorization_created reservation mismatch: {field}"
            )
    creation_occurred_at = _parse_timestamp(
        creation.get("occurred_at"), "authorization_created.occurred_at"
    )
    initial_occurred_at = _parse_timestamp(
        initial["occurred_at"], "reservation.occurred_at"
    )
    terminal_occurred_at = _parse_timestamp(
        terminal["occurred_at"], "committed terminal.occurred_at"
    )
    if creation_occurred_at <= initial_occurred_at:
        raise DispatchAuthorizationReservationError(
            "authorization_created does not follow the committed reservation"
        )
    if terminal_occurred_at < creation_occurred_at:
        raise DispatchAuthorizationReservationError(
            "committed terminal occurred_at precedes authorization_created"
        )
    exact_terminal_links = {
        "authorization_created_event_id": creation.get("event_id"),
        "lifecycle_event_sequence_number": creation.get("sequence_number"),
        "lifecycle_raw_line_sha256": _digest(raw_line),
        "lifecycle_raw_line_byte_length": len(raw_line),
    }
    for field, expected in exact_terminal_links.items():
        if payload[field] != expected:
            raise DispatchAuthorizationReservationError(
                f"committed terminal lifecycle link mismatch: {field}"
            )


def _validate_clean_rollback_cross_surface(
    root: Path,
    initial: Mapping[str, Any],
    terminal: Mapping[str, Any],
) -> None:
    target = _repo_path(
        root,
        initial["authorization_binding"]["authorization_target_path"],
        "reserved KDAUTH target",
    )
    authorization_root = _repo_path(
        root, AUTHORIZATION_ROOT.as_posix(), "KDAUTH authority root"
    )
    if target.parent != authorization_root:
        raise DispatchAuthorizationReservationError(
            "reserved KDAUTH target parent is not the authority root"
        )
    _reject_symlink_components(
        target.parent, "reserved KDAUTH target parent"
    )
    if _lexical_entry_exists(target):
        raise DispatchAuthorizationReservationError(
            "clean rollback retains a lexical entry at the reserved KDAUTH "
            "target"
        )
    authorization_id = initial["authorization_binding"]["authorization_id"]
    if any(
        event.get("event_type") == "authorization_created"
        and event.get("authorization_id") == authorization_id
        for event, _ in _read_audit_lines(root)
    ):
        raise DispatchAuthorizationReservationError(
            "clean rollback retains authorization_created"
        )
    payload = terminal["event_payload"]
    prior_length = payload["prior_lifecycle_audit_byte_length"]
    final_length = payload["final_lifecycle_audit_byte_length"]
    if prior_length != final_length:
        raise DispatchAuthorizationReservationError(
            "clean rollback prior/final audit lengths differ"
        )
    audit = _repo_path(root, AUDIT_PATH.as_posix(), "lifecycle audit")
    actual_length = audit.stat().st_size if audit.exists() else 0
    if actual_length != final_length:
        raise DispatchAuthorizationReservationError(
            "clean rollback final audit length is not the actual length"
        )


def _cross_surface_findings(
    root: Path, events: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    if len(events) == 1:
        return [
            _finding(
                events[0],
                "attempt_reserved_without_terminal",
                terminal_outcome=None,
            )
        ]
    initial, terminal = events
    if terminal["event_type"] == "crossing_integrity_critical":
        return [
            _finding(
                initial,
                "crossing_integrity_critical",
                terminal_outcome=terminal["event_type"],
            )
        ]
    try:
        if terminal["event_type"] == "crossing_committed":
            _validate_committed_cross_surface(root, initial, terminal)
        else:
            _validate_clean_rollback_cross_surface(root, initial, terminal)
    except DispatchAuthorizationReservationError:
        finding_type = (
            "crossing_committed_without_exact_authorization_created"
            if terminal["event_type"] == "crossing_committed"
            else "reservation_terminal_binding_mismatch"
        )
        return [
            _finding(
                initial,
                finding_type,
                terminal_outcome=terminal["event_type"],
            )
        ]
    return []


def _finding(
    event: Mapping[str, Any] | None,
    finding_type: str,
    *,
    terminal_outcome: str | None,
) -> dict[str, Any]:
    authorization = (
        event.get("authorization_binding", {}) if event else {}
    )
    dispatch = event.get("dispatch_binding", {}) if event else {}
    run = event.get("run_binding", {}) if event else {}
    queue = event.get("queue_binding", {}) if event else {}
    return {
        "finding_type": finding_type,
        "attempt_id": event.get("attempt_id") if event else None,
        "reservation_stream_path": (
            event.get("reservation_stream_path") if event else None
        ),
        "authorization_id": authorization.get("authorization_id"),
        "authorization_target_path":
            authorization.get("authorization_target_path"),
        "dispatch_id": dispatch.get("dispatch_id"),
        "dispatch_record_path": dispatch.get("dispatch_record_path"),
        "run_id": run.get("run_id"),
        "execution_event_stream_path":
            run.get("execution_event_stream_path"),
        "queue_item_id": queue.get("queue_item_id"),
        "terminal_outcome": terminal_outcome,
        "reason_code": FINDING_REASON_CODES[finding_type],
        "operator_inspection_required": True,
        "non_authority": True,
    }


def validate_dispatch_authorization_reservation_stream(
    *,
    repo_root: Path,
    reservation_path: Path,
    require_terminal: bool = False,
) -> dict[str, Any]:
    """Validate one authoritative stream and return read-only facts/findings."""
    root = _resolve_root(repo_root)
    path = _reject_symlink_components(
        reservation_path, "reservation stream"
    )
    try:
        relative_path = path.resolve().relative_to(root).as_posix()
    except ValueError as exc:
        raise DispatchAuthorizationReservationError(
            "reservation stream escapes the repository"
        ) from exc
    if not relative_path.startswith(RESERVATION_ROOT.as_posix() + "/"):
        raise DispatchAuthorizationReservationError(
            "reservation stream is outside the authoritative root"
        )
    raw = _read_stream_bytes(path, "reservation stream")
    events = _parse_stream(root, raw, relative_path)
    if require_terminal and len(events) != 2:
        raise DispatchAuthorizationReservationError(
            "completed reservation stream requires one terminal"
        )
    findings = _cross_surface_findings(root, events)
    terminal = events[1] if len(events) == 2 else None
    return {
        "valid": True,
        "attempt_id": events[0]["attempt_id"],
        "reservation_stream_path": relative_path,
        "event_count": len(events),
        "terminal_outcome": (
            terminal["event_type"] if terminal is not None else None
        ),
        "identities_permanently_reserved": True,
        "automatic_retry_with_same_identities_forbidden": True,
        "raw_sha256": _digest(raw),
        "byte_length": len(raw),
        "events": events,
        "findings": findings,
        "non_authority": True,
    }


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
        raise DispatchAuthorizationReservationError(
            "retained Git history is unavailable"
        ) from exc
    if check and result.returncode != 0:
        raise DispatchAuthorizationReservationError(
            f"git history command failed: {' '.join(args)}: "
            f"{result.stderr.strip()}"
        )
    return result.stdout


def _history_streams(root: Path) -> Iterable[tuple[str, bytes, str]]:
    if (
        _git(
            root, "rev-parse", "--is-inside-work-tree", check=False
        ).strip()
        != "true"
    ):
        raise DispatchAuthorizationReservationError(
            "retained Git history is unavailable; reservation scan fails closed"
        )
    tracked_root = RESERVATION_ROOT.as_posix()
    commits = [
        line
        for line in _git(
            root, "log", "--all", "--format=%H", "--", tracked_root
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
            tracked_root,
        ).splitlines()
        for path in paths:
            if not path.endswith(".crossing_reservation.jsonl"):
                raise DispatchAuthorizationReservationError(
                    f"unexpected retained reservation entry: {path}"
                )
            blob_id = _git(root, "rev-parse", f"{commit}:{path}").strip()
            key = (path, blob_id)
            if key in seen:
                continue
            seen.add(key)
            try:
                result = subprocess.run(
                    ["git", "show", f"{commit}:{path}"],
                    cwd=root,
                    capture_output=True,
                    check=True,
                )
            except (OSError, subprocess.CalledProcessError) as exc:
                raise DispatchAuthorizationReservationError(
                    f"retained reservation is unreadable: {commit}:{path}"
                ) from exc
            yield path, result.stdout, commit


def _current_streams(root: Path) -> Iterable[tuple[str, bytes, str | None]]:
    directory = _repo_path(
        root, RESERVATION_ROOT.as_posix(), "reservation root"
    )
    if not directory.exists():
        return
    if directory.is_symlink() or not directory.is_dir():
        raise DispatchAuthorizationReservationError(
            "reservation root is not a regular directory"
        )
    for path in sorted(directory.iterdir(), key=lambda item: item.name):
        if (
            path.is_symlink()
            or not path.is_file()
            or not path.name.endswith(".crossing_reservation.jsonl")
        ):
            raise DispatchAuthorizationReservationError(
                f"unexpected reservation root entry: {path.name}"
            )
        yield (
            path.relative_to(root).as_posix(),
            _read_stream_bytes(path, path.name),
            None,
        )


def _validate_raw_stream(
    root: Path,
    path: str,
    raw: bytes,
    *,
    validate_cross_surfaces: bool,
) -> dict[str, Any]:
    events = _parse_stream(root, raw, path)
    findings = (
        _cross_surface_findings(root, events)
        if validate_cross_surfaces
        else []
    )
    terminal = events[1] if len(events) == 2 else None
    return {
        "valid": True,
        "attempt_id": events[0]["attempt_id"],
        "reservation_stream_path": path,
        "event_count": len(events),
        "terminal_outcome": terminal["event_type"] if terminal else None,
        "events": events,
        "findings": findings,
        "raw_sha256": _digest(raw),
        "byte_length": len(raw),
        "identities_permanently_reserved": True,
        "automatic_retry_with_same_identities_forbidden": True,
        "non_authority": True,
    }


def _identity_values(event: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "attempt_id": event["attempt_id"],
        "reservation_stream_path": event["reservation_stream_path"],
        "authorization_id":
            event["authorization_binding"]["authorization_id"],
        "authorization_target_path":
            event["authorization_binding"]["authorization_target_path"],
        "dispatch_id": event["dispatch_binding"]["dispatch_id"],
        "dispatch_record_path":
            event["dispatch_binding"]["dispatch_record_path"],
        "run_id": event["run_binding"]["run_id"],
        "execution_event_stream_path":
            event["run_binding"]["execution_event_stream_path"],
        "queue_authorization_pair": (
            event["queue_binding"]["queue_item_id"],
            event["queue_binding"]["authorization_id"],
        ),
        "reviewed_identity_tuple": (
            event["authorization_binding"]["authorization_id"],
            event["dispatch_binding"]["dispatch_id"],
            event["run_binding"]["run_id"],
            event["reviewed_content_binding"][
                "reviewed_whole_file_sha256"
            ],
        ),
        "core_identity_tuple": (
            event["authorization_binding"]["authorization_id"],
            event["dispatch_binding"]["dispatch_id"],
            event["run_binding"]["run_id"],
            event["authorization_binding"]["authorization_core_sha256"],
        ),
    }


PROTECTED_IDENTITY_FIELDS = (
    "authorization_id",
    "authorization_target_path",
    "dispatch_id",
    "dispatch_record_path",
    "run_id",
    "execution_event_stream_path",
    "queue_authorization_pair",
    "reviewed_identity_tuple",
    "core_identity_tuple",
)


def _logical_attempt_model(
    *,
    root: Path,
    include_retained_history: bool,
    validate_cross_surfaces: bool,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    current = list(_current_streams(root))
    historical = (
        list(_history_streams(root)) if include_retained_history else []
    )
    grouped: dict[
        tuple[str, str],
        dict[bytes, list[tuple[str, str | None]]],
    ] = {}
    attempt_paths: dict[str, set[str]] = {}
    path_attempts: dict[str, set[str]] = {}
    for path, raw, commit in [*current, *historical]:
        source_kind = "current" if commit is None else "retained_history"
        try:
            parsed = _validate_raw_stream(
                root,
                path,
                raw,
                validate_cross_surfaces=False,
            )
        except DispatchAuthorizationReservationError as exc:
            source = path if commit is None else f"{commit}:{path}"
            raise DispatchAuthorizationReservationError(
                f"reservation history contains an invalid stream at {source}: "
                f"{exc}"
            ) from exc
        attempt_id = parsed["attempt_id"]
        stream_path = parsed["reservation_stream_path"]
        key = (attempt_id, stream_path)
        grouped.setdefault(key, {}).setdefault(raw, []).append(
            (source_kind, commit)
        )
        attempt_paths.setdefault(attempt_id, set()).add(stream_path)
        path_attempts.setdefault(stream_path, set()).add(attempt_id)

    for attempt_id, paths in attempt_paths.items():
        if len(paths) != 1:
            raise DispatchAuthorizationReservationError(
                f"logical reservation attempt has multiple paths: {attempt_id}"
            )
    for path, attempt_ids in path_attempts.items():
        if len(attempt_ids) != 1:
            raise DispatchAuthorizationReservationError(
                f"reservation path has multiple attempt IDs: {path}"
            )

    logical_attempts: list[dict[str, Any]] = []
    for (attempt_id, path), version_sources in sorted(grouped.items()):
        ordered = sorted(version_sources, key=lambda value: (len(value), value))
        for index, previous in enumerate(ordered):
            for later in ordered[index + 1:]:
                if not later.startswith(previous):
                    raise DispatchAuthorizationReservationError(
                        "reservation history contains non-prefix or ambiguous "
                        f"competing versions for {attempt_id} at {path}"
                    )
        longest_length = max(len(raw) for raw in ordered)
        longest = [raw for raw in ordered if len(raw) == longest_length]
        if len(longest) != 1:
            raise DispatchAuthorizationReservationError(
                "reservation history contains ambiguous competing longest "
                f"versions for {attempt_id} at {path}"
            )
        selected_raw = longest[0]
        result = _validate_raw_stream(
            root,
            path,
            selected_raw,
            validate_cross_surfaces=validate_cross_surfaces,
        )
        selected_sources = version_sources[selected_raw]
        result["source_kind"] = (
            "current"
            if any(kind == "current" for kind, _ in selected_sources)
            else "retained_history"
        )
        commits = sorted(
            {
                commit
                for sources in version_sources.values()
                for _, commit in sources
                if commit is not None
            }
        )
        result["source_commit"] = commits[-1] if commits else None
        result["source_commits"] = commits
        result["history_version_count"] = len(version_sources)
        logical_attempts.append(result)

    collisions: list[dict[str, Any]] = []
    for left_index, left in enumerate(logical_attempts):
        left_event = left["events"][0]
        left_key = (
            left_event["attempt_id"],
            left_event["reservation_stream_path"],
        )
        left_values = _identity_values(left_event)
        for right in logical_attempts[left_index + 1:]:
            right_event = right["events"][0]
            right_key = (
                right_event["attempt_id"],
                right_event["reservation_stream_path"],
            )
            if left_key == right_key:
                continue
            right_values = _identity_values(right_event)
            collision_fields = [
                field
                for field in PROTECTED_IDENTITY_FIELDS
                if left_values[field] == right_values[field]
            ]
            if collision_fields:
                collisions.append(
                    {
                        "left": left,
                        "right": right,
                        "fields": collision_fields,
                    }
                )
    return logical_attempts, collisions


def scan_dispatch_authorization_reservations(
    *,
    repo_root: Path,
    include_retained_history: bool = True,
) -> list[dict[str, Any]]:
    """Return one fail-closed logical state per current/retained attempt."""
    root = _resolve_root(repo_root)
    logical_attempts, collisions = _logical_attempt_model(
        root=root,
        include_retained_history=include_retained_history,
        validate_cross_surfaces=True,
    )
    if collisions:
        collision = collisions[0]
        left = collision["left"]["events"][0]
        right = collision["right"]["events"][0]
        raise DispatchAuthorizationReservationError(
            "distinct reservation attempts collide on protected identities: "
            f"{left['attempt_id']} at {left['reservation_stream_path']} and "
            f"{right['attempt_id']} at {right['reservation_stream_path']}: "
            + ", ".join(collision["fields"])
        )
    return logical_attempts


def _reject_reserved_identity_reuse(
    root: Path, candidate: Mapping[str, Any]
) -> None:
    expected = _identity_values(candidate)
    for result in scan_dispatch_authorization_reservations(
        repo_root=root, include_retained_history=True
    ):
        historical = _identity_values(result["events"][0])
        collisions = [
            name
            for name, value in expected.items()
            if historical.get(name) == value
        ]
        if collisions:
            raise DispatchAuthorizationReservationError(
                "reservation identities are permanently consumed: "
                + ", ".join(collisions)
            )


def _reject_control_surface_identity_reuse(
    root: Path, candidate: Mapping[str, Any]
) -> None:
    """Reject identities already present in KDAUTH/dispatch/run history."""
    from tools.canon_intake.dispatch_authorization import (
        DispatchAuthorizationError,
        _consumption_bindings,
        _history_documents,
        _iter_current_control_documents,
    )

    expected = {
        "authorization_id": candidate["authorization_binding"][
            "authorization_id"
        ],
        "authorization_path": candidate["authorization_binding"][
            "authorization_target_path"
        ],
        "authorization_file_sha256": candidate[
            "reviewed_content_binding"
        ]["reviewed_whole_file_sha256"],
        "queue_item_id": candidate["queue_binding"]["queue_item_id"],
        "dispatch_id": candidate["dispatch_binding"]["dispatch_id"],
        "run_id": candidate["run_binding"]["run_id"],
        "dispatch_path": candidate["dispatch_binding"][
            "dispatch_record_path"
        ],
        "stream_path": candidate["run_binding"][
            "execution_event_stream_path"
        ],
    }
    try:
        sources: list[tuple[str, bytes]] = list(
            _iter_current_control_documents(root)
        )
        sources.extend(_history_documents(root))
    except DispatchAuthorizationError as exc:
        raise DispatchAuthorizationReservationError(
            f"control-plane history is invalid: {exc}"
        ) from exc
    seen: set[tuple[str, str]] = set()
    for path, raw in sources:
        key = (path, _digest(raw))
        if key in seen:
            continue
        seen.add(key)
        bindings: list[dict[str, Any]]
        if path.endswith(".dispatch_authorization.json"):
            try:
                authorization = json.loads(raw.decode("utf-8"))
            except (UnicodeError, json.JSONDecodeError) as exc:
                raise DispatchAuthorizationReservationError(
                    f"KDAUTH history is malformed: {path}"
                ) from exc
            if not isinstance(authorization, dict):
                raise DispatchAuthorizationReservationError(
                    f"KDAUTH history is not an object: {path}"
                )
            core = authorization.get("authorization_core", {})
            crossing = (
                core.get("crossing_identities", {})
                if isinstance(core, dict)
                else {}
            )
            queue = (
                core.get("queue_binding", {})
                if isinstance(core, dict)
                else {}
            )
            bindings = [
                {
                    "source": path,
                    "authorization_id": authorization.get(
                        "authorization_id"
                    ),
                    "authorization_path": authorization.get(
                        "authorization_artifact_target_path"
                    ),
                    "authorization_file_sha256": _digest(raw),
                    "queue_item_id": queue.get("queue_item_id"),
                    "dispatch_id": crossing.get("dispatch_id"),
                    "run_id": crossing.get("run_id"),
                    "dispatch_path": crossing.get(
                        "dispatch_record_path"
                    ),
                    "stream_path": crossing.get(
                        "execution_event_stream_path"
                    ),
                }
            ]
        else:
            try:
                bindings = _consumption_bindings(path, raw)
            except DispatchAuthorizationError as exc:
                raise DispatchAuthorizationReservationError(
                    f"control-plane history is malformed: {exc}"
                ) from exc
        for binding in bindings:
            collisions = [
                field
                for field, value in expected.items()
                if value is not None and binding.get(field) == value
            ]
            if collisions:
                raise DispatchAuthorizationReservationError(
                    "control-plane history already consumes reservation "
                    f"identities in {binding['source']}: "
                    + ", ".join(collisions)
                )


def _fsync_directory(path: Path) -> str:
    if os.name == "nt":
        return "not_supported_on_platform"
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    fd = os.open(path, flags)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)
    return "verified"


@dataclass
class CrossingLock:
    """One repository-wide KDAUTH crossing lock held across all phases."""

    repo_root: Path
    path: Path
    fd: int | None = None
    acquired: bool = False

    def __enter__(self) -> "CrossingLock":
        if self.acquired:
            raise DispatchAuthorizationReservationError(
                "crossing lock is already acquired"
            )
        self.path.parent.mkdir(parents=True, exist_ok=True)
        _reject_symlink_components(self.path, "crossing lock")
        try:
            self.fd = os.open(
                self.path,
                os.O_CREAT | os.O_EXCL | os.O_WRONLY | BINARY_FLAG,
                0o600,
            )
            lock_bytes = repo_canonical_json_v1(
                {
                    "lock_kind": "kdauth_crossing",
                    "pid": os.getpid(),
                    "writer_identity": WRITER_IDENTITY,
                }
            ) + b"\n"
            _write_all(self.fd, lock_bytes)
            os.fsync(self.fd)
            self.acquired = True
            return self
        except FileExistsError as exc:
            raise DispatchAuthorizationReservationError(
                "KDAUTH crossing lock already exists; stale locks fail closed"
            ) from exc
        except Exception:
            if self.fd is not None:
                os.close(self.fd)
                self.fd = None
            if self.path.exists():
                try:
                    self.path.unlink()
                except OSError:
                    pass
            raise

    def __exit__(self, exc_type, exc, traceback) -> bool:
        cleanup_error: Exception | None = None
        try:
            if self.fd is not None:
                os.close(self.fd)
                self.fd = None
            if self.path.exists():
                self.path.unlink()
                _fsync_directory(self.path.parent)
        except Exception as caught:
            cleanup_error = caught
        finally:
            self.acquired = False
        if cleanup_error is not None:
            raise DispatchAuthorizationReservationIntegrityCriticalError(
                "crossing lock cleanup failed; operator inspection required"
            ) from cleanup_error
        return False


def dispatch_authorization_crossing_lock(
    *, repo_root: Path
) -> CrossingLock:
    root = _resolve_root(repo_root)
    lock_path = _repo_path(
        root, CROSSING_LOCK_PATH.as_posix(), "crossing lock"
    )
    return CrossingLock(repo_root=root, path=lock_path)


def _require_lock(lock: CrossingLock) -> Path:
    if not isinstance(lock, CrossingLock) or not lock.acquired:
        raise DispatchAuthorizationReservationError(
            "the shared KDAUTH crossing lock must be held"
        )
    expected_path = _repo_path(
        lock.repo_root,
        CROSSING_LOCK_PATH.as_posix(),
        "crossing lock",
    )
    if lock.path != expected_path or not lock.path.is_file():
        raise DispatchAuthorizationReservationError(
            "the held lock is not the repository-wide KDAUTH crossing lock"
        )
    return lock.repo_root


def _write_all(fd: int, raw: bytes) -> None:
    written = 0
    while written < len(raw):
        count = os.write(fd, raw[written:])
        if count <= 0:
            raise OSError("write returned no progress")
        written += count


def _cleanup_temp(path: Path) -> None:
    if not path.exists():
        return
    try:
        path.unlink()
    except OSError as exc:
        raise DispatchAuthorizationReservationError(
            "non-authoritative pre-publication temporary cleanup failed"
        ) from exc


def reserve_dispatch_authorization_crossing_locked(
    *,
    lock: CrossingLock,
    event: Mapping[str, Any],
) -> dict[str, Any]:
    """Durably publish one complete initial reservation under the held lock."""
    root = _require_lock(lock)
    initial = _validate_event(root, event)
    if initial["event_type"] != "attempt_reserved":
        raise DispatchAuthorizationReservationError(
            "initial reservation API requires attempt_reserved"
        )
    candidate = repo_canonical_json_v1(initial) + b"\n"
    expected_path = initial["reservation_stream_path"]
    target = _repo_path(root, expected_path, "reservation target")
    reservation_root = _repo_path(
        root, RESERVATION_ROOT.as_posix(), "reservation root"
    )
    reservation_root.mkdir(parents=True, exist_ok=True)
    _reject_symlink_components(reservation_root, "reservation root")
    if target.parent != reservation_root:
        raise DispatchAuthorizationReservationError(
            "reservation target parent is not the authority root"
        )
    if _lexical_entry_exists(target):
        raise DispatchAuthorizationReservationError(
            "reservation target is permanently single-use"
        )
    _reject_reserved_identity_reuse(root, initial)
    _reject_control_surface_identity_reuse(root, initial)
    temp = reservation_root / (
        f".{initial['attempt_id']}.{uuid.uuid4().hex}.tmp"
    )
    fd: int | None = None
    published = False
    directory_fsync_status = "not_attempted"
    try:
        fd = os.open(
            temp,
            os.O_CREAT | os.O_EXCL | os.O_WRONLY | BINARY_FLAG,
            0o600,
        )
        _write_all(fd, candidate)
        os.fsync(fd)
        os.close(fd)
        fd = None
        if _read_stream_bytes(temp, "reservation temporary") != candidate:
            raise DispatchAuthorizationReservationError(
                "reservation temporary byte verification failed"
            )
        _parse_stream(root, candidate, expected_path)
        try:
            os.link(temp, target)
        except FileExistsError as exc:
            raise DispatchAuthorizationReservationError(
                "reservation target collided during no-overwrite publication"
            ) from exc
        published = True
        _reject_symlink_components(target, "published reservation")
        if _is_link_or_reparse(target) or not target.is_file():
            raise DispatchAuthorizationReservationIntegrityCriticalError(
                "published reservation is not the exact expected regular file"
            )
        if _read_stream_bytes(target, "published reservation") != candidate:
            raise DispatchAuthorizationReservationIntegrityCriticalError(
                "published reservation byte verification failed"
            )
        directory_fsync_status = _fsync_directory(reservation_root)
        _cleanup_temp(temp)
        validation = validate_dispatch_authorization_reservation_stream(
            repo_root=root,
            reservation_path=target,
            require_terminal=False,
        )
        return {
            "reservation_committed": True,
            "reservation_stream_path": expected_path,
            "attempt_id": initial["attempt_id"],
            "raw_sha256": _digest(candidate),
            "byte_length": len(candidate),
            "directory_fsync_status": directory_fsync_status,
            "identities_permanently_reserved": True,
            "automatic_retry_with_same_identities_forbidden": True,
            "validation": validation,
            "non_authority": True,
        }
    except DispatchAuthorizationReservationIntegrityCriticalError:
        raise
    except Exception as exc:
        if fd is not None:
            os.close(fd)
        if published:
            raise DispatchAuthorizationReservationIntegrityCriticalError(
                "reservation was published but durable verification did not "
                "complete; identities remain burned"
            ) from exc
        _cleanup_temp(temp)
        if isinstance(exc, DispatchAuthorizationReservationError):
            raise
        raise DispatchAuthorizationReservationError(
            "reservation failed before publication; no KDAUTH mutation may begin"
        ) from exc


def append_dispatch_authorization_crossing_terminal_locked(
    *,
    lock: CrossingLock,
    event: Mapping[str, Any],
) -> dict[str, Any]:
    """Append one durable terminal without rewriting the initial reservation."""
    root = _require_lock(lock)
    terminal = _validate_event(root, event)
    if terminal["event_type"] not in TERMINAL_EVENT_TYPES:
        raise DispatchAuthorizationReservationError(
            "terminal append API requires a closed terminal event"
        )
    path = _repo_path(
        root, terminal["reservation_stream_path"], "reservation target"
    )
    before = validate_dispatch_authorization_reservation_stream(
        repo_root=root,
        reservation_path=path,
        require_terminal=False,
    )
    if before["event_count"] != 1:
        raise DispatchAuthorizationReservationError(
            "reservation stream already has a terminal"
        )
    initial = before["events"][0]
    for field in COMMON_BINDING_FIELDS:
        if terminal[field] != initial[field]:
            raise DispatchAuthorizationReservationError(
                f"terminal common binding mismatch: {field}"
            )
    if terminal["event_type"] == "crossing_committed":
        _validate_committed_cross_surface(root, initial, terminal)
    elif terminal["event_type"] == "crossing_rolled_back_clean":
        _validate_clean_rollback_cross_surface(root, initial, terminal)
    terminal_raw = repo_canonical_json_v1(terminal) + b"\n"
    fd: int | None = None
    append_started = False
    try:
        fd = os.open(path, os.O_WRONLY | os.O_APPEND | BINARY_FLAG)
        append_started = True
        _write_all(fd, terminal_raw)
        os.fsync(fd)
        os.close(fd)
        fd = None
        after = validate_dispatch_authorization_reservation_stream(
            repo_root=root,
            reservation_path=path,
            require_terminal=True,
        )
        if after["events"][1] != terminal:
            raise DispatchAuthorizationReservationIntegrityCriticalError(
                "terminal post-append reread mismatch"
            )
        return {
            "terminal_committed": True,
            "attempt_id": terminal["attempt_id"],
            "reservation_stream_path": terminal[
                "reservation_stream_path"
            ],
            "terminal_outcome": terminal["event_type"],
            "terminal_raw_sha256": _digest(terminal_raw),
            "terminal_raw_byte_length": len(terminal_raw),
            "identities_permanently_reserved": True,
            "automatic_retry_with_same_identities_forbidden": True,
            "validation": after,
            "non_authority": True,
        }
    except DispatchAuthorizationReservationIntegrityCriticalError:
        raise
    except Exception as exc:
        if fd is not None:
            os.close(fd)
        if append_started:
            raise DispatchAuthorizationReservationIntegrityCriticalError(
                "terminal append failed or is uncertain; the initial "
                "reservation remains authoritative and must not be retried"
            ) from exc
        if isinstance(exc, DispatchAuthorizationReservationError):
            raise
        raise DispatchAuthorizationReservationError(
            "terminal append did not begin"
        ) from exc


def _creation_has_exact_kdauth_target(
    root: Path, creation: Mapping[str, Any]
) -> bool:
    path_value = creation.get("authorization_path")
    if not isinstance(path_value, str):
        return False
    try:
        path = _repo_path(root, path_value, "created KDAUTH target")
    except DispatchAuthorizationReservationError:
        return False
    if not path.is_file() or path.is_symlink():
        return False
    try:
        raw = _read_stream_bytes(path, "created KDAUTH target")
        authorization = json.loads(raw.decode("utf-8"))
    except (
        DispatchAuthorizationReservationError,
        UnicodeError,
        json.JSONDecodeError,
    ):
        return False
    return (
        isinstance(authorization, dict)
        and authorization.get("authorization_id")
        == creation.get("authorization_id")
        and authorization.get("authorization_artifact_target_path")
        == path_value
        and authorization.get("authorization_core_sha256")
        == creation.get("authorization_core_sha256")
        and _digest(raw) == creation.get("authorization_file_sha256")
        and len(raw) == creation.get("authorization_byte_length")
    )


def collect_dispatch_authorization_crossing_findings(
    *, repo_root: Path
) -> list[dict[str, Any]]:
    """Collect closed read-only integrity findings for the query layer."""
    root = _resolve_root(repo_root)
    findings: list[dict[str, Any]] = []
    try:
        valid_results, collisions = _logical_attempt_model(
            root=root,
            include_retained_history=True,
            validate_cross_surfaces=True,
        )
    except DispatchAuthorizationReservationError:
        valid_results = []
        collisions = []
        findings.append(
            _finding(
                None,
                "reservation_duplicate_or_invalid_sequence",
                terminal_outcome=None,
            )
        )
    for result in valid_results:
        findings.extend(result["findings"])
    collision_rows: set[tuple[str, str]] = set()
    for collision in collisions:
        for result in (collision["left"], collision["right"]):
            event = result["events"][0]
            key = (
                event["attempt_id"],
                event["reservation_stream_path"],
            )
            if key in collision_rows:
                continue
            collision_rows.add(key)
            findings.append(
                _finding(
                    event,
                    "reservation_identity_collision_across_attempts",
                    terminal_outcome=result["terminal_outcome"],
                )
            )

    initial_events = [result["events"][0] for result in valid_results]
    try:
        creation_rows = [
            event
            for event, _ in _read_audit_lines(root)
            if event.get("event_type") == "authorization_created"
        ]
    except DispatchAuthorizationReservationError:
        creation_rows = []
        findings.append(
            _finding(
                None,
                "reservation_duplicate_or_invalid_sequence",
                terminal_outcome=None,
            )
        )
    for creation in creation_rows:
        if not _creation_has_exact_kdauth_target(root, creation):
            continue
        creation_time: datetime | None
        try:
            creation_time = _parse_timestamp(
                creation.get("occurred_at"),
                "authorization_created.occurred_at",
            )
        except DispatchAuthorizationReservationError:
            creation_time = None
        matching = []
        for event in initial_events:
            authorization = event["authorization_binding"]
            reviewed = event["reviewed_content_binding"]
            if (
                creation_time is not None
                and _parse_timestamp(
                    event["occurred_at"], "reservation.occurred_at"
                )
                < creation_time
                and creation.get("authorization_id")
                == authorization["authorization_id"]
                and creation.get("authorization_path")
                == authorization["authorization_target_path"]
                and creation.get("authorization_file_sha256")
                == reviewed["reviewed_whole_file_sha256"]
                and creation.get("authorization_byte_length")
                == reviewed["reviewed_byte_length"]
                and creation.get("authorization_core_sha256")
                == authorization["authorization_core_sha256"]
                and creation.get("queue_item_id")
                == event["queue_binding"]["queue_item_id"]
                and creation.get("dispatch_id")
                == event["dispatch_binding"]["dispatch_id"]
                and creation.get("run_id")
                == event["run_binding"]["run_id"]
            ):
                matching.append(event)
        if not matching:
            synthetic = {
                "authorization_binding": {
                    "authorization_id": creation.get("authorization_id"),
                    "authorization_target_path":
                        creation.get("authorization_path"),
                },
                "dispatch_binding": {
                    "dispatch_id": creation.get("dispatch_id"),
                    "dispatch_record_path": None,
                },
                "run_binding": {
                    "run_id": creation.get("run_id"),
                    "execution_event_stream_path": None,
                },
                "queue_binding": {
                    "queue_item_id": creation.get("queue_item_id")
                },
            }
            findings.append(
                _finding(
                    synthetic,
                    "authorization_created_without_prior_crossing_reservation",
                    terminal_outcome=None,
                )
            )
    return sorted(
        findings,
        key=lambda row: (
            row["finding_type"],
            row["attempt_id"] or "",
            row["authorization_id"] or "",
        ),
    )
