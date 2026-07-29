import contextlib
import copy
import hashlib
import inspect
import json
import os
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import duckdb
import pytest

from tests import test_dispatch_writer as dispatch_support
from tools.canon_intake import dispatch_writer
from tools.canon_intake import execution_event_writer as writer
from tools.canon_intake.dispatch_authorization import (
    read_and_validate_dispatch_authorization_audit,
    serialize_dispatch_authorization,
)
from tools.canon_intake.execution_event import (
    ExecutionEventError,
    collect_execution_stream_integrity_findings,
    derive_execution_event,
    read_and_validate_execution_stream,
    serialize_execution_event,
)
from tools.research_query import query_layer


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
    stream_relative = dispatch["run_binding"]["execution_event_stream_path"]
    stream_path = prepared["root"] / stream_relative
    stream_path.parent.mkdir(parents=True, exist_ok=True)
    prepared.update(
        {
            "dispatch": dispatch,
            "dispatch_raw": dispatch_raw,
            "dispatch_hash": _hash(dispatch_raw),
            "run_id": dispatch["run_binding"]["run_id"],
            "stream_relative": stream_relative,
            "stream_path": stream_path,
            "actor": {
                "actor_id": "synthetic-operator",
                "tool_name": "synthetic-execution-adapter",
                "tool_version": "test-only-v1",
                "tool_source_path": "tests/test_execution_event_writer.py",
                "tool_source_sha256": "sha256:" + "3" * 64,
            },
        }
    )
    return prepared


def _kwargs(
    fixture: dict,
    *,
    event_type: str,
    event_input: dict,
    timestamp: str,
) -> dict:
    return {
        "repo_root": fixture["root"],
        "dispatch_path": fixture["dispatch_path"],
        "reviewed_dispatch_whole_file_sha256": fixture["dispatch_hash"],
        "run_id": fixture["run_id"],
        "stream_path": fixture["stream_relative"],
        "event_type": event_type,
        "timestamp_utc": timestamp,
        "actor": fixture["actor"],
        "event_input": event_input,
    }


def _start(fixture: dict, *, process_started: bool = True) -> dict:
    return writer.write_execution_event(
        **_kwargs(
            fixture,
            event_type="run_start",
            timestamp="2026-07-20T12:00:01Z",
            event_input={"runner_process_started": process_started},
        )
    )


def _attempt(
    fixture: dict,
    *,
    variant_id: str,
    category: str = "successful",
    reason: str = "completed",
    second: int,
) -> dict:
    return writer.write_execution_event(
        **_kwargs(
            fixture,
            event_type="attempt_outcome",
            timestamp=f"2026-07-20T12:00:{second:02d}Z",
            event_input={
                "variant_id": variant_id,
                "outcome_category": category,
                "reason_code": reason,
            },
        )
    )


def _terminal(
    fixture: dict,
    *,
    state: str = "run_blocked",
    reason: str = "fail_closed_stop_condition",
    process_started: bool = True,
) -> dict:
    return writer.write_execution_event(
        **_kwargs(
            fixture,
            event_type="run_terminal",
            timestamp="2026-07-20T12:01:00Z",
            event_input={
                "terminal_state": state,
                "terminal_reason_code": reason,
                "process_started": process_started,
            },
        )
    )


def _validated(fixture: dict, *, terminal: bool = False) -> dict:
    return read_and_validate_execution_stream(
        repo_root=fixture["root"],
        dispatch_path=fixture["dispatch_path"],
        reviewed_dispatch_whole_file_sha256=fixture["dispatch_hash"],
        require_terminal=terminal,
    )


