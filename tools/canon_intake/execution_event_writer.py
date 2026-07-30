"""Protected append-only writer for canonical execution-event streams."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from collections import Counter
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from tools.canon_intake.dispatch_authorization_writer import (
    _AnchoredDirectory,
    _AnchoredFile,
    _write_all,
)
from tools.canon_intake.execution_event import (
    ACCOUNTING_CATEGORIES,
    EXECUTION_WRITER_COMBINED_UNCERTAINTY,
    EXECUTION_WRITER_IDENTITY,
    EXECUTION_WRITER_INTEGRITY_ROOT,
    EXECUTION_WRITER_INTEGRITY_SCHEMA_VERSION,
    OUTCOME_CATEGORIES,
    ExecutionEventError,
    derive_execution_event,
    execution_writer_integrity_record_name,
    read_and_validate_execution_stream,
    serialize_execution_event,
    serialize_execution_writer_integrity_record,
)

WRITER_IDENTITY = EXECUTION_WRITER_IDENTITY
LOCK_ROOT = Path("research/queue")


class ExecutionEventWriterError(ValueError):
    """A proposed execution-event append failed closed before mutation."""


class ExecutionEventWriterIntegrityCriticalError(ExecutionEventWriterError):
    """An append or durability result is uncertain and requires inspection."""


def _digest(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def _selected_path(root: Path, selected: Path) -> Path:
    value = Path(selected)
    return value if value.is_absolute() else root / value


def _require_exact_keys(
    value: Mapping[str, Any],
    expected: set[str],
    *,
    label: str,
) -> None:
    actual = set(value)
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        details = []
        if missing:
            details.append("missing " + ", ".join(missing))
        if extra:
            details.append("unexpected " + ", ".join(extra))
        raise ExecutionEventWriterError(f"{label} fields are invalid: {'; '.join(details)}")


def _validate_requested_binding(
    *,
    dispatch: Mapping[str, Any],
    run_id: str,
    stream_path: str,
) -> None:
    if not isinstance(run_id, str) or not run_id:
        raise ExecutionEventWriterError("run_id must be explicitly supplied")
    if not isinstance(stream_path, str) or not stream_path:
        raise ExecutionEventWriterError("stream_path must be explicitly supplied")
    if run_id != dispatch["run_binding"]["run_id"]:
        raise ExecutionEventWriterError("requested run ID differs from exact dispatch")
    if stream_path != dispatch["run_binding"]["execution_event_stream_path"]:
        raise ExecutionEventWriterError("requested stream path differs from exact dispatch")
    if stream_path != dispatch["output_targets"]["execution_event_stream_path"]:
        raise ExecutionEventWriterError("dispatch run/output stream bindings differ")


def _event_payload(
    *,
    dispatch: Mapping[str, Any],
    event_type: str,
    event_input: Mapping[str, Any],
    existing_events: list[dict[str, Any]],
) -> dict[str, Any]:
    if not isinstance(event_input, Mapping):
        raise ExecutionEventWriterError("event_input must be one object")
    planned = dispatch["denominator"]["planned"]
    attempts = [
        event["attempt_outcome"]
        for event in existing_events
        if event["event_type"] == "attempt_outcome"
    ]
    if event_type == "run_start":
        _require_exact_keys(
            event_input,
            {"runner_process_started"},
            label="run_start input",
        )
        return {
            "start_state": "invocation_started",
            "runner_process_started": event_input["runner_process_started"],
            "planned_denominator": planned,
            "budget": {**dispatch["budget"], "actual": 0},
            "seed": dispatch["execution_parameters"]["seed"],
            "workers": dispatch["execution_parameters"]["workers"],
            "automatic_retry": dispatch["execution_parameters"]["automatic_retry"],
        }
    if event_type == "attempt_outcome":
        _require_exact_keys(
            event_input,
            {"variant_id", "outcome_category", "reason_code"},
            label="attempt_outcome input",
        )
        return {
            "attempt_number": len(attempts) + 1,
            "variant_id": event_input["variant_id"],
            "retry_ordinal": 0,
            "outcome_category": event_input["outcome_category"],
            "reason_code": event_input["reason_code"],
            "counts_toward_budget": True,
            "counts_toward_denominator": True,
        }
    if event_type == "run_terminal":
        _require_exact_keys(
            event_input,
            {"terminal_state", "terminal_reason_code", "process_started"},
            label="run_terminal input",
        )
        observed = Counter(attempt["outcome_category"] for attempt in attempts)
        outcome_counts = {category: observed[category] for category in OUTCOME_CATEGORIES}
        outcome_counts["not_attempted"] = planned - len(attempts)
        return {
            "terminal_state": event_input["terminal_state"],
            "terminal_reason_code": event_input["terminal_reason_code"],
            "process_started": event_input["process_started"],
            "denominator_accounting": {
                "basis": dispatch["denominator"]["basis"],
                "planned": planned,
                "attempts_recorded": len(attempts),
                "population_accounted_total": sum(
                    outcome_counts[category] for category in ACCOUNTING_CATEGORIES
                ),
                "not_attempted": planned - len(attempts),
                "outcome_counts": outcome_counts,
                "mismatch_policy": "reject",
            },
            "budget": {**dispatch["budget"], "actual": len(attempts)},
        }
    raise ExecutionEventWriterError("event_type is outside the closed vocabulary")


def _derive_candidate(
    *,
    root: Path,
    validated_stream: Mapping[str, Any],
    event_type: str,
    timestamp_utc: str,
    actor: Mapping[str, Any],
    event_input: Mapping[str, Any],
) -> tuple[dict[str, Any], bytes, bytes]:
    if not isinstance(event_input, Mapping):
        raise ExecutionEventWriterError("event_input must be one object")
    state = validated_stream["state"]
    existing_events = validated_stream["events"]
    if state == "missing":
        if event_type != "run_start":
            raise ExecutionEventWriterError(
                "a missing execution stream can only be created by run_start"
            )
    else:
        if event_type == "run_start":
            raise ExecutionEventWriterError("run_start already exists")
        if state == "terminal":
            raise ExecutionEventWriterError("execution stream is already terminal")
        if actor != existing_events[0]["actor"]:
            raise ExecutionEventWriterError("actor/tool identity changed within stream")
    attempts = [
        event["attempt_outcome"]
        for event in existing_events
        if event["event_type"] == "attempt_outcome"
    ]
    if event_type == "attempt_outcome":
        if not existing_events[0]["run_start"]["runner_process_started"]:
            raise ExecutionEventWriterError(
                "attempt cannot follow a start where the process did not start"
            )
        if len(attempts) >= validated_stream["dispatch"]["denominator"]["planned"]:
            raise ExecutionEventWriterError("attempt count would exceed planned denominator")
        requested_variant = event_input.get("variant_id")
        if requested_variant in {attempt["variant_id"] for attempt in attempts}:
            raise ExecutionEventWriterError("variant ID recurs in execution stream")
    if (
        event_type == "run_terminal"
        and event_input.get("process_started")
        != existing_events[0]["run_start"]["runner_process_started"]
    ):
        raise ExecutionEventWriterError("start/terminal process-start truth mismatch")
    payload = _event_payload(
        dispatch=validated_stream["dispatch"],
        event_type=event_type,
        event_input=event_input,
        existing_events=existing_events,
    )
    sequence_number = len(existing_events) + 1
    try:
        event = derive_execution_event(
            repo_root=root,
            dispatch=validated_stream["dispatch"],
            dispatch_file_sha256=validated_stream["dispatch_file_sha256"],
            event_type=event_type,
            sequence_number=sequence_number,
            timestamp_utc=timestamp_utc,
            actor=actor,
            payload=payload,
        )
    except ExecutionEventError as exc:
        raise ExecutionEventWriterError(str(exc)) from exc
    event_raw = serialize_execution_event(event)
    prior_raw = validated_stream["raw"] or b""
    return event, event_raw, prior_raw + event_raw


def _preflight(
    *,
    root: Path,
    dispatch_path: Path,
    reviewed_dispatch_whole_file_sha256: str,
    run_id: str,
    stream_path: str,
    event_type: str,
    timestamp_utc: str,
    actor: Mapping[str, Any],
    event_input: Mapping[str, Any],
) -> dict[str, Any]:
    try:
        result = read_and_validate_execution_stream(
            repo_root=root,
            dispatch_path=dispatch_path,
            reviewed_dispatch_whole_file_sha256=reviewed_dispatch_whole_file_sha256,
            allow_missing=True,
            require_terminal=False,
            scan_retained_history=True,
        )
    except ExecutionEventError as exc:
        raise ExecutionEventWriterError(str(exc)) from exc
    _validate_requested_binding(
        dispatch=result["dispatch"],
        run_id=run_id,
        stream_path=stream_path,
    )
    _derive_candidate(
        root=root,
        validated_stream=result,
        event_type=event_type,
        timestamp_utc=timestamp_utc,
        actor=actor,
        event_input=event_input,
    )
    return result


def _write_combined_uncertainty_record(
    *,
    integrity_parent: _AnchoredDirectory,
    state: Mapping[str, Any],
) -> str:
    sequence_number = state["event_sequence_number"]
    name = execution_writer_integrity_record_name(
        run_id=state["run_id"],
        event_sequence_number=sequence_number,
    )
    record = {
        "schema_version": EXECUTION_WRITER_INTEGRITY_SCHEMA_VERSION,
        "record_kind": EXECUTION_WRITER_COMBINED_UNCERTAINTY,
        "writer_identity": WRITER_IDENTITY,
        "dispatch_id": state["dispatch_id"],
        "dispatch_path": state["dispatch_path"],
        "run_id": state["run_id"],
        "execution_event_stream_path": state["stream_path"],
        "event_id": state["event_id"],
        "event_sequence_number": sequence_number,
        "primary_failure_phase": "append_or_durability",
        "primary_uncertainty_class": "append_or_durability_uncertain",
        "event_durable": state["event_durable"],
        "stream_may_have_changed": state["append_started"],
        "lock_cleanup_also_uncertain": True,
        "operator_inspection_required": True,
        "non_authority": True,
    }
    raw = serialize_execution_writer_integrity_record(record)
    integrity_file: _AnchoredFile | None = None
    integrity_parent.assert_current()
    integrity_parent.require_absent(name)
    try:
        integrity_file = integrity_parent.create(name)
        _write_all(integrity_file.fd, raw)
        integrity_file.fsync()
        integrity_parent.fsync()
        integrity_parent.assert_current()
        integrity_parent.verify_reference(
            name,
            expected_identity=integrity_file.identity,
            expected_raw=raw,
        )
    finally:
        if integrity_file is not None:
            integrity_file.close()
    return (EXECUTION_WRITER_INTEGRITY_ROOT / name).as_posix()


@contextmanager
def _run_append_lock(
    *,
    root: Path,
    run_id: str,
    state: dict[str, Any],
    integrity_parent: _AnchoredDirectory,
) -> Iterator[_AnchoredDirectory]:
    parent: _AnchoredDirectory | None = None
    lock_file: _AnchoredFile | None = None
    primary_integrity_error: ExecutionEventWriterIntegrityCriticalError | None = None
    lock_name = f".{run_id}.execution_event_append.lock"
    try:
        parent = _AnchoredDirectory(
            root=root,
            relative=LOCK_ROOT,
            label="execution append lock parent",
        )
        parent.assert_current()
        parent.require_absent(lock_name)
        lock_file = parent.create(lock_name)
        lock_raw = (
            json.dumps(
                {
                    "lock_kind": "canonical_execution_event_append",
                    "pid": os.getpid(),
                    "run_id": run_id,
                    "writer_identity": WRITER_IDENTITY,
                },
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
            + b"\n"
        )
        _write_all(lock_file.fd, lock_raw)
        lock_file.fsync()
        parent.fsync()
        parent.assert_current()
        parent.verify_reference(
            lock_name,
            expected_identity=lock_file.identity,
            expected_raw=lock_raw,
        )
        yield parent
    except FileExistsError as exc:
        raise ExecutionEventWriterError(
            "per-run execution append lock exists; stale locks fail closed"
        ) from exc
    except ExecutionEventWriterIntegrityCriticalError as exc:
        primary_integrity_error = exc
        raise
    except ExecutionEventWriterError:
        raise
    except OSError as exc:
        if state["append_started"]:
            error = ExecutionEventWriterIntegrityCriticalError(
                "execution append or durability is uncertain; preserve history and inspect"
            )
            error.failure_phase = "append_or_durability"
            error.uncertainty_class = "append_or_durability_uncertain"
            error.stream_may_have_changed = True
            error.event_durable = state["event_durable"]
            error.lock_cleanup_also_uncertain = False
            error.integrity_visibility_recorded = False
            error.integrity_visibility_record_path = None
            error.integrity_visibility_record_uncertain = False
            primary_integrity_error = error
            raise error from exc
        raise ExecutionEventWriterError(
            "descriptor-anchored per-run append lock is unavailable"
        ) from exc
    finally:
        cleanup_error: OSError | None = None
        if lock_file is not None:
            try:
                lock_file.delete()
                if parent is not None:
                    parent.fsync()
                    parent.assert_current()
            except OSError as exc:
                cleanup_error = exc
                lock_file.close()
        if parent is not None:
            parent.close()
        if cleanup_error is not None:
            if primary_integrity_error is not None:
                primary_integrity_error.lock_cleanup_also_uncertain = True
                try:
                    record_path = _write_combined_uncertainty_record(
                        integrity_parent=integrity_parent,
                        state=state,
                    )
                except Exception as visibility_error:
                    primary_integrity_error.integrity_visibility_recorded = False
                    try:
                        expected_name = execution_writer_integrity_record_name(
                            run_id=state["run_id"],
                            event_sequence_number=state["event_sequence_number"],
                        )
                    except Exception:
                        expected_name = None
                    primary_integrity_error.integrity_visibility_record_path = (
                        (EXECUTION_WRITER_INTEGRITY_ROOT / expected_name).as_posix()
                        if expected_name is not None
                        else None
                    )
                    primary_integrity_error.integrity_visibility_record_uncertain = True
                    primary_integrity_error.integrity_visibility_record_error = str(
                        visibility_error
                    )
                else:
                    primary_integrity_error.integrity_visibility_recorded = True
                    primary_integrity_error.integrity_visibility_record_path = record_path
                    primary_integrity_error.integrity_visibility_record_uncertain = False
            else:
                error = ExecutionEventWriterIntegrityCriticalError(
                    "execution append lock cleanup is uncertain; operator inspection required"
                )
                error.failure_phase = "lock_cleanup"
                error.uncertainty_class = "lock_cleanup_uncertain"
                error.stream_may_have_changed = state["append_started"]
                error.event_durable = state["event_durable"]
                error.lock_cleanup_also_uncertain = False
                error.integrity_visibility_recorded = False
                error.integrity_visibility_record_path = None
                error.integrity_visibility_record_uncertain = False
                raise error from cleanup_error


def _append_under_lock(
    *,
    root: Path,
    lock_parent: _AnchoredDirectory,
    dispatch_path: Path,
    reviewed_dispatch_whole_file_sha256: str,
    run_id: str,
    stream_path: str,
    event_type: str,
    timestamp_utc: str,
    actor: Mapping[str, Any],
    event_input: Mapping[str, Any],
    state: dict[str, Any],
) -> dict[str, Any]:
    dispatch_parent: _AnchoredDirectory | None = None
    stream_parent: _AnchoredDirectory | None = None
    dispatch_file: _AnchoredFile | None = None
    stream_file: _AnchoredFile | None = None
    try:
        dispatch_parent = _AnchoredDirectory(
            root=root,
            relative=dispatch_path.parent.relative_to(root),
            label="authoritative dispatch parent",
        )
        stream_parent = _AnchoredDirectory(
            root=root,
            relative=Path(stream_path).parent,
            label="execution stream parent",
        )
        dispatch_file = dispatch_parent.open_existing(
            dispatch_path.name,
            writable=False,
        )
        dispatch_raw = dispatch_file.read()
        if _digest(dispatch_raw) != reviewed_dispatch_whole_file_sha256:
            raise ExecutionEventWriterError("anchored dispatch bytes differ from reviewed SHA-256")
        stream_name = Path(stream_path).name
        try:
            stream_file = stream_parent.open_existing(stream_name, writable=True)
            anchored_prior_raw: bytes | None = stream_file.read()
        except FileNotFoundError:
            stream_file = None
            anchored_prior_raw = None

        try:
            validated = read_and_validate_execution_stream(
                repo_root=root,
                dispatch_path=dispatch_path,
                reviewed_dispatch_whole_file_sha256=reviewed_dispatch_whole_file_sha256,
                allow_missing=True,
                require_terminal=False,
                scan_retained_history=True,
            )
        except ExecutionEventError as exc:
            raise ExecutionEventWriterError(str(exc)) from exc
        _validate_requested_binding(
            dispatch=validated["dispatch"],
            run_id=run_id,
            stream_path=stream_path,
        )
        if json.loads(dispatch_raw.decode("utf-8")) != validated["dispatch"]:
            raise OSError("anchored dispatch differs from authoritative validation")
        if validated["raw"] != anchored_prior_raw:
            raise OSError("anchored stream differs from authoritative validation")

        event, event_raw, completed_raw = _derive_candidate(
            root=root,
            validated_stream=validated,
            event_type=event_type,
            timestamp_utc=timestamp_utc,
            actor=actor,
            event_input=event_input,
        )
        state["event_id"] = event["event_id"]
        state["event_sequence_number"] = event["sequence_number"]
        for parent in (lock_parent, dispatch_parent, stream_parent):
            parent.assert_current()
        dispatch_parent.verify_reference(
            dispatch_path.name,
            expected_identity=dispatch_file.identity,
            expected_raw=dispatch_raw,
        )
        if stream_file is None:
            stream_parent.require_absent(stream_name)
            state["append_started"] = True
            stream_file = stream_parent.create(stream_name)
        else:
            stream_parent.verify_reference(
                stream_name,
                expected_identity=stream_file.identity,
                expected_raw=anchored_prior_raw,
            )
            end = os.lseek(stream_file.fd, 0, os.SEEK_END)
            if end != len(anchored_prior_raw):
                raise OSError("anchored stream length changed before append")
            state["append_started"] = True

        _write_all(stream_file.fd, event_raw)
        stream_file.fsync()
        stream_parent.fsync()
        for parent in (lock_parent, dispatch_parent, stream_parent):
            parent.assert_current()
        dispatch_parent.verify_reference(
            dispatch_path.name,
            expected_identity=dispatch_file.identity,
            expected_raw=dispatch_raw,
        )
        stream_parent.verify_reference(
            stream_name,
            expected_identity=stream_file.identity,
            expected_raw=completed_raw,
        )
        if stream_file.read() != completed_raw:
            raise OSError("durable execution stream reread mismatch")
        try:
            completed = read_and_validate_execution_stream(
                repo_root=root,
                dispatch_path=dispatch_path,
                reviewed_dispatch_whole_file_sha256=reviewed_dispatch_whole_file_sha256,
                allow_missing=False,
                require_terminal=event_type == "run_terminal",
                scan_retained_history=True,
            )
        except ExecutionEventError as exc:
            raise OSError("completed execution stream validation failed") from exc
        if (
            completed["raw"] != completed_raw
            or completed["events"][-1] != event
            or completed["stream_file_sha256"] != _digest(completed_raw)
        ):
            raise OSError("completed execution stream proof differs from appended event")
        stream_parent.verify_reference(
            stream_name,
            expected_identity=stream_file.identity,
            expected_raw=completed_raw,
        )
        dispatch_parent.verify_reference(
            dispatch_path.name,
            expected_identity=dispatch_file.identity,
            expected_raw=dispatch_raw,
        )
        state["event_durable"] = True
        return {
            "event": event,
            "event_raw": event_raw,
            "completed": completed,
        }
    except ExecutionEventWriterIntegrityCriticalError:
        raise
    except ExecutionEventWriterError:
        raise
    except Exception as exc:
        if state["append_started"]:
            error = ExecutionEventWriterIntegrityCriticalError(
                "execution append or durable verification is uncertain; history was not repaired"
            )
            error.failure_phase = "append_or_durability"
            error.uncertainty_class = "append_or_durability_uncertain"
            error.stream_may_have_changed = True
            error.event_durable = state["event_durable"]
            error.lock_cleanup_also_uncertain = False
            error.integrity_visibility_recorded = False
            error.integrity_visibility_record_path = None
            error.integrity_visibility_record_uncertain = False
            raise error from exc
        raise ExecutionEventWriterError(
            "descriptor-anchored execution append validation failed"
        ) from exc
    finally:
        if stream_file is not None:
            stream_file.close()
        if dispatch_file is not None:
            dispatch_file.close()
        if stream_parent is not None:
            stream_parent.close()
        if dispatch_parent is not None:
            dispatch_parent.close()


def write_execution_event(
    *,
    repo_root: Path,
    dispatch_path: Path,
    reviewed_dispatch_whole_file_sha256: str,
    run_id: str,
    stream_path: str,
    event_type: str,
    timestamp_utc: str,
    actor: Mapping[str, Any],
    event_input: Mapping[str, Any],
) -> dict[str, Any]:
    """Append exactly one lawful canonical event to one consumed dispatch stream."""
    if not isinstance(reviewed_dispatch_whole_file_sha256, str):
        raise ExecutionEventWriterError(
            "reviewed dispatch whole-file SHA-256 must be explicitly supplied"
        )
    if not isinstance(actor, Mapping):
        raise ExecutionEventWriterError("actor/tool identity must be one object")
    lexical_root = _selected_path(Path.cwd(), Path(repo_root))
    selected_dispatch = _selected_path(lexical_root, dispatch_path)
    preflight = _preflight(
        root=lexical_root,
        dispatch_path=selected_dispatch,
        reviewed_dispatch_whole_file_sha256=reviewed_dispatch_whole_file_sha256,
        run_id=run_id,
        stream_path=stream_path,
        event_type=event_type,
        timestamp_utc=timestamp_utc,
        actor=actor,
        event_input=event_input,
    )
    root = lexical_root.resolve()
    selected_dispatch = _selected_path(root, dispatch_path)
    dispatch = preflight["dispatch"]
    state: dict[str, Any] = {
        "append_started": False,
        "event_durable": False,
        "dispatch_id": dispatch["dispatch_id"],
        "dispatch_path": dispatch["dispatch_record_path"],
        "run_id": run_id,
        "stream_path": stream_path,
        "event_id": None,
        "event_sequence_number": None,
    }
    integrity_parent: _AnchoredDirectory | None = None
    try:
        integrity_parent = _AnchoredDirectory(
            root=root,
            relative=EXECUTION_WRITER_INTEGRITY_ROOT,
            label="execution-writer integrity parent",
        )
        integrity_parent.assert_current()
        with _run_append_lock(
            root=root,
            run_id=run_id,
            state=state,
            integrity_parent=integrity_parent,
        ) as lock_parent:
            appended = _append_under_lock(
                root=root,
                lock_parent=lock_parent,
                dispatch_path=selected_dispatch,
                reviewed_dispatch_whole_file_sha256=(reviewed_dispatch_whole_file_sha256),
                run_id=run_id,
                stream_path=stream_path,
                event_type=event_type,
                timestamp_utc=timestamp_utc,
                actor=actor,
                event_input=event_input,
                state=state,
            )
    except ExecutionEventWriterError:
        raise
    except OSError as exc:
        raise ExecutionEventWriterError(
            "descriptor-anchored execution-writer integrity parent is unavailable"
        ) from exc
    finally:
        if integrity_parent is not None:
            integrity_parent.close()
    event = appended["event"]
    completed = appended["completed"]
    return {
        "event_appended": True,
        "event_id": event["event_id"],
        "event_type": event["event_type"],
        "sequence_number": event["sequence_number"],
        "run_id": run_id,
        "stream_path": stream_path,
        "event_sha256": _digest(appended["event_raw"]),
        "stream_file_sha256": completed["stream_file_sha256"],
        "stream_byte_length": completed["stream_byte_length"],
        "stream_state": completed["state"],
        "writer_identity": WRITER_IDENTITY,
        "non_authority": {
            "control_plane_history_only": True,
            "does_not_invoke_runner": True,
            "does_not_create_result_population": True,
            "does_not_create_dispatch_or_kdauth": True,
            "does_not_authorize_runtime_paper_live_or_capital": True,
        },
    }


def _json_object(value: str, label: str) -> dict[str, Any]:
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError as exc:
        raise ExecutionEventWriterError(f"{label} must be valid JSON") from exc
    if not isinstance(parsed, dict):
        raise ExecutionEventWriterError(f"{label} must decode to one object")
    return parsed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--dispatch", type=Path, required=True)
    parser.add_argument(
        "--reviewed-dispatch-whole-file-sha256",
        required=True,
    )
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--stream-path", required=True)
    parser.add_argument(
        "--event-type",
        choices=("run_start", "attempt_outcome", "run_terminal"),
        required=True,
    )
    parser.add_argument("--timestamp-utc", required=True)
    parser.add_argument("--actor-json", required=True)
    parser.add_argument("--event-input-json", required=True)
    args = parser.parse_args()
    try:
        result = write_execution_event(
            repo_root=args.repo_root,
            dispatch_path=args.dispatch,
            reviewed_dispatch_whole_file_sha256=(args.reviewed_dispatch_whole_file_sha256),
            run_id=args.run_id,
            stream_path=args.stream_path,
            event_type=args.event_type,
            timestamp_utc=args.timestamp_utc,
            actor=_json_object(args.actor_json, "actor-json"),
            event_input=_json_object(args.event_input_json, "event-input-json"),
        )
    except ExecutionEventWriterError as exc:
        parser.exit(2, f"execution-event writer stopped: {exc}\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
