from __future__ import annotations

import ast
import hashlib
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from pydantic import ValidationError

from tools.hermes.broker.acceptance import make_claim_payload, make_key_registry
from tools.hermes.broker.adapters import readonly_repo_evidence as adapter_module
from tools.hermes.broker.adapters.readonly_repo_evidence import (
    ReadonlyAdapterError,
    readonly_repo_evidence,
)
from tools.hermes.broker.crypto import approval_signed_bytes, verify_signed_claim
from tools.hermes.broker.h3_readonly import (
    READONLY_ACTION_TYPE,
    READONLY_ADAPTER_ID,
    READONLY_ADAPTER_VERSION,
    READONLY_FILE_BYTES_EXCEEDED_REASON,
    READONLY_FILE_COUNT_EXCEEDED_REASON,
    READONLY_PROJECTION_SCHEMA_VERSION,
    READONLY_REGISTRY_VERSION,
    H3ReadonlyExecutableAction,
    H3ReadonlyProjectedParameters,
    H3ReadonlyProjection,
    H3ReadonlyResultRecord,
    ProjectionError,
    build_h3_readonly_projection,
    h3_1_readonly_registry,
)
from tools.hermes.broker.models import ExactBound, TimeoutBound
from tools.hermes.broker.readonly_dispatch import (
    BrokerReadonlyDispatchResult,
    derive_dispatch_id,
)
from tools.hermes.broker.readonly_result_store import (
    H3ReadonlyResultStore,
    ResultStoreError,
)
from tools.hermes.broker.registry import REGISTRY_SCHEMA_VERSION, RegistryEntry, production_registry
from tools.hermes.broker.serialization import broker_sha256
from tools.hermes.broker.signing import (
    WysiwysBindingError,
    build_wysiwys_surface,
    production_trusted_public_key,
    sign_wysiwys_surface,
)
from tools.hermes.broker.state import BrokerActionState
from tools.hermes.proposals.models import A0_DOMAINS, AffectedDomain, AuthorityClass

REPO_ROOT = Path(__file__).resolve().parents[1]
REPO_SHA = "3" * 40
NOW = datetime(2026, 8, 27, 12, 0, tzinfo=UTC)


def _action(
    *,
    action_id: str = "h3-act-1",
    adapter_id: str = READONLY_ADAPTER_ID,
    adapter_version: str = READONLY_ADAPTER_VERSION,
    registry_version: str = READONLY_REGISTRY_VERSION,
    max_files: int = 512,
    max_file_bytes: int = 2_000_000,
    repo_sha: str = REPO_SHA,
) -> H3ReadonlyExecutableAction:
    return H3ReadonlyExecutableAction(
        executable_action_schema_version="hermes_executable_action_v1",
        executable_action_id=action_id,
        action_type=READONLY_ACTION_TYPE,
        prepared_record_id="HERMES-PREP-20260827T120000Z-1111111111111111",
        prepared_payload_sha256="a" * 64,
        source_proposal_id="HERMES-PROP-20260827T120000Z-1111111111111111",
        source_proposal_content_sha256="b" * 64,
        repo_sha=repo_sha,
        action_registry_version=registry_version,
        adapter_id=adapter_id,
        adapter_version=adapter_version,
        authority_class=AuthorityClass.A1,
        human_authored=True,
        hermes_authored=False,
        target={
            "kind": "repo_status_entry_evidence",
            "evidence_root_relpath": "docs/status_entries",
        },
        scope={
            "domain": AffectedDomain.BOUNDED_INVESTIGATION,
            "operation": "readonly_repo_evidence_summary_only",
        },
        parameters={
            "filename_prefix": "WP-HERMES-",
            "filename_suffix": ".md",
            "max_files": max_files,
            "max_file_bytes": max_file_bytes,
        },
        budget_bound={"amount": 1, "unit": "read-credit", "hard_limit": True},
        count_or_quantity_bound={"amount": 512, "unit": "file", "hard_limit": True},
        timeout={"seconds": 60, "hard_limit": True},
    )


