"""CPW authority and sealed, synthetic-only byte validation. No pathname reader.

The custodian prepares and seals objects outside this boundary. The caller passes
handles, never source paths. No compiler, callback, model or raw-byte return exists.
"""

from __future__ import annotations

import hashlib
import json
import os
import stat
import subprocess
import sys
from pathlib import Path
from typing import Annotated, Literal

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from psycopg import Error as DatabaseError
from pydantic import Field, ValidationError, model_validator

from .envelope import canonical_json, content_hash, validate_envelope
from .models import Count, Identity, Positive, RepoSha, Sha, StrictModel
from .store import AuthorityConflict, ResearchAuthorityStore

CADENCE = {"15m": 900_000, "30m": 1_800_000, "1h": 3_600_000, "4h": 14_400_000, "1d": 86_400_000}
HexKey = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]


class Refused(AuthorityConflict):
    """Bounded refusal code only; never include inputs or source exceptions."""


class Interval(StrictModel):
    start_ms: Count
    end_ms: Positive

    @model_validator(mode="after")
    def ordered(self):
        if self.start_ms >= self.end_ms:
            raise ValueError("empty interval")
        return self


class ObjectBinding(StrictModel):
    object_id: Identity
    kind: Literal["base", "derived", "feature"]
    timeframe: Literal["15m", "30m", "1h", "4h", "1d"]
    interval: Interval
    # Full canonical identity is distinct from bounded object digest.
    canonical_sha256: Sha
    canonical_parent_sha256: Sha
    catalog_sha256: Sha
    validation_sha256: Sha
    recipe_sha256: Sha
    parents: tuple[Identity, ...]
    sha256: Sha
    byte_length: Annotated[int, Field(gt=0, le=1_048_576)]
    row_count: Annotated[int, Field(gt=0, le=4096)]
    device: Count
    inode: Positive
    ctime_ns: Positive
    storage: Literal["linux_sealed_anonymous_v1"]


class Request(StrictModel):
    schema_version: Literal["cpw_nonholdout_synthetic_v1"]
    purpose: Literal["synthetic_bounded_byte_validation"]
    repository: Literal["toobigtofailbot-maker/crypto-perp-wedge"]
    data_version: Identity
    repo_sha: RepoSha
    campaign_id: Identity
    contamination_domain_id: Identity
    holdout_id: Identity
    envelope_sha256: Sha
    lineage_version: Positive
    lineage_sha256: Sha
    protocol_sha256: Sha
    manifest_sha256: Sha
    feature_manifest_sha256: Sha
    instrument: Literal["BTCUSDT"]
    venue: Literal["Binance USDT-M"]
    market: Literal["perpetual"]
    timeframe: Literal["15m", "30m", "1h", "4h", "1d"]
    evaluation: Interval
    lookback_bars: Count
    # This consumer supports row-local/trailing information only.
    label_horizon_bars: Literal[0]
    fitting: Literal["none"]
    objects: Annotated[tuple[ObjectBinding, ...], Field(min_length=1, max_length=32)]


class Custodian(StrictModel):
    record_id: Identity
    approved_by: Literal["Karl"]
    approval_reference: Identity
    public_key_hex: HexKey
    valid_from_ms: Count
    valid_until_ms: Positive


class Designation(StrictModel):
    record_id: Identity
    approved_by: Literal["Karl"]
    approval_reference: Identity
    custodian_id: Identity
    valid_from_ms: Count
    valid_until_ms: Positive
    request: Request
    protected_mapping_complete: Literal[True]
    protected_intervals: Annotated[tuple[Interval, ...], Field(min_length=1)]


class Revocation(StrictModel):
    record_id: Identity
    approved_by: Literal["Karl"]
    approval_reference: Identity
    target_id: Identity
    # Replacement is revoke old ID + designate a new immutable ID.
    action: Literal["revoke", "replace"]
    successor_id: Identity | None

    @model_validator(mode="after")
    def successor(self):
        if (self.action == "replace") != (self.successor_id is not None):
            raise ValueError("replacement requires successor")
        if self.successor_id == self.target_id:
            raise ValueError("replacement must be distinct")
        return self


class Attestation(StrictModel):
    attestation_id: Identity
    custodian_id: Identity
    designation_id: Identity
    designation_sha256: Sha
    request_sha256: Sha
    valid_from_ms: Count
    valid_until_ms: Positive
    signature_hex: Annotated[str, Field(pattern=r"^[0-9a-f]{128}$")]


def signing_bytes(attestation: Attestation) -> bytes:
    return b"CPW-NONHOLDOUT-02J\x00" + canonical_json(
        attestation.model_dump(mode="json", exclude={"signature_hex"})
    ).encode("ascii")


