"""Bounded operator/test acceptance for BROKER-1; never a service or dispatch surface."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Annotated, Any, Literal

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from pydantic import Field

from tools.hermes.prepare.models import (
    BoundedDiagnosticPreparedPayload,
    FutureActionType,
    PreparedPayloadBase,
    PreparedPayloadType,
    StrategyLabPreparedPayload,
)
from tools.hermes.prepare.serialization import canonical_json_bytes
from tools.hermes.proposals.models import AffectedDomain, AuthorityClass, ProposalType

from .crypto import (
    KeyState,
    TrustedKeyRegistry,
    TrustedPublicKey,
    approval_signed_bytes,
)
from .models import (
    APPROVAL_DOMAIN_SEPARATOR,
    ApprovalClaimPayload,
    ExactBound,
    ExecutableAction,
    Identity,
    SignedApprovalClaim,
    StrictBrokerModel,
    TimeoutBound,
)
from .registry import REGISTRY_SCHEMA_VERSION, ActionRegistry, RegistryEntry
from .retention import BrokerArtifactStore, RetentionError
from .serialization import broker_sha256, scope_digest
from .verification import verify_approval

PROOF_ACTION_TYPE = "broker1.proof.verify_identity_v1"
PROOF_REGISTRY_VERSION = "broker1-proof-registry-v1"
PROOF_ADAPTER_ID = "broker1-proof-non-dispatchable"
PROOF_ADAPTER_VERSION = "1.0.0"
PROOF_KEY_REGISTRY_VERSION = "broker1-proof-keys-v1"


class ProofTarget(StrictBrokerModel):
    kind: Literal["broker1_verification_fixture"]
    fixture_id: Identity


class ProofScope(StrictBrokerModel):
    domain: Literal[AffectedDomain.TEST_ONLY_TOOLING]
    operation: Literal["verify_exact_identity_only"]


class ProofParameters(StrictBrokerModel):
    challenge: Annotated[str, Field(min_length=1, max_length=128)]
    expected_identity: Identity


class ProofExecutableAction(ExecutableAction[ProofTarget, ProofScope, ProofParameters]):
    action_type: Literal[PROOF_ACTION_TYPE]


def proof_registry() -> ActionRegistry:
    return ActionRegistry(
        version=PROOF_REGISTRY_VERSION,
        entries=(
            RegistryEntry(
                registry_schema_version=REGISTRY_SCHEMA_VERSION,
                registry_version=PROOF_REGISTRY_VERSION,
                action_type=PROOF_ACTION_TYPE,
                action_model=ProofExecutableAction,
                required_authority_class=AuthorityClass.A1,
                target_model=ProofTarget,
                scope_model=ProofScope,
                parameters_model=ProofParameters,
                budget_model=ExactBound,
                count_or_quantity_model=ExactBound,
                timeout_model=TimeoutBound,
                adapter_id=PROOF_ADAPTER_ID,
                adapter_version=PROOF_ADAPTER_VERSION,
                affected_domains=frozenset({AffectedDomain.TEST_ONLY_TOOLING}),
                dispatch_capable=False,
                proof_only=True,
            ),
        ),
    )


def _evidence(repo_sha: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    reference = "project://status"
    identity_sha = hashlib.sha256(repo_sha.encode("ascii")).hexdigest()
    anchors = [
        {
            "ref": reference,
            "repo_sha": repo_sha,
            "evidence_identities": [{"path": "docs/project_status.md", "sha256": identity_sha}],
            "query_limit": None,
        }
    ]
    facts = [{"statement": "Fresh BROKER-1 acceptance fixture.", "evidence_refs": [reference]}]
    return anchors, facts


def make_prepared_payload(
    *,
    authority_class: AuthorityClass,
    repo_sha: str,
    prepared_record_id: str,
) -> PreparedPayloadBase:
    anchors, facts = _evidence(repo_sha)
    common: dict[str, Any] = {
        "schema_version": "hermes_prepared_payload_v1",
        "repo_sha": repo_sha,
        "source_session_id": "broker1-fresh-acceptance",
        "source_proposal_id": prepared_record_id.replace("HERMES-PREP", "HERMES-PROP"),
        "source_proposal_content_sha256": hashlib.sha256(
            (prepared_record_id + ":source-proposal").encode("ascii")
        ).hexdigest(),
        "source_proposal_repo_sha": repo_sha,
        "source_authority_class": authority_class,
        "evidence_refs": ["project://status"],
        "evidence_anchors": anchors,
        "facts": facts,
        "inferences": ["This fresh artifact is inert acceptance input only."],
        "open_questions": [],
        "target": "Fresh verification-only acceptance target.",
        "scope": "No action; no automatic consumer.",
        "parameters": {"mode": "verification_only"},
        "count_or_quantity_bound": {"amount": 1, "unit": "proof", "hard_limit": True},
        "budget_bound": {"amount": 1, "unit": "proof-credit", "hard_limit": True},
        "timeout": {"seconds": 60, "hard_limit": True},
        "expected_outputs": ["One non-authority verification decision."],
        "validation_plan": ["Recompute exact hashes and deny any mismatch."],
        "rollback_or_stop_conditions": ["Stop before every downstream side effect."],
        "authority_class": authority_class,
        "human_review_required": True,
        "not_authority": True,
        "automatic_consumers": [],
        "self_approval": False,
        "direct_execution": False,
        "standing_authority": False,
        "approval_token_eligible": False,
        "broker_eligible": False,
        "dispatch_eligible": False,
    }
    if authority_class is AuthorityClass.A1:
        return BoundedDiagnosticPreparedPayload.model_validate(
            {
                **common,
                "prepared_payload_type": PreparedPayloadType.BOUNDED_DIAGNOSTIC,
                "source_proposal_type": ProposalType.INVESTIGATION,
                "future_action_type": FutureActionType.BOUNDED_DIAGNOSTIC_DRAFT,
                "body": {
                    "diagnostic_question": "Can BROKER-1 verify exact authority bytes?",
                    "read_only_targets": ["fresh acceptance fixture"],
                    "allowed_diagnostic_concept": "Verification only.",
                    "diagnostic_outputs": ["allow/reject decision"],
                    "execution": False,
                },
            }
        )
    return StrategyLabPreparedPayload.model_validate(
        {
            **common,
            "prepared_payload_type": PreparedPayloadType.STRATEGY_LAB,
            "source_proposal_type": ProposalType.STRATEGY_ADJUSTMENT,
            "future_action_type": FutureActionType.STRATEGY_LAB_DRAFT,
            "permanent_non_executable": True,
            "protected_human_gate_only": True,
            "body": {
                "future_lab_only_experiment_or_spec_draft": "A0 remains proposal-only.",
                "parameters_or_search_space_draft": ["No executable parameters."],
                "data_or_evidence_inputs": ["project://status"],
                "falsification_criteria": ["Any execution path is failure."],
                "candidate_or_promotion_authority": False,
                "go_authority": False,
            },
        }
    )


def prepared_record_bytes(
    *,
    payload: PreparedPayloadBase,
    prepared_record_id: str,
    created_at: datetime,
) -> bytes:
    payload_hash = hashlib.sha256(canonical_json_bytes(payload)).hexdigest()
    record = {
        "schema_version": "hermes_prepared_outbox_v1",
        "prepared_record_id": prepared_record_id,
        "created_at_utc": created_at.isoformat(timespec="seconds").replace("+00:00", "Z"),
        "source": {
            "system": "hermes",
            "session_id": payload.source_session_id,
            "repo_sha": payload.repo_sha,
            "branch": "codex/wp-hermes-broker-1-verification-core-01",
            "source_proposal_id": payload.source_proposal_id,
            "source_proposal_content_sha256": payload.source_proposal_content_sha256,
            "evidence_refs": list(payload.evidence_refs),
        },
        "prepared_payload_type": payload.prepared_payload_type.value,
        "prepared_payload": payload.model_dump(mode="json"),
        "prepared_payload_sha256": payload_hash,
        "hash_scope": "canonical bytes of prepared_payload only; outer metadata excluded",
        "canonicalization": {
            "algorithm": "hermes_canonical_json_v1",
            "encoding": "UTF-8",
            "key_order": "lexicographic",
            "newline": "LF",
            "trailing_newline_count": 1,
        },
        "human_review_required": True,
        "not_authority": True,
        "automatic_consumers": [],
        "self_approval": False,
        "direct_execution": False,
        "approval_token_eligible": False,
        "broker_eligible": False,
        "dispatch_eligible": False,
        "authority": {
            "not_repo_truth": True,
            "not_scientific_truth": True,
            "not_canonical_evidence": True,
            "not_candidate_or_promotion_authority": True,
            "not_dispatch_or_execution_authority": True,
            "not_runtime_or_risk_authority": True,
        },
    }
    return canonical_json_bytes(record)


def write_fresh_prepared_fixture(
    *,
    source_root: Path,
    authority_class: AuthorityClass,
    repo_sha: str,
    prepared_record_id: str,
    created_at: datetime,
) -> tuple[PreparedPayloadBase, Path]:
    source_root.mkdir(parents=True, exist_ok=True)
    payload = make_prepared_payload(
        authority_class=authority_class,
        repo_sha=repo_sha,
        prepared_record_id=prepared_record_id,
    )
    raw = prepared_record_bytes(
        payload=payload,
        prepared_record_id=prepared_record_id,
        created_at=created_at,
    )
    path = source_root / f"{prepared_record_id}.prepared.json"
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "wb", closefd=True) as handle:
        handle.write(raw)
        handle.flush()
        os.fsync(handle.fileno())
    return payload, path


def make_action(
    *,
    payload: PreparedPayloadBase,
    prepared_record_id: str,
    action_id: str,
) -> ProofExecutableAction:
    return ProofExecutableAction(
        executable_action_schema_version="hermes_executable_action_v1",
        executable_action_id=action_id,
        action_type=PROOF_ACTION_TYPE,
        prepared_record_id=prepared_record_id,
        prepared_payload_sha256=hashlib.sha256(canonical_json_bytes(payload)).hexdigest(),
        source_proposal_id=payload.source_proposal_id,
        source_proposal_content_sha256=payload.source_proposal_content_sha256,
        repo_sha=payload.repo_sha,
        action_registry_version=PROOF_REGISTRY_VERSION,
        adapter_id=PROOF_ADAPTER_ID,
        adapter_version=PROOF_ADAPTER_VERSION,
        authority_class=AuthorityClass.A1,
        human_authored=True,
        hermes_authored=False,
        target={"kind": "broker1_verification_fixture", "fixture_id": action_id},
        scope={
            "domain": AffectedDomain.TEST_ONLY_TOOLING,
            "operation": "verify_exact_identity_only",
        },
        parameters={"challenge": "exact-byte-proof", "expected_identity": action_id},
        budget_bound={"amount": 1, "unit": "proof-credit", "hard_limit": True},
        count_or_quantity_bound={"amount": 1, "unit": "decision", "hard_limit": True},
        timeout={"seconds": 60, "hard_limit": True},
    )


def make_claim_payload(
    *,
    action: ProofExecutableAction,
    signer_key_id: str,
    issued_at: datetime,
    not_before: datetime | None = None,
    expiry: datetime | None = None,
) -> ApprovalClaimPayload:
    return ApprovalClaimPayload(
        schema_version="hermes_broker_approval_claim_v1",
        domain_separator=APPROVAL_DOMAIN_SEPARATOR,
        approval_id=f"APPROVAL-{action.executable_action_id}",
        executable_action_id=action.executable_action_id,
        executable_action_sha256=broker_sha256(action),
        prepared_record_id=action.prepared_record_id,
        prepared_payload_sha256=action.prepared_payload_sha256,
        source_proposal_id=action.source_proposal_id,
        source_proposal_content_sha256=action.source_proposal_content_sha256,
        repo_sha=action.repo_sha,
        authority_class=AuthorityClass.A1,
        action_type=action.action_type,
        action_registry_version=action.action_registry_version,
        adapter_id=action.adapter_id,
        adapter_version=action.adapter_version,
        scope_digest=scope_digest(action.scope),
        budget_bound=action.budget_bound,
        count_or_quantity_bound=action.count_or_quantity_bound,
        timeout=action.timeout,
        issued_at=issued_at,
        not_before=not_before or issued_at,
        expiry=expiry or issued_at + timedelta(minutes=10),
        single_use_nonce=hashlib.sha256(action.executable_action_id.encode("ascii")).hexdigest(),
        signer_key_id=signer_key_id,
        key_registry_version=PROOF_KEY_REGISTRY_VERSION,
    )


def sign_claim_for_proof(
    *,
    action: ProofExecutableAction,
    prepared_payload: PreparedPayloadBase,
    claim_payload: ApprovalClaimPayload,
    private_key: Ed25519PrivateKey,
) -> SignedApprovalClaim:
    """Operator/test guard: refuses every non-A1 or A0-linked object before signing."""

    if (
        action.authority_class is not AuthorityClass.A1
        or prepared_payload.authority_class is not AuthorityClass.A1
        or prepared_payload.source_authority_class is not AuthorityClass.A1
        or claim_payload.authority_class is not AuthorityClass.A1
    ):
        raise ValueError("proof signing harness refuses A0 or non-A1 authority")
    unsigned = SignedApprovalClaim.model_construct(
        payload=claim_payload,
        signature_algorithm="ed25519",
        signature_encoding="lowercase_hex",
        signature="0" * 128,
    )
    signature = private_key.sign(approval_signed_bytes(unsigned)).hex()
    return SignedApprovalClaim(
        payload=claim_payload,
        signature_algorithm="ed25519",
        signature_encoding="lowercase_hex",
        signature=signature,
    )


def _adversarial_sign(
    payload: ApprovalClaimPayload,
    private_key: Ed25519PrivateKey,
) -> SignedApprovalClaim:
    """Simulate a compromised signer; intentionally bypasses the operator guard for A0 proof."""

    unsigned = SignedApprovalClaim.model_construct(
        payload=payload,
        signature_algorithm="ed25519",
        signature_encoding="lowercase_hex",
        signature="0" * 128,
    )
    return SignedApprovalClaim(
        payload=payload,
        signature_algorithm="ed25519",
        signature_encoding="lowercase_hex",
        signature=private_key.sign(approval_signed_bytes(unsigned)).hex(),
    )


def make_key_registry(
    *,
    private_key: Ed25519PrivateKey,
    key_id: str,
    added_at: datetime,
    revoked: bool = False,
) -> TrustedKeyRegistry:
    public = private_key.public_key().public_bytes(
        serialization.Encoding.Raw,
        serialization.PublicFormat.Raw,
    )
    return TrustedKeyRegistry(
        key_registry_schema_version="hermes_broker_trusted_keys_v1",
        key_registry_version=PROOF_KEY_REGISTRY_VERSION,
        keys=(
            TrustedPublicKey(
                key_id=key_id,
                algorithm="ed25519",
                public_key_encoding="lowercase_hex",
                public_key=public.hex(),
                state=KeyState.REVOKED if revoked else KeyState.ACTIVE,
                added_at=added_at,
                revoked_at=added_at if revoked else None,
                revocation_reason="BROKER-1 revoked-key proof" if revoked else None,
                fixture_only=True,
            ),
        ),
    )


def run_physical_acceptance(
    *,
    artifact_root: Path,
    repository_root: Path,
    worktree_root: Path,
    current_repo_sha: str,
    evaluated_at: datetime,
) -> dict[str, Any]:
    """Execute the required physical no-side-effect proof on one host."""

    token = uuid.uuid4().hex[:16]
    stamp = evaluated_at.strftime("%Y%m%dT%H%M%SZ")
    a1_id = f"HERMES-PREP-{stamp}-{token}"
    a0_id = f"HERMES-PREP-{stamp}-{uuid.uuid4().hex[:16]}"
    source_root = worktree_root / "scratch" / f"broker1_acceptance_source_{token}"
    a1_payload, a1_source = write_fresh_prepared_fixture(
        source_root=source_root,
        authority_class=AuthorityClass.A1,
        repo_sha=current_repo_sha,
        prepared_record_id=a1_id,
        created_at=evaluated_at,
    )
    a0_payload, a0_source = write_fresh_prepared_fixture(
        source_root=source_root,
        authority_class=AuthorityClass.A0,
        repo_sha=current_repo_sha,
        prepared_record_id=a0_id,
        created_at=evaluated_at,
    )
    store = BrokerArtifactStore(
        artifact_root,
        repository_root=repository_root,
        active_worktree_root=worktree_root,
    )
    a1_receipt = store.retain_from_outbox(
        source_outbox_root=source_root,
        prepared_record_id=a1_id,
        clock=evaluated_at,
    )
    a0_receipt = store.retain_from_outbox(
        source_outbox_root=source_root,
        prepared_record_id=a0_id,
        clock=evaluated_at,
    )
    no_overwrite_rejected = False
    try:
        store.retain_from_outbox(
            source_outbox_root=source_root,
            prepared_record_id=a1_id,
            clock=evaluated_at,
        )
    except RetentionError:
        no_overwrite_rejected = True

    private_key = Ed25519PrivateKey.generate()
    key_id = f"broker1-proof-key-{token}"
    keys = make_key_registry(
        private_key=private_key,
        key_id=key_id,
        added_at=evaluated_at - timedelta(seconds=1),
    )
    registry = proof_registry()
    a1_action = make_action(
        payload=a1_payload,
        prepared_record_id=a1_id,
        action_id=f"broker1-a1-{token}",
    )
    a1_claim_payload = make_claim_payload(
        action=a1_action,
        signer_key_id=key_id,
        issued_at=evaluated_at,
    )
    a1_claim = sign_claim_for_proof(
        action=a1_action,
        prepared_payload=a1_payload,
        claim_payload=a1_claim_payload,
        private_key=private_key,
    )
    allow = verify_approval(
        action_input=a1_action,
        signed_claim_input=a1_claim,
        action_registry=registry,
        key_registry=keys,
        artifact_store=store,
        current_repo_sha=current_repo_sha,
        evaluated_at=evaluated_at,
    )

    a0_action = make_action(
        payload=a0_payload,
        prepared_record_id=a0_id,
        action_id=f"broker1-a0-adversarial-{token}",
    )
    a0_claim_payload = make_claim_payload(
        action=a0_action,
        signer_key_id=key_id,
        issued_at=evaluated_at,
    )
    signing_guard_rejected_a0 = False
    try:
        sign_claim_for_proof(
            action=a0_action,
            prepared_payload=a0_payload,
            claim_payload=a0_claim_payload,
            private_key=private_key,
        )
    except ValueError:
        signing_guard_rejected_a0 = True
    a0_claim = _adversarial_sign(a0_claim_payload, private_key)
    reject_a0 = verify_approval(
        action_input=a0_action,
        signed_claim_input=a0_claim,
        action_registry=registry,
        key_registry=keys,
        artifact_store=store,
        current_repo_sha=current_repo_sha,
        evaluated_at=evaluated_at,
    )

    revoked_keys = make_key_registry(
        private_key=private_key,
        key_id=key_id,
        added_at=evaluated_at - timedelta(seconds=1),
        revoked=True,
    )
    revoked = verify_approval(
        action_input=a1_action,
        signed_claim_input=a1_claim,
        action_registry=registry,
        key_registry=revoked_keys,
        artifact_store=store,
        current_repo_sha=current_repo_sha,
        evaluated_at=evaluated_at,
    )
    prepared_direct = verify_approval(
        action_input=a1_payload,
        signed_claim_input=a1_claim,
        action_registry=registry,
        key_registry=keys,
        artifact_store=store,
        current_repo_sha=current_repo_sha,
        evaluated_at=evaluated_at,
    )
    generic_direct = verify_approval(
        action_input={"prose": "attempted authority"},
        signed_claim_input=a1_claim,
        action_registry=registry,
        key_registry=keys,
        artifact_store=store,
        current_repo_sha=current_repo_sha,
        evaluated_at=evaluated_at,
    )

    tampered_action = a1_action.model_dump(mode="python")
    tampered_action["prepared_payload_sha256"] = "0" * 64
    hash_tamper = verify_approval(
        action_input=tampered_action,
        signed_claim_input=a1_claim,
        action_registry=registry,
        key_registry=keys,
        artifact_store=store,
        current_repo_sha=current_repo_sha,
        evaluated_at=evaluated_at,
    )
    stale_registry_payload = ApprovalClaimPayload.model_validate(
        {
            **a1_claim_payload.model_dump(mode="python"),
            "action_registry_version": "stale-registry-v1",
        }
    )
    stale_registry = verify_approval(
        action_input=a1_action,
        signed_claim_input=_adversarial_sign(stale_registry_payload, private_key),
        action_registry=registry,
        key_registry=keys,
        artifact_store=store,
        current_repo_sha=current_repo_sha,
        evaluated_at=evaluated_at,
    )
    stale_adapter_payload = ApprovalClaimPayload.model_validate(
        {
            **a1_claim_payload.model_dump(mode="python"),
            "adapter_version": "stale-adapter-v1",
        }
    )
    stale_adapter = verify_approval(
        action_input=a1_action,
        signed_claim_input=_adversarial_sign(stale_adapter_payload, private_key),
        action_registry=registry,
        key_registry=keys,
        artifact_store=store,
        current_repo_sha=current_repo_sha,
        evaluated_at=evaluated_at,
    )
    wrong_repo_payload = ApprovalClaimPayload.model_validate(
        {
            **a1_claim_payload.model_dump(mode="python"),
            "repo_sha": "0" * 40,
        }
    )
    wrong_repo = verify_approval(
        action_input=a1_action,
        signed_claim_input=_adversarial_sign(wrong_repo_payload, private_key),
        action_registry=registry,
        key_registry=keys,
        artifact_store=store,
        current_repo_sha=current_repo_sha,
        evaluated_at=evaluated_at,
    )
    early_payload = make_claim_payload(
        action=a1_action,
        signer_key_id=key_id,
        issued_at=evaluated_at,
        not_before=evaluated_at + timedelta(seconds=1),
        expiry=evaluated_at + timedelta(minutes=10),
    )
    too_early = verify_approval(
        action_input=a1_action,
        signed_claim_input=_adversarial_sign(early_payload, private_key),
        action_registry=registry,
        key_registry=keys,
        artifact_store=store,
        current_repo_sha=current_repo_sha,
        evaluated_at=evaluated_at,
    )
    expired_payload = make_claim_payload(
        action=a1_action,
        signer_key_id=key_id,
        issued_at=evaluated_at - timedelta(minutes=10),
        not_before=evaluated_at - timedelta(minutes=10),
        expiry=evaluated_at,
    )
    expired = verify_approval(
        action_input=a1_action,
        signed_claim_input=_adversarial_sign(expired_payload, private_key),
        action_registry=registry,
        key_registry=keys,
        artifact_store=store,
        current_repo_sha=current_repo_sha,
        evaluated_at=evaluated_at,
    )

    # Removing only the fresh source fixtures is the required worktree-independence proof.
    a1_source.unlink()
    a0_source.unlink()
    retained_after_source_removal = (
        store.verify_retained(a1_id).prepared_payload_sha256 == a1_receipt.prepared_payload_sha256
    )
    return {
        "acceptance_schema_version": "hermes_broker1_physical_acceptance_v1",
        "artifact_root": str(artifact_root.resolve()),
        "repo_sha": current_repo_sha,
        "cryptography_private_key_persisted": False,
        "a1_decision": allow.model_dump(mode="json"),
        "a0_valid_signature_decision": reject_a0.model_dump(mode="json"),
        "a0_signing_guard_rejected": signing_guard_rejected_a0,
        "prepared_plan_direct_decision": prepared_direct.model_dump(mode="json"),
        "generic_dict_direct_decision": generic_direct.model_dump(mode="json"),
        "hash_tamper_decision": hash_tamper.model_dump(mode="json"),
        "revoked_key_decision": revoked.model_dump(mode="json"),
        "stale_registry_decision": stale_registry.model_dump(mode="json"),
        "stale_adapter_decision": stale_adapter.model_dump(mode="json"),
        "wrong_repo_decision": wrong_repo.model_dump(mode="json"),
        "too_early_decision": too_early.model_dump(mode="json"),
        "expired_decision": expired.model_dump(mode="json"),
        "a1_retention_receipt": a1_receipt.to_dict(),
        "a0_retention_receipt": a0_receipt.to_dict(),
        "no_overwrite_rejected": no_overwrite_rejected,
        "retained_after_source_removal": retained_after_source_removal,
        "production_registry_entry_count": 0,
        "proof_registry_entry_count": len(registry.entries),
        "reservation_created": False,
        "dispatch_request_created": False,
        "downstream_side_effect": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run BROKER-1 physical no-action acceptance")
    parser.add_argument("--artifact-root", required=True, type=Path)
    parser.add_argument("--repository-root", required=True, type=Path)
    parser.add_argument("--worktree-root", required=True, type=Path)
    parser.add_argument("--repo-sha", required=True)
    args = parser.parse_args()
    result = run_physical_acceptance(
        artifact_root=args.artifact_root,
        repository_root=args.repository_root,
        worktree_root=args.worktree_root,
        current_repo_sha=args.repo_sha,
        evaluated_at=datetime.now(UTC).replace(microsecond=0),
    )
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
