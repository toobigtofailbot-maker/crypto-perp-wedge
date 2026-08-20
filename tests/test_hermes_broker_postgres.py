from __future__ import annotations

import os
import shutil
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from threading import Barrier
from typing import Any

import psycopg
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from tools.hermes.broker import migrations
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
    BrokerReservationError,
    BrokerReservationService,
)
from tools.hermes.broker.retention import BrokerArtifactStore
from tools.hermes.broker.store import (
    BrokerAuthorityStore,
    TrustedKeyRegistryUnavailable,
)
from tools.hermes.proposals.models import AuthorityClass

REPO_ROOT = Path(__file__).resolve().parents[1]
REPO_SHA = "5" * 40


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
class PostgresCase:
    service: BrokerReservationService
    store: BrokerAuthorityStore
    artifact_store: BrokerArtifactStore
    private_key: Ed25519PrivateKey
    action: Any
    payload: ApprovalClaimPayload
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


def _insert_key(
    dsn: str,
    private_key: Ed25519PrivateKey,
    *,
    key_id: str = "broker2-postgres-key",
    epoch: int = 1,
    version: str = PROOF_KEY_REGISTRY_VERSION,
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


def _case(
    tmp_path: Path,
    dsn: str,
    *,
    action_id: str,
    suffix: str,
    insert_key: bool,
) -> PostgresCase:
    now = datetime.now(UTC).replace(microsecond=0)
    prepared_id = f"HERMES-PREP-20260818T130000Z-{suffix}"
    source = tmp_path / f"source-{suffix}"
    prepared, _ = write_fresh_prepared_fixture(
        source_root=source,
        authority_class=AuthorityClass.A1,
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
    action = make_action(payload=prepared, prepared_record_id=prepared_id, action_id=action_id)
    payload = make_claim_payload(
        action=action,
        signer_key_id="broker2-postgres-key",
        issued_at=now,
    )
    signed = sign_claim_for_proof(
        action=action,
        prepared_payload=prepared,
        claim_payload=payload,
        private_key=private_key,
    )
    if insert_key:
        _insert_key(dsn, private_key, added_at=now)
    store = BrokerAuthorityStore(dsn)
    return PostgresCase(
        service=BrokerReservationService(
            store=store,
            artifact_store=artifact_store,
            action_registry=proof_registry(),
            current_repo_sha=REPO_SHA,
        ),
        store=store,
        artifact_store=artifact_store,
        private_key=private_key,
        action=action,
        payload=payload,
        signed=signed,
        evaluated_at=now,
    )


def _reserve(case: PostgresCase) -> Any:
    return case.service.reserve(
        action_input=case.action,
        signed_claim_input=case.signed,
        evaluated_at=case.evaluated_at,
    )


def _physical_counts(dsn: str) -> tuple[int, int]:
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


def test_migration_checksum_catalog_constraints_and_triggers(
    broker_dsn: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    expected_versions = ("0001_broker_authority", "0002_broker_dry_run_dispatch")
    assert apply_migrations(broker_dsn).already_applied == expected_versions
    real_dir = migrations.MIGRATIONS_DIR
    migration_copy = tmp_path / "migrations"
    migration_copy.mkdir()
    for version in expected_versions:
        shutil.copyfile(real_dir / f"{version}.sql", migration_copy / f"{version}.sql")
    monkeypatch.setattr(migrations, "MIGRATIONS_DIR", migration_copy)
    assert apply_migrations(broker_dsn).already_applied == expected_versions
    # Modified bytes under either applied migration version are rejected, and the
    # historical 0001 bytes stay protected alongside the new 0002 migration.
    for version in expected_versions:
        target = migration_copy / f"{version}.sql"
        original = target.read_text(encoding="utf-8")
        target.write_text(original + "\n-- changed\n", encoding="utf-8")
        with pytest.raises(RuntimeError, match="checksum mismatch"):
            apply_migrations(broker_dsn)
        target.write_text(original, encoding="utf-8")

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
        constraints = {
            row[0]
            for row in connection.execute(
                """
                SELECT conname FROM pg_constraint
                WHERE connamespace = 'hermes_broker'::regnamespace
                """
            )
        }
        triggers = {
            row[0]
            for row in connection.execute(
                """
                SELECT tgname FROM pg_trigger
                WHERE tgrelid IN (
                    SELECT oid FROM pg_class
                    WHERE relnamespace = 'hermes_broker'::regnamespace
                ) AND NOT tgisinternal
                """
            )
        }
    assert tables == {
        "schema_migrations",
        "broker_approval",
        "broker_reservation",
        "broker_authority_audit",
        "broker_trusted_key",
        "broker_action_state",
    }
    assert {
        "uq_broker_reservation_single_use_nonce",
        "uq_broker_reservation_idempotency_key",
    } <= constraints
    assert triggers == {
        "broker_approval_immutable",
        "broker_reservation_immutable",
        "broker_authority_audit_immutable",
        "broker_trusted_key_immutable",
        "broker_action_state_guard",
    }
    assert not any("dispatch" in table for table in tables)


def test_database_guards_immutable_rows_and_closed_state_transitions(
    broker_dsn: str, tmp_path: Path
) -> None:
    case = _case(
        tmp_path,
        broker_dsn,
        action_id="broker2-db-guard-action",
        suffix="2222222222222222",
        insert_key=True,
    )
    result = _reserve(case)
    assert result.outcome == "reserved"
    with psycopg.connect(broker_dsn) as connection:
        with pytest.raises(psycopg.Error):
            connection.execute(
                """
                UPDATE hermes_broker.broker_reservation
                SET reserved_at = clock_timestamp()
                WHERE reservation_id = %s
                """,
                (result.reservation_id,),
            )
        connection.rollback()
        with pytest.raises(psycopg.Error):
            connection.execute(
                """
                UPDATE hermes_broker.broker_action_state
                SET state = 'verified', state_version = state_version + 1,
                    reservation_id = NULL, updated_at = clock_timestamp()
                WHERE executable_action_id = %s
                """,
                (case.action.executable_action_id,),
            )
        connection.rollback()
        with pytest.raises(psycopg.Error):
            connection.execute(
                """
                UPDATE hermes_broker.broker_action_state
                SET state = 'failed', state_version = state_version + 1,
                    updated_at = clock_timestamp()
                WHERE executable_action_id = %s
                """,
                (case.action.executable_action_id,),
            )


def test_current_key_epoch_loads_public_material_and_mixed_version_fails_closed(
    broker_dsn: str,
) -> None:
    now = datetime.now(UTC).replace(microsecond=0)
    first = Ed25519PrivateKey.from_private_bytes(bytes(range(32)))
    second = Ed25519PrivateKey.from_private_bytes(bytes(range(1, 33)))
    _insert_key(broker_dsn, first, key_id="key-one", added_at=now, version="keys-v1")
    registry = BrokerAuthorityStore(broker_dsn).load_current_trusted_key_registry()
    assert registry.key_registry_version == "keys-v1"
    assert (
        registry.keys[0].public_key
        == first.public_key()
        .public_bytes(
            serialization.Encoding.Raw,
            serialization.PublicFormat.Raw,
        )
        .hex()
    )
    with psycopg.connect(broker_dsn) as connection:
        private_columns = connection.execute(
            """
            SELECT count(*) FROM information_schema.columns
            WHERE table_schema = 'hermes_broker'
              AND table_name = 'broker_trusted_key'
              AND column_name ILIKE '%private%'
            """
        ).fetchone()[0]
    assert private_columns == 0
    _insert_key(
        broker_dsn,
        second,
        key_id="key-two",
        added_at=now,
        version="keys-v2",
    )
    with pytest.raises(TrustedKeyRegistryUnavailable, match="mixed registry versions"):
        BrokerAuthorityStore(broker_dsn).load_current_trusted_key_registry()


def test_real_concurrent_identical_and_conflicting_nonce_races(
    broker_dsn: str, tmp_path: Path
) -> None:
    same = _case(
        tmp_path,
        broker_dsn,
        action_id="broker2-race-same",
        suffix="3333333333333333",
        insert_key=True,
    )
    barrier = Barrier(2)

    def run_same() -> Any:
        barrier.wait()
        return _reserve(same)

    with ThreadPoolExecutor(max_workers=2) as pool:
        same_results = list(pool.map(lambda _: run_same(), range(2)))
    assert {result.outcome for result in same_results} == {"reserved"}
    assert len({result.reservation_id for result in same_results}) == 1
    assert sum(result.idempotent_existing for result in same_results) == 1
    assert _physical_counts(broker_dsn) == (1, 1)

    with psycopg.connect(broker_dsn, autocommit=True) as connection:
        connection.execute("DROP SCHEMA hermes_broker CASCADE")
    apply_migrations(broker_dsn)
    left = _case(
        tmp_path,
        broker_dsn,
        action_id="broker2-race-left",
        suffix="4444444444444444",
        insert_key=True,
    )
    right = _case(
        tmp_path,
        broker_dsn,
        action_id="broker2-race-right",
        suffix="5555555555555555",
        insert_key=False,
    )
    shared_nonce = "d" * 64
    left.payload = left.payload.model_copy(update={"single_use_nonce": shared_nonce})
    left.signed = left.sign(left.payload)
    right.payload = right.payload.model_copy(update={"single_use_nonce": shared_nonce})
    right.signed = right.sign(right.payload)
    barrier = Barrier(2)

    def run_conflict(case: PostgresCase) -> Any:
        barrier.wait()
        return _reserve(case)

    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(run_conflict, case) for case in (left, right)]
        conflict_results = [future.result() for future in futures]
    assert sorted(result.outcome for result in conflict_results) == ["rejected", "reserved"]
    loser = next(result for result in conflict_results if result.outcome == "rejected")
    assert loser.rejection_reason == "nonce_already_reserved"
    assert _physical_counts(broker_dsn) == (1, 1)


def test_deferred_commit_failure_leaves_verified_and_nonce_reusable(
    broker_dsn: str, tmp_path: Path
) -> None:
    case = _case(
        tmp_path,
        broker_dsn,
        action_id="broker2-commit-failure",
        suffix="6666666666666666",
        insert_key=True,
    )
    with psycopg.connect(broker_dsn) as connection:
        connection.execute(
            """
            CREATE FUNCTION hermes_broker.test_fail_reservation_commit()
            RETURNS trigger LANGUAGE plpgsql AS $$
            BEGIN
                RAISE EXCEPTION 'test-only deferred reservation commit failure';
            END;
            $$
            """
        )
        connection.execute(
            """
            CREATE CONSTRAINT TRIGGER test_fail_reservation_commit
            AFTER INSERT ON hermes_broker.broker_reservation
            DEFERRABLE INITIALLY DEFERRED
            FOR EACH ROW EXECUTE FUNCTION hermes_broker.test_fail_reservation_commit()
            """
        )
    with pytest.raises(BrokerReservationError, match="did not commit"):
        _reserve(case)
    state = case.store.get_action_state(case.action.executable_action_id)
    assert state is not None and state.state.value == "verified"
    assert _physical_counts(broker_dsn) == (0, 0)
    with psycopg.connect(broker_dsn) as connection:
        event_types = [
            row[0]
            for row in connection.execute(
                """
                SELECT event_type FROM hermes_broker.broker_authority_audit
                ORDER BY audit_sequence
                """
            )
        ]
        assert event_types == ["claim_submitted", "claim_verified"]
        connection.execute(
            "DROP TRIGGER test_fail_reservation_commit ON hermes_broker.broker_reservation"
        )
        connection.execute("DROP FUNCTION hermes_broker.test_fail_reservation_commit()")
    result = _reserve(case)
    assert result.outcome == "reserved"
    assert _physical_counts(broker_dsn) == (1, 1)


def test_committed_reservation_survives_fresh_store_and_permanently_burns_nonce(
    broker_dsn: str, tmp_path: Path
) -> None:
    original = _case(
        tmp_path,
        broker_dsn,
        action_id="broker2-crash-original",
        suffix="7777777777777777",
        insert_key=True,
    )
    first = _reserve(original)
    restarted = PostgresCase(
        service=BrokerReservationService(
            store=BrokerAuthorityStore(broker_dsn),
            artifact_store=original.artifact_store,
            action_registry=proof_registry(),
            current_repo_sha=REPO_SHA,
        ),
        store=BrokerAuthorityStore(broker_dsn),
        artifact_store=original.artifact_store,
        private_key=original.private_key,
        action=original.action,
        payload=original.payload,
        signed=original.signed,
        evaluated_at=original.evaluated_at,
    )
    replay = _reserve(restarted)
    assert replay.reservation_id == first.reservation_id
    assert replay.idempotent_existing is True

    conflicting = _case(
        tmp_path,
        broker_dsn,
        action_id="broker2-crash-conflict",
        suffix="8888888888888888",
        insert_key=False,
    )
    conflicting.payload = conflicting.payload.model_copy(
        update={"single_use_nonce": original.payload.single_use_nonce}
    )
    conflicting.signed = conflicting.sign(conflicting.payload)
    conflict = _reserve(conflicting)
    assert conflict.outcome == "rejected"
    assert conflict.rejection_reason == "nonce_already_reserved"
    assert _physical_counts(broker_dsn) == (1, 1)
