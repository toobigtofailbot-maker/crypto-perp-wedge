import copy
import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest
from jsonschema import Draft7Validator

import tools.canon_intake.dispatch_authorization as authorization_validator
import tools.canon_intake.dispatch_authorization_reservation as reservation
from tests import test_dispatch_authorization as authorization_test_support
from tools.canon_intake.dispatch_authorization import (
    DispatchAuthorizationError,
    validate_dispatch_authorization,
)
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
    for schema_name in (
        reservation.SCHEMA_NAME,
        "canon_dispatch_authorization_audit_event.schema.json",
    ):
        shutil.copy2(
            source_repo / "research/schemas" / schema_name,
            schema_dir / schema_name,
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


def _audit_event(
    index: int,
    *,
    authorization_id: str | None = None,
) -> dict:
    token = f"AUDIT{index:03d}"
    selected_id = authorization_id or f"KDAUTH-{token}-R2-{9100 + index}"
    return {
        "schema_version": "canon_dispatch_authorization_audit_event_v1",
        "event_id": f"KDAUTH-EVENT-{selected_id}-000001",
        "sequence_number": 1,
        "event_type": "authorization_created",
        "authorization_id": selected_id,
        "authorization_path": (
            "research/queue/dispatch_authorizations/"
            f"{selected_id}.dispatch_authorization.json"
        ),
        "authorization_file_sha256": "sha256:" + f"{index:x}"[-1] * 64,
        "authorization_byte_length": 1000 + index,
        "authorization_core_sha256": "sha256:" + f"{index + 8:x}"[-1] * 64,
        "authorization_core_hash_scope": "dispatch_authorization_core_v1",
        "queue_item_id": f"QI-20260724-{token}",
        "dispatch_id": f"DSP-20260724-{token}",
        "run_id": f"RUN-20260724-{token}",
        "occurred_at": f"2026-07-24T12:{10 + index:02d}:00Z",
        "actor": "Karl",
        "tool_identity": "synthetic-kdauth-writer-v1",
        "event_payload": {
            "event_kind": "authorization_created",
            "creation_posture": "protected_exclusive_create",
        },
        "non_authority_declaration": {
            "lifecycle_history_only": True,
            "does_not_invoke_runner": True,
            "not_result_population_authority": True,
            "not_ranking_recommendation_authority": True,
            "not_candidate_readiness_promotion_authority": True,
            "not_runtime_paper_live_authority": True,
        },
    }


def _write_audit(root: Path, *events: dict) -> tuple[Path, int]:
    raw = b"".join(
        repo_canonical_json_v1(event) + b"\n" for event in events
    )
    path = root / reservation.AUDIT_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)
    return path, len(raw)


def _audit_terminal_event(
    created: dict,
    *,
    event_type: str = "authorization_revoked",
) -> dict:
    terminal = copy.deepcopy(created)
    terminal["event_id"] = (
        f"KDAUTH-EVENT-{created['authorization_id']}-000002"
    )
    terminal["sequence_number"] = 2
    terminal["event_type"] = event_type
    terminal["occurred_at"] = "2026-07-24T13:00:00Z"
    if event_type == "authorization_revoked":
        terminal["event_payload"] = {
            "event_kind": "authorization_revoked",
            "reason": "synthetic lifecycle terminal",
        }
    elif event_type == "authorization_consumed":
        terminal["event_payload"] = {
            "event_kind": "authorization_consumed",
            "consumer_tool": "synthetic-dispatch-writer-v1",
            "dispatch_record_path": (
                "research/queue/dispatch_records/"
                f"{created['dispatch_id']}.dispatch_record.json"
            ),
            "consumption_is_permanent": True,
        }
    else:
        raise AssertionError(event_type)
    return terminal


def _assert_invalid_audit_fails_clean_rollback_replay(
    root: Path,
    *events: dict,
) -> None:
    initial = _attempt_event()
    terminal = _terminal(initial, "crossing_rolled_back_clean")
    path = _write_stream(root, initial, terminal)
    audit_path, audit_length = _write_audit(root, *events)
    expected_raw = b"".join(
        repo_canonical_json_v1(event) + b"\n" for event in events
    )
    assert audit_length > terminal["event_payload"][
        "final_lifecycle_audit_byte_length"
    ]
    assert audit_path.read_bytes() == expected_raw
    assert expected_raw.endswith(b"\n")

    with pytest.raises(
        DispatchAuthorizationReservationError,
        match="lifecycle audit validation failed",
    ):
        reservation._validate_clean_rollback_replay(
            root.resolve(), initial, terminal
        )

    validated = validate_dispatch_authorization_reservation_stream(
        repo_root=root,
        reservation_path=path,
        require_terminal=True,
    )
    assert "reservation_terminal_binding_mismatch" in {
        row["finding_type"] for row in validated["findings"]
    }
    findings = collect_dispatch_authorization_crossing_findings(
        repo_root=root
    )
    assert "reservation_terminal_binding_mismatch" in {
        row["finding_type"] for row in findings
    }


