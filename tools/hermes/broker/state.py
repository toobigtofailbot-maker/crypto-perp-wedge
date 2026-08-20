"""Closed BROKER-2 state, audit, and result models with no side effects."""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from enum import Enum
from typing import Any, Literal

from pydantic import model_validator

from .models import Identity, Sha256, StrictBrokerModel
from .serialization import broker_canonical_json_bytes


class BrokerActionState(str, Enum):
    SUBMITTED = "submitted"
    VERIFIED = "verified"
    RESERVED = "reserved"
    REJECTED = "rejected"
    DISPATCHED = "dispatched"
    COMPLETED = "completed"
    FAILED = "failed"
    RECONCILE_REQUIRED = "reconcile_required"


class BrokerAuditEventType(str, Enum):
    CLAIM_SUBMITTED = "claim_submitted"
    CLAIM_VERIFIED = "claim_verified"
    CLAIM_REJECTED = "claim_rejected"
    NONCE_RESERVED = "nonce_reserved"
    DISPATCH_REQUESTED = "dispatch_requested"
    DISPATCH_COMPLETED = "dispatch_completed"
    DISPATCH_FAILED = "dispatch_failed"
    RECONCILE_REQUIRED = "reconcile_required"


class BrokerReservationResult(StrictBrokerModel):
    outcome: Literal["reserved", "rejected"]
    executable_action_id: Identity
    executable_action_sha256: Sha256
    approval_id: Identity
    reservation_id: Identity | None
    state: BrokerActionState
    idempotent_existing: bool
    rejection_reason: str | None
    downstream_side_effect: Literal[False]

    @model_validator(mode="after")
    def validate_outcome(self) -> BrokerReservationResult:
        if self.outcome == "reserved":
            if self.state is not BrokerActionState.RESERVED or self.reservation_id is None:
                raise ValueError("reserved result requires durable reserved state")
            if self.rejection_reason is not None:
                raise ValueError("reserved result cannot carry a rejection reason")
        elif (
            self.state is not BrokerActionState.REJECTED
            or self.reservation_id is not None
            or not self.rejection_reason
        ):
            raise ValueError("rejected result requires a reason and no reservation")
        return self


class BrokerAuditRecord(StrictBrokerModel):
    event_id: Identity
    event_type: BrokerAuditEventType
    approval_id: str | None
    executable_action_id: str | None
    executable_action_sha256: str | None
    prepared_record_id: str | None
    prepared_payload_sha256: str | None
    source_proposal_id: str | None
    source_proposal_content_sha256: str | None
    repo_sha: str | None
    action_registry_version: str | None
    adapter_id: str | None
    adapter_version: str | None
    key_registry_version: str | None
    single_use_nonce: str | None
    reservation_id: str | None
    dispatch_id: str | None
    occurred_at: datetime
    actor: Literal["broker"]
    reason_code: str | None
    event_payload_canonical: bytes
    event_payload_sha256: Sha256


def _utc_text(value: datetime) -> str:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("audit timestamp must be timezone-aware")
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


def build_audit_record(
    *,
    event_type: BrokerAuditEventType,
    occurred_at: datetime,
    bindings: dict[str, Any],
    reason_code: str | None = None,
    evidence: dict[str, Any] | None = None,
) -> BrokerAuditRecord:
    """Create one deterministic canonical authority-audit event."""

    payload = {
        "schema_version": "hermes_broker_authority_audit_v1",
        "event_type": event_type.value,
        "occurred_at": _utc_text(occurred_at),
        "actor": "broker",
        **{key: value for key, value in bindings.items() if value is not None},
    }
    if reason_code is not None:
        payload["reason_code"] = reason_code
    if evidence:
        payload["evidence"] = evidence
    canonical = broker_canonical_json_bytes(payload)
    digest = hashlib.sha256(canonical).hexdigest()
    return BrokerAuditRecord(
        event_id=f"BROKER-AUD-{digest[:32]}",
        event_type=event_type,
        occurred_at=occurred_at,
        actor="broker",
        reason_code=reason_code,
        event_payload_canonical=canonical,
        event_payload_sha256=digest,
        **{
            field: bindings.get(field)
            for field in (
                "approval_id",
                "executable_action_id",
                "executable_action_sha256",
                "prepared_record_id",
                "prepared_payload_sha256",
                "source_proposal_id",
                "source_proposal_content_sha256",
                "repo_sha",
                "action_registry_version",
                "adapter_id",
                "adapter_version",
                "key_registry_version",
                "single_use_nonce",
                "reservation_id",
                "dispatch_id",
            )
        },
    )
