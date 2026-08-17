from __future__ import annotations

from datetime import UTC, datetime

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from pydantic import ValidationError

from tools.hermes.broker.acceptance import (
    make_action,
    make_claim_payload,
    make_key_registry,
    make_prepared_payload,
    sign_claim_for_proof,
)
from tools.hermes.broker.crypto import (
    KeyState,
    RevokedKeyError,
    SignatureVerificationError,
    TrustedKeyRegistry,
    TrustedPublicKey,
    UnknownKeyError,
    approval_signed_bytes,
    verify_signed_claim,
)
from tools.hermes.broker.models import SignedApprovalClaim
from tools.hermes.broker.serialization import (
    BrokerCanonicalizationError,
    broker_canonical_json_bytes,
)
from tools.hermes.prepare.serialization import canonical_json_bytes as h25_canonical_json_bytes
from tools.hermes.proposals.models import AuthorityClass

NOW = datetime(2026, 8, 17, 12, 0, tzinfo=UTC)
REPO_SHA = "1" * 40
PREPARED_ID = "HERMES-PREP-20260817T120000Z-0123456789abcdef"


def _signed_fixture() -> tuple[
    Ed25519PrivateKey,
    SignedApprovalClaim,
    TrustedKeyRegistry,
]:
    private = Ed25519PrivateKey.from_private_bytes(bytes(range(32)))
    prepared = make_prepared_payload(
        authority_class=AuthorityClass.A1,
        repo_sha=REPO_SHA,
        prepared_record_id=PREPARED_ID,
    )
    action = make_action(
        payload=prepared,
        prepared_record_id=PREPARED_ID,
        action_id="broker1-crypto-vector",
    )
    payload = make_claim_payload(
        action=action,
        signer_key_id="broker1-test-key",
        issued_at=NOW,
    )
    signed = sign_claim_for_proof(
        action=action,
        prepared_payload=prepared,
        claim_payload=payload,
        private_key=private,
    )
    registry = make_key_registry(
        private_key=private,
        key_id="broker1-test-key",
        added_at=NOW,
    )
    return private, signed, registry


def test_known_good_ed25519_signature_and_exact_signed_bytes_verify() -> None:
    _private, signed, registry = _signed_fixture()
    message = approval_signed_bytes(signed)
    assert message.startswith(b"hermes-broker-approval-v1\x00{")
    assert message.endswith(b"\n") and b"\r\n" not in message
    verify_signed_claim(signed, registry)


def test_broker_canonical_json_is_deterministic_unicode_lf_and_float_forbidden() -> None:
    left = {"z": ["東京", "México"], "a": {"y": 2, "x": True}}
    right = {"a": {"x": True, "y": 2}, "z": ["東京", "México"]}
    encoded = broker_canonical_json_bytes(left)
    assert encoded == broker_canonical_json_bytes(right)
    assert encoded.endswith(b"\n") and not encoded.endswith(b"\n\n")
    assert b"\r\n" not in encoded and "東京".encode() in encoded
    with pytest.raises(BrokerCanonicalizationError, match="floating-point"):
        broker_canonical_json_bytes({"value": 0.5})
    assert h25_canonical_json_bytes({"value": 0.5}).endswith(b"\n")


def test_wrong_key_and_key_id_public_key_mismatch_fail_closed() -> None:
    _private, signed, _registry = _signed_fixture()
    wrong = make_key_registry(
        private_key=Ed25519PrivateKey.generate(),
        key_id="broker1-test-key",
        added_at=NOW,
    )
    with pytest.raises(SignatureVerificationError):
        verify_signed_claim(signed, wrong)


def test_unknown_and_revoked_key_fail_closed() -> None:
    private, signed, _registry = _signed_fixture()
    unknown = make_key_registry(private_key=private, key_id="different-key", added_at=NOW)
    with pytest.raises(UnknownKeyError):
        verify_signed_claim(signed, unknown)
    revoked = make_key_registry(
        private_key=private,
        key_id="broker1-test-key",
        added_at=NOW,
        revoked=True,
    )
    with pytest.raises(RevokedKeyError):
        verify_signed_claim(signed, revoked)


def test_one_bit_message_and_signature_changes_fail_closed() -> None:
    _private, signed, registry = _signed_fixture()
    payload_data = signed.payload.model_dump(mode="python")
    payload_data["single_use_nonce"] = "f" + payload_data["single_use_nonce"][1:]
    message_mutation = SignedApprovalClaim(
        payload=payload_data,
        signature_algorithm="ed25519",
        signature_encoding="lowercase_hex",
        signature=signed.signature,
    )
    with pytest.raises(SignatureVerificationError):
        verify_signed_claim(message_mutation, registry)

    first = int(signed.signature[:2], 16) ^ 1
    signature_mutation = signed.model_copy(
        update={"signature": f"{first:02x}" + signed.signature[2:]}
    )
    with pytest.raises(SignatureVerificationError):
        verify_signed_claim(signature_mutation, registry)


@pytest.mark.parametrize(
    "field,value",
    [
        ("signature", "00" * 63),
        ("signature", "00" * 65),
        ("signature", "GG" * 64),
        ("signature_algorithm", "rsa"),
        ("signature_encoding", "base64url"),
    ],
)
def test_malformed_or_unsupported_signature_envelope_rejects(field: str, value: str) -> None:
    _private, signed, _registry = _signed_fixture()
    raw = signed.model_dump(mode="python")
    raw[field] = value
    with pytest.raises(ValidationError):
        SignedApprovalClaim.model_validate(raw)


@pytest.mark.parametrize("public_key", ["00" * 31, "00" * 33, "GG" * 32])
def test_malformed_public_key_rejects(public_key: str) -> None:
    with pytest.raises(ValidationError):
        TrustedPublicKey(
            key_id="bad-key",
            algorithm="ed25519",
            public_key_encoding="lowercase_hex",
            public_key=public_key,
            state=KeyState.ACTIVE,
            added_at=NOW,
            revoked_at=None,
            revocation_reason=None,
            fixture_only=True,
        )


def test_duplicate_key_id_and_private_material_field_reject() -> None:
    private, _signed, registry = _signed_fixture()
    key = registry.keys[0]
    with pytest.raises(ValidationError, match="duplicate"):
        TrustedKeyRegistry(
            key_registry_schema_version="hermes_broker_trusted_keys_v1",
            key_registry_version="broker1-proof-keys-v1",
            keys=(key, key),
        )
    raw = key.model_dump(mode="python")
    raw["private_key"] = private.private_bytes_raw().hex()
    with pytest.raises(ValidationError):
        TrustedPublicKey.model_validate(raw)


def test_signing_harness_refuses_a0_linkage() -> None:
    private = Ed25519PrivateKey.generate()
    prepared = make_prepared_payload(
        authority_class=AuthorityClass.A0,
        repo_sha=REPO_SHA,
        prepared_record_id=PREPARED_ID,
    )
    action = make_action(
        payload=prepared,
        prepared_record_id=PREPARED_ID,
        action_id="broker1-a0-refusal",
    )
    payload = make_claim_payload(
        action=action,
        signer_key_id="broker1-test-key",
        issued_at=NOW,
    )
    with pytest.raises(ValueError, match="refuses A0"):
        sign_claim_for_proof(
            action=action,
            prepared_payload=prepared,
            claim_payload=payload,
            private_key=private,
        )