def _distinct_attempt(suffix: str) -> dict:
    return _attempt_event(
        attempt_id=f"KDAUTH-XING-20260724-{suffix}",
        authorization_id=f"KDAUTH-{suffix}-R2-9002",
        dispatch_id=f"DSP-20260724-{suffix}",
        run_id=f"RUN-20260724-{suffix}",
        queue_item_id=f"QI-20260724-{suffix}",
    )


def _symlink_or_skip(
    link: Path,
    target: Path,
    *,
    target_is_directory: bool,
) -> None:
    try:
        link.symlink_to(target, target_is_directory=target_is_directory)
    except OSError:
        pytest.skip("this environment cannot create the required symlink")


@pytest.mark.parametrize(
    "value",
    [
        "../escape",
        "research\\queue\\escape",
        "/absolute/escape",
        "research//queue/escape",
        "research/./queue/escape",
        "C:/absolute/escape",
    ],
)
def test_repo_path_rejects_nonlexical_relative_posix_forms(
    synthetic_repo: Path, value: str
) -> None:
    with pytest.raises(
        DispatchAuthorizationReservationError,
        match="repo-relative|traversal",
    ):
        reservation._repo_path(synthetic_repo.resolve(), value, "test path")


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


def test_clean_rollback_exact_current_audit_length_allows_terminal_append(
    synthetic_repo: Path,
) -> None:
    _, audit_length = _write_audit(synthetic_repo, _audit_event(1))
    initial = _attempt_event()
    terminal = _terminal(initial, "crossing_rolled_back_clean")
    terminal["event_payload"]["prior_lifecycle_audit_byte_length"] = (
        audit_length
    )
    terminal["event_payload"]["final_lifecycle_audit_byte_length"] = (
        audit_length
    )

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
    assert result["validation"]["findings"] == []


def test_clean_rollback_stale_declared_length_rejected_before_append(
    synthetic_repo: Path,
) -> None:
    _write_audit(synthetic_repo, _audit_event(1))
    initial = _attempt_event()
    terminal = _terminal(initial, "crossing_rolled_back_clean")

    with dispatch_authorization_crossing_lock(
        repo_root=synthetic_repo
    ) as lock:
        reserve_dispatch_authorization_crossing_locked(
            lock=lock, event=initial
        )
        with pytest.raises(
            DispatchAuthorizationReservationError,
            match="stale before terminal append",
        ):
            append_dispatch_authorization_crossing_terminal_locked(
                lock=lock, event=terminal
            )
    validated = validate_dispatch_authorization_reservation_stream(
        repo_root=synthetic_repo,
        reservation_path=_stream_path(synthetic_repo, initial),
    )
    assert validated["event_count"] == 1


@pytest.mark.parametrize("append_count", [1, 3])
def test_clean_rollback_replay_allows_unrelated_later_audit_appends(
    synthetic_repo: Path,
    append_count: int,
) -> None:
    initial = _attempt_event()
    terminal = _terminal(initial, "crossing_rolled_back_clean")
    with dispatch_authorization_crossing_lock(
        repo_root=synthetic_repo
    ) as lock:
        reserve_dispatch_authorization_crossing_locked(
            lock=lock, event=initial
        )
        append_dispatch_authorization_crossing_terminal_locked(
            lock=lock, event=terminal
        )
    _write_audit(
        synthetic_repo,
        *[_audit_event(index) for index in range(1, append_count + 1)],
    )

    validated = validate_dispatch_authorization_reservation_stream(
        repo_root=synthetic_repo,
        reservation_path=_stream_path(synthetic_repo, initial),
        require_terminal=True,
    )
    assert validated["findings"] == []
    assert collect_dispatch_authorization_crossing_findings(
        repo_root=synthetic_repo
    ) == []


def test_clean_rollback_replay_shorter_audit_fails_closed(
    synthetic_repo: Path,
) -> None:
    initial = _attempt_event()
    terminal = _terminal(initial, "crossing_rolled_back_clean")
    terminal["event_payload"]["prior_lifecycle_audit_byte_length"] = 100
    terminal["event_payload"]["final_lifecycle_audit_byte_length"] = 100
    path = _write_stream(synthetic_repo, initial, terminal)

    validated = validate_dispatch_authorization_reservation_stream(
        repo_root=synthetic_repo,
        reservation_path=path,
        require_terminal=True,
    )
    assert [row["finding_type"] for row in validated["findings"]] == [
        "reservation_terminal_binding_mismatch"
    ]
    with pytest.raises(
        DispatchAuthorizationReservationError,
        match="shorter than the recorded final length",
    ):
        reservation._validate_clean_rollback_replay(
            synthetic_repo.resolve(), initial, terminal
        )


