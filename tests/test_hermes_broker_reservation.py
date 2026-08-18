from __future__ import annotations

import ast
import os
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import psycopg
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from tools.hermes.broker.acceptance import (
    PROOF_KEY_REGISTRY_VERSION,
    make_action,
    make_claim_payload,
    proof_registry,
    sign_claim_for_proof,
    write_fresh_prepared_fixture,
)
from tools.hermes.broker.crypto import approval_signed_bytes
from tools.hermes.broker.migrations import apply_migrations
from tools.hermes.broker.models import ApprovalClaimPayload, SignedApprovalClaim
from tools.hermes.broker.reservation import (
    BrokerReservationService,
    reservation_idempotency_key,
)
from tools.hermes.broker.retention import BrokerArtifactStore
from tools.hermes.broker.serialization import broker_sha256
from tools.hermes.broker.state import BrokerActionState, BrokerAuditEventType
from tools.hermes.broker.store import BrokerAuthorityStore
from tools.hermes.proposals.models import AuthorityClass

REPO_ROOT = Path(__file__).resolve().parents[1]
REPO_SHA = "4" * 40


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


@dataclass
class ReservationCase:
    dsn: str
    service: BrokerReservationService
    store: BrokerAuthorityStore
    artifact_store: BrokerArtifactStore
    private_key: Ed25519PrivateKey
    prepared: Any
    action: Any
    claim_payload: ApprovalClaimPayload
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


