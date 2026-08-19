"""BROKER-2 orchestration: verify, durably reserve once, and stop."""

from __future__ import annotations

import re
from collections.abc import Mapping
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ValidationError

from tools.hermes.proposals.models import AuthorityClass

from .models import DecisionValue, ExecutableAction, SignedApprovalClaim
from .registry import ActionRegistry
from .retention import BrokerArtifactStore
from .serialization import broker_canonical_json_bytes, broker_sha256, scope_digest
from .state import (
    BrokerActionState,
    BrokerAuditEventType,
    BrokerReservationResult,
    build_audit_record,
)
from .store import (
    ActionStateRecord,
    ApprovalIdentityConflict,
    ApprovalRecord,
    BrokerAuthorityStore,
    BrokerStoreError,
    NonceReservationConflict,
    ReservationRecord,
    TrustedKeyRegistryUnavailable,
)
from .verification import ZERO_SHA256, verify_approval

NONCE_UNIQUE_CONSTRAINT = "uq_broker_reservation_single_use_nonce"
IDEMPOTENCY_SCHEMA_VERSION = "hermes_broker_reservation_idempotency_v1"


class BrokerReservationError(RuntimeError):
    """A durable operation error that never fabricates a terminal state."""


class _InputRejection(ValueError):
    def __init__(self, reason: str, raw_action: Mapping[str, Any] | None, raw_claim: Any) -> None:
        super().__init__(reason)
        self.reason = reason
        self.raw_action = raw_action
        self.raw_claim = raw_claim


def _mapping(value: Mapping[str, Any] | BaseModel) -> Mapping[str, Any] | None:
    if isinstance(value, BaseModel):
        return value.model_dump(mode="python")
    return value if isinstance(value, Mapping) else None


def _identity(value: Any, fallback: str = "unknown") -> str:
    if isinstance(value, str) and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,127}", value):
        return value
    return fallback


def reservation_idempotency_key(executable_action_sha256: str, nonce: str) -> str:
    return broker_sha256(
        {
            "schema_version": IDEMPOTENCY_SCHEMA_VERSION,
            "executable_action_sha256": executable_action_sha256,
            "single_use_nonce": nonce,
        }
    )


