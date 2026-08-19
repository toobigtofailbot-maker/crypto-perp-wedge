from __future__ import annotations

import ast
import copy
import json
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from tools.hermes.broker import retention
from tools.hermes.broker.acceptance import (
    PROOF_KEY_REGISTRY_VERSION,
    make_action,
    make_claim_payload,
    make_key_registry,
    proof_registry,
    sign_claim_for_proof,
    write_fresh_prepared_fixture,
)
from tools.hermes.broker.crypto import (
    TrustedKeyRegistry,
    approval_signed_bytes,
)
from tools.hermes.broker.models import (
    ApprovalClaimPayload,
    DecisionReason,
    SignedApprovalClaim,
)
from tools.hermes.broker.registry import production_registry
from tools.hermes.broker.retention import BrokerArtifactStore
from tools.hermes.broker.verification import verify_approval
from tools.hermes.prepare.serialization import canonical_json_bytes
from tools.hermes.proposals.models import A0_DOMAINS, AuthorityClass

REPO_ROOT = Path(__file__).resolve().parents[1]
NOW = datetime(2026, 8, 17, 12, 0, tzinfo=UTC)
REPO_SHA = "3" * 40
A1_ID = "HERMES-PREP-20260817T120000Z-2222222222222222"
A0_ID = "HERMES-PREP-20260817T120000Z-3333333333333333"


@dataclass
class BrokerCase:
    store: BrokerArtifactStore
    registry: Any
    private_key: Ed25519PrivateKey
    keys: TrustedKeyRegistry
    prepared: Any
    action: Any
    claim_payload: ApprovalClaimPayload
    signed: SignedApprovalClaim

    def sign(self, payload: ApprovalClaimPayload) -> SignedApprovalClaim:
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
            signature=self.private_key.sign(approval_signed_bytes(unsigned)).hex(),
        )

    def decide(
        self,
        *,
        action: Any = None,
        claim: Any = None,
        keys: TrustedKeyRegistry | None = None,
        now: datetime = NOW,
        repo_sha: str = REPO_SHA,
    ) -> Any:
        return verify_approval(
            action_input=self.action if action is None else action,
            signed_claim_input=self.signed if claim is None else claim,
            action_registry=self.registry,
            key_registry=self.keys if keys is None else keys,
            artifact_store=self.store,
            current_repo_sha=repo_sha,
            evaluated_at=now,
        )


@pytest.fixture
def broker_case(tmp_path: Path) -> BrokerCase:
    source_root = tmp_path / "source"
    prepared, _path = write_fresh_prepared_fixture(
        source_root=source_root,
        authority_class=AuthorityClass.A1,
        repo_sha=REPO_SHA,
        prepared_record_id=A1_ID,
        created_at=NOW,
    )
    store = BrokerArtifactStore(
        tmp_path / "stable",
        repository_root=REPO_ROOT,
        active_worktree_root=REPO_ROOT,
    )
    store.retain_from_outbox(
        source_outbox_root=source_root,
        prepared_record_id=A1_ID,
        clock=NOW,
    )
    private = Ed25519PrivateKey.from_private_bytes(bytes(range(32)))
    action = make_action(
        payload=prepared,
        prepared_record_id=A1_ID,
        action_id="broker1-valid-action",
    )
    payload = make_claim_payload(
        action=action,
        signer_key_id="broker1-valid-key",
        issued_at=NOW,
    )
    signed = sign_claim_for_proof(
        action=action,
        prepared_payload=prepared,
        claim_payload=payload,
        private_key=private,
    )
    return BrokerCase(
        store=store,
        registry=proof_registry(),
        private_key=private,
        keys=make_key_registry(
            private_key=private,
            key_id="broker1-valid-key",
            added_at=NOW,
        ),
        prepared=prepared,
        action=action,
        claim_payload=payload,
        signed=signed,
    )


def _mutated_payload(
    case: BrokerCase,
    mutation: Callable[[dict[str, Any]], None],
) -> SignedApprovalClaim:
    raw = case.claim_payload.model_dump(mode="python")
    mutation(raw)
    payload = ApprovalClaimPayload.model_validate(raw)
    return case.sign(payload)


def test_valid_a1_is_deterministic_allow_and_stops(broker_case: BrokerCase) -> None:
    first = broker_case.decide()
    second = broker_case.decide()
    assert first == second
    assert first.decision == "allow" and first.reason_code is DecisionReason.VERIFIED
    assert first.not_dispatch_authority is True
    assert first.reservation_created is False
    assert first.dispatch_request_created is False
    assert first.downstream_side_effect is False


