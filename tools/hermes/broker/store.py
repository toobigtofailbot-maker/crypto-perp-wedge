"""Bounded PostgreSQL repository for durable BROKER-2 authority state."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Literal

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from .crypto import TrustedKeyRegistry, TrustedPublicKey
from .state import BrokerActionState, BrokerAuditRecord


class BrokerStoreError(RuntimeError):
    """Bounded durable-store error; it never implies a new persistent state."""


class ApprovalIdentityConflict(BrokerStoreError):
    pass


class TrustedKeyRegistryUnavailable(BrokerStoreError):
    pass


class BrokerStateConflict(BrokerStoreError):
    pass


class NonceReservationConflict(BrokerStoreError):
    def __init__(self, constraint_name: str | None) -> None:
        super().__init__(f"reservation uniqueness conflict: {constraint_name or 'unknown'}")
        self.constraint_name = constraint_name


@dataclass(frozen=True)
class ApprovalRecord:
    approval_id: str
    executable_action_id: str
    executable_action_sha256: str
    executable_action_canonical: bytes
    signed_claim_sha256: str
    signed_claim_canonical: bytes
    prepared_record_id: str
    prepared_payload_sha256: str
    source_proposal_id: str
    source_proposal_content_sha256: str
    repo_sha: str
    authority_class: str
    action_type: str
    action_registry_version: str
    adapter_id: str
    adapter_version: str
    key_registry_version: str
    scope_digest: str
    budget_bound: dict[str, Any]
    count_or_quantity_bound: dict[str, Any] | None
    timeout_bound: dict[str, Any]
    issued_at: datetime
    not_before: datetime
    expiry: datetime
    single_use_nonce: str
    signer_key_id: str
    signature_algorithm: str
    signature_encoding: str
    retention_root_ref: str
    submitted_at: datetime


@dataclass(frozen=True)
class ActionStateRecord:
    executable_action_id: str
    executable_action_sha256: str
    approval_id: str
    state: BrokerActionState
    state_version: int
    reservation_id: str | None
    last_reason_code: str | None
    updated_at: datetime


@dataclass(frozen=True)
class ReservationRecord:
    reservation_id: str
    approval_id: str
    executable_action_id: str
    executable_action_sha256: str
    prepared_record_id: str
    prepared_payload_sha256: str
    single_use_nonce: str
    idempotency_key: str
    reserved_at: datetime


@dataclass(frozen=True)
class ReservationTransactionResult:
    status: Literal["created", "existing", "expired"]
    reservation: ReservationRecord | None


_APPROVAL_COLUMNS = tuple(ApprovalRecord.__dataclass_fields__)
_APPROVAL_IDENTITY_COLUMNS = tuple(
    column for column in _APPROVAL_COLUMNS if column != "submitted_at"
)


def _bytes(value: Any) -> bytes:
    return bytes(value) if isinstance(value, memoryview) else value


def _action_state(row: dict[str, Any]) -> ActionStateRecord:
    return ActionStateRecord(
        executable_action_id=row["executable_action_id"],
        executable_action_sha256=row["executable_action_sha256"],
        approval_id=row["approval_id"],
        state=BrokerActionState(row["state"]),
        state_version=row["state_version"],
        reservation_id=row["reservation_id"],
        last_reason_code=row["last_reason_code"],
        updated_at=row["updated_at"],
    )


def _reservation(row: dict[str, Any]) -> ReservationRecord:
    return ReservationRecord(
        **{field: row[field] for field in ReservationRecord.__dataclass_fields__}
    )


class BrokerAuthorityStore:
    """Database-only repository; it has no dispatch, adapter, or retry surface."""

    def __init__(self, dsn: str) -> None:
        if not dsn or not dsn.strip():
            raise ValueError("broker PostgreSQL DSN is required")
        self._dsn = dsn

    def _connect(self) -> psycopg.Connection[dict[str, Any]]:
        return psycopg.connect(self._dsn, row_factory=dict_row)

    def database_time(self) -> datetime:
        with self._connect() as connection:
            return connection.execute("SELECT clock_timestamp() AS now").fetchone()["now"]

    def load_current_trusted_key_registry(self) -> TrustedKeyRegistry:
        with self._connect() as connection:
            epoch_row = connection.execute(
                "SELECT MAX(registry_epoch) AS epoch FROM hermes_broker.broker_trusted_key"
            ).fetchone()
            epoch = epoch_row["epoch"]
            if epoch is None:
                raise TrustedKeyRegistryUnavailable("no durable trusted-key snapshot exists")
            rows = connection.execute(
                """
                SELECT key_registry_version, key_id, algorithm, public_key_encoding,
                       public_key, state, added_at, revoked_at, revocation_reason, fixture_only
                FROM hermes_broker.broker_trusted_key
                WHERE registry_epoch = %s
                ORDER BY key_id
                """,
                (epoch,),
            ).fetchall()
        versions = {row["key_registry_version"] for row in rows}
        if len(versions) != 1:
            raise TrustedKeyRegistryUnavailable(
                "current durable trusted-key snapshot has mixed registry versions"
            )
        try:
            return TrustedKeyRegistry(
                key_registry_schema_version="hermes_broker_trusted_keys_v1",
                key_registry_version=versions.pop(),
                keys=tuple(
                    TrustedPublicKey(
                        key_id=row["key_id"],
                        algorithm=row["algorithm"],
                        public_key_encoding=row["public_key_encoding"],
                        public_key=row["public_key"],
                        state=row["state"],
                        added_at=row["added_at"].astimezone(UTC),
                        revoked_at=(
                            row["revoked_at"].astimezone(UTC)
                            if row["revoked_at"] is not None
                            else None
                        ),
                        revocation_reason=row["revocation_reason"],
                        fixture_only=row["fixture_only"],
                    )
                    for row in rows
                ),
            )
        except ValueError as exc:
            raise TrustedKeyRegistryUnavailable(
                f"current durable trusted-key snapshot is invalid: {exc}"
            ) from exc

    def submit_approval(
        self,
        approval: ApprovalRecord,
        audit: BrokerAuditRecord,
    ) -> ActionStateRecord:
        json_columns = {"budget_bound", "count_or_quantity_bound", "timeout_bound"}
        values = tuple(
            Jsonb(value) if column in json_columns and value is not None else value
            for column in _APPROVAL_COLUMNS
            for value in (getattr(approval, column),)
        )
        placeholders = ", ".join(["%s"] * len(_APPROVAL_COLUMNS))
        columns = ", ".join(_APPROVAL_COLUMNS)
        with self._connect() as connection, connection.transaction():
            connection.execute(
                f"""
                INSERT INTO hermes_broker.broker_approval ({columns})
                VALUES ({placeholders})
                ON CONFLICT DO NOTHING
                """,
                values,
            )
            stored = connection.execute(
                """
                SELECT * FROM hermes_broker.broker_approval
                WHERE approval_id = %s
                """,
                (approval.approval_id,),
            ).fetchone()
            if stored is None or not self._approval_matches(stored, approval):
                raise ApprovalIdentityConflict(
                    f"approval identity conflict: {approval.approval_id}"
                )
            inserted = connection.execute(
                """
                INSERT INTO hermes_broker.broker_action_state (
                    executable_action_id, executable_action_sha256, approval_id,
                    state, state_version, reservation_id, last_reason_code, updated_at
                ) VALUES (%s, %s, %s, 'submitted', 1, NULL, NULL, %s)
                ON CONFLICT (executable_action_id) DO NOTHING
                RETURNING executable_action_id
                """,
                (
                    approval.executable_action_id,
                    approval.executable_action_sha256,
                    approval.approval_id,
                    approval.submitted_at,
                ),
            ).fetchone()
            state_row = self._select_action_state(connection, approval.executable_action_id)
            if (
                state_row["executable_action_sha256"] != approval.executable_action_sha256
                or state_row["approval_id"] != approval.approval_id
            ):
                raise ApprovalIdentityConflict(
                    f"action identity conflict: {approval.executable_action_id}"
                )
            if inserted is not None:
                self._append_audit(connection, audit)
            return _action_state(state_row)

    @staticmethod
    def _approval_matches(stored: dict[str, Any], approval: ApprovalRecord) -> bool:
        for column in _APPROVAL_IDENTITY_COLUMNS:
            left = _bytes(stored[column])
            right = getattr(approval, column)
            if left != right:
                return False
        return True

    def get_action_state(self, executable_action_id: str) -> ActionStateRecord | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT * FROM hermes_broker.broker_action_state
                WHERE executable_action_id = %s
                """,
                (executable_action_id,),
            ).fetchone()
        return _action_state(row) if row is not None else None

    def mark_verified(
        self,
        executable_action_id: str,
        audit: BrokerAuditRecord,
    ) -> ActionStateRecord:
        with self._connect() as connection, connection.transaction():
            row = self._select_action_state(connection, executable_action_id, lock=True)
            if row["state"] == BrokerActionState.SUBMITTED.value:
                row = connection.execute(
                    """
                    UPDATE hermes_broker.broker_action_state
                    SET state = 'verified', state_version = state_version + 1, updated_at = %s
                    WHERE executable_action_id = %s
                    RETURNING *
                    """,
                    (audit.occurred_at, executable_action_id),
                ).fetchone()
                self._append_audit(connection, audit)
            return _action_state(row)

    def mark_rejected(
        self,
        executable_action_id: str,
        reason_code: str,
        audit: BrokerAuditRecord,
    ) -> ActionStateRecord:
        with self._connect() as connection, connection.transaction():
            row = self._select_action_state(connection, executable_action_id, lock=True)
            if row["state"] in (
                BrokerActionState.SUBMITTED.value,
                BrokerActionState.VERIFIED.value,
            ):
                row = connection.execute(
                    """
                    UPDATE hermes_broker.broker_action_state
                    SET state = 'rejected', state_version = state_version + 1,
                        reservation_id = NULL, last_reason_code = %s, updated_at = %s
                    WHERE executable_action_id = %s
                    RETURNING *
                    """,
                    (reason_code, audit.occurred_at, executable_action_id),
                ).fetchone()
                self._append_audit(connection, audit)
            return _action_state(row)

    def reserve(
        self,
        *,
        approval_id: str,
        executable_action_id: str,
        executable_action_sha256: str,
        prepared_record_id: str,
        prepared_payload_sha256: str,
        single_use_nonce: str,
        idempotency_key: str,
        reservation_id: str,
        audit_builder: Any,
    ) -> ReservationTransactionResult:
        """Atomically claim the nonce, append audit, and enter terminal reserved state."""

        try:
            return self._reserve_transaction(
                approval_id=approval_id,
                executable_action_id=executable_action_id,
                executable_action_sha256=executable_action_sha256,
                prepared_record_id=prepared_record_id,
                prepared_payload_sha256=prepared_payload_sha256,
                single_use_nonce=single_use_nonce,
                idempotency_key=idempotency_key,
                reservation_id=reservation_id,
                audit_builder=audit_builder,
            )
        except psycopg.errors.UniqueViolation as exc:
            raise NonceReservationConflict(exc.diag.constraint_name) from exc
        except psycopg.Error as exc:
            raise BrokerStoreError("reservation transaction did not commit") from exc

    def _reserve_transaction(
        self,
        *,
        approval_id: str,
        executable_action_id: str,
        executable_action_sha256: str,
        prepared_record_id: str,
        prepared_payload_sha256: str,
        single_use_nonce: str,
        idempotency_key: str,
        reservation_id: str,
        audit_builder: Any,
    ) -> ReservationTransactionResult:

        with self._connect() as connection, connection.transaction():
            state = self._select_action_state(connection, executable_action_id, lock=True)
            if state["state"] == BrokerActionState.RESERVED.value:
                existing = self._select_reservation_by_idempotency(connection, idempotency_key)
                if existing is None:
                    raise BrokerStateConflict("reserved state has no matching reservation")
                return ReservationTransactionResult("existing", _reservation(existing))
            if state["state"] != BrokerActionState.VERIFIED.value:
                raise BrokerStateConflict(
                    f"reservation requires verified state, found {state['state']}"
                )
            approval = connection.execute(
                """
                SELECT * FROM hermes_broker.broker_approval
                WHERE approval_id = %s AND executable_action_id = %s
                """,
                (approval_id, executable_action_id),
            ).fetchone()
            if approval is None:
                raise BrokerStateConflict("durable approval binding is missing")
            transaction_time = connection.execute("SELECT clock_timestamp() AS now").fetchone()[
                "now"
            ]
            if transaction_time >= approval["expiry"]:
                audit = audit_builder(
                    occurred_at=transaction_time,
                    reason_code="expired_before_reservation",
                )
                connection.execute(
                    """
                    UPDATE hermes_broker.broker_action_state
                    SET state = 'rejected', state_version = state_version + 1,
                        reservation_id = NULL,
                        last_reason_code = 'expired_before_reservation', updated_at = %s
                    WHERE executable_action_id = %s
                    """,
                    (transaction_time, executable_action_id),
                )
                self._append_audit(connection, audit)
                return ReservationTransactionResult("expired", None)
            row = connection.execute(
                """
                INSERT INTO hermes_broker.broker_reservation (
                    reservation_id, approval_id, executable_action_id,
                    executable_action_sha256, prepared_record_id,
                    prepared_payload_sha256, single_use_nonce, idempotency_key, reserved_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING *
                """,
                (
                    reservation_id,
                    approval_id,
                    executable_action_id,
                    executable_action_sha256,
                    prepared_record_id,
                    prepared_payload_sha256,
                    single_use_nonce,
                    idempotency_key,
                    transaction_time,
                ),
            ).fetchone()
            audit = audit_builder(
                occurred_at=transaction_time,
                reservation_id=reservation_id,
                idempotency_key=idempotency_key,
            )
            self._append_audit(connection, audit)
            connection.execute(
                """
                UPDATE hermes_broker.broker_action_state
                SET state = 'reserved', state_version = state_version + 1,
                    reservation_id = %s, last_reason_code = NULL, updated_at = %s
                WHERE executable_action_id = %s
                """,
                (reservation_id, transaction_time, executable_action_id),
            )
        return ReservationTransactionResult("created", _reservation(row))

    def reservation_by_idempotency(self, idempotency_key: str) -> ReservationRecord | None:
        with self._connect() as connection:
            row = self._select_reservation_by_idempotency(connection, idempotency_key)
        return _reservation(row) if row is not None else None

    def reservation_by_nonce(self, nonce: str) -> ReservationRecord | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT * FROM hermes_broker.broker_reservation
                WHERE single_use_nonce = %s
                """,
                (nonce,),
            ).fetchone()
        return _reservation(row) if row is not None else None

    @staticmethod
    def _select_action_state(
        connection: psycopg.Connection[dict[str, Any]],
        executable_action_id: str,
        *,
        lock: bool = False,
    ) -> dict[str, Any]:
        suffix = " FOR UPDATE" if lock else ""
        row = connection.execute(
            """
            SELECT * FROM hermes_broker.broker_action_state
            WHERE executable_action_id = %s
            """
            + suffix,
            (executable_action_id,),
        ).fetchone()
        if row is None:
            raise BrokerStateConflict(f"action state is missing: {executable_action_id}")
        return row

    @staticmethod
    def _select_reservation_by_idempotency(
        connection: psycopg.Connection[dict[str, Any]],
        idempotency_key: str,
    ) -> dict[str, Any] | None:
        return connection.execute(
            """
            SELECT * FROM hermes_broker.broker_reservation
            WHERE idempotency_key = %s
            """,
            (idempotency_key,),
        ).fetchone()

    @staticmethod
    def _append_audit(
        connection: psycopg.Connection[dict[str, Any]],
        audit: BrokerAuditRecord,
    ) -> None:
        inserted = connection.execute(
            """
            INSERT INTO hermes_broker.broker_authority_audit (
                event_id, event_type, approval_id, executable_action_id,
                executable_action_sha256, prepared_record_id, prepared_payload_sha256,
                source_proposal_id, source_proposal_content_sha256, repo_sha,
                action_registry_version, adapter_id, adapter_version, key_registry_version,
                single_use_nonce, reservation_id, occurred_at, actor, reason_code,
                event_payload_canonical, event_payload_sha256
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            ON CONFLICT (event_id) DO NOTHING
            RETURNING event_id
            """,
            (
                audit.event_id,
                audit.event_type.value,
                audit.approval_id,
                audit.executable_action_id,
                audit.executable_action_sha256,
                audit.prepared_record_id,
                audit.prepared_payload_sha256,
                audit.source_proposal_id,
                audit.source_proposal_content_sha256,
                audit.repo_sha,
                audit.action_registry_version,
                audit.adapter_id,
                audit.adapter_version,
                audit.key_registry_version,
                audit.single_use_nonce,
                audit.reservation_id,
                audit.occurred_at,
                audit.actor,
                audit.reason_code,
                audit.event_payload_canonical,
                audit.event_payload_sha256,
            ),
        ).fetchone()
        if inserted is None:
            row = connection.execute(
                """
                SELECT event_payload_sha256
                FROM hermes_broker.broker_authority_audit
                WHERE event_id = %s
                """,
                (audit.event_id,),
            ).fetchone()
            if row is None or row["event_payload_sha256"] != audit.event_payload_sha256:
                raise BrokerStateConflict(f"audit identity conflict: {audit.event_id}")