@pytest.mark.parametrize(
    "extension",
    [
        b'{"malformed":true',
        b'{"malformed":}\n',
    ],
)
def test_clean_rollback_replay_rejects_partial_or_malformed_audit_extension(
    synthetic_repo: Path,
    extension: bytes,
) -> None:
    initial = _attempt_event()
    terminal = _terminal(initial, "crossing_rolled_back_clean")
    path = _write_stream(synthetic_repo, initial, terminal)
    audit = synthetic_repo / reservation.AUDIT_PATH
    audit.parent.mkdir(parents=True, exist_ok=True)
    audit.write_bytes(extension)

    validated = validate_dispatch_authorization_reservation_stream(
        repo_root=synthetic_repo,
        reservation_path=path,
        require_terminal=True,
    )
    assert [row["finding_type"] for row in validated["findings"]] == [
        "reservation_terminal_binding_mismatch"
    ]


def test_clean_rollback_replay_matching_later_creation_is_a_finding(
    synthetic_repo: Path,
) -> None:
    initial = _attempt_event()
    terminal = _terminal(initial, "crossing_rolled_back_clean")
    path = _write_stream(synthetic_repo, initial, terminal)
    _write_audit(
        synthetic_repo,
        _audit_event(
            1,
            authorization_id=initial["authorization_binding"][
                "authorization_id"
            ],
        ),
    )

    validated = validate_dispatch_authorization_reservation_stream(
        repo_root=synthetic_repo,
        reservation_path=path,
        require_terminal=True,
    )
    assert [row["finding_type"] for row in validated["findings"]] == [
        "reservation_terminal_binding_mismatch"
    ]


def test_clean_rollback_replay_rejects_canonical_schema_missing_audit_line(
    synthetic_repo: Path,
) -> None:
    _assert_invalid_audit_fails_clean_rollback_replay(
        synthetic_repo,
        {"malformed_but_canonical": True},
    )


def test_clean_rollback_replay_rejects_schema_invalid_lifecycle_field(
    synthetic_repo: Path,
) -> None:
    invalid = _audit_event(1)
    invalid["authorization_file_sha256"] = "sha256:not-a-valid-hash"
    _assert_invalid_audit_fails_clean_rollback_replay(
        synthetic_repo,
        invalid,
    )


def test_clean_rollback_replay_rejects_unknown_lifecycle_property(
    synthetic_repo: Path,
) -> None:
    invalid = _audit_event(1)
    invalid["unexpected_closed_schema_field"] = True
    _assert_invalid_audit_fails_clean_rollback_replay(
        synthetic_repo,
        invalid,
    )


def test_clean_rollback_replay_rejects_lifecycle_terminal_before_creation(
    synthetic_repo: Path,
) -> None:
    invalid = _audit_terminal_event(_audit_event(1))
    invalid["sequence_number"] = 1
    invalid["event_id"] = (
        f"KDAUTH-EVENT-{invalid['authorization_id']}-000001"
    )
    _assert_invalid_audit_fails_clean_rollback_replay(
        synthetic_repo,
        invalid,
    )


@pytest.mark.parametrize(
    "duplicate_kind",
    ["creation", "sequence"],
)
def test_clean_rollback_replay_rejects_duplicate_lifecycle_history(
    synthetic_repo: Path,
    duplicate_kind: str,
) -> None:
    created = _audit_event(1)
    duplicate = copy.deepcopy(created)
    if duplicate_kind == "creation":
        duplicate["sequence_number"] = 2
        duplicate["event_id"] = (
            f"KDAUTH-EVENT-{created['authorization_id']}-000002"
        )
        duplicate["occurred_at"] = "2026-07-24T13:00:00Z"
    _assert_invalid_audit_fails_clean_rollback_replay(
        synthetic_repo,
        created,
        duplicate,
    )


def test_clean_rollback_replay_accepts_multiple_unrelated_valid_lifecycles(
    synthetic_repo: Path,
) -> None:
    initial = _attempt_event()
    terminal = _terminal(initial, "crossing_rolled_back_clean")
    path = _write_stream(synthetic_repo, initial, terminal)
    first = _audit_event(1)
    second = _audit_event(2)
    _write_audit(
        synthetic_repo,
        first,
        second,
        _audit_terminal_event(first),
        _audit_terminal_event(second, event_type="authorization_consumed"),
    )

    validated = validate_dispatch_authorization_reservation_stream(
        repo_root=synthetic_repo,
        reservation_path=path,
        require_terminal=True,
    )
    assert validated["findings"] == []
    assert collect_dispatch_authorization_crossing_findings(
        repo_root=synthetic_repo
    ) == []


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