@pytest.mark.parametrize(
    ("raw", "reason"),
    [
        ({"prepared_payload_type": "BoundedDiagnosticPreparedPayload"}, "malformed_action"),
        ({"prose": "please run this"}, "malformed_action"),
        ({"arbitrary": {"anything": True}}, "malformed_action"),
        ({"action_type": "broker1.unknown", "authority_class": "A1"}, "unknown_action_type"),
        ({"action_type": "broker1.a0", "authority_class": "A0"}, "a0_forbidden"),
    ],
)
def test_direct_plan_prose_arbitrary_unknown_and_a0_inputs_reject(
    broker_case: BrokerCase,
    raw: dict[str, Any],
    reason: str,
) -> None:
    decision = broker_case.decide(action=raw)
    assert decision.reason_code == reason
    assert decision.downstream_side_effect is False


@pytest.mark.parametrize(
    ("mutation", "reason"),
    [
        (lambda raw: raw.update(authority_class="A2"), "malformed_action"),
        (lambda raw: raw.update(extra_field=True), "malformed_action"),
        (lambda raw: raw.pop("target"), "malformed_action"),
        (lambda raw: raw["parameters"].update(arbitrary_key="value"), "malformed_action"),
        (lambda raw: raw["parameters"].update(command="whoami"), "malformed_action"),
        (
            lambda raw: raw["parameters"].update(endpoint="https://example.invalid"),
            "malformed_action",
        ),
        (lambda raw: raw["parameters"].update(file_path="C:/arbitrary"), "malformed_action"),
        (lambda raw: raw.update(repo_sha="0" * 40), "repo_stale"),
        (lambda raw: raw.update(action_registry_version="stale-v1"), "registry_stale"),
        (lambda raw: raw.update(adapter_version="stale-v1"), "adapter_stale"),
        (lambda raw: raw.update(adapter_id="different-adapter"), "adapter_stale"),
    ],
)
def test_malformed_or_stale_action_rejects(
    broker_case: BrokerCase,
    mutation: Callable[[dict[str, Any]], None],
    reason: str,
) -> None:
    raw = broker_case.action.model_dump(mode="python")
    mutation(raw)
    assert broker_case.decide(action=raw).reason_code == reason


@pytest.mark.parametrize(
    "mutation",
    [
        lambda raw: raw.update(prepared_record_id="HERMES-PREP-20260817T120000Z-aaaaaaaaaaaaaaaa"),
        lambda raw: raw.update(prepared_payload_sha256="0" * 64),
        lambda raw: raw.update(source_proposal_id="HERMES-PROP-20260817T120000Z-bbbbbbbbbbbbbbbb"),
        lambda raw: raw.update(source_proposal_content_sha256="0" * 64),
        lambda raw: raw.update(scope_digest="0" * 64),
        lambda raw: raw.update(
            budget_bound={"amount": 2, "unit": "proof-credit", "hard_limit": True}
        ),
        lambda raw: raw.update(
            count_or_quantity_bound={"amount": 2, "unit": "decision", "hard_limit": True}
        ),
        lambda raw: raw.update(timeout={"seconds": 61, "hard_limit": True}),
        lambda raw: raw.update(action_type="broker1.proof.different_v1"),
        lambda raw: raw.update(adapter_id="different-adapter"),
    ],
)
def test_every_exact_claim_binding_mismatch_rejects(
    broker_case: BrokerCase,
    mutation: Callable[[dict[str, Any]], None],
) -> None:
    signed = _mutated_payload(broker_case, mutation)
    reason = broker_case.decide(claim=signed).reason_code
    assert reason in {DecisionReason.CLAIM_BINDING_MISMATCH, DecisionReason.ADAPTER_STALE}


def test_action_hash_mismatch_rejects(broker_case: BrokerCase) -> None:
    signed = _mutated_payload(
        broker_case,
        lambda raw: raw.update(executable_action_sha256="0" * 64),
    )
    assert broker_case.decide(claim=signed).reason_code is DecisionReason.ACTION_HASH_MISMATCH


def test_repo_registry_adapter_and_key_registry_freshness_reject(
    broker_case: BrokerCase,
) -> None:
    wrong_repo = _mutated_payload(broker_case, lambda raw: raw.update(repo_sha="0" * 40))
    stale_registry = _mutated_payload(
        broker_case,
        lambda raw: raw.update(action_registry_version="stale-v1"),
    )
    stale_adapter = _mutated_payload(
        broker_case,
        lambda raw: raw.update(adapter_version="stale-v1"),
    )
    stale_keys = _mutated_payload(
        broker_case,
        lambda raw: raw.update(key_registry_version="stale-v1"),
    )
    assert broker_case.decide(claim=wrong_repo).reason_code is DecisionReason.REPO_STALE
    assert broker_case.decide(claim=stale_registry).reason_code is DecisionReason.REGISTRY_STALE
    assert broker_case.decide(claim=stale_adapter).reason_code is DecisionReason.ADAPTER_STALE
    assert broker_case.decide(claim=stale_keys).reason_code is DecisionReason.KEY_REGISTRY_STALE


