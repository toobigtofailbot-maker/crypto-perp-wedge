"""What-you-see-is-what-you-sign (WYSIWYS) approval signing for H3-1.

This module makes ``human_authored=true`` a real cryptographic binding rather than an
assertion. It displays the exact canonical executable-action bytes and their
SHA-256, and the exact Ed25519 signing-message bytes and their SHA-256, then signs
over *exactly those bytes*. The bytes Karl sees, hashes, and signs are provably the
bytes the broker verifies and the adapter executes:

    surface.action_sha256           == broker_sha256(action)
                                    == claim.payload.executable_action_sha256
    surface.signing_message_bytes   == approval_signed_bytes(signed_claim)
    sha256(surface.signing_message) == surface.signing_message_sha256

Key custody for this first read-only action is a software Ed25519 key generated
outside the repository. The private key is supplied to :func:`sign_wysiwys_surface`
at signing time by the operator and is never stored, logged, or returned here; the
broker holds only the public key (see :func:`production_trusted_public_key`).
Hardware custody (HSM/Yubikey) is required before any future *mutating* action.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

from tools.hermes.proposals.models import AuthorityClass

from .crypto import (
    KeyState,
    TrustedKeyRegistry,
    TrustedPublicKey,
    approval_signed_bytes,
    verify_signed_claim,
)
from .models import (
    ApprovalClaimPayload,
    ExecutableAction,
    SignedApprovalClaim,
)
from .serialization import broker_canonical_json_bytes, broker_sha256, scope_digest

WYSIWYS_SURFACE_SCHEMA_VERSION = "hermes_broker_wysiwys_signing_surface_v1"


class WysiwysBindingError(ValueError):
    """Raised when the claim to be signed does not exactly bind the action seen."""


@dataclass(frozen=True)
class WysiwysSigningSurface:
    """The exact bytes and hashes surfaced for signing; nothing else is signed."""

    action: ExecutableAction
    claim_payload: ApprovalClaimPayload
    action_canonical_bytes: bytes
    action_sha256: str
    claim_payload_canonical_bytes: bytes
    signing_message_bytes: bytes
    signing_message_sha256: str

    def render(self) -> str:
        """Return the human-facing what-you-sign display text."""

        return (
            f"schema: {WYSIWYS_SURFACE_SCHEMA_VERSION}\n"
            f"executable_action_id: {self.action.executable_action_id}\n"
            f"action_type: {self.action.action_type}\n"
            f"repo_sha: {self.action.repo_sha}\n"
            f"approval_id: {self.claim_payload.approval_id}\n"
            f"signer_key_id: {self.claim_payload.signer_key_id}\n"
            f"key_registry_version: {self.claim_payload.key_registry_version}\n"
            "--- executable action (canonical bytes; sign nothing else) ---\n"
            f"{self.action_canonical_bytes.decode('utf-8')}"
            f"executable_action_sha256: {self.action_sha256}\n"
            "--- ed25519 signing message sha256 (over the claim payload) ---\n"
            f"signing_message_sha256: {self.signing_message_sha256}\n"
        )

    def to_manifest(self) -> dict[str, str]:
        return {
            "schema_version": WYSIWYS_SURFACE_SCHEMA_VERSION,
            "executable_action_id": self.action.executable_action_id,
            "action_type": self.action.action_type,
            "repo_sha": self.action.repo_sha,
            "approval_id": self.claim_payload.approval_id,
            "signer_key_id": self.claim_payload.signer_key_id,
            "key_registry_version": self.claim_payload.key_registry_version,
            "executable_action_sha256": self.action_sha256,
            "signing_message_sha256": self.signing_message_sha256,
        }


def build_wysiwys_surface(
    *,
    action: ExecutableAction,
    claim_payload: ApprovalClaimPayload,
) -> WysiwysSigningSurface:
    """Build the exact signing surface, failing closed unless the claim binds the action.

    Every field the broker later checks for exact equality is verified here *before*
    the surface is shown, so what is displayed is provably what will verify.
    """

    action_canonical_bytes = broker_canonical_json_bytes(action)
    action_sha256 = hashlib.sha256(action_canonical_bytes).hexdigest()
    if action_sha256 != broker_sha256(action):  # pragma: no cover - identity invariant
        raise WysiwysBindingError("canonical action hash is not self-consistent")

    exact_bindings = (
        (claim_payload.executable_action_sha256, action_sha256),
        (claim_payload.executable_action_id, action.executable_action_id),
        (claim_payload.prepared_record_id, action.prepared_record_id),
        (claim_payload.prepared_payload_sha256, action.prepared_payload_sha256),
        (claim_payload.source_proposal_id, action.source_proposal_id),
        (claim_payload.source_proposal_content_sha256, action.source_proposal_content_sha256),
        (claim_payload.repo_sha, action.repo_sha),
        (claim_payload.action_type, action.action_type),
        (claim_payload.action_registry_version, action.action_registry_version),
        (claim_payload.adapter_id, action.adapter_id),
        (claim_payload.adapter_version, action.adapter_version),
        (claim_payload.scope_digest, scope_digest(action.scope)),
        (claim_payload.budget_bound, action.budget_bound),
        (claim_payload.count_or_quantity_bound, action.count_or_quantity_bound),
        (claim_payload.timeout, action.timeout),
    )
    if any(left != right for left, right in exact_bindings):
        raise WysiwysBindingError("claim payload does not exactly bind the action being signed")
    if claim_payload.authority_class is not AuthorityClass.A1:
        raise WysiwysBindingError("only A1 read-only actions may be signed via this surface")
    if action.authority_class is not AuthorityClass.A1 or action.human_authored is not True:
        raise WysiwysBindingError("action must be human-authored A1")

    unsigned = SignedApprovalClaim.model_construct(
        payload=claim_payload,
        signature_algorithm="ed25519",
        signature_encoding="lowercase_hex",
        signature="0" * 128,
    )
    signing_message_bytes = approval_signed_bytes(unsigned)
    claim_payload_canonical_bytes = broker_canonical_json_bytes(claim_payload)
    return WysiwysSigningSurface(
        action=action,
        claim_payload=claim_payload,
        action_canonical_bytes=action_canonical_bytes,
        action_sha256=action_sha256,
        claim_payload_canonical_bytes=claim_payload_canonical_bytes,
        signing_message_bytes=signing_message_bytes,
        signing_message_sha256=hashlib.sha256(signing_message_bytes).hexdigest(),
    )


def sign_wysiwys_surface(
    surface: WysiwysSigningSurface,
    private_key: Ed25519PrivateKey,
) -> SignedApprovalClaim:
    """Sign exactly the surfaced bytes and prove the signature binds them.

    The private key is used only here and is never persisted or returned.
    """

    signature = private_key.sign(surface.signing_message_bytes)
    signed = SignedApprovalClaim(
        payload=surface.claim_payload,
        signature_algorithm="ed25519",
        signature_encoding="lowercase_hex",
        signature=signature.hex(),
    )
    # Prove what was signed is exactly what was surfaced and what the broker verifies.
    if approval_signed_bytes(signed) != surface.signing_message_bytes:
        raise WysiwysBindingError("signed message diverged from the surfaced bytes")
    if hashlib.sha256(approval_signed_bytes(signed)).hexdigest() != surface.signing_message_sha256:
        raise WysiwysBindingError("signed message hash diverged from the surfaced hash")
    public_key = private_key.public_key()
    public_hex = public_key.public_bytes(
        serialization.Encoding.Raw,
        serialization.PublicFormat.Raw,
    ).hex()
    self_check = TrustedKeyRegistry(
        key_registry_schema_version="hermes_broker_trusted_keys_v1",
        key_registry_version=surface.claim_payload.key_registry_version,
        keys=(
            TrustedPublicKey(
                key_id=surface.claim_payload.signer_key_id,
                algorithm="ed25519",
                public_key_encoding="lowercase_hex",
                public_key=public_hex,
                state=KeyState.ACTIVE,
                added_at=surface.claim_payload.issued_at,
                revoked_at=None,
                revocation_reason=None,
                fixture_only=False,
            ),
        ),
    )
    verify_signed_claim(signed, self_check)
    return signed


def production_trusted_public_key(
    *,
    public_key: Ed25519PublicKey,
    key_id: str,
    key_registry_version: str,
    added_at: datetime,
) -> TrustedPublicKey:
    """Build the broker's public-key-only trust entry for a software production key.

    The broker stores only this public key. ``fixture_only`` is ``False`` because this
    is a real production key, but the private half never enters the repo, an image, a
    tracked file, the broker config, or Hermes.
    """

    public_hex = public_key.public_bytes(
        serialization.Encoding.Raw,
        serialization.PublicFormat.Raw,
    ).hex()
    return TrustedPublicKey(
        key_id=key_id,
        algorithm="ed25519",
        public_key_encoding="lowercase_hex",
        public_key=public_hex,
        state=KeyState.ACTIVE,
        added_at=added_at,
        revoked_at=None,
        revocation_reason=None,
        fixture_only=False,
    )