def test_logical_attempt_collapses_valid_one_line_then_two_line_history(
    synthetic_repo: Path,
) -> None:
    initial = _attempt_event()
    terminal = _terminal(initial, "crossing_integrity_critical")
    path = _write_stream(synthetic_repo, initial)
    _commit(synthetic_repo, "retain initial prefix")
    _write_stream(synthetic_repo, initial, terminal)
    _commit(synthetic_repo, "append terminal")

    scans = scan_dispatch_authorization_reservations(
        repo_root=synthetic_repo,
        include_retained_history=True,
    )
    assert len(scans) == 1
    assert scans[0]["attempt_id"] == initial["attempt_id"]
    assert scans[0]["event_count"] == 2
    assert scans[0]["history_version_count"] == 2
    assert scans[0]["terminal_outcome"] == "crossing_integrity_critical"


def test_current_current_exact_duplicate_tuple_fails_closed(
    synthetic_repo: Path,
) -> None:
    first = _attempt_event()
    second = copy.deepcopy(first)
    second["attempt_id"] = "KDAUTH-XING-20260724-TEST0002"
    second["event_id"] = f"{second['attempt_id']}-000001"
    second["reservation_stream_path"] = (
        "research/queue/dispatch_authorization_reservations/"
        f"{second['attempt_id']}.crossing_reservation.jsonl"
    )
    _write_stream(synthetic_repo, first)
    _write_stream(synthetic_repo, second)

    with pytest.raises(
        DispatchAuthorizationReservationError,
        match="distinct reservation attempts collide",
    ):
        scan_dispatch_authorization_reservations(repo_root=synthetic_repo)


@pytest.mark.parametrize(
    "collision_kind,expected_field",
    [
        ("authorization", "authorization_id"),
        ("dispatch", "dispatch_id"),
        ("run", "run_id"),
        ("queue_authorization_pair", "queue_authorization_pair"),
    ],
)
def test_current_current_partial_identity_collision_fails_closed(
    synthetic_repo: Path,
    collision_kind: str,
    expected_field: str,
) -> None:
    first = _attempt_event()
    second = _distinct_attempt("PART0002")
    if collision_kind == "authorization":
        second["authorization_binding"] = copy.deepcopy(
            first["authorization_binding"]
        )
        second["queue_binding"]["authorization_id"] = first[
            "authorization_binding"
        ]["authorization_id"]
    elif collision_kind == "dispatch":
        second["dispatch_binding"] = copy.deepcopy(first["dispatch_binding"])
    elif collision_kind == "run":
        second["run_binding"] = copy.deepcopy(first["run_binding"])
    else:
        second["authorization_binding"] = copy.deepcopy(
            first["authorization_binding"]
        )
        second["queue_binding"] = copy.deepcopy(first["queue_binding"])
    _write_stream(synthetic_repo, first)
    _write_stream(synthetic_repo, second)

    with pytest.raises(
        DispatchAuthorizationReservationError,
        match=expected_field,
    ):
        scan_dispatch_authorization_reservations(repo_root=synthetic_repo)


def test_path_only_collision_is_invalid_because_paths_are_id_derived(
    synthetic_repo: Path,
) -> None:
    first = _attempt_event()
    second = _distinct_attempt("PATH0002")
    second["authorization_binding"]["authorization_target_path"] = first[
        "authorization_binding"
    ]["authorization_target_path"]
    _write_stream(synthetic_repo, first)
    _write_stream(synthetic_repo, second)

    with pytest.raises(
        DispatchAuthorizationReservationError,
        match="not derived from authorization ID",
    ):
        scan_dispatch_authorization_reservations(repo_root=synthetic_repo)


def test_current_retained_identity_collision_fails_closed(
    synthetic_repo: Path,
) -> None:
    retained = _attempt_event()
    path = _write_stream(synthetic_repo, retained)
    _commit(synthetic_repo, "retain first attempt")
    path.unlink()
    _commit(synthetic_repo, "delete first attempt")
    current = copy.deepcopy(retained)
    current["attempt_id"] = "KDAUTH-XING-20260724-TEST0002"
    current["event_id"] = f"{current['attempt_id']}-000001"
    current["reservation_stream_path"] = (
        "research/queue/dispatch_authorization_reservations/"
        f"{current['attempt_id']}.crossing_reservation.jsonl"
    )
    _write_stream(synthetic_repo, current)

    with pytest.raises(
        DispatchAuthorizationReservationError,
        match="distinct reservation attempts collide",
    ):
        scan_dispatch_authorization_reservations(repo_root=synthetic_repo)


def test_retained_retained_identity_collision_fails_closed(
    synthetic_repo: Path,
) -> None:
    first = _attempt_event()
    first_path = _write_stream(synthetic_repo, first)
    _commit(synthetic_repo, "retain first attempt")
    first_path.unlink()
    _commit(synthetic_repo, "delete first attempt")
    second = copy.deepcopy(first)
    second["attempt_id"] = "KDAUTH-XING-20260724-TEST0002"
    second["event_id"] = f"{second['attempt_id']}-000001"
    second["reservation_stream_path"] = (
        "research/queue/dispatch_authorization_reservations/"
        f"{second['attempt_id']}.crossing_reservation.jsonl"
    )
    second_path = _write_stream(synthetic_repo, second)
    _commit(synthetic_repo, "retain second attempt")
    second_path.unlink()
    _commit(synthetic_repo, "delete second attempt")

    with pytest.raises(
        DispatchAuthorizationReservationError,
        match="distinct reservation attempts collide",
    ):
        scan_dispatch_authorization_reservations(repo_root=synthetic_repo)