def _insert_key_snapshot(
    dsn: str,
    private_key: Ed25519PrivateKey,
    *,
    key_id: str,
    added_at: datetime,
    epoch: int = 1,
    version: str = PROOF_KEY_REGISTRY_VERSION,
    revoked: bool = False,
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
            ) VALUES (%s, %s, %s, 'ed25519', 'lowercase_hex', %s, %s, %s, %s, %s, TRUE)
            """,
            (
                epoch,
                version,
                key_id,
                public_key.hex(),
                "revoked" if revoked else "active",
                added_at,
                added_at if revoked else None,
                "test revocation" if revoked else None,
            ),
        )


def _case(
    tmp_path: Path,
    dsn: str,
    *,
    action_id: str = "broker2-valid-action",
    prepared_suffix: str = "1111111111111111",
    insert_key: bool = True,
    issued_at: datetime | None = None,
    expiry: datetime | None = None,
) -> ReservationCase:
    evaluated_at = issued_at or datetime.now(UTC).replace(microsecond=0)
    prepared_id = f"HERMES-PREP-20260818T120000Z-{prepared_suffix}"
    source = tmp_path / f"source-{prepared_suffix}"
    prepared, _ = write_fresh_prepared_fixture(
        source_root=source,
        authority_class=AuthorityClass.A1,
        repo_sha=REPO_SHA,
        prepared_record_id=prepared_id,
        created_at=evaluated_at,
    )
    artifact_store = BrokerArtifactStore(
        tmp_path / f"stable-{prepared_suffix}",
        repository_root=REPO_ROOT,
        active_worktree_root=REPO_ROOT,
    )
    artifact_store.retain_from_outbox(
        source_outbox_root=source,
        prepared_record_id=prepared_id,
        clock=evaluated_at,
    )
    private_key = Ed25519PrivateKey.from_private_bytes(bytes(range(32)))
    action = make_action(payload=prepared, prepared_record_id=prepared_id, action_id=action_id)
    payload = make_claim_payload(
        action=action,
        signer_key_id="broker2-valid-key",
        issued_at=evaluated_at,
        expiry=expiry,
    )
    signed = sign_claim_for_proof(
        action=action,
        prepared_payload=prepared,
        claim_payload=payload,
        private_key=private_key,
    )
    if insert_key:
        _insert_key_snapshot(
            dsn,
            private_key,
            key_id="broker2-valid-key",
            added_at=evaluated_at,
        )
    store = BrokerAuthorityStore(dsn)
    service = BrokerReservationService(
        store=store,
        artifact_store=artifact_store,
        action_registry=proof_registry(),
        current_repo_sha=REPO_SHA,
    )
    return ReservationCase(
        dsn=dsn,
        service=service,
        store=store,
        artifact_store=artifact_store,
        private_key=private_key,
        prepared=prepared,
        action=action,
        claim_payload=payload,
        signed=signed,
        evaluated_at=evaluated_at,
    )


def _counts(dsn: str) -> tuple[int, int, list[str]]:
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
        events = [
            row[0]
            for row in connection.execute(
                """
                SELECT event_type FROM hermes_broker.broker_authority_audit
                ORDER BY audit_sequence
                """
            ).fetchall()
        ]
    return reservations, nonce_events, events


def test_normal_reservation_is_terminal_and_exact_replay_is_idempotent(
    broker_dsn: str, tmp_path: Path
) -> None:
    case = _case(tmp_path, broker_dsn)
    first = case.service.reserve(
        action_input=case.action,
        signed_claim_input=case.signed,
        evaluated_at=case.evaluated_at,
    )
    second = case.service.reserve(
        action_input=case.action,
        signed_claim_input=case.signed,
        evaluated_at=case.evaluated_at,
    )

    assert first.outcome == "reserved"
    assert first.state is BrokerActionState.RESERVED
    assert first.idempotent_existing is False
    assert first.downstream_side_effect is False
    assert second.reservation_id == first.reservation_id
    assert second.idempotent_existing is True
    assert _counts(broker_dsn) == (
        1,
        1,
        ["claim_submitted", "claim_verified", "nonce_reserved"],
    )


def test_closed_state_audit_and_idempotency_vocabularies() -> None:
    assert {state.value for state in BrokerActionState} == {
        "submitted",
        "verified",
        "reserved",
        "rejected",
    }
    assert {event.value for event in BrokerAuditEventType} == {
        "claim_submitted",
        "claim_verified",
        "claim_rejected",
        "nonce_reserved",
    }
    action_hash = "a" * 64
    nonce = "b" * 64
    expected = broker_sha256(
        {
            "schema_version": "hermes_broker_reservation_idempotency_v1",
            "executable_action_sha256": action_hash,
            "single_use_nonce": nonce,
        }
    )
    assert reservation_idempotency_key(action_hash, nonce) == expected


def test_missing_durable_key_snapshot_fails_closed(broker_dsn: str, tmp_path: Path) -> None:
    case = _case(tmp_path, broker_dsn, insert_key=False)
    result = case.service.reserve(
        action_input=case.action,
        signed_claim_input=case.signed,
        evaluated_at=case.evaluated_at,
    )
    assert result.outcome == "rejected"
    assert result.rejection_reason == "trusted_key_registry_unavailable"
    assert _counts(broker_dsn)[:2] == (0, 0)


@pytest.mark.parametrize(
    ("registry_version", "revoked", "reason"),
    [
        (PROOF_KEY_REGISTRY_VERSION, True, "revoked_signer"),
        ("broker2-current-keys-v2", False, "key_registry_stale"),
    ],
)
def test_current_durable_revocation_and_registry_version_fail_closed(
    broker_dsn: str,
    tmp_path: Path,
    registry_version: str,
    revoked: bool,
    reason: str,
) -> None:
    case = _case(tmp_path, broker_dsn, insert_key=False)
    _insert_key_snapshot(
        broker_dsn,
        case.private_key,
        key_id="broker2-valid-key",
        added_at=case.evaluated_at,
        version=registry_version,
        revoked=revoked,
    )
    result = case.service.reserve(
        action_input=case.action,
        signed_claim_input=case.signed,
        evaluated_at=case.evaluated_at,
    )
    assert result.outcome == "rejected"
    assert result.rejection_reason == reason
    assert _counts(broker_dsn)[:2] == (0, 0)


def test_transaction_time_expiry_recheck_rejects_without_nonce_burn(
    broker_dsn: str, tmp_path: Path
) -> None:
    issued_at = datetime.now(UTC).replace(microsecond=0) - timedelta(minutes=2)
    case = _case(
        tmp_path,
        broker_dsn,
        issued_at=issued_at,
        expiry=issued_at + timedelta(minutes=1),
    )
    result = case.service.reserve(
        action_input=case.action,
        signed_claim_input=case.signed,
        evaluated_at=issued_at + timedelta(seconds=1),
    )
    assert result.outcome == "rejected"
    assert result.rejection_reason == "expired_before_reservation"
    assert _counts(broker_dsn) == (
        0,
        0,
        ["claim_submitted", "claim_verified", "claim_rejected"],
    )


def test_valid_signature_cannot_reserve_retained_a0(broker_dsn: str, tmp_path: Path) -> None:
    case = _case(tmp_path, broker_dsn)
    a0_id = "HERMES-PREP-20260818T120000Z-aaaaaaaaaaaaaaaa"
    source = tmp_path / "a0-source"
    a0_payload, _ = write_fresh_prepared_fixture(
        source_root=source,
        authority_class=AuthorityClass.A0,
        repo_sha=REPO_SHA,
        prepared_record_id=a0_id,
        created_at=case.evaluated_at,
    )
    case.artifact_store.retain_from_outbox(
        source_outbox_root=source,
        prepared_record_id=a0_id,
        clock=case.evaluated_at,
    )
    action = make_action(
        payload=a0_payload,
        prepared_record_id=a0_id,
        action_id="broker2-signed-a0-adversary",
    )
    payload = make_claim_payload(
        action=action,
        signer_key_id="broker2-valid-key",
        issued_at=case.evaluated_at,
    )
    signed = case.sign(payload)
    result = case.service.reserve(
        action_input=action,
        signed_claim_input=signed,
        evaluated_at=case.evaluated_at,
    )
    assert result.outcome == "rejected"
    assert result.rejection_reason == "a0_forbidden"
    assert _counts(broker_dsn)[:2] == (0, 0)


def test_broker2_production_surface_has_no_external_execution_capability() -> None:
    files = [
        REPO_ROOT / "tools/hermes/broker/migrations.py",
        REPO_ROOT / "tools/hermes/broker/state.py",
        REPO_ROOT / "tools/hermes/broker/store.py",
        REPO_ROOT / "tools/hermes/broker/reservation.py",
    ]
    forbidden_import_roots = {
        "httpx",
        "prefect",
        "requests",
        "socket",
        "subprocess",
        "urllib",
    }
    for path in files:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        imports = {
            node.module.split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module
        }
        imports.update(
            alias.name.split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        )
        assert not (imports & forbidden_import_roots), path.name
    result_fields = set(BrokerReservationService.reserve.__annotations__)
    assert "adapter" not in result_fields
    assert "dispatcher" not in result_fields