def test_lawful_start_multiple_attempts_and_terminal_are_exact_and_visible(
    fixture,
):
    start = _start(fixture)
    before_attempt = fixture["stream_path"].read_bytes()
    first = _attempt(
        fixture,
        variant_id="SYNTHETIC-VARIANT-001",
        second=2,
    )
    after_first = fixture["stream_path"].read_bytes()
    second = _attempt(
        fixture,
        variant_id="SYNTHETIC-VARIANT-002",
        category="failed",
        reason="runner_failure",
        second=3,
    )
    terminal = _terminal(fixture)

    result = _validated(fixture, terminal=True)
    assert [
        start["sequence_number"],
        first["sequence_number"],
        second["sequence_number"],
        terminal["sequence_number"],
    ] == [1, 2, 3, 4]
    assert [event["event_type"] for event in result["events"]] == [
        "run_start",
        "attempt_outcome",
        "attempt_outcome",
        "run_terminal",
    ]
    assert after_first.startswith(before_attempt)
    assert fixture["stream_path"].read_bytes().startswith(after_first)
    assert result["raw"] == b"".join(serialize_execution_event(event) for event in result["events"])
    for index, event in enumerate(result["events"], 1):
        assert event["event_id"] == f"EXEC-EVENT-{fixture['run_id']}-{index:06d}"
        assert event["bindings"]["dispatch_record_sha256"] == fixture["dispatch_hash"]
        assert event["stream_path"] == fixture["stream_relative"]
    accounting = result["events"][-1]["run_terminal"]["denominator_accounting"]
    assert accounting["attempts_recorded"] == 2
    assert accounting["outcome_counts"]["successful"] == 1
    assert accounting["outcome_counts"]["failed"] == 1
    assert accounting["not_attempted"] == fixture["dispatch"]["denominator"]["planned"] - 2
    assert result["events"][-1]["run_terminal"]["budget"]["actual"] == 2
    assert collect_execution_stream_integrity_findings(repo_root=fixture["root"]) == []


def test_completed_terminal_requires_every_planned_member_attempted(fixture):
    _start(fixture)
    for number in range(1, fixture["dispatch"]["denominator"]["planned"] + 1):
        _attempt(
            fixture,
            variant_id=f"SYNTHETIC-VARIANT-{number:03d}",
            second=number + 1,
        )
    result = _terminal(
        fixture,
        state="run_completed",
        reason="completed_denominator_accounted",
    )
    assert result["stream_state"] == "terminal"
    terminal = _validated(fixture, terminal=True)["events"][-1]["run_terminal"]
    assert terminal["denominator_accounting"]["not_attempted"] == 0
    assert terminal["budget"]["actual"] == fixture["dispatch"]["denominator"]["planned"]


@pytest.mark.parametrize(
    "action,error",
    [
        ("attempt_first", "only be created by run_start"),
        ("terminal_first", "only be created by run_start"),
        ("duplicate_start", "already exists"),
        ("post_terminal_attempt", "already terminal"),
        ("second_terminal", "already terminal"),
        ("duplicate_variant", "variant ID recurs"),
        ("invalid_reason", "outcome/reason"),
        ("invalid_outcome", "schema validation"),
        ("extra_retry", "unexpected retry_ordinal"),
    ],
)
def test_illegal_event_requests_fail_before_append(fixture, action, error):
    if action == "attempt_first":
        kwargs = _kwargs(
            fixture,
            event_type="attempt_outcome",
            timestamp="2026-07-20T12:00:02Z",
            event_input={
                "variant_id": "SYNTHETIC-VARIANT-001",
                "outcome_category": "successful",
                "reason_code": "completed",
            },
        )
    elif action == "terminal_first":
        kwargs = _kwargs(
            fixture,
            event_type="run_terminal",
            timestamp="2026-07-20T12:00:02Z",
            event_input={
                "terminal_state": "run_blocked",
                "terminal_reason_code": "fail_closed_stop_condition",
                "process_started": False,
            },
        )
    else:
        _start(fixture)
        if action == "duplicate_start":
            kwargs = _kwargs(
                fixture,
                event_type="run_start",
                timestamp="2026-07-20T12:00:02Z",
                event_input={"runner_process_started": True},
            )
        elif action in {"post_terminal_attempt", "second_terminal"}:
            _terminal(fixture)
            if action == "post_terminal_attempt":
                kwargs = _kwargs(
                    fixture,
                    event_type="attempt_outcome",
                    timestamp="2026-07-20T12:02:00Z",
                    event_input={
                        "variant_id": "SYNTHETIC-VARIANT-002",
                        "outcome_category": "successful",
                        "reason_code": "completed",
                    },
                )
            else:
                kwargs = _kwargs(
                    fixture,
                    event_type="run_terminal",
                    timestamp="2026-07-20T12:02:00Z",
                    event_input={
                        "terminal_state": "run_blocked",
                        "terminal_reason_code": "fail_closed_stop_condition",
                        "process_started": True,
                    },
                )
        else:
            _attempt(
                fixture,
                variant_id="SYNTHETIC-VARIANT-001",
                second=2,
            )
            event_input = {
                "variant_id": (
                    "SYNTHETIC-VARIANT-001"
                    if action == "duplicate_variant"
                    else "SYNTHETIC-VARIANT-002"
                ),
                "outcome_category": ("unknown" if action == "invalid_outcome" else "successful"),
                "reason_code": ("execution_error" if action == "invalid_reason" else "completed"),
            }
            if action == "extra_retry":
                event_input["retry_ordinal"] = 1
            kwargs = _kwargs(
                fixture,
                event_type="attempt_outcome",
                timestamp="2026-07-20T12:00:03Z",
                event_input=event_input,
            )
    before = fixture["stream_path"].read_bytes() if fixture["stream_path"].exists() else None
    with pytest.raises(writer.ExecutionEventWriterError, match=error):
        writer.write_execution_event(**kwargs)
    after = fixture["stream_path"].read_bytes() if fixture["stream_path"].exists() else None
    assert after == before


