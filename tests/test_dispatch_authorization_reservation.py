import copy
import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest
from jsonschema import Draft7Validator

import tools.canon_intake.dispatch_authorization_reservation as reservation
from tools.canon_intake.dispatch_authorization_reservation import (
    DispatchAuthorizationReservationError,
    DispatchAuthorizationReservationIntegrityCriticalError,
    append_dispatch_authorization_crossing_terminal_locked,
    collect_dispatch_authorization_crossing_findings,
    dispatch_authorization_crossing_lock,
    repo_canonical_json_v1,
    reserve_dispatch_authorization_crossing_locked,
    scan_dispatch_authorization_reservations,
    validate_dispatch_authorization_reservation_stream,
)


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
def source_repo() -> Path:
    return Path(__file__).resolve().parents[1]


@pytest.fixture
def synthetic_repo(tmp_path: Path, source_repo: Path) -> Path:
    root = tmp_path / "repo"
    schema_dir = root / "research/schemas"
    schema_dir.mkdir(parents=True)
    shutil.copy2(
        source_repo
        / "research/schemas"
        / reservation.SCHEMA_NAME,
        schema_dir / reservation.SCHEMA_NAME,
    )
    _git(root, "init", "-q")
    _commit(root, "fixture schema")
    return root


def _non_authority() -> dict:
    return {
        "control_plane_integrity_history_only": True,
        "not_dispatch_authorization": True,
        "not_karl_approval": True,
        "not_kdauth_lifecycle_event": True,
        "does_not_create_dispatch": True,
        "does_not_create_execution_event": True,
        "does_not_invoke_runner": True,
        "not_result_population_authority": True,
        "not_ranking_recommendation_authority": True,
        "not_candidate_readiness_promotion_authority": True,
        "not_retry_recovery_authority": True,
        "not_scheduler_runtime_authority": True,
        "not_paper_live_authority": True,
        "not_oms_risk_reconciliation_authority": True,
        "not_broker_exchange_order_capital_authority": True,
    }


def _attempt_event(
    *,
    attempt_id: str = "KDAUTH-XING-20260724-TEST0001",
    authorization_id: str = "KDAUTH-TEST-R2-9001",
    dispatch_id: str = "DSP-20260724-TEST0001",
    run_id: str = "RUN-20260724-TEST0001",
    queue_item_id: str = "QI-20260724-TEST0001",
) -> dict:
    path = (
        "research/queue/dispatch_authorization_reservations/"
        f"{attempt_id}.crossing_reservation.jsonl"
    )
    return {
        "schema_version": reservation.SCHEMA_VERSION,
        "event_id": f"{attempt_id}-000001",
        "sequence_number": 1,
        "event_type": "attempt_reserved",
        "attempt_id": attempt_id,
        "reservation_stream_path": path,
        "authorization_binding": {
            "authorization_id": authorization_id,
            "authorization_target_path": (
                "research/queue/dispatch_authorizations/"
                f"{authorization_id}.dispatch_authorization.json"
            ),
            "authorization_core_sha256": "sha256:" + "1" * 64,
            "authorization_core_hash_scope":
                "dispatch_authorization_core_v1",
            "authorization_core_canonicalization":
                "repo_canonical_json_v1",
        },
        "dispatch_binding": {
            "dispatch_id": dispatch_id,
            "dispatch_record_path": (
                "research/queue/dispatch_records/"
                f"{dispatch_id}.dispatch_record.json"
            ),
        },
        "run_binding": {
            "run_id": run_id,
            "execution_event_stream_path": (
                "research/queue/execution_events/"
                f"{run_id}.execution_events.jsonl"
            ),
        },
        "queue_binding": {
            "queue_item_id": queue_item_id,
            "authorization_id": authorization_id,
            "queue_authorization_pair_scope":
                "queue_item_and_dispatch_authorization",
        },
        "reviewed_content_binding": {
            "reviewed_whole_file_sha256": "sha256:" + "2" * 64,
            "reviewed_byte_length": 1234,
            "reviewed_content_scope":
                "exact_kdauth_whole_file_bytes_including_final_lf",
        },
        "reserved_at": "2026-07-24T12:00:00Z",
        "occurred_at": "2026-07-24T12:00:00Z",
        "actor": "Karl",
        "writer_identity": reservation.WRITER_IDENTITY,
        "identities_permanently_reserved": True,
        "automatic_retry_with_same_identities_forbidden": True,
        "event_payload": {
            "reservation_committed_before_kdauth_mutation": True,
            "kdauth_target_mutation_started": False,
            "kdauth_lifecycle_mutation_started": False,
            "reservation_commit_posture":
                "exclusive_create_complete_write_fsync_verified",
            "terminal_outcome_pending": True,
        },
        "non_authority_declaration": _non_authority(),
    }


