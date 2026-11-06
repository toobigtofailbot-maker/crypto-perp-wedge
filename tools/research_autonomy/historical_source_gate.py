"""D3-2: custodian-authorized, study-specific historical nonholdout source custody.

Reuses the 02J owner-controlled custodian/revocation records, `nonholdout_control` table and
`nonholdout_read` audit event. Adds only a historical designation grammar
(`cpw_nonholdout_historical_v1`) that 02J's synthetic validator can never accept, and an
OS-enforced use-time lease. No migration, second ledger, approval or scientific authority.

Order enforced for the original-study route: authorize (custodial integrity read under an
OS lease) -> D4 `_execution_binding` may hash -> fresh Karl marker -> `consume_for_run`
(durable recheck, single use) -> runner -> `verify_unchanged` -> `verify_commit` at
terminal commit. Unsupported storage fails closed.

Threat model: trusts the host OS, the custodian key and Karl's owner DB connection. The
lease blocks writes/renames/deletes of the leased file and its ancestors on Windows and
requires FS_IMMUTABLE_FL on Linux; it does not stop other local processes from reading.
"""

from __future__ import annotations

import hashlib
import io
import json
import os
import stat
import sys
from pathlib import Path, PurePosixPath
from typing import Annotated, Literal

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from psycopg import Connection
from psycopg import Error as DatabaseError
from psycopg.pq import TransactionStatus
from pydantic import Field, ValidationError, model_validator

from .envelope import canonical_json, content_hash, validate_envelope
from .models import Count, Identity, Positive, RepoSha, Sha, StrictModel
from .nonholdout_qualification import (
    CADENCE,
    Custodian,
    Interval,
    NonHoldoutQualification,
    _code_sha,
    _now,
    _parse,
    _valid,
)
from .store import AuthorityConflict, ResearchAuthorityStore

SCHEMA = "cpw_nonholdout_historical_v1"
ROLES = ("ohlcv_input", "d4_catalog_slice", "d2_import_report")
STORAGE = {"win32": "windows_share_deny_write_v1", "linux": "linux_immutable_flag_v1"}
REFUSAL = "BLOCKED_NONHOLDOUT_CUSTODY"
REVOKED = "BLOCKED_DATA_USE_OR_REVOKED"
RepoPath = Annotated[str, Field(pattern=r"^[A-Za-z0-9_./-]+$", max_length=400)]


class Refused(AuthorityConflict):
    """Bounded refusal code only; never echoes inputs or protected bytes."""


class HistoricalObject(StrictModel):
    role: Literal["ohlcv_input", "d4_catalog_slice", "d2_import_report"]
    repo_path: RepoPath
    sha256: Sha
    byte_length: Positive
    device: Count
    inode: Positive

    @model_validator(mode="after")
    def role_path(self):
        root, suffix = {
            "ohlcv_input": ("data/processed/d4a/", ".csv"),
            "d4_catalog_slice": ("research/data_slices/", ".catalog_slice.json"),
            "d2_import_report": ("research/data_slices/", ".import_report.json"),
        }[self.role]
        if (not self.repo_path.startswith(root) or not self.repo_path.endswith(suffix)
                or any(p in {"", ".", ".."} for p in self.repo_path.split("/"))):
            raise ValueError("role-scoped ordinary repo path required")
        return self


class HistoricalRequest(StrictModel):
    schema_version: Literal["cpw_nonholdout_historical_v1"]
    purpose: Literal["historical_nonholdout_study_read"]
    repository: Literal["toobigtofailbot-maker/crypto-perp-wedge"]
    repo_sha: RepoSha
    campaign_id: Identity
    search_id: Identity
    contract_hash: Sha
    strategy_spec_hash: Sha
    original_parent_sha256: Sha
    contamination_domain_id: Identity
    holdout_id: Identity
    envelope_sha256: Sha
    protocol_sha256: Sha
    data_identity: Identity
    data_version: Identity
    instrument: Literal["BTCUSDT"]
    venue: Literal["Binance USDT-M"]
    market: Literal["perpetual"]
    timeframe: Literal["15m"]
    # The D4 adapter consumes the entire physical object: it IS the effective window.
    effective_window: Interval
    label_horizon_bars: Literal[0]
    fitting: Literal["none"]
    storage: Literal["windows_share_deny_write_v1", "linux_immutable_flag_v1"]
    objects: Annotated[tuple[HistoricalObject, ...], Field(min_length=3, max_length=3)]

    @model_validator(mode="after")
    def closed_dependencies(self):
        if tuple(o.role for o in self.objects) != ROLES:
            raise ValueError("exactly the three D4 inputs in order")
        if len({o.repo_path for o in self.objects}) != 3:
            raise ValueError("distinct objects required")
        step = CADENCE["15m"]
        if self.effective_window.start_ms % step or self.effective_window.end_ms % step:
            raise ValueError("partial bar window")
        return self


