"""Protected synthetic-use KDAUTH crossing and lifecycle append capability.

This module creates no production authorization by itself.  Callers must supply
reviewed proposal bytes, their independent whole-file SHA-256, fresh crossing
identities, and the exact approving actor.
"""

from __future__ import annotations

import argparse
import copy
import ctypes
import hashlib
import json
import os
import re
import stat
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Mapping

from tools.canon_intake.dispatch_authorization import (
    AUDIT_PATH,
    DispatchAuthorizationError,
    _validate_dispatch_authorization_audit_raw,
    read_and_validate_dispatch_authorization_audit,
    repo_canonical_json_v1,
    validate_dispatch_authorization,
    validate_dispatch_authorization_for_consumption,
    validate_dispatch_authorization_candidate,
)
from tools.canon_intake.dispatch_authorization_reservation import (
    SCHEMA_VERSION as RESERVATION_SCHEMA_VERSION,
    WRITER_IDENTITY as RESERVATION_WRITER_IDENTITY,
    DispatchAuthorizationReservationError,
    DispatchAuthorizationReservationIntegrityCriticalError,
    append_dispatch_authorization_crossing_terminal_locked,
    dispatch_authorization_crossing_lock,
    reserve_dispatch_authorization_crossing_locked,
)


WRITER_IDENTITY = "dispatch_authorization_writer_v1"
ATTEMPT_ID_RE = re.compile(r"^KDAUTH-XING-[0-9]{8}-[A-Z0-9]{8}$")
SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
BINARY_FLAG = getattr(os, "O_BINARY", 0)
READ_CHUNK_SIZE = 1024 * 1024
LIFECYCLE_TERMINALS = {
    "authorization_superseded",
    "authorization_revoked",
    "authorization_consumed",
}
AUDIT_NON_AUTHORITY = {
    "lifecycle_history_only": True,
    "does_not_invoke_runner": True,
    "not_result_population_authority": True,
    "not_ranking_recommendation_authority": True,
    "not_candidate_readiness_promotion_authority": True,
    "not_runtime_paper_live_authority": True,
}
RESERVATION_NON_AUTHORITY = {
    "control_plane_integrity_history_only": True,
    "not_dispatch_authorization": True,
    "not_karl_approval": True,
    "not_kdauth_lifecycle_event": True,
    "does_not_create_dispatch": True,
    "does_not_create_execution_event": True,
    "does_not_invoke_runner": True,
    "not_result_population_authority": True,
    "not_ranking_recommendation_authority": True,
    "not_candidate_readiness_promotion_authority": True,
    "not_retry_recovery_authority": True,
    "not_scheduler_runtime_authority": True,
    "not_paper_live_authority": True,
    "not_oms_risk_reconciliation_authority": True,
    "not_broker_exchange_order_capital_authority": True,
}


class DispatchAuthorizationWriterError(ValueError):
    """Protected writer stopped before a complete committed crossing."""


class DispatchAuthorizationWriterIntegrityCriticalError(DispatchAuthorizationWriterError):
    """A post-reservation state is uncertain and requires operator inspection."""