def _projection(**kwargs: Any) -> H3ReadonlyProjection:
    return build_h3_readonly_projection(
        action=kwargs.pop("action", _action()),
        action_registry=kwargs.pop("action_registry", h3_1_readonly_registry()),
        approval_id=kwargs.pop("approval_id", "APPROVAL-h3-act-1"),
        reservation_id=kwargs.pop("reservation_id", "BROKER-RES-" + "0" * 32),
        single_use_nonce=kwargs.pop("single_use_nonce", "f" * 64),
    )


# --------------------------------------------------------------------------- registry


def test_production_registry_has_exactly_one_real_read_only_action() -> None:
    registry = production_registry()
    assert registry.version == READONLY_REGISTRY_VERSION
    assert len(registry.entries) == 1
    entry = registry.entries[0]
    assert entry.action_type == READONLY_ACTION_TYPE
    assert entry.adapter_id == READONLY_ADAPTER_ID
    assert entry.adapter_version == READONLY_ADAPTER_VERSION
    assert entry.required_authority_class is AuthorityClass.A1
    assert entry.affected_domains == frozenset({AffectedDomain.BOUNDED_INVESTIGATION})
    assert not (entry.affected_domains & A0_DOMAINS)
    assert entry.dispatch_capable is True
    assert entry.proof_only is False
    assert entry.read_only is True
    assert not any(callable(value) for name, value in vars(entry).items() if "model" not in name)


def _entry(**overrides: Any) -> RegistryEntry:
    base: dict[str, Any] = {
        "registry_schema_version": REGISTRY_SCHEMA_VERSION,
        "registry_version": READONLY_REGISTRY_VERSION,
        "action_type": READONLY_ACTION_TYPE,
        "action_model": H3ReadonlyExecutableAction,
        "required_authority_class": AuthorityClass.A1,
        "target_model": type(_action().target),
        "scope_model": type(_action().scope),
        "parameters_model": type(_action().parameters),
        "budget_model": ExactBound,
        "count_or_quantity_model": ExactBound,
        "timeout_model": TimeoutBound,
        "adapter_id": READONLY_ADAPTER_ID,
        "adapter_version": READONLY_ADAPTER_VERSION,
        "affected_domains": frozenset({AffectedDomain.BOUNDED_INVESTIGATION}),
        "dispatch_capable": True,
        "proof_only": False,
        "read_only": True,
    }
    base.update(overrides)
    return RegistryEntry(**base)


def test_registry_model_locks_read_only_and_dispatch_proof_xor() -> None:
    # A mutating entry can never be registered.
    with pytest.raises(ValueError, match="read-only"):
        _entry(read_only=False)
    # An entry is exactly one of proof_only or dispatch_capable, never both.
    with pytest.raises(ValueError, match="exactly one"):
        _entry(dispatch_capable=True, proof_only=True)
    with pytest.raises(ValueError, match="exactly one"):
        _entry(dispatch_capable=False, proof_only=False)
    # A0 domains and non-A1 authority remain impossible.
    with pytest.raises(ValueError, match="A0 domains"):
        _entry(affected_domains=frozenset({AffectedDomain.OMS}))
    with pytest.raises(ValueError, match="require A1"):
        _entry(required_authority_class=AuthorityClass.A2)
    # A non-dispatching proof entry is still expressible (read-only).
    proof = _entry(dispatch_capable=False, proof_only=True)
    assert proof.dispatch_capable is False and proof.proof_only is True and proof.read_only is True


# --------------------------------------------------------------------------- action model


