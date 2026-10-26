"""Synthetic independent custody, real isolated PostgreSQL, no historical opens."""

import builtins
import hashlib
import io
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Event

import psycopg
import pytest
import test_research_autonomy_postgres as pgtests
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from psycopg.conninfo import make_conninfo

import tools.research_autonomy.nonholdout_qualification as qualification
from tools.research_autonomy.envelope import content_hash
from tools.research_autonomy.nonholdout_qualification import (
    Attestation,
    Custodian,
    Designation,
    Interval,
    NonHoldoutQualification,
    ObjectBinding,
    Refused,
    Request,
    Revocation,
    signing_bytes,
    synthetic_bytes,
)
from tools.research_autonomy.store import ResearchAuthorityStore

H = "sha256:" + "1" * 64
REAL_CODE_SHA = qualification._code_sha
authority_db = pgtests.authority_db
opened = pgtests.opened
LINUX = sys.platform == "linux"
linux_only = pytest.mark.skipif(
    not LINUX, reason="sealed anonymous Linux handles only; Windows denial tested separately"
)


def _sealed(raw, *, seal=True):
    import fcntl

    fd = os.memfd_create("cpw-02j-synthetic", os.MFD_ALLOW_SEALING | os.MFD_CLOEXEC)
    os.write(fd, raw)
    if seal:
        fcntl.fcntl(
            fd,
            fcntl.F_ADD_SEALS,
            fcntl.F_SEAL_SEAL | fcntl.F_SEAL_WRITE | fcntl.F_SEAL_GROW | fcntl.F_SEAL_SHRINK,
        )
    return fd


def _sign(key, attestation):
    return attestation.model_copy(
        update={"signature_hex": key.sign(signing_bytes(attestation)).hex()}
    )


