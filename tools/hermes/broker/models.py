"""Strict project-owned models for the BROKER-1 verification boundary."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from typing import Annotated, Generic, Literal, TypeVar

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from tools.hermes.proposals.models import AuthorityClass

Sha256 = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
RepoSha = Annotated[str, Field(pattern=r"^[0-9a-f]{40}$")]
Identity = Annotated[str, Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")]
ActionType = Annotated[str, Field(pattern=r"^[a-z][a-z0-9._-]{2,127}$")]
Version = Annotated[str, Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")]
Nonce = Annotated[str, Field(pattern=r"^[0-9a-f]{32,128}$")]

APPROVAL_DOMAIN_SEPARATOR = "hermes-broker-approval-v1"
MAX_APPROVAL_LIFETIME_SECONDS = 3600


class StrictBrokerModel(BaseModel):
    """Immutable, extra-forbidden base for every authority-bearing object."""

    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)


class ExactBound(StrictBrokerModel):
    amount: Annotated[int, Field(ge=0, le=10**12)]
    unit: Annotated[str, Field(min_length=1, max_length=80)]
    hard_limit: Literal[True]


class TimeoutBound(StrictBrokerModel):
    seconds: Annotated[int, Field(ge=1, le=86_400)]
    hard_limit: Literal[True]


TargetT = TypeVar("TargetT", bound=StrictBrokerModel)
ScopeT = TypeVar("ScopeT", bound=StrictBrokerModel)
ParametersT = TypeVar("ParametersT", bound=StrictBrokerModel)


class ExecutableAction(
    StrictBrokerModel,
    Generic[TargetT, ScopeT, ParametersT],
):
    """Human-authored action envelope; concrete types come only from a registry entry."""

    executable_action_schema_version: Literal["hermes_executable_action_v1"]
    executable_action_id: Identity
    action_type: ActionType
    prepared_record_id: Identity
    prepared_payload_sha256: Sha256
    source_proposal_id: Identity
    source_proposal_content_sha256: Sha256
    repo_sha: RepoSha
    action_registry_version: Version
    adapter_id: Identity
    adapter_version: Version
    authority_class: Literal[AuthorityClass.A1]
    human_authored: Literal[True]
    hermes_authored: Literal[False]
    target: TargetT
    scope: ScopeT
    parameters: ParametersT
    budget_bound: ExactBound
    count_or_quantity_bound: ExactBound | None
    timeout: TimeoutBound


def _validate_utc_second(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("approval timestamps must be timezone-aware UTC")
    if value.utcoffset().total_seconds() != 0:
        raise ValueError("approval timestamps must use UTC")
    if value.microsecond != 0:
        raise ValueError("approval timestamps must have whole-second precision")
    return value.astimezone(UTC)


class ApprovalClaimPayload(StrictBrokerModel):
    schema_version: Literal["hermes_broker_approval_claim_v1"]
    domain_separator: Literal[APPROVAL_DOMAIN_SEPARATOR]
    approval_id: Identity
    executable_action_id: Identity
    executable_action_sha256: Sha256
    prepared_record_id: Identity
    prepared_payload_sha256: Sha256
    source_proposal_id: Identity
    source_proposal_content_sha256: Sha256
    repo_sha: RepoSha
    authority_class: Literal[AuthorityClass.A1]
    action_type: ActionType
    action_registry_version: Version
    adapter_id: Identity
    adapter_version: Version
    scope_digest: Sha256
    budget_bound: ExactBound
    count_or_quantity_bound: ExactBound | None
    timeout: TimeoutBound
    issued_at: datetime
    not_before: datetime
    expiry: datetime
    single_use_nonce: Nonce
    signer_key_id: Identity
    key_registry_version: Version

    _issued_utc = field_validator("issued_at")(_validate_utc_second)
    _not_before_utc = field_validator("not_before")(_validate_utc_second)
    _expiry_utc = field_validator("expiry")(_validate_utc_second)

    @model_validator(mode="after")
    def validate_time_order(self) -> ApprovalClaimPayload:
        if self.issued_at > self.not_before:
            raise ValueError("issued_at must be at or before not_before")
        if self.not_before > self.expiry:
            raise ValueError("not_before must be at or before expiry")
        if self.expiry <= self.issued_at:
            raise ValueError("expiry must be after issued_at")
        return self


class SignedApprovalClaim(StrictBrokerModel):
    payload: ApprovalClaimPayload
    signature_algorithm: Literal["ed25519"]
    signature_encoding: Literal["lowercase_hex"]
    signature: Annotated[str, Field(pattern=r"^[0-9a-f]{128}$")]


class DecisionValue(str, Enum):
    ALLOW = "allow"
    REJECT = "reject"


class DecisionReason(str, Enum):
    VERIFIED = "verified"
    UNKNOWN_ACTION_TYPE = "unknown_action_type"
    A0_FORBIDDEN = "a0_forbidden"
    PREPARED_ARTIFACT_INVALID = "prepared_artifact_invalid"
    PREPARED_HASH_MISMATCH = "prepared_hash_mismatch"
    SOURCE_LINEAGE_MISMATCH = "source_lineage_mismatch"
    ACTION_HASH_MISMATCH = "action_hash_mismatch"
    CLAIM_BINDING_MISMATCH = "claim_binding_mismatch"
    UNKNOWN_SIGNER = "unknown_signer"
    REVOKED_SIGNER = "revoked_signer"
    INVALID_SIGNATURE = "invalid_signature"
    NOT_YET_VALID = "not_yet_valid"
    EXPIRED = "expired"
    APPROVAL_LIFETIME_EXCEEDED = "approval_lifetime_exceeded"
    REPO_STALE = "repo_stale"
    REGISTRY_STALE = "registry_stale"
    ADAPTER_STALE = "adapter_stale"
    KEY_REGISTRY_STALE = "key_registry_stale"
    MALFORMED_ACTION = "malformed_action"
    MALFORMED_CLAIM = "malformed_claim"
    UNSUPPORTED_ALGORITHM = "unsupported_algorithm"


class BrokerDecision(StrictBrokerModel):
    broker_decision_schema_version: Literal["hermes_broker_decision_v1"]
    decision_id: Identity
    decision: DecisionValue
    repo_sha: RepoSha
    executable_action_id: Identity
    executable_action_sha256: Sha256
    approval_id: Identity
    prepared_record_id: Identity
    prepared_payload_sha256: Sha256
    signer_key_id: Identity
    action_type: ActionType
    action_registry_version: Version
    adapter_id: Identity
    adapter_version: Version
    evaluated_at: datetime
    reason_code: DecisionReason
    not_dispatch_authority: Literal[True]
    reservation_created: Literal[False]
    dispatch_request_created: Literal[False]
    downstream_side_effect: Literal[False]

    _evaluated_utc = field_validator("evaluated_at")(_validate_utc_second)
