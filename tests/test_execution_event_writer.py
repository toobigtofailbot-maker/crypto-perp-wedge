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
    EXECUTION_WRITER_INTEGRITY_ROOT,
    EXECUTION_WRITER_MUTATION_RESERVED,
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
    (prepared["root"] / EXECUTION_WRITER_INTEGRITY_ROOT).mkdir(
        parents=True,
        exist_ok=True,
    )
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
    audit_root = fixture["root"] / EXECUTION_WRITER_INTEGRITY_ROOT
    reservations = sorted(audit_root.glob("*.execution_writer_visibility_reservation.json"))
    durable_proofs = sorted(audit_root.glob("*.execution_writer_event_durable.json"))
    assert len(reservations) == 4
    assert len(durable_proofs) == 4
    retained_marker_bytes = {path: path.read_bytes() for path in [*reservations, *durable_proofs]}
    assert collect_execution_stream_integrity_findings(repo_root=fixture["root"]) == []
    assert {path: path.read_bytes() for path in retained_marker_bytes} == retained_marker_bytes


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


def _assert_redirect_remains_integrity_visible(
    fixture,
    monkeypatch,
    *,
    durable_combined_uncertainty: bool = False,
) -> None:
    with pytest.raises(ExecutionEventError, match="symlink or reparse") as direct:
        _validated(fixture)
    monkeypatch.setattr(query_layer, "REPO_ROOT", fixture["root"])
    conn = duckdb.connect(database=":memory:")
    try:
        if durable_combined_uncertainty:
            findings = collect_execution_stream_integrity_findings(repo_root=fixture["root"])
            query_layer._register_execution_stream_integrity_findings(conn)
            query_types = {
                row[0]
                for row in conn.execute(
                    "SELECT finding_type FROM execution_stream_integrity_findings"
                ).fetchall()
            }
            expected = {
                "execution_writer_append_or_durability_uncertain",
                "execution_writer_lock_cleanup_also_uncertain",
            }
            assert expected <= {row["finding_type"] for row in findings}
            assert expected <= query_types
        else:
            with pytest.raises(
                ExecutionEventError,
                match="symlink or reparse",
            ) as findings:
                collect_execution_stream_integrity_findings(repo_root=fixture["root"])
            with pytest.raises(
                ExecutionEventError,
                match="symlink or reparse",
            ) as query:
                query_layer._register_execution_stream_integrity_findings(conn)
            assert str(findings.value)
            assert str(query.value)
    finally:
        conn.close()
    assert str(direct.value)


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
    ("substitution_target", "lock_cleanup_also_uncertain"),
    [
        ("execution stream parent", False),
        ("execution append lock parent", True),
    ],
    ids=["stream-parent", "lock-parent"],
)
def test_pre_append_post_anchor_parent_substitution_preserves_primary_precedence(
    fixture,
    tmp_path,
    monkeypatch,
    substitution_target,
    lock_cleanup_also_uncertain,
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
        "lock_cleanup_started": False,
        "lock_cleanup_completed": False,
    }
    real_derive = writer._derive_candidate
    real_assert_current = writer._AnchoredDirectory.assert_current
    real_verify_reference = writer._AnchoredDirectory.verify_reference
    real_write_all = writer._write_all
    real_delete = writer._AnchoredFile.delete

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

    def observe_real_cleanup(self):
        if self.name.endswith(".execution_event_append.lock"):
            trace["lock_cleanup_started"] = True
            result = real_delete(self)
            trace["lock_cleanup_completed"] = True
            return result
        raise AssertionError(f"unexpected protected cleanup target: {self.name}")

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
    monkeypatch.setattr(writer._AnchoredFile, "delete", observe_real_cleanup)

    with pytest.raises(writer.ExecutionEventWriterIntegrityCriticalError) as caught:
        _attempt(
            fixture,
            variant_id="SYNTHETIC-VARIANT-001",
            second=2,
        )

    assert caught.value.failure_phase == "append_or_durability"
    assert caught.value.uncertainty_class == "append_or_durability_uncertain"
    assert caught.value.stream_may_have_changed is True
    assert caught.value.event_durable is False
    assert caught.value.lock_cleanup_also_uncertain is lock_cleanup_also_uncertain
    assert str(caught.value)
    assert trace["candidate_derivations"] == 2
    assert trace["substitution_timing"] is not None
    assert trace["append_started"] is True
    assert trace["append_completed"] is True
    assert trace["lock_cleanup_started"] is True
    assert trace["lock_cleanup_completed"] is True
    retained_parent = trace["retained_parent"]
    assert retained_parent is not None
    physical_stream = (
        retained_parent / fixture["stream_path"].name
        if substitution_target == "execution stream parent"
        else fixture["stream_path"]
    )
    after = physical_stream.read_bytes()
    assert after.startswith(before)
    assert len(after) > len(before)
    assert json.loads(after.splitlines()[-1])["event_type"] == "attempt_outcome"
    assert list(outside.iterdir()) == []
    assert substitution_path.resolve() == outside.resolve()
    assert substitution_path.is_dir()
    assert retained_parent.is_dir()
    assert not list(
        retained_parent.glob(".*.execution_event_append.lock")
        if substitution_target == "execution append lock parent"
        else ()
    )
    if lock_cleanup_also_uncertain:
        assert caught.value.integrity_visibility_recorded is True
        assert caught.value.integrity_visibility_record_uncertain is False
        record_path = fixture["root"] / (caught.value.integrity_visibility_record_path)
        record = json.loads(record_path.read_text(encoding="utf-8"))
        assert record["primary_failure_phase"] == "append_or_durability"
        assert record["event_durable"] is False
        assert record["stream_may_have_changed"] is True
        assert record["lock_cleanup_also_uncertain"] is True
    _assert_redirect_remains_integrity_visible(
        fixture,
        monkeypatch,
        durable_combined_uncertainty=lock_cleanup_also_uncertain,
    )
    assert list(outside.iterdir()) == []