@pytest.fixture
def case(authority_db, tmp_path, monkeypatch):
    _, _, envelope, _, store, _, contract = opened(authority_db, tmp_path, writer=True)
    from tools.research_autonomy.envelope import envelope_hash, validate_envelope

    payload = envelope.model_dump(mode="json")
    payload["envelope_version"] = 2
    payload["surface"]["timeframes"] = ["15m", "30m", "1h", "4h", "1d"]
    payload["content_sha256"] = envelope_hash(payload)
    envelope = validate_envelope(payload, repo_sha=envelope.repo_sha)
    store.register_envelope(envelope)
    snapshot = store.open_campaign(
        envelope,
        campaign_id="CAMPAIGN-PARTITION",
        contamination_domain_id="DOMAIN-FIXTURE",
        holdout_id="HOLDOUT-FIXTURE",
        hypothesis_fingerprint=H,
    )
    # Most cases isolate authority/handles with the existing temporary Git fixture.
    # The separate exact-head case exercises the real source-root Git binding.
    monkeypatch.setattr(qualification, "_code_sha", lambda: envelope.repo_sha)
    owner = NonHoldoutQualification(
        ResearchAuthorityStore(
            make_conninfo(authority_db[0], options="-c role=cpw_nonholdout_owner")
        )
    )
    boundary = NonHoldoutQualification(store)
    key = Ed25519PrivateKey.generate()  # Ephemeral fixture issuer; never persisted.
    now = int(time.time() * 1000)
    custodian = Custodian(
        record_id="CUSTODIAN-TEST",
        approved_by="Karl",
        approval_reference="TEST-ONLY",
        public_key_hex=key.public_key()
        .public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        .hex(),
        valid_from_ms=now - 60_000,
        valid_until_ms=now + 60_000,
    )
    obj = ObjectBinding(
        object_id="BASE-TEST",
        kind="base",
        timeframe="15m",
        interval=Interval(start_ms=1_704_067_200_000, end_ms=1_704_069_900_000),
        canonical_parent_sha256=H,
        canonical_sha256=H,
        catalog_sha256=H,
        validation_sha256=H,
        recipe_sha256=H,
        parents=(),
        sha256=H,
        byte_length=1,
        row_count=3,
        device=0,
        inode=1,
        ctime_ns=1,
        storage="linux_sealed_anonymous_v1",
    )
    raw = synthetic_bytes(obj)
    handles = {obj.object_id: -1}
    if LINUX:
        handles[obj.object_id] = _sealed(raw)
        facts = os.fstat(handles[obj.object_id])
        obj = obj.model_copy(
            update={"device": facts.st_dev, "inode": facts.st_ino, "ctime_ns": facts.st_ctime_ns}
        )
    obj = obj.model_copy(
        update={"sha256": "sha256:" + hashlib.sha256(raw).hexdigest(), "byte_length": len(raw)}
    )
    req = Request(
        schema_version="cpw_nonholdout_synthetic_v1",
        purpose="synthetic_bounded_byte_validation",
        repository="toobigtofailbot-maker/crypto-perp-wedge",
        data_version="SYNTHETIC-V1",
        repo_sha=envelope.repo_sha,
        campaign_id=snapshot.campaign_id,
        contamination_domain_id=snapshot.contamination_domain_id,
        holdout_id=snapshot.holdout.holdout_id,
        envelope_sha256=envelope.content_sha256,
        lineage_version=snapshot.lineage_version,
        lineage_sha256=snapshot.lineage_sha256,
        protocol_sha256=content_hash(envelope.scientific_protocol.model_dump(mode="json")),
        manifest_sha256=H,
        feature_manifest_sha256=H,
        instrument="BTCUSDT",
        venue="Binance USDT-M",
        market="perpetual",
        timeframe="15m",
        evaluation=obj.interval,
        lookback_bars=0,
        label_horizon_bars=0,
        fitting="none",
        objects=(obj,),
    )
    designation = Designation(
        record_id="PARTITION-TEST",
        approved_by="Karl",
        approval_reference="TEST-ONLY",
        custodian_id=custodian.record_id,
        valid_from_ms=now - 60_000,
        valid_until_ms=now + 60_000,
        request=req,
        protected_mapping_complete=True,
        protected_intervals=(Interval(start_ms=1_800_000_000_000, end_ms=1_800_086_400_000),),
    )
    owner.control("custodian", custodian)
    owner.control("designation", designation)
    attestation = _sign(
        key,
        Attestation(
            attestation_id="ATTESTATION-TEST",
            custodian_id=custodian.record_id,
            designation_id=designation.record_id,
            designation_sha256=content_hash(designation.model_dump(mode="json")),
            request_sha256=content_hash(req.model_dump(mode="json")),
            valid_from_ms=now - 60_000,
            valid_until_ms=now + 60_000,
            signature_hex="0" * 128,
        ),
    )
    state = {
        "boundary": boundary,
        "owner": owner,
        "key": key,
        "request": req,
        "attestation": attestation,
        "envelope": envelope,
        "repo_sha": envelope.repo_sha,
        "handles": handles,
        "designation": designation,
        "custodian": custodian,
        "store": store,
        "contract": contract,
    }
    yield state
    if LINUX:
        for fd in handles.values():
            os.close(fd)


def _call(case, **updates):
    args = {k: case[k] for k in ("request", "attestation", "envelope", "repo_sha", "handles")}
    return case["boundary"].validate_synthetic(**(args | updates))


def _no_reads(monkeypatch):
    from tools.research_runner import spec_signal_compiler

    calls = []

    def tripwire(*args, **kwargs):
        calls.append(True)
        raise AssertionError("unqualified source open/read or compiler invocation")

    # PostgreSQL is already imported; it needs no Python file opens for a query.
    schema = (
        Path(__file__).resolve().parents[1]
        / "research/schemas/bounded_research_envelope.schema.json"
    )

    def metadata_only(original):
        def guarded(path, *args, **kwargs):
            if Path(path) == schema:
                return original(path, *args, **kwargs)
            return tripwire()

        return guarded

    monkeypatch.setattr(builtins, "open", metadata_only(builtins.open))
    monkeypatch.setattr(io, "open", metadata_only(io.open))
    monkeypatch.setattr(Path, "open", metadata_only(Path.open))
    monkeypatch.setattr(os, "open", tripwire)
    if hasattr(os, "pread"):
        monkeypatch.setattr(os, "pread", tripwire)
    monkeypatch.setattr(spec_signal_compiler, "compile_signal", tripwire)
    return calls


def _refused(case, monkeypatch, **updates):
    with monkeypatch.context() as context:
        calls = _no_reads(context)
        with pytest.raises(Refused, match="^NONHOLDOUT_REFUSED$") as result:
            _call(case, **updates)
        assert calls == []
        assert result.value.__cause__ is None


