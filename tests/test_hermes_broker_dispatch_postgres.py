from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import psycopg
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from tools.hermes.broker import dispatch as dispatch_module
from tools.hermes.broker.acceptance import (
    make_claim_payload,
    sign_claim_for_proof,
    write_fresh_prepared_fixture,
)
from tools.hermes.broker.crypto import approval_signed_bytes
from tools.hermes.broker.dispatch import (
    RECONCILE_REASON,
    BrokerDryRunDispatchService,
)
from tools.hermes.broker.dry_run_adapter import DRY_RUN_FAILED_REASON, dry_run_noop
from tools.hermes.broker.migrations import apply_migrations
from tools.hermes.broker.models import ApprovalClaimPayload, SignedApprovalClaim
from tools.hermes.broker.projection import (
    DRY_RUN_PROOF_ADAPTER_ID,
    DRY_RUN_PROOF_ADAPTER_VERSION,
    DRY_RUN_PROOF_REGISTRY_VERSION,
    Broker3ProofExecutableAction,
    dry_run_proof_registry,
)
from tools.hermes.broker.reservation import BrokerReservationService
from tools.hermes.broker.retention import BrokerArtifactStore
from tools.hermes.broker.state import BrokerActionState
from tools.hermes.broker.store import BrokerAuthorityStore
from tools.hermes.prepare.serialization import canonical_json_bytes
from tools.hermes.proposals.models import AffectedDomain, AuthorityClass

REPO_ROOT = Path(__file__).resolve().parents[1]
REPO_SHA = "6" * 40
DRY_RUN_PROOF_ACTION_TYPE = "broker3.proof.dry_run_noop_v1"


class SecretDsn(str):
    def __repr__(self) -> str:
        return "<isolated broker test DSN>"


def _test_dsn() -> SecretDsn:
    dsn = os.environ.get("HERMES_BROKER_TEST_DSN") or os.environ.get("RESEARCH_MEMORY_TEST_DSN")
    if not dsn:
        pytest.skip("HERMES_BROKER_TEST_DSN is required for PostgreSQL integration tests")
    with psycopg.connect(dsn) as connection:
        database = connection.execute("SELECT current_database()").fetchone()[0]
    if "test" not in database.lower():
        pytest.fail("broker tests require an isolated database whose name contains 'test'")
    return SecretDsn(dsn)


@pytest.fixture()
def broker_dsn() -> str:
    dsn = _test_dsn()
    lock_connection = psycopg.connect(dsn, autocommit=True)
    lock_connection.execute("SELECT pg_advisory_lock(721003002)")
    try:
        with psycopg.connect(dsn, autocommit=True) as connection:
            connection.execute("DROP SCHEMA IF EXISTS hermes_broker CASCADE")
        apply_migrations(dsn)
        yield dsn
    finally:
        with psycopg.connect(dsn, autocommit=True) as connection:
            connection.execute("DROP SCHEMA IF EXISTS hermes_broker CASCADE")
        lock_connection.execute("SELECT pg_advisory_unlock(721003002)")
        lock_connection.close()


class NoopSpy:
    """Counts fixed no-op invocations; may optionally simulate a crash before finalization."""

    def __init__(self, *, raise_error: bool = False) -> None:
        self.calls = 0
        self.raise_error = raise_error

    def __call__(self, projection: Any) -> Any:
        self.calls += 1
        if self.raise_error:
            raise RuntimeError("simulated crash before dry-run finalization")
        return dry_run_noop(projection)


@dataclass
class DispatchCase:
    dsn: str
    service: BrokerDryRunDispatchService
    reservation_service: BrokerReservationService
    store: BrokerAuthorityStore
    artifact_store: BrokerArtifactStore
    private_key: Ed25519PrivateKey
    prepared: Any
    action: Any
    signed: SignedApprovalClaim
    evaluated_at: datetime

    def sign(self, payload: ApprovalClaimPayload) -> SignedApprovalClaim:
        unsigned = SignedApprovalClaim.model_construct(
            payload=payload,
            signature_algorithm="ed25519",
            signature_encoding="lowercase_hex",
            signature="0" * 128,
        )
        return SignedApprovalClaim(
            payload=payload,
            signature_algorithm="ed25519",
            signature_encoding="lowercase_hex",
            signature=self.private_key.sign(approval_signed_bytes(unsigned)).hex(),
        )

    def dispatch(self) -> Any:
        return self.service.dispatch_dry_run(
            action_input=self.action,
            signed_claim_input=self.signed,
            evaluated_at=self.evaluated_at,
        )


