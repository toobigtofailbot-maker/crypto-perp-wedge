"""Denial-only contract, real-source mutations and fresh offline inspections."""
import copy
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

import pytest

from tools.nautilus_adapter import noncapital_supervisor_hold as h


def write(path, value):
    path.write_bytes(h.p.encoded(value))


def cli(*args):
    return subprocess.run([sys.executable, "-B", "-m", h.__name__, *map(str, args)],
                          capture_output=True, text=True, timeout=60, check=False)


@pytest.mark.parametrize("args", [[], ["run"], ["verify"], ["resume"],
    ["run", "--output", "/tmp/uncreated-n4-03"],
    ["verify", "--output", "/tmp/uncreated-n4-03"],
    ["run", "--public-noncapital-proof", "--output", "/tmp/uncreated-n4-03", "--venue", "BINANCE"]])
def test_cli_defaults_and_unknown_authority_refuse(args):
    assert cli(*args).returncode != 0


def test_missing_proof_and_digest_refuse_without_writes(tmp_path):
    for trusted in (None, "", "0" * 64, "A" * 64):
        with pytest.raises((ValueError, FileNotFoundError)):
            h.verify(tmp_path, trusted)
    assert list(tmp_path.iterdir()) == []


def test_output_rejects_repository_nonempty_and_links(tmp_path):
    with pytest.raises(ValueError):
        h.external(h.ROOT)
    other_repo = tmp_path / "other-repo"
    other_repo.mkdir()
    (other_repo / ".git").write_text("gitdir: elsewhere")
    child = other_repo / "output"
    child.mkdir()
    with pytest.raises(ValueError):
        h.external(child)
    (tmp_path / "retain").write_text("owned")
    with pytest.raises(ValueError):
        h.external(tmp_path, empty=True)
    assert (tmp_path / "retain").read_text() == "owned"
    link = tmp_path / "link"
    try:
        link.symlink_to(child, target_is_directory=True)
    except OSError:
        return  # Windows symlink privileges are optional; Linux physical profile checks this.
    with pytest.raises(ValueError):
        h.external(link)


@pytest.mark.parametrize("raw", [b'{"x":1,"x":2}', b'{"x":NaN}', b'{"x":Infinity}', b'{"torn":'])
def test_strict_json_refuses_duplicate_nonfinite_and_torn(tmp_path, raw):
    target = tmp_path / "input.json"
    target.write_bytes(raw)
    with pytest.raises((ValueError, json.JSONDecodeError)):
        h.load(target)
    assert target.read_bytes() == raw


@pytest.mark.parametrize("value", [{}, {"pid": 1}, {"pid": True, "pid_namespace": "pid:[1]"},
    {"pid": 0, "pid_namespace": "pid:[1]"}, {"pid": 1, "pid_namespace": ""},
    {"pid": 1, "pid_namespace": "pid:[1]", "permit": True}])
def test_process_identity_requires_real_namespace_shape(value):
    with pytest.raises(ValueError):
        h.identity(value)


def test_no_protected_consumer_or_account_imports():
    text = Path(h.__file__).read_text()
    for token in ("from src", "import src", "from lib", "BinanceExecutionClient", "os.environ",
                  "api_key", "api_secret", "signed_request", "ALLOW", "SAFE_TO_RESUME", "TRADING_READY"):
        assert token not in text
    assert h.DENIAL["authority"] == h.p.AUTHORITY
    assert h.DENIAL["disposition"] == "HOLD"
    assert all(h.DENIAL[k] is False for k in ("cpw_production_supervisor_connected",
               "authenticated_venue_reconciled", "execution_permit_issued"))


@pytest.fixture(scope="module")
def physical():
    location = os.environ.get("CPW_N4_03_PHYSICAL")
    if not location:
        pytest.skip("physical profile requires CPW_N4_03_PHYSICAL; not physical acceptance")
    root = Path(location)
    assert root.is_dir(), "configured physical evidence absent"
    trusted = h.sha(root / "supervisor-hold.json")
    assert h.verify(root, trusted)["status"] == "VERIFIED_HOLD"
    return root, trusted, h.inventory(root)


@pytest.fixture
def clone(physical, tmp_path):
    source, _, before = physical
    root = tmp_path / "disposable-clone"
    shutil.copytree(source, root)
    yield root
    assert h.inventory(source) == before, "mutation touched counted physical source"


def reseal_outer(root, change=None):
    """Recompute untrusted outer hashes so tests reach semantic checks."""
    record = h.load(root / "supervisor-hold.json")
    if change:
        change(record)
    record["files"] = {k: v for k, v in h.inventory(root).items()
                       if k not in {"supervisor-hold.json", "hold-ack.json"}}
    write(root / "supervisor-hold.json", record)
    trusted = h.sha(root / "supervisor-hold.json")
    write(root / "hold-ack.json", {"schema": h.SCHEMA, "hold_sha256": trusted,
                                   "sealed_ns": record["sealed_ns"]})
    return trusted