@pytest.mark.parametrize("mutation", ["sequence_gap", "event_id_gap", "malformed_tail"])
def test_existing_gap_or_malformed_tail_remains_visible_and_is_never_repaired(fixture, mutation):
    _start(fixture)
    raw = fixture["stream_path"].read_bytes()
    event = derive_execution_event(
        repo_root=fixture["root"],
        dispatch=fixture["dispatch"],
        dispatch_file_sha256=fixture["dispatch_hash"],
        event_type="attempt_outcome",
        sequence_number=2,
        timestamp_utc="2026-07-20T12:00:02Z",
        actor=fixture["actor"],
        payload={
            "attempt_number": 1,
            "variant_id": "SYNTHETIC-VARIANT-001",
            "retry_ordinal": 0,
            "outcome_category": "successful",
            "reason_code": "completed",
            "counts_toward_budget": True,
            "counts_toward_denominator": True,
        },
    )
    if mutation == "sequence_gap":
        event["sequence_number"] = 3
        event["event_id"] = f"EXEC-EVENT-{fixture['run_id']}-000003"
    elif mutation == "event_id_gap":
        event["event_id"] = f"EXEC-EVENT-{fixture['run_id']}-000003"
    raw += serialize_execution_event(event)
    if mutation == "malformed_tail":
        raw = raw[:-1]
    fixture["stream_path"].write_bytes(raw)
    before = fixture["stream_path"].read_bytes()
    with pytest.raises(writer.ExecutionEventWriterError):
        _attempt(
            fixture,
            variant_id="SYNTHETIC-VARIANT-002",
            second=3,
        )
    assert fixture["stream_path"].read_bytes() == before
    findings = collect_execution_stream_integrity_findings(repo_root=fixture["root"])
    assert [row["finding_type"] for row in findings] == ["execution_stream_malformed"]


@pytest.mark.parametrize(
    "binding",
    [
        "queue",
        "kdauth",
        "lineage",
        "dataset",
        "runner",
        "budget",
        "denominator",
        "output",
    ],
)
def test_drifted_dispatch_bindings_fail_closed_before_append(fixture, binding):
    dispatch = copy.deepcopy(fixture["dispatch"])
    if binding == "queue":
        dispatch["queue_binding"]["raw_sha256"] = "sha256:" + "9" * 64
    elif binding == "kdauth":
        dispatch["dispatch_authorization"]["source_sha256"] = "sha256:" + "9" * 64
    elif binding == "lineage":
        dispatch["artifact_bindings"]["strategy_spec"]["sha256"] = "sha256:" + "9" * 64
    elif binding == "dataset":
        dispatch["dataset_binding"]["sha256"] = "sha256:" + "9" * 64
    elif binding == "runner":
        dispatch["runner_binding"]["source_sha256"] = "sha256:" + "9" * 64
    elif binding == "budget":
        dispatch["budget"]["upper_bound"] += 1
    elif binding == "denominator":
        dispatch["denominator"]["planned"] += 1
    else:
        dispatch["output_targets"]["execution_event_stream_path"] = (
            "research/queue/execution_events/RUN-20260720-DRIFT001.execution_events.jsonl"
        )
    raw = serialize_dispatch_authorization(dispatch)
    fixture["dispatch_path"].write_bytes(raw)
    kwargs = _kwargs(
        fixture,
        event_type="run_start",
        timestamp="2026-07-20T12:00:01Z",
        event_input={"runner_process_started": True},
    )
    kwargs["reviewed_dispatch_whole_file_sha256"] = _hash(raw)
    with pytest.raises(writer.ExecutionEventWriterError):
        writer.write_execution_event(**kwargs)
    assert not fixture["stream_path"].exists()


