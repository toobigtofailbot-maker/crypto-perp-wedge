"""Ed25519 verification and public-key trust for BROKER-1.

No private-key or signing API exists in this broker verification module.
"""

from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from typing import Annotated, Literal

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from pydantic import Field, field_validator, model_validator

from .models import (
    APPROVAL_DOMAIN_SEPARATOR,
    Identity,
    SignedApprovalClaim,
    StrictBrokerModel,
    Version,
)
from .serialization import broker_canonical_json_bytes

SIGNED_MESSAGE_PREFIX = b"hermes-broker-approval-v1\x00"


class KeyState(str, Enum):
    ACTIVE = "active"
    REVOKED = "revoked"


def _utc_second(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("key-registry timestamps must be timezone-aware UTC")
    if value.utcoffset().total_seconds() != 0 or value.microsecond != 0:
        raise ValueError("key-registry timestamps must be whole-second UTC")
    return value.astimezone(UTC)


class TrustedPublicKey(StrictBrokerModel):
    key_id: Identity
    algorithm: Literal["ed25519"]
    public_key_encoding: Literal["lowercase_hex"]
    public_key: Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
    state: KeyState
    added_at: datetime
    revoked_at: datetime | None
    revocation_reason: Annotated[str, Field(min_length=1, max_length=500)] | None
    fixture_only: bool

    _added_utc = field_validator("added_at")(_utc_second)
    _revoked_utc = field_validator("revoked_at")(_utc_second)

    @model_validator(mode="after")
    def validate_state(self) -> TrustedPublicKey:
        if self.state is KeyState.ACTIVE:
            if self.revoked_at is not None or self.revocation_reason is not None:
                raise ValueError("active public key cannot carry revocation fields")
        else:
            if self.revoked_at is None or self.revocation_reason is None:
                raise ValueError("revoked public key requires timestamp and reason")
            if self.revoked_at < self.added_at:
                raise ValueError("revocation cannot predate key addition")
        return self


class TrustedKeyRegistry(StrictBrokerModel):
    key_registry_schema_version: Literal["hermes_broker_trusted_keys_v1"]
    key_registry_version: Version
    keys: tuple[TrustedPublicKey, ...]

    @model_validator(mode="after")
    def validate_unique_ids(self) -> TrustedKeyRegistry:
        identities = tuple(key.key_id for key in self.keys)
        if len(identities) != len(set(identities)):
            raise ValueError("duplicate key_id is forbidden")
        return self

    def find(self, key_id: str) -> TrustedPublicKey | None:
        return next((key for key in self.keys if key.key_id == key_id), None)


class CryptoVerificationError(ValueError):
    pass


class UnknownKeyError(CryptoVerificationError):
    pass


class RevokedKeyError(CryptoVerificationError):
    pass


class KeyRegistryStaleError(CryptoVerificationError):
    pass


class SignatureVerificationError(CryptoVerificationError):
    pass


def approval_signed_bytes(claim: SignedApprovalClaim | object) -> bytes:
    """Return the one locked Ed25519 message for an unsigned claim payload."""

    payload = claim.payload if isinstance(claim, SignedApprovalClaim) else claim
    if getattr(payload, "domain_separator", None) != APPROVAL_DOMAIN_SEPARATOR:
        raise SignatureVerificationError("approval domain separator is invalid")
    return SIGNED_MESSAGE_PREFIX + broker_canonical_json_bytes(payload)


def verify_signed_claim(
    claim: SignedApprovalClaim,
    key_registry: TrustedKeyRegistry,
) -> None:
    """Verify one claim against exactly one active allowlisted Ed25519 public key."""

    if claim.payload.key_registry_version != key_registry.key_registry_version:
        raise KeyRegistryStaleError("approval key registry version is stale")
    key = key_registry.find(claim.payload.signer_key_id)
    if key is None:
        raise UnknownKeyError("approval signer key ID is unknown")
    if key.state is KeyState.REVOKED:
        raise RevokedKeyError("approval signer key ID is revoked")
    try:
        public_bytes = bytes.fromhex(key.public_key)
        signature = bytes.fromhex(claim.signature)
        if len(public_bytes) != 32 or len(signature) != 64:
            raise ValueError("invalid Ed25519 byte length")
        public_key = Ed25519PublicKey.from_public_bytes(public_bytes)
        public_key.verify(signature, approval_signed_bytes(claim))
    except (InvalidSignature, ValueError) as exc:
        raise SignatureVerificationError("Ed25519 signature verification failed") from exc
