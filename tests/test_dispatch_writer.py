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
from datetime import datetime, timezone
from pathlib import Path

import duckdb
import pytest

from tests import test_dispatch_authorization as authorization_support
from tools.canon_intake import dispatch_writer as writer
from tools.canon_intake import (
    dispatch_authorization_reservation as reservation,
)
from tools.research_query import query_layer
from tools.canon_intake.dispatch_authorization import (
    DispatchAuthorizationError,
    collect_dispatch_without_consumption_findings,
    read_and_validate_dispatch_authorization_audit,
    serialize_dispatch_authorization,
    validate_dispatch_authorization,
    validate_dispatch_record_for_authorization,
)
from tools.canon_intake.dispatch_authorization_writer import (
    append_dispatch_authorization_lifecycle_event,
    write_dispatch_authorization,
)
from tools.canon_intake.dispatch_manifest import (
    derive_dispatch_record,
    serialize_derived_dispatch_record,
    serialize_dispatch_manifest,
    write_dispatch_manifest,
)


def _hash(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def _remove_readonly(function, path, exc_info):
    del exc_info
    os.chmod(path, 0o700)
    function(path)


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


def _attempt_id(token: str) -> str:
    date = datetime.now(timezone.utc).strftime("%Y%m%d")
    return f"KDAUTH-XING-{date}-{token}"


def _prepare_fixture(tmp_path: Path, source_repo: Path) -> dict:
    fixture = authorization_support._fixture(
        tmp_path,
        source_repo,
        reservation_state="none",
    )
    dispatch_schema = (
        source_repo / "research/schemas/canon_dispatch_record.schema.json"
    )
    shutil.copy2(
        dispatch_schema,
        fixture["root"] / "research/schemas" / dispatch_schema.name,
    )
    manifest_proposal = (
        fixture["root"] / "review/dispatch_manifest.review.json"
    )
    authorization_proposal = (
        fixture["root"] / "review/kdauth.review.json"
    )
    manifest_proposal.parent.mkdir(parents=True)
    manifest_proposal.write_bytes(fixture["manifest_raw"])
    authorization_proposal.write_bytes(fixture["authorization_raw"])
    fixture["manifest_path"].unlink()
    fixture["authorization_path"].unlink()
    fixture["audit_path"].unlink()
    dispatch_path = (
        fixture["root"]
        / fixture["manifest"]["crossing_identities"][
            "dispatch_record_path"
        ]
    )
    dispatch_path.parent.mkdir(parents=True)
    shutil.rmtree(
        fixture["root"] / ".git",
        onerror=_remove_readonly,
    )
    _git(fixture["root"], "init", "-q")
    _commit(fixture["root"], "synthetic pre-dispatch dependencies")

    manifest_result = write_dispatch_manifest(
        repo_root=fixture["root"],
        proposal_path=manifest_proposal,
        reviewed_whole_file_sha256=_hash(fixture["manifest_raw"]),
    )
    authorization_result = write_dispatch_authorization(
        repo_root=fixture["root"],
        proposal_path=authorization_proposal,
        reviewed_whole_file_sha256=_hash(fixture["authorization_raw"]),
        attempt_id=_attempt_id("DSPWRITE"),
        actor="Karl",
    )
    fixture.update(
        {
            "manifest_proposal": manifest_proposal,
            "authorization_proposal": authorization_proposal,
            "dispatch_path": dispatch_path,
            "manifest_result": manifest_result,
            "authorization_result": authorization_result,
        }
    )
    return fixture


@pytest.fixture
def source_repo() -> Path:
    return Path(__file__).resolve().parents[1]


@pytest.fixture
def fixture(tmp_path: Path, source_repo: Path) -> dict:
    return _prepare_fixture(tmp_path, source_repo)


def _writer_kwargs(fixture: dict) -> dict:
    crossing = fixture["manifest"]["crossing_identities"]
    return {
        "repo_root": fixture["root"],
        "manifest_path": fixture["manifest_path"],
        "reviewed_manifest_whole_file_sha256": _hash(
            fixture["manifest_raw"]
        ),
        "manifest_id": fixture["manifest"]["manifest_id"],
        "authorization_path": fixture["authorization_path"],
        "reviewed_authorization_whole_file_sha256": _hash(
            fixture["authorization_raw"]
        ),
        "authorization_id": fixture["authorization"][
            "authorization_id"
        ],
        "dispatch_id": crossing["dispatch_id"],
        "run_id": crossing["run_id"],
        "actor": "Karl",
    }


def test_end_to_end_writers_create_exact_dispatch_then_consume_once(fixture):
    independently_derived = derive_dispatch_record(
        manifest=fixture["manifest"],
        manifest_raw=fixture["manifest_raw"],
        authorization=fixture["authorization"],
        authorization_raw=fixture["authorization_raw"],
    )
    expected_raw = serialize_derived_dispatch_record(
        manifest=fixture["manifest"],
        manifest_raw=fixture["manifest_raw"],
        authorization=fixture["authorization"],
        authorization_raw=fixture["authorization_raw"],
    )

    result = writer.write_dispatch_record(**_writer_kwargs(fixture))

    assert fixture["manifest_result"]["manifest_created"] is True
    assert fixture["authorization_result"]["crossing_committed"] is True
    assert result["dispatch_created"] is True
    assert result["authorization_consumed"] is True
    assert fixture["dispatch_path"].read_bytes() == expected_raw
    assert json.loads(expected_raw) == independently_derived
    validation = validate_dispatch_record_for_authorization(
        repo_root=fixture["root"],
        dispatch_path=fixture["dispatch_path"],
    )
    assert validation["lifecycle_state"] == "consumed"
    rows, _ = read_and_validate_dispatch_authorization_audit(
        repo_root=fixture["root"]
    )
    matching = [
        event
        for event, _ in rows
        if event["authorization_id"]
        == fixture["authorization"]["authorization_id"]
    ]
    assert [event["event_type"] for event in matching] == [
        "authorization_created",
        "authorization_consumed",
    ]
    assert (
        matching[-1]["event_payload"]["dispatch_record_path"]
        == independently_derived["dispatch_record_path"]
    )
    assert collect_dispatch_without_consumption_findings(
        repo_root=fixture["root"]
    ) == []

    with pytest.raises(writer.DispatchWriterError):
        writer.write_dispatch_record(**_writer_kwargs(fixture))


def test_post_dispatch_consumption_failure_preserves_visible_integrity(
    fixture, monkeypatch
):
    def fail_before_append(**kwargs):
        del kwargs
        raise RuntimeError("synthetic lifecycle interruption")

    monkeypatch.setattr(
        writer,
        "append_dispatch_authorization_lifecycle_event",
        fail_before_append,
    )
    with pytest.raises(
        writer.DispatchWriterIntegrityCriticalError,
        match="durable dispatch exists",
    ) as caught:
        writer.write_dispatch_record(**_writer_kwargs(fixture))
    assert caught.value.dispatch_durable is True
    assert fixture["dispatch_path"].is_file()
    findings = collect_dispatch_without_consumption_findings(
        repo_root=fixture["root"]
    )
    assert [finding["dispatch_id"] for finding in findings] == [
        fixture["manifest"]["crossing_identities"]["dispatch_id"]
    ]
    with pytest.raises(writer.DispatchWriterError):
        writer.write_dispatch_record(**_writer_kwargs(fixture))
    assert (
        validate_dispatch_authorization(
            repo_root=fixture["root"],
            authorization_path=fixture["authorization_path"],
            scan_history=False,
        )["lifecycle_state"]
        == "created"
    )


def test_precreate_failure_leaves_no_dispatch_and_no_consumption(
    fixture, monkeypatch
):
    real_create = writer._AnchoredDirectory.create

    def fail_dispatch_create(self, name):
        if name.endswith(".dispatch_record.json"):
            raise OSError("synthetic exclusive-create failure")
        return real_create(self, name)

    monkeypatch.setattr(writer._AnchoredDirectory, "create", fail_dispatch_create)
    with pytest.raises(writer.DispatchWriterIntegrityCriticalError):
        writer.write_dispatch_record(**_writer_kwargs(fixture))
    assert not fixture["dispatch_path"].exists()
    assert (
        validate_dispatch_authorization(
            repo_root=fixture["root"],
            authorization_path=fixture["authorization_path"],
        )["lifecycle_state"]
        == "created"
    )
    assert collect_dispatch_without_consumption_findings(
        repo_root=fixture["root"]
    ) == []


@pytest.mark.parametrize("selected", ["manifest", "authorization"])
def test_in_lock_reviewed_byte_drift_fails_before_dispatch(
    fixture, monkeypatch, selected
):
    real_lock = writer.dispatch_authorization_crossing_lock

    @contextlib.contextmanager
    def drift_after_preflight(*, repo_root):
        with real_lock(repo_root=repo_root) as held:
            path = (
                fixture["manifest_path"]
                if selected == "manifest"
                else fixture["authorization_path"]
            )
            path.write_bytes(path.read_bytes() + b" ")
            yield held

    monkeypatch.setattr(
        writer, "dispatch_authorization_crossing_lock", drift_after_preflight
    )
    with pytest.raises(writer.DispatchWriterError):
        writer.write_dispatch_record(**_writer_kwargs(fixture))
    assert not fixture["dispatch_path"].exists()
    rows, _ = read_and_validate_dispatch_authorization_audit(
        repo_root=fixture["root"]
    )
    assert rows[-1][0]["event_type"] == "authorization_created"


@pytest.mark.parametrize(
    "field, replacement",
    [
        ("queue_binding", {"queue_item_id": "QI-20260720-DRIFT9001"}),
        ("lineage", {"strategy_spec": {"artifact_id": "DRIFT"}}),
        ("dataset", {"dataset_id": "DRIFT"}),
        ("funding", {"funding_series_id": "DRIFT"}),
        ("runner", {"version": "drift"}),
        ("denominator", {"planned": 999}),
        ("budget", {"upper_bound": 999}),
        ("execution_parameters", {"seed": 999}),
        (
            "crossing_identities",
            {"run_id": "RUN-20260720-DRIFT9001"},
        ),
        (
            "output_targets",
            {
                "provisional_result_paths": [
                    "scratch/FIXTURE-RUN/dispatch/drift.json"
                ]
            },
        ),
    ],
)
def test_any_manifest_derived_field_drift_is_rejected(
    fixture, field, replacement
):
    manifest = copy.deepcopy(fixture["manifest"])
    manifest[field].update(replacement)
    raw = serialize_dispatch_manifest(manifest)
    fixture["manifest_path"].write_bytes(raw)
    kwargs = _writer_kwargs(fixture)
    kwargs["reviewed_manifest_whole_file_sha256"] = _hash(raw)
    with pytest.raises(writer.DispatchWriterError):
        writer.write_dispatch_record(**kwargs)
    assert not fixture["dispatch_path"].exists()


@pytest.mark.parametrize(
    "identity",
    ["manifest_id", "authorization_id", "dispatch_id", "run_id"],
)
def test_explicit_identity_substitution_is_rejected(fixture, identity):
    kwargs = _writer_kwargs(fixture)
    kwargs[identity] = "SUBSTITUTED-ID"
    with pytest.raises(
        writer.DispatchWriterError,
        match=f"{identity} differs",
    ):
        writer.write_dispatch_record(**kwargs)
    assert not fixture["dispatch_path"].exists()


@pytest.mark.parametrize("selected", ["manifest", "authorization"])
def test_review_hash_substitution_is_rejected(fixture, selected):
    kwargs = _writer_kwargs(fixture)
    kwargs[
        f"reviewed_{selected}_whole_file_sha256"
    ] = "sha256:" + "0" * 64
    with pytest.raises(writer.DispatchWriterError, match="mismatch"):
        writer.write_dispatch_record(**kwargs)
    assert not fixture["dispatch_path"].exists()


@pytest.mark.parametrize("selected", ["manifest", "authorization"])
def test_non_authoritative_review_path_is_rejected(fixture, selected):
    kwargs = _writer_kwargs(fixture)
    kwargs[f"{selected}_path"] = fixture[
        f"{selected}_proposal"
    ]
    with pytest.raises(writer.DispatchWriterError):
        writer.write_dispatch_record(**kwargs)
    assert not fixture["dispatch_path"].exists()


def test_api_and_cli_accept_no_caller_supplied_dispatch_bytes(
    fixture, monkeypatch, capsys
):
    assert "dispatch" not in inspect.signature(
        writer.write_dispatch_record
    ).parameters
    kwargs = _writer_kwargs(fixture)
    argv = [
        "dispatch_writer",
        "--repo-root",
        str(kwargs["repo_root"]),
        "--manifest",
        str(kwargs["manifest_path"]),
        "--reviewed-manifest-whole-file-sha256",
        kwargs["reviewed_manifest_whole_file_sha256"],
        "--manifest-id",
        kwargs["manifest_id"],
        "--authorization",
        str(kwargs["authorization_path"]),
        "--reviewed-authorization-whole-file-sha256",
        kwargs["reviewed_authorization_whole_file_sha256"],
        "--authorization-id",
        kwargs["authorization_id"],
        "--dispatch-id",
        kwargs["dispatch_id"],
        "--run-id",
        kwargs["run_id"],
        "--actor",
        kwargs["actor"],
    ]
    monkeypatch.setattr(sys, "argv", argv)
    assert writer.main() == 0
    output = json.loads(capsys.readouterr().out)
    assert output["dispatch_file_sha256"] == _hash(
        fixture["dispatch_path"].read_bytes()
    )


@pytest.mark.parametrize(
    "terminal,payload",
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
def test_terminal_kdauth_is_rejected_before_dispatch(
    fixture, terminal, payload
):
    append_dispatch_authorization_lifecycle_event(
        repo_root=fixture["root"],
        authorization_path=fixture["authorization_path"],
        event_type=terminal,
        actor="Karl",
        event_payload=payload,
    )
    with pytest.raises(writer.DispatchWriterError):
        writer.write_dispatch_record(**_writer_kwargs(fixture))
    assert not fixture["dispatch_path"].exists()


def test_missing_reservation_and_malformed_audit_fail_closed(fixture):
    reservation_path = next(
        (
            fixture["root"]
            / "research/queue/dispatch_authorization_reservations"
        ).glob("*.jsonl")
    )
    reservation_path.unlink()
    with pytest.raises(writer.DispatchWriterError):
        writer.write_dispatch_record(**_writer_kwargs(fixture))
    assert not fixture["dispatch_path"].exists()

    fixture["audit_path"].write_bytes(
        fixture["audit_path"].read_bytes() + b'{"partial":true}'
    )
    with pytest.raises(writer.DispatchWriterError):
        writer.write_dispatch_record(**_writer_kwargs(fixture))
    assert not fixture["dispatch_path"].exists()


def test_current_and_retained_dispatch_collisions_fail_closed(fixture):
    derived = derive_dispatch_record(
        manifest=fixture["manifest"],
        manifest_raw=fixture["manifest_raw"],
        authorization=fixture["authorization"],
        authorization_raw=fixture["authorization_raw"],
    )
    fixture["dispatch_path"].write_bytes(
        serialize_dispatch_authorization(derived)
    )
    with pytest.raises(writer.DispatchWriterError):
        writer.write_dispatch_record(**_writer_kwargs(fixture))

    _commit(fixture["root"], "synthetic retained dispatch collision")
    fixture["dispatch_path"].unlink()
    _commit(fixture["root"], "remove current dispatch collision")
    with pytest.raises(writer.DispatchWriterError):
        writer.write_dispatch_record(**_writer_kwargs(fixture))
    assert not fixture["dispatch_path"].exists()


@pytest.mark.parametrize(
    "collision_field",
    [
        "authorization_id",
        "queue_item_id",
        "dispatch_id",
        "run_id",
        "dispatch_path",
        "stream_path",
    ],
)
def test_every_single_use_binding_collision_is_rejected(
    fixture, collision_field
):
    derived = derive_dispatch_record(
        manifest=fixture["manifest"],
        manifest_raw=fixture["manifest_raw"],
        authorization=fixture["authorization"],
        authorization_raw=fixture["authorization_raw"],
    )
    other = copy.deepcopy(derived)
    other["dispatch_id"] = "DSP-20260720-OTHER9002"
    other["dispatch_record_path"] = (
        "research/queue/dispatch_records/"
        "DSP-20260720-OTHER9002.dispatch_record.json"
    )
    other["run_binding"]["run_id"] = "RUN-20260720-OTHER9002"
    other["run_binding"]["execution_event_stream_path"] = (
        "research/queue/execution_events/"
        "RUN-20260720-OTHER9002.execution_events.jsonl"
    )
    other["dispatch_authorization"]["authorization_id"] = (
        "KDAUTH-OTHER-R2-9002"
    )
    other["dispatch_authorization"]["source_path"] = (
        "research/queue/dispatch_authorizations/"
        "KDAUTH-OTHER-R2-9002.dispatch_authorization.json"
    )
    other["dispatch_authorization"]["source_sha256"] = "sha256:" + "9" * 64
    other["queue_binding"]["queue_item_id"] = "QI-20260720-OTHER9002"
    if collision_field == "authorization_id":
        other["dispatch_authorization"]["authorization_id"] = derived[
            "dispatch_authorization"
        ]["authorization_id"]
    elif collision_field == "queue_item_id":
        other["queue_binding"]["queue_item_id"] = derived["queue_binding"][
            "queue_item_id"
        ]
    elif collision_field == "dispatch_id":
        other["dispatch_id"] = derived["dispatch_id"]
    elif collision_field == "run_id":
        other["run_binding"]["run_id"] = derived["run_binding"]["run_id"]
    elif collision_field == "dispatch_path":
        other["dispatch_record_path"] = derived["dispatch_record_path"]
    else:
        other["run_binding"]["execution_event_stream_path"] = derived[
            "run_binding"
        ]["execution_event_stream_path"]
    path = (
        fixture["dispatch_path"].parent
        / "DSP-20260720-OTHER9002.dispatch_record.json"
    )
    path.write_bytes(serialize_dispatch_authorization(other))
    with pytest.raises(writer.DispatchWriterError):
        writer.write_dispatch_record(**_writer_kwargs(fixture))
    assert not fixture["dispatch_path"].exists()


def _make_directory_redirect(path: Path, destination: Path) -> Path:
    retained = path.with_name(path.name + "-retained")
    path.rename(retained)
    destination.mkdir()
    try:
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


@pytest.mark.parametrize("surface", ["target", "audit"])
def test_reparse_or_symlink_parent_is_rejected(
    fixture, tmp_path, surface
):
    selected = (
        fixture["dispatch_path"].parent
        if surface == "target"
        else fixture["audit_path"].parent
    )
    outside = tmp_path / f"outside-{surface}"
    _make_directory_redirect(selected, outside)
    with pytest.raises(writer.DispatchWriterError):
        writer.write_dispatch_record(**_writer_kwargs(fixture))
    assert not fixture["dispatch_path"].exists()


def test_post_validation_path_substitution_race_is_not_followed(
    fixture, tmp_path, monkeypatch
):
    real_validate = writer._validate_reviewed_inputs
    calls = 0
    retained = None
    outside = tmp_path / "outside-race"

    def replace_after_locked_validation(**kwargs):
        nonlocal calls, retained
        result = real_validate(**kwargs)
        calls += 1
        if calls == 2:
            retained = _make_directory_redirect(
                fixture["dispatch_path"].parent,
                outside,
            )
        return result

    monkeypatch.setattr(
        writer, "_validate_reviewed_inputs", replace_after_locked_validation
    )
    with pytest.raises(writer.DispatchWriterError):
        writer.write_dispatch_record(**_writer_kwargs(fixture))
    assert retained is not None
    assert not fixture["dispatch_path"].exists()
    assert list(outside.iterdir()) == []
    assert list(retained.glob("*.dispatch_record.json")) == []


def test_partial_dispatch_write_is_integrity_critical_and_preserved(
    fixture, monkeypatch
):
    real_write_all = writer._write_all
    calls = 0

    def partial_target(fd, raw):
        nonlocal calls
        calls += 1
        if calls == 2:
            os.write(fd, raw[:17])
            raise OSError("synthetic partial dispatch write")
        return real_write_all(fd, raw)

    monkeypatch.setattr(writer, "_write_all", partial_target)
    with pytest.raises(
        writer.DispatchWriterIntegrityCriticalError,
        match="durable verification is uncertain",
    ):
        writer.write_dispatch_record(**_writer_kwargs(fixture))
    assert fixture["dispatch_path"].read_bytes() == (
        serialize_derived_dispatch_record(
            manifest=fixture["manifest"],
            manifest_raw=fixture["manifest_raw"],
            authorization=fixture["authorization"],
            authorization_raw=fixture["authorization_raw"],
        )[:17]
    )
    assert (
        validate_dispatch_authorization(
            repo_root=fixture["root"],
            authorization_path=fixture["authorization_path"],
            scan_history=False,
        )["lifecycle_state"]
        == "created"
    )


@pytest.mark.parametrize("failure", ["file_fsync", "reread"])
def test_dispatch_durability_uncertainty_preserves_exact_evidence(
    fixture, monkeypatch, failure
):
    expected_raw = serialize_derived_dispatch_record(
        manifest=fixture["manifest"],
        manifest_raw=fixture["manifest_raw"],
        authorization=fixture["authorization"],
        authorization_raw=fixture["authorization_raw"],
    )
    if failure == "file_fsync":
        real_fsync = writer._AnchoredFile.fsync

        def fail_target_fsync(self):
            if self.name.endswith(".dispatch_record.json"):
                raise OSError("synthetic target fsync failure")
            return real_fsync(self)

        monkeypatch.setattr(
            writer._AnchoredFile, "fsync", fail_target_fsync
        )
    else:
        real_verify = writer._AnchoredDirectory.verify_reference

        def fail_target_reread(self, name, **kwargs):
            if name.endswith(".dispatch_record.json"):
                raise OSError("synthetic target reread ambiguity")
            return real_verify(self, name, **kwargs)

        monkeypatch.setattr(
            writer._AnchoredDirectory,
            "verify_reference",
            fail_target_reread,
        )
    with pytest.raises(writer.DispatchWriterIntegrityCriticalError):
        writer.write_dispatch_record(**_writer_kwargs(fixture))
    assert fixture["dispatch_path"].read_bytes() == expected_raw
    rows, _ = read_and_validate_dispatch_authorization_audit(
        repo_root=fixture["root"]
    )
    assert rows[-1][0]["event_type"] == "authorization_created"


def test_dispatch_lock_cleanup_uncertainty_never_returns_success(
    fixture, monkeypatch
):
    real_delete = writer._AnchoredFile.delete

    def fail_lock_delete(self):
        if self.name == writer.LOCK_PATH.name:
            raise OSError("synthetic lock cleanup failure")
        return real_delete(self)

    monkeypatch.setattr(writer._AnchoredFile, "delete", fail_lock_delete)
    with pytest.raises(
        writer.DispatchWriterIntegrityCriticalError,
        match="lock cleanup failed",
    ) as caught:
        writer.write_dispatch_record(**_writer_kwargs(fixture))
    assert caught.value.dispatch_durable is True
    assert fixture["dispatch_path"].is_file()
    validation = validate_dispatch_record_for_authorization(
        repo_root=fixture["root"],
        dispatch_path=fixture["dispatch_path"],
    )
    assert validation["lifecycle_state"] == "consumed"
    assert (fixture["root"] / writer.LOCK_PATH).is_file()


def test_shared_kdauth_lock_cleanup_uncertainty_preserves_record(
    fixture, monkeypatch
):
    real_exit = reservation.CrossingLock.__exit__
    calls = 0

    def fail_first_cleanup(self, exc_type, exc, traceback):
        nonlocal calls
        calls += 1
        result = real_exit(self, exc_type, exc, traceback)
        if calls == 1:
            raise (
                reservation
                .DispatchAuthorizationReservationIntegrityCriticalError(
                    "synthetic shared lock cleanup uncertainty"
                )
            )
        return result

    monkeypatch.setattr(
        reservation.CrossingLock, "__exit__", fail_first_cleanup
    )
    with pytest.raises(
        writer.DispatchWriterIntegrityCriticalError,
        match="protected lock",
    ):
        writer.write_dispatch_record(**_writer_kwargs(fixture))
    assert fixture["dispatch_path"].is_file()
    assert len(
        collect_dispatch_without_consumption_findings(
            repo_root=fixture["root"]
        )
    ) == 1


def test_post_write_validation_uncertainty_preserves_record(
    fixture, monkeypatch
):
    def fail_validation(**kwargs):
        del kwargs
        raise DispatchAuthorizationError(
            "synthetic post-write validation failure"
        )

    monkeypatch.setattr(
        writer,
        "validate_dispatch_authorization_for_consumption",
        fail_validation,
    )
    with pytest.raises(writer.DispatchWriterIntegrityCriticalError):
        writer.write_dispatch_record(**_writer_kwargs(fixture))
    assert fixture["dispatch_path"].is_file()
    assert len(
        collect_dispatch_without_consumption_findings(
            repo_root=fixture["root"]
        )
    ) == 1


def test_concurrent_writers_commit_exactly_one_dispatch(fixture):
    kwargs = _writer_kwargs(fixture)

    def run():
        try:
            return ("ok", writer.write_dispatch_record(**kwargs))
        except writer.DispatchWriterError as exc:
            return ("stopped", str(exc))

    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(lambda _: run(), range(2)))
    assert [status for status, _ in outcomes].count("ok") == 1
    assert [status for status, _ in outcomes].count("stopped") == 1
    assert fixture["dispatch_path"].is_file()
    assert collect_dispatch_without_consumption_findings(
        repo_root=fixture["root"]
    ) == []


def test_read_only_sql_integrity_view_exposes_unconsumed_dispatch(
    fixture, monkeypatch
):
    def fail_before_append(**kwargs):
        del kwargs
        raise RuntimeError("synthetic lifecycle interruption")

    monkeypatch.setattr(
        writer,
        "append_dispatch_authorization_lifecycle_event",
        fail_before_append,
    )
    with pytest.raises(writer.DispatchWriterIntegrityCriticalError):
        writer.write_dispatch_record(**_writer_kwargs(fixture))
    before = {
        path.relative_to(fixture["root"]).as_posix(): _hash(path.read_bytes())
        for path in fixture["root"].rglob("*")
        if path.is_file() and ".git" not in path.parts
    }
    monkeypatch.setattr(query_layer, "REPO_ROOT", fixture["root"])
    tail = query_layer.VIEWS_PATH.read_text(encoding="utf-8").split(
        "-- Which valid canonical dispatches lack their exact KDAUTH "
        "consumption event?",
        1,
    )[1]
    conn = duckdb.connect(database=":memory:")
    try:
        query_layer._register_dispatch_without_consumption_findings(conn)
        conn.execute(tail)
        rows = conn.execute(
            "SELECT dispatch_id FROM "
            "v_integrity_dispatch_authorization_dispatch_without_consumption"
        ).fetchall()
    finally:
        conn.close()
    assert rows == [
        (fixture["manifest"]["crossing_identities"]["dispatch_id"],)
    ]
    after = {
        path.relative_to(fixture["root"]).as_posix(): _hash(path.read_bytes())
        for path in fixture["root"].rglob("*")
        if path.is_file() and ".git" not in path.parts
    }
    assert after == before
