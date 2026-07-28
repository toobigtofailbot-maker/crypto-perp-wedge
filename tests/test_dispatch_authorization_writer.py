import copy
import hashlib
import json
import os
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from tests import test_dispatch_authorization as authorization_support
from tools.canon_intake import dispatch_authorization as authorization
from tools.canon_intake import dispatch_authorization_reservation as reservation
from tools.canon_intake import dispatch_authorization_writer as writer
from tools.canon_intake.dispatch_authorization import (
    DispatchAuthorizationError,
    collect_dispatch_without_consumption_findings,
    repo_canonical_json_v1,
    serialize_dispatch_authorization,
    validate_dispatch_authorization,
    validate_dispatch_authorization_candidate,
    validate_dispatch_record_for_authorization,
)
from tools.canon_intake.dispatch_manifest import derive_dispatch_record


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


def _remove_readonly(function, path, exc_info):
    del exc_info
    os.chmod(path, 0o700)
    function(path)


def prepared_fixture(tmp_path: Path, source_repo: Path) -> dict:
    fixture = authorization_support._fixture(
        tmp_path,
        source_repo,
        reservation_state="none",
    )
    dispatch_schema = source_repo / "research/schemas/canon_dispatch_record.schema.json"
    shutil.copy2(
        dispatch_schema,
        fixture["root"] / "research/schemas" / dispatch_schema.name,
    )
    proposal = fixture["root"] / "review/kdauth.review.json"
    proposal.parent.mkdir(parents=True)
    proposal.write_bytes(fixture["authorization_raw"])
    fixture["proposal_path"] = proposal
    fixture["authorization_path"].unlink()
    fixture["audit_path"].unlink()
    shutil.rmtree(fixture["root"] / ".git", onerror=_remove_readonly)
    _git(fixture["root"], "init", "-q")
    _commit(fixture["root"], "synthetic pre-crossing dependencies")
    return fixture


@pytest.fixture
def source_repo() -> Path:
    return Path(__file__).resolve().parents[1]


@pytest.fixture
def fixture(tmp_path: Path, source_repo: Path) -> dict:
    return prepared_fixture(tmp_path, source_repo)


def _attempt_id(token: str) -> str:
    date = datetime.now(timezone.utc).strftime("%Y%m%d")
    return f"KDAUTH-XING-{date}-{token}"


def _make_directory_redirect(path: Path, destination: Path) -> None:
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


def _replace_directory_with_redirect(
    path: Path,
    destination: Path,
) -> Path:
    retained = path.with_name(path.name + "-retained")
    path.rename(retained)
    destination.mkdir()
    _make_directory_redirect(path, destination)
    return retained


def cross(fixture: dict, token: str = "WRITER01") -> dict:
    return writer.write_dispatch_authorization(
        repo_root=fixture["root"],
        proposal_path=fixture["proposal_path"],
        reviewed_whole_file_sha256=_hash(fixture["authorization_raw"]),
        attempt_id=_attempt_id(token),
        actor="Karl",
    )


def dispatch_record(fixture: dict, source_repo: Path) -> tuple[dict, Path]:
    del source_repo
    authorization = fixture["authorization"]
    template = derive_dispatch_record(
        manifest=fixture["manifest"],
        manifest_raw=fixture["manifest_raw"],
        authorization=authorization,
        authorization_raw=fixture["authorization_raw"],
    )
    path = fixture["root"] / template["dispatch_record_path"]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(serialize_dispatch_authorization(template))
    return template, path


