import copy
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

import pytest

from tests import test_dispatch_writer as dispatch_support
from tools.canon_intake import dispatch_writer
from tools.canon_intake.execution_event import (
    EXECUTION_WRITER_COMBINED_UNCERTAINTY,
    EXECUTION_WRITER_EVENT_DURABLE,
    EXECUTION_WRITER_IDENTITY,
    EXECUTION_WRITER_INTEGRITY_ROOT,
    EXECUTION_WRITER_INTEGRITY_SCHEMA_VERSION,
    EXECUTION_WRITER_MUTATION_RESERVED,
    EXECUTION_WRITER_VISIBILITY_MARKER_SCHEMA_VERSION,
    ExecutionEventError,
    collect_execution_stream_integrity_findings,
    derive_execution_event,
    execution_writer_integrity_record_name,
    execution_writer_visibility_marker_name,
    read_and_validate_execution_stream,
    serialize_execution_event,
    serialize_execution_writer_integrity_record,
    serialize_execution_writer_visibility_marker,
    validate_execution_event,
    validate_execution_stream_history,
)


def _hash(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def _git(root: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)


def _commit(root: Path, message: str) -> None:
    _git(root, "add", ".")
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "commit",
            "-m",
            message,
        ],
        cwd=root,
        check=True,
        capture_output=True,
    )


@pytest.fixture
def fixture(tmp_path: Path) -> dict:
    source_repo = Path(__file__).resolve().parents[1]
    prepared = dispatch_support._prepare_fixture(tmp_path, source_repo)
    schema = source_repo / "research/schemas/canon_execution_event.schema.json"
    shutil.copy2(schema, prepared["root"] / "research/schemas" / schema.name)
    dispatch_writer.write_dispatch_record(**dispatch_support._writer_kwargs(prepared))
    dispatch_raw = prepared["dispatch_path"].read_bytes()
    dispatch = json.loads(dispatch_raw)
    stream_path = prepared["root"] / dispatch["run_binding"]["execution_event_stream_path"]
    stream_path.parent.mkdir(parents=True, exist_ok=True)
    (prepared["root"] / EXECUTION_WRITER_INTEGRITY_ROOT).mkdir(
        parents=True,
        exist_ok=True,
    )
    prepared.update(
        {
            "dispatch": dispatch,
            "dispatch_raw": dispatch_raw,
            "dispatch_hash": _hash(dispatch_raw),
            "stream_path": stream_path,
            "actor": {
                "actor_id": "synthetic-operator",
                "tool_name": "synthetic-execution-writer",
                "tool_version": "test-only-v1",
                "tool_source_path": "tests/test_execution_event.py",
                "tool_source_sha256": "sha256:" + "3" * 64,
            },
        }
    )
    return prepared


def _start(fixture: dict, *, process_started: bool = True) -> dict:
    dispatch = fixture["dispatch"]
    return derive_execution_event(
        repo_root=fixture["root"],
        dispatch=dispatch,
        dispatch_file_sha256=fixture["dispatch_hash"],
        event_type="run_start",
        sequence_number=1,
        timestamp_utc="2026-07-20T12:00:01Z",
        actor=fixture["actor"],
        payload={
            "start_state": "invocation_started",
            "runner_process_started": process_started,
            "planned_denominator": dispatch["denominator"]["planned"],
            "budget": {**dispatch["budget"], "actual": 0},
            "seed": dispatch["execution_parameters"]["seed"],
            "workers": dispatch["execution_parameters"]["workers"],
            "automatic_retry": False,
        },
    )


def _attempt(
    fixture: dict,
    *,
    number: int,
    category: str = "successful",
    reason: str = "completed",
) -> dict:
    return derive_execution_event(
        repo_root=fixture["root"],
        dispatch=fixture["dispatch"],
        dispatch_file_sha256=fixture["dispatch_hash"],
        event_type="attempt_outcome",
        sequence_number=number + 1,
        timestamp_utc=f"2026-07-20T12:00:{number + 1:02d}Z",
        actor=fixture["actor"],
        payload={
            "attempt_number": number,
            "variant_id": f"SYNTHETIC-VARIANT-{number:03d}",
            "retry_ordinal": 0,
            "outcome_category": category,
            "reason_code": reason,
            "counts_toward_budget": True,
            "counts_toward_denominator": True,
        },
    )