def test_duplicate_collision_produces_closed_integrity_rows(
    synthetic_repo: Path,
) -> None:
    first = _attempt_event()
    second = copy.deepcopy(first)
    second["attempt_id"] = "KDAUTH-XING-20260724-TEST0002"
    second["event_id"] = f"{second['attempt_id']}-000001"
    second["reservation_stream_path"] = (
        "research/queue/dispatch_authorization_reservations/"
        f"{second['attempt_id']}.crossing_reservation.jsonl"
    )
    _write_stream(synthetic_repo, first)
    _write_stream(synthetic_repo, second)

    findings = collect_dispatch_authorization_crossing_findings(
        repo_root=synthetic_repo
    )
    collision_rows = [
        row
        for row in findings
        if row["finding_type"]
        == "reservation_identity_collision_across_attempts"
    ]
    assert {row["attempt_id"] for row in collision_rows} == {
        first["attempt_id"],
        second["attempt_id"],
    }
    assert {
        row["reason_code"] for row in collision_rows
    } == {"protected_identity_collision_across_distinct_attempts"}


def test_retained_only_integrity_critical_remains_visible_after_deletion(
    synthetic_repo: Path,
) -> None:
    initial = _attempt_event()
    path = _write_stream(
        synthetic_repo,
        initial,
        _terminal(initial, "crossing_integrity_critical"),
    )
    _commit(synthetic_repo, "retain critical terminal")
    path.unlink()
    _commit(synthetic_repo, "delete critical stream")

    findings = collect_dispatch_authorization_crossing_findings(
        repo_root=synthetic_repo
    )
    assert [row["finding_type"] for row in findings] == [
        "crossing_integrity_critical"
    ]


def test_retained_only_unterminated_remains_visible_after_deletion(
    synthetic_repo: Path,
) -> None:
    initial = _attempt_event()
    path = _write_stream(synthetic_repo, initial)
    _commit(synthetic_repo, "retain unterminated attempt")
    path.unlink()
    _commit(synthetic_repo, "delete unterminated stream")

    findings = collect_dispatch_authorization_crossing_findings(
        repo_root=synthetic_repo
    )
    assert [row["finding_type"] for row in findings] == [
        "attempt_reserved_without_terminal"
    ]


