"""Original trusted physical receipts -> actual CPW guard -> instrumented inert sink."""
import json
import os
import shutil
import subprocess
import sys
import time
import uuid
from pathlib import Path

import pytest

from src.execution import nautilus_recovery_hold_guard as g
from tools.nautilus_adapter import noncapital_cpw_safety_integration as c


@pytest.fixture(scope="module")
def physical():
    location = os.environ.get("CPW_N4_04_PHYSICAL")
    trusted = os.environ.get("CPW_N4_04_TRUSTED_HOLD")
    if not location:
        pytest.skip("optional physical receipt profile; required for N4-04 acceptance")
    assert trusted, "out-of-band physical trust required"
    root = Path(location)
    before = c.h.inventory(root)
    assert c.h.verify(root, trusted)["status"] == "VERIFIED_HOLD"
    yield root, trusted
    assert c.h.inventory(root) == before


@pytest.fixture
def clone(physical, tmp_path):
    original, trusted = physical
    root = tmp_path / "hold"
    shutil.copytree(original, root)
    return root, trusted


def write(path, value):
    path.write_bytes(c.h.p.encoded(value))


def rehash(root):
    record = c.h.load(root / "supervisor-hold.json")
    record["files"] = {k: v for k, v in c.h.inventory(root).items()
                       if k not in {"supervisor-hold.json", "hold-ack.json"}}
    write(root / "supervisor-hold.json", record)
    trusted = c.h.sha(root / "supervisor-hold.json")
    write(root / "hold-ack.json", {"schema": c.h.SCHEMA, "hold_sha256": trusted,
                                  "sealed_ns": record["sealed_ns"]})
    return trusted


def test_physical_case_bindings_and_real_pre_dispatch_denial(physical):
    root, trusted = physical
    result = c.verify(root, trusted)
    assert result["status"] == c.STATUS and result["state"] == "FROZEN"
    assert set(result["cases"]) == {label for label, *_ in c.h.CASES}
    assert result["binding"]["preack_refused"] is True
    for row in result["cases"].values():
        assert row["refused_attempts"] == 9
        assert not any(row["underlying_calls"].values())
    assert all(result[k] is False for k in ("execution_permit_issued",
               "authenticated_venue_reconciled", "cpw_production_supervisor_connected"))


@pytest.mark.parametrize("mutation", ["digest", "hold", "ack", "schema", "authority",
    "source", "trader", "run", "stale", "inner", "unknown-exposure", "reason"])
def test_actual_original_verifier_rejects_tamper_even_rehashed(clone, mutation):
    root, trusted = clone
    record = c.h.load(root / "supervisor-hold.json")
    if mutation == "digest":
        trusted = "0" * 64
    elif mutation in ("hold", "ack"):
        (root / ("supervisor-hold.json" if mutation == "hold" else "hold-ack.json")).unlink()
    elif mutation in ("schema", "authority", "source", "trader", "run", "reason"):
        key = {"schema": "schema", "authority": "execution_permit_issued",
               "source": "bridge_sha256", "trader": "binding", "run": "binding",
               "reason": "blockers"}[mutation]
        record[key] = True if mutation == "authority" else "forged"
        write(root / "supervisor-hold.json", record)
        trusted = rehash(root)
    else:
        for source in ("native", "source-proofs"):
            target = root / source / "clean-open/manifest.json"
            manifest = c.h.load(target)
            if mutation == "stale":
                manifest["time_ns"] = 1
            elif mutation == "unknown-exposure":
                manifest["state"]["native"]["positions"] = {}
            else:
                manifest["state"]["balance"] = "1"
            write(target, manifest)
            ack = c.h.load(target.with_name("ack.json"))
            ack["sha256"] = c.h.sha(target)
            write(target.with_name("ack.json"), ack)
        trusted = rehash(root)
    before = c.h.inventory(root)
    decision = g.inspect_hold(root, trusted)
    assert not decision.evidence_verified and decision.state.value == "FROZEN"
    assert c.intercept()["refused_attempts"] == 9
    assert c.h.inventory(root) == before


def test_receipt_two_fresh_processes_and_no_original_mutation(physical, tmp_path):
    original, trusted = physical
    output = tmp_path / "decision"
    output.mkdir()
    digest = c.seal(output, original, trusted)
    record = c.h.load(output / "cpw-decision.json")
    results = []
    for _ in range(2):
        command = [sys.executable, "-B", "-m", c.__name__, "inspect-decision",
                   "--original", str(original), "--expected-hold-sha256", trusted,
                   "--decision-output", str(output), "--expected-decision-sha256", digest,
                   "--decision-id", record["decision_id"]]
        result = subprocess.run(command, capture_output=True, text=True, timeout=120, check=False)
        assert result.returncode == 0, result.stdout + result.stderr
        results.append(json.loads(result.stdout))
    assert results[0].pop("pid") != results[1].pop("pid")
    assert results[0] == results[1]
    with pytest.raises(ValueError):
        c.seal(output, original, trusted)