class HistoricalDesignation(StrictModel):
    record_id: Identity
    approved_by: Literal["Karl"]
    approval_reference: Identity
    custodian_id: Identity
    valid_from_ms: Count
    valid_until_ms: Positive
    request: HistoricalRequest
    protected_mapping_complete: Literal[True]
    protected_intervals: Annotated[tuple[Interval, ...], Field(min_length=1)]


class HistoricalAttestation(StrictModel):
    attestation_id: Identity
    custodian_id: Identity
    designation_id: Identity
    designation_sha256: Sha
    request_sha256: Sha
    valid_from_ms: Count
    valid_until_ms: Positive
    signature_hex: Annotated[str, Field(pattern=r"^[0-9a-f]{128}$")]


def signing_bytes(attestation: HistoricalAttestation) -> bytes:
    # Domain-separated from 02J so a synthetic signature can never authorize history.
    return b"CPW-NONHOLDOUT-HISTORICAL-D3-2\x00" + canonical_json(
        attestation.model_dump(mode="json", exclude={"signature_hex"})
    ).encode("ascii")


def _sha256_handle(fd: int) -> str:
    digest = hashlib.sha256()
    os.lseek(fd, 0, os.SEEK_SET)
    while chunk := os.read(fd, 1 << 20):
        digest.update(chunk)
    return "sha256:" + digest.hexdigest()


def _components(root: Path, repo_path: str) -> list[Path]:
    """Repo root, every directory, then the file; indirection anywhere is refused."""
    parts = PurePosixPath(repo_path).parts
    if any(p in {"", ".", ".."} for p in parts):
        raise Refused(REFUSAL)
    chain, cursor = [root], root
    for part in parts:
        cursor = cursor / part
        attrs = cursor.lstat()
        if stat.S_ISLNK(attrs.st_mode) or getattr(attrs, "st_file_attributes", 0) & 0x400:
            raise Refused(REFUSAL)
        chain.append(cursor)
    return chain


class _WindowsLease:
    """Share-read-only file handle plus no-delete-share ancestor handles (blocks swap)."""

    def __init__(self, chain: list[Path]):
        import ctypes
        import msvcrt
        from ctypes import wintypes

        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.CreateFileW.restype = wintypes.HANDLE
        kernel.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
                                       wintypes.LPVOID, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
        self._kernel, self._dirs, self.fd = kernel, [], None
        generic_read, share_read, share_write = 0x80000000, 0x1, 0x2
        open_existing, backup, no_reparse = 3, 0x02000000, 0x00200000
        invalid = wintypes.HANDLE(-1).value
        anchors = [*reversed(chain[-1].parents), *chain[1:-1]]
        try:
            for directory in dict.fromkeys(anchors):
                handle = kernel.CreateFileW(str(directory), generic_read, share_read | share_write,
                                            None, open_existing, backup | no_reparse, None)
                if handle in (None, invalid):
                    raise Refused(REFUSAL)
                self._dirs.append(handle)
            handle = kernel.CreateFileW(str(chain[-1]), generic_read, share_read, None,
                                        open_existing, no_reparse, None)
            if handle in (None, invalid):
                raise Refused(REFUSAL)
            self.fd = msvcrt.open_osfhandle(handle, os.O_RDONLY | os.O_BINARY)
        except BaseException:
            self.close()
            raise

    def close(self):
        if self.fd is not None:
            os.close(self.fd)
            self.fd = None
        while self._dirs:
            self._kernel.CloseHandle(self._dirs.pop())