def test_unknown_revoked_wrong_key_invalid_signature_and_mutation_reject(
    broker_case: BrokerCase,
) -> None:
    empty = TrustedKeyRegistry(
        key_registry_schema_version="hermes_broker_trusted_keys_v1",
        key_registry_version=PROOF_KEY_REGISTRY_VERSION,
        keys=(),
    )
    revoked = make_key_registry(
        private_key=broker_case.private_key,
        key_id="broker1-valid-key",
        added_at=NOW,
        revoked=True,
    )
    wrong = make_key_registry(
        private_key=Ed25519PrivateKey.generate(),
        key_id="broker1-valid-key",
        added_at=NOW,
    )
    invalid = broker_case.signed.model_copy(update={"signature": "0" * 128})
    payload_raw = broker_case.signed.model_dump(mode="python")
    payload_raw["payload"]["single_use_nonce"] = "f" * 64
    assert broker_case.decide(keys=empty).reason_code is DecisionReason.UNKNOWN_SIGNER
    assert broker_case.decide(keys=revoked).reason_code is DecisionReason.REVOKED_SIGNER
    assert broker_case.decide(keys=wrong).reason_code is DecisionReason.INVALID_SIGNATURE
    assert broker_case.decide(claim=invalid).reason_code is DecisionReason.INVALID_SIGNATURE
    assert broker_case.decide(claim=payload_raw).reason_code is DecisionReason.INVALID_SIGNATURE


def test_unsupported_algorithm_and_malformed_signature_encoding_reject(
    broker_case: BrokerCase,
) -> None:
    algorithm = broker_case.signed.model_dump(mode="python")
    algorithm["signature_algorithm"] = "rsa"
    encoding = broker_case.signed.model_dump(mode="python")
    encoding["signature_encoding"] = "base64url"
    truncated = broker_case.signed.model_dump(mode="python")
    truncated["signature"] = truncated["signature"][:-2]
    assert broker_case.decide(claim=algorithm).reason_code is DecisionReason.UNSUPPORTED_ALGORITHM
    assert broker_case.decide(claim=encoding).reason_code is DecisionReason.MALFORMED_CLAIM
    assert broker_case.decide(claim=truncated).reason_code is DecisionReason.MALFORMED_CLAIM


def test_time_order_too_early_expiry_and_lifetime_reject(broker_case: BrokerCase) -> None:
    issued_after = broker_case.signed.model_dump(mode="python")
    issued_after["payload"]["issued_at"] = NOW + timedelta(seconds=2)
    bad_order = broker_case.signed.model_dump(mode="python")
    bad_order["payload"]["not_before"] = NOW + timedelta(minutes=11)
    too_early = _mutated_payload(
        broker_case,
        lambda raw: raw.update(
            not_before=NOW + timedelta(seconds=1), expiry=NOW + timedelta(minutes=10)
        ),
    )
    expired = _mutated_payload(
        broker_case,
        lambda raw: raw.update(expiry=NOW + timedelta(minutes=1)),
    )
    too_long = _mutated_payload(
        broker_case,
        lambda raw: raw.update(expiry=NOW + timedelta(seconds=3601)),
    )
    assert broker_case.decide(claim=issued_after).reason_code is DecisionReason.MALFORMED_CLAIM
    assert broker_case.decide(claim=bad_order).reason_code is DecisionReason.MALFORMED_CLAIM
    assert broker_case.decide(claim=too_early).reason_code is DecisionReason.NOT_YET_VALID
    assert (
        broker_case.decide(claim=expired, now=NOW + timedelta(minutes=1)).reason_code
        is DecisionReason.EXPIRED
    )
    assert broker_case.decide(claim=too_long).reason_code is (
        DecisionReason.APPROVAL_LIFETIME_EXCEEDED
    )