def _blocked_terminal(fixture: dict, attempts: list[dict]) -> dict:
    dispatch = fixture["dispatch"]
    planned = dispatch["denominator"]["planned"]
    counts = {
        "successful": 0,
        "failed": 0,
        "invalid": 0,
        "excluded": 0,
        "errored": 0,
        "aborted": 0,
        "filtered": 0,
        "data_unavailable": 0,
        "not_attempted": planned - len(attempts),
    }
    for event in attempts:
        counts[event["attempt_outcome"]["outcome_category"]] += 1
    return derive_execution_event(
        repo_root=fixture["root"],
        dispatch=dispatch,
        dispatch_file_sha256=fixture["dispatch_hash"],
        event_type="run_terminal",
        sequence_number=len(attempts) + 2,
        timestamp_utc="2026-07-20T12:01:00Z",
        actor=fixture["actor"],
        payload={
            "terminal_state": "run_blocked",
            "terminal_reason_code": "fail_closed_stop_condition",
            "process_started": True,
            "denominator_accounting": {
                "basis": dispatch["denominator"]["basis"],
                "planned": planned,
                "attempts_recorded": len(attempts),
                "population_accounted_total": planned,
                "not_attempted": planned - len(attempts),
                "outcome_counts": counts,
                "mismatch_policy": "reject",
            },
            "budget": {**dispatch["budget"], "actual": len(attempts)},
        },
    )


def _write_stream(fixture: dict, events: list[dict]) -> bytes:
    raw = b"".join(serialize_execution_event(event) for event in events)
    fixture["stream_path"].write_bytes(raw)
    return raw


def test_public_derivation_owns_bindings_and_returns_exact_canonical_line(
    fixture,
):
    event = _start(fixture)
    validation = validate_execution_event(
        repo_root=fixture["root"],
        dispatch=fixture["dispatch"],
        dispatch_file_sha256=fixture["dispatch_hash"],
        event=event,
    )

    assert event["bindings"] == {
        "dispatch_id": fixture["dispatch"]["dispatch_id"],
        "dispatch_record_path": fixture["dispatch"]["dispatch_record_path"],
        "dispatch_record_sha256": fixture["dispatch_hash"],
        "run_id": fixture["dispatch"]["run_binding"]["run_id"],
        "queue_item_id": fixture["dispatch"]["queue_binding"]["queue_item_id"],
    }
    assert validation["canonical_raw"] == serialize_execution_event(event)
    assert validation["canonical_raw"].endswith(b"\n")
    assert validation["canonical_raw"].count(b"\n") == 1
    assert json.loads(validation["canonical_raw"]) == event


def test_authoritative_consumed_dispatch_accepts_complete_exact_stream(fixture):
    attempts = [
        _attempt(fixture, number=1),
        _attempt(
            fixture,
            number=2,
            category="failed",
            reason="runner_failure",
        ),
    ]
    events = [_start(fixture), *attempts, _blocked_terminal(fixture, attempts)]
    raw = _write_stream(fixture, events)

    result = read_and_validate_execution_stream(
        repo_root=fixture["root"],
        dispatch_path=fixture["dispatch_path"],
        reviewed_dispatch_whole_file_sha256=fixture["dispatch_hash"],
        require_terminal=True,
    )

    assert result["state"] == "terminal"
    assert result["events"] == events
    assert result["raw"] == raw
    assert result["dispatch_validation"]["lifecycle_state"] == "consumed"
    assert collect_execution_stream_integrity_findings(repo_root=fixture["root"]) == []


