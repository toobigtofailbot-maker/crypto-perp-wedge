from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from tools.hermes.broker import retention
from tools.hermes.broker.acceptance import write_fresh_prepared_fixture
from tools.hermes.broker.retention import (
    ARTIFACT_ROOT_ENV,
    BrokerArtifactStore,
    RetentionError,
)
from tools.hermes.prepare.serialization import canonical_json_bytes
from tools.hermes.proposals.models import AuthorityClass

REPO_ROOT = Path(__file__).resolve().parents[1]
NOW = datetime(2026, 8, 17, 12, 0, tzinfo=UTC)
REPO_SHA = "2" * 40
PREPARED_ID = "HERMES-PREP-20260817T120000Z-1111111111111111"


def _source(tmp_path: Path, *, authority: AuthorityClass = AuthorityClass.A1) -> tuple[Path, Path]:
    root = tmp_path / "source"
    _payload, path = write_fresh_prepared_fixture(
        source_root=root,
        authority_class=authority,
        repo_sha=REPO_SHA,
        prepared_record_id=PREPARED_ID,
        created_at=NOW,
    )
    return root, path


def _store(tmp_path: Path) -> BrokerArtifactStore:
    return BrokerArtifactStore(
        tmp_path / "stable",
        repository_root=REPO_ROOT,
        active_worktree_root=REPO_ROOT,
    )


def test_exact_source_bytes_are_exclusive_fsynced_and_worktree_independent(
    tmp_path: Path,
) -> None:
    source_root, source_path = _source(tmp_path)
    source_bytes = source_path.read_bytes()
    store = _store(tmp_path)
    receipt = store.retain_from_outbox(
        source_outbox_root=source_root,
        prepared_record_id=PREPARED_ID,
        clock=NOW,
    )
    retained_path = store.retained_path(PREPARED_ID)
    assert retained_path.read_bytes() == source_bytes
    assert receipt.exact_source_bytes_preserved is True
    assert receipt.source_byte_sha256 == receipt.retained_byte_sha256
    assert receipt.file_fsync is True
    assert receipt.directory_fsync == (
        "unsupported_on_windows" if retention.os.name == "nt" else "completed"
    )
    assert receipt.not_authority is True and receipt.not_approval is True
    assert receipt.broker_decision_created is False
    with pytest.raises(RetentionError, match="already exists"):
        store.retain_from_outbox(
            source_outbox_root=source_root,
            prepared_record_id=PREPARED_ID,
            clock=NOW,
        )
    source_path.unlink()
    assert store.verify_retained(PREPARED_ID).prepared_payload_sha256 == (
        receipt.prepared_payload_sha256
    )


def test_stable_root_inside_repository_or_worktree_rejects() -> None:
    with pytest.raises(RetentionError, match="outside repository/worktrees"):
        BrokerArtifactStore(
            REPO_ROOT / "scratch" / "broker1-forbidden-root",
            repository_root=REPO_ROOT,
            active_worktree_root=REPO_ROOT,
        )


