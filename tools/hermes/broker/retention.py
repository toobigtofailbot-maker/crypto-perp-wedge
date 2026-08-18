"""Operator-only stable retention for inert H2.5 prepared artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import TypeAdapter

from tools.hermes.prepare.models import PreparedPayload, PreparedPayloadBase
from tools.hermes.prepare.serialization import canonical_json_bytes

ARTIFACT_ROOT_ENV = "HERMES_BROKER_ARTIFACT_ROOT"
MAX_PREPARED_RECORD_BYTES = 2_000_000
PREPARED_ID_RE = re.compile(r"^HERMES-PREP-[0-9]{8}T[0-9]{6}Z-[0-9a-f]{16}$")
PREPARED_ADAPTER = TypeAdapter(PreparedPayload)
FILE_ATTRIBUTE_REPARSE_POINT = 0x0400

_OUTER_KEYS = frozenset(
    {
        "schema_version",
        "prepared_record_id",
        "created_at_utc",
        "source",
        "prepared_payload_type",
        "prepared_payload",
        "prepared_payload_sha256",
        "hash_scope",
        "canonicalization",
        "human_review_required",
        "not_authority",
        "automatic_consumers",
        "self_approval",
        "direct_execution",
        "approval_token_eligible",
        "broker_eligible",
        "dispatch_eligible",
        "authority",
    }
)
_SOURCE_KEYS = frozenset(
    {
        "system",
        "session_id",
        "repo_sha",
        "branch",
        "source_proposal_id",
        "source_proposal_content_sha256",
        "evidence_refs",
    }
)
_NON_AUTHORITY = {
    "not_repo_truth": True,
    "not_scientific_truth": True,
    "not_canonical_evidence": True,
    "not_candidate_or_promotion_authority": True,
    "not_dispatch_or_execution_authority": True,
    "not_runtime_or_risk_authority": True,
}


class RetentionError(RuntimeError):
    """Fail-closed stable-retention error."""


@dataclass(frozen=True)
class VerifiedPreparedArtifact:
    path: Path
    raw_bytes: bytes
    record: dict[str, Any]
    payload: PreparedPayloadBase
    prepared_payload_sha256: str


@dataclass(frozen=True)
class RetentionReceipt:
    receipt_schema_version: str
    prepared_record_id: str
    prepared_payload_sha256: str
    source_byte_sha256: str
    retained_byte_sha256: str
    retained_relative_path: str
    retained_at: str
    exact_source_bytes_preserved: bool
    exclusive_create: bool
    file_fsync: bool
    directory_fsync: str
    not_authority: bool
    not_approval: bool
    broker_decision_created: bool
    dispatch_request_created: bool

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


def _is_reparse_or_symlink(path: Path) -> bool:
    try:
        result = os.lstat(path)
    except FileNotFoundError:
        return False
    attributes = getattr(result, "st_file_attributes", 0)
    return stat.S_ISLNK(result.st_mode) or bool(attributes & FILE_ATTRIBUTE_REPARSE_POINT)


def _assert_existing_path_components_are_direct(path: Path) -> None:
    absolute = Path(os.path.abspath(path))
    cursor = Path(absolute.anchor)
    for part in absolute.parts[1:]:
        cursor /= part
        if cursor.exists() and _is_reparse_or_symlink(cursor):
            raise RetentionError(f"path traverses a symlink, junction, or reparse point: {cursor}")


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _validate_prepared_id(prepared_record_id: str) -> None:
    if PREPARED_ID_RE.fullmatch(prepared_record_id) is None:
        raise RetentionError("prepared_record_id is not a fixed H2.5 identity")


def _read_regular_file(path: Path, *, max_bytes: int) -> bytes:
    _assert_existing_path_components_are_direct(path)
    if _is_reparse_or_symlink(path):
        raise RetentionError("prepared artifact must not be a symlink or reparse point")
    try:
        info = path.stat(follow_symlinks=False)
    except FileNotFoundError as exc:
        raise RetentionError("prepared artifact is absent") from exc
    if not stat.S_ISREG(info.st_mode):
        raise RetentionError("prepared artifact must be a regular file")
    if info.st_size > max_bytes:
        raise RetentionError("prepared artifact exceeds the fixed byte limit")
    return path.read_bytes()


def verify_prepared_bytes(
    raw_bytes: bytes,
    *,
    path: Path,
    expected_prepared_record_id: str,
) -> VerifiedPreparedArtifact:
    """Validate the exact merged H2.5 outer and nested inert contract."""

    if len(raw_bytes) > MAX_PREPARED_RECORD_BYTES:
        raise RetentionError("prepared artifact exceeds the fixed byte limit")
    try:
        record = json.loads(raw_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RetentionError("prepared artifact is not valid UTF-8 JSON") from exc
    if not isinstance(record, dict) or frozenset(record) != _OUTER_KEYS:
        raise RetentionError("prepared artifact outer record is not the closed H2.5 shape")
    if record.get("schema_version") != "hermes_prepared_outbox_v1":
        raise RetentionError("prepared artifact has the wrong H2.5 outer schema")
    if record.get("prepared_record_id") != expected_prepared_record_id:
        raise RetentionError("prepared artifact identity does not match its fixed filename")
    source = record.get("source")
    if not isinstance(source, dict) or frozenset(source) != _SOURCE_KEYS:
        raise RetentionError("prepared artifact source envelope is invalid")
    if source.get("system") != "hermes" or not isinstance(source.get("branch"), str):
        raise RetentionError("prepared artifact source envelope is not Hermes-produced")
    try:
        payload = PREPARED_ADAPTER.validate_python(record.get("prepared_payload"))
    except Exception as exc:
        raise RetentionError("nested H2.5 prepared payload is invalid") from exc
    nested = payload.model_dump(mode="json")
    if record.get("prepared_payload") != nested:
        raise RetentionError("outer prepared payload is not the exact validated H2.5 object")
    expected_source = {
        "system": "hermes",
        "session_id": payload.source_session_id,
        "repo_sha": payload.repo_sha,
        "branch": source["branch"],
        "source_proposal_id": payload.source_proposal_id,
        "source_proposal_content_sha256": payload.source_proposal_content_sha256,
        "evidence_refs": list(payload.evidence_refs),
    }
    if (
        source != expected_source
        or record.get("prepared_payload_type") != payload.prepared_payload_type
    ):
        raise RetentionError("prepared outer/source fields conflict with the nested payload")
    inert_fields = {
        "human_review_required": True,
        "not_authority": True,
        "automatic_consumers": [],
        "self_approval": False,
        "direct_execution": False,
        "approval_token_eligible": False,
        "broker_eligible": False,
        "dispatch_eligible": False,
        "authority": _NON_AUTHORITY,
    }
    if any(record.get(key) != value for key, value in inert_fields.items()):
        raise RetentionError("prepared artifact inert authority fields are invalid")
    if record.get("hash_scope") != (
        "canonical bytes of prepared_payload only; outer metadata excluded"
    ):
        raise RetentionError("prepared artifact hash scope is invalid")
    if record.get("canonicalization") != {
        "algorithm": "hermes_canonical_json_v1",
        "encoding": "UTF-8",
        "key_order": "lexicographic",
        "newline": "LF",
        "trailing_newline_count": 1,
    }:
        raise RetentionError("prepared artifact canonicalization declaration is invalid")
    digest = hashlib.sha256(canonical_json_bytes(payload)).hexdigest()
    if record.get("prepared_payload_sha256") != digest:
        raise RetentionError("prepared_payload_sha256 does not match the exact H2.5 serializer")
    if raw_bytes != canonical_json_bytes(record):
        raise RetentionError("prepared outer record bytes are not canonical H2.5 bytes")
    return VerifiedPreparedArtifact(
        path=path,
        raw_bytes=raw_bytes,
        record=record,
        payload=payload,
        prepared_payload_sha256=digest,
    )


class BrokerArtifactStore:
    """Stable, external, no-overwrite store used only for prepared-artifact verification."""

    def __init__(
        self,
        root: Path,
        *,
        repository_root: Path,
        active_worktree_root: Path,
    ) -> None:
        if root is None:
            raise RetentionError("the stable broker artifact root must be explicitly supplied")
        self.root = Path(os.path.abspath(root))
        self.forbidden_roots = tuple(
            Path(os.path.abspath(item)).resolve()
            for item in (repository_root, active_worktree_root)
        )
        self._validate_external_root()

    @classmethod
    def from_environment(
        cls,
        *,
        repository_root: Path,
        active_worktree_root: Path,
    ) -> BrokerArtifactStore:
        value = os.environ.get(ARTIFACT_ROOT_ENV)
        if not value:
            raise RetentionError(f"{ARTIFACT_ROOT_ENV} must be explicitly supplied")
        return cls(
            Path(value),
            repository_root=repository_root,
            active_worktree_root=active_worktree_root,
        )

    @property
    def prepared_root(self) -> Path:
        return self.root / "prepared"

    def _validate_external_root(self) -> None:
        _assert_existing_path_components_are_direct(self.root)
        resolved = self.root.resolve()
        if any(_is_within(resolved, forbidden) for forbidden in self.forbidden_roots):
            raise RetentionError("stable broker artifact root must be outside repository/worktrees")
        if _is_reparse_or_symlink(self.root):
            raise RetentionError("stable broker artifact root must not be a reparse point")

    def _prepare_root(self) -> None:
        self._validate_external_root()
        self.prepared_root.mkdir(parents=True, exist_ok=True)
        self._validate_existing_prepared_root()

    def _validate_existing_prepared_root(self) -> None:
        self._validate_external_root()
        _assert_existing_path_components_are_direct(self.prepared_root)
        if not self.prepared_root.is_dir() or _is_reparse_or_symlink(self.prepared_root):
            raise RetentionError("stable prepared root is not a direct regular directory")

    def retained_path(self, prepared_record_id: str) -> Path:
        _validate_prepared_id(prepared_record_id)
        return self.prepared_root / f"{prepared_record_id}.prepared.json"

    def verify_retained(self, prepared_record_id: str) -> VerifiedPreparedArtifact:
        # Verification is read-only: a missing store is rejected, never created.
        self._validate_existing_prepared_root()
        path = self.retained_path(prepared_record_id)
        raw = _read_regular_file(path, max_bytes=MAX_PREPARED_RECORD_BYTES)
        if path.resolve().parent != self.prepared_root.resolve():
            raise RetentionError("retained artifact escaped the fixed prepared root")
        return verify_prepared_bytes(
            raw,
            path=path,
            expected_prepared_record_id=prepared_record_id,
        )

    def retain_from_outbox(
        self,
        *,
        source_outbox_root: Path,
        prepared_record_id: str,
        clock: datetime | None = None,
    ) -> RetentionReceipt:
        """Operator-only exact-byte crossing; produces no approval or broker decision."""

        _validate_prepared_id(prepared_record_id)
        source_root = Path(os.path.abspath(source_outbox_root))
        _assert_existing_path_components_are_direct(source_root)
        if not source_root.is_dir() or _is_reparse_or_symlink(source_root):
            raise RetentionError("source outbox root must be an existing direct directory")
        source_path = source_root / f"{prepared_record_id}.prepared.json"
        if source_path.resolve().parent != source_root.resolve():
            raise RetentionError("source artifact escaped the fixed outbox root")
        source_bytes = _read_regular_file(source_path, max_bytes=MAX_PREPARED_RECORD_BYTES)
        source = verify_prepared_bytes(
            source_bytes,
            path=source_path,
            expected_prepared_record_id=prepared_record_id,
        )

        self._prepare_root()
        destination = self.retained_path(prepared_record_id)
        if destination.exists() or _is_reparse_or_symlink(destination):
            raise RetentionError("retained artifact destination already exists")
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0)
        try:
            descriptor = os.open(destination, flags, 0o600)
        except FileExistsError as exc:
            raise RetentionError("retained artifact destination already exists") from exc
        with os.fdopen(descriptor, "wb", closefd=True) as handle:
            handle.write(source.raw_bytes)
            handle.flush()
            os.fsync(handle.fileno())

        directory_fsync = "unsupported_on_windows"
        if os.name != "nt":
            directory_flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
            directory_descriptor = os.open(self.prepared_root, directory_flags)
            try:
                os.fsync(directory_descriptor)
            finally:
                os.close(directory_descriptor)
            directory_fsync = "completed"

        retained = self.verify_retained(prepared_record_id)
        if retained.raw_bytes != source.raw_bytes:
            raise RetentionError("retained artifact bytes differ from exact source bytes")
        timestamp = (clock or datetime.now(UTC)).astimezone(UTC)
        source_digest = hashlib.sha256(source.raw_bytes).hexdigest()
        retained_digest = hashlib.sha256(retained.raw_bytes).hexdigest()
        return RetentionReceipt(
            receipt_schema_version="hermes_broker_retention_receipt_v1",
            prepared_record_id=prepared_record_id,
            prepared_payload_sha256=retained.prepared_payload_sha256,
            source_byte_sha256=source_digest,
            retained_byte_sha256=retained_digest,
            retained_relative_path=f"prepared/{destination.name}",
            retained_at=timestamp.isoformat(timespec="seconds").replace("+00:00", "Z"),
            exact_source_bytes_preserved=source_digest == retained_digest,
            exclusive_create=True,
            file_fsync=True,
            directory_fsync=directory_fsync,
            not_authority=True,
            not_approval=True,
            broker_decision_created=False,
            dispatch_request_created=False,
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="Retain one inert H2.5 prepared artifact")
    parser.add_argument("--source-outbox-root", required=True, type=Path)
    parser.add_argument("--prepared-record-id", required=True)
    parser.add_argument("--artifact-root", required=True, type=Path)
    parser.add_argument("--repository-root", required=True, type=Path)
    parser.add_argument("--worktree-root", required=True, type=Path)
    args = parser.parse_args()
    store = BrokerArtifactStore(
        args.artifact_root,
        repository_root=args.repository_root,
        active_worktree_root=args.worktree_root,
    )
    receipt = store.retain_from_outbox(
        source_outbox_root=args.source_outbox_root,
        prepared_record_id=args.prepared_record_id,
    )
    print(json.dumps(receipt.to_dict(), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