class _LinuxLease:
    """Requires FS_IMMUTABLE_FL on the file and every directory up to the repo root."""

    FS_IOC_GETFLAGS, FS_IMMUTABLE_FL = 0x80086601, 0x10

    def __init__(self, chain: list[Path]):
        import array
        import fcntl

        self.fd = None
        opened = []
        try:
            for index, path in enumerate(chain):
                last = index == len(chain) - 1
                flags = os.O_RDONLY | os.O_NOFOLLOW | (0 if last else os.O_DIRECTORY)
                fd = os.open(path, flags)
                opened.append(fd)
                value = array.array("l", [0])
                try:
                    fcntl.ioctl(fd, self.FS_IOC_GETFLAGS, value, True)
                except OSError:
                    raise Refused("UNSUPPORTED_IMMUTABLE_STORAGE") from None
                if not value[0] & self.FS_IMMUTABLE_FL:
                    raise Refused("UNSUPPORTED_IMMUTABLE_STORAGE")
            self.fd = opened.pop()
        finally:
            for fd in opened:
                os.close(fd)

    def close(self):
        if self.fd is not None:
            os.close(self.fd)
            self.fd = None


def _lease(chain: list[Path], storage: str):
    if STORAGE.get(sys.platform) != storage:
        raise Refused("UNSUPPORTED_IMMUTABLE_STORAGE")
    return (_WindowsLease if sys.platform == "win32" else _LinuxLease)(chain)


class HistoricalLease:
    """Nonreusable, in-memory custody of the exact designated objects for one study."""

    def __init__(self, gate, root, designation, attestation, request, leases):
        self._gate, self._root = gate, root
        self.designation, self.attestation, self.request = designation, attestation, request
        self._leases = leases
        self.receipt = None

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def close(self):
        for lease in self._leases.values():
            lease.close()
        self._leases = {}

    def _identity(self, obj: HistoricalObject) -> None:
        lease = self._leases.get(obj.role)
        if lease is None or lease.fd is None:
            raise Refused(REFUSAL)
        facts, path_facts = os.fstat(lease.fd), (self._root / obj.repo_path).stat()
        if (facts.st_dev, facts.st_ino, facts.st_size) != (obj.device, obj.inode, obj.byte_length) or (
            path_facts.st_dev, path_facts.st_ino) != (facts.st_dev, facts.st_ino):
            raise Refused(REFUSAL)

    def require_preread(self, paths) -> None:
        """Called before D4 `_execution_binding` hashes or parses any historical byte."""
        expected = [(self._root / o.repo_path).absolute() for o in self.request.objects]
        given = [(Path(p) if Path(p).is_absolute() else self._root / p).absolute() for p in paths]
        if given != expected:
            raise Refused(REFUSAL)
        with self._gate.store._transaction() as conn:
            self._gate._durable(conn, self.attestation, self.request)
        for obj in self.request.objects:
            self._identity(obj)

    def verify_unchanged(self) -> None:
        for obj in self.request.objects:
            self._identity(obj)
            if _sha256_handle(self._leases[obj.role].fd) != obj.sha256:
                raise Refused(REFUSAL)

    def consume_for_run(self, *, execution, approval_sha256: str) -> dict:
        """After the fresh Karl marker and before the runner: durable recheck, single use."""
        if self.receipt is not None:
            raise Refused("ATTESTATION_ALREADY_USED")
        for obj in self.request.objects:
            if execution.get(obj.role + "_path") != obj.repo_path or execution.get(obj.role + "_sha256") != obj.sha256:
                raise Refused(REFUSAL)
        if execution.get("data_slice_identity") != self.request.data_identity:
            raise Refused(REFUSAL)
        self.verify_unchanged()
        payload = {
            "phase": "historical_runner_use",
            "request_sha256": self.attestation.request_sha256,
            "attestation": self.attestation.model_dump(mode="json"),
            "execution_sha256": content_hash(dict(execution)),
            "approval_sha256": approval_sha256,
        }
        event_id = "nonholdout-read:" + self.attestation.attestation_id
        try:
            with self._gate.store._transaction() as conn:
                self._gate._durable(conn, self.attestation, self.request)
                if conn.execute("SELECT 1 FROM research_authority.authority_audit WHERE event_id=%s",
                                (event_id,)).fetchone():
                    raise Refused("ATTESTATION_ALREADY_USED")
                self._gate.store._audit(conn, event_id=event_id, event_type="nonholdout_read", payload=payload,
                                        campaign=self._gate.store._campaign(conn, self.request.campaign_id))
        except (DatabaseError, ValidationError, ValueError, TypeError) as exc:
            if isinstance(exc, Refused):
                raise
            raise Refused(REVOKED) from None
        self.receipt = {
            "schema_version": "cpw_historical_custody_use_receipt_v1",
            "audit_event_id": event_id,
            "attestation_id": self.attestation.attestation_id,
            "designation_id": self.attestation.designation_id,
            "campaign_id": self.request.campaign_id,
            "request_sha256": self.attestation.request_sha256,
            "execution_sha256": payload["execution_sha256"],
            "approval_sha256": approval_sha256,
            "not_authority": True,
        }
        return dict(self.receipt)


