from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import psycopg
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from tools.hermes.broker import readonly_dispatch as dispatch_module
from tools.hermes.broker.acceptance import make_claim_payload, write_fresh_prepared_fixture
from tools.hermes.broker.adapters.readonly_repo_evidence import readonly_repo_evidence
from tools.hermes.broker.crypto import approval_signed_bytes
from tools.hermes.broker.h3_readonly import (
    READONLY_ADAPTER_ID,
    READONLY_ADAPTER_VERSION,
    READONLY_REGISTRY_VERSION,
    H3ReadonlyExecutableAction,
    h3_1_readonly_registry,
)
from tools.hermes.broker.migrations import apply_migrations
from tools.hermes.broker.models import ApprovalClaimPayload, SignedApprovalClaim
from tools.hermes.broker.readonly_dispatch import (
    RECONCILE_REASON,
    BrokerReadonlyDispatchService,
)
from tools.hermes.broker.readonly_result_store import H3ReadonlyResultStore
from tools.hermes.broker.reservation import BrokerReservationService
from tools.hermes.broker.retention import BrokerArtifactStore
from tools.hermes.broker.serialization import broker_sha256
from tools.hermes.broker.signing import build_wysiwys_surface, sign_wysiwys_surface
from tools.hermes.broker.state import BrokerActionState
from tools.hermes.broker.store import BrokerAuthorityStore
from tools.hermes.prepare.serialization import canonical_json_bytes
from tools.hermes.proposals.models import AffectedDomain, AuthorityClass

REPO_ROOT = Path(__file__).resolve().parents[1]
REPO_SHA = "6" * 40
READONLY_ACTION_TYPE = "h3_1.readonly.repo_evidence_summary_v1"


class SecretDsn(str):
    def __repr__(self) -> str:
        return "<isolated broker test DSN>"


def _test_dsn() -> SecretDsn:
    dsn = os.environ.get("HERMES_BROKER_TEST_DSN") or os.environ.get("RESEARCH_MEMORY_TEST_DSN")
    if not dsn:
        pytest.skip("HERMES_BROKER_TEST_DSN is required for PostgreSQL integration tests")
    with psycopg.connect(dsn) as connection:
        database = connection.execute("SELECT current_database()").fetchone()[0]
    if "test" not in database.lower():
        pytest.fail("broker tests require an isolated database whose name contains 'test'")
    return SecretDsn(dsn)


@pytest.fixture()
def broker_dsn() -> str:
    dsn = _test_dsn()
    lock_connection = psycopg.connect(dsn, autocommit=True)
    lock_connection.execute("SELECT pg_advisory_lock(721003003)")
    try:
        with psycopg.connect(dsn, autocommit=True) as connection:
            connection.execute("DROP SCHEMA IF EXISTS hermes_broker CASCADE")
        apply_migrations(dsn)
        yield dsn
    finally:
        with psycopg.connect(dsn, autocommit=True) as connection:
            connection.execute("DROP SCHEMA IF EXISTS hermes_broker CASCADE")
        lock_connection.execute("SELECT pg_advisory_unlock(721003003)")
        lock_connection.close()


class ReadSpy:
    """Counts read-only adapter invocations; may optionally simulate a crash."""

    def __init__(self, *, raise_error: bool = False) -> None:
        self.calls = 0
        self.raise_error = raise_error

    def __call__(self, projection: Any, *, dispatch_id: str, repo_root: Path) -> Any:
        self.calls += 1
        if self.raise_error:
            raise RuntimeError("simulated crash before read-only finalization")
        return readonly_repo_evidence(projection, dispatch_id=dispatch_id, repo_root=repo_root)