def test_positive_crossing_reserves_before_exact_target_and_creation(fixture, monkeypatch):
    sequence = []
    real_reserve = writer.reserve_dispatch_authorization_crossing_locked
    real_target_write = writer._exclusive_write_target
    real_audit_append = writer._append_audit_line
    real_terminal = writer.append_dispatch_authorization_crossing_terminal_locked

    def reserve_first(**kwargs):
        result = real_reserve(**kwargs)
        sequence.append("attempt_reserved")
        return result

    def target_after_reservation(**kwargs):
        assert sequence == ["attempt_reserved"]
        result = real_target_write(**kwargs)
        sequence.append("target")
        return result

    def audit_after_target(**kwargs):
        assert sequence == ["attempt_reserved", "target"]
        result = real_audit_append(**kwargs)
        sequence.append("authorization_created")
        return result

    def terminal_last(*, lock, event):
        assert sequence == [
            "attempt_reserved",
            "target",
            "authorization_created",
        ]
        result = real_terminal(lock=lock, event=event)
        sequence.append(event["event_type"])
        return result

    monkeypatch.setattr(
        writer,
        "reserve_dispatch_authorization_crossing_locked",
        reserve_first,
    )
    monkeypatch.setattr(writer, "_exclusive_write_target", target_after_reservation)
    monkeypatch.setattr(writer, "_append_audit_line", audit_after_target)
    monkeypatch.setattr(
        writer,
        "append_dispatch_authorization_crossing_terminal_locked",
        terminal_last,
    )
    result = cross(fixture)
    assert sequence == [
        "attempt_reserved",
        "target",
        "authorization_created",
        "crossing_committed",
    ]
    assert result["crossing_committed"] is True
    assert result["reviewed_whole_file_sha256"] == _hash(fixture["authorization_raw"])
    assert result["reviewed_byte_length"] == len(fixture["authorization_raw"])
    assert fixture["authorization_path"].read_bytes() == fixture["authorization_raw"]
    audit_raw = fixture["audit_path"].read_bytes()
    created = json.loads(audit_raw.decode("utf-8"))
    assert created["authorization_file_sha256"] == _hash(fixture["authorization_raw"])
    stream = (
        fixture["root"]
        / "research/queue/dispatch_authorization_reservations"
        / f"{result['attempt_id']}.crossing_reservation.jsonl"
    )
    lines = stream.read_bytes().splitlines(keepends=True)
    assert len(lines) == 2
    initial, terminal = [json.loads(line) for line in lines]
    assert initial["event_type"] == "attempt_reserved"
    assert terminal["event_type"] == "crossing_committed"
    assert terminal["event_payload"]["lifecycle_raw_line_sha256"] == _hash(audit_raw)
    assert terminal["event_payload"]["lifecycle_raw_line_byte_length"] == len(audit_raw)
    assert terminal["event_payload"]["resulting_authorization_whole_file_sha256"] == _hash(
        fixture["authorization_raw"]
    )
    assert terminal["event_payload"]["resulting_authorization_byte_length"] == len(
        fixture["authorization_raw"]
    )
    assert result["non_authority"]["does_not_create_dispatch"] is True


def test_cli_uses_independent_review_hash_and_fresh_attempt(fixture, monkeypatch, capsys):
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "dispatch_authorization_writer",
            "--repo-root",
            str(fixture["root"]),
            "--proposal",
            str(fixture["proposal_path"]),
            "--reviewed-whole-file-sha256",
            _hash(fixture["authorization_raw"]),
            "--attempt-id",
            _attempt_id("CLI00001"),
            "--actor",
            "Karl",
        ],
    )
    assert writer.main() == 0
    result = json.loads(capsys.readouterr().out)
    assert result["crossing_committed"] is True
    assert result["reviewed_byte_length"] == len(fixture["authorization_raw"])


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("hash", "sha256:" + "0" * 64, "does not match proposal"),
        ("actor", "NotKarl", "actor must exactly equal"),
        ("attempt", "bad-attempt", "attempt ID must match"),
    ],
)
def test_hash_actor_and_attempt_fail_before_mutation(fixture, field, value, message):
    kwargs = {
        "repo_root": fixture["root"],
        "proposal_path": fixture["proposal_path"],
        "reviewed_whole_file_sha256": _hash(fixture["authorization_raw"]),
        "attempt_id": _attempt_id("BADINPUT"),
        "actor": "Karl",
    }
    kwargs[
        {
            "hash": "reviewed_whole_file_sha256",
            "actor": "actor",
            "attempt": "attempt_id",
        }[field]
    ] = value
    with pytest.raises(writer.DispatchAuthorizationWriterError, match=message):
        writer.write_dispatch_authorization(**kwargs)
    assert not fixture["authorization_path"].exists()
    assert not fixture["audit_path"].exists()
    assert not (fixture["root"] / reservation.RESERVATION_ROOT).exists()