def test_action_model_is_closed_and_rejects_extra_or_wrong_fields() -> None:
    with pytest.raises(ValidationError):
        H3ReadonlyExecutableAction.model_validate(
            {
                **_action().model_dump(mode="python"),
                "parameters": {
                    "filename_prefix": "WP-HERMES-",
                    "filename_suffix": ".md",
                    "max_files": 10,
                    "max_file_bytes": 1000,
                    "extra": True,
                },
            }
        )
    with pytest.raises(ValidationError):
        H3ReadonlyExecutableAction.model_validate(
            {**_action().model_dump(mode="python"), "action_type": "h3_1.readonly.other_v1"}
        )
    # A wrong evidence root literal is rejected (fixed target).
    with pytest.raises(ValidationError):
        H3ReadonlyExecutableAction.model_validate(
            {
                **_action().model_dump(mode="python"),
                "target": {"kind": "repo_status_entry_evidence", "evidence_root_relpath": "src"},
            }
        )


# --------------------------------------------------------------------------- projection


def test_projection_binds_exact_reserved_identity_and_is_deterministic() -> None:
    first = _projection()
    second = _projection()
    assert first == second
    assert first.projection_sha256 == second.projection_sha256
    assert first.action_type == READONLY_ACTION_TYPE
    assert first.action_registry_version == READONLY_REGISTRY_VERSION
    assert first.adapter_id == READONLY_ADAPTER_ID
    assert first.adapter_version == READONLY_ADAPTER_VERSION
    assert first.approval_id == "APPROVAL-h3-act-1"
    assert first.reservation_id == "BROKER-RES-" + "0" * 32
    assert first.single_use_nonce == "f" * 64
    assert first.repo_sha == REPO_SHA
    assert first.projection_schema_version == READONLY_PROJECTION_SCHEMA_VERSION
    assert first.read_only is True
    assert first.executable_action_sha256 == broker_sha256(_action())


def test_projected_parameters_are_a_closed_schema_of_exact_fields() -> None:
    assert set(H3ReadonlyProjectedParameters.model_fields) == {
        "evidence_root_relpath",
        "filename_prefix",
        "filename_suffix",
        "max_files",
        "max_file_bytes",
        "operation",
    }


def test_projection_fails_closed_on_wrong_registry_adapter_and_type() -> None:
    with pytest.raises(ProjectionError, match="registry version"):
        _projection(action=_action(registry_version="h3-1-readonly-registry-v2"))
    with pytest.raises(ProjectionError, match="adapter id"):
        _projection(action=_action(adapter_id="not-the-readonly-adapter"))
    with pytest.raises(ProjectionError, match="adapter version"):
        _projection(action=_action(adapter_version="9.9.9"))


# --------------------------------------------------------------------------- adapter


def _write_evidence(root: Path, files: dict[str, bytes]) -> None:
    evidence = root / "docs" / "status_entries"
    evidence.mkdir(parents=True, exist_ok=True)
    for name, data in files.items():
        (evidence / name).write_bytes(data)


def test_adapter_reads_committed_evidence_deterministically(tmp_path: Path) -> None:
    _write_evidence(
        tmp_path,
        {
            "WP-HERMES-B.md": b"beta\n",
            "WP-HERMES-A.md": b"alpha\n",
            "README.md": b"ignored\n",
            "WP-OTHER-X.md": b"ignored\n",
        },
    )
    projection = _projection()
    record = readonly_repo_evidence(
        projection, dispatch_id="BROKER-DIS-" + "0" * 32, repo_root=tmp_path
    )
    assert record.outcome == "completed"
    assert record.reason_code is None
    assert [entry.relpath for entry in record.entries] == [
        "docs/status_entries/WP-HERMES-A.md",
        "docs/status_entries/WP-HERMES-B.md",
    ]
    assert record.entries[0].sha256 == hashlib.sha256(b"alpha\n").hexdigest()
    assert record.file_count == 2
    assert record.total_byte_size == len(b"alpha\n") + len(b"beta\n")
    assert record.mutation_side_effect is False
    assert record.wrote_repo_or_canonical is False
    again = readonly_repo_evidence(
        projection, dispatch_id="BROKER-DIS-" + "0" * 32, repo_root=tmp_path
    )
    assert record == again