def _insert_key(
    dsn: str,
    private_key: Ed25519PrivateKey,
    *,
    key_id: str = "broker3-key",
    epoch: int = 1,
    version: str = "broker1-proof-keys-v1",
    added_at: datetime,
) -> None:
    public_key = private_key.public_key().public_bytes(
        serialization.Encoding.Raw,
        serialization.PublicFormat.Raw,
    )
    with psycopg.connect(dsn) as connection:
        connection.execute(
            """
            INSERT INTO hermes_broker.broker_trusted_key (
                registry_epoch, key_registry_version, key_id, algorithm,
                public_key_encoding, public_key, state, added_at,
                revoked_at, revocation_reason, fixture_only
            ) VALUES (%s, %s, %s, 'ed25519', 'lowercase_hex', %s,
                      'active', %s, NULL, NULL, TRUE)
            """,
            (epoch, version, key_id, public_key.hex(), added_at),
        )


def _make_action(
    prepared: Any,
    prepared_id: str,
    action_id: str,
    outcome: str,
) -> Broker3ProofExecutableAction:
    return Broker3ProofExecutableAction(
        executable_action_schema_version="hermes_executable_action_v1",
        executable_action_id=action_id,
        action_type=DRY_RUN_PROOF_ACTION_TYPE,
        prepared_record_id=prepared_id,
        prepared_payload_sha256=hashlib.sha256(canonical_json_bytes(prepared)).hexdigest(),
        source_proposal_id=prepared.source_proposal_id,
        source_proposal_content_sha256=prepared.source_proposal_content_sha256,
        repo_sha=prepared.repo_sha,
        action_registry_version=DRY_RUN_PROOF_REGISTRY_VERSION,
        adapter_id=DRY_RUN_PROOF_ADAPTER_ID,
        adapter_version=DRY_RUN_PROOF_ADAPTER_VERSION,
        authority_class=AuthorityClass.A1,
        human_authored=True,
        hermes_authored=False,
        target={"kind": "broker3_dry_run_fixture", "fixture_id": action_id},
        scope={"domain": AffectedDomain.TEST_ONLY_TOOLING, "operation": "dry_run_noop_only"},
        parameters={"challenge": "exact-byte-proof", "requested_dry_run_outcome": outcome},
        budget_bound={"amount": 1, "unit": "proof-credit", "hard_limit": True},
        count_or_quantity_bound={"amount": 1, "unit": "decision", "hard_limit": True},
        timeout={"seconds": 60, "hard_limit": True},
    )