@linux_only
def test_positive_sealed_synthetic_and_no_reusable_receipt(case):
    result = _call(case)
    assert result == {
        "status": "SYNTHETIC_BYTES_VALIDATED",
        "request_sha256": case["attestation"].request_sha256,
        "object_count": 1,
        "scientific_status": "NOT_READY",
        "search_contract": "NOT_ISSUABLE",
        "native_handoff": "NATIVE_HANDOFF_NOT_INTEGRATED",
    }
    with pytest.raises(Refused):
        _call(case)  # The completed read advanced durable lineage; old evidence cannot replay.


@pytest.mark.parametrize(
    "field,value",
    [
        ("repo_sha", "0" * 40),
        ("envelope_sha256", H),
        ("protocol_sha256", H),
        ("manifest_sha256", "sha256:" + "2" * 64),
        ("feature_manifest_sha256", "sha256:" + "2" * 64),
        ("campaign_id", "OTHER-CAMPAIGN"),
        ("contamination_domain_id", "OTHER-DOMAIN"),
        ("holdout_id", "OTHER-HOLDOUT"),
        ("lineage_version", 100),
        ("lookback_bars", 1),
        ("label_horizon_bars", 1),
        ("fitting", "global"),
        ("purpose", "historical"),
        ("instrument", "ETHUSDT"),
    ],
)
def test_misbindings_no_opens(case, monkeypatch, field, value):
    _refused(case, monkeypatch, request=case["request"].model_copy(update={field: value}))


@pytest.mark.parametrize(
    "field,value",
    [
        ("custodian_id", "UNKNOWN"),
        ("designation_id", "UNKNOWN"),
        ("signature_hex", "0" * 128),
        ("request_sha256", H),
        ("designation_sha256", H),
        ("valid_until_ms", 1),
        ("valid_from_ms", 9_999_999_999_999),
        ("attestation_id", "REPLAYED-ID"),
    ],
)
def test_forged_expired_mutated_attestation(case, monkeypatch, field, value):
    _refused(case, monkeypatch, attestation=case["attestation"].model_copy(update={field: value}))


@pytest.mark.parametrize("target", ["CUSTODIAN-TEST", "PARTITION-TEST", "ATTESTATION-TEST"])
def test_revocation_is_durable(case, monkeypatch, target):
    record = Revocation(
        record_id="REVOKE-TEST",
        approved_by="Karl",
        approval_reference="TEST-ONLY",
        target_id=target,
        action="revoke",
        successor_id=None,
    )
    case["owner"].control("revocation", record)
    case["owner"].control("revocation", record)  # exact crash/retry is idempotent
    case["boundary"] = NonHoldoutQualification(ResearchAuthorityStore(case["store"]._dsn))
    _refused(case, monkeypatch)


def test_operator_cannot_appoint_or_revoke(case):
    for kind, record in (
        ("custodian", case["custodian"]),
        ("designation", case["designation"]),
        (
            "revocation",
            Revocation(
                record_id="ILLEGAL",
                approved_by="Karl",
                approval_reference="TEST-ONLY",
                target_id="PARTITION-TEST",
                action="revoke",
                successor_id=None,
            ),
        ),
    ):
        with pytest.raises(Refused):
            case["boundary"].control(kind, record)


@pytest.mark.parametrize(
    "mutation", ["unknown", "partial", "parent", "feature", "hidden", "history", "cycle"]
)
def test_invalid_ancestry_and_physical_metadata(case, monkeypatch, mutation):
    req = case["request"].model_dump(mode="json")
    obj = req["objects"][0]
    if mutation == "unknown":
        obj["unrecognized"] = "protected sentinel"
    elif mutation == "partial":
        obj["interval"]["end_ms"] -= 1
    elif mutation == "parent":
        obj.update(kind="derived", timeframe="30m", parents=["MISSING"])
    elif mutation == "feature":
        obj.update(kind="feature", parents=["MISSING"])
    elif mutation == "hidden":
        req["lookback_bars"] = 10
    elif mutation == "history":
        obj["sha256"] = H
    else:
        obj.update(kind="feature", parents=[obj["object_id"]])
    _refused(case, monkeypatch, request=req)


