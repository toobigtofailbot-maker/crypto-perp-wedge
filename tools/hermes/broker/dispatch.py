"""BROKER-3 orchestration: verify, reserve, project, dry-run dispatch, audit.

The public entrypoint is bound to exactly one fixed no-op action. It accepts no
adapter callable, adapter registry, command, endpoint, file path, network client,
dispatcher callback, or retry callback. It composes only the unchanged BROKER-2
reservation service, the durable store, the fixed proof registry, the fixed
projection, and the fixed no-op adapter.
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, model_validator

from .dry_run_adapter import dry_run_noop
from .models import Identity, Sha256, SignedApprovalClaim, StrictBrokerModel
from .projection import (
    DRY_RUN_PROOF_ACTION_TYPE,
    Broker3ProofExecutableAction,
    DryRunProjection,
    build_dry_run_projection,
)
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

DISPATCH_IDENTITY_SCHEMA_VERSION = "hermes_broker_dry_run_dispatch_identity_v1"
RECONCILE_REASON = "dry_run_dispatch_completion_unknown"

_TERMINAL_OUTCOMES: dict[BrokerActionState, str] = {
    BrokerActionState.COMPLETED: "completed",
    BrokerActionState.FAILED: "failed",
    BrokerActionState.RECONCILE_REQUIRED: "reconcile_required",
}


class BrokerDispatchError(RuntimeError):
    """A durable dispatch operation error that never fabricates a terminal state."""


class StrandedDispatchError(BrokerDispatchError):
    """A prior dispatch attempt is durably `dispatched` and needs explicit reconcile."""


class BrokerDispatchResult(StrictBrokerModel):
    outcome: Literal["completed", "failed", "reconcile_required", "rejected"]
    executable_action_id: Identity
    executable_action_sha256: Sha256
    approval_id: Identity
    reservation_id: Identity | None
    dispatch_id: Identity | None
    state: BrokerActionState
    idempotent_existing: bool
    reason_code: str | None
    downstream_side_effect: Literal[False]

    @model_validator(mode="after")
    def validate_outcome(self) -> BrokerDispatchResult:
        if self.outcome == "completed":
            if (
                self.state is not BrokerActionState.COMPLETED
                or self.reservation_id is None
                or self.dispatch_id is None
                or self.reason_code is not None
            ):
                raise ValueError("completed dispatch requires reservation, dispatch, no reason")
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
            ):
                raise ValueError("rejected dispatch carries a reason and no reservation/dispatch")
        return self


def derive_dispatch_id(projection: DryRunProjection) -> str:
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


class BrokerDryRunDispatchService:
    """Turns one unchanged BROKER-2 reservation into one inert dry-run dispatch proof."""

    def __init__(
        self,
        *,
        reservation_service: BrokerReservationService,
        store: BrokerAuthorityStore,
        action_registry: ActionRegistry,
    ) -> None:
        self._reservation_service = reservation_service
        self._store = store
        self._action_registry = action_registry

    def dispatch_dry_run(
        self,
        *,
        action_input: Mapping[str, Any] | BaseModel,
        signed_claim_input: Mapping[str, Any] | BaseModel,
        evaluated_at: datetime,
    ) -> BrokerDispatchResult:
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
            raise StrandedDispatchError(
                "a prior dispatch attempt is stranded; explicit reconcile is required"
            )

        # Exactly one fixed no-op adapter invocation, only after the durable commit.
        adapter_result = dry_run_noop(projection)
        finalized_at = self._store.database_time()
        if adapter_result.outcome == "completed":
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
                ),
            )
        else:
            finalize = self._store.finalize_dispatch(
                executable_action_id=action.executable_action_id,
                dispatch_id=dispatch_id,
                outcome="failed",
                reason_code=adapter_result.reason_code,
                audit=self._dispatch_audit(
                    event_type=BrokerAuditEventType.DISPATCH_FAILED,
                    action=action,
                    claim=claim,
                    reservation_id=reservation.reservation_id,
                    dispatch_id=dispatch_id,
                    projection=projection,
                    occurred_at=finalized_at,
                    reason_code=adapter_result.reason_code,
                ),
            )
        return self._terminal_result(finalize.state, dispatch_id, idempotent_existing=False)

    def reconcile_stranded_dispatch(
        self,
        *,
        action_input: Mapping[str, Any] | BaseModel,
        signed_claim_input: Mapping[str, Any] | BaseModel,
        evaluated_at: datetime,
    ) -> BrokerDispatchResult:
        """Explicitly classify a durably stranded `dispatched` action as reconcile_required.

        This never invokes the no-op adapter, never retries dispatch, and never
        unburns or reissues the nonce.
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
    ) -> tuple[Broker3ProofExecutableAction, SignedApprovalClaim, DryRunProjection, str]:
        action = self._materialize_action(action_input)
        claim = self._materialize_claim(signed_claim_input)
        assert reservation.reservation_id is not None
        projection = build_dry_run_projection(
            action=action,
            action_registry=self._action_registry,
            approval_id=reservation.approval_id,
            reservation_id=reservation.reservation_id,
            single_use_nonce=claim.payload.single_use_nonce,
        )
        return action, claim, projection, derive_dispatch_id(projection)

    def _materialize_action(
        self, action_input: Mapping[str, Any] | BaseModel
    ) -> Broker3ProofExecutableAction:
        raw = (
            action_input.model_dump(mode="python")
            if isinstance(action_input, BaseModel)
            else dict(action_input)
        )
        entry = self._action_registry.get(DRY_RUN_PROOF_ACTION_TYPE)
        if entry is None:
            raise BrokerDispatchError("dispatch registry is missing the broker3 proof entry")
        action = entry.action_model.model_validate(raw)
        if not isinstance(action, Broker3ProofExecutableAction):
            raise BrokerDispatchError("materialized action is not the broker3 proof action")
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
        action: Broker3ProofExecutableAction,
        claim: SignedApprovalClaim,
        reservation_id: str,
        dispatch_id: str,
        projection: DryRunProjection,
        occurred_at: datetime,
        reason_code: str | None = None,
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
        return build_audit_record(
            event_type=event_type,
            occurred_at=occurred_at,
            bindings=bindings,
            reason_code=reason_code,
            evidence={
                "projection_sha256": projection.projection_sha256,
                "projection_schema_version": projection.projection_schema_version,
                "dry_run": True,
            },
        )

    def _terminal_result(
        self,
        state: Any,
        dispatch_id: str,
        *,
        idempotent_existing: bool,
    ) -> BrokerDispatchResult:
        outcome = _TERMINAL_OUTCOMES[state.state]
        reason = state.last_reason_code if outcome in ("failed", "reconcile_required") else None
        return BrokerDispatchResult(
            outcome=outcome,
            executable_action_id=state.executable_action_id,
            executable_action_sha256=state.executable_action_sha256,
            approval_id=state.approval_id,
            reservation_id=state.reservation_id,
            dispatch_id=state.dispatch_id or dispatch_id,
            state=state.state,
            idempotent_existing=idempotent_existing,
            reason_code=reason,
            downstream_side_effect=False,
        )

    @staticmethod
    def _rejected_result(reservation: BrokerReservationResult) -> BrokerDispatchResult:
        return BrokerDispatchResult(
            outcome="rejected",
            executable_action_id=reservation.executable_action_id,
            executable_action_sha256=reservation.executable_action_sha256,
            approval_id=reservation.approval_id,
            reservation_id=None,
            dispatch_id=None,
            state=BrokerActionState.REJECTED,
            idempotent_existing=reservation.idempotent_existing,
            reason_code=reservation.rejection_reason or "rejected",
            downstream_side_effect=False,
        )