def test_substituted_hash_path_unconsumed_and_requested_bindings_fail(fixture):
    base = _kwargs(
        fixture,
        event_type="run_start",
        timestamp="2026-07-20T12:00:01Z",
        event_input={"runner_process_started": True},
    )
    cases = []
    wrong_hash = dict(base)
    wrong_hash["reviewed_dispatch_whole_file_sha256"] = "sha256:" + "0" * 64
    cases.append(wrong_hash)
    wrong_run = dict(base)
    wrong_run["run_id"] = "RUN-20260720-WRONG001"
    cases.append(wrong_run)
    wrong_stream = dict(base)
    wrong_stream["stream_path"] = (
        "research/queue/execution_events/RUN-20260720-WRONG001.execution_events.jsonl"
    )
    cases.append(wrong_stream)
    alternate = fixture["root"] / "review/dispatch.copy.json"
    alternate.write_bytes(fixture["dispatch_raw"])
    wrong_path = dict(base)
    wrong_path["dispatch_path"] = alternate
    cases.append(wrong_path)
    for kwargs in cases:
        with pytest.raises(writer.ExecutionEventWriterError):
            writer.write_execution_event(**kwargs)
        assert not fixture["stream_path"].exists()

    rows, _ = read_and_validate_dispatch_authorization_audit(repo_root=fixture["root"])
    fixture["audit_path"].write_bytes(b"".join(raw for _, raw in rows[:-1]))
    with pytest.raises(writer.ExecutionEventWriterError, match="consumed"):
        writer.write_execution_event(**base)
    assert not fixture["stream_path"].exists()


def test_retained_history_collision_or_deletion_blocks_reuse(fixture):
    _start(fixture)
    _commit(fixture["root"], "retain execution start")
    retained_raw = fixture["stream_path"].read_bytes()
    fixture["stream_path"].unlink()
    _commit(fixture["root"], "delete retained execution stream")
    with pytest.raises(writer.ExecutionEventWriterError, match="deleted"):
        writer.write_execution_event(
            **_kwargs(
                fixture,
                event_type="run_start",
                timestamp="2026-07-20T12:00:02Z",
                event_input={"runner_process_started": True},
            )
        )
    assert not fixture["stream_path"].exists()
    assert retained_raw


def _make_directory_redirect(path: Path, destination: Path) -> Path:
    retained = path.with_name(path.name + "-retained")
    try:
        path.rename(retained)
        destination.mkdir()
        if os.name == "nt":
            subprocess.run(
                [
                    "cmd.exe",
                    "/d",
                    "/c",
                    "mklink",
                    "/J",
                    str(path),
                    str(destination),
                ],
                check=True,
                capture_output=True,
            )
        else:
            path.symlink_to(destination, target_is_directory=True)
    except (OSError, subprocess.CalledProcessError) as exc:
        pytest.skip(f"directory redirect unavailable: {exc}")
    return retained


def test_stream_and_lock_parent_redirect_is_rejected(fixture, tmp_path):
    outside = tmp_path / "outside"
    retained = _make_directory_redirect(fixture["stream_path"].parent, outside)
    with pytest.raises(writer.ExecutionEventWriterError):
        _start(fixture)
    assert list(outside.iterdir()) == []
    assert not list(retained.glob("*.execution_events.jsonl"))


def test_lock_parent_redirect_is_rejected_without_outside_write(fixture, tmp_path):
    lock_parent = fixture["root"] / writer.LOCK_ROOT
    outside = tmp_path / "outside-lock"
    retained = _make_directory_redirect(lock_parent, outside)
    with pytest.raises(writer.ExecutionEventWriterError):
        _start(fixture)
    assert list(outside.iterdir()) == []
    assert not list(retained.glob(".*.execution_event_append.lock"))