def _case(
    tmp_path: Path,
    dsn: str,
    *,
    action_id: str,
    suffix: str,
    outcome: str = "completed",
    authority_class: AuthorityClass = AuthorityClass.A1,
    insert_key: bool = True,
) -> DispatchCase:
    now = datetime.now(UTC).replace(microsecond=0)
    prepared_id = f"HERMES-PREP-20260819T130000Z-{suffix}"
    source = tmp_path / f"source-{suffix}"
    prepared, _ = write_fresh_prepared_fixture(
        source_root=source,
        authority_class=authority_class,
        repo_sha=REPO_SHA,
        prepared_record_id=prepared_id,
        created_at=now,
    )
    artifact_store = BrokerArtifactStore(
        tmp_path / f"stable-{suffix}",
        repository_root=REPO_ROOT,
        active_worktree_root=REPO_ROOT,
    )
    artifact_store.retain_from_outbox(
        source_outbox_root=source,
        prepared_record_id=prepared_id,
        clock=now,
    )
    private_key = Ed25519PrivateKey.from_private_bytes(bytes(range(32)))
    key_id = f"{action_id}-key"
    action = _make_action(prepared, prepared_id, action_id, outcome)
    payload = make_claim_payload(action=action, signer_key_id=key_id, issued_at=now)
    if authority_class is AuthorityClass.A1:
        signed = sign_claim_for_proof(
            action=action,
            prepared_payload=prepared,
            claim_payload=payload,
            private_key=private_key,
        )
    else:
        # A0 adversary: the operator signing guard refuses A0, so sign directly.
        unsigned = SignedApprovalClaim.model_construct(
            payload=payload,
            signature_algorithm="ed25519",
            signature_encoding="lowercase_hex",
            signature="0" * 128,
        )
        signed = SignedApprovalClaim(
            payload=payload,
            signature_algorithm="ed25519",
            signature_encoding="lowercase_hex",
            signature=private_key.sign(approval_signed_bytes(unsigned)).hex(),
        )
    if insert_key:
        _insert_key(dsn, private_key, key_id=key_id, added_at=now)
    store = BrokerAuthorityStore(dsn)
    reservation_service = BrokerReservationService(
        store=store,
        artifact_store=artifact_store,
        action_registry=dry_run_proof_registry(),
        current_repo_sha=REPO_SHA,
    )
    service = BrokerDryRunDispatchService(
        reservation_service=reservation_service,
        store=store,
        action_registry=dry_run_proof_registry(),
    )
    return DispatchCase(
        dsn=dsn,
        service=service,
        reservation_service=reservation_service,
        store=store,
        artifact_store=artifact_store,
        private_key=private_key,
        prepared=prepared,
        action=action,
        signed=signed,
        evaluated_at=now,
    )


def _fresh_service(case: DispatchCase, dsn: str) -> BrokerDryRunDispatchService:
    store = BrokerAuthorityStore(dsn)
    reservation_service = BrokerReservationService(
        store=store,
        artifact_store=case.artifact_store,
        action_registry=dry_run_proof_registry(),
        current_repo_sha=REPO_SHA,
    )
    return BrokerDryRunDispatchService(
        reservation_service=reservation_service,
        store=store,
        action_registry=dry_run_proof_registry(),
    )


def _events(dsn: str) -> list[str]:
    with psycopg.connect(dsn) as connection:
        return [
            row[0]
            for row in connection.execute(
                """
                SELECT event_type FROM hermes_broker.broker_authority_audit
                ORDER BY audit_sequence
                """
            )
        ]


def _event_count(dsn: str, event_type: str) -> int:
    with psycopg.connect(dsn) as connection:
        return connection.execute(
            "SELECT count(*) FROM hermes_broker.broker_authority_audit WHERE event_type = %s",
            (event_type,),
        ).fetchone()[0]


def _counts(dsn: str) -> tuple[int, int]:
    with psycopg.connect(dsn) as connection:
        reservations = connection.execute(
            "SELECT count(*) FROM hermes_broker.broker_reservation"
        ).fetchone()[0]
        nonce_events = connection.execute(
            """
            SELECT count(*) FROM hermes_broker.broker_authority_audit
            WHERE event_type = 'nonce_reserved'
            """
        ).fetchone()[0]
    return reservations, nonce_events


def _state_row(dsn: str, action_id: str) -> dict[str, Any]:
    with psycopg.connect(dsn, row_factory=psycopg.rows.dict_row) as connection:
        return connection.execute(
            "SELECT * FROM hermes_broker.broker_action_state WHERE executable_action_id = %s",
            (action_id,),
        ).fetchone()