@pytest.mark.parametrize("mutation", ["ack", "torn", "seal", "directory", "replay", "reason", "source"])
def test_decision_seal_ack_and_identity_refuse(physical, tmp_path, mutation):
    original, trusted = physical
    output = tmp_path / "decision"
    output.mkdir()
    digest = c.seal(output, original, trusted)
    record = c.h.load(output / "cpw-decision.json")
    decision_id = record["decision_id"]
    if mutation == "ack":
        (output / "cpw-ack.json").unlink()
    elif mutation == "torn":
        (output / "cpw-ack.json").write_bytes(b'{')
    elif mutation == "seal":
        (output / "cpw-decision.json").unlink()
    elif mutation == "directory":
        substituted = tmp_path / "substituted"
        shutil.copytree(output, substituted)
        output = substituted
    elif mutation == "replay":
        decision_id = str(uuid.uuid4())
    else:
        if mutation == "reason":
            record["decision"]["reason"] = ""
        else:
            record["sources"] = {}
        write(output / "cpw-decision.json", record)
        digest = c.h.sha(output / "cpw-decision.json")
        write(output / "cpw-ack.json", {"schema": c.SCHEMA,
              "decision_sha256": digest, "decision_id": decision_id})
    with pytest.raises((ValueError, OSError, json.JSONDecodeError)):
        c.inspect_decision(output, digest, original, trusted, decision_id)
    assert c.intercept()["refused_attempts"] == 9


def test_crash_before_ack_cannot_verify_or_reseal(physical, tmp_path):
    original, trusted = physical
    output = tmp_path / "decision"
    output.mkdir()
    code = """
import sys,time
from pathlib import Path
from tools.nautilus_adapter import noncapital_cpw_safety_integration as c
atomic = c.atomic
def interrupted(root,name,value):
    atomic(root,name,value)
    if name == 'cpw-decision.json':
        time.sleep(60)
c.atomic = interrupted
c.seal(Path(sys.argv[1]),Path(sys.argv[2]),sys.argv[3])
"""
    process = subprocess.Popen([sys.executable, "-B", "-c", code, str(output),
                                str(original), trusted], stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, text=True)
    try:
        deadline = time.monotonic() + 30
        while not (output / "cpw-decision.json").exists():
            assert process.poll() is None, process.communicate()
            assert time.monotonic() < deadline
            time.sleep(.02)
        process.kill()
        process.wait(timeout=10)
        assert process.returncode != 0
    finally:
        if process.poll() is None:
            process.kill()
        process.communicate(timeout=10)
    record = c.h.load(output / "cpw-decision.json")
    with pytest.raises(ValueError):
        c.inspect_decision(output, c.h.sha(output / "cpw-decision.json"), original,
                           trusted, record["decision_id"])
    with pytest.raises(ValueError):
        c.seal(output, original, trusted)


def test_traversal_repository_and_symlink_refusal(tmp_path):
    with pytest.raises(ValueError):
        c.external(tmp_path / "..")
    with pytest.raises(ValueError):
        c.external(c.h.ROOT)
    if os.name == "nt":
        return  # Linux physical profile executes the required link boundary.
    linked = tmp_path / "linked"
    linked.symlink_to(tmp_path, target_is_directory=True)
    with pytest.raises(ValueError):
        c.external(linked)


@pytest.mark.parametrize("argv", [[], ["run"], ["resume"], ["verify"],
    ["verify", "--original", "/missing", "--expected-hold-sha256", "0" * 64],
    ["run", "--original", "/missing"], ["verify", "--allow-orders"]])
def test_cli_refuses_unknown_or_missing_authority(argv):
    result = subprocess.run([sys.executable, "-B", "-m", c.__name__, *argv],
                            capture_output=True, text=True, timeout=30, check=False)
    assert result.returncode != 0
    assert '"execution_permit_issued": true' not in result.stdout


def test_invalid_output_preflights_before_physical_launch(tmp_path, monkeypatch, capsys):
    launched = []
    monkeypatch.setattr(c.h, "run", lambda *_: launched.append(True))
    assert c.main(["run", "--public-noncapital-proof", "--original", str(tmp_path),
                   "--decision-output", str(tmp_path)]) == 1
    assert launched == []
    assert json.loads(capsys.readouterr().out)["status"] == "BLOCKED"


def test_output_substitution_cannot_write_through_link(physical, tmp_path, monkeypatch):
    if os.name != "posix":
        return  # Emission itself refuses outside the descriptor-supported physical profile.
    original, trusted = physical
    output, moved, victim = (tmp_path / name for name in ("decision", "moved", "victim"))
    output.mkdir()
    victim.mkdir()
    real_verify = c.verify
    def substituted(*args):
        result = real_verify(*args)
        output.rename(moved)
        output.symlink_to(victim, target_is_directory=True)
        return result
    monkeypatch.setattr(c, "verify", substituted)
    with pytest.raises(ValueError):
        c.seal(output, original, trusted)
    assert list(victim.iterdir()) == [] and list(moved.iterdir()) == []


def test_binding_read_cannot_bypass_final_original_equality(clone, monkeypatch):
    root, trusted = clone
    load = c.h.load
    reads = []
    def tampered(path):
        if path == root / "supervisor-hold.json":
            reads.append(path)
            if len(reads) == 2:
                record = load(path)
                record["binding"] = {"forged": True}
                write(path, record)
        return load(path)
    monkeypatch.setattr(c.h, "load", tampered)
    with pytest.raises(ValueError, match="original evidence changed"):
        c.verify(root, trusted)