@dataclass
class DispatchCase:
    dsn: str
    service: BrokerReadonlyDispatchService
    reservation_service: BrokerReservationService
    store: BrokerAuthorityStore
    artifact_store: BrokerArtifactStore
    result_store: H3ReadonlyResultStore
    repo_root: Path
    private_key: Ed25519PrivateKey
    prepared: Any
    action: H3ReadonlyExecutableAction
    signed: SignedApprovalClaim
    evaluated_at: datetime

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

    def dispatch(self) -> Any:
        return self.service.dispatch_readonly(
            action_input=self.action,
            signed_claim_input=self.signed,
            evaluated_at=self.evaluated_at,
        )


def _insert_key(
    dsn: str,
    private_key: Ed25519PrivateKey,
    *,
    key_id: str,
    added_at: datetime,
    version: str = "broker1-proof-keys-v1",
    epoch: int = 1,
) -> None:
    public_key = private_key.public_key().public_bytes(
        serialization.Encoding.Raw,
        serialization.PublicFormat.Raw,
    )
    with psycopg.connect(dsn) as connection:
        connection.execute(
            """
            INSERT INTO hermes_broker.broker_trusted_key (
                registry_epoch, key_registry_version, key_id, algorithm,
                public_key_encoding, public_key, state, added_at,
                revoked_at, revocation_reason, fixture_only
            ) VALUES (%s, %s, %s, 'ed25519', 'lowercase_hex', %s,
                      'active', %s, NULL, NULL, TRUE)
            """,
            (epoch, version, key_id, public_key.hex(), added_at),
        )