def _install_combined_uncertainty_currentness_failures(monkeypatch):
    trace = {"lock_currentness_checks": 0}
    real_assert_current = writer._AnchoredDirectory.assert_current

    def fail_post_append_and_post_cleanup_currentness(self):
        if self.label == "execution append lock parent":
            trace["lock_currentness_checks"] += 1
            if trace["lock_currentness_checks"] in {4, 5}:
                raise OSError("synthetic execution append lock parent currentness failure")
        return real_assert_current(self)

    monkeypatch.setattr(
        writer._AnchoredDirectory,
        "assert_current",
        fail_post_append_and_post_cleanup_currentness,
    )
    return trace


def _writer_uncertainty_rows(fixture):
    expected_types = {
        "execution_writer_append_or_durability_uncertain",
        "execution_writer_lock_cleanup_also_uncertain",
    }
    findings = collect_execution_stream_integrity_findings(repo_root=fixture["root"])
    rows = [row for row in findings if row["finding_type"] in expected_types]
    assert {row["finding_type"] for row in rows} == expected_types
    assert all(row["stream_state"] == "integrity_critical" for row in rows)
    assert all(row["operator_inspection_required"] for row in rows)
    assert all(row["non_authority"] for row in rows)
    return rows


def test_combined_uncertainty_is_durable_and_query_visible_cross_platform(
    fixture,
    monkeypatch,
):
    _start(fixture)
    before = fixture["stream_path"].read_bytes()
    trace = {
        "lock_currentness_checks": 0,
        "candidate_derivations": 0,
        "event_writes": 0,
        "lock_deletes": 0,
    }
    real_assert_current = writer._AnchoredDirectory.assert_current
    real_derive = writer._derive_candidate
    real_write_all = writer._write_all
    real_delete = writer._AnchoredFile.delete

    def fail_post_append_and_post_cleanup_currentness(self):
        if self.label == "execution append lock parent":
            trace["lock_currentness_checks"] += 1
            if trace["lock_currentness_checks"] in {4, 5}:
                raise OSError("synthetic execution append lock parent currentness failure")
        return real_assert_current(self)

    def observe_candidate(**kwargs):
        result = real_derive(**kwargs)
        trace["candidate_derivations"] += 1
        return result

    def observe_writes(fd, raw):
        if raw.startswith(b'{"actor"'):
            trace["event_writes"] += 1
        return real_write_all(fd, raw)

    def observe_cleanup(self):
        if not self.name.endswith(".execution_event_append.lock"):
            raise AssertionError(f"unexpected protected cleanup target: {self.name}")
        trace["lock_deletes"] += 1
        return real_delete(self)

    def forbid_truncate(self, length):
        raise AssertionError(f"execution writer attempted forbidden truncate to {length}")

    monkeypatch.setattr(
        writer._AnchoredDirectory,
        "assert_current",
        fail_post_append_and_post_cleanup_currentness,
    )
    monkeypatch.setattr(writer, "_derive_candidate", observe_candidate)
    monkeypatch.setattr(writer, "_write_all", observe_writes)
    monkeypatch.setattr(writer._AnchoredFile, "delete", observe_cleanup)
    monkeypatch.setattr(writer._AnchoredFile, "truncate", forbid_truncate)

    with pytest.raises(writer.ExecutionEventWriterIntegrityCriticalError) as caught:
        _attempt(
            fixture,
            variant_id="SYNTHETIC-VARIANT-001",
            second=2,
        )

    error = caught.value
    assert error.failure_phase == "append_or_durability"
    assert error.uncertainty_class == "append_or_durability_uncertain"
    assert error.event_durable is False
    assert error.stream_may_have_changed is True
    assert error.lock_cleanup_also_uncertain is True
    assert error.integrity_visibility_recorded is True
    assert error.integrity_visibility_record_uncertain is False
    assert trace == {
        "lock_currentness_checks": 5,
        "candidate_derivations": 2,
        "event_writes": 1,
        "lock_deletes": 1,
    }
    after = fixture["stream_path"].read_bytes()
    assert after.startswith(before)
    assert json.loads(after.splitlines()[-1])["event_type"] == "attempt_outcome"
    assert not (
        fixture["root"] / writer.LOCK_ROOT / f".{fixture['run_id']}.execution_event_append.lock"
    ).exists()

    record_path = fixture["root"] / error.integrity_visibility_record_path
    record_raw = record_path.read_bytes()
    record = json.loads(record_raw)
    assert record_raw.endswith(b"\n")
    assert record == {
        "schema_version": "canon_execution_writer_integrity_visibility_v1",
        "record_kind": "append_or_durability_and_lock_cleanup_uncertain",
        "writer_identity": writer.WRITER_IDENTITY,
        "dispatch_id": fixture["dispatch"]["dispatch_id"],
        "dispatch_path": fixture["dispatch"]["dispatch_record_path"],
        "run_id": fixture["run_id"],
        "execution_event_stream_path": fixture["stream_relative"],
        "event_id": f"EXEC-EVENT-{fixture['run_id']}-000002",
        "event_sequence_number": 2,
        "primary_failure_phase": "append_or_durability",
        "primary_uncertainty_class": "append_or_durability_uncertain",
        "event_durable": False,
        "stream_may_have_changed": True,
        "lock_cleanup_also_uncertain": True,
        "operator_inspection_required": True,
        "non_authority": True,
    }

    expected_types = {
        "execution_writer_append_or_durability_uncertain",
        "execution_writer_lock_cleanup_also_uncertain",
    }
    findings = collect_execution_stream_integrity_findings(repo_root=fixture["root"])
    finding_types = {row["finding_type"] for row in findings}
    assert expected_types <= finding_types
    assert "execution_stream_incomplete" in finding_types
    uncertainty_rows = [row for row in findings if row["finding_type"] in expected_types]
    assert all(row["stream_state"] == "integrity_critical" for row in uncertainty_rows)
    assert all(row["operator_inspection_required"] for row in uncertainty_rows)
    assert all(row["non_authority"] for row in uncertainty_rows)

    monkeypatch.setattr(query_layer, "REPO_ROOT", fixture["root"])
    conn = duckdb.connect(database=":memory:")
    try:
        query_layer._register_execution_stream_integrity_findings(conn)
        query_rows = conn.execute(
            "SELECT finding_type, stream_state "
            "FROM execution_stream_integrity_findings "
            "WHERE finding_type LIKE 'execution_writer_%'"
        ).fetchall()
    finally:
        conn.close()
    assert set(query_rows) == {
        (
            "execution_writer_append_or_durability_uncertain",
            "integrity_critical",
        ),
        (
            "execution_writer_lock_cleanup_also_uncertain",
            "integrity_critical",
        ),
    }