def _terminal(initial: dict, event_type: str) -> dict:
    event = copy.deepcopy(initial)
    event["event_id"] = f"{initial['attempt_id']}-000002"
    event["sequence_number"] = 2
    event["event_type"] = event_type
    event["occurred_at"] = "2026-07-24T12:01:00Z"
    if event_type == "crossing_rolled_back_clean":
        event["event_payload"] = {
            "terminal_outcome": event_type,
            "kdauth_target_absence_proven": True,
            "lifecycle_audit_restored_to_exact_prior_length": True,
            "prior_lifecycle_audit_byte_length": 0,
            "final_lifecycle_audit_byte_length": 0,
            "rollback_durability_proven": True,
            "durability_uncertainty": False,
            "operator_inspection_required": False,
            "terminal_is_permanent": True,
        }
    elif event_type == "crossing_integrity_critical":
        event["event_payload"] = {
            "terminal_outcome": event_type,
            "operator_inspection_required": True,
            "terminal_is_permanent": True,
            "failure_phase": "kdauth_target_fsync",
            "uncertainty_class": "durability_not_proven",
            "kdauth_target_state": "unknown",
            "lifecycle_audit_state": "unchanged",
        }
    elif event_type == "crossing_committed":
        event["event_payload"] = {
            "terminal_outcome": event_type,
            "kdauth_target_durable": True,
            "authorization_created_durable": True,
            "resulting_authorization_path": initial[
                "authorization_binding"
            ]["authorization_target_path"],
            "resulting_authorization_whole_file_sha256": initial[
                "reviewed_content_binding"
            ]["reviewed_whole_file_sha256"],
            "resulting_authorization_byte_length": initial[
                "reviewed_content_binding"
            ]["reviewed_byte_length"],
            "resulting_authorization_core_sha256": initial[
                "authorization_binding"
            ]["authorization_core_sha256"],
            "lifecycle_audit_path": reservation.AUDIT_PATH.as_posix(),
            "authorization_created_event_id":
                "KDAUTH-EVENT-KDAUTH-TEST-R2-9001-000001",
            "lifecycle_event_sequence_number": 1,
            "lifecycle_raw_line_sha256": "sha256:" + "3" * 64,
            "lifecycle_raw_line_byte_length": 999,
            "rollback_performed": False,
            "operator_inspection_required": False,
            "terminal_is_permanent": True,
        }
    else:
        raise AssertionError(event_type)
    return event


def _stream_path(root: Path, event: dict) -> Path:
    return root / Path(event["reservation_stream_path"])


def _write_stream(root: Path, *events: dict) -> Path:
    path = _stream_path(root, events[0])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(
        b"".join(repo_canonical_json_v1(event) + b"\n" for event in events)
    )
    return path


def test_schema_is_closed_valid_draft7(source_repo: Path) -> None:
    schema = json.loads(
        (
            source_repo
            / "research/schemas"
            / reservation.SCHEMA_NAME
        ).read_text(encoding="utf-8")
    )
    Draft7Validator.check_schema(schema)
    assert schema["$schema"] == "http://json-schema.org/draft-07/schema#"
    assert schema["$id"] == reservation.SCHEMA_NAME

    def walk(value):
        if isinstance(value, dict):
            if value.get("type") == "object":
                assert value.get("additionalProperties") is False
            for child in value.values():
                walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)

    walk(schema)


@pytest.mark.parametrize(
    "event_type",
    [
        "crossing_committed",
        "crossing_rolled_back_clean",
        "crossing_integrity_critical",
    ],
)
def test_all_closed_event_shapes_validate(
    synthetic_repo: Path, event_type: str
) -> None:
    initial = _attempt_event()
    terminal = _terminal(initial, event_type)
    validator = reservation._schema_validator(synthetic_repo)
    assert list(validator.iter_errors(initial)) == []
    assert list(validator.iter_errors(terminal)) == []