def test_missing_and_incomplete_streams_are_visible_without_mutation(fixture):
    before = fixture["dispatch_path"].read_bytes()
    missing = read_and_validate_execution_stream(
        repo_root=fixture["root"],
        dispatch_path=fixture["dispatch_path"],
        reviewed_dispatch_whole_file_sha256=fixture["dispatch_hash"],
        allow_missing=True,
    )
    assert missing["state"] == "missing"
    assert [
        finding["finding_type"]
        for finding in collect_execution_stream_integrity_findings(repo_root=fixture["root"])
    ] == ["execution_stream_missing"]

    _write_stream(fixture, [_start(fixture), _attempt(fixture, number=1)])
    incomplete = read_and_validate_execution_stream(
        repo_root=fixture["root"],
        dispatch_path=fixture["dispatch_path"],
        reviewed_dispatch_whole_file_sha256=fixture["dispatch_hash"],
    )
    assert incomplete["state"] == "in_progress"
    with pytest.raises(ExecutionEventError, match="incomplete"):
        read_and_validate_execution_stream(
            repo_root=fixture["root"],
            dispatch_path=fixture["dispatch_path"],
            reviewed_dispatch_whole_file_sha256=fixture["dispatch_hash"],
            require_terminal=True,
        )
    assert [
        finding["finding_type"]
        for finding in collect_execution_stream_integrity_findings(repo_root=fixture["root"])
    ] == ["execution_stream_incomplete"]
    assert fixture["dispatch_path"].read_bytes() == before


@pytest.mark.parametrize("record_state", ["canonical", "partial"])
def test_combined_writer_uncertainty_record_is_independently_read_only_visible(
    fixture,
    record_state,
):
    run_id = fixture["dispatch"]["run_binding"]["run_id"]
    stream_path = fixture["dispatch"]["run_binding"]["execution_event_stream_path"]
    name = execution_writer_integrity_record_name(
        run_id=run_id,
        event_sequence_number=2,
    )
    path = fixture["root"] / EXECUTION_WRITER_INTEGRITY_ROOT / name
    record = {
        "schema_version": EXECUTION_WRITER_INTEGRITY_SCHEMA_VERSION,
        "record_kind": EXECUTION_WRITER_COMBINED_UNCERTAINTY,
        "writer_identity": EXECUTION_WRITER_IDENTITY,
        "dispatch_id": fixture["dispatch"]["dispatch_id"],
        "dispatch_path": fixture["dispatch"]["dispatch_record_path"],
        "run_id": run_id,
        "execution_event_stream_path": stream_path,
        "event_id": f"EXEC-EVENT-{run_id}-000002",
        "event_sequence_number": 2,
        "primary_failure_phase": "append_or_durability",
        "primary_uncertainty_class": "append_or_durability_uncertain",
        "event_durable": False,
        "stream_may_have_changed": True,
        "lock_cleanup_also_uncertain": True,
        "operator_inspection_required": True,
        "non_authority": True,
    }
    raw = (
        serialize_execution_writer_integrity_record(record)
        if record_state == "canonical"
        else b'{"partial":true}'
    )
    path.write_bytes(raw)

    findings = collect_execution_stream_integrity_findings(repo_root=fixture["root"])

    assert path.read_bytes() == raw
    expected_types = {
        "execution_writer_append_or_durability_uncertain",
        "execution_writer_lock_cleanup_also_uncertain",
    }
    incident_rows = [row for row in findings if row["finding_type"] in expected_types]
    assert {row["finding_type"] for row in incident_rows} == expected_types
    assert all(row["run_id"] == run_id for row in incident_rows)
    assert all(row["execution_event_stream_path"] == stream_path for row in incident_rows)
    assert all(row["stream_state"] == "integrity_critical" for row in incident_rows)
    assert all(row["operator_inspection_required"] for row in incident_rows)
    assert all(row["non_authority"] for row in incident_rows)
    if record_state == "canonical":
        assert all(
            row["dispatch_id"] == fixture["dispatch"]["dispatch_id"] for row in incident_rows
        )
        assert all("malformed" not in row["reason"] for row in incident_rows)
    else:
        assert all(row["dispatch_id"] is None for row in incident_rows)
        assert all("malformed" in row["reason"] for row in incident_rows)


