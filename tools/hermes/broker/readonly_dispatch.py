"""H3-1 orchestration: verify, reserve, burn, project, read-only dispatch, audit.

This is the first real ask-and-act path. It composes only the unchanged BROKER-2
reservation service, the durable store, the fixed H3-1 read-only registry/projection,
the one structurally read-only adapter, and the inert external result store. It
accepts no arbitrary adapter callable, dispatcher callback, retry callback, command,
endpoint, or network client. The single real effect is a bounded read of committed
repo evidence at the bound SHA plus one inert result-record write; nothing in the
repo, canonical store, or any protected surface is mutated.
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, model_validator

from .adapters.readonly_repo_evidence import readonly_repo_evidence
from .h3_readonly import (
    READONLY_ACTION_TYPE,
    H3ReadonlyExecutableAction,
    H3ReadonlyProjection,
    build_h3_readonly_projection,
)
from .models import Identity, Sha256, SignedApprovalClaim, StrictBrokerModel
from .readonly_result_store import H3ReadonlyResultStore
from .registry import ActionRegistry
from .reservation import BrokerReservationService
from .serialization import broker_sha256
from .state import (
    BrokerActionState,
    BrokerAuditEventType,
    BrokerAuditRecord,
    BrokerReservationResult,
    build_audit_record,
)
from .store import BrokerAuthorityStore

DISPATCH_IDENTITY_SCHEMA_VERSION = "hermes_broker_h3_readonly_dispatch_identity_v1"
RECONCILE_REASON = "h3_readonly_dispatch_completion_unknown"

_TERMINAL_OUTCOMES: dict[BrokerActionState, str] = {
    BrokerActionState.COMPLETED: "completed",
    BrokerActionState.FAILED: "failed",
    BrokerActionState.RECONCILE_REQUIRED: "reconcile_required",
}


class BrokerReadonlyDispatchError(RuntimeError):
    """A durable dispatch error that never fabricates a terminal state."""


class StrandedReadonlyDispatchError(BrokerReadonlyDispatchError):
    """A prior dispatch attempt is durably `dispatched` and needs explicit reconcile."""


class BrokerReadonlyDispatchResult(StrictBrokerModel):
    outcome: Literal["completed", "failed", "reconcile_required", "rejected"]
    executable_action_id: Identity
    executable_action_sha256: Sha256
    approval_id: Identity
    reservation_id: Identity | None
    dispatch_id: Identity | None
    state: BrokerActionState
    idempotent_existing: bool
    reason_code: str | None
    result_record_id: Identity | None
    result_record_sha256: Sha256 | None
    retained_relative_path: str | None
    mutation_side_effect: Literal[False]
    protected_surface_touched: Literal[False]

    @model_validator(mode="after")
    def validate_outcome(self) -> BrokerReadonlyDispatchResult:
        if self.outcome == "completed":
            if (
                self.state is not BrokerActionState.COMPLETED
                or self.reservation_id is None
                or self.dispatch_id is None
                or self.reason_code is not None
            ):
                raise ValueError("completed dispatch requires reservation and dispatch")
            # A fresh completion must surface its written result record; an
            # idempotent replay returns the durable terminal state without
            # re-reading the already-persisted result artifact.
            if not self.idempotent_existing and self.result_record_id is None:
                raise ValueError("a fresh completed read-only dispatch must bind its result record")
        elif self.outcome == "failed":
            if (
                self.state is not BrokerActionState.FAILED
                or self.reservation_id is None
                or self.dispatch_id is None
                or not (self.reason_code and self.reason_code.strip())
            ):
                raise ValueError("failed dispatch requires reservation, dispatch, and a reason")
        elif self.outcome == "reconcile_required":
            if (
                self.state is not BrokerActionState.RECONCILE_REQUIRED
                or self.reservation_id is None
                or self.dispatch_id is None
                or not (self.reason_code and self.reason_code.strip())
            ):
                raise ValueError("reconcile requires reservation, dispatch, and a reason")
        else:  # rejected
            if (
                self.state is not BrokerActionState.REJECTED
                or self.reservation_id is not None
                or self.dispatch_id is not None
                or not (self.reason_code and self.reason_code.strip())
                or self.result_record_id is not None
            ):
                raise ValueError("rejected dispatch carries a reason and no reservation/dispatch")
        return self


def derive_dispatch_id(projection: H3ReadonlyProjection) -> str:
    """Derive one deterministic dispatch identity from exact reserved/projection bytes."""

    identity_document = {
        "schema_version": DISPATCH_IDENTITY_SCHEMA_VERSION,
        "reservation_id": projection.reservation_id,
        "executable_action_sha256": projection.executable_action_sha256,
        "single_use_nonce": projection.single_use_nonce,
        "action_type": projection.action_type,
        "adapter_id": projection.adapter_id,
        "adapter_version": projection.adapter_version,
        "projection_sha256": projection.projection_sha256,
    }
    return f"BROKER-DIS-{broker_sha256(identity_document)[:32]}"


class BrokerReadonlyDispatchService:
    """Turns one unchanged BROKER-2 reservation into one real read-only dispatch."""

    def __init__(
        self,
        *,
        reservation_service: BrokerReservationService,
        store: BrokerAuthorityStore,
        action_registry: ActionRegistry,
        result_store: H3ReadonlyResultStore,
        repo_root: Path,
    ) -> None:
        self._reservation_service = reservation_service
        self._store = store
        self._action_registry = action_registry
        self._result_store = result_store
        self._repo_root = Path(repo_root)

    def dispatch_readonly(
        self,
        *,
        action_input: Mapping[str, Any] | BaseModel,
        signed_claim_input: Mapping[str, Any] | BaseModel,
        evaluated_at: datetime,
    ) -> BrokerReadonlyDispatchResult:
        reservation = self._reservation_service.reserve(
            action_input=action_input,
            signed_claim_input=signed_claim_input,
            evaluated_at=evaluated_at,
        )
        if reservation.outcome != "reserved" or reservation.reservation_id is None:
            return self._rejected_result(reservation)

        action, claim, projection, dispatch_id = self._project(
            action_input, signed_claim_input, reservation
        )

        requested_at = self._store.database_time()
        request = self._store.request_dispatch(
            executable_action_id=action.executable_action_id,
            reservation_id=reservation.reservation_id,
            dispatch_id=dispatch_id,
            audit=self._dispatch_audit(
                event_type=BrokerAuditEventType.DISPATCH_REQUESTED,
                action=action,
                claim=claim,
                reservation_id=reservation.reservation_id,
                dispatch_id=dispatch_id,
                projection=projection,
                occurred_at=requested_at,
            ),
        )
        if request.status == "terminal":
            return self._terminal_result(request.state, dispatch_id, idempotent_existing=True)
        if request.status == "already_dispatched":
            raise StrandedReadonlyDispatchError(
                "a prior dispatch attempt is stranded; explicit reconcile is required"
            )

        # Exactly one read-only adapter invocation, only after the durable commit.
        record = readonly_repo_evidence(
            projection, dispatch_id=dispatch_id, repo_root=self._repo_root
        )
        # The single inert write in the loop: persist the read-only result record.
        receipt = self._result_store.write_result(record)
        finalized_at = self._store.database_time()
        result_evidence = {
            "result_record_id": record.result_record_id,
            "result_record_sha256": receipt.result_record_sha256,
            "retained_relative_path": receipt.retained_relative_path,
            "read_only": True,
            "mutation_side_effect": False,
        }
        if record.outcome == "completed":
            finalize = self._store.finalize_dispatch(
                executable_action_id=action.executable_action_id,
                dispatch_id=dispatch_id,
                outcome="completed",
                reason_code=None,
                audit=self._dispatch_audit(
                    event_type=BrokerAuditEventType.DISPATCH_COMPLETED,
                    action=action,
                    claim=claim,
                    reservation_id=reservation.reservation_id,
                    dispatch_id=dispatch_id,
                    projection=projection,
                    occurred_at=finalized_at,
                    result_evidence=result_evidence,
                ),
            )
        else:
            finalize = self._store.finalize_dispatch(
                executable_action_id=action.executable_action_id,
                dispatch_id=dispatch_id,
                outcome="failed",
                reason_code=record.reason_code,
                audit=self._dispatch_audit(
                    event_type=BrokerAuditEventType.DISPATCH_FAILED,
                    action=action,
                    claim=claim,
                    reservation_id=reservation.reservation_id,
                    dispatch_id=dispatch_id,
                    projection=projection,
                    occurred_at=finalized_at,
                    reason_code=record.reason_code,
                    result_evidence=result_evidence,
                ),
            )
        return self._terminal_result(
            finalize.state,
            dispatch_id,
            idempotent_existing=False,
            result_record_id=record.result_record_id,
            result_record_sha256=receipt.result_record_sha256,
            retained_relative_path=receipt.retained_relative_path,
        )

    def reconcile_stranded_dispatch(
        self,
        *,
        action_input: Mapping[str, Any] | BaseModel,
        signed_claim_input: Mapping[str, Any] | BaseModel,
        evaluated_at: datetime,
    ) -> BrokerReadonlyDispatchResult:
        """Explicitly classify a durably stranded `dispatched` action as reconcile_required.

        This never invokes the read-only adapter, never writes a result record, never
        retries dispatch, and never unburns or reissues the nonce.
        """

        reservation = self._reservation_service.reserve(
            action_input=action_input,
            signed_claim_input=signed_claim_input,
            evaluated_at=evaluated_at,
        )
        if reservation.outcome != "reserved" or reservation.reservation_id is None:
            return self._rejected_result(reservation)

        action, claim, projection, dispatch_id = self._project(
            action_input, signed_claim_input, reservation
        )
        occurred_at = self._store.database_time()
        result = self._store.classify_reconcile_required(
            executable_action_id=action.executable_action_id,
            dispatch_id=dispatch_id,
            reason_code=RECONCILE_REASON,
            audit=self._dispatch_audit(
                event_type=BrokerAuditEventType.RECONCILE_REQUIRED,
                action=action,
                claim=claim,
                reservation_id=reservation.reservation_id,
                dispatch_id=dispatch_id,
                projection=projection,
                occurred_at=occurred_at,
                reason_code=RECONCILE_REASON,
            ),
        )
        return self._terminal_result(
            result.state, dispatch_id, idempotent_existing=result.status == "already_final"
        )

    def _project(
        self,
        action_input: Mapping[str, Any] | BaseModel,
        signed_claim_input: Mapping[str, Any] | BaseModel,
        reservation: BrokerReservationResult,
    ) -> tuple[H3ReadonlyExecutableAction, SignedApprovalClaim, H3ReadonlyProjection, str]:
        action = self._materialize_action(action_input)
        claim = self._materialize_claim(signed_claim_input)
        assert reservation.reservation_id is not None
        projection = build_h3_readonly_projection(
            action=action,
            action_registry=self._action_registry,
            approval_id=reservation.approval_id,
            reservation_id=reservation.reservation_id,
            single_use_nonce=claim.payload.single_use_nonce,
        )
        return action, claim, projection, derive_dispatch_id(projection)

    def _materialize_action(
        self, action_input: Mapping[str, Any] | BaseModel
    ) -> H3ReadonlyExecutableAction:
        raw = (
            action_input.model_dump(mode="python")
            if isinstance(action_input, BaseModel)
            else dict(action_input)
        )
        entry = self._action_registry.get(READONLY_ACTION_TYPE)
        if entry is None:
            raise BrokerReadonlyDispatchError("dispatch registry is missing the H3-1 entry")
        action = entry.action_model.model_validate(raw)
        if not isinstance(action, H3ReadonlyExecutableAction):
            raise BrokerReadonlyDispatchError(
                "materialized action is not the H3-1 read-only action"
            )
        return action

    @staticmethod
    def _materialize_claim(
        signed_claim_input: Mapping[str, Any] | BaseModel,
    ) -> SignedApprovalClaim:
        raw = (
            signed_claim_input.model_dump(mode="python")
            if isinstance(signed_claim_input, BaseModel)
            else dict(signed_claim_input)
        )
        return SignedApprovalClaim.model_validate(raw)

    @staticmethod
    def _dispatch_audit(
        *,
        event_type: BrokerAuditEventType,
        action: H3ReadonlyExecutableAction,
        claim: SignedApprovalClaim,
        reservation_id: str,
        dispatch_id: str,
        projection: H3ReadonlyProjection,
        occurred_at: datetime,
        reason_code: str | None = None,
        result_evidence: dict[str, Any] | None = None,
    ) -> BrokerAuditRecord:
        bindings = {
            "approval_id": claim.payload.approval_id,
            "executable_action_id": action.executable_action_id,
            "executable_action_sha256": projection.executable_action_sha256,
            "prepared_record_id": action.prepared_record_id,
            "prepared_payload_sha256": action.prepared_payload_sha256,
            "source_proposal_id": action.source_proposal_id,
            "source_proposal_content_sha256": action.source_proposal_content_sha256,
            "repo_sha": action.repo_sha,
            "action_registry_version": action.action_registry_version,
            "adapter_id": action.adapter_id,
            "adapter_version": action.adapter_version,
            "key_registry_version": claim.payload.key_registry_version,
            "single_use_nonce": claim.payload.single_use_nonce,
            "reservation_id": reservation_id,
            "dispatch_id": dispatch_id,
        }
        evidence = {
            "projection_sha256": projection.projection_sha256,
            "projection_schema_version": projection.projection_schema_version,
            "read_only": True,
        }
        if result_evidence is not None:
            evidence.update(result_evidence)
        return build_audit_record(
            event_type=event_type,
            occurred_at=occurred_at,
            bindings=bindings,
            reason_code=reason_code,
            evidence=evidence,
        )

    def _terminal_result(
        self,
        state: Any,
        dispatch_id: str,
        *,
        idempotent_existing: bool,
        result_record_id: str | None = None,
        result_record_sha256: str | None = None,
        retained_relative_path: str | None = None,
    ) -> BrokerReadonlyDispatchResult:
        outcome = _TERMINAL_OUTCOMES[state.state]
        reason = state.last_reason_code if outcome in ("failed", "reconcile_required") else None
        return BrokerReadonlyDispatchResult(
            outcome=outcome,
            executable_action_id=state.executable_action_id,
            executable_action_sha256=state.executable_action_sha256,
            approval_id=state.approval_id,
            reservation_id=state.reservation_id,
            dispatch_id=state.dispatch_id or dispatch_id,
            state=state.state,
            idempotent_existing=idempotent_existing,
            reason_code=reason,
            result_record_id=result_record_id,
            result_record_sha256=result_record_sha256,
            retained_relative_path=retained_relative_path,
            mutation_side_effect=False,
            protected_surface_touched=False,
        )

    @staticmethod
    def _rejected_result(reservation: BrokerReservationResult) -> BrokerReadonlyDispatchResult:
        return BrokerReadonlyDispatchResult(
            outcome="rejected",
            executable_action_id=reservation.executable_action_id,
            executable_action_sha256=reservation.executable_action_sha256,
            approval_id=reservation.approval_id,
            reservation_id=None,
            dispatch_id=None,
            state=BrokerActionState.REJECTED,
            idempotent_existing=reservation.idempotent_existing,
            reason_code=reservation.rejection_reason or "rejected",
            result_record_id=None,
            result_record_sha256=None,
            retained_relative_path=None,
            mutation_side_effect=False,
            protected_surface_touched=False,
        )