def test_environment_root_is_required(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(ARTIFACT_ROOT_ENV, raising=False)
    with pytest.raises(RetentionError, match=ARTIFACT_ROOT_ENV):
        BrokerArtifactStore.from_environment(
            repository_root=REPO_ROOT,
            active_worktree_root=REPO_ROOT,
        )


def test_read_only_lookup_does_not_create_a_missing_store(tmp_path: Path) -> None:
    root = tmp_path / "missing-stable"
    store = BrokerArtifactStore(
        root,
        repository_root=REPO_ROOT,
        active_worktree_root=REPO_ROOT,
    )
    with pytest.raises(RetentionError, match="stable prepared root"):
        store.verify_retained(PREPARED_ID)
    assert not root.exists()


def test_source_root_file_and_destination_reparse_cases_reject(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source_root, source_path = _source(tmp_path)
    store = _store(tmp_path)
    original = retention._is_reparse_or_symlink

    monkeypatch.setattr(
        retention,
        "_is_reparse_or_symlink",
        lambda path: path == source_root or original(path),
    )
    with pytest.raises(RetentionError, match="symlink|junction|reparse"):
        store.retain_from_outbox(
            source_outbox_root=source_root,
            prepared_record_id=PREPARED_ID,
        )

    monkeypatch.setattr(
        retention,
        "_is_reparse_or_symlink",
        lambda path: path == source_path or original(path),
    )
    with pytest.raises(RetentionError, match="symlink|junction|reparse"):
        store.retain_from_outbox(
            source_outbox_root=source_root,
            prepared_record_id=PREPARED_ID,
        )

    destination = store.prepared_root / f"{PREPARED_ID}.prepared.json"
    monkeypatch.setattr(
        retention,
        "_is_reparse_or_symlink",
        lambda path: path == destination or original(path),
    )
    with pytest.raises(RetentionError, match="already exists"):
        store.retain_from_outbox(
            source_outbox_root=source_root,
            prepared_record_id=PREPARED_ID,
        )


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (lambda record: record.update(schema_version="wrong"), "wrong H2.5 outer schema"),
        (lambda record: record["prepared_payload"].update(extra=True), "nested H2.5"),
        (lambda record: record.update(prepared_payload_sha256="0" * 64), "prepared_payload"),
        (lambda record: record.update(broker_eligible=True), "inert authority"),
        (lambda record: record["source"].update(repo_sha="0" * 40), "conflict"),
    ],
)
def test_malformed_outer_nested_hash_and_inert_state_reject(
    tmp_path: Path,
    mutation: object,
    message: str,
) -> None:
    source_root, source_path = _source(tmp_path)
    record = json.loads(source_path.read_text(encoding="utf-8"))
    mutation(record)  # type: ignore[operator]
    source_path.write_bytes(canonical_json_bytes(record))
    with pytest.raises(RetentionError, match=message):
        _store(tmp_path).retain_from_outbox(
            source_outbox_root=source_root,
            prepared_record_id=PREPARED_ID,
        )


def test_a0_permanence_must_remain_valid(tmp_path: Path) -> None:
    source_root, source_path = _source(tmp_path, authority=AuthorityClass.A0)
    record = json.loads(source_path.read_text(encoding="utf-8"))
    record["prepared_payload"]["permanent_non_executable"] = False
    source_path.write_bytes(canonical_json_bytes(record))
    with pytest.raises(RetentionError, match="nested H2.5"):
        _store(tmp_path).retain_from_outbox(
            source_outbox_root=source_root,
            prepared_record_id=PREPARED_ID,
        )


def test_traversal_bad_id_nonregular_and_oversized_reject(tmp_path: Path) -> None:
    source_root, source_path = _source(tmp_path)
    store = _store(tmp_path)
    for bad_id in ("../escape", "HERMES-PREP-invalid"):
        with pytest.raises(RetentionError, match="fixed H2.5 identity"):
            store.retain_from_outbox(
                source_outbox_root=source_root,
                prepared_record_id=bad_id,
            )
    source_path.unlink()
    source_path.mkdir()
    with pytest.raises(RetentionError, match="regular file"):
        store.retain_from_outbox(
            source_outbox_root=source_root,
            prepared_record_id=PREPARED_ID,
        )
    source_path.rmdir()
    source_path.write_bytes(b"x" * (retention.MAX_PREPARED_RECORD_BYTES + 1))
    with pytest.raises(RetentionError, match="byte limit"):
        store.retain_from_outbox(
            source_outbox_root=source_root,
            prepared_record_id=PREPARED_ID,
        )


def test_noncanonical_outer_bytes_reject_without_semantic_rewrite(tmp_path: Path) -> None:
    source_root, source_path = _source(tmp_path)
    record = json.loads(source_path.read_text(encoding="utf-8"))
    source_path.write_text(json.dumps(record, indent=2), encoding="utf-8")
    with pytest.raises(RetentionError, match="not canonical"):
        _store(tmp_path).retain_from_outbox(
            source_outbox_root=source_root,
            prepared_record_id=PREPARED_ID,
        )