def _visibility_marker_record(fixture, *, record_kind):
    run_id = fixture["dispatch"]["run_binding"]["run_id"]
    durable = record_kind == EXECUTION_WRITER_EVENT_DURABLE
    return {
        "schema_version": EXECUTION_WRITER_VISIBILITY_MARKER_SCHEMA_VERSION,
        "record_kind": record_kind,
        "writer_identity": EXECUTION_WRITER_IDENTITY,
        "dispatch_id": fixture["dispatch"]["dispatch_id"],
        "dispatch_path": fixture["dispatch"]["dispatch_record_path"],
        "run_id": run_id,
        "execution_event_stream_path": fixture["dispatch"]["run_binding"][
            "execution_event_stream_path"
        ],
        "event_id": f"EXEC-EVENT-{run_id}-000002",
        "event_sequence_number": 2,
        "event_durable": durable,
        "stream_file_sha256": "sha256:" + "a" * 64 if durable else None,
        "stream_byte_length": 123 if durable else None,
        "lock_cleanup_succeeded_after_primary_uncertainty": False,
        "non_authority": True,
    }


@pytest.mark.parametrize("malformed_kind", ["reservation", "durable_proof"])
def test_partial_visibility_marker_remains_conservatively_visible_without_mutation(
    fixture,
    malformed_kind,
):
    run_id = fixture["dispatch"]["run_binding"]["run_id"]
    audit_root = fixture["root"] / EXECUTION_WRITER_INTEGRITY_ROOT
    reservation_name = execution_writer_visibility_marker_name(
        run_id=run_id,
        event_sequence_number=2,
        record_kind=EXECUTION_WRITER_MUTATION_RESERVED,
    )
    reservation_path = audit_root / reservation_name
    if malformed_kind == "reservation":
        reservation_path.write_bytes(b'{"partial":true}')
    else:
        reservation_path.write_bytes(
            serialize_execution_writer_visibility_marker(
                _visibility_marker_record(
                    fixture,
                    record_kind=EXECUTION_WRITER_MUTATION_RESERVED,
                )
            )
        )
        durable_name = execution_writer_visibility_marker_name(
            run_id=run_id,
            event_sequence_number=2,
            record_kind=EXECUTION_WRITER_EVENT_DURABLE,
        )
        (audit_root / durable_name).write_bytes(b'{"partial":true}')
    before = {path: path.read_bytes() for path in audit_root.iterdir()}

    findings = collect_execution_stream_integrity_findings(repo_root=fixture["root"])

    assert {path: path.read_bytes() for path in audit_root.iterdir()} == before
    expected_types = {
        "execution_writer_append_or_durability_uncertain",
        "execution_writer_lock_cleanup_also_uncertain",
    }
    rows = [row for row in findings if row["finding_type"] in expected_types]
    assert {row["finding_type"] for row in rows} == expected_types
    assert all("malformed" in row["reason"] for row in rows if "append" in row["finding_type"])


@pytest.mark.parametrize(
    "mutation,error",
    [
        ("dispatch_hash", "reviewed SHA-256"),
        ("outcome_reason", "outcome/reason"),
        ("duplicate_variant", "variant ID recurs"),
        ("actor_drift", "actor/tool identity changed"),
        ("terminal_category_count", "successful count differs"),
        ("event_after_terminal", "appears after terminal"),
        ("partial_tail", "partial tail"),
    ],
)
def test_malformed_or_conflicting_streams_fail_closed(fixture, mutation, error):
    attempts = [_attempt(fixture, number=1)]
    events = [_start(fixture), *attempts, _blocked_terminal(fixture, attempts)]
    reviewed_hash = fixture["dispatch_hash"]
    if mutation == "dispatch_hash":
        reviewed_hash = "sha256:" + "0" * 64
    elif mutation == "outcome_reason":
        events[1]["attempt_outcome"]["reason_code"] = "execution_error"
    elif mutation == "duplicate_variant":
        second = _attempt(fixture, number=2)
        second["attempt_outcome"]["variant_id"] = events[1]["attempt_outcome"]["variant_id"]
        events = [
            events[0],
            events[1],
            second,
            _blocked_terminal(fixture, [events[1], second]),
        ]
    elif mutation == "actor_drift":
        events[1]["actor"]["actor_id"] = "different-actor"
    elif mutation == "terminal_category_count":
        counts = events[-1]["run_terminal"]["denominator_accounting"]["outcome_counts"]
        counts["successful"] = 0
        counts["failed"] = 1
    elif mutation == "event_after_terminal":
        trailing = _attempt(fixture, number=2)
        trailing["sequence_number"] = 4
        trailing["event_id"] = (
            "EXEC-EVENT-" + fixture["dispatch"]["run_binding"]["run_id"] + "-000004"
        )
        events.append(trailing)
    raw = b"".join(serialize_execution_event(event) for event in events)
    if mutation == "partial_tail":
        raw = raw[:-1]
    fixture["stream_path"].write_bytes(raw)

    with pytest.raises(ExecutionEventError, match=error):
        read_and_validate_execution_stream(
            repo_root=fixture["root"],
            dispatch_path=fixture["dispatch_path"],
            reviewed_dispatch_whole_file_sha256=reviewed_hash,
        )