class HistoricalSourceGate:
    def __init__(self, store: ResearchAuthorityStore, repo_root: Path):
        self.store = store
        self.root = repo_root.resolve(strict=True)
        self._native = NonHoldoutQualification(store)

    def designate(self, record) -> None:
        """Owner connection only (same privilege as 02J control); stores an immutable designation."""
        try:
            record = _parse(HistoricalDesignation, record)
            raw = record.model_dump(mode="json")
            payload = {"record_id": record.record_id, "kind": "designation", "record": raw,
                       "content_sha256": content_hash(raw)}
            event_id = "nonholdout:" + record.record_id
            with self.store._transaction() as conn:
                allowed = conn.execute(
                    "SELECT has_table_privilege(current_user,'research_authority.nonholdout_control','INSERT') AS ok"
                ).fetchone()["ok"]
                if not allowed:
                    raise Refused("OWNER_CONNECTION_REQUIRED")
                if self.store._replay(conn, event_id, "nonholdout_control", payload):
                    return
                self.store._audit(conn, event_id=event_id, event_type="nonholdout_control", payload=payload)
                conn.execute("INSERT INTO research_authority.nonholdout_control VALUES (%s,%s,%s,%s,%s)",
                             (record.record_id, "designation", canonical_json(raw), content_hash(raw), event_id))
        except (KeyError, TypeError, ValueError, OSError, DatabaseError):
            raise Refused("CONTROL_REFUSED") from None

    def _durable(self, conn, attestation, request):
        """Current durable authority, revocation, validity and holdout state; never cached."""
        designation = self._native._record(conn, attestation.designation_id, "designation", HistoricalDesignation)
        custodian = self._native._record(conn, attestation.custodian_id, "custodian", Custodian)
        self._native._unrevoked(conn, attestation.attestation_id)
        contract = self.store._load_contract(conn, request.search_id)
        if contract.contract_hash != request.contract_hash:
            raise Refused("DURABLE_BINDING")
        campaign = self.store._campaign(conn, request.campaign_id)
        row = conn.execute("SELECT semantic_payload FROM research_authority.envelope_registry "
                           "WHERE envelope_id=%s AND envelope_version=%s",
                           (campaign["envelope_id"], campaign["envelope_version"])).fetchone()
        envelope = validate_envelope(json.loads(row["semantic_payload"]), repo_sha=request.repo_sha)
        self.store._active_envelope(conn, envelope)
        if campaign["state"] != "open":
            raise Refused("CLOSED_CAMPAIGN")
        snapshot = self.store._snapshot(conn, request.campaign_id)
        if (snapshot.envelope_content_sha256 != request.envelope_sha256
                or snapshot.contamination_domain_id != request.contamination_domain_id
                or snapshot.holdout.holdout_id != request.holdout_id
                or snapshot.holdout.state != "unexposed" or snapshot.holdout.contaminated):
            raise Refused("DURABLE_BINDING")
        if (designation.custodian_id != attestation.custodian_id or designation.request != request
                or content_hash(designation.model_dump(mode="json")) != attestation.designation_sha256
                or content_hash(request.model_dump(mode="json")) != attestation.request_sha256):
            raise Refused("ATTESTATION_BINDING")
        Ed25519PublicKey.from_public_bytes(bytes.fromhex(custodian.public_key_hex)).verify(
            bytes.fromhex(attestation.signature_hex), signing_bytes(attestation))
        now = _now(conn)
        for record in (designation, custodian, attestation):
            _valid(record, now)
        return designation

    def authorize(self, *, attestation, request, envelope, contract, repo_sha: str) -> HistoricalLease:
        """Custodial integrity read only: verifies and leases bytes; grants no runner use."""
        leases = {}
        try:
            attestation = _parse(HistoricalAttestation, attestation)
            request = _parse(HistoricalRequest, request)
            if repo_sha != _code_sha():
                raise Refused("STALE_CODE")
            envelope = validate_envelope(envelope, repo_sha=repo_sha)
            protocol = envelope.scientific_protocol
            if (request.repo_sha != repo_sha or request.envelope_sha256 != envelope.content_sha256
                    or request.protocol_sha256 != content_hash(protocol.model_dump(mode="json"))):
                raise Refused("CODE_ENVELOPE_BINDING")
            if (request.campaign_id, request.search_id, request.contract_hash, request.strategy_spec_hash,
                request.data_identity, request.data_version, request.repo_sha,
                request.holdout_id) != (contract.campaign_id, contract.search_id, contract.contract_hash,
                                        contract.strategy_spec_hash, contract.data_identity,
                                        contract.data_version, contract.repo_sha,
                                        contract.split_protocol.final_holdout_ref):
                raise Refused("STUDY_BINDING")
            with self.store._transaction() as conn:
                self.store._active_envelope(conn, envelope)
                designation = self._durable(conn, attestation, request)
                horizon = (protocol.purge_bars + protocol.embargo_bars) * CADENCE["15m"]
                window = request.effective_window
                if any(window.start_ms - horizon < h.end_ms and h.start_ms < window.end_ms + horizon
                       for h in designation.protected_intervals):
                    raise Refused("PROTECTED_OVERLAP")
                if window.end_ms > _now(conn):
                    raise Refused("INCOMPLETE_AVAILABILITY")
                if conn.execute("SELECT 1 FROM research_authority.authority_audit WHERE event_id=%s",
                                ("nonholdout-read:" + attestation.attestation_id,)).fetchone():
                    raise Refused("ATTESTATION_ALREADY_USED")
            # Pin every object before reading any byte, then hash through the leased handles.
            for obj in request.objects:
                leases[obj.role] = _lease(_components(self.root, obj.repo_path), request.storage)
            lease = HistoricalLease(self, self.root, designation, attestation, request, leases)
            lease.verify_unchanged()
            catalog = json.loads(_read_handle(leases["d4_catalog_slice"].fd))
            if (catalog.get("slice_identity", {}).get("data_slice_identity") != request.data_identity
                    or catalog.get("normalized", {}).get("sha256") != request.objects[0].sha256.removeprefix("sha256:")
                    or catalog.get("normalized", {}).get("path", "").replace("\\", "/") != request.objects[0].repo_path):
                raise Refused(REFUSAL)
            report = json.loads(_read_handle(leases["d2_import_report"].fd))
            if (report.get("normalized", {}).get("sha256") != catalog["normalized"]["sha256"]
                    or report.get("normalized", {}).get("path", "").replace("\\", "/") != request.objects[0].repo_path):
                raise Refused(REFUSAL)
            _verify_coverage(request, contract, catalog, report, leases["ohlcv_input"].fd)
            return lease
        except Refused:
            for item in leases.values():
                item.close()
            raise
        except (AuthorityConflict, ValidationError, ValueError, TypeError, KeyError, OSError,
                InvalidSignature, DatabaseError):
            for item in leases.values():
                item.close()
            raise Refused(REFUSAL) from None

    def verify_commit(self, receipt: dict, *, _transaction=None):
        """Recheck custody in the native terminal transaction, or as a standalone diagnostic."""
        from .store import _terminal_evidence

        try:
            if _transaction is not None:
                if (_transaction is not _terminal_evidence.get()
                        or _transaction[0] is not self.store or _transaction[2] != self.root
                        or type(_transaction[1]) is not Connection
                        or _transaction[1].info.transaction_status != TransactionStatus.INTRANS):
                    raise Refused(REVOKED)
                return self._verify_commit(_transaction[1], receipt)
            with self.store._transaction() as conn:
                self._verify_commit(conn, receipt)
        except Refused:
            raise
        except (AuthorityConflict, ValidationError, ValueError, TypeError, KeyError, IndexError, DatabaseError):
            raise Refused(REVOKED) from None

    def _verify_commit(self, conn, receipt):
        row = conn.execute("SELECT normalized_payload FROM research_authority.authority_audit "
                           "WHERE event_id=%s AND event_type='nonholdout_read'",
                           (receipt["audit_event_id"],)).fetchone()
        if row is None:
            raise Refused(REVOKED)
        used = json.loads(row["normalized_payload"])["input"]
        attestation = _parse(HistoricalAttestation, used["attestation"])
        if (used["execution_sha256"] != receipt["execution_sha256"]
                or used["approval_sha256"] != receipt["approval_sha256"]
                or attestation.attestation_id != receipt["attestation_id"]):
            raise Refused(REVOKED)
        designation = self._native._record(conn, attestation.designation_id, "designation",
                                           HistoricalDesignation)
        self._durable(conn, attestation, designation.request)
        if (receipt.get("designation_id") != designation.record_id
                or receipt.get("campaign_id") != designation.request.campaign_id
                or receipt.get("request_sha256") != attestation.request_sha256):
            raise Refused(REVOKED)
        return designation.request


