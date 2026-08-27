"""Inert, external, no-overwrite retention for one H3-1 read-only result record.

The read-only diagnostic mutates nothing in the repo or the canonical store. The
only artifact it produces -- the structured read-only result record -- is written
here, to a stable root that must live *outside* the repository and every worktree,
with exclusive-create no-overwrite semantics and a symlink/reparse guard. This is
the sole filesystem write in the H3-1 loop besides the broker's own durable audit.
"""

from __future__ import annotations

import hashlib
import os
import stat
from dataclasses import dataclass
from pathlib import Path

from .h3_readonly import H3ReadonlyResultRecord
from .serialization import broker_canonical_json_bytes

RESULT_ROOT_ENV = "HERMES_BROKER_H3_RESULT_ROOT"
MAX_RESULT_RECORD_BYTES = 4_000_000
FILE_ATTRIBUTE_REPARSE_POINT = 0x0400


class ResultStoreError(RuntimeError):
    """Fail-closed read-only-result retention error."""


@dataclass(frozen=True)
class ResultRetentionReceipt:
    receipt_schema_version: str
    result_record_id: str
    retained_relative_path: str
    retained_byte_sha256: str
    result_record_sha256: str
    exclusive_create: bool
    file_fsync: bool
    directory_fsync: str
    not_authority: bool
    wrote_repo_or_canonical: bool

    def to_dict(self) -> dict[str, object]:
        return self.__dict__.copy()


def _is_reparse_or_symlink(path: Path) -> bool:
    try:
        result = os.lstat(path)
    except FileNotFoundError:
        return False
    attributes = getattr(result, "st_file_attributes", 0)
    return stat.S_ISLNK(result.st_mode) or bool(attributes & FILE_ATTRIBUTE_REPARSE_POINT)


def _assert_direct_components(path: Path) -> None:
    absolute = Path(os.path.abspath(path))
    cursor = Path(absolute.anchor)
    for part in absolute.parts[1:]:
        cursor /= part
        if cursor.exists() and _is_reparse_or_symlink(cursor):
            raise ResultStoreError(f"result path traverses a reparse point: {cursor}")


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


class H3ReadonlyResultStore:
    """Stable external no-overwrite store for the inert read-only result record."""

    def __init__(
        self,
        root: Path,
        *,
        repository_root: Path,
        active_worktree_root: Path,
    ) -> None:
        if root is None:
            raise ResultStoreError("the stable read-only result root must be explicitly supplied")
        self.root = Path(os.path.abspath(root))
        self.forbidden_roots = tuple(
            Path(os.path.abspath(item)).resolve()
            for item in (repository_root, active_worktree_root)
        )
        self._validate_external_root()

    @property
    def results_root(self) -> Path:
        return self.root / "h3_readonly_results"

    def _validate_external_root(self) -> None:
        _assert_direct_components(self.root)
        resolved = self.root.resolve()
        if any(_is_within(resolved, forbidden) for forbidden in self.forbidden_roots):
            raise ResultStoreError("read-only result root must be outside repository/worktrees")
        if _is_reparse_or_symlink(self.root):
            raise ResultStoreError("read-only result root must not be a reparse point")

    def _prepare_results_root(self) -> None:
        self._validate_external_root()
        self.results_root.mkdir(parents=True, exist_ok=True)
        _assert_direct_components(self.results_root)
        if not self.results_root.is_dir() or _is_reparse_or_symlink(self.results_root):
            raise ResultStoreError("stable read-only result root is not a direct directory")

    def result_path(self, result_record_id: str) -> Path:
        if not (result_record_id and result_record_id.startswith("H3RO-")):
            raise ResultStoreError("result_record_id is not a fixed H3-1 result identity")
        return self.results_root / f"{result_record_id}.h3readonly.json"

    def write_result(self, record: H3ReadonlyResultRecord) -> ResultRetentionReceipt:
        """Write one result record exactly once; never overwrite an existing file."""

        if not isinstance(record, H3ReadonlyResultRecord):
            raise ResultStoreError("only an H3ReadonlyResultRecord may be retained")
        raw = broker_canonical_json_bytes(record)
        if len(raw) > MAX_RESULT_RECORD_BYTES:
            raise ResultStoreError("read-only result record exceeds the fixed byte limit")
        record_sha256 = hashlib.sha256(raw).hexdigest()

        self._prepare_results_root()
        destination = self.result_path(record.result_record_id)
        if destination.exists() or _is_reparse_or_symlink(destination):
            raise ResultStoreError("read-only result destination already exists")
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0)
        try:
            descriptor = os.open(destination, flags, 0o600)
        except FileExistsError as exc:
            raise ResultStoreError("read-only result destination already exists") from exc
        with os.fdopen(descriptor, "wb", closefd=True) as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())

        directory_fsync = "unsupported_on_windows"
        if os.name != "nt":
            directory_flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
            directory_descriptor = os.open(self.results_root, directory_flags)
            try:
                os.fsync(directory_descriptor)
            finally:
                os.close(directory_descriptor)
            directory_fsync = "completed"

        retained = destination.read_bytes()
        if retained != raw:
            raise ResultStoreError("retained read-only result bytes differ from source bytes")
        return ResultRetentionReceipt(
            receipt_schema_version="hermes_broker_h3_readonly_result_receipt_v1",
            result_record_id=record.result_record_id,
            retained_relative_path=f"h3_readonly_results/{destination.name}",
            retained_byte_sha256=hashlib.sha256(retained).hexdigest(),
            result_record_sha256=record_sha256,
            exclusive_create=True,
            file_fsync=True,
            directory_fsync=directory_fsync,
            not_authority=True,
            wrote_repo_or_canonical=False,
        )