class BrokerReservationService:
    """Turns one unchanged BROKER-1 allow decision into durable reserved state only."""

    def __init__(
        self,
        *,
        store: BrokerAuthorityStore,
        artifact_store: BrokerArtifactStore,
        action_registry: ActionRegistry,
        current_repo_sha: str,
    ) -> None:
        self._store = store
        self._artifact_store = artifact_store
        self._action_registry = action_registry
        self._current_repo_sha = current_repo_sha

    def reserve(
        self,
        *,
        action_input: Mapping[str, Any] | BaseModel,
        signed_claim_input: Mapping[str, Any] | BaseModel,
        evaluated_at: datetime,
    ) -> BrokerReservationResult:
        try:
            action, claim = self._materialize(action_input, signed_claim_input)
        except _InputRejection as exc:
            return self._input_rejection_result(exc)

        action_sha256 = broker_sha256(action)
        nonce = claim.payload.single_use_nonce
        idempotency_key = reservation_idempotency_key(action_sha256, nonce)
        existing = self._store.reservation_by_idempotency(idempotency_key)
        if existing is not None:
            self._require_reservation_identity(
                existing,
                executable_action_sha256=action_sha256,
                single_use_nonce=nonce,
                idempotency_key=idempotency_key,
            )
            return self._reserved_result(existing, idempotent_existing=True)

        submitted_at = self._store.database_time()
        approval = self._approval_record(action, claim, action_sha256, submitted_at)
        bindings = self._audit_bindings(approval)
        submitted_audit = build_audit_record(
            event_type=BrokerAuditEventType.CLAIM_SUBMITTED,
            occurred_at=submitted_at,
            bindings=bindings,
            evidence={
                "signed_claim_sha256": approval.signed_claim_sha256,
                "retention_root_ref": approval.retention_root_ref,
            },
        )
        try:
            state = self._store.submit_approval(approval, submitted_audit)
        except (ApprovalIdentityConflict, BrokerStoreError) as exc:
            raise BrokerReservationError("durable broker submission did not commit") from exc

        terminal = self._existing_terminal_result(state, idempotency_key, nonce)
        if terminal is not None:
            return terminal

        if state.state is BrokerActionState.SUBMITTED:
            state = self._verify_and_transition(
                action=action,
                claim=claim,
                evaluated_at=evaluated_at,
                bindings=bindings,
            )
            if state.state is BrokerActionState.REJECTED:
                return self._rejected_result(
                    approval,
                    state.last_reason_code or "verification_rejected",
                )
            terminal = self._existing_terminal_result(state, idempotency_key, nonce)
            if terminal is not None:
                return terminal

        deterministic_reservation_id = f"BROKER-RES-{idempotency_key[:32]}"

        def audit_builder(
            *,
            occurred_at: datetime,
            reason_code: str | None = None,
            reservation_id: str | None = None,
            idempotency_key: str | None = None,
        ) -> Any:
            if reason_code is not None:
                return build_audit_record(
                    event_type=BrokerAuditEventType.CLAIM_REJECTED,
                    occurred_at=occurred_at,
                    bindings=bindings,
                    reason_code=reason_code,
                    evidence={"transaction_time_expiry_recheck": True},
                )
            return build_audit_record(
                event_type=BrokerAuditEventType.NONCE_RESERVED,
                occurred_at=occurred_at,
                bindings={**bindings, "reservation_id": reservation_id},
                evidence={
                    "idempotency_key": idempotency_key,
                    "nonce_unique_constraint": NONCE_UNIQUE_CONSTRAINT,
                    "committed_reservation_timestamp": occurred_at.isoformat(),
                },
            )

        try:
            transaction = self._store.reserve(
                approval_id=approval.approval_id,
                executable_action_id=approval.executable_action_id,
                executable_action_sha256=approval.executable_action_sha256,
                prepared_record_id=approval.prepared_record_id,
                prepared_payload_sha256=approval.prepared_payload_sha256,
                single_use_nonce=approval.single_use_nonce,
                idempotency_key=idempotency_key,
                reservation_id=deterministic_reservation_id,
                audit_builder=audit_builder,
            )
        except NonceReservationConflict as exc:
            return self._resolve_unique_conflict(
                approval=approval,
                bindings=bindings,
                idempotency_key=idempotency_key,
                constraint_name=exc.constraint_name,
            )
        except BrokerStoreError as exc:
            raise BrokerReservationError("reservation transaction did not commit") from exc

        if transaction.status == "expired":
            return self._rejected_result(approval, "expired_before_reservation")
        if transaction.reservation is None:
            raise BrokerReservationError("reservation transaction returned no durable row")
        self._require_reservation_identity(
            transaction.reservation,
            executable_action_sha256=action_sha256,
            single_use_nonce=nonce,
            idempotency_key=idempotency_key,
        )
        return self._reserved_result(
            transaction.reservation,
            idempotent_existing=transaction.status == "existing",
        )

    def _materialize(
        self,
        action_input: Mapping[str, Any] | BaseModel,
        signed_claim_input: Mapping[str, Any] | BaseModel,
    ) -> tuple[ExecutableAction, SignedApprovalClaim]:
        raw_action = _mapping(action_input)
        raw_claim = _mapping(signed_claim_input)
        if raw_action is None:
            raise _InputRejection("malformed_action", None, raw_claim)
        if raw_action.get("authority_class") in (AuthorityClass.A0, "A0"):
            raise _InputRejection("a0_forbidden", raw_action, raw_claim)
        action_type = raw_action.get("action_type")
        if not isinstance(action_type, str):
            raise _InputRejection("malformed_action", raw_action, raw_claim)
        entry = self._action_registry.get(action_type)
        if entry is None:
            raise _InputRejection("unknown_action_type", raw_action, raw_claim)
        try:
            action = entry.action_model.model_validate(raw_action)
        except ValidationError as exc:
            raise _InputRejection("malformed_action", raw_action, raw_claim) from exc
        if raw_claim is None:
            raise _InputRejection("malformed_claim", raw_action, raw_claim)
        try:
            claim = SignedApprovalClaim.model_validate(raw_claim)
        except ValidationError as exc:
            raise _InputRejection("malformed_claim", raw_action, raw_claim) from exc
        return action, claim

    def _verify_and_transition(
        self,
        *,
        action: ExecutableAction,
        claim: SignedApprovalClaim,
        evaluated_at: datetime,
        bindings: dict[str, Any],
    ) -> ActionStateRecord:
        try:
            key_registry = self._store.load_current_trusted_key_registry()
        except TrustedKeyRegistryUnavailable:
            return self._reject_state(
                action.executable_action_id,
                bindings,
                "trusted_key_registry_unavailable",
                self._store.database_time(),
            )
        decision = verify_approval(
            action_input=action,
            signed_claim_input=claim,
            action_registry=self._action_registry,
            key_registry=key_registry,
            artifact_store=self._artifact_store,
            current_repo_sha=self._current_repo_sha,
            evaluated_at=evaluated_at,
        )
        if decision.decision is DecisionValue.REJECT:
            return self._reject_state(
                action.executable_action_id,
                bindings,
                decision.reason_code.value,
                decision.evaluated_at,
                decision_id=decision.decision_id,
                signed_claim_sha256=broker_sha256(claim),
            )
        audit = build_audit_record(
            event_type=BrokerAuditEventType.CLAIM_VERIFIED,
            occurred_at=decision.evaluated_at,
            bindings=bindings,
            evidence={
                "broker1_decision_id": decision.decision_id,
                "broker1_reason": "verified",
                "signed_claim_sha256": broker_sha256(claim),
            },
        )
        return self._store.mark_verified(action.executable_action_id, audit)

    def _reject_state(
        self,
        executable_action_id: str,
        bindings: dict[str, Any],
        reason: str,
        occurred_at: datetime,
        **evidence: Any,
    ) -> ActionStateRecord:
        audit = build_audit_record(
            event_type=BrokerAuditEventType.CLAIM_REJECTED,
            occurred_at=occurred_at,
            bindings=bindings,
            reason_code=reason,
            evidence=evidence,
        )
        return self._store.mark_rejected(executable_action_id, reason, audit)

    def _resolve_unique_conflict(
        self,
        *,
        approval: ApprovalRecord,
        bindings: dict[str, Any],
        idempotency_key: str,
        constraint_name: str | None,
    ) -> BrokerReservationResult:
        existing = self._store.reservation_by_nonce(approval.single_use_nonce)
        if existing is not None and existing.idempotency_key == idempotency_key:
            self._require_reservation_identity(
                existing,
                executable_action_sha256=approval.executable_action_sha256,
                single_use_nonce=approval.single_use_nonce,
                idempotency_key=idempotency_key,
            )
            return self._reserved_result(existing, idempotent_existing=True)
        occurred_at = self._store.database_time()
        state = self._reject_state(
            approval.executable_action_id,
            bindings,
            "nonce_already_reserved",
            occurred_at,
            nonce_unique_constraint=constraint_name,
        )
        if state.state is BrokerActionState.RESERVED and existing is not None:
            self._require_reservation_identity(
                existing,
                executable_action_sha256=approval.executable_action_sha256,
                single_use_nonce=approval.single_use_nonce,
                idempotency_key=idempotency_key,
            )
            return self._reserved_result(existing, idempotent_existing=True)
        return self._rejected_result(approval, "nonce_already_reserved")

    def _approval_record(
        self,
        action: ExecutableAction,
        claim: SignedApprovalClaim,
        action_sha256: str,
        submitted_at: datetime,
    ) -> ApprovalRecord:
        payload = claim.payload
        return ApprovalRecord(
            approval_id=payload.approval_id,
            executable_action_id=action.executable_action_id,
            executable_action_sha256=action_sha256,
            executable_action_canonical=broker_canonical_json_bytes(action),
            signed_claim_sha256=broker_sha256(claim),
            signed_claim_canonical=broker_canonical_json_bytes(claim),
            prepared_record_id=action.prepared_record_id,
            prepared_payload_sha256=action.prepared_payload_sha256,
            source_proposal_id=action.source_proposal_id,
            source_proposal_content_sha256=action.source_proposal_content_sha256,
            repo_sha=action.repo_sha,
            authority_class=action.authority_class.value,
            action_type=action.action_type,
            action_registry_version=action.action_registry_version,
            adapter_id=action.adapter_id,
            adapter_version=action.adapter_version,
            key_registry_version=payload.key_registry_version,
            scope_digest=scope_digest(action.scope),
            budget_bound=action.budget_bound.model_dump(mode="json"),
            count_or_quantity_bound=(
                action.count_or_quantity_bound.model_dump(mode="json")
                if action.count_or_quantity_bound is not None
                else None
            ),
            timeout_bound=action.timeout.model_dump(mode="json"),
            issued_at=payload.issued_at,
            not_before=payload.not_before,
            expiry=payload.expiry,
            single_use_nonce=payload.single_use_nonce,
            signer_key_id=payload.signer_key_id,
            signature_algorithm=claim.signature_algorithm,
            signature_encoding=claim.signature_encoding,
            retention_root_ref=str(self._artifact_store.root.resolve()),
            submitted_at=submitted_at,
        )

    @staticmethod
    def _audit_bindings(approval: ApprovalRecord) -> dict[str, Any]:
        return {
            "approval_id": approval.approval_id,
            "executable_action_id": approval.executable_action_id,
            "executable_action_sha256": approval.executable_action_sha256,
            "prepared_record_id": approval.prepared_record_id,
            "prepared_payload_sha256": approval.prepared_payload_sha256,
            "source_proposal_id": approval.source_proposal_id,
            "source_proposal_content_sha256": approval.source_proposal_content_sha256,
            "repo_sha": approval.repo_sha,
            "action_registry_version": approval.action_registry_version,
            "adapter_id": approval.adapter_id,
            "adapter_version": approval.adapter_version,
            "key_registry_version": approval.key_registry_version,
            "single_use_nonce": approval.single_use_nonce,
        }

    def _existing_terminal_result(
        self,
        state: ActionStateRecord,
        idempotency_key: str,
        single_use_nonce: str,
    ) -> BrokerReservationResult | None:
        if state.state is BrokerActionState.RESERVED:
            existing = self._store.reservation_by_idempotency(idempotency_key)
            if existing is None:
                raise BrokerReservationError("reserved action has no matching reservation")
            self._require_reservation_identity(
                existing,
                executable_action_sha256=state.executable_action_sha256,
                single_use_nonce=single_use_nonce,
                idempotency_key=idempotency_key,
            )
            return self._reserved_result(existing, idempotent_existing=True)
        if state.state is BrokerActionState.REJECTED:
            return BrokerReservationResult(
                outcome="rejected",
                executable_action_id=state.executable_action_id,
                executable_action_sha256=state.executable_action_sha256,
                approval_id=state.approval_id,
                reservation_id=None,
                state=BrokerActionState.REJECTED,
                idempotent_existing=False,
                rejection_reason=state.last_reason_code or "rejected",
                downstream_side_effect=False,
            )
        return None

    @staticmethod
    def _require_reservation_identity(
        reservation: ReservationRecord,
        *,
        executable_action_sha256: str,
        single_use_nonce: str,
        idempotency_key: str,
    ) -> None:
        if (
            reservation.executable_action_sha256 != executable_action_sha256
            or reservation.single_use_nonce != single_use_nonce
            or reservation.idempotency_key != idempotency_key
        ):
            raise BrokerReservationError("durable reservation identity conflict")

    @staticmethod
    def _reserved_result(
        reservation: ReservationRecord,
        *,
        idempotent_existing: bool,
    ) -> BrokerReservationResult:
        return BrokerReservationResult(
            outcome="reserved",
            executable_action_id=reservation.executable_action_id,
            executable_action_sha256=reservation.executable_action_sha256,
            approval_id=reservation.approval_id,
            reservation_id=reservation.reservation_id,
            state=BrokerActionState.RESERVED,
            idempotent_existing=idempotent_existing,
            rejection_reason=None,
            downstream_side_effect=False,
        )

    @staticmethod
    def _rejected_result(approval: ApprovalRecord, reason: str) -> BrokerReservationResult:
        return BrokerReservationResult(
            outcome="rejected",
            executable_action_id=approval.executable_action_id,
            executable_action_sha256=approval.executable_action_sha256,
            approval_id=approval.approval_id,
            reservation_id=None,
            state=BrokerActionState.REJECTED,
            idempotent_existing=False,
            rejection_reason=reason,
            downstream_side_effect=False,
        )

    @staticmethod
    def _input_rejection_result(exc: _InputRejection) -> BrokerReservationResult:
        raw_action = exc.raw_action or {}
        raw_claim = exc.raw_claim if isinstance(exc.raw_claim, Mapping) else {}
        raw_payload = raw_claim.get("payload") if isinstance(raw_claim, Mapping) else {}
        payload = raw_payload if isinstance(raw_payload, Mapping) else {}
        return BrokerReservationResult(
            outcome="rejected",
            executable_action_id=_identity(raw_action.get("executable_action_id")),
            executable_action_sha256=ZERO_SHA256,
            approval_id=_identity(payload.get("approval_id")),
            reservation_id=None,
            state=BrokerActionState.REJECTED,
            idempotent_existing=False,
            rejection_reason=exc.reason,
            downstream_side_effect=False,
        )