def mutate_native(root, change):
    for folder in ("native", "source-proofs"):
        change(root / folder)
    return reseal_outer(root)


def mutate_manifest(root, change):
    def apply(native):
        path = native / "clean-open" / "manifest.json"
        manifest = h.load(path)
        change(manifest)
        manifest["chain"][0]["payload"] = manifest["instrument"]
        for i, quote in enumerate(manifest["quotes"], 1):
            manifest["chain"][i]["payload"] = quote
        manifest["chain"][-2]["payload"] = manifest["state"]
        manifest["chain"][-1]["payload"] = manifest["records"]
        for i, row in enumerate(manifest["chain"]):
            row["previous"] = manifest["chain"][i - 1]["sha256"] if i else None
            row["sha256"] = h.p.digest({k: v for k, v in row.items() if k != "sha256"})
        old = h.sha(path)
        write(path, manifest)
        new = h.sha(path)
        for target in native.rglob("*.json"):
            if target != path:
                raw = target.read_bytes()
                if old.encode() in raw:
                    target.write_bytes(raw.replace(old.encode(), new.encode()))
        write(native / "clean-open" / "ack.json", {**h.p.LABELS, "pid": manifest["pid"],
              "sha256": new, "run_id": manifest["run_id"]})
    return mutate_native(root, apply)


def test_real_matrix_is_denial_only_and_source_bound(physical):
    root, trusted, before = physical
    result = h.verify(root, trusted)
    assert result["status"] == "VERIFIED_HOLD"
    assert result["inspection"] == "OFFLINE_ARTIFACT_ONLY_NOT_FRESH_NATIVE_RECOVERY"
    assert all(result[k] == value for k, value in h.DENIAL.items())
    assert all(type(result[k]) is int and result[k] == 0 for k in h.ZERO)
    record = h.load(root / "supervisor-hold.json")
    assert [c["case"] for c in record["binding"]["cases"]] == ["clean-open", "clean-flat", "ack-kill"]
    assert record["binding"]["preack_refused"] is True
    assert record["binding"]["cleanup_verified"] is True
    assert h.inventory(root) == before


def test_two_fresh_offline_verifiers_are_idempotent_without_engine(physical):
    root, trusted, before = physical
    code = ("import json,socket,subprocess,sys; from tools.nautilus_adapter import noncapital_supervisor_hold as h; "
            "deny=lambda *a,**k: (_ for _ in ()).throw(AssertionError('network/engine/process action')); "
            "socket.socket=deny; h.p.node=deny; subprocess.Popen=deny; "
            "print(json.dumps(h.verify(sys.argv[1],sys.argv[2])))")
    results = []
    for _ in range(2):
        run = subprocess.run([sys.executable, "-B", "-c", code, str(root), trusted],
                             capture_output=True, text=True, timeout=60, check=False)
        assert run.returncode == 0, run.stdout + run.stderr
        results.append(json.loads(run.stdout))
    assert len({r["pid"] for r in results} | {os.getpid()}) == 3
    assert all(r["status"] == "VERIFIED_HOLD" for r in results)
    assert h.inventory(root) == before


@pytest.mark.parametrize("mutation", ["missing-hold", "torn-hold", "missing-ack", "torn-ack", "wrong-digest", "tamper", "alien", "copy-mismatch"])
def test_untrusted_missing_torn_and_alien_material_blocks(clone, mutation):
    trusted = h.sha(clone / "supervisor-hold.json")
    target = clone / "supervisor-hold.json"
    if mutation == "missing-hold":
        target.unlink()
    elif mutation == "torn-hold":
        target.write_bytes(b'{"torn":')
        trusted = h.sha(target)
    elif mutation == "missing-ack":
        (clone / "hold-ack.json").unlink()
    elif mutation == "torn-ack":
        (clone / "hold-ack.json").write_bytes(b'{"torn":')
    elif mutation == "wrong-digest":
        trusted = "0" * 64
    elif mutation == "tamper":
        with (clone / "native" / "cleanup.json").open("ab") as stream:
            stream.write(b" ")
    elif mutation == "alien":
        (clone / "alien.json").write_text("{}")
        trusted = reseal_outer(clone)
    else:
        (clone / "native" / "cleanup.json").write_text("{}")
        trusted = reseal_outer(clone)
    result = cli("verify", "--output", clone, "--expected-hold-sha256", trusted)
    assert result.returncode == 1, result.stdout + result.stderr
    outcome = json.loads(result.stdout)
    assert outcome["status"] == "BLOCKED" and outcome["execution_permit_issued"] is False