def test_post_preflight_pre_anchor_parent_substitution_cannot_redirect_append(
    fixture,
    tmp_path,
    monkeypatch,
):
    real_preflight = writer._preflight
    outside = tmp_path / "outside-race"
    retained = None

    def substitute_after_preflight(**kwargs):
        nonlocal retained
        result = real_preflight(**kwargs)
        retained = _make_directory_redirect(fixture["stream_path"].parent, outside)
        return result

    monkeypatch.setattr(writer, "_preflight", substitute_after_preflight)
    with pytest.raises(writer.ExecutionEventWriterError):
        _start(fixture)
    assert retained is not None
    assert list(outside.iterdir()) == []
    assert not list(retained.glob("*.execution_events.jsonl"))


@pytest.mark.parametrize(
    ("substitution_target", "expected_failure_phase"),
    [
        ("execution stream parent", "append_or_durability"),
        ("execution append lock parent", "lock_cleanup"),
    ],
    ids=["stream-parent", "lock-parent"],
)
def test_post_anchor_post_validation_parent_substitution_fails_closed(
    fixture,
    tmp_path,
    monkeypatch,
    substitution_target,
    expected_failure_phase,
):
    _start(fixture)
    _commit(fixture["root"], "retain execution start before parent substitution")
    before = fixture["stream_path"].read_bytes()
    lock_parent_path = fixture["root"] / writer.LOCK_ROOT
    substitution_path = (
        fixture["stream_path"].parent
        if substitution_target == "execution stream parent"
        else lock_parent_path
    )
    outside = tmp_path / (
        "outside-stream-parent"
        if substitution_target == "execution stream parent"
        else "outside-lock-parent"
    )
    trace = {
        "candidate_derivations": 0,
        "currentness_checks": {},
        "substitution_timing": None,
        "retained_parent": None,
        "append_started": False,
        "append_completed": False,
    }
    real_derive = writer._derive_candidate
    real_assert_current = writer._AnchoredDirectory.assert_current
    real_verify_reference = writer._AnchoredDirectory.verify_reference
    real_write_all = writer._write_all

    def track_candidate_derivation(**kwargs):
        result = real_derive(**kwargs)
        trace["candidate_derivations"] += 1
        return result

    def track_currentness(self):
        result = real_assert_current(self)
        checks = trace["currentness_checks"]
        checks[self.label] = checks.get(self.label, 0) + 1
        return result

    def substitute_after_pre_mutation_checks(self, name, **kwargs):
        result = real_verify_reference(self, name, **kwargs)
        if self.label == "authoritative dispatch parent" and trace["substitution_timing"] is None:
            assert trace["candidate_derivations"] == 2
            assert trace["currentness_checks"]["execution stream parent"] == 1
            assert trace["currentness_checks"]["authoritative dispatch parent"] == 1
            assert trace["currentness_checks"]["execution append lock parent"] == 3
            assert (
                lock_parent_path / f".{fixture['run_id']}.execution_event_append.lock"
            ).is_file()
            trace["retained_parent"] = _make_directory_redirect(
                substitution_path,
                outside,
            )
            trace["substitution_timing"] = (
                "after locked validation, candidate derivation, and all "
                "pre-mutation parent-currentness checks; before stream "
                "verification and append"
            )
        return result

    def observe_real_append(fd, raw):
        if raw.startswith(b'{"actor"'):
            trace["append_started"] = True
            result = real_write_all(fd, raw)
            trace["append_completed"] = True
            return result
        return real_write_all(fd, raw)

    monkeypatch.setattr(writer, "_derive_candidate", track_candidate_derivation)
    monkeypatch.setattr(
        writer._AnchoredDirectory,
        "assert_current",
        track_currentness,
    )
    monkeypatch.setattr(
        writer._AnchoredDirectory,
        "verify_reference",
        substitute_after_pre_mutation_checks,
    )
    monkeypatch.setattr(writer, "_write_all", observe_real_append)

    with pytest.raises(writer.ExecutionEventWriterIntegrityCriticalError) as caught:
        _attempt(
            fixture,
            variant_id="SYNTHETIC-VARIANT-001",
            second=2,
        )

    assert caught.value.failure_phase == expected_failure_phase
    assert caught.value.stream_may_have_changed is True
    assert caught.value.event_durable is False
    assert trace["substitution_timing"] is not None
    assert trace["append_started"] is True
    assert trace["append_completed"] is True
    retained_parent = trace["retained_parent"]
    assert retained_parent is not None
    physical_stream = retained_parent / fixture["stream_path"].relative_to(substitution_path)
    after = physical_stream.read_bytes()
    assert after.startswith(before)
    assert len(after) > len(before)
    assert json.loads(after.splitlines()[-1])["event_type"] == "attempt_outcome"
    assert list(outside.iterdir()) == []
    assert substitution_path.resolve() == outside.resolve()
    assert substitution_path.is_dir()
    assert retained_parent.is_dir()

    with pytest.raises(ExecutionEventError, match="symlink or reparse") as direct:
        _validated(fixture)
    with pytest.raises(ExecutionEventError, match="symlink or reparse") as findings:
        collect_execution_stream_integrity_findings(repo_root=fixture["root"])
    monkeypatch.setattr(query_layer, "REPO_ROOT", fixture["root"])
    conn = duckdb.connect(database=":memory:")
    try:
        with pytest.raises(ExecutionEventError, match="symlink or reparse") as query:
            query_layer._register_execution_stream_integrity_findings(conn)
    finally:
        conn.close()
    assert str(direct.value)
    assert str(findings.value)
    assert str(query.value)
    assert list(outside.iterdir()) == []


