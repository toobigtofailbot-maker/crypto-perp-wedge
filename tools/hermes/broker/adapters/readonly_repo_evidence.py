"""The one structurally read-only H3-1 adapter.

This adapter is deliberately minimal and read-only. It has no network, socket,
HTTP, child-process, shell, filesystem *write*, canonical-writer, workflow-engine, Codex,
Governor, MCP, runtime/paper/live, OMS/risk/reconciliation, exchange/order/capital,
environment-mutation, randomness, uuid, database, or retry surface.

It reads only committed repo evidence at the bound repo SHA -- specifically the
committed ``docs/status_entries/WP-HERMES-*.md`` files -- and returns a deterministic
structured summary record. Every file access is read-only (``O_RDONLY``),
symlink/reparse-guarded, path-escape-guarded, and byte/count-bounded. The adapter
never creates, writes, truncates, renames, or deletes any path.
"""

from __future__ import annotations

import hashlib
import os
import stat
from pathlib import Path

from ..h3_readonly import (
    READONLY_ADAPTER_ID,
    READONLY_ADAPTER_VERSION,
    READONLY_FILE_BYTES_EXCEEDED_REASON,
    READONLY_FILE_COUNT_EXCEEDED_REASON,
    READONLY_RESULT_SCHEMA_VERSION,
    H3EvidenceEntry,
    H3ReadonlyProjection,
    H3ReadonlyResultRecord,
    derive_result_record_id,
)

ADAPTER_ID = READONLY_ADAPTER_ID
ADAPTER_VERSION = READONLY_ADAPTER_VERSION
FILE_ATTRIBUTE_REPARSE_POINT = 0x0400


class ReadonlyAdapterError(RuntimeError):
    """Fail-closed structural safety refusal; never a silent success."""


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
            raise ReadonlyAdapterError(f"evidence path traverses a reparse point: {cursor}")


def _read_regular_file_bytes(path: Path, *, max_bytes: int) -> bytes | None:
    """Read one regular file read-only, or return None if it exceeds the byte cap."""

    if _is_reparse_or_symlink(path):
        raise ReadonlyAdapterError("evidence file must not be a symlink or reparse point")
    try:
        info = path.stat(follow_symlinks=False)
    except FileNotFoundError as exc:  # pragma: no cover - guarded by enumeration
        raise ReadonlyAdapterError("evidence file vanished during read") from exc
    if not stat.S_ISREG(info.st_mode):
        raise ReadonlyAdapterError("evidence file must be a regular file")
    if info.st_size > max_bytes:
        return None
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0)
    descriptor = os.open(path, flags)
    try:
        with os.fdopen(descriptor, "rb", closefd=True) as handle:
            data = handle.read(max_bytes + 1)
    except BaseException:  # pragma: no cover - defensive close
        os.close(descriptor)
        raise
    if len(data) > max_bytes:
        return None
    return data


def _resolve_evidence_root(repo_root: Path, evidence_root_relpath: str) -> Path:
    root = Path(os.path.abspath(repo_root))
    _assert_direct_components(root)
    if not root.is_dir() or _is_reparse_or_symlink(root):
        raise ReadonlyAdapterError("repo root must be an existing direct directory")
    evidence_root = Path(os.path.abspath(root / evidence_root_relpath))
    if evidence_root.resolve().parent != root.resolve() and not _is_within(evidence_root, root):
        raise ReadonlyAdapterError("evidence root escaped the repo root")
    _assert_direct_components(evidence_root)
    if not evidence_root.is_dir() or _is_reparse_or_symlink(evidence_root):
        raise ReadonlyAdapterError("evidence root is not a direct regular directory")
    return evidence_root


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True


