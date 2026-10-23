"""OS hard termination and fresh native reconstruction; no journal replay."""
import copy
import hashlib
import json
import os
import subprocess
import time

import pytest

from tools.nautilus_adapter import native_cache_restart as proof
from test_nautilus_n2_02_native_cache import ROOT, child, command, native_source, trader


@pytest.mark.parametrize("scenario", proof.SCENARIOS)
def test_os_crash_after_durable_checkpoint(tmp_path, scenario):
    owner, root = trader(), tmp_path / "crashed"
    log = tmp_path / "producer.log"
    with log.open("w", encoding="utf-8") as output:
        process = subprocess.Popen(command("hold", root, owner, scenario), cwd=ROOT,
                                   stdout=output, stderr=subprocess.STDOUT)
        try:
            deadline = time.monotonic() + 60
            while not (root / "checkpoint.json").exists():
                assert process.poll() is None, log.read_text()
                assert time.monotonic() < deadline, log.read_text()
                time.sleep(.05)
            checkpoint = json.loads((root / "checkpoint.json").read_bytes())
            assert process.pid == checkpoint["pid"] != os.getpid()
            data = (root / "manifest.json").read_bytes()
            assert hashlib.sha256(data).hexdigest() == checkpoint["sha256"]
            manifest = json.loads(data)
            db, _ = proof.backend()
            before = proof.records(db, owner)
            assert before == manifest["records"]
            assert process.poll() is None
            kill_ns = time.time_ns()
            process.kill()  # Windows TerminateProcess of this exact owned Popen handle.
            process.wait(timeout=10)
            assert process.returncode != 0
        finally:
            if process.poll() is None:
                process.kill()
                process.wait(timeout=10)
    first = child("restore", root, owner, checkpoint["sha256"], partial=scenario == "reversal")
    second = child("restore", root, owner, checkpoint["sha256"], partial=scenario == "reversal")
    assert len({process.pid, first["pid"], second["pid"], os.getpid()}) == 4
    assert len({manifest["instance_id"], first["instance_id"], second["instance_id"]}) == 3
    assert first["state_sha256"] == second["state_sha256"] == proof.fixture._hash(manifest["state"])
    assert first["economics"] == second["economics"] == manifest["economics"]
    assert first["new_orders"] == second["new_orders"] == first["new_fills"] == second["new_fills"] == 0
    assert first["status"] == second["status"] == proof.STATUS
    assert first["history_equal"] is second["history_equal"] is (scenario == "round_trip")
    assert first["proof_status"] == second["proof_status"] == (
        "PARTIAL_NATIVE_HISTORY_LOSS" if scenario == "reversal" else "NATIVE_DURABILITY_PROVEN")
    assert checkpoint["time_ns"] <= kill_ns < first["time_ns"]
    assert proof.records(db, owner) == before
    assert (root / "manifest.json").read_bytes() == data
    receipt = {"scenario": scenario, "producer_pid": process.pid, "exit_code": process.returncode,
               "kill_time_ns": kill_ns, "checkpoint": checkpoint, "first": first, "second": second}
    proof.write_json(tmp_path / "crash-receipt.json", receipt)
    print(json.dumps(receipt, sort_keys=True))


@pytest.mark.parametrize("mutation", ["wrong_namespace", "divergent_digest", "expired", "wrong_source"])
def test_checkpoint_rejected_without_original_mutation(tmp_path, native_source, mutation):
    source, owner, result, manifest = native_source
    db, _ = proof.backend()
    before = proof.records(db, owner)
    root = tmp_path / "copy"
    root.mkdir()
    altered = copy.deepcopy(manifest)
    digest = result["sha256"]
    target = owner
    if mutation == "wrong_namespace":
        target = trader()
    elif mutation == "expired":
        altered["time_ns"] = 1
    elif mutation == "wrong_source":
        altered["source"] = "external-journal"
    proof.write_json(root / "manifest.json", altered)
    if mutation in ("expired", "wrong_source"):
        digest = hashlib.sha256((root / "manifest.json").read_bytes()).hexdigest()
    if mutation == "divergent_digest":
        digest = "0" * 64
    child("restore", root, target, digest, succeeds=False)
    assert proof.records(db, owner) == before


@pytest.mark.parametrize("mutation", ["empty", "missing", "corrupt", "truncated"])
def test_disposable_native_record_corruption(tmp_path, native_source, mutation):
    _, valid_owner, _, valid_manifest = native_source
    db, _ = proof.backend()
    valid_before = proof.records(db, valid_owner)
    owner, root = trader(), tmp_path / "negative-producer"
    result = child("produce", root, owner, "round_trip")
    keys = list(proof.records(db, owner))
    order_key = next(k for k in keys if ":orders:" in k)
    if mutation == "empty":
        db.delete(*keys)
    elif mutation == "missing":
        db.delete(next(k for k in keys if ":accounts:" in k))
    elif mutation == "corrupt":
        db.lset(order_key, 0, b"{invalid native event}")
    else:
        db.ltrim(order_key, 0, 0)
    changed = proof.records(db, owner)
    error = child("restore", root, owner, result["sha256"], succeeds=False)
    assert "missing/corrupt native records" in error
    assert proof.records(db, owner) == changed
    assert proof.records(db, valid_owner) == valid_before == valid_manifest["records"]