def test_process_stop_before_final_incident_creation_retains_read_only_evidence(
    fixture,
    monkeypatch,
):
    class SimulatedProcessStop(BaseException):
        pass

    _start(fixture)
    trace = _install_combined_uncertainty_currentness_failures(monkeypatch)
    final_record_attempted = False

    def stop_before_final_create(*, integrity_parent, state):
        nonlocal final_record_attempted
        final_record_attempted = True
        assert state["append_started"] is True
        assert state["event_durable"] is False
        raise SimulatedProcessStop("synthetic stop before final incident create")

    monkeypatch.setattr(writer, "_write_combined_uncertainty_record", stop_before_final_create)

    with pytest.raises(SimulatedProcessStop):
        _attempt(
            fixture,
            variant_id="SYNTHETIC-VARIANT-001",
            second=2,
        )

    assert final_record_attempted is True
    assert trace["lock_currentness_checks"] == 5
    final_name = writer.execution_writer_integrity_record_name(
        run_id=fixture["run_id"],
        event_sequence_number=2,
    )
    reservation_name = writer.execution_writer_visibility_marker_name(
        run_id=fixture["run_id"],
        event_sequence_number=2,
        record_kind=EXECUTION_WRITER_MUTATION_RESERVED,
    )
    audit_root = fixture["root"] / EXECUTION_WRITER_INTEGRITY_ROOT
    assert not (audit_root / final_name).exists()
    reservation_path = audit_root / reservation_name
    reservation_raw = reservation_path.read_bytes()

    rows = _writer_uncertainty_rows(fixture)

    assert reservation_path.read_bytes() == reservation_raw
    assert all("reservation" in row["reason"] for row in rows)
    assert all("durable incident record" not in row["reason"] for row in rows)
    monkeypatch.setattr(query_layer, "REPO_ROOT", fixture["root"])
    conn = duckdb.connect(database=":memory:")
    try:
        query_layer._register_execution_stream_integrity_findings(conn)
        query_types = {
            row[0]
            for row in conn.execute(
                "SELECT finding_type FROM execution_stream_integrity_findings "
                "WHERE finding_type LIKE 'execution_writer_%'"
            ).fetchall()
        }
    finally:
        conn.close()
    assert query_types == {
        "execution_writer_append_or_durability_uncertain",
        "execution_writer_lock_cleanup_also_uncertain",
    }