def readonly_repo_evidence(
    projection: H3ReadonlyProjection,
    *,
    dispatch_id: str,
    repo_root: Path,
) -> H3ReadonlyResultRecord:
    """Return the deterministic read-only evidence summary for one projection.

    Only reads occur. The repo working tree is pinned to the bound repo SHA by the
    upstream broker verification (``action.repo_sha == current_repo_sha``); this
    function trusts that gate and never spawns a child process or touches git objects.
    """

    if not isinstance(projection, H3ReadonlyProjection):
        raise TypeError("the H3-1 read-only adapter accepts only an H3ReadonlyProjection")
    params = projection.projected_parameters
    evidence_root = _resolve_evidence_root(repo_root, params.evidence_root_relpath)
    repo_abs = Path(os.path.abspath(repo_root))

    matched: list[Path] = []
    for child in sorted(evidence_root.iterdir(), key=lambda item: item.name):
        name = child.name
        if not (name.startswith(params.filename_prefix) and name.endswith(params.filename_suffix)):
            continue
        if _is_reparse_or_symlink(child):
            raise ReadonlyAdapterError("evidence file must not be a symlink or reparse point")
        if not child.is_file():
            continue
        matched.append(child)

    if len(matched) > params.max_files:
        return _failed_record(
            projection, dispatch_id, reason_code=READONLY_FILE_COUNT_EXCEEDED_REASON
        )

    entries: list[H3EvidenceEntry] = []
    total = 0
    for path in matched:
        data = _read_regular_file_bytes(path, max_bytes=params.max_file_bytes)
        if data is None:
            return _failed_record(
                projection, dispatch_id, reason_code=READONLY_FILE_BYTES_EXCEEDED_REASON
            )
        relpath = path.resolve().relative_to(repo_abs.resolve()).as_posix()
        entries.append(
            H3EvidenceEntry(
                relpath=relpath,
                byte_size=len(data),
                sha256=hashlib.sha256(data).hexdigest(),
            )
        )
        total += len(data)

    frozen = tuple(entries)
    return H3ReadonlyResultRecord(
        result_schema_version=READONLY_RESULT_SCHEMA_VERSION,
        result_record_id=derive_result_record_id(projection, dispatch_id, frozen),
        executable_action_id=projection.executable_action_id,
        executable_action_sha256=projection.executable_action_sha256,
        approval_id=projection.approval_id,
        reservation_id=projection.reservation_id,
        dispatch_id=dispatch_id,
        repo_sha=projection.repo_sha,
        action_type=projection.action_type,
        adapter_id=ADAPTER_ID,
        adapter_version=ADAPTER_VERSION,
        projection_sha256=projection.projection_sha256,
        evidence_root_relpath=params.evidence_root_relpath,
        entries=frozen,
        file_count=len(frozen),
        total_byte_size=total,
        outcome="completed",
        reason_code=None,
        mutation_side_effect=False,
        protected_surface_touched=False,
        network_access=False,
        child_process_spawned=False,
        wrote_repo_or_canonical=False,
    )


def _failed_record(
    projection: H3ReadonlyProjection,
    dispatch_id: str,
    *,
    reason_code: str,
) -> H3ReadonlyResultRecord:
    return H3ReadonlyResultRecord(
        result_schema_version=READONLY_RESULT_SCHEMA_VERSION,
        result_record_id=derive_result_record_id(projection, dispatch_id, ()),
        executable_action_id=projection.executable_action_id,
        executable_action_sha256=projection.executable_action_sha256,
        approval_id=projection.approval_id,
        reservation_id=projection.reservation_id,
        dispatch_id=dispatch_id,
        repo_sha=projection.repo_sha,
        action_type=projection.action_type,
        adapter_id=ADAPTER_ID,
        adapter_version=ADAPTER_VERSION,
        projection_sha256=projection.projection_sha256,
        evidence_root_relpath=projection.projected_parameters.evidence_root_relpath,
        entries=(),
        file_count=0,
        total_byte_size=0,
        outcome="failed",
        reason_code=reason_code,
        mutation_side_effect=False,
        protected_surface_touched=False,
        network_access=False,
        child_process_spawned=False,
        wrote_repo_or_canonical=False,
    )