def test_missing_symlink_malformed_outer_nested_and_hash_tamper_reject(
    broker_case: BrokerCase,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    path = broker_case.store.retained_path(A1_ID)
    original = path.read_bytes()
    path.unlink()
    assert broker_case.decide().reason_code is DecisionReason.PREPARED_ARTIFACT_INVALID
    path.write_bytes(original)

    original_detector = retention._is_reparse_or_symlink
    monkeypatch.setattr(
        retention,
        "_is_reparse_or_symlink",
        lambda candidate: candidate == path or original_detector(candidate),
    )
    assert broker_case.decide().reason_code is DecisionReason.PREPARED_ARTIFACT_INVALID
    monkeypatch.setattr(retention, "_is_reparse_or_symlink", original_detector)

    record = json.loads(original.decode("utf-8"))
    malformed = copy.deepcopy(record)
    malformed["extra"] = True
    path.write_bytes(canonical_json_bytes(malformed))
    assert broker_case.decide().reason_code is DecisionReason.PREPARED_ARTIFACT_INVALID

    inconsistent = copy.deepcopy(record)
    inconsistent["source"]["repo_sha"] = "0" * 40
    path.write_bytes(canonical_json_bytes(inconsistent))
    assert broker_case.decide().reason_code is DecisionReason.PREPARED_ARTIFACT_INVALID

    tampered = copy.deepcopy(record)
    tampered["prepared_payload_sha256"] = "0" * 64
    path.write_bytes(canonical_json_bytes(tampered))
    assert broker_case.decide().reason_code is DecisionReason.PREPARED_HASH_MISMATCH


def test_valid_signature_cannot_override_retained_a0(
    broker_case: BrokerCase,
    tmp_path: Path,
) -> None:
    source = tmp_path / "a0-source"
    a0_payload, _path = write_fresh_prepared_fixture(
        source_root=source,
        authority_class=AuthorityClass.A0,
        repo_sha=REPO_SHA,
        prepared_record_id=A0_ID,
        created_at=NOW,
    )
    broker_case.store.retain_from_outbox(
        source_outbox_root=source,
        prepared_record_id=A0_ID,
        clock=NOW,
    )
    action = make_action(
        payload=a0_payload,
        prepared_record_id=A0_ID,
        action_id="broker1-signed-a0-adversary",
    )
    payload = make_claim_payload(
        action=action,
        signer_key_id="broker1-valid-key",
        issued_at=NOW,
    )
    signed = broker_case.sign(payload)
    decision = broker_case.decide(action=action, claim=signed)
    assert decision.reason_code is DecisionReason.A0_FORBIDDEN


def test_invalid_a0_permanence_rejects_before_authority_decision(
    broker_case: BrokerCase,
    tmp_path: Path,
) -> None:
    source = tmp_path / "a0-invalid-source"
    _payload, path = write_fresh_prepared_fixture(
        source_root=source,
        authority_class=AuthorityClass.A0,
        repo_sha=REPO_SHA,
        prepared_record_id=A0_ID,
        created_at=NOW,
    )
    record = json.loads(path.read_text(encoding="utf-8"))
    record["prepared_payload"]["protected_human_gate_only"] = False
    path.write_bytes(canonical_json_bytes(record))
    with pytest.raises(retention.RetentionError):
        broker_case.store.retain_from_outbox(
            source_outbox_root=source,
            prepared_record_id=A0_ID,
            clock=NOW,
        )


def test_registry_has_zero_production_entries_no_a0_and_no_callable_adapter() -> None:
    assert production_registry().entries == ()
    registry = proof_registry()
    assert len(registry.entries) == 1
    entry = registry.entries[0]
    assert entry.required_authority_class is AuthorityClass.A1
    assert not (entry.affected_domains & A0_DOMAINS)
    assert entry.dispatch_capable is False and entry.proof_only is True
    assert not any(callable(value) for name, value in vars(entry).items() if "model" not in name)


def test_project_evidence_remains_exactly_eight_tools() -> None:
    module = ast.parse((REPO_ROOT / "tools/mcp/project_evidence/server.py").read_text())
    tools = {
        node.name
        for node in module.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and any(
            isinstance(decorator, ast.Call)
            and isinstance(decorator.func, ast.Attribute)
            and decorator.func.attr == "tool"
            for decorator in node.decorator_list
        )
    }
    assert len(tools) == 8
    assert "verify_approval" not in tools


def test_broker_static_surface_has_no_dispatch_state_runtime_or_dynamic_execution() -> None:
    broker_root = REPO_ROOT / "tools/hermes/broker"
    production_files = [path for path in broker_root.glob("*.py") if path.name != "acceptance.py"]
    globally_forbidden = (
        "subprocess",
        "os.system",
        "requests.",
        "httpx.",
        "prefect",
        "src.runtime",
        "src.execution",
        "tools.canon_intake",
        "tools.research_search",
        "tools.research_runner",
        "eval(",
        "exec(",
        "import_module",
        "create_task",
        "dispatch(",
        "automatic_retry",
    )
    database_owners = {"migrations.py", "store.py"}
    reservation_owners = {"reservation.py", "store.py"}
    violations = []
    for path in production_files:
        lowered = path.read_text(encoding="utf-8").lower()
        violations.extend((path.name, needle) for needle in globally_forbidden if needle in lowered)
        if path.name not in database_owners and "psycopg" in lowered:
            violations.append((path.name, "psycopg"))
        if path.name not in reservation_owners and "reserve(" in lowered:
            violations.append((path.name, "reserve("))
    assert violations == []