@pytest.mark.parametrize("field,value", [("schema", "unknown_v2"), ("disposition", "READY"),
    ("authenticated_venue_reconciled", True), ("cpw_production_supervisor_connected", True),
    ("execution_permit_issued", True), ("order_authority", True),
    ("n3_05_status", "ADMITTED_FOR_OBSERVATION_ONLY"), ("blockers", []),
    ("bridge_sha256", "0" * 64), ("authority", "NO_NEW_ORDERS")])
def test_rehashed_outer_authority_and_schema_forgery_blocks(clone, field, value):
    trusted = reseal_outer(clone, lambda record: record.__setitem__(field, value))
    with pytest.raises(ValueError):
        h.verify(clone, trusted)


@pytest.mark.parametrize("mutation", ["balance", "fee", "position", "source", "version", "lock-version",
    "environment-authority", "provider", "missing-quote", "stale-quote", "stale-checkpoint",
    "process-namespace", "duplicate-event", "requests-signed"])
def test_rehashed_native_semantic_contradictions_block(clone, mutation):
    def change(m):
        if mutation == "balance":
            m["state"]["balance"] = "10000"
        elif mutation == "fee":
            order = next(iter(m["state"]["native"]["orders"].values()))
            next(e for e in order["events"] if e["type"] == "OrderFilled")["commission"] = "1 USDT"
        elif mutation == "position":
            next(iter(m["state"]["native"]["positions"].values()))["state"]["signed_qty"] = 2
        elif mutation == "source":
            m["sources"]["noncapital_persistent_session.py"] = "0" * 64
        elif mutation == "version":
            m["environment"]["versions"]["nautilus-trader"] = "1.999.0"
        elif mutation == "lock-version":
            name = next(k for k in m["environment"]["versions"] if k not in {"nautilus-trader", "pyarrow"})
            m["environment"]["versions"][name] = "unapproved-version"
        elif mutation == "environment-authority":
            m["environment"]["execution_permit_issued"] = True
        elif mutation == "provider":
            m["quotes"][0]["native_type"] = "synthetic.QuoteTick"
        elif mutation == "missing-quote":
            m["quotes"] = []
        elif mutation == "stale-quote":
            m["quotes"][0]["observed_ns"] += 60_000_000_000
        elif mutation == "stale-checkpoint":
            m["time_ns"] -= 3_600_000_000_001
        elif mutation == "process-namespace":
            m["process"]["pid_namespace"] = ""
        elif mutation == "duplicate-event":
            order = next(iter(m["state"]["native"]["orders"].values()))
            order["events"].append(copy.deepcopy(order["events"][-1]))
        else:
            m["requests"][0]["signed"] = True
    trusted = mutate_manifest(clone, change)
    with pytest.raises(ValueError):
        h.verify(clone, trusted)


def test_rehashed_publication_must_equal_actual_native_event(clone):
    def change(manifest):
        event = next(row["payload"] for row in manifest["chain"]
                     if isinstance(row["payload"], dict) and row["payload"].get("type") == "OrderFilled")
        event["commission"] = "999 USDT"
    mutate_manifest(clone, change)
    native = clone / "source-proofs" / "clean-open"
    sealed_ns = h.load(clone / "supervisor-hold.json")["sealed_ns"]
    with pytest.raises(ValueError, match="publication"):
        h.checkpoint(native, h.sha(native / "manifest.json"), sealed_ns)


def test_rehashed_producer_pid_must_equal_physical_producer_receipt(clone):
    def change(manifest):
        manifest["pid"] = 999999
        manifest["process"]["pid"] = 999999
    mutate_manifest(clone, change)
    sealed_ns = h.load(clone / "supervisor-hold.json")["sealed_ns"]
    with pytest.raises(ValueError, match="producer"):
        h.inspect_native(clone / "source-proofs", sealed_ns)


def test_rehashed_preack_reader_cannot_smuggle_authority(clone):
    def change(native):
        target = native / "preack-kill-result.json"
        result = h.load(target)
        result["readers"][0]["execution_permit_issued"] = True
        write(target, result)
        summary_path = native / "controller-result.json"
        summary = h.load(summary_path)
        summary["cases"][-1] = result
        write(summary_path, summary)
        for command in sorted(native.glob("command-*.json")):
            receipt = h.load(command)
            if "restore" in receipt["argv"] and "/tmp/proof/preack-kill" in receipt["argv"]:
                lines = receipt["stdout"].splitlines()
                lines[-1] = json.dumps(result["readers"][0])
                receipt["stdout"] = "\n".join(lines) + "\n"
                write(command, receipt)
                break
    trusted = mutate_native(clone, change)
    with pytest.raises(ValueError):
        h.verify(clone, trusted)


def test_rehashed_future_supervisor_seal_is_invalid(clone):
    trusted = reseal_outer(clone, lambda record: record.__setitem__("sealed_ns", time.time_ns() + 60_000_000_000))
    with pytest.raises(ValueError):
        h.verify(clone, trusted)