def test_full_completed_dry_run_loop_has_no_real_side_effect(
    broker_dsn: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    case = _case(tmp_path, broker_dsn, action_id="b3-completed", suffix="1111111111111111")
    spy = NoopSpy()
    monkeypatch.setattr(dispatch_module, "dry_run_noop", spy)
    result = case.dispatch()
    assert result.outcome == "completed"
    assert result.state is BrokerActionState.COMPLETED
    assert result.dispatch_id.startswith("BROKER-DIS-")
    assert result.reason_code is None
    assert result.downstream_side_effect is False
    assert spy.calls == 1
    assert _events(broker_dsn) == [
        "claim_submitted",
        "claim_verified",
        "nonce_reserved",
        "dispatch_requested",
        "dispatch_completed",
    ]
    assert _counts(broker_dsn) == (1, 1)
    row = _state_row(broker_dsn, "b3-completed")
    assert row["state"] == "completed"
    assert row["dispatch_id"] == result.dispatch_id
    assert row["last_reason_code"] is None


def test_deterministic_failed_dry_run_loop(
    broker_dsn: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    case = _case(
        tmp_path, broker_dsn, action_id="b3-failed", suffix="2222222222222222", outcome="failed"
    )
    spy = NoopSpy()
    monkeypatch.setattr(dispatch_module, "dry_run_noop", spy)
    result = case.dispatch()
    assert result.outcome == "failed"
    assert result.state is BrokerActionState.FAILED
    assert result.reason_code == DRY_RUN_FAILED_REASON
    assert result.downstream_side_effect is False
    assert spy.calls == 1
    assert _events(broker_dsn) == [
        "claim_submitted",
        "claim_verified",
        "nonce_reserved",
        "dispatch_requested",
        "dispatch_failed",
    ]
    assert _counts(broker_dsn) == (1, 1)
    row = _state_row(broker_dsn, "b3-failed")
    assert row["state"] == "failed"
    assert row["last_reason_code"] == DRY_RUN_FAILED_REASON


def test_burned_nonce_never_redispatches(
    broker_dsn: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    case = _case(tmp_path, broker_dsn, action_id="b3-replay", suffix="3333333333333333")
    spy = NoopSpy()
    monkeypatch.setattr(dispatch_module, "dry_run_noop", spy)
    first = case.dispatch()
    replay = case.dispatch()
    assert first.outcome == "completed"
    assert replay.outcome == "completed"
    assert replay.dispatch_id == first.dispatch_id
    assert replay.idempotent_existing is True
    assert spy.calls == 1
    assert _event_count(broker_dsn, "dispatch_requested") == 1
    assert _event_count(broker_dsn, "dispatch_completed") == 1
    assert _counts(broker_dsn) == (1, 1)


def test_conflicting_action_on_burned_nonce_never_reaches_dispatch(
    broker_dsn: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    winner = _case(tmp_path, broker_dsn, action_id="b3-winner", suffix="4444444444444444")
    spy = NoopSpy()
    monkeypatch.setattr(dispatch_module, "dry_run_noop", spy)
    assert winner.dispatch().outcome == "completed"

    loser = _case(
        tmp_path,
        broker_dsn,
        action_id="b3-loser",
        suffix="5555555555555555",
        insert_key=True,
    )
    loser_payload = loser.signed.payload.model_copy(
        update={"single_use_nonce": winner.signed.payload.single_use_nonce}
    )
    loser.signed = loser.sign(loser_payload)
    result = loser.dispatch()
    assert result.outcome == "rejected"
    assert result.reason_code == "nonce_already_reserved"
    assert spy.calls == 1
    assert _event_count(broker_dsn, "dispatch_requested") == 1
    assert _counts(broker_dsn) == (1, 1)
    assert _state_row(broker_dsn, "b3-loser")["state"] == "rejected"


def test_crash_stranded_reconcile_and_terminal_replay(
    broker_dsn: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    case = _case(tmp_path, broker_dsn, action_id="b3-crash", suffix="6666666666666666")
    spy = NoopSpy(raise_error=True)
    monkeypatch.setattr(dispatch_module, "dry_run_noop", spy)
    with pytest.raises(RuntimeError, match="simulated crash"):
        case.dispatch()
    assert spy.calls == 1

    # The dispatch_requested transaction committed before the (crashing) adapter call.
    row = _state_row(broker_dsn, "b3-crash")
    assert row["state"] == "dispatched"
    assert row["dispatch_id"] is not None
    assert row["last_reason_code"] is None
    assert _counts(broker_dsn) == (1, 1)
    assert _events(broker_dsn) == [
        "claim_submitted",
        "claim_verified",
        "nonce_reserved",
        "dispatch_requested",
    ]

    # A fresh process (fresh store/service) explicitly reconciles the stranded dispatch.
    fresh = _fresh_service(case, broker_dsn)
    recon = fresh.reconcile_stranded_dispatch(
        action_input=case.action,
        signed_claim_input=case.signed,
        evaluated_at=case.evaluated_at,
    )
    assert recon.outcome == "reconcile_required"
    assert recon.reason_code == RECONCILE_REASON
    assert recon.dispatch_id == row["dispatch_id"]
    assert spy.calls == 1  # reconcile invoked no adapter
    assert _events(broker_dsn) == [
        "claim_submitted",
        "claim_verified",
        "nonce_reserved",
        "dispatch_requested",
        "reconcile_required",
    ]
    assert _counts(broker_dsn) == (1, 1)

    # Replaying the full loop after reconcile never re-invokes the adapter or re-burns.
    replay = case.service.dispatch_dry_run(
        action_input=case.action,
        signed_claim_input=case.signed,
        evaluated_at=case.evaluated_at,
    )
    assert replay.outcome == "reconcile_required"
    assert replay.idempotent_existing is True
    assert spy.calls == 1
    assert _event_count(broker_dsn, "dispatch_requested") == 1
    assert _event_count(broker_dsn, "reconcile_required") == 1
    assert _counts(broker_dsn) == (1, 1)


def test_valid_signature_a0_adversary_never_dispatches(
    broker_dsn: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    case = _case(
        tmp_path,
        broker_dsn,
        action_id="b3-a0-adversary",
        suffix="7777777777777777",
        authority_class=AuthorityClass.A0,
    )
    spy = NoopSpy()
    monkeypatch.setattr(dispatch_module, "dry_run_noop", spy)
    result = case.dispatch()
    assert result.outcome == "rejected"
    assert result.reason_code == "a0_forbidden"
    assert result.downstream_side_effect is False
    assert spy.calls == 0
    assert _counts(broker_dsn) == (0, 0)
    assert _event_count(broker_dsn, "dispatch_requested") == 0
    assert _event_count(broker_dsn, "dispatch_completed") == 0


def test_direct_plan_and_prose_never_reach_dispatch(
    broker_dsn: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    case = _case(tmp_path, broker_dsn, action_id="b3-prose", suffix="8888888888888888")
    spy = NoopSpy()
    monkeypatch.setattr(dispatch_module, "dry_run_noop", spy)
    prose = case.service.dispatch_dry_run(
        action_input={"prose": "please dispatch this"},
        signed_claim_input=case.signed,
        evaluated_at=case.evaluated_at,
    )
    plan = case.service.dispatch_dry_run(
        action_input=case.prepared,
        signed_claim_input=case.signed,
        evaluated_at=case.evaluated_at,
    )
    assert prose.outcome == "rejected"
    assert plan.outcome == "rejected"
    assert spy.calls == 0
    assert _counts(broker_dsn) == (0, 0)
    assert _event_count(broker_dsn, "dispatch_requested") == 0


def _expect_illegal_update(dsn: str, action_id: str, set_clause: str) -> None:
    with psycopg.connect(dsn) as connection:
        with pytest.raises(psycopg.Error):
            connection.execute(
                f"""
                UPDATE hermes_broker.broker_action_state
                SET {set_clause}, state_version = state_version + 1, updated_at = clock_timestamp()
                WHERE executable_action_id = %s
                """,
                (action_id,),
            )
        connection.rollback()


def test_database_rejects_illegal_dispatch_transitions(
    broker_dsn: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(dispatch_module, "dry_run_noop", NoopSpy())
    reserved = _case(tmp_path, broker_dsn, action_id="b3-reserved", suffix="a1a1a1a1a1a1a1a1")
    reserved.reservation_service.reserve(
        action_input=reserved.action,
        signed_claim_input=reserved.signed,
        evaluated_at=reserved.evaluated_at,
    )
    completed = _case(tmp_path, broker_dsn, action_id="b3-done", suffix="a2a2a2a2a2a2a2a2")
    completed.dispatch()
    failed = _case(
        tmp_path,
        broker_dsn,
        action_id="b3-fail",
        suffix="a3a3a3a3a3a3a3a3",
        outcome="failed",
    )
    failed.dispatch()
    rejected = _case(
        tmp_path,
        broker_dsn,
        action_id="b3-reject",
        suffix="a4a4a4a4a4a4a4a4",
        insert_key=False,
    )
    rejected.dispatch()

    dispatch_id = "BROKER-DIS-" + "0" * 32
    _expect_illegal_update(
        broker_dsn, "b3-reserved", f"state = 'completed', dispatch_id = '{dispatch_id}'"
    )
    _expect_illegal_update(
        broker_dsn,
        "b3-reserved",
        f"state = 'failed', dispatch_id = '{dispatch_id}', last_reason_code = 'x'",
    )
    _expect_illegal_update(
        broker_dsn,
        "b3-reserved",
        f"state = 'reconcile_required', dispatch_id = '{dispatch_id}', last_reason_code = 'x'",
    )
    _expect_illegal_update(broker_dsn, "b3-done", "state = 'dispatched'")
    _expect_illegal_update(broker_dsn, "b3-fail", "state = 'dispatched', last_reason_code = NULL")
    _expect_illegal_update(
        broker_dsn,
        "b3-reject",
        f"state = 'dispatched', reservation_id = 'r', dispatch_id = '{dispatch_id}'",
    )

    # A stranded dispatched action cannot be forced back to reserved.
    crash = _case(tmp_path, broker_dsn, action_id="b3-strand", suffix="a5a5a5a5a5a5a5a5")
    monkeypatch.setattr(dispatch_module, "dry_run_noop", NoopSpy(raise_error=True))
    with pytest.raises(RuntimeError):
        crash.dispatch()
    _expect_illegal_update(broker_dsn, "b3-strand", "state = 'reserved', dispatch_id = NULL")


def test_audit_table_rejects_out_of_contract_dispatch_events(broker_dsn: str) -> None:
    base_columns = (
        "event_id, event_type, occurred_at, actor, "
        "event_payload_canonical, event_payload_sha256, reservation_id, dispatch_id, reason_code"
    )

    def _insert(values: tuple[Any, ...]) -> None:
        with psycopg.connect(broker_dsn) as connection:
            with pytest.raises(psycopg.Error):
                connection.execute(
                    f"""
                    INSERT INTO hermes_broker.broker_authority_audit ({base_columns})
                    VALUES (%s, %s, clock_timestamp(), 'broker', %s, %s, %s, %s, %s)
                    """,
                    values,
                )
            connection.rollback()

    payload = b"{}\n"
    digest = hashlib.sha256(payload).hexdigest()
    res = "BROKER-RES-" + "0" * 32
    dis = "BROKER-DIS-" + "0" * 32
    # Unknown event type.
    _insert(("E1", "bogus_event", payload, digest, res, dis, None))
    # dispatch_requested requires dispatch_id and reservation_id.
    _insert(("E2", "dispatch_requested", payload, digest, None, None, None))
    # dispatch_failed requires a reason.
    _insert(("E3", "dispatch_failed", payload, digest, res, dis, None))
    # reconcile_required requires a reason.
    _insert(("E4", "reconcile_required", payload, digest, res, dis, None))
    # dispatch_requested must not carry a reason.
    _insert(("E5", "dispatch_requested", payload, digest, res, dis, "nope"))
    # dispatch_completed must not carry a reason.
    _insert(("E6", "dispatch_completed", payload, digest, res, dis, "nope"))


def test_migrations_apply_in_order_without_a_dispatch_table(broker_dsn: str) -> None:
    assert apply_migrations(broker_dsn).already_applied == (
        "0001_broker_authority",
        "0002_broker_dry_run_dispatch",
    )
    with psycopg.connect(broker_dsn) as connection:
        tables = {
            row[0]
            for row in connection.execute(
                """
                SELECT table_name FROM information_schema.tables
                WHERE table_schema = 'hermes_broker'
                """
            )
        }
        state_columns = {
            row[0]
            for row in connection.execute(
                """
                SELECT column_name FROM information_schema.columns
                WHERE table_schema = 'hermes_broker' AND table_name = 'broker_action_state'
                """
            )
        }
        audit_columns = {
            row[0]
            for row in connection.execute(
                """
                SELECT column_name FROM information_schema.columns
                WHERE table_schema = 'hermes_broker' AND table_name = 'broker_authority_audit'
                """
            )
        }
    assert not any("dispatch" in table for table in tables)
    assert "dispatch_id" in state_columns
    assert "dispatch_id" in audit_columns