@pytest.mark.parametrize("final_failure", ["audit_parent_currentness", "exclusive_create"])
def test_final_incident_create_failure_uses_retained_reservation_evidence(
    fixture,
    monkeypatch,
    final_failure,
):
    _start(fixture)
    trace = _install_combined_uncertainty_currentness_failures(monkeypatch)
    real_combined_record = writer._write_combined_uncertainty_record
    real_assert_current = writer._AnchoredDirectory.assert_current
    real_create = writer._AnchoredDirectory.create
    final_record_started = False

    def observe_final_record(**kwargs):
        nonlocal final_record_started
        final_record_started = True
        return real_combined_record(**kwargs)

    def fail_final_currentness(self):
        if (
            final_failure == "audit_parent_currentness"
            and final_record_started
            and self.label == "execution-writer integrity parent"
        ):
            raise OSError("synthetic final incident audit-parent currentness failure")
        return real_assert_current(self)

    def fail_final_create(self, name):
        if final_failure == "exclusive_create" and name.endswith(
            ".execution_writer_integrity.json"
        ):
            raise OSError("synthetic final incident exclusive-create failure")
        return real_create(self, name)

    monkeypatch.setattr(writer, "_write_combined_uncertainty_record", observe_final_record)
    monkeypatch.setattr(writer._AnchoredDirectory, "assert_current", fail_final_currentness)
    monkeypatch.setattr(writer._AnchoredDirectory, "create", fail_final_create)

    with pytest.raises(writer.ExecutionEventWriterIntegrityCriticalError) as caught:
        _attempt(
            fixture,
            variant_id="SYNTHETIC-VARIANT-001",
            second=2,
        )

    error = caught.value
    assert error.failure_phase == "append_or_durability"
    assert error.event_durable is False
    assert error.stream_may_have_changed is True
    assert error.lock_cleanup_also_uncertain is True
    assert error.integrity_visibility_recorded is False
    assert error.integrity_visibility_record_uncertain is True
    assert final_record_started is True
    assert trace["lock_currentness_checks"] == 5
    final_path = fixture["root"] / error.integrity_visibility_record_path
    assert not final_path.exists()
    rows = _writer_uncertainty_rows(fixture)
    assert all("reservation" in row["reason"] for row in rows)