def test_retained_committed_prefix_collapse_does_not_report_missing_terminal(
    synthetic_repo: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    initial = _attempt_event()
    terminal = _terminal(initial, "crossing_committed")
    path = _write_stream(synthetic_repo, initial)
    _commit(synthetic_repo, "retain committed prefix")
    _write_stream(synthetic_repo, initial, terminal)
    _commit(synthetic_repo, "retain committed terminal")
    path.unlink()
    _commit(synthetic_repo, "delete committed stream")
    monkeypatch.setattr(
        reservation,
        "_validate_committed_cross_surface",
        lambda root, first, last: None,
    )

    assert collect_dispatch_authorization_crossing_findings(
        repo_root=synthetic_repo
    ) == []


def test_retained_clean_rollback_remains_finding_free(
    synthetic_repo: Path,
) -> None:
    initial = _attempt_event()
    path = _write_stream(
        synthetic_repo,
        initial,
        _terminal(initial, "crossing_rolled_back_clean"),
    )
    _commit(synthetic_repo, "retain clean rollback")
    path.unlink()
    _commit(synthetic_repo, "delete clean rollback stream")

    assert collect_dispatch_authorization_crossing_findings(
        repo_root=synthetic_repo
    ) == []


def test_retained_only_clean_rollback_allows_unrelated_audit_growth(
    synthetic_repo: Path,
) -> None:
    initial = _attempt_event()
    path = _write_stream(
        synthetic_repo,
        initial,
        _terminal(initial, "crossing_rolled_back_clean"),
    )
    _commit(synthetic_repo, "retain clean rollback")
    path.unlink()
    _commit(synthetic_repo, "delete clean rollback stream")
    _write_audit(synthetic_repo, _audit_event(1), _audit_event(2))

    assert collect_dispatch_authorization_crossing_findings(
        repo_root=synthetic_repo
    ) == []


def test_conflicting_retained_versions_produce_invalid_history_finding(
    synthetic_repo: Path,
) -> None:
    initial = _attempt_event()
    path = _write_stream(synthetic_repo, initial)
    _commit(synthetic_repo, "retain original attempt")
    path.unlink()
    _commit(synthetic_repo, "delete original attempt")
    rewritten = copy.deepcopy(initial)
    rewritten["reviewed_content_binding"]["reviewed_byte_length"] = 1235
    _write_stream(synthetic_repo, rewritten)
    _commit(synthetic_repo, "retain conflicting rewrite")
    path.unlink()
    _commit(synthetic_repo, "delete conflicting rewrite")

    findings = collect_dispatch_authorization_crossing_findings(
        repo_root=synthetic_repo
    )
    assert [row["finding_type"] for row in findings] == [
        "reservation_duplicate_or_invalid_sequence"
    ]


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


def test_dangling_symlink_at_reservation_target_fails_closed(
    synthetic_repo: Path,
) -> None:
    initial = _attempt_event()
    target = _stream_path(synthetic_repo, initial)
    target.parent.mkdir(parents=True, exist_ok=True)
    _symlink_or_skip(
        target,
        target.with_name("missing-reservation-target"),
        target_is_directory=False,
    )
    assert os.path.lexists(target)

    with dispatch_authorization_crossing_lock(
        repo_root=synthetic_repo
    ) as lock:
        with pytest.raises(
            DispatchAuthorizationReservationError,
            match="symlink|reparse",
        ):
            reserve_dispatch_authorization_crossing_locked(
                lock=lock, event=initial
            )


def test_dangling_symlink_at_kdauth_target_blocks_clean_rollback(
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
        target = synthetic_repo / initial["authorization_binding"][
            "authorization_target_path"
        ]
        target.parent.mkdir(parents=True, exist_ok=True)
        _symlink_or_skip(
            target,
            target.with_name("missing-kdauth-target"),
            target_is_directory=False,
        )
        assert os.path.lexists(target)
        with pytest.raises(
            DispatchAuthorizationReservationError,
            match="symlink|reparse",
        ):
            append_dispatch_authorization_crossing_terminal_locked(
                lock=lock, event=terminal
            )


@pytest.mark.parametrize("destination_kind", ["inside", "outside"])
def test_symlinked_reservation_parent_redirect_fails_closed(
    synthetic_repo: Path,
    tmp_path: Path,
    destination_kind: str,
) -> None:
    initial = _attempt_event()
    reservation_root = synthetic_repo / reservation.RESERVATION_ROOT
    reservation_root.parent.mkdir(parents=True, exist_ok=True)
    destination = (
        synthetic_repo / "safe-but-nonauthoritative"
        if destination_kind == "inside"
        else tmp_path / "outside-repository"
    )
    destination.mkdir()
    _symlink_or_skip(
        reservation_root,
        destination,
        target_is_directory=True,
    )

    with dispatch_authorization_crossing_lock(
        repo_root=synthetic_repo
    ) as lock:
        with pytest.raises(
            DispatchAuthorizationReservationError,
            match="symlink|reparse",
        ):
            reserve_dispatch_authorization_crossing_locked(
                lock=lock, event=initial
            )


@pytest.mark.skipif(os.name != "nt", reason="Windows junction fixture")
def test_windows_junction_reservation_parent_redirect_fails_closed(
    synthetic_repo: Path,
    tmp_path: Path,
) -> None:
    initial = _attempt_event()
    reservation_root = synthetic_repo / reservation.RESERVATION_ROOT
    reservation_root.parent.mkdir(parents=True, exist_ok=True)
    destination = tmp_path / "junction-destination"
    destination.mkdir()
    created = subprocess.run(
        [
            "cmd.exe",
            "/c",
            "mklink",
            "/J",
            str(reservation_root),
            str(destination),
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    if created.returncode != 0:
        pytest.skip("this environment cannot create the required junction")

    with dispatch_authorization_crossing_lock(
        repo_root=synthetic_repo
    ) as lock:
        with pytest.raises(
            DispatchAuthorizationReservationError,
            match="symlink|reparse",
        ):
            reserve_dispatch_authorization_crossing_locked(
                lock=lock, event=initial
            )


def test_reservation_target_occupied_by_directory_fails_closed(
    synthetic_repo: Path,
) -> None:
    initial = _attempt_event()
    target = _stream_path(synthetic_repo, initial)
    target.mkdir(parents=True)

    with dispatch_authorization_crossing_lock(
        repo_root=synthetic_repo
    ) as lock:
        with pytest.raises(
            DispatchAuthorizationReservationError,
            match="single-use",
        ):
            reserve_dispatch_authorization_crossing_locked(
                lock=lock, event=initial
            )


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


def test_terminal_occurred_at_must_not_precede_initial_occurred_at(
    synthetic_repo: Path,
) -> None:
    initial = _attempt_event()
    initial["occurred_at"] = "2026-07-24T12:01:00Z"
    terminal = _terminal(initial, "crossing_integrity_critical")
    terminal["occurred_at"] = "2026-07-24T12:00:30Z"
    path = _write_stream(synthetic_repo, initial, terminal)

    with pytest.raises(
        DispatchAuthorizationReservationError,
        match="terminal occurred_at must not precede initial",
    ):
        validate_dispatch_authorization_reservation_stream(
            repo_root=synthetic_repo,
            reservation_path=path,
        )


def test_terminal_occurred_at_must_not_precede_reserved_at(
    synthetic_repo: Path,
) -> None:
    initial = _attempt_event()
    terminal = _terminal(initial, "crossing_integrity_critical")
    terminal["occurred_at"] = "2026-07-24T11:59:59Z"
    path = _write_stream(synthetic_repo, initial, terminal)

    with pytest.raises(
        DispatchAuthorizationReservationError,
        match="occurred_at must not precede reserved_at",
    ):
        validate_dispatch_authorization_reservation_stream(
            repo_root=synthetic_repo,
            reservation_path=path,
        )


@pytest.mark.parametrize(
    ("lifecycle_event_type", "historical_replay_allowed"),
    [
        ("authorization_consumed", True),
        ("authorization_revoked", False),
        ("authorization_superseded", False),
    ],
)
def test_public_crossing_transition_and_terminal_lifecycle_replay(
    tmp_path: Path,
    source_repo: Path,
    lifecycle_event_type: str,
    historical_replay_allowed: bool,
) -> None:
    fixture = authorization_test_support._fixture(
        tmp_path,
        source_repo,
        reservation_state="none",
    )
    fixture["created"]["occurred_at"] = "2026-07-24T12:01:00Z"
    creation_raw = (
        authorization_test_support.repo_canonical_json_v1(fixture["created"])
        + b"\n"
    )
    authorization_raw = fixture["authorization_raw"]
    fixture["authorization_path"].unlink()
    fixture["audit_path"].unlink()

    def remove_readonly(function, path, exc_info):
        del exc_info
        os.chmod(path, 0o700)
        function(path)

    shutil.rmtree(fixture["root"] / ".git", onerror=remove_readonly)
    _git(fixture["root"], "init", "-q")
    _commit(fixture["root"], "synthetic pre-crossing dependencies")

    assert not fixture["authorization_path"].exists()
    assert not fixture["audit_path"].exists()
    assert not (fixture["root"] / reservation.RESERVATION_ROOT).exists()
    assert not (
        fixture["root"] / authorization_validator.DISPATCH_ROOT
    ).exists()
    assert not (
        fixture["root"] / authorization_validator.EXECUTION_ROOT
    ).exists()

    initial = authorization_test_support._crossing_reservation_event(
        fixture,
        "KDAUTH-XING-20260724-E2E90001",
        reserved_at="2026-07-24T12:00:00Z",
        occurred_at="2026-07-24T12:00:00Z",
    )
    committed = authorization_test_support._matching_committed_terminal(
        fixture,
        initial,
        occurred_at="2026-07-24T12:02:00Z",
    )
    with dispatch_authorization_crossing_lock(
        repo_root=fixture["root"]
    ) as lock:
        reserved = reserve_dispatch_authorization_crossing_locked(
            lock=lock,
            event=initial,
        )
        assert reserved["reservation_committed"] is True
        fixture["authorization_path"].write_bytes(authorization_raw)
        fixture["audit_path"].write_bytes(creation_raw)
        completed = append_dispatch_authorization_crossing_terminal_locked(
            lock=lock,
            event=committed,
        )
        assert completed["terminal_outcome"] == "crossing_committed"

    active = validate_dispatch_authorization(
        repo_root=fixture["root"],
        authorization_path=fixture["authorization_path"],
        require_audit=True,
        scan_history=True,
    )
    assert active["valid"] is True
    assert active["lifecycle_state"] == "created"

    lifecycle_terminal = authorization_test_support._terminal_event(
        fixture,
        lifecycle_event_type,
    )
    fixture["audit_path"].write_bytes(
        creation_raw
        + authorization_test_support.repo_canonical_json_v1(
            lifecycle_terminal
        )
        + b"\n"
    )
    with pytest.raises(DispatchAuthorizationError, match="not consumable"):
        validate_dispatch_authorization(
            repo_root=fixture["root"],
            authorization_path=fixture["authorization_path"],
            require_audit=True,
            scan_history=True,
        )

    stream = fixture["root"] / initial["reservation_stream_path"]
    replay = validate_dispatch_authorization_reservation_stream(
        repo_root=fixture["root"],
        reservation_path=stream,
        require_terminal=True,
    )
    assert replay["valid"] is True
    collected = collect_dispatch_authorization_crossing_findings(
        repo_root=fixture["root"]
    )
    if historical_replay_allowed:
        assert replay["findings"] == []
        assert collected == []
    else:
        assert [row["finding_type"] for row in replay["findings"]] == [
            "crossing_committed_without_exact_authorization_created"
        ]
        assert [row["finding_type"] for row in collected] == [
            "crossing_committed_without_exact_authorization_created"
        ]

    wrong_link = copy.deepcopy(committed)
    wrong_link["event_payload"]["lifecycle_raw_line_sha256"] = (
        "sha256:" + "0" * 64
    )
    _write_stream(fixture["root"], initial, wrong_link)
    invalid_replay = validate_dispatch_authorization_reservation_stream(
        repo_root=fixture["root"],
        reservation_path=stream,
        require_terminal=True,
    )
    assert [
        (row["finding_type"], row["reason_code"])
        for row in invalid_replay["findings"]
    ] == [
        (
            "crossing_committed_without_exact_authorization_created",
            "exact_creation_binding_missing",
        )
    ]


def test_missing_required_dataset_is_honest_non_authority_finding(
    tmp_path: Path,
    source_repo: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import duckdb

    from tools.research_query import query_layer

    fixture = authorization_test_support._fixture(
        tmp_path,
        source_repo,
        reservation_state="committed",
    )
    dataset_path = fixture["root"] / fixture["authorization"][
        "authorization_core"
    ]["dataset"]["data_path"]
    dataset_path.unlink()

    with pytest.raises(
        DispatchAuthorizationError,
        match="1d dataset must be a regular non-symlink file",
    ):
        validate_dispatch_authorization(
            repo_root=fixture["root"],
            authorization_path=fixture["authorization_path"],
            require_audit=False,
            scan_history=False,
        )

    stream = next(
        (fixture["root"] / reservation.RESERVATION_ROOT).glob("*.jsonl")
    )
    initial = json.loads(stream.read_text(encoding="utf-8").splitlines()[0])
    findings = collect_dispatch_authorization_crossing_findings(
        repo_root=fixture["root"]
    )
    assert len(findings) == 1
    finding = findings[0]
    assert finding == {
        "finding_type": (
            "crossing_committed_required_validation_input_unavailable"
        ),
        "attempt_id": initial["attempt_id"],
        "reservation_stream_path": initial["reservation_stream_path"],
        "authorization_id": initial["authorization_binding"][
            "authorization_id"
        ],
        "authorization_target_path": initial["authorization_binding"][
            "authorization_target_path"
        ],
        "dispatch_id": initial["dispatch_binding"]["dispatch_id"],
        "dispatch_record_path": initial["dispatch_binding"][
            "dispatch_record_path"
        ],
        "run_id": initial["run_binding"]["run_id"],
        "execution_event_stream_path": initial["run_binding"][
            "execution_event_stream_path"
        ],
        "queue_item_id": initial["queue_binding"]["queue_item_id"],
        "terminal_outcome": "crossing_committed",
        "reason_code": "canonical_1d_dataset_unavailable",
        "operator_inspection_required": True,
        "non_authority": True,
    }
    assert finding["finding_type"] != (
        "crossing_committed_without_exact_authorization_created"
    )
    assert finding["reason_code"] != "exact_creation_binding_missing"

    monkeypatch.setattr(query_layer, "REPO_ROOT", fixture["root"])
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
    assert rows == [finding]
    conn.close()


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
    creation = _audit_event(
        1,
        authorization_id="KDAUTH-TEST-R2-9001",
    )
    creation["authorization_path"] = authorization_rel
    creation["authorization_file_sha256"] = reservation._digest(
        authorization_raw
    )
    creation["authorization_byte_length"] = len(authorization_raw)
    creation["authorization_core_sha256"] = "sha256:" + "1" * 64
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


def test_query_registration_exposes_cross_attempt_identity_collision(
    synthetic_repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import duckdb

    from tools.research_query import query_layer

    first = _attempt_event()
    second = copy.deepcopy(first)
    second["attempt_id"] = "KDAUTH-XING-20260724-TEST0002"
    second["event_id"] = f"{second['attempt_id']}-000001"
    second["reservation_stream_path"] = (
        "research/queue/dispatch_authorization_reservations/"
        f"{second['attempt_id']}.crossing_reservation.jsonl"
    )
    _write_stream(synthetic_repo, first)
    _write_stream(synthetic_repo, second)
    monkeypatch.setattr(query_layer, "REPO_ROOT", synthetic_repo)
    conn = duckdb.connect(database=":memory:")
    query_layer._register_dispatch_authorization_crossing_reservation_findings(
        conn
    )
    rows = conn.execute(
        """
        SELECT finding_type, reason_code
        FROM dispatch_authorization_crossing_reservation_findings
        WHERE finding_type =
            'reservation_identity_collision_across_attempts'
        ORDER BY attempt_id
        """
    ).fetchall()
    assert rows == [
        (
            "reservation_identity_collision_across_attempts",
            "protected_identity_collision_across_distinct_attempts",
        ),
        (
            "reservation_identity_collision_across_attempts",
            "protected_identity_collision_across_distinct_attempts",
        ),
    ]
    conn.close()