def test_adapter_enforces_count_and_byte_caps_with_deterministic_failure(tmp_path: Path) -> None:
    _write_evidence(
        tmp_path,
        {"WP-HERMES-A.md": b"a\n", "WP-HERMES-B.md": b"b\n", "WP-HERMES-C.md": b"c\n"},
    )
    count_capped = readonly_repo_evidence(
        _projection(action=_action(max_files=2)),
        dispatch_id="BROKER-DIS-" + "0" * 32,
        repo_root=tmp_path,
    )
    assert count_capped.outcome == "failed"
    assert count_capped.reason_code == READONLY_FILE_COUNT_EXCEEDED_REASON
    assert count_capped.file_count == 0

    byte_capped = readonly_repo_evidence(
        _projection(action=_action(max_file_bytes=1)),
        dispatch_id="BROKER-DIS-" + "0" * 32,
        repo_root=tmp_path,
    )
    assert byte_capped.outcome == "failed"
    assert byte_capped.reason_code == READONLY_FILE_BYTES_EXCEEDED_REASON


def test_adapter_writes_nothing_to_the_repo(tmp_path: Path) -> None:
    _write_evidence(tmp_path, {"WP-HERMES-A.md": b"alpha\n"})
    evidence = tmp_path / "docs" / "status_entries"
    before = {p.name: (p.stat().st_size, p.stat().st_mtime_ns) for p in evidence.iterdir()}
    readonly_repo_evidence(_projection(), dispatch_id="BROKER-DIS-" + "0" * 32, repo_root=tmp_path)
    after = {p.name: (p.stat().st_size, p.stat().st_mtime_ns) for p in evidence.iterdir()}
    assert before == after
    # No new file anywhere under the repo root was created.
    assert sorted(p.name for p in evidence.iterdir()) == ["WP-HERMES-A.md"]