def synthetic_bytes(obj: ObjectBinding) -> bytes:
    """Closed fixture grammar, no arbitrary fixture label can admit history."""
    step = CADENCE[obj.timeframe]
    rows = ["open_ms,available_ms,value\n"]
    for i in range(obj.row_count):
        opened = obj.interval.start_ms + i * step
        rows.append(f"{opened},{opened + step},{i + 1}\n")
    return "".join(rows).encode("ascii")


def _parse(model, value):
    # Revalidate instances too: model_copy/model_construct must not bypass checks.
    payload = value.model_dump(mode="json") if isinstance(value, StrictModel) else value
    return model.model_validate_json(canonical_json(payload))


def _valid(record, now):
    if not record.valid_from_ms <= now < record.valid_until_ms:
        raise Refused("INACTIVE_EVIDENCE")


def _now(conn):
    return int(
        conn.execute("SELECT extract(epoch FROM clock_timestamp())*1000 AS ms").fetchone()["ms"]
    )


def _code_sha():
    root = Path(__file__).resolve().parents[2]
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True, check=True
    )
    # A commit identity cannot bless modified verifier/dependency bytes.
    subprocess.run(
        ["git", "diff", "--no-ext-diff", "--exit-code", "HEAD", "--", "tools/research_autonomy"],
        cwd=root,
        capture_output=True,
        check=True,
    )
    subprocess.run(
        [
            "git",
            "ls-files",
            "--error-unmatch",
            "tools/research_autonomy/nonholdout_qualification.py",
        ],
        cwd=root,
        capture_output=True,
        check=True,
    )
    return result.stdout.strip()


def _scope(request):
    objects = {obj.object_id: obj for obj in request.objects}
    if len(objects) != len(request.objects):
        raise Refused("DUPLICATE_OBJECT")
    step = CADENCE[request.timeframe]
    start = request.evaluation.start_ms - request.lookback_bars * step
    if start < 0 or request.evaluation.start_ms % step or request.evaluation.end_ms % step:
        raise Refused("WINDOW_GRID")
    execution = [
        o for o in request.objects if o.kind != "feature" and o.timeframe == request.timeframe
    ]
    if len(execution) != 1 or execution[0].interval != Interval(
        start_ms=start, end_ms=request.evaluation.end_ms
    ):
        raise Refused("EFFECTIVE_WINDOW")
    visited, pending = set(), set()

    def visit(obj):
        if obj.object_id in pending:
            raise Refused("ANCESTRY_CYCLE")
        if obj.object_id in visited:
            return
        pending.add(obj.object_id)
        cadence = CADENCE[obj.timeframe]
        if (
            obj.interval.start_ms % cadence
            or obj.interval.end_ms % cadence
            or obj.row_count * cadence != obj.interval.end_ms - obj.interval.start_ms
        ):
            raise Refused("PARTIAL_BAR")
        if obj.kind == "base":
            if (
                obj.parents
                or obj.timeframe not in {"15m", "1d"}
                or obj.canonical_parent_sha256 != obj.canonical_sha256
            ):
                raise Refused("CANONICAL_BASE")
        else:
            if len(obj.parents) != 1 or obj.parents[0] not in objects:
                raise Refused("MISSING_ANCESTRY")
            parent = objects[obj.parents[0]]
            if obj.kind == "derived":
                if (
                    obj.timeframe not in {"30m", "1h", "4h"}
                    or parent.kind != "base"
                    or parent.timeframe != "15m"
                ):
                    raise Refused("D2_021_PARENT")
            elif (
                parent.kind == "feature"
                or parent.timeframe != obj.timeframe
                or parent.interval != obj.interval
            ):
                raise Refused("FEATURE_PARENT")
            if (
                obj.canonical_parent_sha256 != parent.canonical_sha256
                or parent.interval.start_ms > obj.interval.start_ms
                or parent.interval.end_ms < obj.interval.end_ms
            ):
                raise Refused("PARENT_BINDING")
            visit(parent)
        expected = synthetic_bytes(obj)
        if (
            obj.byte_length != len(expected)
            or obj.sha256 != "sha256:" + hashlib.sha256(expected).hexdigest()
        ):
            raise Refused("NOT_SYNTHETIC_BYTES")
        pending.remove(obj.object_id)
        visited.add(obj.object_id)

    for obj in request.objects:
        visit(obj)
    # All inputs must be the execution ancestry or exact row-local features on it.
    used = {execution[0].object_id}
    todo = [execution[0]]
    todo += [
        o for o in request.objects if o.kind == "feature" and o.parents == (execution[0].object_id,)
    ]
    while todo:
        obj = todo.pop()
        used.add(obj.object_id)
        todo.extend(objects[p] for p in obj.parents if p not in used)
    if used != set(objects):
        raise Refused("UNDECLARED_INPUT_USE")