def test_initial_reservation_is_exact_no_overwrite_and_lock_continues(
    synthetic_repo: Path,
) -> None:
    initial = _attempt_event()
    with dispatch_authorization_crossing_lock(
        repo_root=synthetic_repo
    ) as lock:
        result = reserve_dispatch_authorization_crossing_locked(
            lock=lock, event=initial
        )
        assert lock.acquired is True
        assert result["reservation_committed"] is True
        assert result["directory_fsync_status"] in {
            "verified",
            "not_supported_on_platform",
        }
        path = _stream_path(synthetic_repo, initial)
        assert path.read_bytes() == repo_canonical_json_v1(initial) + b"\n"
        with pytest.raises(
            DispatchAuthorizationReservationError,
            match="single-use|consumed",
        ):
            reserve_dispatch_authorization_crossing_locked(
                lock=lock, event=initial
            )
    assert not (
        synthetic_repo / reservation.CROSSING_LOCK_PATH
    ).exists()


def test_clean_rollback_terminal_is_append_only_and_burns_identity(
    synthetic_repo: Path,
) -> None:
    initial = _attempt_event()
    terminal = _terminal(initial, "crossing_rolled_back_clean")
    with dispatch_authorization_crossing_lock(
        repo_root=synthetic_repo
    ) as lock:
        reserve_dispatch_authorization_crossing_locked(
            lock=lock, event=initial
        )
        result = append_dispatch_authorization_crossing_terminal_locked(
            lock=lock, event=terminal
        )
        assert result["terminal_outcome"] == "crossing_rolled_back_clean"
        with pytest.raises(
            DispatchAuthorizationReservationError,
            match="already has a terminal",
        ):
            append_dispatch_authorization_crossing_terminal_locked(
                lock=lock, event=terminal
            )
    validated = validate_dispatch_authorization_reservation_stream(
        repo_root=synthetic_repo,
        reservation_path=_stream_path(synthetic_repo, initial),
        require_terminal=True,
    )
    assert validated["event_count"] == 2
    assert validated["findings"] == []


def test_integrity_critical_terminal_is_visible(
    synthetic_repo: Path,
) -> None:
    initial = _attempt_event()
    terminal = _terminal(initial, "crossing_integrity_critical")
    with dispatch_authorization_crossing_lock(
        repo_root=synthetic_repo
    ) as lock:
        reserve_dispatch_authorization_crossing_locked(
            lock=lock, event=initial
        )
        append_dispatch_authorization_crossing_terminal_locked(
            lock=lock, event=terminal
        )
    findings = collect_dispatch_authorization_crossing_findings(
        repo_root=synthetic_repo
    )
    assert [row["finding_type"] for row in findings] == [
        "crossing_integrity_critical"
    ]
    assert findings[0]["operator_inspection_required"] is True
    assert findings[0]["non_authority"] is True


def test_missing_terminal_is_visible_and_still_burns(
    synthetic_repo: Path,
) -> None:
    initial = _attempt_event()
    with dispatch_authorization_crossing_lock(
        repo_root=synthetic_repo
    ) as lock:
        reserve_dispatch_authorization_crossing_locked(
            lock=lock, event=initial
        )
    findings = collect_dispatch_authorization_crossing_findings(
        repo_root=synthetic_repo
    )
    assert findings[0]["finding_type"] == "attempt_reserved_without_terminal"
    assert findings[0]["reason_code"] == "terminal_missing"


def test_terminal_common_binding_drift_and_extra_event_fail_closed(
    synthetic_repo: Path,
) -> None:
    initial = _attempt_event()
    terminal = _terminal(initial, "crossing_integrity_critical")
    terminal["run_binding"]["run_id"] = "RUN-20260724-DIFFER01"
    path = _write_stream(synthetic_repo, initial, terminal)
    with pytest.raises(
        DispatchAuthorizationReservationError,
        match="binding mismatch|not derived",
    ):
        validate_dispatch_authorization_reservation_stream(
            repo_root=synthetic_repo,
            reservation_path=path,
        )
    path.write_bytes(
        repo_canonical_json_v1(initial)
        + b"\n"
        + repo_canonical_json_v1(_terminal(
            initial, "crossing_integrity_critical"
        ))
        + b"\n"
        + repo_canonical_json_v1(_terminal(
            initial, "crossing_integrity_critical"
        ))
        + b"\n"
    )
    with pytest.raises(
        DispatchAuthorizationReservationError, match="one or two"
    ):
        validate_dispatch_authorization_reservation_stream(
            repo_root=synthetic_repo,
            reservation_path=path,
        )