def test_dispatch_drift_after_lock_acquisition_fails_before_append(fixture, monkeypatch):
    real_lock = writer._run_append_lock

    @contextlib.contextmanager
    def drift_inside_lock(**kwargs):
        with real_lock(**kwargs) as held:
            fixture["dispatch_path"].write_bytes(fixture["dispatch_raw"] + b" ")
            yield held

    monkeypatch.setattr(writer, "_run_append_lock", drift_inside_lock)
    with pytest.raises(writer.ExecutionEventWriterError):
        _start(fixture)
    assert not fixture["stream_path"].exists()


def test_partial_append_is_integrity_critical_preserved_and_visible(fixture, monkeypatch):
    _start(fixture)
    before = fixture["stream_path"].read_bytes()
    real_write = writer._write_all

    def partial_event(fd, raw):
        if raw.startswith(b'{"actor"'):
            os.write(fd, raw[:19])
            raise OSError("synthetic partial append")
        return real_write(fd, raw)

    monkeypatch.setattr(writer, "_write_all", partial_event)
    with pytest.raises(writer.ExecutionEventWriterIntegrityCriticalError):
        _attempt(
            fixture,
            variant_id="SYNTHETIC-VARIANT-001",
            second=2,
        )
    assert fixture["stream_path"].read_bytes().startswith(before)
    assert fixture["stream_path"].read_bytes() != before
    assert [
        row["finding_type"]
        for row in collect_execution_stream_integrity_findings(repo_root=fixture["root"])
    ] == ["execution_stream_malformed"]


def test_preserved_malformed_tail_remains_visible_in_sql_integrity_view(fixture, monkeypatch):
    _start(fixture)
    fixture["stream_path"].write_bytes(fixture["stream_path"].read_bytes() + b"{")
    monkeypatch.setattr(query_layer, "REPO_ROOT", fixture["root"])
    conn = duckdb.connect(database=":memory:")
    query_layer._register_execution_stream_integrity_findings(conn)
    rows = conn.execute(
        "SELECT finding_type, stream_state FROM execution_stream_integrity_findings"
    ).fetchall()
    conn.close()
    assert rows == [("execution_stream_malformed", "invalid")]