def _digest(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _format_timestamp(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def _parse_timestamp(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise DispatchAuthorizationWriterError("timestamp must be timezone-aware RFC3339") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise DispatchAuthorizationWriterError("timestamp must be timezone-aware")
    return parsed


def _timestamp_after(previous: str) -> str:
    floor = _parse_timestamp(previous) + timedelta(microseconds=1)
    return _format_timestamp(max(_utc_now(), floor))


def _write_all(fd: int, raw: bytes) -> None:
    written = 0
    while written < len(raw):
        count = os.write(fd, raw[written:])
        if count <= 0:
            raise OSError("write returned no progress")
        written += count


def _read_all(fd: int) -> bytes:
    os.lseek(fd, 0, os.SEEK_SET)
    chunks = []
    while True:
        chunk = os.read(fd, READ_CHUNK_SIZE)
        if not chunk:
            return b"".join(chunks)
        chunks.append(chunk)


if os.name == "nt":
    import msvcrt
    from ctypes import wintypes

    _KERNEL32 = ctypes.WinDLL("kernel32", use_last_error=True)
    _NTDLL = ctypes.WinDLL("ntdll")
    _INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value

    _FILE_LIST_DIRECTORY = 0x0001
    _FILE_READ_DATA = 0x0001
    _FILE_WRITE_DATA = 0x0002
    _FILE_APPEND_DATA = 0x0004
    _FILE_READ_ATTRIBUTES = 0x0080
    _DELETE = 0x00010000
    _SYNCHRONIZE = 0x00100000
    _FILE_SHARE_ALL = 0x00000007
    _OPEN_EXISTING = 3
    _FILE_CREATE = 2
    _FILE_OPEN = 1
    _FILE_DIRECTORY_FILE = 0x00000001
    _FILE_SYNCHRONOUS_IO_NONALERT = 0x00000020
    _FILE_NON_DIRECTORY_FILE = 0x00000040
    _FILE_OPEN_FOR_BACKUP_INTENT = 0x00004000
    _FILE_OPEN_REPARSE_POINT = 0x00200000
    _FILE_FLAG_BACKUP_SEMANTICS = 0x02000000
    _FILE_ATTRIBUTE_DIRECTORY = 0x00000010
    _FILE_ATTRIBUTE_NORMAL = 0x00000080
    _FILE_ATTRIBUTE_REPARSE_POINT = 0x00000400
    _OBJ_CASE_INSENSITIVE = 0x00000040
    _FILE_DISPOSITION_INFO_CLASS = 4

    class _UnicodeString(ctypes.Structure):
        _fields_ = [
            ("Length", wintypes.USHORT),
            ("MaximumLength", wintypes.USHORT),
            ("Buffer", wintypes.LPWSTR),
        ]

    class _ObjectAttributes(ctypes.Structure):
        _fields_ = [
            ("Length", wintypes.ULONG),
            ("RootDirectory", wintypes.HANDLE),
            ("ObjectName", ctypes.POINTER(_UnicodeString)),
            ("Attributes", wintypes.ULONG),
            ("SecurityDescriptor", ctypes.c_void_p),
            ("SecurityQualityOfService", ctypes.c_void_p),
        ]

    class _IoStatusBlock(ctypes.Structure):
        _fields_ = [
            ("Status", ctypes.c_void_p),
            ("Information", ctypes.c_size_t),
        ]

    class _ByHandleFileInformation(ctypes.Structure):
        _fields_ = [
            ("dwFileAttributes", wintypes.DWORD),
            ("ftCreationTime", wintypes.FILETIME),
            ("ftLastAccessTime", wintypes.FILETIME),
            ("ftLastWriteTime", wintypes.FILETIME),
            ("dwVolumeSerialNumber", wintypes.DWORD),
            ("nFileSizeHigh", wintypes.DWORD),
            ("nFileSizeLow", wintypes.DWORD),
            ("nNumberOfLinks", wintypes.DWORD),
            ("nFileIndexHigh", wintypes.DWORD),
            ("nFileIndexLow", wintypes.DWORD),
        ]

    class _FileDispositionInfo(ctypes.Structure):
        _fields_ = [("DeleteFile", wintypes.BOOL)]

    _KERNEL32.CreateFileW.argtypes = [
        wintypes.LPCWSTR,
        wintypes.DWORD,
        wintypes.DWORD,
        ctypes.c_void_p,
        wintypes.DWORD,
        wintypes.DWORD,
        wintypes.HANDLE,
    ]
    _KERNEL32.CreateFileW.restype = wintypes.HANDLE
    _KERNEL32.GetFileInformationByHandle.argtypes = [
        wintypes.HANDLE,
        ctypes.POINTER(_ByHandleFileInformation),
    ]
    _KERNEL32.GetFileInformationByHandle.restype = wintypes.BOOL
    _KERNEL32.FlushFileBuffers.argtypes = [wintypes.HANDLE]
    _KERNEL32.FlushFileBuffers.restype = wintypes.BOOL
    _KERNEL32.SetFileInformationByHandle.argtypes = [
        wintypes.HANDLE,
        ctypes.c_int,
        ctypes.c_void_p,
        wintypes.DWORD,
    ]
    _KERNEL32.SetFileInformationByHandle.restype = wintypes.BOOL
    _KERNEL32.CloseHandle.argtypes = [wintypes.HANDLE]
    _KERNEL32.CloseHandle.restype = wintypes.BOOL
    _NTDLL.NtCreateFile.argtypes = [
        ctypes.POINTER(wintypes.HANDLE),
        wintypes.DWORD,
        ctypes.POINTER(_ObjectAttributes),
        ctypes.POINTER(_IoStatusBlock),
        ctypes.c_void_p,
        wintypes.ULONG,
        wintypes.ULONG,
        wintypes.ULONG,
        wintypes.ULONG,
        ctypes.c_void_p,
        wintypes.ULONG,
    ]
    _NTDLL.NtCreateFile.restype = wintypes.LONG
    _NTDLL.RtlNtStatusToDosError.argtypes = [wintypes.LONG]
    _NTDLL.RtlNtStatusToDosError.restype = wintypes.ULONG


def _win_close_handle(handle: int) -> None:
    if os.name == "nt" and handle:
        _KERNEL32.CloseHandle(handle)


def _win_file_information(handle: int) -> Any:
    info = _ByHandleFileInformation()
    if not _KERNEL32.GetFileInformationByHandle(handle, ctypes.byref(info)):
        raise ctypes.WinError(ctypes.get_last_error())
    return info


def _win_identity(handle: int) -> tuple[int, int, int]:
    info = _win_file_information(handle)
    return (
        int(info.dwVolumeSerialNumber),
        int(info.nFileIndexHigh),
        int(info.nFileIndexLow),
    )


def _win_require_type(handle: int, *, directory: bool, label: str) -> None:
    info = _win_file_information(handle)
    if info.dwFileAttributes & _FILE_ATTRIBUTE_REPARSE_POINT:
        raise OSError(f"{label} is a reparse point")
    is_directory = bool(info.dwFileAttributes & _FILE_ATTRIBUTE_DIRECTORY)
    if is_directory != directory:
        expected = "directory" if directory else "regular file"
        raise OSError(f"{label} is not a {expected}")


def _win_open_absolute_directory(path: Path, *, writable: bool) -> int:
    access = (
        _FILE_LIST_DIRECTORY
        | _FILE_READ_ATTRIBUTES
        | _SYNCHRONIZE
        | (_FILE_WRITE_DATA if writable else 0)
    )
    handle = _KERNEL32.CreateFileW(
        str(path),
        access,
        _FILE_SHARE_ALL,
        None,
        _OPEN_EXISTING,
        _FILE_FLAG_BACKUP_SEMANTICS | _FILE_OPEN_REPARSE_POINT,
        None,
    )
    if handle == _INVALID_HANDLE_VALUE:
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        _win_require_type(handle, directory=True, label=str(path))
    except Exception:
        _win_close_handle(handle)
        raise
    return int(handle)


def _win_open_relative_handle(
    parent_handle: int,
    name: str,
    *,
    access: int,
    disposition: int,
    directory: bool,
) -> int:
    encoded = name.encode("utf-16-le")
    buffer = ctypes.create_unicode_buffer(name)
    unicode_name = _UnicodeString(
        len(encoded),
        len(encoded) + 2,
        ctypes.cast(buffer, wintypes.LPWSTR),
    )
    attributes = _ObjectAttributes(
        ctypes.sizeof(_ObjectAttributes),
        parent_handle,
        ctypes.pointer(unicode_name),
        _OBJ_CASE_INSENSITIVE,
        None,
        None,
    )
    io_status = _IoStatusBlock()
    handle = wintypes.HANDLE()
    options = (
        _FILE_OPEN_REPARSE_POINT
        | _FILE_SYNCHRONOUS_IO_NONALERT
        | _FILE_OPEN_FOR_BACKUP_INTENT
        | (_FILE_DIRECTORY_FILE if directory else _FILE_NON_DIRECTORY_FILE)
    )
    status = _NTDLL.NtCreateFile(
        ctypes.byref(handle),
        access,
        ctypes.byref(attributes),
        ctypes.byref(io_status),
        None,
        _FILE_ATTRIBUTE_NORMAL,
        _FILE_SHARE_ALL,
        disposition,
        options,
        None,
        0,
    )
    if status < 0:
        error = int(_NTDLL.RtlNtStatusToDosError(status))
        raise ctypes.WinError(error)
    value = int(handle.value)
    try:
        _win_require_type(value, directory=directory, label=name)
    except Exception:
        _win_close_handle(value)
        raise
    return value


def _native_directory_chain(
    root: Path,
    relative: Path,
    *,
    writable_final: bool,
) -> tuple[int, tuple[int, ...]]:
    if relative.is_absolute() or any(part in {"", ".", ".."} for part in relative.parts):
        raise OSError("mutable parent must be lexical beneath repo root")
    if os.name == "nt":
        current = _win_open_absolute_directory(root, writable=writable_final and not relative.parts)
        try:
            for index, component in enumerate(relative.parts):
                final = index == len(relative.parts) - 1
                access = (
                    _FILE_LIST_DIRECTORY
                    | _FILE_READ_ATTRIBUTES
                    | _SYNCHRONIZE
                    | (_FILE_WRITE_DATA if writable_final and final else 0)
                )
                following = _win_open_relative_handle(
                    current,
                    component,
                    access=access,
                    disposition=_FILE_OPEN,
                    directory=True,
                )
                _win_close_handle(current)
                current = following
            return current, _win_identity(current)
        except Exception:
            _win_close_handle(current)
            raise

    if (
        not hasattr(os, "O_NOFOLLOW")
        or os.open not in os.supports_dir_fd
        or os.unlink not in os.supports_dir_fd
    ):
        raise OSError("platform lacks dir_fd/O_NOFOLLOW anchored mutation support")
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    current = os.open(root, flags)
    try:
        for component in relative.parts:
            following = os.open(component, flags, dir_fd=current)
            os.close(current)
            current = following
        metadata = os.fstat(current)
        if not stat.S_ISDIR(metadata.st_mode):
            raise OSError("mutable parent is not a directory")
        return current, (int(metadata.st_dev), int(metadata.st_ino))
    except Exception:
        os.close(current)
        raise


def _native_close_directory(native: int) -> None:
    if os.name == "nt":
        _win_close_handle(native)
    else:
        os.close(native)


def _native_directory_fsync(native: int) -> str:
    if os.name == "nt":
        if not _KERNEL32.FlushFileBuffers(native):
            raise ctypes.WinError(ctypes.get_last_error())
    else:
        os.fsync(native)
    return "verified"


def _fd_identity(fd: int) -> tuple[int, ...]:
    if os.name == "nt":
        return _win_identity(msvcrt.get_osfhandle(fd))
    metadata = os.fstat(fd)
    return (int(metadata.st_dev), int(metadata.st_ino))


class _AnchoredFile:
    def __init__(
        self,
        *,
        parent: "_AnchoredDirectory",
        name: str,
        fd: int,
        identity: tuple[int, ...],
    ) -> None:
        self.parent = parent
        self.name = name
        self.fd: int | None = fd
        self.identity = identity

    def close(self) -> None:
        if self.fd is not None:
            os.close(self.fd)
            self.fd = None

    def read(self) -> bytes:
        if self.fd is None:
            raise OSError("anchored file is closed")
        return _read_all(self.fd)

    def fsync(self) -> None:
        if self.fd is None:
            raise OSError("anchored file is closed")
        os.fsync(self.fd)

    def truncate(self, length: int) -> None:
        if self.fd is None:
            raise OSError("anchored file is closed")
        os.ftruncate(self.fd, length)

    def delete(self) -> None:
        if self.fd is None:
            raise OSError("anchored file is closed")
        self.parent.verify_reference(
            self.name,
            expected_identity=self.identity,
            expected_raw=self.read(),
        )
        if os.name == "nt":
            delete_handle = _win_open_relative_handle(
                self.parent.native,
                self.name,
                access=_DELETE | _FILE_READ_ATTRIBUTES | _SYNCHRONIZE,
                disposition=_FILE_OPEN,
                directory=False,
            )
            try:
                if _win_identity(delete_handle) != self.identity:
                    raise OSError("anchored final component identity changed")
                disposition = _FileDispositionInfo(True)
                if not _KERNEL32.SetFileInformationByHandle(
                    delete_handle,
                    _FILE_DISPOSITION_INFO_CLASS,
                    ctypes.byref(disposition),
                    ctypes.sizeof(disposition),
                ):
                    raise ctypes.WinError(ctypes.get_last_error())
            finally:
                _win_close_handle(delete_handle)
        else:
            os.unlink(self.name, dir_fd=self.parent.native)
        self.close()


class _AnchoredDirectory:
    def __init__(
        self,
        *,
        root: Path,
        relative: Path,
        label: str,
    ) -> None:
        self.root = root
        self.relative = relative
        self.label = label
        self.native, self.identity = _native_directory_chain(
            root,
            relative,
            writable_final=True,
        )

    def close(self) -> None:
        if self.native is not None:
            _native_close_directory(self.native)
            self.native = None

    def assert_current(self) -> None:
        if self.native is None:
            raise OSError(f"{self.label} anchor is closed")
        current, identity = _native_directory_chain(
            self.root,
            self.relative,
            writable_final=False,
        )
        _native_close_directory(current)
        if identity != self.identity:
            raise OSError(f"{self.label} identity changed")

    def fsync(self) -> str:
        if self.native is None:
            raise OSError(f"{self.label} anchor is closed")
        return _native_directory_fsync(self.native)

    def _open_file(
        self,
        name: str,
        *,
        create: bool,
        writable: bool,
    ) -> _AnchoredFile:
        if self.native is None:
            raise OSError(f"{self.label} anchor is closed")
        if not name or name in {".", ".."} or "/" in name or "\\" in name:
            raise OSError("anchored final component is invalid")
        if os.name == "nt":
            access = _FILE_READ_DATA | _FILE_READ_ATTRIBUTES | _SYNCHRONIZE
            if writable:
                access |= _FILE_WRITE_DATA | _FILE_APPEND_DATA
            handle = _win_open_relative_handle(
                self.native,
                name,
                access=access,
                disposition=_FILE_CREATE if create else _FILE_OPEN,
                directory=False,
            )
            try:
                flags = os.O_RDWR if writable else os.O_RDONLY
                fd = msvcrt.open_osfhandle(handle, flags | BINARY_FLAG)
            except Exception:
                _win_close_handle(handle)
                raise
        else:
            flags = (os.O_RDWR if writable else os.O_RDONLY) | os.O_NOFOLLOW | BINARY_FLAG
            if create:
                flags |= os.O_CREAT | os.O_EXCL
            fd = os.open(name, flags, 0o600, dir_fd=self.native)
            metadata = os.fstat(fd)
            if not stat.S_ISREG(metadata.st_mode):
                os.close(fd)
                raise OSError("anchored final component is not a regular file")
        return _AnchoredFile(
            parent=self,
            name=name,
            fd=fd,
            identity=_fd_identity(fd),
        )

    def open_existing(self, name: str, *, writable: bool) -> _AnchoredFile:
        return self._open_file(name, create=False, writable=writable)

    def create(self, name: str) -> _AnchoredFile:
        return self._open_file(name, create=True, writable=True)

    def snapshot(
        self,
        name: str,
        *,
        allow_missing: bool,
    ) -> tuple[bytes, tuple[int, ...]] | None:
        try:
            opened = self.open_existing(name, writable=False)
        except FileNotFoundError:
            if allow_missing:
                return None
            raise
        try:
            return opened.read(), opened.identity
        finally:
            opened.close()

    def verify_reference(
        self,
        name: str,
        *,
        expected_identity: tuple[int, ...],
        expected_raw: bytes,
    ) -> None:
        snapshot = self.snapshot(name, allow_missing=False)
        if snapshot != (expected_raw, expected_identity):
            raise OSError(f"{self.label} final component changed")

    def require_absent(self, name: str) -> None:
        if self.snapshot(name, allow_missing=True) is not None:
            raise OSError(f"{self.label} final component is not absent")


class _AnchoredParents:
    def __init__(
        self,
        *,
        root: Path,
        target_parent: Path,
        audit_parent: Path,
    ) -> None:
        try:
            target_relative = target_parent.relative_to(root)
            audit_relative = audit_parent.relative_to(root)
        except ValueError as exc:
            raise DispatchAuthorizationWriterError("mutable parent escapes repo root") from exc
        self.target = _AnchoredDirectory(
            root=root,
            relative=target_relative,
            label="KDAUTH target parent",
        )
        try:
            self.audit = _AnchoredDirectory(
                root=root,
                relative=audit_relative,
                label="KDAUTH audit parent",
            )
        except Exception:
            self.target.close()
            raise

    def __enter__(self) -> "_AnchoredParents":
        return self

    def __exit__(self, *args: Any) -> None:
        self.audit.close()
        self.target.close()

    def assert_current(self) -> None:
        self.target.assert_current()
        self.audit.assert_current()

    def prove_durability_available(self) -> None:
        self.target.fsync()
        self.audit.fsync()


def _open_anchored_parents(
    *,
    root: Path,
    target_parent: Path,
    audit_parent: Path,
) -> _AnchoredParents:
    try:
        parents = _AnchoredParents(
            root=root,
            target_parent=target_parent,
            audit_parent=audit_parent,
        )
        parents.assert_current()
        parents.prove_durability_available()
        return parents
    except DispatchAuthorizationWriterError:
        raise
    except Exception as exc:
        raise DispatchAuthorizationWriterError(
            "descriptor-anchored no-reparse parent guarantee is unavailable"
        ) from exc


def _read_regular(path: Path, label: str) -> bytes:
    if path.is_symlink() or not path.is_file():
        raise DispatchAuthorizationWriterError(f"{label} must be a regular non-symlink file")
    try:
        return path.read_bytes()
    except OSError as exc:
        raise DispatchAuthorizationWriterError(f"{label} is unreadable") from exc


def _load_proposal(path: Path) -> tuple[dict[str, Any], bytes]:
    raw = _read_regular(path, "dispatch authorization proposal")
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise DispatchAuthorizationWriterError(
            "dispatch authorization proposal is not readable UTF-8 JSON"
        ) from exc
    if not isinstance(value, dict):
        raise DispatchAuthorizationWriterError(
            "dispatch authorization proposal must be a JSON object"
        )
    return value, raw


def _candidate_validation(
    *,
    root: Path,
    proposal_path: Path,
    reviewed_whole_file_sha256: str,
    reviewed_byte_length: int,
) -> dict[str, Any]:
    try:
        return validate_dispatch_authorization_candidate(
            repo_root=root,
            proposal_path=proposal_path,
            expected_whole_file_sha256=reviewed_whole_file_sha256,
            expected_byte_length=reviewed_byte_length,
        )
    except DispatchAuthorizationError as exc:
        raise DispatchAuthorizationWriterError(str(exc)) from exc


def _initial_reservation_event(
    *,
    authorization: Mapping[str, Any],
    reviewed_hash: str,
    reviewed_length: int,
    attempt_id: str,
    actor: str,
    reserved_at: str,
) -> dict[str, Any]:
    core = authorization["authorization_core"]
    crossing = core["crossing_identities"]
    authorization_id = authorization["authorization_id"]
    return {
        "schema_version": RESERVATION_SCHEMA_VERSION,
        "event_id": f"{attempt_id}-000001",
        "sequence_number": 1,
        "event_type": "attempt_reserved",
        "attempt_id": attempt_id,
        "reservation_stream_path": (
            "research/queue/dispatch_authorization_reservations/"
            f"{attempt_id}.crossing_reservation.jsonl"
        ),
        "authorization_binding": {
            "authorization_id": authorization_id,
            "authorization_target_path": authorization["authorization_artifact_target_path"],
            "authorization_core_sha256": authorization["authorization_core_sha256"],
            "authorization_core_hash_scope": "dispatch_authorization_core_v1",
            "authorization_core_canonicalization": "repo_canonical_json_v1",
        },
        "dispatch_binding": {
            "dispatch_id": crossing["dispatch_id"],
            "dispatch_record_path": crossing["dispatch_record_path"],
        },
        "run_binding": {
            "run_id": crossing["run_id"],
            "execution_event_stream_path": crossing["execution_event_stream_path"],
        },
        "queue_binding": {
            "queue_item_id": core["queue_binding"]["queue_item_id"],
            "authorization_id": authorization_id,
            "queue_authorization_pair_scope": "queue_item_and_dispatch_authorization",
        },
        "reviewed_content_binding": {
            "reviewed_whole_file_sha256": reviewed_hash,
            "reviewed_byte_length": reviewed_length,
            "reviewed_content_scope": "exact_kdauth_whole_file_bytes_including_final_lf",
        },
        "reserved_at": reserved_at,
        "occurred_at": reserved_at,
        "actor": actor,
        "writer_identity": RESERVATION_WRITER_IDENTITY,
        "identities_permanently_reserved": True,
        "automatic_retry_with_same_identities_forbidden": True,
        "event_payload": {
            "reservation_committed_before_kdauth_mutation": True,
            "kdauth_target_mutation_started": False,
            "kdauth_lifecycle_mutation_started": False,
            "reservation_commit_posture": "exclusive_create_complete_write_fsync_verified",
            "terminal_outcome_pending": True,
        },
        "non_authority_declaration": copy.deepcopy(RESERVATION_NON_AUTHORITY),
    }


def _creation_event(
    *,
    authorization: Mapping[str, Any],
    raw: bytes,
    actor: str,
    occurred_at: str,
) -> dict[str, Any]:
    core = authorization["authorization_core"]
    crossing = core["crossing_identities"]
    authorization_id = authorization["authorization_id"]
    return {
        "schema_version": "canon_dispatch_authorization_audit_event_v1",
        "event_id": f"KDAUTH-EVENT-{authorization_id}-000001",
        "sequence_number": 1,
        "event_type": "authorization_created",
        "authorization_id": authorization_id,
        "authorization_path": authorization["authorization_artifact_target_path"],
        "authorization_file_sha256": _digest(raw),
        "authorization_byte_length": len(raw),
        "authorization_core_sha256": authorization["authorization_core_sha256"],
        "authorization_core_hash_scope": "dispatch_authorization_core_v1",
        "queue_item_id": core["queue_binding"]["queue_item_id"],
        "dispatch_id": crossing["dispatch_id"],
        "run_id": crossing["run_id"],
        "occurred_at": occurred_at,
        "actor": actor,
        "tool_identity": WRITER_IDENTITY,
        "event_payload": {
            "event_kind": "authorization_created",
            "creation_posture": "protected_exclusive_create",
        },
        "non_authority_declaration": copy.deepcopy(AUDIT_NON_AUTHORITY),
    }


def _terminal_from_initial(
    initial: Mapping[str, Any],
    *,
    event_type: str,
    occurred_at: str,
    payload: Mapping[str, Any],
) -> dict[str, Any]:
    terminal = copy.deepcopy(dict(initial))
    terminal["event_id"] = f"{initial['attempt_id']}-000002"
    terminal["sequence_number"] = 2
    terminal["event_type"] = event_type
    terminal["occurred_at"] = occurred_at
    terminal["event_payload"] = dict(payload)
    return terminal


def _append_audit_line(
    *,
    audit_parent: _AnchoredDirectory,
    audit_name: str,
    prior_raw: bytes,
    prior_identity: tuple[int, ...] | None,
    line: bytes,
    audit_file: _AnchoredFile | None = None,
) -> tuple[_AnchoredFile, str]:
    failure_phase = "authorization_created_append"
    uncertainty_class = "append_state_ambiguous"
    try:
        if prior_identity is None:
            if audit_file is not None:
                raise OSError("unexpected pre-opened audit file")
            audit_file = audit_parent.create(audit_name)
        else:
            if audit_file is None:
                audit_file = audit_parent.open_existing(
                    audit_name,
                    writable=True,
                )
            if audit_file.identity != prior_identity or audit_file.read() != prior_raw:
                raise OSError("lifecycle audit identity or bytes changed before append")
        if audit_file.fd is None:
            raise OSError("anchored audit file is closed")
        os.lseek(audit_file.fd, 0, os.SEEK_END)
        _write_all(audit_file.fd, line)
        failure_phase = "authorization_created_fsync"
        uncertainty_class = "durability_not_proven"
        audit_file.fsync()
        failure_phase = "post_crossing_verification"
        uncertainty_class = "cross_surface_binding_mismatch"
        if audit_file.read() != prior_raw + line:
            raise OSError("audit post-append reread mismatch")
        audit_parent.verify_reference(
            audit_name,
            expected_identity=audit_file.identity,
            expected_raw=prior_raw + line,
        )
        failure_phase = "authorization_created_fsync"
        uncertainty_class = "durability_not_proven"
        status = audit_parent.fsync()
        audit_parent.assert_current()
        return audit_file, status
    except Exception as exc:
        error = DispatchAuthorizationWriterIntegrityCriticalError(
            f"{failure_phase} failed or is uncertain; operator inspection required"
        )
        setattr(error, "failure_phase", failure_phase)
        setattr(error, "uncertainty_class", uncertainty_class)
        setattr(error, "anchored_file", audit_file)
        raise error from exc


def _exclusive_write_target(
    *,
    target_parent: _AnchoredDirectory,
    target_name: str,
    raw: bytes,
) -> tuple[_AnchoredFile, str]:
    target_file: _AnchoredFile | None = None
    try:
        target_file = target_parent.create(target_name)
    except Exception as exc:
        error = DispatchAuthorizationWriterIntegrityCriticalError(
            "KDAUTH target create or path identity is uncertain after durable "
            "reservation; "
            "operator inspection required"
        )
        setattr(error, "failure_phase", "kdauth_target_exclusive_create")
        setattr(
            error,
            "uncertainty_class",
            "unexpected_integrity_uncertainty",
        )
        setattr(error, "anchored_file", target_file)
        raise error from exc
    failure_phase = "kdauth_target_write"
    uncertainty_class = "partial_write"
    try:
        if target_file.fd is None:
            raise OSError("anchored target file is closed")
        _write_all(target_file.fd, raw)
        failure_phase = "kdauth_target_fsync"
        uncertainty_class = "durability_not_proven"
        target_file.fsync()
        failure_phase = "post_crossing_verification"
        uncertainty_class = "cross_surface_binding_mismatch"
        if target_file.read() != raw:
            raise OSError("KDAUTH post-write reread mismatch")
        target_parent.verify_reference(
            target_name,
            expected_identity=target_file.identity,
            expected_raw=raw,
        )
        failure_phase = "kdauth_target_fsync"
        uncertainty_class = "durability_not_proven"
        status = target_parent.fsync()
        target_parent.assert_current()
        return target_file, status
    except Exception as exc:
        error = DispatchAuthorizationWriterIntegrityCriticalError(
            "KDAUTH exclusive create/write/fsync is uncertain; operator inspection required"
        )
        setattr(
            error,
            "failure_phase",
            failure_phase,
        )
        setattr(
            error,
            "uncertainty_class",
            uncertainty_class,
        )
        setattr(error, "anchored_file", target_file)
        raise error from exc


def _restore_exact_prior_state(
    *,
    parents: _AnchoredParents,
    target_name: str,
    target_file: _AnchoredFile | None,
    audit_name: str,
    audit_file: _AnchoredFile | None,
    prior_audit_raw: bytes,
    prior_audit_identity: tuple[int, ...] | None,
) -> None:
    parents.assert_current()
    if audit_file is not None:
        if prior_audit_identity is not None:
            audit_file.truncate(len(prior_audit_raw))
            audit_file.fsync()
            if audit_file.read() != prior_audit_raw:
                raise OSError("audit rollback byte verification failed")
            parents.audit.verify_reference(
                audit_name,
                expected_identity=prior_audit_identity,
                expected_raw=prior_audit_raw,
            )
        else:
            audit_file.delete()
            parents.audit.require_absent(audit_name)
        parents.audit.fsync()
    elif prior_audit_identity is not None:
        parents.audit.verify_reference(
            audit_name,
            expected_identity=prior_audit_identity,
            expected_raw=prior_audit_raw,
        )
    else:
        parents.audit.require_absent(audit_name)
    if target_file is not None:
        target_file.delete()
        parents.target.fsync()
    parents.target.require_absent(target_name)
    if prior_audit_identity is not None:
        parents.audit.verify_reference(
            audit_name,
            expected_identity=prior_audit_identity,
            expected_raw=prior_audit_raw,
        )
    else:
        parents.audit.require_absent(audit_name)
    parents.assert_current()


def _path_integrity_critical(
    message: str,
    *,
    phase: str = "post_crossing_verification",
    uncertainty: str = "unexpected_integrity_uncertainty",
) -> DispatchAuthorizationWriterIntegrityCriticalError:
    error = DispatchAuthorizationWriterIntegrityCriticalError(
        f"{message}; operator inspection required"
    )
    setattr(error, "failure_phase", phase)
    setattr(error, "uncertainty_class", uncertainty)
    return error


def _assert_post_reservation_anchors(
    *,
    parents: _AnchoredParents,
    target_name: str,
    target_file: _AnchoredFile | None,
    target_raw: bytes | None,
    audit_name: str,
    audit_file: _AnchoredFile | None,
    audit_raw: bytes,
    audit_identity: tuple[int, ...] | None,
) -> None:
    try:
        parents.assert_current()
        if target_file is None:
            parents.target.require_absent(target_name)
        elif target_raw is not None:
            parents.target.verify_reference(
                target_name,
                expected_identity=target_file.identity,
                expected_raw=target_raw,
            )
        if audit_file is not None:
            parents.audit.verify_reference(
                audit_name,
                expected_identity=audit_file.identity,
                expected_raw=audit_raw,
            )
        elif audit_identity is None:
            parents.audit.require_absent(audit_name)
        else:
            parents.audit.verify_reference(
                audit_name,
                expected_identity=audit_identity,
                expected_raw=audit_raw,
            )
    except Exception as exc:
        raise _path_integrity_critical(
            "mutable parent or final component identity changed"
        ) from exc


def _validate_audit_bytes(
    *,
    root: Path,
    raw: bytes,
    allow_missing: bool = False,
) -> list[tuple[dict[str, Any], bytes]]:
    if allow_missing and not raw:
        return []
    try:
        return _validate_dispatch_authorization_audit_raw(root, raw)
    except DispatchAuthorizationError as exc:
        raise DispatchAuthorizationWriterError(str(exc)) from exc


def _validated_audit_append(
    *,
    root: Path,
    prior_raw: bytes,
    event: Mapping[str, Any],
) -> tuple[bytes, list[tuple[dict[str, Any], bytes]]]:
    if not isinstance(event, Mapping):
        raise DispatchAuthorizationWriterError(
            "dispatch-authorization audit event must be a mapping"
        )
    line = repo_canonical_json_v1(dict(event)) + b"\n"
    rows = _validate_audit_bytes(root=root, raw=prior_raw + line)
    return line, rows


def _append_integrity_critical_best_effort(
    *,
    lock: Any,
    initial: Mapping[str, Any],
    failure: BaseException,
    parents: _AnchoredParents,
    target_name: str,
    target_file: _AnchoredFile | None,
    audit_name: str,
    audit_file: _AnchoredFile | None,
    prior_audit_raw: bytes,
) -> None:
    target_state = "unknown"
    try:
        if target_file is None:
            if (
                parents.target.snapshot(
                    target_name,
                    allow_missing=True,
                )
                is None
            ):
                target_state = "absent"
        else:
            target_raw = target_file.read()
            reviewed = initial["reviewed_content_binding"]
            target_state = (
                "complete"
                if _digest(target_raw) == reviewed["reviewed_whole_file_sha256"]
                and len(target_raw) == reviewed["reviewed_byte_length"]
                else "partial"
            )
    except OSError:
        target_state = "unknown"
    audit_state = "unknown"
    try:
        if audit_file is not None:
            current_audit = audit_file.read()
        else:
            snapshot = parents.audit.snapshot(
                audit_name,
                allow_missing=True,
            )
            current_audit = snapshot[0] if snapshot is not None else b""
        if current_audit == prior_audit_raw:
            audit_state = "unchanged"
        elif current_audit.startswith(prior_audit_raw):
            try:
                rows = _validate_audit_bytes(
                    root=lock.repo_root,
                    raw=current_audit,
                )
                exact_creation = any(
                    event["event_type"] == "authorization_created"
                    and event["authorization_id"]
                    == initial["authorization_binding"]["authorization_id"]
                    for event, _ in rows
                )
                audit_state = "authorization_created_complete" if exact_creation else "partial_tail"
            except DispatchAuthorizationWriterError:
                audit_state = "partial_tail"
    except OSError:
        pass
    phase = getattr(failure, "failure_phase", "unexpected_protected_writer_failure")
    uncertainty = getattr(failure, "uncertainty_class", "unexpected_integrity_uncertainty")
    terminal = _terminal_from_initial(
        initial,
        event_type="crossing_integrity_critical",
        occurred_at=_timestamp_after(initial["occurred_at"]),
        payload={
            "terminal_outcome": "crossing_integrity_critical",
            "operator_inspection_required": True,
            "terminal_is_permanent": True,
            "failure_phase": phase,
            "uncertainty_class": uncertainty,
            "kdauth_target_state": target_state,
            "lifecycle_audit_state": audit_state,
        },
    )
    try:
        append_dispatch_authorization_crossing_terminal_locked(
            lock=lock,
            event=terminal,
        )
    except Exception:
        return


def write_dispatch_authorization(
    *,
    repo_root: Path,
    proposal_path: Path,
    reviewed_whole_file_sha256: str,
    attempt_id: str,
    actor: str,
) -> dict[str, Any]:
    """Execute one reservation-before-mutation protected KDAUTH crossing."""
    root = repo_root.resolve()
    if SHA256_RE.fullmatch(reviewed_whole_file_sha256) is None:
        raise DispatchAuthorizationWriterError(
            "reviewed whole-file SHA-256 must use sha256:<64 lowercase hex>"
        )
    if ATTEMPT_ID_RE.fullmatch(attempt_id) is None:
        raise DispatchAuthorizationWriterError(
            "attempt ID must match KDAUTH-XING-YYYYMMDD-XXXXXXXX"
        )
    proposal, proposal_raw = _load_proposal(proposal_path)
    if _digest(proposal_raw) != reviewed_whole_file_sha256:
        raise DispatchAuthorizationWriterError(
            "reviewed whole-file SHA-256 does not match proposal bytes"
        )
    if actor != proposal.get("approved_by"):
        raise DispatchAuthorizationWriterError("actor must exactly equal proposal approved_by")
    reviewed_length = len(proposal_raw)
    prelock_validation = _candidate_validation(
        root=root,
        proposal_path=proposal_path,
        reviewed_whole_file_sha256=reviewed_whole_file_sha256,
        reviewed_byte_length=reviewed_length,
    )
    prelock_target = root / Path(prelock_validation["authorization_path"])
    prelock_audit = root / AUDIT_PATH
    with _open_anchored_parents(
        root=root,
        target_parent=prelock_target.parent,
        audit_parent=prelock_audit.parent,
    ):
        pass

    result: dict[str, Any] | None = None
    try:
        with dispatch_authorization_crossing_lock(repo_root=root) as lock:
            inside_proposal, inside_raw = _load_proposal(proposal_path)
            if inside_raw != proposal_raw:
                raise DispatchAuthorizationWriterError(
                    "proposal bytes changed before the in-lock crossing"
                )
            inside_validation = _candidate_validation(
                root=root,
                proposal_path=proposal_path,
                reviewed_whole_file_sha256=reviewed_whole_file_sha256,
                reviewed_byte_length=reviewed_length,
            )
            if inside_validation["whole_file_sha256"] != (reviewed_whole_file_sha256):
                raise DispatchAuthorizationWriterError(
                    "in-lock reviewed whole-file SHA-256 mismatch"
                )
            if inside_proposal != proposal:
                raise DispatchAuthorizationWriterError(
                    "proposal JSON changed before the in-lock crossing"
                )
            target = root / Path(inside_validation["authorization_path"])
            audit_path = root / AUDIT_PATH
            target_name = target.name
            audit_name = audit_path.name
            with _open_anchored_parents(
                root=root,
                target_parent=target.parent,
                audit_parent=audit_path.parent,
            ) as parents:
                parents.target.require_absent(target_name)
                audit_snapshot = parents.audit.snapshot(
                    audit_name,
                    allow_missing=True,
                )
                if audit_snapshot is None:
                    prior_audit_raw = b""
                    prior_audit_identity = None
                    audit_file: _AnchoredFile | None = None
                else:
                    prior_audit_raw, prior_audit_identity = audit_snapshot
                    audit_file = parents.audit.open_existing(
                        audit_name,
                        writable=True,
                    )
                    if (
                        audit_file.identity != prior_audit_identity
                        or audit_file.read() != prior_audit_raw
                    ):
                        audit_file.close()
                        raise DispatchAuthorizationWriterError(
                            "lifecycle audit changed during anchored validation"
                        )
                target_file: _AnchoredFile | None = None
                try:
                    audit_rows, prior_audit_length = read_and_validate_dispatch_authorization_audit(
                        repo_root=root,
                        allow_missing=True,
                    )
                    anchored_rows = _validate_audit_bytes(
                        root=root,
                        raw=prior_audit_raw,
                        allow_missing=True,
                    )
                    if audit_rows != anchored_rows or prior_audit_length != len(prior_audit_raw):
                        raise DispatchAuthorizationWriterError(
                            "lifecycle audit changed during in-lock validation"
                        )
                    parents.assert_current()
                    if prior_audit_identity is None:
                        parents.audit.require_absent(audit_name)
                    else:
                        parents.audit.verify_reference(
                            audit_name,
                            expected_identity=prior_audit_identity,
                            expected_raw=prior_audit_raw,
                        )

                    reserved_at = _format_timestamp(_utc_now())
                    initial = _initial_reservation_event(
                        authorization=inside_proposal,
                        reviewed_hash=reviewed_whole_file_sha256,
                        reviewed_length=reviewed_length,
                        attempt_id=attempt_id,
                        actor=actor,
                        reserved_at=reserved_at,
                    )
                    try:
                        reservation_result = reserve_dispatch_authorization_crossing_locked(
                            lock=lock,
                            event=initial,
                        )
                    except DispatchAuthorizationReservationIntegrityCriticalError as exc:
                        raise (
                            DispatchAuthorizationWriterIntegrityCriticalError(
                                "reservation publication is uncertain; no "
                                "KDAUTH mutation began and all identities "
                                "remain burned"
                            )
                        ) from exc
                    except DispatchAuthorizationReservationError as exc:
                        raise DispatchAuthorizationWriterError(
                            f"reservation failed before KDAUTH mutation: {exc}"
                        ) from exc

                    try:
                        _assert_post_reservation_anchors(
                            parents=parents,
                            target_name=target_name,
                            target_file=None,
                            target_raw=None,
                            audit_name=audit_name,
                            audit_file=audit_file,
                            audit_raw=prior_audit_raw,
                            audit_identity=prior_audit_identity,
                        )
                        (
                            target_file,
                            target_directory_fsync_status,
                        ) = _exclusive_write_target(
                            target_parent=parents.target,
                            target_name=target_name,
                            raw=inside_raw,
                        )
                        if _digest(target_file.read()) != reviewed_whole_file_sha256:
                            failure = DispatchAuthorizationWriterIntegrityCriticalError(
                                "written KDAUTH hash differs from reviewed bytes"
                            )
                            setattr(
                                failure,
                                "failure_phase",
                                "post_crossing_verification",
                            )
                            setattr(
                                failure,
                                "uncertainty_class",
                                "cross_surface_binding_mismatch",
                            )
                            raise failure

                        creation = _creation_event(
                            authorization=inside_proposal,
                            raw=inside_raw,
                            actor=actor,
                            occurred_at=_timestamp_after(initial["occurred_at"]),
                        )
                        creation_line, creation_rows = _validated_audit_append(
                            root=root,
                            prior_raw=prior_audit_raw,
                            event=creation,
                        )
                        _assert_post_reservation_anchors(
                            parents=parents,
                            target_name=target_name,
                            target_file=target_file,
                            target_raw=inside_raw,
                            audit_name=audit_name,
                            audit_file=audit_file,
                            audit_raw=prior_audit_raw,
                            audit_identity=prior_audit_identity,
                        )
                        (
                            audit_file,
                            audit_directory_fsync_status,
                        ) = _append_audit_line(
                            audit_parent=parents.audit,
                            audit_name=audit_name,
                            prior_raw=prior_audit_raw,
                            prior_identity=prior_audit_identity,
                            line=creation_line,
                            audit_file=audit_file,
                        )
                        final_audit_raw = prior_audit_raw + creation_line
                        final_rows = _validate_audit_bytes(
                            root=root,
                            raw=audit_file.read(),
                        )
                        if final_rows != creation_rows or final_rows[-1] != (
                            creation,
                            creation_line,
                        ):
                            raise _path_integrity_critical(
                                "writer-time KDAUTH lifecycle is not created",
                                phase="post_crossing_verification",
                                uncertainty="cross_surface_binding_mismatch",
                            )
                        _assert_post_reservation_anchors(
                            parents=parents,
                            target_name=target_name,
                            target_file=target_file,
                            target_raw=inside_raw,
                            audit_name=audit_name,
                            audit_file=audit_file,
                            audit_raw=final_audit_raw,
                            audit_identity=prior_audit_identity,
                        )
                        committed = _terminal_from_initial(
                            initial,
                            event_type="crossing_committed",
                            occurred_at=_timestamp_after(creation["occurred_at"]),
                            payload={
                                "terminal_outcome": "crossing_committed",
                                "kdauth_target_durable": True,
                                "authorization_created_durable": True,
                                "resulting_authorization_path": inside_validation[
                                    "authorization_path"
                                ],
                                "resulting_authorization_whole_file_sha256": reviewed_whole_file_sha256,
                                "resulting_authorization_byte_length": reviewed_length,
                                "resulting_authorization_core_sha256": inside_validation[
                                    "authorization_core_sha256"
                                ],
                                "lifecycle_audit_path": AUDIT_PATH.as_posix(),
                                "authorization_created_event_id": creation["event_id"],
                                "lifecycle_event_sequence_number": creation["sequence_number"],
                                "lifecycle_raw_line_sha256": _digest(creation_line),
                                "lifecycle_raw_line_byte_length": len(creation_line),
                                "rollback_performed": False,
                                "operator_inspection_required": False,
                                "terminal_is_permanent": True,
                            },
                        )
                        try:
                            terminal_result = (
                                append_dispatch_authorization_crossing_terminal_locked(
                                    lock=lock,
                                    event=committed,
                                )
                            )
                        except DispatchAuthorizationReservationIntegrityCriticalError as exc:
                            failure = DispatchAuthorizationWriterIntegrityCriticalError(
                                "committed terminal append is uncertain; "
                                "operator inspection required"
                            )
                            setattr(
                                failure,
                                "failure_phase",
                                "reservation_terminal_append",
                            )
                            setattr(
                                failure,
                                "uncertainty_class",
                                "terminal_append_failed",
                            )
                            raise failure from exc
                        result = {
                            "crossing_committed": True,
                            "attempt_id": attempt_id,
                            "authorization_id": inside_validation["authorization_id"],
                            "authorization_path": inside_validation["authorization_path"],
                            "reviewed_whole_file_sha256": reviewed_whole_file_sha256,
                            "reviewed_byte_length": reviewed_length,
                            "authorization_core_sha256": inside_validation[
                                "authorization_core_sha256"
                            ],
                            "creation_event_id": creation["event_id"],
                            "reservation": reservation_result,
                            "terminal": terminal_result,
                            "target_directory_fsync_status": target_directory_fsync_status,
                            "audit_directory_fsync_status": audit_directory_fsync_status,
                            "non_authority": {
                                "does_not_create_dispatch": True,
                                "does_not_invoke_runner": True,
                                "does_not_create_execution_event": True,
                                "does_not_create_result_population": True,
                                "does_not_grant_runtime_or_capital_authority": True,
                            },
                        }
                    except DispatchAuthorizationWriterIntegrityCriticalError as failure:
                        attached = getattr(
                            failure,
                            "anchored_file",
                            None,
                        )
                        if target_file is None:
                            target_file = attached
                        elif audit_file is None:
                            audit_file = attached
                        _append_integrity_critical_best_effort(
                            lock=lock,
                            initial=initial,
                            failure=failure,
                            parents=parents,
                            target_name=target_name,
                            target_file=target_file,
                            audit_name=audit_name,
                            audit_file=audit_file,
                            prior_audit_raw=prior_audit_raw,
                        )
                        raise
                    except Exception as failure:
                        try:
                            _restore_exact_prior_state(
                                parents=parents,
                                target_name=target_name,
                                target_file=target_file,
                                audit_name=audit_name,
                                audit_file=audit_file,
                                prior_audit_raw=prior_audit_raw,
                                prior_audit_identity=prior_audit_identity,
                            )
                            rolled_back = _terminal_from_initial(
                                initial,
                                event_type="crossing_rolled_back_clean",
                                occurred_at=_timestamp_after(initial["occurred_at"]),
                                payload={
                                    "terminal_outcome": "crossing_rolled_back_clean",
                                    "kdauth_target_absence_proven": True,
                                    "lifecycle_audit_restored_to_exact_prior_length": True,
                                    "prior_lifecycle_audit_byte_length": prior_audit_length,
                                    "final_lifecycle_audit_byte_length": prior_audit_length,
                                    "rollback_durability_proven": True,
                                    "durability_uncertainty": False,
                                    "operator_inspection_required": False,
                                    "terminal_is_permanent": True,
                                },
                            )
                            append_dispatch_authorization_crossing_terminal_locked(
                                lock=lock,
                                event=rolled_back,
                            )
                        except Exception as rollback_exc:
                            critical = DispatchAuthorizationWriterIntegrityCriticalError(
                                "clean rollback or rollback terminal failed; "
                                "operator inspection required"
                            )
                            setattr(
                                critical,
                                "failure_phase",
                                "rollback",
                            )
                            setattr(
                                critical,
                                "uncertainty_class",
                                "rollback_failed",
                            )
                            _append_integrity_critical_best_effort(
                                lock=lock,
                                initial=initial,
                                failure=critical,
                                parents=parents,
                                target_name=target_name,
                                target_file=target_file,
                                audit_name=audit_name,
                                audit_file=audit_file,
                                prior_audit_raw=prior_audit_raw,
                            )
                            raise critical from rollback_exc
                        raise DispatchAuthorizationWriterError(
                            "crossing failed after reservation and was rolled "
                            "back cleanly; identities remain permanently burned"
                        ) from failure
                finally:
                    if audit_file is not None:
                        audit_file.close()
                    if target_file is not None:
                        target_file.close()
    except DispatchAuthorizationReservationIntegrityCriticalError as exc:
        raise DispatchAuthorizationWriterIntegrityCriticalError(
            "shared crossing lock cleanup failed; operator inspection required"
        ) from exc
    except DispatchAuthorizationReservationError as exc:
        raise DispatchAuthorizationWriterError(f"shared crossing lock unavailable: {exc}") from exc

    if result is None:
        raise DispatchAuthorizationWriterIntegrityCriticalError(
            "crossing ended without a committed result"
        )
    return result


def append_dispatch_authorization_lifecycle_event(
    *,
    repo_root: Path,
    authorization_path: Path,
    event_type: str,
    actor: str,
    event_payload: Mapping[str, Any],
) -> dict[str, Any]:
    """Append one legal terminal lifecycle event under the shared lock."""
    if event_type not in LIFECYCLE_TERMINALS:
        raise DispatchAuthorizationWriterError(
            "lifecycle append accepts only superseded, revoked, or consumed"
        )
    root = repo_root.resolve()
    selected_authorization = Path(authorization_path)
    if not selected_authorization.is_absolute():
        selected_authorization = root / selected_authorization
    audit_path = root / AUDIT_PATH
    result: dict[str, Any] | None = None
    try:
        with dispatch_authorization_crossing_lock(repo_root=root):
            with _open_anchored_parents(
                root=root,
                target_parent=selected_authorization.parent,
                audit_parent=audit_path.parent,
            ) as parents:
                authorization_file: _AnchoredFile | None = None
                audit_file: _AnchoredFile | None = None
                try:
                    authorization_file = parents.target.open_existing(
                        selected_authorization.name,
                        writable=False,
                    )
                    authorization_raw = authorization_file.read()
                    audit_file = parents.audit.open_existing(
                        audit_path.name,
                        writable=True,
                    )
                    prior_raw = audit_file.read()
                    dispatch_rel: str | None = None
                    if event_type == "authorization_consumed":
                        selected_dispatch = event_payload.get("dispatch_record_path")
                        if not isinstance(selected_dispatch, str):
                            raise DispatchAuthorizationWriterError(
                                "consumption requires dispatch_record_path"
                            )
                        dispatch_rel = selected_dispatch
                        validation = validate_dispatch_authorization_for_consumption(
                            repo_root=root,
                            authorization_path=selected_authorization,
                            dispatch_path=root / Path(dispatch_rel),
                        )
                    else:
                        validation = validate_dispatch_authorization(
                            repo_root=root,
                            authorization_path=selected_authorization,
                            require_audit=True,
                            scan_history=True,
                        )
                    rows, prior_length = read_and_validate_dispatch_authorization_audit(
                        repo_root=root
                    )
                    anchored_rows = _validate_audit_bytes(
                        root=root,
                        raw=prior_raw,
                    )
                    if (
                        rows != anchored_rows
                        or prior_length != len(prior_raw)
                        or validation["whole_file_sha256"] != _digest(authorization_raw)
                        or validation["byte_length"] != len(authorization_raw)
                    ):
                        raise DispatchAuthorizationWriterError(
                            "anchored lifecycle inputs changed during validation"
                        )
                    _assert_post_reservation_anchors(
                        parents=parents,
                        target_name=selected_authorization.name,
                        target_file=authorization_file,
                        target_raw=authorization_raw,
                        audit_name=audit_path.name,
                        audit_file=audit_file,
                        audit_raw=prior_raw,
                        audit_identity=audit_file.identity,
                    )
                    authorization = json.loads(authorization_raw.decode("utf-8"))
                    matching = [
                        row
                        for row, _ in anchored_rows
                        if row["authorization_id"] == validation["authorization_id"]
                    ]
                    if not matching or matching[-1]["event_type"] != ("authorization_created"):
                        raise DispatchAuthorizationWriterError(
                            "authorization lifecycle is not open for one terminal append"
                        )
                    if event_type == "authorization_consumed":
                        dispatch_validation = validation["dispatch_validation"]
                        if dispatch_validation["dispatch_path"] != dispatch_rel:
                            raise DispatchAuthorizationWriterError(
                                "consumption dispatch path is not exact"
                            )
                    core = authorization["authorization_core"]
                    crossing = core["crossing_identities"]
                    sequence = len(matching) + 1
                    event = {
                        "schema_version": "canon_dispatch_authorization_audit_event_v1",
                        "event_id": (
                            f"KDAUTH-EVENT-{authorization['authorization_id']}-{sequence:06d}"
                        ),
                        "sequence_number": sequence,
                        "event_type": event_type,
                        "authorization_id": authorization["authorization_id"],
                        "authorization_path": authorization["authorization_artifact_target_path"],
                        "authorization_file_sha256": _digest(authorization_raw),
                        "authorization_byte_length": len(authorization_raw),
                        "authorization_core_sha256": authorization["authorization_core_sha256"],
                        "authorization_core_hash_scope": "dispatch_authorization_core_v1",
                        "queue_item_id": core["queue_binding"]["queue_item_id"],
                        "dispatch_id": crossing["dispatch_id"],
                        "run_id": crossing["run_id"],
                        "occurred_at": _timestamp_after(matching[-1]["occurred_at"]),
                        "actor": actor,
                        "tool_identity": WRITER_IDENTITY,
                        "event_payload": dict(event_payload),
                        "non_authority_declaration": copy.deepcopy(AUDIT_NON_AUTHORITY),
                    }
                    if event["event_payload"].get("event_kind") != event_type:
                        raise DispatchAuthorizationWriterError(
                            "lifecycle event payload kind mismatch"
                        )
                    line, expected_rows = _validated_audit_append(
                        root=root,
                        prior_raw=prior_raw,
                        event=event,
                    )
                    (
                        audit_file,
                        audit_directory_fsync_status,
                    ) = _append_audit_line(
                        audit_parent=parents.audit,
                        audit_name=audit_path.name,
                        prior_raw=prior_raw,
                        prior_identity=audit_file.identity,
                        line=line,
                        audit_file=audit_file,
                    )
                    final_raw = prior_raw + line
                    try:
                        after = _validate_audit_bytes(
                            root=root,
                            raw=audit_file.read(),
                        )
                        _assert_post_reservation_anchors(
                            parents=parents,
                            target_name=selected_authorization.name,
                            target_file=authorization_file,
                            target_raw=authorization_raw,
                            audit_name=audit_path.name,
                            audit_file=audit_file,
                            audit_raw=final_raw,
                            audit_identity=audit_file.identity,
                        )
                    except Exception as exc:
                        raise _path_integrity_critical(
                            "lifecycle append is durable but validation is uncertain",
                            phase="post_crossing_verification",
                            uncertainty="cross_surface_binding_mismatch",
                        ) from exc
                    if after != expected_rows or after[-1] != (event, line):
                        raise _path_integrity_critical(
                            "lifecycle append post-write verification failed",
                            phase="post_crossing_verification",
                            uncertainty="cross_surface_binding_mismatch",
                        )
                    result = {
                        "event_appended": True,
                        "authorization_id": authorization["authorization_id"],
                        "event_id": event["event_id"],
                        "event_type": event_type,
                        "raw_line_sha256": _digest(line),
                        "raw_line_byte_length": len(line),
                        "audit_directory_fsync_status": audit_directory_fsync_status,
                        "non_authority": True,
                    }
                finally:
                    if audit_file is not None:
                        audit_file.close()
                    if authorization_file is not None:
                        authorization_file.close()
    except DispatchAuthorizationError as exc:
        raise DispatchAuthorizationWriterError(str(exc)) from exc
    except DispatchAuthorizationReservationIntegrityCriticalError as exc:
        raise DispatchAuthorizationWriterIntegrityCriticalError(
            "shared crossing lock cleanup failed; operator inspection required"
        ) from exc
    except DispatchAuthorizationReservationError as exc:
        raise DispatchAuthorizationWriterError(str(exc)) from exc
    if result is None:
        raise DispatchAuthorizationWriterIntegrityCriticalError(
            "lifecycle append ended without a durable result"
        )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--proposal", type=Path, required=True)
    parser.add_argument("--reviewed-whole-file-sha256", required=True)
    parser.add_argument("--attempt-id", required=True)
    parser.add_argument("--actor", required=True)
    args = parser.parse_args()
    try:
        result = write_dispatch_authorization(
            repo_root=args.repo_root,
            proposal_path=args.proposal,
            reviewed_whole_file_sha256=args.reviewed_whole_file_sha256,
            attempt_id=args.attempt_id,
            actor=args.actor,
        )
    except DispatchAuthorizationWriterError as exc:
        parser.exit(2, f"dispatch authorization writer stopped: {exc}\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