@pytest.mark.parametrize(
    "mutation,match",
    [
        (lambda raw: b"\xef\xbb\xbf" + raw, "BOM"),
        (lambda raw: raw.replace(b"\n", b"\r\n"), "LF"),
        (lambda raw: raw.rstrip(b"\n"), "partial tail"),
        (lambda raw: raw + b"\n", "blank line|one or two"),
    ],
)
def test_serialization_drift_fails_closed(
    synthetic_repo: Path, mutation, match: str
) -> None:
    initial = _attempt_event()
    path = _write_stream(synthetic_repo, initial)
    path.write_bytes(mutation(path.read_bytes()))
    with pytest.raises(DispatchAuthorizationReservationError, match=match):
        validate_dispatch_authorization_reservation_stream(
            repo_root=synthetic_repo,
            reservation_path=path,
        )


def test_retained_deleted_stream_still_burns_all_bound_identities(
    synthetic_repo: Path,
) -> None:
    initial = _attempt_event()
    terminal = _terminal(initial, "crossing_integrity_critical")
    path = _write_stream(synthetic_repo, initial, terminal)
    _commit(synthetic_repo, "reserve and terminate")
    path.unlink()
    _commit(synthetic_repo, "delete without releasing identities")
    scans = scan_dispatch_authorization_reservations(
        repo_root=synthetic_repo,
        include_retained_history=True,
    )
    assert any(
        result["attempt_id"] == initial["attempt_id"] for result in scans
    )
    replacement = _attempt_event(
        attempt_id="KDAUTH-XING-20260724-TEST0002"
    )
    with dispatch_authorization_crossing_lock(
        repo_root=synthetic_repo
    ) as lock:
        with pytest.raises(
            DispatchAuthorizationReservationError,
            match="permanently consumed",
        ):
            reserve_dispatch_authorization_crossing_locked(
                lock=lock, event=replacement
            )


def test_existing_dispatch_surface_blocks_reservation(
    synthetic_repo: Path,
) -> None:
    initial = _attempt_event()
    dispatch = {
        "dispatch_id": initial["dispatch_binding"]["dispatch_id"],
        "dispatch_record_path": initial["dispatch_binding"][
            "dispatch_record_path"
        ],
        "queue_binding": {
            "queue_item_id": initial["queue_binding"]["queue_item_id"]
        },
        "run_binding": {
            "run_id": initial["run_binding"]["run_id"],
            "execution_event_stream_path": initial["run_binding"][
                "execution_event_stream_path"
            ],
        },
        "dispatch_authorization": {
            "authorization_id": "KDAUTH-OTHER-R2-9002",
            "source_path": (
                "research/queue/dispatch_authorizations/"
                "KDAUTH-OTHER-R2-9002.dispatch_authorization.json"
            ),
        },
    }
    dispatch_path = synthetic_repo / initial["dispatch_binding"][
        "dispatch_record_path"
    ]
    dispatch_path.parent.mkdir(parents=True)
    dispatch_path.write_text(json.dumps(dispatch), encoding="utf-8")
    with dispatch_authorization_crossing_lock(
        repo_root=synthetic_repo
    ) as lock:
        with pytest.raises(
            DispatchAuthorizationReservationError,
            match="control-plane history already consumes",
        ):
            reserve_dispatch_authorization_crossing_locked(
                lock=lock, event=initial
            )