def _redesignate(case, **changes):
    designation = case["designation"].model_copy(
        update={"record_id": "PARTITION-CHANGED", **changes}
    )
    case["owner"].control("designation", designation)
    case["designation"] = designation
    case["request"] = designation.request
    case["attestation"] = _sign(
        case["key"],
        case["attestation"].model_copy(
            update={
                "designation_id": designation.record_id,
                "designation_sha256": content_hash(designation.model_dump(mode="json")),
                "request_sha256": content_hash(designation.request.model_dump(mode="json")),
            }
        ),
    )


@pytest.mark.parametrize("change", ["overlap", "expired", "horizon"])
def test_authenticated_but_unsafe_designation(case, monkeypatch, change):
    obj = case["request"].objects[0]
    updates = (
        {"protected_intervals": (obj.interval,)} if change == "overlap" else {"valid_until_ms": 1}
    )
    if change == "horizon":
        updates = {
            "protected_intervals": (
                Interval(start_ms=obj.interval.end_ms, end_ms=obj.interval.end_ms + 900_000),
            )
        }
        # Fixture approved protocol has explicit purge/embargo bars.
        assert (
            case["envelope"].scientific_protocol.purge_bars
            + case["envelope"].scientific_protocol.embargo_bars
            > 0
        )
    _redesignate(case, **updates)
    _refused(case, monkeypatch)


@linux_only
@pytest.mark.parametrize(
    "change",
    ["different_sealed", "unsealed", "ordinary", "hardlink", "symlink", "path", "swapped_fd"],
)
def test_storage_replacement_refuses_before_read(case, tmp_path, monkeypatch, change):
    obj = case["request"].objects[0]
    fd = None
    if change in {"different_sealed", "unsealed", "swapped_fd"}:
        fd = _sealed(synthetic_bytes(obj), seal=change != "unsealed")
        value = fd
    elif change == "path":
        value = "C:/protected/sentinel.csv"
    else:
        path = tmp_path / "unqualified.csv"
        path.write_text("PROTECTED-SENTINEL")
        if change == "hardlink":
            os.link(path, tmp_path / "alias")
        if change == "symlink":
            link = tmp_path / "symlink"
            link.symlink_to(path)
            path = link
        fd = os.open(path, os.O_RDONLY)
        value = fd
    try:
        _refused(case, monkeypatch, handles={obj.object_id: value})
    finally:
        if fd is not None:
            os.close(fd)


@linux_only
def test_seals_prevent_in_place_and_mmap_mutation(case, monkeypatch):
    import mmap

    fd = next(iter(case["handles"].values()))
    for action in (
        lambda: os.pwrite(fd, b"X", 0),
        lambda: os.ftruncate(fd, 0),
        lambda: mmap.mmap(fd, 0, access=mmap.ACCESS_WRITE),
    ):
        with pytest.raises(OSError):
            action()
    assert os.pread(fd, 1_048_576, 0) == synthetic_bytes(case["request"].objects[0])
    # Linux may advance ctime even on a denied write. Stale identity stays denied.
    _refused(case, monkeypatch)


def test_missing_db_has_bounded_exception(case, monkeypatch, caplog):
    case["boundary"] = NonHoldoutQualification(
        ResearchAuthorityStore("host=127.0.0.1 port=1 dbname=missing_test connect_timeout=1")
    )
    _refused(case, monkeypatch)
    assert "protected" not in caplog.text.lower()


def test_contaminated_domain_cannot_reset_by_campaign(case, monkeypatch):
    case["store"].record_holdout_event(
        case["contract"].search_id, event_id="ESCAPE-TEST", informative_escape=True
    )
    _refused(case, monkeypatch)


@linux_only
def test_crash_rolls_back_read_audit_and_retry_keeps_domain(case, monkeypatch):
    original = case["store"]._audit
    with monkeypatch.context() as context:

        def crash(conn, **kwargs):
            original(conn, **kwargs)
            raise RuntimeError("synthetic crash before commit")

        context.setattr(case["store"], "_audit", crash)
        with pytest.raises(RuntimeError, match="synthetic crash"):
            _call(case)
    assert _call(case)["status"] == "SYNTHETIC_BYTES_VALIDATED"
    assert (
        case["store"].load_snapshot(case["request"].campaign_id).contamination_domain_id
        == case["request"].contamination_domain_id
    )