@pytest.mark.parametrize("failure", ["file_fsync", "parent_fsync", "reread", "validator"])
def test_durability_or_validation_uncertainty_never_reports_success(fixture, monkeypatch, failure):
    _start(fixture)
    before = fixture["stream_path"].read_bytes()
    if failure == "file_fsync":
        real_fsync = writer._AnchoredFile.fsync

        def fail_stream_fsync(self):
            if self.name.endswith(".execution_events.jsonl"):
                raise OSError("synthetic stream fsync uncertainty")
            return real_fsync(self)

        monkeypatch.setattr(writer._AnchoredFile, "fsync", fail_stream_fsync)
    elif failure == "parent_fsync":
        real_parent_fsync = writer._AnchoredDirectory.fsync

        def fail_parent_fsync(self):
            if self.label == "execution stream parent":
                raise OSError("synthetic parent fsync uncertainty")
            return real_parent_fsync(self)

        monkeypatch.setattr(writer._AnchoredDirectory, "fsync", fail_parent_fsync)
    elif failure == "reread":
        real_verify = writer._AnchoredDirectory.verify_reference
        stream_verifications = 0

        def fail_stream_reread(self, name, **kwargs):
            nonlocal stream_verifications
            if name.endswith(".execution_events.jsonl"):
                stream_verifications += 1
                if stream_verifications == 2:
                    raise OSError("synthetic stream reread uncertainty")
            return real_verify(self, name, **kwargs)

        monkeypatch.setattr(
            writer._AnchoredDirectory,
            "verify_reference",
            fail_stream_reread,
        )
    else:
        real_validate = writer.read_and_validate_execution_stream
        calls = 0

        def fail_post_append(**kwargs):
            nonlocal calls
            calls += 1
            if calls == 3:
                raise ExecutionEventError("synthetic post-append validator uncertainty")
            return real_validate(**kwargs)

        monkeypatch.setattr(writer, "read_and_validate_execution_stream", fail_post_append)
    with pytest.raises(writer.ExecutionEventWriterIntegrityCriticalError):
        _attempt(
            fixture,
            variant_id="SYNTHETIC-VARIANT-001",
            second=2,
        )
    assert fixture["stream_path"].read_bytes().startswith(before)


def test_lock_cleanup_uncertainty_never_returns_success(fixture, monkeypatch):
    real_delete = writer._AnchoredFile.delete

    def fail_lock_delete(self):
        if self.name.endswith(".execution_event_append.lock"):
            raise OSError("synthetic lock cleanup uncertainty")
        return real_delete(self)

    monkeypatch.setattr(writer._AnchoredFile, "delete", fail_lock_delete)
    with pytest.raises(
        writer.ExecutionEventWriterIntegrityCriticalError,
        match="lock cleanup",
    ) as caught:
        _start(fixture)
    assert caught.value.event_durable is True
    assert _validated(fixture)["events"][0]["event_type"] == "run_start"
    assert (
        fixture["root"] / writer.LOCK_ROOT / f".{fixture['run_id']}.execution_event_append.lock"
    ).is_file()


def test_concurrent_appenders_leave_only_one_lawful_next_event(fixture):
    _start(fixture)
    kwargs = _kwargs(
        fixture,
        event_type="attempt_outcome",
        timestamp="2026-07-20T12:00:02Z",
        event_input={
            "variant_id": "SYNTHETIC-VARIANT-001",
            "outcome_category": "successful",
            "reason_code": "completed",
        },
    )

    def run():
        try:
            return ("ok", writer.write_execution_event(**kwargs))
        except writer.ExecutionEventWriterError as exc:
            return ("stopped", str(exc))

    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(lambda _: run(), range(2)))
    assert [status for status, _ in outcomes].count("ok") == 1
    assert [status for status, _ in outcomes].count("stopped") == 1
    result = _validated(fixture)
    assert [event["sequence_number"] for event in result["events"]] == [1, 2]
    assert result["events"][1]["attempt_outcome"]["attempt_number"] == 1


def test_cli_matches_api_and_writer_has_no_runner_or_subprocess_dependency(
    fixture,
):
    command = [
        sys.executable,
        "-m",
        "tools.canon_intake.execution_event_writer",
        "--repo-root",
        str(fixture["root"]),
        "--dispatch",
        str(fixture["dispatch_path"]),
        "--reviewed-dispatch-whole-file-sha256",
        fixture["dispatch_hash"],
        "--run-id",
        fixture["run_id"],
        "--stream-path",
        fixture["stream_relative"],
        "--event-type",
        "run_start",
        "--timestamp-utc",
        "2026-07-20T12:00:01Z",
        "--actor-json",
        json.dumps(fixture["actor"]),
        "--event-input-json",
        json.dumps({"runner_process_started": True}),
    ]
    completed = subprocess.run(
        command,
        cwd=Path(__file__).resolve().parents[1],
        check=True,
        capture_output=True,
        text=True,
    )
    result = json.loads(completed.stdout)
    assert result["event_appended"] is True
    assert result["sequence_number"] == 1
    source = inspect.getsource(writer)
    assert "tools.research_runner" not in source
    assert "subprocess" not in source
    assert "result_population" not in source.lower().replace(
        "does_not_create_result_population",
        "",
    )
