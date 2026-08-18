"""Deterministic BROKER-1 allow/reject verification with no downstream action."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ValidationError

from tools.hermes.proposals.models import A0_DOMAINS, AuthorityClass

from .crypto import (
    KeyRegistryStaleError,
    RevokedKeyError,
    SignatureVerificationError,
    TrustedKeyRegistry,
    UnknownKeyError,
    verify_signed_claim,
)
from .models import (
    MAX_APPROVAL_LIFETIME_SECONDS,
    BrokerDecision,
    DecisionReason,
    DecisionValue,
    ExecutableAction,
    SignedApprovalClaim,
)
from .registry import ActionRegistry, RegistryEntry
from .retention import BrokerArtifactStore, RetentionError
from .serialization import broker_sha256, scope_digest

ZERO_SHA256 = "0" * 64


def _mapping(value: Mapping[str, Any] | BaseModel) -> Mapping[str, Any] | None:
    if isinstance(value, BaseModel):
        return value.model_dump(mode="python")
    return value if isinstance(value, Mapping) else None


def _whole_second_utc(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("broker evaluation time must be timezone-aware UTC")
    if value.utcoffset().total_seconds() != 0 or value.microsecond != 0:
        raise ValueError("broker evaluation time must be whole-second UTC")
    return value.astimezone(UTC)


def _context_defaults(registry: ActionRegistry) -> dict[str, str]:
    return {
        "executable_action_id": "unknown",
        "executable_action_sha256": ZERO_SHA256,
        "approval_id": "unknown",
        "prepared_record_id": "unknown",
        "prepared_payload_sha256": ZERO_SHA256,
        "signer_key_id": "unknown",
        "action_type": "broker1.invalid",
        "action_registry_version": registry.version,
        "adapter_id": "unknown",
        "adapter_version": "unknown",
    }


def _decision(
    *,
    allowed: bool,
    reason: DecisionReason,
    repo_sha: str,
    evaluated_at: datetime,
    context: Mapping[str, str],
) -> BrokerDecision:
    identity_document = {
        "schema_version": "hermes_broker_decision_identity_v1",
        "decision": "allow" if allowed else "reject",
        "reason_code": reason.value,
        "repo_sha": repo_sha,
        "evaluated_at": evaluated_at.isoformat().replace("+00:00", "Z"),
        **context,
    }
    decision_id = f"BROKER-DEC-{broker_sha256(identity_document)[:32]}"
    return BrokerDecision(
        broker_decision_schema_version="hermes_broker_decision_v1",
        decision_id=decision_id,
        decision=DecisionValue.ALLOW if allowed else DecisionValue.REJECT,
        repo_sha=repo_sha,
        evaluated_at=evaluated_at,
        reason_code=reason,
        not_dispatch_authority=True,
        reservation_created=False,
        dispatch_request_created=False,
        downstream_side_effect=False,
        **context,
    )


def _reject(
    reason: DecisionReason,
    *,
    repo_sha: str,
    evaluated_at: datetime,
    context: Mapping[str, str],
) -> BrokerDecision:
    return _decision(
        allowed=False,
        reason=reason,
        repo_sha=repo_sha,
        evaluated_at=evaluated_at,
        context=context,
    )


def _validate_action(
    action_input: Mapping[str, Any] | BaseModel,
    registry: ActionRegistry,
) -> tuple[ExecutableAction | None, RegistryEntry | None, DecisionReason | None]:
    raw = _mapping(action_input)
    if raw is None:
        return None, None, DecisionReason.MALFORMED_ACTION
    if raw.get("authority_class") == AuthorityClass.A0 or raw.get("authority_class") == "A0":
        return None, None, DecisionReason.A0_FORBIDDEN
    action_type = raw.get("action_type")
    if not isinstance(action_type, str):
        return None, None, DecisionReason.MALFORMED_ACTION
    entry = registry.get(action_type)
    if entry is None:
        return None, None, DecisionReason.UNKNOWN_ACTION_TYPE
    try:
        action = entry.action_model.model_validate(raw)
    except ValidationError:
        return None, entry, DecisionReason.MALFORMED_ACTION
    if (
        action.action_type != entry.action_type
        or not isinstance(action.target, entry.target_model)
        or not isinstance(action.scope, entry.scope_model)
        or not isinstance(action.parameters, entry.parameters_model)
        or not isinstance(action.budget_bound, entry.budget_model)
        or (
            action.count_or_quantity_bound is not None
            and entry.count_or_quantity_model is not None
            and not isinstance(action.count_or_quantity_bound, entry.count_or_quantity_model)
        )
        or (action.count_or_quantity_bound is None) != (entry.count_or_quantity_model is None)
        or not isinstance(action.timeout, entry.timeout_model)
    ):
        return None, entry, DecisionReason.MALFORMED_ACTION
    if entry.affected_domains & A0_DOMAINS:
        return None, entry, DecisionReason.A0_FORBIDDEN
    return action, entry, None


def verify_approval(
    *,
    action_input: Mapping[str, Any] | BaseModel,
    signed_claim_input: Mapping[str, Any] | BaseModel,
    action_registry: ActionRegistry,
    key_registry: TrustedKeyRegistry,
    artifact_store: BrokerArtifactStore,
    current_repo_sha: str,
    evaluated_at: datetime,
) -> BrokerDecision:
    """Return a verification result and stop; never reserve, dispatch, or invoke anything."""

    evaluated_at = _whole_second_utc(evaluated_at)
    context = _context_defaults(action_registry)
    action, entry, action_error = _validate_action(action_input, action_registry)
    raw_action = _mapping(action_input)
    if raw_action is not None:
        raw_action_type = raw_action.get("action_type")
        if isinstance(raw_action_type, str) and action_registry.get(raw_action_type) is not None:
            context["action_type"] = raw_action_type
    if action_error is not None or action is None or entry is None:
        return _reject(
            action_error or DecisionReason.MALFORMED_ACTION,
            repo_sha=current_repo_sha,
            evaluated_at=evaluated_at,
            context=context,
        )

    action_sha256 = broker_sha256(action)
    context.update(
        executable_action_id=action.executable_action_id,
        executable_action_sha256=action_sha256,
        prepared_record_id=action.prepared_record_id,
        prepared_payload_sha256=action.prepared_payload_sha256,
        action_type=action.action_type,
        action_registry_version=action.action_registry_version,
        adapter_id=action.adapter_id,
        adapter_version=action.adapter_version,
    )
    if action.repo_sha != current_repo_sha:
        return _reject(
            DecisionReason.REPO_STALE,
            repo_sha=current_repo_sha,
            evaluated_at=evaluated_at,
            context=context,
        )
    if action.action_registry_version != action_registry.version:
        return _reject(
            DecisionReason.REGISTRY_STALE,
            repo_sha=current_repo_sha,
            evaluated_at=evaluated_at,
            context=context,
        )
    if action.adapter_id != entry.adapter_id or action.adapter_version != entry.adapter_version:
        return _reject(
            DecisionReason.ADAPTER_STALE,
            repo_sha=current_repo_sha,
            evaluated_at=evaluated_at,
            context=context,
        )

    raw_claim = _mapping(signed_claim_input)
    if raw_claim is None:
        return _reject(
            DecisionReason.MALFORMED_CLAIM,
            repo_sha=current_repo_sha,
            evaluated_at=evaluated_at,
            context=context,
        )
    if raw_claim.get("signature_algorithm") != "ed25519":
        return _reject(
            DecisionReason.UNSUPPORTED_ALGORITHM,
            repo_sha=current_repo_sha,
            evaluated_at=evaluated_at,
            context=context,
        )
    try:
        claim = SignedApprovalClaim.model_validate(raw_claim)
    except ValidationError:
        return _reject(
            DecisionReason.MALFORMED_CLAIM,
            repo_sha=current_repo_sha,
            evaluated_at=evaluated_at,
            context=context,
        )
    context.update(
        approval_id=claim.payload.approval_id,
        signer_key_id=claim.payload.signer_key_id,
    )

    if claim.payload.repo_sha != current_repo_sha:
        return _reject(
            DecisionReason.REPO_STALE,
            repo_sha=current_repo_sha,
            evaluated_at=evaluated_at,
            context=context,
        )
    if claim.payload.action_registry_version != action_registry.version:
        return _reject(
            DecisionReason.REGISTRY_STALE,
            repo_sha=current_repo_sha,
            evaluated_at=evaluated_at,
            context=context,
        )
    if (
        claim.payload.adapter_id != entry.adapter_id
        or claim.payload.adapter_version != entry.adapter_version
    ):
        return _reject(
            DecisionReason.ADAPTER_STALE,
            repo_sha=current_repo_sha,
            evaluated_at=evaluated_at,
            context=context,
        )
    if claim.payload.executable_action_sha256 != action_sha256:
        return _reject(
            DecisionReason.ACTION_HASH_MISMATCH,
            repo_sha=current_repo_sha,
            evaluated_at=evaluated_at,
            context=context,
        )
    exact_bindings = (
        (claim.payload.executable_action_id, action.executable_action_id),
        (claim.payload.prepared_record_id, action.prepared_record_id),
        (claim.payload.prepared_payload_sha256, action.prepared_payload_sha256),
        (claim.payload.source_proposal_id, action.source_proposal_id),
        (
            claim.payload.source_proposal_content_sha256,
            action.source_proposal_content_sha256,
        ),
        (claim.payload.authority_class, action.authority_class),
        (claim.payload.action_type, action.action_type),
        (claim.payload.scope_digest, scope_digest(action.scope)),
        (claim.payload.budget_bound, action.budget_bound),
        (claim.payload.count_or_quantity_bound, action.count_or_quantity_bound),
        (claim.payload.timeout, action.timeout),
    )
    if any(left != right for left, right in exact_bindings):
        return _reject(
            DecisionReason.CLAIM_BINDING_MISMATCH,
            repo_sha=current_repo_sha,
            evaluated_at=evaluated_at,
            context=context,
        )
    lifetime = (claim.payload.expiry - claim.payload.issued_at).total_seconds()
    if lifetime > MAX_APPROVAL_LIFETIME_SECONDS:
        return _reject(
            DecisionReason.APPROVAL_LIFETIME_EXCEEDED,
            repo_sha=current_repo_sha,
            evaluated_at=evaluated_at,
            context=context,
        )
    if evaluated_at < claim.payload.not_before:
        return _reject(
            DecisionReason.NOT_YET_VALID,
            repo_sha=current_repo_sha,
            evaluated_at=evaluated_at,
            context=context,
        )
    if evaluated_at >= claim.payload.expiry:
        return _reject(
            DecisionReason.EXPIRED,
            repo_sha=current_repo_sha,
            evaluated_at=evaluated_at,
            context=context,
        )
    try:
        verify_signed_claim(claim, key_registry)
    except UnknownKeyError:
        reason = DecisionReason.UNKNOWN_SIGNER
    except RevokedKeyError:
        reason = DecisionReason.REVOKED_SIGNER
    except KeyRegistryStaleError:
        reason = DecisionReason.KEY_REGISTRY_STALE
    except SignatureVerificationError:
        reason = DecisionReason.INVALID_SIGNATURE
    else:
        reason = None
    if reason is not None:
        return _reject(
            reason,
            repo_sha=current_repo_sha,
            evaluated_at=evaluated_at,
            context=context,
        )

    try:
        retained = artifact_store.verify_retained(action.prepared_record_id)
    except RetentionError as exc:
        reason = (
            DecisionReason.PREPARED_HASH_MISMATCH
            if "prepared_payload_sha256" in str(exc)
            else DecisionReason.PREPARED_ARTIFACT_INVALID
        )
        return _reject(
            reason,
            repo_sha=current_repo_sha,
            evaluated_at=evaluated_at,
            context=context,
        )
    if retained.payload.authority_class is AuthorityClass.A0:
        return _reject(
            DecisionReason.A0_FORBIDDEN,
            repo_sha=current_repo_sha,
            evaluated_at=evaluated_at,
            context=context,
        )
    if retained.prepared_payload_sha256 != action.prepared_payload_sha256:
        return _reject(
            DecisionReason.PREPARED_HASH_MISMATCH,
            repo_sha=current_repo_sha,
            evaluated_at=evaluated_at,
            context=context,
        )
    lineage = (
        retained.payload.source_proposal_id == action.source_proposal_id,
        retained.payload.source_proposal_content_sha256 == action.source_proposal_content_sha256,
        retained.payload.repo_sha == action.repo_sha,
        retained.payload.source_proposal_repo_sha == action.repo_sha,
        retained.payload.authority_class is AuthorityClass.A1,
        retained.payload.source_authority_class is AuthorityClass.A1,
    )
    if not all(lineage):
        return _reject(
            DecisionReason.SOURCE_LINEAGE_MISMATCH,
            repo_sha=current_repo_sha,
            evaluated_at=evaluated_at,
            context=context,
        )

    return _decision(
        allowed=True,
        reason=DecisionReason.VERIFIED,
        repo_sha=current_repo_sha,
        evaluated_at=evaluated_at,
        context=context,
    )