def test_prepublication_failure_never_creates_authoritative_target(
    synthetic_repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    initial = _attempt_event()

    def fail_link(source, target):
        raise OSError(errno := 5, os.strerror(errno))

    monkeypatch.setattr(reservation.os, "link", fail_link)
    with dispatch_authorization_crossing_lock(
        repo_root=synthetic_repo
    ) as lock:
        with pytest.raises(
            DispatchAuthorizationReservationError,
            match="before publication",
        ):
            reserve_dispatch_authorization_crossing_locked(
                lock=lock, event=initial
            )
    assert not _stream_path(synthetic_repo, initial).exists()
    reservation_root = synthetic_repo / reservation.RESERVATION_ROOT
    assert list(reservation_root.glob("*.tmp")) == []


def test_partial_terminal_failure_never_truncates_initial(
    synthetic_repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    initial = _attempt_event()
    terminal = _terminal(initial, "crossing_integrity_critical")
    with dispatch_authorization_crossing_lock(
        repo_root=synthetic_repo
    ) as lock:
        reserve_dispatch_authorization_crossing_locked(
            lock=lock, event=initial
        )
        original_write = reservation._write_all

        def partial_write(fd: int, raw: bytes) -> None:
            os.write(fd, raw[:5])
            raise OSError("synthetic partial append")

        monkeypatch.setattr(reservation, "_write_all", partial_write)
        with pytest.raises(
            DispatchAuthorizationReservationIntegrityCriticalError,
            match="initial reservation remains authoritative",
        ):
            append_dispatch_authorization_crossing_terminal_locked(
                lock=lock, event=terminal
            )
        monkeypatch.setattr(reservation, "_write_all", original_write)
    raw = _stream_path(synthetic_repo, initial).read_bytes()
    assert raw.startswith(repo_canonical_json_v1(initial) + b"\n")
    assert len(raw) > len(repo_canonical_json_v1(initial) + b"\n")


def test_authorization_created_without_prior_reservation_is_visible(
    synthetic_repo: Path,
) -> None:
    audit = synthetic_repo / reservation.AUDIT_PATH
    audit.parent.mkdir(parents=True, exist_ok=True)
    authorization_rel = (
        "research/queue/dispatch_authorizations/"
        "KDAUTH-TEST-R2-9001.dispatch_authorization.json"
    )
    authorization_path = synthetic_repo / authorization_rel
    authorization_path.parent.mkdir(parents=True, exist_ok=True)
    authorization = {
        "authorization_id": "KDAUTH-TEST-R2-9001",
        "authorization_artifact_target_path": authorization_rel,
        "authorization_core_sha256": "sha256:" + "1" * 64,
    }
    authorization_raw = (
        json.dumps(
            authorization,
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
        )
        + "\n"
    ).encode("utf-8")
    authorization_path.write_bytes(authorization_raw)
    creation = {
        "event_type": "authorization_created",
        "event_id": "KDAUTH-EVENT-KDAUTH-TEST-R2-9001-000001",
        "sequence_number": 1,
        "authorization_id": "KDAUTH-TEST-R2-9001",
        "authorization_path": authorization_rel,
        "authorization_file_sha256": reservation._digest(authorization_raw),
        "authorization_byte_length": len(authorization_raw),
        "authorization_core_sha256": "sha256:" + "1" * 64,
        "queue_item_id": "QI-20260724-TEST0001",
        "dispatch_id": "DSP-20260724-TEST0001",
        "run_id": "RUN-20260724-TEST0001",
        "occurred_at": "2026-07-24T12:01:00Z",
    }
    audit.write_bytes(repo_canonical_json_v1(creation) + b"\n")
    findings = collect_dispatch_authorization_crossing_findings(
        repo_root=synthetic_repo
    )
    assert [row["finding_type"] for row in findings] == [
        "authorization_created_without_prior_crossing_reservation"
    ]


def test_query_registration_exposes_synthetic_integrity_critical(
    synthetic_repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import duckdb

    from tools.research_query import query_layer

    initial = _attempt_event()
    _write_stream(
        synthetic_repo,
        initial,
        _terminal(initial, "crossing_integrity_critical"),
    )
    monkeypatch.setattr(query_layer, "REPO_ROOT", synthetic_repo)
    conn = duckdb.connect(database=":memory:")
    query_layer._register_dispatch_authorization_crossing_reservation_findings(
        conn
    )
    conn.execute(
        """
        CREATE VIEW v_integrity_dispatch_authorization_crossing_reservations AS
        SELECT * FROM dispatch_authorization_crossing_reservation_findings
        """
    )
    rows = query_layer.run_named_view(
        conn,
        "v_integrity_dispatch_authorization_crossing_reservations",
    )
    assert rows[0]["finding_type"] == "crossing_integrity_critical"
    assert rows[0]["reason_code"] == "recorded_integrity_critical"
    assert rows[0]["operator_inspection_required"] is True
    conn.close()