def _read_handle(fd: int) -> bytes:
    os.lseek(fd, 0, os.SEEK_SET)
    chunks = []
    while chunk := os.read(fd, 1 << 20):
        chunks.append(chunk)
    return b"".join(chunks)


def _verify_coverage(request, contract, catalog, report, fd):
    """Bind the entire leased primitive D4 CSV, not a selected strategy window."""
    import pandas as pd

    def ms(value):
        stamp = pd.Timestamp(value)
        if stamp.tzinfo is None or stamp.utcoffset().total_seconds() != 0:
            raise ValueError("UTC required")
        if stamp.value % 1_000_000:
            raise ValueError("millisecond precision required")
        return stamp.value // 1_000_000

    try:
        step = CADENCE["15m"]
        window = request.effective_window
        expected = (window.start_ms, window.end_ms)
        development = tuple(ms(v) for v in contract.split_protocol.development_window.split("/"))
        coverage = catalog["range"]
        count = (window.end_ms - window.start_ms) // step
        if (development != expected or catalog["catalog_version"] != request.data_version
                or catalog["source_type"] != "offline_bulk_or_local_file" or catalog["stream"] != "ohlcv"
                or (ms(coverage["start_utc"]), ms(coverage["end_utc"]) + step) != expected
                or coverage != report["range"]
                or type(coverage["row_count"]) is not int or coverage["row_count"] != count
                or type(coverage["expected_row_count"]) is not int or coverage["expected_row_count"] != count):
            raise Refused("PHYSICAL_COVERAGE_MISMATCH")
        frame = pd.read_csv(io.BytesIO(_read_handle(fd)))
        times = frame["open_time_ms"]
        if (len(frame) != count or times.dtype.kind not in "iu"
                or times.tolist() != list(range(*expected, step))):
            raise Refused("PHYSICAL_COVERAGE_MISMATCH")
        if "open_time" in frame and [ms(v) for v in frame["open_time"]] != times.tolist():
            raise Refused("PHYSICAL_COVERAGE_MISMATCH")
        if "close_time_ms" in frame and (frame["close_time_ms"] != times + step - 1).any():
            raise Refused("PHYSICAL_COVERAGE_MISMATCH")
    except (ValueError, TypeError, KeyError, OverflowError):
        raise Refused("PHYSICAL_COVERAGE_MISMATCH") from None
