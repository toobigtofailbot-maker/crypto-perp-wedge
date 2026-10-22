"""Fresh-process replay of retained native evidence; no operational restart claim."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from tools.nautilus_adapter import paper_sandbox as proof

ROOT = Path(__file__).resolve().parents[1]


def _child(action, directory, binding):
    # No exchange credential environment is propagated to a proof process.
    env = {key: os.environ[key] for key in ("SystemRoot", "WINDIR", "TEMP", "TMP", "PATH") if key in os.environ}
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    if action == "replay":
        code = """
import sys
class NoNativeOrRuntime:
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in ('nautilus_trader', 'src', 'lib'):
            raise RuntimeError('replay forbids native adapters and production runtime')
sys.meta_path.insert(0, NoNativeOrRuntime())
from tools.nautilus_adapter.paper_sandbox import _main
_main()
"""
        command = [sys.executable, "-B", "-c", code, action, str(directory), binding]
    else:
        command = [sys.executable, "-B", "-m", "tools.nautilus_adapter.paper_sandbox", action, str(directory), binding]
    completed = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, text=True, timeout=60)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    return json.loads(completed.stdout.splitlines()[-1])


@pytest.mark.parametrize("scenario", proof.SCENARIOS)
def test_fresh_process_reconstruction_no_execution(tmp_path, scenario):
    root = tmp_path / "episode"
    producer = _child("episode", root, scenario)
    binding = producer["result"]["manifest_sha256"]
    before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in root.iterdir()}
    first = _child("replay", root, binding)
    second = _child("replay", root, binding)
    assert len({os.getpid(), producer["pid"], first["pid"], second["pid"]}) == 4
    assert producer["native_loaded"] is True
    assert first["native_loaded"] is second["native_loaded"] is False
    assert proof._bytes(first["result"]) == proof._bytes(second["result"])
    assert first["result"]["checkpoints"][-1] == producer["result"]["source_observation"]
    assert first["result"]["new_orders"] == first["result"]["new_fills"] == first["result"]["adapter_calls"] == 0
    assert before == {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in root.iterdir()}
    receipt = {"producer": producer, "first_replay": first, "second_replay": second,
               "projection_sha256": proof._hash(first["result"]), "immutable_files": before}
    (tmp_path / "process-receipt.json").write_bytes(proof._bytes(receipt))
    print(json.dumps(receipt, sort_keys=True))


@pytest.fixture(scope="module")
def retained_episode(tmp_path_factory):
    root = tmp_path_factory.mktemp("native-negative-source")
    episode = root / "episode"
    result = proof._run_episode(episode, "round_trip")
    return episode, result["manifest_sha256"]


def _copy(source, destination):
    destination.mkdir()
    for name in ("manifest.json", "events.jsonl"):
        (destination / name).write_bytes((source / name).read_bytes())


def _rebind(root, rows, manifest):
    # Deliberately recompute outer integrity to test semantic checks, not only byte tampering.
    for seq, row in enumerate(rows):
        row["seq"] = seq
        row["previous"] = rows[seq-1]["sha256"] if seq else None
        row["observation_key"] = proof._observation_key(row["payload"], seq)
        row["sha256"] = proof._hash({k: v for k, v in row.items() if k != "sha256"})
    data = b"".join(proof._bytes(row) + b"\n" for row in rows)
    (root / "events.jsonl").write_bytes(data)
    manifest["journal_sha256"] = hashlib.sha256(data).hexdigest()
    manifest["event_count"] = len(rows)
    manifest["tail"] = rows[-1]["sha256"]
    data = proof._bytes(manifest)
    (root / "manifest.json").write_bytes(data)
    return hashlib.sha256(data).hexdigest()


@pytest.mark.parametrize("mutation", ["duplicate_fill", "duplicate_order", "unknown_order", "wrong_currency",
    "nonfinite", "negative_qty", "wrong_quantity_unit", "negative_fee", "wrong_fee", "wrong_source",
    "wrong_version", "mixed_scenario", "unknown_event", "reordered", "missing_fill", "missing_position",
    "wrong_balance", "wrong_position", "stale_snapshot", "wrong_account", "wrong_instrument", "wrong_time",
    "duplicate_trade_id_new_event", "duplicate_order_new_event", "duplicate_account", "wrong_manifest_version",
    "wrong_commission_currency", "nonfinite_margin", "wrong_balance_currency", "authority_drift"])
def test_semantic_corruption_rejected_even_with_rehashed_chain(tmp_path, retained_episode, mutation):
    source, _ = retained_episode
    root = tmp_path / "copy"
    _copy(source, root)
    manifest = json.loads((root / "manifest.json").read_bytes())
    rows = [json.loads(line) for line in (root / "events.jsonl").read_bytes().splitlines()]
    fill_index = next(i for i, r in enumerate(rows) if r["payload"]["type"] == "OrderFilled")
    fill = rows[fill_index]["payload"]
    if mutation == "duplicate_fill":
        rows.insert(fill_index + 1, json.loads(json.dumps(rows[fill_index])))
    elif mutation == "duplicate_order":
        rows.insert(2, json.loads(json.dumps(rows[1])))
    elif mutation == "unknown_order": fill["client_order_id"] = "UNKNOWN"
    elif mutation == "wrong_currency": fill["currency"] = "BTC"
    elif mutation == "nonfinite": fill["last_px"] = "NaN"
    elif mutation == "negative_qty": fill["last_qty"] = "-1.000"
    elif mutation == "wrong_quantity_unit": fill["last_qty"] = "1000.000"
    elif mutation == "negative_fee": fill["commission"] = "-0.04 USDT"
    elif mutation == "wrong_fee": fill["commission"] = "0.05 USDT"
    elif mutation == "wrong_source": rows[fill_index]["source"] = "other"
    elif mutation == "wrong_version": rows[fill_index]["version"] = "2.0.0"
    elif mutation == "mixed_scenario": rows[fill_index]["scenario"] = "reversal"
    elif mutation == "unknown_event": fill["type"] = "HypotheticalFill"
    elif mutation == "reordered": rows[1], rows[2] = rows[2], rows[1]
    elif mutation == "missing_fill": rows.pop(fill_index)
    elif mutation == "missing_position": rows.pop()
    elif mutation == "wrong_balance": rows[0]["payload"]["balances"][0]["total"] = "9999"
    elif mutation == "wrong_position": rows[-1]["payload"]["signed_qty"] = 1.0
    elif mutation == "stale_snapshot": manifest["checkpoints"][-1]["native"]["equity"] = "10000"
    elif mutation == "wrong_account": fill["account_id"] = "BINANCE-001"
    elif mutation == "wrong_instrument": fill["instrument_id"] = "BTCUSDT.BINANCE"
    elif mutation == "wrong_time": fill["ts_init"] = -1
    elif mutation == "duplicate_trade_id_new_event":
        next(r["payload"] for r in rows[fill_index+1:] if r["payload"]["type"] == "OrderFilled")["trade_id"] = fill["trade_id"]
    elif mutation == "duplicate_order_new_event":
        duplicate = json.loads(json.dumps(rows[1]))
        duplicate["payload"]["event_id"] = "different-native-id"
        rows.insert(2, duplicate)
    elif mutation == "duplicate_account":
        rows.insert(1, json.loads(json.dumps(rows[0])))
    elif mutation == "wrong_manifest_version": manifest["version"] = "2.0.0"
    elif mutation == "wrong_commission_currency": fill["commission"] = "0.04 BTC"
    elif mutation == "nonfinite_margin":
        next(r["payload"] for r in rows if r["payload"]["type"] == "AccountState" and r["payload"]["margins"])["margins"][0]["initial"] = "NaN"
    elif mutation == "wrong_balance_currency": rows[0]["payload"]["balances"][0]["currency"] = "BTC"
    elif mutation == "authority_drift": manifest["non_authoritative"] = False
    binding = _rebind(root, rows, manifest)
    with pytest.raises(ValueError):
        proof._reconstruct(root, binding)


@pytest.mark.parametrize("mutation", ["truncate", "alter_hash", "reorder", "missing", "duplicate", "stale_manifest", "untrusted_binding", "malformed_json"])
def test_byte_corruption_and_untrusted_snapshot_rejected(tmp_path, retained_episode, mutation):
    source, binding = retained_episode
    root = tmp_path / "copy"
    _copy(source, root)
    file = root / "events.jsonl"
    raw = file.read_bytes()
    lines = raw.splitlines(keepends=True)
    if mutation == "truncate": file.write_bytes(raw[:-1])
    elif mutation == "alter_hash": file.write_bytes(raw.replace(b'"sha256":"', b'"sha256":"f', 1))
    elif mutation == "reorder": file.write_bytes(b"".join(reversed(lines)))
    elif mutation == "missing": file.write_bytes(b"".join(lines[:-1]))
    elif mutation == "duplicate": file.write_bytes(raw + lines[-1])
    elif mutation == "stale_manifest": (root / "manifest.json").write_bytes(b"{}")
    elif mutation == "untrusted_binding": binding = "0" * 64
    elif mutation == "malformed_json": file.write_bytes(b"broken\n")
    with pytest.raises(ValueError):
        proof._reconstruct(root, binding)