@linux_only
@pytest.mark.parametrize("operation", ["revoke", "contaminate"])
def test_concurrent_control_serializes_through_byte_use(case, monkeypatch, operation):
    reading, release, control_started = Event(), Event(), Event()
    original = os.pread

    def paused(*args):
        reading.set()
        assert release.wait(10)
        return original(*args)

    def control():
        control_started.set()
        if operation == "revoke":
            case["owner"].control(
                "revocation",
                Revocation(
                    record_id="CONCURRENT",
                    approved_by="Karl",
                    approval_reference="TEST-ONLY",
                    target_id="PARTITION-TEST",
                    action="revoke",
                    successor_id=None,
                ),
            )
        else:
            case["store"].record_holdout_event(
                case["contract"].search_id, event_id="CONCURRENT", informative_escape=True
            )

    monkeypatch.setattr(os, "pread", paused)
    with ThreadPoolExecutor(2) as pool:
        read = pool.submit(_call, case)
        assert reading.wait(10)
        revoked = pool.submit(control)
        assert control_started.wait(10)
        assert not revoked.done()
        release.set()
        assert read.result(timeout=10)["status"] == "SYNTHETIC_BYTES_VALIDATED"
        revoked.result(timeout=10)
    _refused(case, monkeypatch)


def test_unsupported_platform_denies_without_handle_inspection(case, monkeypatch):
    import tools.research_autonomy.nonholdout_qualification as module

    monkeypatch.setattr(module.sys, "platform", "win32")
    _refused(case, monkeypatch)


def test_control_table_append_only_and_writer_privileges(case, authority_db):
    with psycopg.connect(case["store"]._dsn) as conn:
        for privilege in ("INSERT", "UPDATE", "DELETE", "TRUNCATE", "TRIGGER"):
            assert not conn.execute(
                "SELECT has_table_privilege(current_user,'research_authority.nonholdout_control',%s)",
                (privilege,),
            ).fetchone()[0]
    for sql in (
        "DELETE FROM research_authority.nonholdout_control",
        "TRUNCATE research_authority.nonholdout_control",
        "UPDATE research_authority.nonholdout_control SET content_sha256='" + H + "'",
    ):
        with psycopg.connect(authority_db[0]) as conn:
            with pytest.raises(psycopg.Error):
                conn.execute(sql)
            conn.rollback()


@linux_only
def test_exact_head_synthetic_integration(case, monkeypatch):
    from tools.research_autonomy.envelope import canonical_json, envelope_hash
    from tools.research_autonomy.models import BoundedResearchEnvelope

    sha = REAL_CODE_SHA()
    payload = case["envelope"].model_dump(mode="json")
    payload.update(repo_sha=sha, envelope_version=3)
    payload["content_sha256"] = envelope_hash(payload)
    envelope = BoundedResearchEnvelope.model_validate_json(canonical_json(payload))
    store = case["store"]
    store.register_envelope(envelope)
    snapshot = store.open_campaign(
        envelope,
        campaign_id="CAMPAIGN-CURRENT-CODE",
        contamination_domain_id=case["request"].contamination_domain_id,
        holdout_id=case["request"].holdout_id,
        hypothesis_fingerprint=H,
    )
    request = case["request"].model_copy(
        update={
            "repo_sha": sha,
            "envelope_sha256": envelope.content_sha256,
            "campaign_id": snapshot.campaign_id,
            "lineage_version": snapshot.lineage_version,
            "lineage_sha256": snapshot.lineage_sha256,
        }
    )
    _redesignate(case, request=request)
    monkeypatch.setattr(qualification, "_code_sha", REAL_CODE_SHA)
    assert _call(case, envelope=envelope, repo_sha=sha)["status"] == "SYNTHETIC_BYTES_VALIDATED"