def test_post_proof_lock_parent_substitution_reports_real_cleanup_uncertainty(
    fixture,
    tmp_path,
    monkeypatch,
):
    _start(fixture)
    _commit(fixture["root"], "retain execution start before cleanup substitution")
    before = fixture["stream_path"].read_bytes()
    lock_parent_path = fixture["root"] / writer.LOCK_ROOT
    outside = tmp_path / "outside-lock-cleanup"
    trace = {
        "append_calls": 0,
        "event_writes": 0,
        "substitution_timing": None,
        "retained_parent": None,
        "lock_cleanup_started": False,
        "lock_cleanup_completed": False,
    }
    real_append = writer._append_under_lock
    real_write_all = writer._write_all
    real_delete = writer._AnchoredFile.delete

    def append_then_substitute(**kwargs):
        trace["append_calls"] += 1
        result = real_append(**kwargs)
        assert kwargs["state"]["event_durable"] is True
        assert trace["event_writes"] == 1
        trace["retained_parent"] = _make_directory_redirect(
            lock_parent_path,
            outside,
        )
        trace["substitution_timing"] = (
            "after append, fsync, reread, completed-stream validation, "
            "post-append anchor proof, and event_durable=true; before real "
            "lock cleanup"
        )
        return result

    def observe_real_append(fd, raw):
        if raw.startswith(b'{"actor"'):
            trace["event_writes"] += 1
        return real_write_all(fd, raw)

    def observe_real_cleanup(self):
        if self.name.endswith(".execution_event_append.lock"):
            trace["lock_cleanup_started"] = True
            result = real_delete(self)
            trace["lock_cleanup_completed"] = True
            return result
        raise AssertionError(f"unexpected protected cleanup target: {self.name}")

    monkeypatch.setattr(writer, "_append_under_lock", append_then_substitute)
    monkeypatch.setattr(writer, "_write_all", observe_real_append)
    monkeypatch.setattr(writer._AnchoredFile, "delete", observe_real_cleanup)

    with pytest.raises(writer.ExecutionEventWriterIntegrityCriticalError) as caught:
        _attempt(
            fixture,
            variant_id="SYNTHETIC-VARIANT-001",
            second=2,
        )

    assert caught.value.failure_phase == "lock_cleanup"
    assert caught.value.uncertainty_class == "lock_cleanup_uncertain"
    assert caught.value.stream_may_have_changed is True
    assert caught.value.event_durable is True
    assert caught.value.lock_cleanup_also_uncertain is False
    assert trace["append_calls"] == 1
    assert trace["event_writes"] == 1
    assert trace["substitution_timing"] is not None
    assert trace["lock_cleanup_started"] is True
    assert trace["lock_cleanup_completed"] is True
    retained_parent = trace["retained_parent"]
    assert retained_parent is not None
    after = fixture["stream_path"].read_bytes()
    assert after.startswith(before)
    assert len(after) > len(before)
    assert json.loads(after.splitlines()[-1])["event_type"] == "attempt_outcome"
    assert not list(retained_parent.glob(".*.execution_event_append.lock"))
    assert list(outside.iterdir()) == []
    assert lock_parent_path.resolve() == outside.resolve()
    assert lock_parent_path.is_dir()
    assert retained_parent.is_dir()
    _assert_redirect_remains_integrity_visible(fixture, monkeypatch)
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
    finding_types = {
        row["finding_type"]
        for row in collect_execution_stream_integrity_findings(repo_root=fixture["root"])
    }
    assert finding_types == {
        "execution_stream_malformed",
        "execution_writer_append_or_durability_uncertain",
    }


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
    assert caught.value.failure_phase == "lock_cleanup"
    assert caught.value.stream_may_have_changed is True
    assert caught.value.event_durable is True
    assert caught.value.lock_cleanup_also_uncertain is False
    assert _validated(fixture)["events"][0]["event_type"] == "run_start"
    assert not list(
        (fixture["root"] / EXECUTION_WRITER_INTEGRITY_ROOT).glob(
            "*.execution_writer_integrity.json"
        )
    )
    assert not {
        row["finding_type"]
        for row in collect_execution_stream_integrity_findings(repo_root=fixture["root"])
        if row["finding_type"].startswith("execution_writer_")
    }
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