class NonHoldoutQualification:
    def __init__(self, store: ResearchAuthorityStore):
        self.store = store

    def control(self, kind, record):
        """Human control connection only; SQL privileges exclude the operator."""
        models = {"custodian": Custodian, "designation": Designation, "revocation": Revocation}
        try:
            record = _parse(models[kind], record)
            if kind == "designation":
                _scope(record.request)
            raw = record.model_dump(mode="json")
            payload = {
                "record_id": record.record_id,
                "kind": kind,
                "record": raw,
                "content_sha256": content_hash(raw),
            }
            event_id = "nonholdout:" + record.record_id
            with self.store._transaction() as conn:
                # Check privilege even on an idempotent retry.
                allowed = conn.execute(
                    "SELECT has_table_privilege(current_user,'research_authority.nonholdout_control','INSERT') AS ok"
                ).fetchone()["ok"]
                if not allowed:
                    raise Refused("OWNER_CONNECTION_REQUIRED")
                if self.store._replay(conn, event_id, "nonholdout_control", payload):
                    return
                self.store._audit(
                    conn, event_id=event_id, event_type="nonholdout_control", payload=payload
                )
                conn.execute(
                    "INSERT INTO research_authority.nonholdout_control VALUES (%s,%s,%s,%s,%s)",
                    (record.record_id, kind, canonical_json(raw), content_hash(raw), event_id),
                )
        except (KeyError, TypeError, ValueError, OSError, DatabaseError):
            raise Refused("CONTROL_REFUSED") from None

    def _record(self, conn, record_id, kind, model):
        row = conn.execute(
            "SELECT * FROM research_authority.nonholdout_control WHERE record_id=%s AND kind=%s",
            (record_id, kind),
        ).fetchone()
        if row is None:
            raise Refused("UNKNOWN_CONTROL")
        record = _parse(model, json.loads(row["semantic_payload"]))
        if content_hash(record.model_dump(mode="json")) != row["content_sha256"]:
            raise Refused("CONTROL_INTEGRITY")
        self._unrevoked(conn, record_id)
        return record

    @staticmethod
    def _unrevoked(conn, target):
        if conn.execute(
            "SELECT 1 FROM research_authority.nonholdout_control WHERE kind='revocation' AND semantic_payload::jsonb->>'target_id'=%s",
            (target,),
        ).fetchone():
            raise Refused("REVOKED")

    def validate_synthetic(self, *, request, attestation, envelope, repo_sha, handles):
        """Read/use linearizes under the authority lock; return no reusable permit."""
        pinned = []
        try:
            request = _parse(Request, request)
            attestation = _parse(Attestation, attestation)
            if repo_sha != _code_sha():
                raise Refused("STALE_CODE")
            envelope = validate_envelope(envelope, repo_sha=repo_sha)
            if request.repo_sha != repo_sha or request.envelope_sha256 != envelope.content_sha256:
                raise Refused("CODE_ENVELOPE_BINDING")
            if (
                request.instrument not in envelope.surface.instruments
                or request.venue not in envelope.surface.venues
                or request.market not in envelope.surface.market_types
                or any(o.timeframe not in envelope.surface.timeframes for o in request.objects)
            ):
                raise Refused("ENVELOPE_SURFACE")
            _scope(request)
            with self.store._transaction() as conn:
                self.store._active_envelope(conn, envelope)
                if self.store._campaign(conn, request.campaign_id)["state"] != "open":
                    raise Refused("CLOSED_CAMPAIGN")
                snapshot = self.store._snapshot(conn, request.campaign_id)
                if (
                    snapshot.envelope_id != envelope.envelope_id
                    or snapshot.envelope_version != envelope.envelope_version
                    or snapshot.envelope_content_sha256 != request.envelope_sha256
                    or snapshot.contamination_domain_id != request.contamination_domain_id
                    or snapshot.holdout.holdout_id != request.holdout_id
                    or snapshot.lineage_version != request.lineage_version
                    or snapshot.lineage_sha256 != request.lineage_sha256
                    or snapshot.holdout.state != "unexposed"
                    or snapshot.holdout.contaminated
                ):
                    raise Refused("DURABLE_BINDING")
                if request.protocol_sha256 != content_hash(
                    envelope.scientific_protocol.model_dump(mode="json")
                ):
                    raise Refused("PROTOCOL_BINDING")
                designation = self._record(
                    conn, attestation.designation_id, "designation", Designation
                )
                custodian = self._record(conn, attestation.custodian_id, "custodian", Custodian)
                self._unrevoked(conn, attestation.attestation_id)
                if conn.execute(
                    "SELECT 1 FROM research_authority.authority_audit WHERE event_id=%s",
                    ("nonholdout-read:" + attestation.attestation_id,),
                ).fetchone():
                    raise Refused("ATTESTATION_ALREADY_USED")
                if (
                    designation.custodian_id != attestation.custodian_id
                    or designation.request != request
                    or content_hash(designation.model_dump(mode="json"))
                    != attestation.designation_sha256
                    or content_hash(request.model_dump(mode="json")) != attestation.request_sha256
                ):
                    raise Refused("ATTESTATION_BINDING")
                Ed25519PublicKey.from_public_bytes(bytes.fromhex(custodian.public_key_hex)).verify(
                    bytes.fromhex(attestation.signature_hex), signing_bytes(attestation)
                )
                for record in (designation, custodian, attestation):
                    _valid(record, _now(conn))
                for obj in request.objects:
                    horizon = (
                        envelope.scientific_protocol.purge_bars
                        + envelope.scientific_protocol.embargo_bars
                    ) * CADENCE[obj.timeframe]
                    if any(
                        obj.interval.start_ms - horizon < h.end_ms
                        and h.start_ms < obj.interval.end_ms + horizon
                        for h in designation.protected_intervals
                    ):
                        raise Refused("PROTECTED_OVERLAP")
                    if obj.interval.end_ms > _now(conn):
                        raise Refused("INCOMPLETE_AVAILABILITY")
                if sys.platform != "linux":
                    raise Refused("UNSUPPORTED_IMMUTABLE_STORAGE")
                import fcntl

                if not all(
                    hasattr(fcntl, name)
                    for name in (
                        "F_GET_SEALS",
                        "F_SEAL_SEAL",
                        "F_SEAL_WRITE",
                        "F_SEAL_GROW",
                        "F_SEAL_SHRINK",
                    )
                ):
                    raise Refused("UNSUPPORTED_IMMUTABLE_STORAGE")

                if set(handles) != {o.object_id for o in request.objects}:
                    raise Refused("HANDLE_SET")
                # Pin and authenticate ALL dependencies before the first byte read.
                seals = (
                    fcntl.F_SEAL_SEAL | fcntl.F_SEAL_WRITE | fcntl.F_SEAL_GROW | fcntl.F_SEAL_SHRINK
                )
                for obj in request.objects:
                    source = handles[obj.object_id]
                    if type(source) is not int:
                        raise Refused("PATHS_UNSUPPORTED")
                    fd = os.dup(source)
                    pinned.append(fd)
                    facts = os.fstat(fd)
                    if (
                        not stat.S_ISREG(facts.st_mode)
                        or facts.st_nlink != 0
                        or (facts.st_dev, facts.st_ino, facts.st_ctime_ns, facts.st_size)
                        != (obj.device, obj.inode, obj.ctime_ns, obj.byte_length)
                        or fcntl.fcntl(fd, fcntl.F_GET_SEALS) & seals != seals
                    ):
                        raise Refused("UNSEALED_OR_WRONG_OBJECT")
                for obj, fd in zip(request.objects, pinned, strict=True):
                    raw = os.pread(fd, obj.byte_length + 1, 0)
                    if raw != synthetic_bytes(obj):
                        raise Refused("SYNTHETIC_CONTENT_MISMATCH")
                for record in (designation, custodian, attestation):
                    _valid(record, _now(conn))
                # Audit the completed bounded use in the existing campaign chain.
                self.store._audit(
                    conn,
                    event_id="nonholdout-read:" + attestation.attestation_id,
                    event_type="nonholdout_read",
                    payload={
                        "request_sha256": attestation.request_sha256,
                        "attestation": attestation.model_dump(mode="json"),
                    },
                    campaign=self.store._campaign(conn, request.campaign_id),
                )
            return {
                "status": "SYNTHETIC_BYTES_VALIDATED",
                "request_sha256": attestation.request_sha256,
                "object_count": len(request.objects),
                "scientific_status": "NOT_READY",
                "search_contract": "NOT_ISSUABLE",
                "native_handoff": "NATIVE_HANDOFF_NOT_INTEGRATED",
            }
        except (
            AuthorityConflict,
            ValidationError,
            ValueError,
            TypeError,
            OSError,
            InvalidSignature,
            DatabaseError,
            subprocess.SubprocessError,
        ):
            raise Refused("NONHOLDOUT_REFUSED") from None
        finally:
            for fd in pinned:
                os.close(fd)