@pytest.mark.parametrize("mutation", ["refusal-error", "integrity-reader-action"])
def test_all_native_refusals_and_integrity_reload_are_bound(clone, mutation):
    def change(native):
        matches = []
        target = "/tmp/proof/refusal-missing-record" if mutation == "refusal-error" else "/tmp/proof/clean-open"
        for command in sorted(native.glob("command-*.json")):
            receipt = h.load(command)
            if "restore" in receipt["argv"] and target in receipt["argv"]:
                matches.append((command, receipt))
        command, receipt = matches[0] if mutation == "refusal-error" else matches[2]
        result = h.last(receipt)
        if mutation == "refusal-error":
            result["error"] = "forged negative without original recovery failure"
        else:
            result["native_commands"] = 1
        lines = receipt["stdout"].splitlines()
        lines[-1] = json.dumps(result)
        receipt["stdout"] = "\n".join(lines) + "\n"
        write(command, receipt)
    trusted = mutate_native(clone, change)
    with pytest.raises(ValueError, match="refusal|reader"):
        h.verify(clone, trusted)


@pytest.mark.parametrize("mutation", ["missing-case", "missing-native-ack", "label", "same-reader", "reader-conflict", "acl", "cleanup", "duplicate-file"])
def test_rehashed_physical_receipt_contradictions_block(clone, mutation):
    def change(native):
        if mutation == "missing-case":
            (native / "clean-flat-result.json").unlink()
        elif mutation == "missing-native-ack":
            (native / "clean-open" / "ack.json").unlink()
        elif mutation == "duplicate-file":
            shutil.copyfile(native / "clean-open-result.json", native / "duplicate-result.json")
        elif mutation == "cleanup":
            value = h.load(native / "cleanup.json")
            value["removed"] += 1
            write(native / "cleanup.json", value)
        elif mutation == "acl":
            for command in native.glob("command-*.json"):
                value = h.load(command)
                if "acl_log()" in value["argv"][-1]:
                    value["stdout"] = '[{"reason":"command","object":"SET"}]\n'
                    write(command, value)
                    break
        else:
            path = native / "clean-open-result.json"
            value = h.load(path)
            if mutation == "label":
                value["status"] = "FORGED_PROVEN"
            elif mutation == "same-reader":
                value["readers"][1]["pid"] = value["readers"][0]["pid"]
                value["readers"][1]["process"] = value["readers"][0]["process"]
            else:
                value["readers"][1]["native"]["balance"] = "10000"
            write(path, value)
            summary_path = native / "controller-result.json"
            summary = h.load(summary_path)
            summary["cases"][0] = value
            write(summary_path, summary)
            reads = []
            for command in sorted(native.glob("command-*.json")):
                receipt = h.load(command)
                if "restore" in receipt["argv"] and "/tmp/proof/clean-open" in receipt["argv"]:
                    reads.append((command, receipt))
            for (command, receipt), reader in zip(reads[:2], value["readers"]):
                lines = receipt["stdout"].splitlines()
                lines[-1] = json.dumps(reader)
                receipt["stdout"] = "\n".join(lines) + "\n"
                write(command, receipt)
    trusted = mutate_native(clone, change)
    with pytest.raises((ValueError, FileNotFoundError)):
        h.verify(clone, trusted)


def test_genuine_os_kill_between_hold_and_ack_never_verifies(physical, tmp_path):
    source, _, before = physical
    root = tmp_path / "interrupted-seal"
    root.mkdir()
    shutil.copytree(source / "native", root / "native")
    marker = tmp_path / "seal-written"
    code = """
import sys,time
from pathlib import Path
from tools.nautilus_adapter import noncapital_supervisor_hold as h
original = h.durable
def interrupted(path,value):
    original(path,value)
    if path.name == 'supervisor-hold.json':
        Path(sys.argv[2]).write_text('hold-written-before-ack')
        time.sleep(60)
h.durable = interrupted
h.seal(Path(sys.argv[1]))
"""
    process = subprocess.Popen([sys.executable, "-B", "-c", code, str(root), str(marker)],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        deadline = time.monotonic() + 30
        while not marker.exists():
            assert process.poll() is None, process.communicate()
            assert time.monotonic() < deadline, "supervisor seal checkpoint absent"
            time.sleep(.02)
        process.kill()
        process.wait(timeout=10)
        assert process.returncode != 0
    finally:
        if process.poll() is None:
            process.kill()
            process.wait(timeout=10)
        process.communicate()
    assert (root / "supervisor-hold.json").exists()
    assert not (root / "hold-ack.json").exists()
    with pytest.raises((ValueError, FileNotFoundError)):
        h.verify(root, h.sha(root / "supervisor-hold.json"))
    assert h.inventory(source) == before