@linux_only
@pytest.mark.parametrize("bad_dependency", [False, True])
def test_transitive_derived_feature_positive(case, monkeypatch, bad_dependency):
    parent = case["request"].objects[0]
    end = parent.interval.start_ms + 6 * 900_000
    interval = Interval(start_ms=parent.interval.start_ms, end_ms=end)
    objects = []
    for identity, kind, timeframe, parents, rows in (
        ("PARENT-15M", "base", "15m", (), 6),
        ("DERIVED-30M", "derived", "30m", ("PARENT-15M",), 3),
        ("FEATURE-30M", "feature", "30m", ("DERIVED-30M",), 3),
    ):
        obj = parent.model_copy(
            update={
                "object_id": identity,
                "kind": kind,
                "timeframe": timeframe,
                "parents": parents,
                "interval": interval,
                "row_count": rows,
                "canonical_sha256": {
                    "base": H,
                    "derived": "sha256:" + "2" * 64,
                    "feature": "sha256:" + "3" * 64,
                }[kind],
                "canonical_parent_sha256": "sha256:" + "2" * 64 if kind == "feature" else H,
            }
        )
        raw = synthetic_bytes(obj)
        fd = _sealed(raw)
        case["handles"][identity] = fd
        facts = os.fstat(fd)
        objects.append(
            obj.model_copy(
                update={
                    "sha256": "sha256:" + hashlib.sha256(raw).hexdigest(),
                    "byte_length": len(raw),
                    "device": facts.st_dev,
                    "inode": facts.st_ino,
                    "ctime_ns": facts.st_ctime_ns,
                }
            )
        )
    os.close(case["handles"].pop(parent.object_id))
    request = case["request"].model_copy(
        update={"objects": tuple(objects), "timeframe": "30m", "evaluation": interval}
    )
    _redesignate(case, request=request)
    if bad_dependency:
        handles = case["handles"] | {"FEATURE-30M": case["handles"]["PARENT-15M"]}
        _refused(case, monkeypatch, handles=handles)
    else:
        assert _call(case)["object_count"] == 3


def test_current_code_cannot_be_self_declared(case, monkeypatch):
    monkeypatch.setattr(qualification, "_code_sha", lambda: "2" * 40)
    _refused(case, monkeypatch)


@linux_only
@pytest.mark.parametrize("kind", ["ordinary", "hardlink", "unsealed"])
def test_authentic_identity_still_requires_anonymous_seals(case, tmp_path, monkeypatch, kind):
    obj = case["request"].objects[0]
    if kind == "unsealed":
        fd = _sealed(synthetic_bytes(obj), seal=False)
    else:
        path = tmp_path / "synthetic-unqualified"
        path.write_bytes(synthetic_bytes(obj))
        if kind == "hardlink":
            os.link(path, tmp_path / "alias")
        fd = os.open(path, os.O_RDONLY)
    try:
        facts = os.fstat(fd)
        obj = obj.model_copy(
            update={"device": facts.st_dev, "inode": facts.st_ino, "ctime_ns": facts.st_ctime_ns}
        )
        _redesignate(case, request=case["request"].model_copy(update={"objects": (obj,)}))
        _refused(case, monkeypatch, handles={obj.object_id: fd})
    finally:
        os.close(fd)


@pytest.mark.parametrize(
    "path",
    [
        r"C:\protected\sentinel.csv",
        r"\\server\share\sentinel",
        "../sentinel",
        "file:stream",
        "junction/sentinel",
        "symlink/sentinel",
    ],
)
def test_no_path_alias_can_enter_handle_consumer(case, monkeypatch, path):
    _refused(case, monkeypatch, handles={case["request"].objects[0].object_id: path})


@pytest.mark.parametrize("state", ["expired", "wrong_key"])
def test_owner_designated_bad_custodian(case, monkeypatch, state):
    custodian = case["custodian"].model_copy(
        update={
            "record_id": "OTHER-CUSTODIAN",
            **({"valid_until_ms": 1} if state == "expired" else {"public_key_hex": "1" * 64}),
        }
    )
    case["owner"].control("custodian", custodian)
    _redesignate(case, custodian_id=custodian.record_id)
    case["attestation"] = _sign(
        case["key"], case["attestation"].model_copy(update={"custodian_id": custodian.record_id})
    )
    _refused(case, monkeypatch)


@linux_only
def test_reused_attestation_id_denied_before_new_read(case, monkeypatch):
    _call(case)
    snapshot = case["store"].load_snapshot(case["request"].campaign_id)
    _redesignate(
        case,
        request=case["request"].model_copy(
            update={
                "lineage_version": snapshot.lineage_version,
                "lineage_sha256": snapshot.lineage_sha256,
            }
        ),
    )
    _refused(case, monkeypatch)