def test_semantically_equal_noncanonical_proposal_fails_before_mutation(
    fixture,
):
    alternate = (
        json.dumps(
            fixture["authorization"],
            sort_keys=False,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")
    assert json.loads(alternate) == fixture["authorization"]
    assert alternate != fixture["authorization_raw"]
    fixture["proposal_path"].write_bytes(alternate)
    with pytest.raises(
        writer.DispatchAuthorizationWriterError,
        match="not deterministic",
    ):
        writer.write_dispatch_authorization(
            repo_root=fixture["root"],
            proposal_path=fixture["proposal_path"],
            reviewed_whole_file_sha256=_hash(alternate),
            attempt_id=_attempt_id("NONCAN01"),
            actor="Karl",
        )
    assert not fixture["authorization_path"].exists()
    assert not fixture["audit_path"].exists()
    assert not (fixture["root"] / reservation.RESERVATION_ROOT).exists()


def test_freshness_invalid_attempt_fails_before_kdauth_mutation(fixture):
    stale_date = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y%m%d")
    with pytest.raises(
        writer.DispatchAuthorizationWriterError,
        match="reservation failed",
    ):
        writer.write_dispatch_authorization(
            repo_root=fixture["root"],
            proposal_path=fixture["proposal_path"],
            reviewed_whole_file_sha256=_hash(fixture["authorization_raw"]),
            attempt_id=f"KDAUTH-XING-{stale_date}-OLDSTAMP",
            actor="Karl",
        )
    assert not fixture["authorization_path"].exists()
    assert not fixture["audit_path"].exists()


def test_existing_or_dangling_link_target_fails_before_reservation(fixture, monkeypatch):
    real_link_check = authorization._is_link_or_reparse

    def report_target_link(path):
        if path == fixture["authorization_path"]:
            return True
        return real_link_check(path)

    monkeypatch.setattr(authorization, "_is_link_or_reparse", report_target_link)
    real_exists = authorization._lexical_entry_exists
    monkeypatch.setattr(
        authorization,
        "_lexical_entry_exists",
        lambda path: path == fixture["authorization_path"] or real_exists(path),
    )
    with pytest.raises(
        writer.DispatchAuthorizationWriterError,
        match="symlink|reparse",
    ):
        cross(fixture, "LINKTGT1")
    assert not fixture["authorization_path"].exists()
    assert not fixture["audit_path"].exists()
    assert not (fixture["root"] / reservation.RESERVATION_ROOT).exists()


def test_symlinked_proposal_fails_before_reservation(fixture, monkeypatch):
    real_link_check = authorization._is_link_or_reparse
    monkeypatch.setattr(
        authorization,
        "_is_link_or_reparse",
        lambda path: path == fixture["proposal_path"] or real_link_check(path),
    )
    with pytest.raises(
        writer.DispatchAuthorizationWriterError,
        match="symlink|reparse",
    ):
        cross(fixture, "LINKPROP")
    assert not fixture["authorization_path"].exists()
    assert not fixture["audit_path"].exists()
    assert not (fixture["root"] / reservation.RESERVATION_ROOT).exists()


def test_redirected_target_parent_fails_before_reservation(fixture):
    target_parent = fixture["authorization_path"].parent
    target_parent.rmdir()
    redirect = fixture["root"] / "redirected-authorization-parent"
    redirect.mkdir()
    _make_directory_redirect(target_parent, redirect)
    with pytest.raises(
        writer.DispatchAuthorizationWriterError,
        match="symlink|reparse",
    ):
        cross(fixture, "REDIRECT")
    assert not fixture["audit_path"].exists()
    assert not (fixture["root"] / reservation.RESERVATION_ROOT).exists()


def test_target_parent_redirect_after_reservation_is_not_followed(fixture, monkeypatch):
    real_reserve = writer.reserve_dispatch_authorization_crossing_locked
    target_parent = fixture["authorization_path"].parent
    redirect = fixture["root"] / "post-reservation-target-redirect"

    def reserve_then_redirect(**kwargs):
        result = real_reserve(**kwargs)
        _replace_directory_with_redirect(target_parent, redirect)
        return result

    monkeypatch.setattr(
        writer,
        "reserve_dispatch_authorization_crossing_locked",
        reserve_then_redirect,
    )
    with pytest.raises(
        writer.DispatchAuthorizationWriterIntegrityCriticalError,
        match="identity changed|inspection required",
    ):
        cross(fixture, "TGTPATH1")
    assert not (redirect / fixture["authorization_path"].name).exists()
    assert not fixture["audit_path"].exists()
    stream = (
        fixture["root"]
        / reservation.RESERVATION_ROOT
        / f"{_attempt_id('TGTPATH1')}.crossing_reservation.jsonl"
    )
    events = [json.loads(line) for line in stream.read_text().splitlines()]
    assert [event["event_type"] for event in events] == [
        "attempt_reserved",
        "crossing_integrity_critical",
    ]


def test_audit_parent_redirect_after_reservation_is_not_followed(fixture, monkeypatch):
    real_reserve = writer.reserve_dispatch_authorization_crossing_locked
    audit_relative = Path(
        "research/queue/post_reservation_audit_redirect_test/dispatch_authorization_events.jsonl"
    )
    monkeypatch.setattr(writer, "AUDIT_PATH", audit_relative)
    monkeypatch.setattr(authorization, "AUDIT_PATH", audit_relative)
    monkeypatch.setattr(reservation, "AUDIT_PATH", audit_relative)
    audit_path = fixture["root"] / audit_relative
    audit_parent = audit_path.parent
    audit_parent.mkdir()
    redirect = fixture["root"] / "post-reservation-audit-redirect"
    retained = None

    def reserve_then_redirect(**kwargs):
        nonlocal retained
        result = real_reserve(**kwargs)
        retained = _replace_directory_with_redirect(audit_parent, redirect)
        return result

    monkeypatch.setattr(
        writer,
        "reserve_dispatch_authorization_crossing_locked",
        reserve_then_redirect,
    )
    with pytest.raises(
        writer.DispatchAuthorizationWriterIntegrityCriticalError,
        match="identity changed|inspection required",
    ):
        cross(fixture, "AUDPATH1")
    assert retained is not None
    assert not (redirect / audit_path.name).exists()
    assert not fixture["authorization_path"].exists()
    stream = (
        fixture["root"]
        / reservation.RESERVATION_ROOT
        / f"{_attempt_id('AUDPATH1')}.crossing_reservation.jsonl"
    )
    events = [json.loads(line) for line in stream.read_text().splitlines()]
    assert events[0]["event_type"] == "attempt_reserved"
    assert all(
        event["event_type"] not in {"crossing_committed", "crossing_rolled_back_clean"}
        for event in events
    )
    if len(events) == 2:
        assert events[-1]["event_type"] == "crossing_integrity_critical"


def test_target_final_reparse_after_reservation_is_not_followed(fixture, monkeypatch):
    real_reserve = writer.reserve_dispatch_authorization_crossing_locked
    redirect = fixture["root"] / "post-reservation-final-redirect"

    def reserve_then_redirect(**kwargs):
        result = real_reserve(**kwargs)
        redirect.mkdir()
        _make_directory_redirect(fixture["authorization_path"], redirect)
        return result

    monkeypatch.setattr(
        writer,
        "reserve_dispatch_authorization_crossing_locked",
        reserve_then_redirect,
    )
    with pytest.raises(
        writer.DispatchAuthorizationWriterIntegrityCriticalError,
        match="identity|inspection required",
    ):
        cross(fixture, "TGTFINAL")
    assert not any(redirect.iterdir())
    assert not fixture["audit_path"].exists()
    stream = (
        fixture["root"]
        / reservation.RESERVATION_ROOT
        / f"{_attempt_id('TGTFINAL')}.crossing_reservation.jsonl"
    )
    events = [json.loads(line) for line in stream.read_text().splitlines()]
    assert [event["event_type"] for event in events] == [
        "attempt_reserved",
        "crossing_integrity_critical",
    ]


@pytest.mark.parametrize("missing_surface", ["target", "audit"])
def test_missing_mutable_parent_stops_before_reservation(fixture, missing_surface):
    parent = (
        fixture["authorization_path"].parent
        if missing_surface == "target"
        else fixture["audit_path"].parent
    )
    parent.rmdir()
    with pytest.raises(
        writer.DispatchAuthorizationWriterError,
        match="anchored|guarantee is unavailable",
    ):
        cross(fixture, f"MISS{missing_surface[:3].upper()}1")
    assert not parent.exists()
    assert not fixture["authorization_path"].exists()
    assert not fixture["audit_path"].exists()
    assert not (fixture["root"] / reservation.RESERVATION_ROOT).exists()


def test_traversal_in_candidate_fails_before_reservation(fixture):
    candidate = copy.deepcopy(fixture["authorization"])
    candidate["authorization_core"]["output_targets"]["scratch_output_root"] = (
        "scratch/authorized/../escape/"
    )
    candidate["authorization_core_sha256"] = authorization_support.authorization_core_sha256(
        candidate["authorization_core"]
    )
    raw = authorization_support.serialize_dispatch_authorization(candidate)
    fixture["proposal_path"].write_bytes(raw)
    with pytest.raises(writer.DispatchAuthorizationWriterError):
        writer.write_dispatch_authorization(
            repo_root=fixture["root"],
            proposal_path=fixture["proposal_path"],
            reviewed_whole_file_sha256=_hash(raw),
            attempt_id=_attempt_id("TRAVERS1"),
            actor="Karl",
        )
    assert not fixture["authorization_path"].exists()
    assert not fixture["audit_path"].exists()
    assert not (fixture["root"] / reservation.RESERVATION_ROOT).exists()


def test_existing_regular_target_fails_before_reservation(fixture):
    fixture["authorization_path"].parent.mkdir(parents=True, exist_ok=True)
    fixture["authorization_path"].write_bytes(b"existing")
    with pytest.raises(
        writer.DispatchAuthorizationWriterError,
        match="malformed|target path is not absent",
    ):
        cross(fixture, "EXISTS01")
    assert fixture["authorization_path"].read_bytes() == b"existing"
    assert not fixture["audit_path"].exists()
    assert not (fixture["root"] / reservation.RESERVATION_ROOT).exists()


def test_proposal_swap_on_lock_entry_fails_before_reservation(fixture, monkeypatch):
    real_lock = writer.dispatch_authorization_crossing_lock

    class SwapLock:
        def __init__(self):
            self.inner = real_lock(repo_root=fixture["root"])

        def __enter__(self):
            lock = self.inner.__enter__()
            fixture["proposal_path"].write_bytes(fixture["authorization_raw"] + b" ")
            return lock

        def __exit__(self, *args):
            return self.inner.__exit__(*args)

    monkeypatch.setattr(
        writer,
        "dispatch_authorization_crossing_lock",
        lambda **kwargs: SwapLock(),
    )
    with pytest.raises(writer.DispatchAuthorizationWriterError, match="changed"):
        cross(fixture, "SWAP0001")
    assert not fixture["authorization_path"].exists()
    assert not fixture["audit_path"].exists()
    assert not (fixture["root"] / reservation.RESERVATION_ROOT).exists()


def test_reservation_failure_prevents_target_and_audit_mutation(fixture, monkeypatch):
    def fail_reservation(**kwargs):
        raise reservation.DispatchAuthorizationReservationError("synthetic")

    monkeypatch.setattr(
        writer,
        "reserve_dispatch_authorization_crossing_locked",
        fail_reservation,
    )
    with pytest.raises(writer.DispatchAuthorizationWriterError, match="reservation"):
        cross(fixture, "RSVFAIL1")
    assert not fixture["authorization_path"].exists()
    assert not fixture["audit_path"].exists()


def test_written_target_mismatch_is_integrity_critical(fixture, monkeypatch):
    real_target_write = writer._exclusive_write_target

    def write_mismatch(**kwargs):
        kwargs["raw"] += b" "
        return real_target_write(**kwargs)

    monkeypatch.setattr(writer, "_exclusive_write_target", write_mismatch)
    with pytest.raises(
        writer.DispatchAuthorizationWriterIntegrityCriticalError,
        match="written KDAUTH hash differs",
    ):
        cross(fixture, "TGTMIS01")
    assert fixture["authorization_path"].read_bytes().endswith(b" ")
    assert not fixture["audit_path"].exists()
    stream = (
        fixture["root"]
        / reservation.RESERVATION_ROOT
        / f"{_attempt_id('TGTMIS01')}.crossing_reservation.jsonl"
    )
    events = [json.loads(line) for line in stream.read_text().splitlines()]
    assert events[0]["event_type"] == "attempt_reserved"
    assert events[-1]["event_type"] == "crossing_integrity_critical"


def test_creation_event_mismatch_rolls_back_only_when_durability_is_proven(fixture, monkeypatch):
    real_creation = writer._creation_event

    def mismatched_creation(**kwargs):
        event = real_creation(**kwargs)
        event["authorization_file_sha256"] = "sha256:" + "0" * 64
        return event

    monkeypatch.setattr(writer, "_creation_event", mismatched_creation)
    with pytest.raises(
        writer.DispatchAuthorizationWriterError,
        match="rolled back cleanly",
    ):
        cross(fixture, "CRTMIS01")
    assert not fixture["authorization_path"].exists()
    assert not fixture["audit_path"].exists()
    stream = (
        fixture["root"]
        / reservation.RESERVATION_ROOT
        / f"{_attempt_id('CRTMIS01')}.crossing_reservation.jsonl"
    )
    events = [json.loads(line) for line in stream.read_text().splitlines()]
    assert [event["event_type"] for event in events] == [
        "attempt_reserved",
        "crossing_rolled_back_clean",
    ]


def test_partial_target_write_is_integrity_critical(fixture, monkeypatch):
    def partial_write(fd, raw):
        os.write(fd, raw[:17])
        raise OSError("synthetic partial target write")

    monkeypatch.setattr(writer, "_write_all", partial_write)
    with pytest.raises(
        writer.DispatchAuthorizationWriterIntegrityCriticalError,
        match="write/fsync is uncertain",
    ):
        cross(fixture, "PARTIAL1")
    assert fixture["authorization_path"].exists()
    assert 0 < fixture["authorization_path"].stat().st_size < len(fixture["authorization_raw"])
    assert not fixture["audit_path"].exists()


def test_target_directory_fsync_failure_is_integrity_critical(fixture, monkeypatch):
    real_directory_fsync = writer._native_directory_fsync
    invocation = 0

    def fail_directory_fsync(native):
        nonlocal invocation
        invocation += 1
        if invocation == 5:
            raise OSError("synthetic target directory fsync failure")
        return real_directory_fsync(native)

    monkeypatch.setattr(
        writer,
        "_native_directory_fsync",
        fail_directory_fsync,
    )
    with pytest.raises(
        writer.DispatchAuthorizationWriterIntegrityCriticalError,
        match="write/fsync is uncertain",
    ):
        cross(fixture, "DIRFSYNC")
    assert fixture["authorization_path"].read_bytes() == fixture["authorization_raw"]
    assert not fixture["audit_path"].exists()


def test_partial_audit_append_is_integrity_critical(fixture, monkeypatch):
    real_write_all = writer._write_all
    invocation = 0

    def partial_second_write(fd, raw):
        nonlocal invocation
        invocation += 1
        if invocation == 2:
            os.write(fd, raw[:19])
            raise OSError("synthetic partial audit append")
        real_write_all(fd, raw)

    monkeypatch.setattr(writer, "_write_all", partial_second_write)
    with pytest.raises(
        writer.DispatchAuthorizationWriterIntegrityCriticalError,
        match="append_state_ambiguous|append failed|uncertain",
    ):
        cross(fixture, "AUDPART1")
    assert fixture["authorization_path"].read_bytes() == fixture["authorization_raw"]
    assert fixture["audit_path"].exists()
    assert not fixture["audit_path"].read_bytes().endswith(b"\n")


def test_lock_cleanup_failure_never_returns_false_success(fixture, monkeypatch):
    real_lock = writer.dispatch_authorization_crossing_lock

    class CleanupFailureLock:
        def __init__(self):
            self.inner = real_lock(repo_root=fixture["root"])

        def __enter__(self):
            return self.inner.__enter__()

        def __exit__(self, *args):
            self.inner.__exit__(*args)
            raise (
                reservation.DispatchAuthorizationReservationIntegrityCriticalError(
                    "synthetic lock cleanup uncertainty"
                )
            )

    monkeypatch.setattr(
        writer,
        "dispatch_authorization_crossing_lock",
        lambda **kwargs: CleanupFailureLock(),
    )
    with pytest.raises(
        writer.DispatchAuthorizationWriterIntegrityCriticalError,
        match="lock cleanup failed",
    ):
        cross(fixture, "LOCKEXIT")
    assert fixture["authorization_path"].exists()
    assert fixture["audit_path"].exists()
    stream = (
        fixture["root"]
        / reservation.RESERVATION_ROOT
        / f"{_attempt_id('LOCKEXIT')}.crossing_reservation.jsonl"
    )
    events = [json.loads(line) for line in stream.read_text().splitlines()]
    assert events[-1]["event_type"] == "crossing_committed"


def test_preappend_terminal_failure_rolls_back_and_burns(fixture, monkeypatch):
    real_append = writer.append_dispatch_authorization_crossing_terminal_locked

    def fail_commit(*, lock, event):
        if event["event_type"] == "crossing_committed":
            raise reservation.DispatchAuthorizationReservationError("synthetic preappend rejection")
        return real_append(lock=lock, event=event)

    monkeypatch.setattr(
        writer,
        "append_dispatch_authorization_crossing_terminal_locked",
        fail_commit,
    )
    with pytest.raises(writer.DispatchAuthorizationWriterError, match="rolled back"):
        cross(fixture, "ROLLBACK")
    assert not fixture["authorization_path"].exists()
    assert not fixture["audit_path"].exists()
    stream = (
        fixture["root"]
        / reservation.RESERVATION_ROOT
        / f"{_attempt_id('ROLLBACK')}.crossing_reservation.jsonl"
    )
    events = [json.loads(line) for line in stream.read_text().splitlines()]
    assert [event["event_type"] for event in events] == [
        "attempt_reserved",
        "crossing_rolled_back_clean",
    ]
    with pytest.raises(
        DispatchAuthorizationError,
        match="crossing reservation permanently consumes",
    ):
        validate_dispatch_authorization_candidate(
            repo_root=fixture["root"],
            proposal_path=fixture["proposal_path"],
        )


def test_uncertain_terminal_is_integrity_critical_without_false_success(fixture, monkeypatch):
    real_append = writer.append_dispatch_authorization_crossing_terminal_locked

    def fail_commit(*, lock, event):
        if event["event_type"] == "crossing_committed":
            raise reservation.DispatchAuthorizationReservationIntegrityCriticalError(
                "synthetic uncertain terminal"
            )
        return real_append(lock=lock, event=event)

    monkeypatch.setattr(
        writer,
        "append_dispatch_authorization_crossing_terminal_locked",
        fail_commit,
    )
    with pytest.raises(writer.DispatchAuthorizationWriterIntegrityCriticalError):
        cross(fixture, "CRITICAL")
    assert fixture["authorization_path"].exists()
    assert fixture["audit_path"].exists()
    stream = (
        fixture["root"]
        / reservation.RESERVATION_ROOT
        / f"{_attempt_id('CRITICAL')}.crossing_reservation.jsonl"
    )
    events = [json.loads(line) for line in stream.read_text().splitlines()]
    assert events[-1]["event_type"] == "crossing_integrity_critical"


def test_stale_shared_lock_fails_before_reservation(fixture):
    lock_path = fixture["root"] / reservation.CROSSING_LOCK_PATH
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    lock_path.write_text("stale\n", encoding="utf-8")
    with pytest.raises(writer.DispatchAuthorizationWriterError, match="lock"):
        cross(fixture, "STALE001")
    assert not fixture["authorization_path"].exists()
    assert not fixture["audit_path"].exists()
    assert not (fixture["root"] / reservation.RESERVATION_ROOT).exists()


def test_concurrent_writers_commit_at_most_one_crossing(fixture):
    def invoke(token):
        try:
            return cross(fixture, token)
        except writer.DispatchAuthorizationWriterError as exc:
            return exc

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(invoke, ("RACE0001", "RACE0002")))
    successes = [result for result in results if isinstance(result, dict)]
    assert len(successes) == 1
    assert fixture["authorization_path"].read_bytes() == fixture["authorization_raw"]
    streams = list((fixture["root"] / reservation.RESERVATION_ROOT).glob("*.jsonl"))
    assert len(streams) == 1


@pytest.mark.parametrize(
    ("event_type", "payload"),
    [
        (
            "authorization_revoked",
            {
                "event_kind": "authorization_revoked",
                "reason": "synthetic revocation",
            },
        ),
        (
            "authorization_superseded",
            {
                "event_kind": "authorization_superseded",
                "new_authorization_id": "KDAUTH-OTHER-R2-9002",
                "new_authorization_path": (
                    "research/queue/dispatch_authorizations/"
                    "KDAUTH-OTHER-R2-9002.dispatch_authorization.json"
                ),
                "reason": "synthetic supersession",
            },
        ),
    ],
)
def test_lifecycle_preconsumption_terminal_is_append_only(fixture, event_type, payload):
    cross(fixture, "LIFECY01")
    result = writer.append_dispatch_authorization_lifecycle_event(
        repo_root=fixture["root"],
        authorization_path=fixture["authorization_path"],
        event_type=event_type,
        actor="Karl",
        event_payload=payload,
    )
    assert result["event_type"] == event_type
    reservations = reservation.scan_dispatch_authorization_reservations(
        repo_root=fixture["root"],
        include_retained_history=True,
    )
    assert len(reservations) == 1
    assert reservations[0]["terminal_outcome"] == "crossing_committed"
    assert reservations[0]["findings"] == []
    assert collect_dispatch_without_consumption_findings(repo_root=fixture["root"]) == []
    with pytest.raises(writer.DispatchAuthorizationWriterError):
        writer.append_dispatch_authorization_lifecycle_event(
            repo_root=fixture["root"],
            authorization_path=fixture["authorization_path"],
            event_type="authorization_revoked",
            actor="Karl",
            event_payload={
                "event_kind": "authorization_revoked",
                "reason": "second event forbidden",
            },
        )


def test_dispatch_sentinel_clears_only_on_exact_consumption(fixture, source_repo):
    cross(fixture, "CONSUME1")
    dispatch, dispatch_path = dispatch_record(fixture, source_repo)
    validated = validate_dispatch_record_for_authorization(
        repo_root=fixture["root"],
        dispatch_path=dispatch_path,
    )
    assert validated["valid"] is True
    findings = collect_dispatch_without_consumption_findings(repo_root=fixture["root"])
    assert len(findings) == 1
    assert findings[0]["dispatch_id"] == dispatch["dispatch_id"]

    result = writer.append_dispatch_authorization_lifecycle_event(
        repo_root=fixture["root"],
        authorization_path=fixture["authorization_path"],
        event_type="authorization_consumed",
        actor="Karl",
        event_payload={
            "event_kind": "authorization_consumed",
            "consumer_tool": "synthetic-dispatch-writer-v1",
            "dispatch_record_path": dispatch["dispatch_record_path"],
            "consumption_is_permanent": True,
        },
    )
    assert result["event_type"] == "authorization_consumed"
    assert collect_dispatch_without_consumption_findings(repo_root=fixture["root"]) == []
    with pytest.raises(DispatchAuthorizationError):
        validate_dispatch_authorization(
            repo_root=fixture["root"],
            authorization_path=fixture["authorization_path"],
        )
    with pytest.raises(writer.DispatchAuthorizationWriterError):
        writer.append_dispatch_authorization_lifecycle_event(
            repo_root=fixture["root"],
            authorization_path=fixture["authorization_path"],
            event_type="authorization_revoked",
            actor="Karl",
            event_payload={
                "event_kind": "authorization_revoked",
                "reason": "post-consumption event forbidden",
            },
        )


def test_retained_committed_crossing_permanently_burns_identities(fixture):
    cross(fixture, "RETAIN01")
    _commit(fixture["root"], "synthetic committed crossing")
    fixture["authorization_path"].unlink()
    fixture["audit_path"].unlink()
    shutil.rmtree(fixture["root"] / reservation.RESERVATION_ROOT)
    _commit(fixture["root"], "synthetic retained crossing removal")
    with pytest.raises(
        writer.DispatchAuthorizationWriterError,
        match="permanently consumes",
    ):
        cross(fixture, "RETAIN02")
    assert not fixture["authorization_path"].exists()
    assert not fixture["audit_path"].exists()
    assert not (fixture["root"] / reservation.RESERVATION_ROOT).exists()


def test_sentinel_ignores_authorization_without_dispatch(fixture):
    cross(fixture, "NODSP001")
    before = {
        path.relative_to(fixture["root"]).as_posix(): _hash(path.read_bytes())
        for path in fixture["root"].rglob("*")
        if path.is_file() and ".git" not in path.parts
    }
    assert collect_dispatch_without_consumption_findings(repo_root=fixture["root"]) == []
    assert collect_dispatch_without_consumption_findings(repo_root=fixture["root"]) == []
    after = {
        path.relative_to(fixture["root"]).as_posix(): _hash(path.read_bytes())
        for path in fixture["root"].rglob("*")
        if path.is_file() and ".git" not in path.parts
    }
    assert after == before


def test_sentinel_remains_for_mismatched_consumption(fixture, source_repo):
    cross(fixture, "MISMATCH")
    dispatch, _ = dispatch_record(fixture, source_repo)
    created = json.loads(fixture["audit_path"].read_text(encoding="utf-8"))
    consumed = copy.deepcopy(created)
    consumed["event_id"] = f"KDAUTH-EVENT-{created['authorization_id']}-000002"
    consumed["sequence_number"] = 2
    consumed["event_type"] = "authorization_consumed"
    consumed["occurred_at"] = writer._timestamp_after(created["occurred_at"])
    consumed["event_payload"] = {
        "event_kind": "authorization_consumed",
        "consumer_tool": "synthetic-dispatch-writer-v1",
        "dispatch_record_path": (
            "research/queue/dispatch_records/DSP-20260727-WRONG001.dispatch_record.json"
        ),
        "consumption_is_permanent": True,
    }
    fixture["audit_path"].write_bytes(
        repo_canonical_json_v1(created) + b"\n" + repo_canonical_json_v1(consumed) + b"\n"
    )
    findings = collect_dispatch_without_consumption_findings(repo_root=fixture["root"])
    assert len(findings) == 1
    assert findings[0]["dispatch_id"] == dispatch["dispatch_id"]
    assert findings[0]["lifecycle_state"] == "consumed"


def test_sentinel_rejects_noncanonical_dispatch_bytes(fixture, source_repo):
    cross(fixture, "CANON001")
    dispatch, dispatch_path = dispatch_record(fixture, source_repo)
    dispatch_path.write_bytes(
        (json.dumps(dispatch, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    )
    with pytest.raises(
        DispatchAuthorizationError,
        match="dispatch record is not canonical",
    ):
        validate_dispatch_record_for_authorization(
            repo_root=fixture["root"],
            dispatch_path=dispatch_path,
        )
    assert collect_dispatch_without_consumption_findings(repo_root=fixture["root"]) == []