def test_noncanonical_jsonl_line_is_rejected(fixture):
    event = _start(fixture)
    fixture["stream_path"].write_bytes(
        json.dumps(event, sort_keys=True, indent=2).encode("utf-8") + b"\n"
    )

    with pytest.raises(ExecutionEventError, match="malformed at line 1"):
        read_and_validate_execution_stream(
            repo_root=fixture["root"],
            dispatch_path=fixture["dispatch_path"],
            reviewed_dispatch_whole_file_sha256=fixture["dispatch_hash"],
        )


def test_retained_history_allows_prefix_growth_and_rejects_delete(fixture):
    start_raw = _write_stream(fixture, [_start(fixture)])
    _commit(fixture["root"], "retain execution start")
    attempt = _attempt(fixture, number=1)
    current_raw = start_raw + serialize_execution_event(attempt)
    fixture["stream_path"].write_bytes(current_raw)

    history = validate_execution_stream_history(
        repo_root=fixture["root"],
        run_id=fixture["dispatch"]["run_binding"]["run_id"],
        stream_path=fixture["dispatch"]["run_binding"]["execution_event_stream_path"],
        current_raw=current_raw,
    )
    assert history["retained_version_count"] == 2

    _commit(fixture["root"], "retain execution prefix growth")
    fixture["stream_path"].unlink()
    _commit(fixture["root"], "delete execution stream")
    with pytest.raises(ExecutionEventError, match="deleted execution stream"):
        read_and_validate_execution_stream(
            repo_root=fixture["root"],
            dispatch_path=fixture["dispatch_path"],
            reviewed_dispatch_whole_file_sha256=fixture["dispatch_hash"],
            allow_missing=True,
        )
    assert "execution_stream_deleted_retained_history" in {
        finding["finding_type"]
        for finding in collect_execution_stream_integrity_findings(repo_root=fixture["root"])
    }


def test_dispatch_must_be_authoritative_consumed_and_exact(fixture):
    alternate = fixture["root"] / "review/dispatch.copy.json"
    alternate.write_bytes(fixture["dispatch_raw"])
    with pytest.raises(ExecutionEventError, match="authoritative"):
        read_and_validate_execution_stream(
            repo_root=fixture["root"],
            dispatch_path=alternate,
            reviewed_dispatch_whole_file_sha256=fixture["dispatch_hash"],
            allow_missing=True,
        )


def test_derived_payload_cannot_override_dispatch_bindings(fixture):
    payload = copy.deepcopy(_start(fixture)["run_start"])
    payload["planned_denominator"] += 1
    with pytest.raises(ExecutionEventError, match="denominator differs"):
        derive_execution_event(
            repo_root=fixture["root"],
            dispatch=fixture["dispatch"],
            dispatch_file_sha256=fixture["dispatch_hash"],
            event_type="run_start",
            sequence_number=1,
            timestamp_utc="2026-07-20T12:00:01Z",
            actor=fixture["actor"],
            payload=payload,
        )