def test_adapter_refuses_symlink_reparse_and_missing_root(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    with pytest.raises(ReadonlyAdapterError, match="repo root"):
        readonly_repo_evidence(
            _projection(), dispatch_id="BROKER-DIS-" + "0" * 32, repo_root=tmp_path / "absent"
        )
    _write_evidence(tmp_path, {"WP-HERMES-A.md": b"alpha\n"})
    target = tmp_path / "docs" / "status_entries" / "WP-HERMES-A.md"
    original = adapter_module._is_reparse_or_symlink
    monkeypatch.setattr(
        adapter_module,
        "_is_reparse_or_symlink",
        lambda candidate: Path(candidate) == target or original(candidate),
    )
    with pytest.raises(ReadonlyAdapterError, match="symlink or reparse"):
        readonly_repo_evidence(
            _projection(), dispatch_id="BROKER-DIS-" + "0" * 32, repo_root=tmp_path
        )


def test_result_record_model_is_closed_with_read_only_assertions() -> None:
    with pytest.raises(ValidationError):
        H3ReadonlyResultRecord.model_validate(
            {
                "result_schema_version": "hermes_broker_h3_1_readonly_result_v1",
                "result_record_id": "H3RO-" + "0" * 32,
                "executable_action_id": "h3-act-1",
                "executable_action_sha256": "a" * 64,
                "approval_id": "APPROVAL-h3-act-1",
                "reservation_id": "BROKER-RES-" + "0" * 32,
                "dispatch_id": "BROKER-DIS-" + "0" * 32,
                "repo_sha": REPO_SHA,
                "action_type": READONLY_ACTION_TYPE,
                "adapter_id": READONLY_ADAPTER_ID,
                "adapter_version": READONLY_ADAPTER_VERSION,
                "projection_sha256": "c" * 64,
                "evidence_root_relpath": "docs/status_entries",
                "entries": [],
                "file_count": 0,
                "total_byte_size": 0,
                "outcome": "completed",
                "reason_code": None,
                # A record can never assert a mutation side effect.
                "mutation_side_effect": True,
                "protected_surface_touched": False,
                "network_access": False,
                "child_process_spawned": False,
                "wrote_repo_or_canonical": False,
            }
        )


def test_adapter_import_surface_is_read_only_and_minimal() -> None:
    src = (REPO_ROOT / "tools/hermes/broker/adapters/readonly_repo_evidence.py").read_text()
    tree = ast.parse(src)
    external_roots: set[str] = set()
    internal_modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            external_roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.level and node.module:
                internal_modules.add(node.module.split(".")[0])
            elif node.module:
                external_roots.add(node.module.split(".")[0])
    # The import allowlist alone forbids every network/subprocess/dynamic module
    # (subprocess, socket, urllib, httpx, requests, shutil, ctypes, importlib, ...):
    # the adapter imports only these read-capable roots and one local module.
    assert external_roots <= {"__future__", "hashlib", "os", "stat", "pathlib"}
    assert internal_modules <= {"h3_readonly"}
    # No concrete write/exec/mutation *call* appears anywhere in the source (prose in
    # docstrings is fine; these needles only match real API calls).
    lowered = src.lower()
    for forbidden in (
        "os.system(",
        "o_wronly",
        "o_creat",
        "o_trunc",
        ".write(",
        ".unlink(",
        ".rmdir(",
        ".rename(",
        ".mkdir(",
        "os.remove(",
        "shutil.",
    ):
        assert forbidden not in lowered, forbidden


# --------------------------------------------------------------------------- result store


def test_result_store_is_external_no_overwrite_and_symlink_guarded(tmp_path: Path) -> None:
    _write_evidence(tmp_path / "repo", {"WP-HERMES-A.md": b"alpha\n"})
    # A store root inside the repository/worktree is refused.
    with pytest.raises(ResultStoreError, match="outside repository"):
        H3ReadonlyResultStore(
            tmp_path / "repo" / "inside",
            repository_root=tmp_path / "repo",
            active_worktree_root=tmp_path / "repo",
        )
    store = H3ReadonlyResultStore(
        tmp_path / "external",
        repository_root=tmp_path / "repo",
        active_worktree_root=tmp_path / "repo",
    )
    record = readonly_repo_evidence(
        _projection(), dispatch_id="BROKER-DIS-" + "0" * 32, repo_root=tmp_path / "repo"
    )
    receipt = store.write_result(record)
    assert receipt.wrote_repo_or_canonical is False
    assert receipt.exclusive_create is True
    written = store.result_path(record.result_record_id)
    assert written.is_file()
    assert hashlib.sha256(written.read_bytes()).hexdigest() == receipt.retained_byte_sha256
    # No overwrite of an existing result record.
    with pytest.raises(ResultStoreError, match="already exists"):
        store.write_result(record)


# --------------------------------------------------------------------------- WYSIWYS


def test_wysiwys_hash_equality_end_to_end() -> None:
    action = _action()
    private_key = Ed25519PrivateKey.from_private_bytes(bytes(range(32)))
    payload = make_claim_payload(action=action, signer_key_id="h3-prod-key", issued_at=NOW)
    surface = build_wysiwys_surface(action=action, claim_payload=payload)

    # The displayed action hash is the exact hash the broker recomputes and the claim binds.
    assert surface.action_sha256 == broker_sha256(action)
    assert surface.action_sha256 == payload.executable_action_sha256
    assert surface.action_sha256 in surface.render()
    assert surface.signing_message_sha256 in surface.render()
    assert surface.to_manifest()["executable_action_sha256"] == surface.action_sha256

    signed = sign_wysiwys_surface(surface, private_key)
    # The signed message is exactly the surfaced bytes and hash.
    assert approval_signed_bytes(signed) == surface.signing_message_bytes
    assert (
        hashlib.sha256(approval_signed_bytes(signed)).hexdigest() == surface.signing_message_sha256
    )
    keys = make_key_registry(private_key=private_key, key_id="h3-prod-key", added_at=NOW)
    verify_signed_claim(signed, keys)  # does not raise
    # The projection built from the same action carries the same action hash.
    projection = _projection(action=action)
    assert projection.executable_action_sha256 == surface.action_sha256


def test_wysiwys_refuses_a_claim_that_does_not_bind_the_action() -> None:
    action = _action()
    other = _action(action_id="h3-act-OTHER")
    payload = make_claim_payload(action=other, signer_key_id="h3-prod-key", issued_at=NOW)
    with pytest.raises(WysiwysBindingError, match="exactly bind"):
        build_wysiwys_surface(action=action, claim_payload=payload)


def test_wysiwys_tampered_action_after_signing_fails_broker_hash_binding() -> None:
    action = _action()
    private_key = Ed25519PrivateKey.from_private_bytes(bytes(range(32)))
    payload = make_claim_payload(action=action, signer_key_id="h3-prod-key", issued_at=NOW)
    surface = build_wysiwys_surface(action=action, claim_payload=payload)
    signed = sign_wysiwys_surface(surface, private_key)
    # A one-field tamper changes the action hash; the signed claim no longer binds it.
    tampered = action.model_copy(update={"executable_action_id": "h3-act-TAMPERED"})
    assert broker_sha256(tampered) != signed.payload.executable_action_sha256


def test_production_trusted_public_key_is_public_only_and_not_fixture() -> None:
    private_key = Ed25519PrivateKey.from_private_bytes(bytes(range(32)))
    entry = production_trusted_public_key(
        public_key=private_key.public_key(),
        key_id="h3-prod-key",
        key_registry_version="h3-1-production-keys-v1",
        added_at=NOW,
    )
    assert entry.fixture_only is False
    assert entry.state.value == "active"
    assert len(entry.public_key) == 64


# --------------------------------------------------------------------------- dispatch result / id


def test_dispatch_id_is_deterministic_and_identity_bound() -> None:
    first = _projection()
    assert derive_dispatch_id(first) == derive_dispatch_id(first)
    assert derive_dispatch_id(first).startswith("BROKER-DIS-")
    other = _projection(action=_action(action_id="h3-act-2"))
    assert derive_dispatch_id(first) != derive_dispatch_id(other)


def _dispatch_result(**overrides: Any) -> dict[str, Any]:
    base = {
        "outcome": "completed",
        "executable_action_id": "h3-act-1",
        "executable_action_sha256": "a" * 64,
        "approval_id": "APPROVAL-h3-act-1",
        "reservation_id": "BROKER-RES-" + "0" * 32,
        "dispatch_id": "BROKER-DIS-" + "0" * 32,
        "state": BrokerActionState.COMPLETED,
        "idempotent_existing": False,
        "reason_code": None,
        "result_record_id": "H3RO-" + "0" * 32,
        "result_record_sha256": "c" * 64,
        "retained_relative_path": "h3_readonly_results/H3RO.h3readonly.json",
        "mutation_side_effect": False,
        "protected_surface_touched": False,
    }
    base.update(overrides)
    return base


def test_dispatch_result_contract_is_closed() -> None:
    assert BrokerReadonlyDispatchResult(**_dispatch_result()).outcome == "completed"
    # A fresh completed dispatch must bind a result record.
    with pytest.raises(ValidationError):
        BrokerReadonlyDispatchResult(**_dispatch_result(result_record_id=None))
    # An idempotent replay may return completed without re-surfacing the result.
    assert (
        BrokerReadonlyDispatchResult(
            **_dispatch_result(idempotent_existing=True, result_record_id=None)
        ).outcome
        == "completed"
    )
    # A rejected result carries no reservation/dispatch/result and needs a reason.
    assert (
        BrokerReadonlyDispatchResult(
            **_dispatch_result(
                outcome="rejected",
                state=BrokerActionState.REJECTED,
                reservation_id=None,
                dispatch_id=None,
                reason_code="a0_forbidden",
                result_record_id=None,
                result_record_sha256=None,
                retained_relative_path=None,
            )
        ).outcome
        == "rejected"
    )
    # mutation_side_effect can never be True.
    with pytest.raises(ValidationError):
        BrokerReadonlyDispatchResult(**_dispatch_result(mutation_side_effect=True))