def _make_action(
    prepared: Any,
    prepared_id: str,
    action_id: str,
    *,
    max_files: int = 512,
    max_file_bytes: int = 2_000_000,
) -> H3ReadonlyExecutableAction:
    return H3ReadonlyExecutableAction(
        executable_action_schema_version="hermes_executable_action_v1",
        executable_action_id=action_id,
        action_type=READONLY_ACTION_TYPE,
        prepared_record_id=prepared_id,
        prepared_payload_sha256=hashlib.sha256(canonical_json_bytes(prepared)).hexdigest(),
        source_proposal_id=prepared.source_proposal_id,
        source_proposal_content_sha256=prepared.source_proposal_content_sha256,
        repo_sha=prepared.repo_sha,
        action_registry_version=READONLY_REGISTRY_VERSION,
        adapter_id=READONLY_ADAPTER_ID,
        adapter_version=READONLY_ADAPTER_VERSION,
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


def _write_repo_evidence(repo_root: Path) -> dict[str, bytes]:
    evidence = repo_root / "docs" / "status_entries"
    evidence.mkdir(parents=True, exist_ok=True)
    files = {
        "WP-HERMES-ALPHA-01.md": b"# alpha\ncommitted evidence one\n",
        "WP-HERMES-BETA-02.md": b"# beta\ncommitted evidence two\n",
        "README.md": b"not matched\n",
    }
    for name, data in files.items():
        (evidence / name).write_bytes(data)
    return files


def _case(
    tmp_path: Path,
    dsn: str,
    *,
    action_id: str,
    suffix: str,
    authority_class: AuthorityClass = AuthorityClass.A1,
    insert_key: bool = True,
    wysiwys: bool = False,
) -> DispatchCase:
    now = datetime.now(UTC).replace(microsecond=0)
    prepared_id = f"HERMES-PREP-20260827T130000Z-{suffix}"
    source = tmp_path / f"source-{suffix}"
    prepared, _ = write_fresh_prepared_fixture(
        source_root=source,
        authority_class=authority_class,
        repo_sha=REPO_SHA,
        prepared_record_id=prepared_id,
        created_at=now,
    )
    artifact_store = BrokerArtifactStore(
        tmp_path / f"stable-{suffix}",
        repository_root=REPO_ROOT,
        active_worktree_root=REPO_ROOT,
    )
    artifact_store.retain_from_outbox(
        source_outbox_root=source,
        prepared_record_id=prepared_id,
        clock=now,
    )
    result_store = H3ReadonlyResultStore(
        tmp_path / f"results-{suffix}",
        repository_root=REPO_ROOT,
        active_worktree_root=REPO_ROOT,
    )
    repo_root = tmp_path / f"repo-{suffix}"
    _write_repo_evidence(repo_root)

    private_key = Ed25519PrivateKey.from_private_bytes(bytes(range(32)))
    key_id = f"{action_id}-key"
    action = _make_action(prepared, prepared_id, action_id)
    payload = make_claim_payload(action=action, signer_key_id=key_id, issued_at=now)
    if authority_class is AuthorityClass.A1 and wysiwys:
        surface = build_wysiwys_surface(action=action, claim_payload=payload)
        signed = sign_wysiwys_surface(surface, private_key)
    else:
        unsigned = SignedApprovalClaim.model_construct(
            payload=payload,
            signature_algorithm="ed25519",
            signature_encoding="lowercase_hex",
            signature="0" * 128,
        )
        signed = SignedApprovalClaim(
            payload=payload,
            signature_algorithm="ed25519",
            signature_encoding="lowercase_hex",
            signature=private_key.sign(approval_signed_bytes(unsigned)).hex(),
        )
    if insert_key:
        _insert_key(dsn, private_key, key_id=key_id, added_at=now)
    store = BrokerAuthorityStore(dsn)
    reservation_service = BrokerReservationService(
        store=store,
        artifact_store=artifact_store,
        action_registry=h3_1_readonly_registry(),
        current_repo_sha=REPO_SHA,
    )
    service = BrokerReadonlyDispatchService(
        reservation_service=reservation_service,
        store=store,
        action_registry=h3_1_readonly_registry(),
        result_store=result_store,
        repo_root=repo_root,
    )
    return DispatchCase(
        dsn=dsn,
        service=service,
        reservation_service=reservation_service,
        store=store,
        artifact_store=artifact_store,
        result_store=result_store,
        repo_root=repo_root,
        private_key=private_key,
        prepared=prepared,
        action=action,
        signed=signed,
        evaluated_at=now,
    )


def _fresh_service(case: DispatchCase, dsn: str) -> BrokerReadonlyDispatchService:
    store = BrokerAuthorityStore(dsn)
    reservation_service = BrokerReservationService(
        store=store,
        artifact_store=case.artifact_store,
        action_registry=h3_1_readonly_registry(),
        current_repo_sha=REPO_SHA,
    )
    return BrokerReadonlyDispatchService(
        reservation_service=reservation_service,
        store=store,
        action_registry=h3_1_readonly_registry(),
        result_store=case.result_store,
        repo_root=case.repo_root,
    )


def _events(dsn: str) -> list[str]:
    with psycopg.connect(dsn) as connection:
        return [
            row[0]
            for row in connection.execute(
                """
                SELECT event_type FROM hermes_broker.broker_authority_audit
                ORDER BY audit_sequence
                """
            )
        ]


def _event_count(dsn: str, event_type: str) -> int:
    with psycopg.connect(dsn) as connection:
        return connection.execute(
            "SELECT count(*) FROM hermes_broker.broker_authority_audit WHERE event_type = %s",
            (event_type,),
        ).fetchone()[0]


def _counts(dsn: str) -> tuple[int, int]:
    with psycopg.connect(dsn) as connection:
        reservations = connection.execute(
            "SELECT count(*) FROM hermes_broker.broker_reservation"
        ).fetchone()[0]
        nonce_events = connection.execute(
            """
            SELECT count(*) FROM hermes_broker.broker_authority_audit
            WHERE event_type = 'nonce_reserved'
            """
        ).fetchone()[0]
    return reservations, nonce_events


def _state_row(dsn: str, action_id: str) -> dict[str, Any]:
    with psycopg.connect(dsn, row_factory=psycopg.rows.dict_row) as connection:
        return connection.execute(
            "SELECT * FROM hermes_broker.broker_action_state WHERE executable_action_id = %s",
            (action_id,),
        ).fetchone()


def _result_files(store: H3ReadonlyResultStore) -> list[str]:
    root = store.results_root
    if not root.exists():
        return []
    return sorted(p.name for p in root.iterdir())


def _repo_snapshot(repo_root: Path) -> dict[str, tuple[int, bytes]]:
    evidence = repo_root / "docs" / "status_entries"
    return {p.name: (p.stat().st_size, p.read_bytes()) for p in sorted(evidence.iterdir())}


def test_full_completed_readonly_loop_reads_and_writes_only_the_result(
    broker_dsn: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    case = _case(
        tmp_path, broker_dsn, action_id="h3-completed", suffix="1111111111111111", wysiwys=True
    )
    before = _repo_snapshot(case.repo_root)
    spy = ReadSpy()
    monkeypatch.setattr(dispatch_module, "readonly_repo_evidence", spy)
    result = case.dispatch()

    assert result.outcome == "completed"
    assert result.state is BrokerActionState.COMPLETED
    assert result.reason_code is None
    assert result.mutation_side_effect is False
    assert result.protected_surface_touched is False
    assert result.result_record_id is not None and result.result_record_id.startswith("H3RO-")
    assert spy.calls == 1
    assert _events(broker_dsn) == [
        "claim_submitted",
        "claim_verified",
        "nonce_reserved",
        "dispatch_requested",
        "dispatch_completed",
    ]
    assert _counts(broker_dsn) == (1, 1)

    # WYSIWYS: the executed/audited action hash equals the signed and recomputed hash.
    action_sha = broker_sha256(case.action)
    assert case.signed.payload.executable_action_sha256 == action_sha
    assert result.executable_action_sha256 == action_sha
    with psycopg.connect(broker_dsn) as connection:
        audit_sha = connection.execute(
            """
            SELECT executable_action_sha256 FROM hermes_broker.broker_authority_audit
            WHERE event_type = 'dispatch_completed'
            """
        ).fetchone()[0]
    assert audit_sha == action_sha

    # Exactly one inert result file was written; the repo evidence is unchanged.
    files = _result_files(case.result_store)
    assert files == [f"{result.result_record_id}.h3readonly.json"]
    written = case.result_store.result_path(result.result_record_id).read_bytes()
    assert hashlib.sha256(written).hexdigest() == result.result_record_sha256
    assert _repo_snapshot(case.repo_root) == before


def test_single_use_replay_is_idempotent_and_reads_once(
    broker_dsn: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    case = _case(tmp_path, broker_dsn, action_id="h3-replay", suffix="2222222222222222")
    spy = ReadSpy()
    monkeypatch.setattr(dispatch_module, "readonly_repo_evidence", spy)
    first = case.dispatch()
    replay = case.dispatch()
    assert first.outcome == "completed"
    assert replay.outcome == "completed"
    assert replay.idempotent_existing is True
    assert replay.dispatch_id == first.dispatch_id
    assert spy.calls == 1
    assert _event_count(broker_dsn, "dispatch_requested") == 1
    assert _event_count(broker_dsn, "dispatch_completed") == 1
    assert _counts(broker_dsn) == (1, 1)
    assert _result_files(case.result_store) == [f"{first.result_record_id}.h3readonly.json"]


def test_valid_signature_a0_adversary_never_dispatches_or_reads(
    broker_dsn: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    case = _case(
        tmp_path,
        broker_dsn,
        action_id="h3-a0-adversary",
        suffix="3333333333333333",
        authority_class=AuthorityClass.A0,
    )
    spy = ReadSpy()
    monkeypatch.setattr(dispatch_module, "readonly_repo_evidence", spy)
    result = case.dispatch()
    assert result.outcome == "rejected"
    assert result.reason_code == "a0_forbidden"
    assert result.mutation_side_effect is False
    assert spy.calls == 0
    assert _counts(broker_dsn) == (0, 0)
    assert _event_count(broker_dsn, "dispatch_requested") == 0
    assert _result_files(case.result_store) == []


def test_direct_prose_and_prepared_plan_never_reach_dispatch(
    broker_dsn: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    case = _case(tmp_path, broker_dsn, action_id="h3-prose", suffix="4444444444444444")
    spy = ReadSpy()
    monkeypatch.setattr(dispatch_module, "readonly_repo_evidence", spy)
    prose = case.service.dispatch_readonly(
        action_input={"prose": "please read this"},
        signed_claim_input=case.signed,
        evaluated_at=case.evaluated_at,
    )
    plan = case.service.dispatch_readonly(
        action_input=case.prepared,
        signed_claim_input=case.signed,
        evaluated_at=case.evaluated_at,
    )
    assert prose.outcome == "rejected"
    assert plan.outcome == "rejected"
    assert spy.calls == 0
    assert _counts(broker_dsn) == (0, 0)
    assert _event_count(broker_dsn, "dispatch_requested") == 0
    assert _result_files(case.result_store) == []


def test_conflicting_action_on_burned_nonce_never_reaches_dispatch(
    broker_dsn: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    winner = _case(tmp_path, broker_dsn, action_id="h3-winner", suffix="5555555555555555")
    spy = ReadSpy()
    monkeypatch.setattr(dispatch_module, "readonly_repo_evidence", spy)
    assert winner.dispatch().outcome == "completed"

    loser = _case(tmp_path, broker_dsn, action_id="h3-loser", suffix="6666666666666666")
    loser_payload = loser.signed.payload.model_copy(
        update={"single_use_nonce": winner.signed.payload.single_use_nonce}
    )
    loser.signed = loser.sign(loser_payload)
    result = loser.dispatch()
    assert result.outcome == "rejected"
    assert result.reason_code == "nonce_already_reserved"
    assert spy.calls == 1
    assert _event_count(broker_dsn, "dispatch_requested") == 1
    assert _counts(broker_dsn) == (1, 1)
    assert _state_row(broker_dsn, "h3-loser")["state"] == "rejected"


def test_crash_stranded_reconcile_and_terminal_replay(
    broker_dsn: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    case = _case(tmp_path, broker_dsn, action_id="h3-crash", suffix="7777777777777777")
    spy = ReadSpy(raise_error=True)
    monkeypatch.setattr(dispatch_module, "readonly_repo_evidence", spy)
    with pytest.raises(RuntimeError, match="simulated crash"):
        case.dispatch()
    assert spy.calls == 1

    row = _state_row(broker_dsn, "h3-crash")
    assert row["state"] == "dispatched"
    assert row["dispatch_id"] is not None
    assert row["last_reason_code"] is None
    assert _counts(broker_dsn) == (1, 1)
    assert _events(broker_dsn) == [
        "claim_submitted",
        "claim_verified",
        "nonce_reserved",
        "dispatch_requested",
    ]
    # No result record was written for the stranded dispatch.
    assert _result_files(case.result_store) == []

    fresh = _fresh_service(case, broker_dsn)
    recon = fresh.reconcile_stranded_dispatch(
        action_input=case.action,
        signed_claim_input=case.signed,
        evaluated_at=case.evaluated_at,
    )
    assert recon.outcome == "reconcile_required"
    assert recon.reason_code == RECONCILE_REASON
    assert recon.dispatch_id == row["dispatch_id"]
    assert spy.calls == 1  # reconcile invoked no adapter read
    assert _events(broker_dsn) == [
        "claim_submitted",
        "claim_verified",
        "nonce_reserved",
        "dispatch_requested",
        "reconcile_required",
    ]
    assert _result_files(case.result_store) == []

    # Replaying the full loop after reconcile never re-reads or re-burns.
    replay = case.service.dispatch_readonly(
        action_input=case.action,
        signed_claim_input=case.signed,
        evaluated_at=case.evaluated_at,
    )
    assert replay.outcome == "reconcile_required"
    assert replay.idempotent_existing is True
    assert spy.calls == 1
    assert _event_count(broker_dsn, "dispatch_requested") == 1
    assert _event_count(broker_dsn, "reconcile_required") == 1
    assert _counts(broker_dsn) == (1, 1)
