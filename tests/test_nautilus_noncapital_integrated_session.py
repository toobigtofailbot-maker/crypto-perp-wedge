"""Native offline acceptance, semantic corruption and actual process-death controls."""
import asyncio
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

import pytest

from tools.nautilus_adapter import noncapital_integrated_session as p


def source_instrument():
    from tools.nautilus_adapter import binance_usdm_offline_reports as previous
    from nautilus_trader.model.instruments import CryptoPerpetual
    _, _, objects = previous.parse_tape(previous.load_fixture(previous.FIXTURE))
    source = CryptoPerpetual.to_dict(objects[0])
    # N3-01's synthetic fixture predates this market-order filter control.
    source["info"]["filters"].append({"filterType": "MARKET_LOT_SIZE", "minQty": "0.001",
                                      "maxQty": "120", "stepSize": "0.001"})
    return source


def tick(now, **changes):
    from nautilus_trader.model.data import QuoteTick
    from nautilus_trader.model.identifiers import InstrumentId
    from nautilus_trader.model.objects import Price, Quantity
    args = dict(instrument_id=InstrumentId.from_str(p.n3.NATIVE_ID), bid_price=Price.from_str("80000.00"),
                ask_price=Price.from_str("80000.10"), bid_size=Quantity.from_str("1.000"),
                ask_size=Quantity.from_str("1.000"), ts_event=now, ts_init=now)
    args.update(changes)
    return QuoteTick(**args)


async def produce(root, pause=False):
    source = source_instrument()
    environment = p.n2._environment()
    journal = p.Journal(root, {"instrument": source, "instrument_hash": p.n2._hash(source),
        "local_instrument": p.local_spec(source), "environment": environment,
        "provenance": "SYNTHETIC OFFLINE TEST ONLY"})
    session = p.NativeSession(source, journal)
    try:
        session.step(tick(time.time_ns()))
        if pause:
            p.durable(root / "kill-ready.json", p.n2._bytes({"pid": os.getpid(),
                "journal_sha256": p.file_hash(root / "events.jsonl"), "native": session.snapshot()}))
            await asyncio.sleep(30)
        session.step(tick(time.time_ns()))
        return journal.seal(session.snapshot())
    finally:
        session.close()


@pytest.fixture(scope="module")
def completed(tmp_path_factory):
    root = tmp_path_factory.mktemp("n4-native")
    digest = asyncio.run(produce(root))
    return root, digest


def test_native_round_trip_accounting_and_venue(completed):
    root, digest = completed
    result = p.verify(root, digest)
    assert result["durably_observed"]["quantity"] == "0"
    assert result["durably_observed"]["fees"] == "0.06400004"
    assert result["durably_observed"]["balance"] == "9999.93589996"
    assert result["native_cache_rehydrated"] is False
    rows = [json.loads(x) for x in (root / "events.jsonl").read_bytes().splitlines()]
    assert {r["payload"].get("instrument_id") for r in rows if r["kind"] == "native"} == {None, p.LOCAL_ID}


def child(code, *args):
    # Explicit safe environment: no exchange credentials propagate.
    env = {k: os.environ[k] for k in ("PATH", "SystemRoot", "WINDIR", "TEMP", "TMP", "PYTHONPATH") if k in os.environ}
    return subprocess.run([sys.executable, "-B", "-c", code, *map(str, args)],
                          capture_output=True, text=True, timeout=60, env=env)


VERIFY_CODE = """
import sys
class NoExecution:
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in ('nautilus_trader','src','lib'):
            raise RuntimeError('verifier cannot load execution')
sys.meta_path.insert(0,NoExecution())
from tools.nautilus_adapter.noncapital_integrated_session import main
raise SystemExit(main(['verify','--output',sys.argv[1],'--expected-manifest-sha256',sys.argv[2]]))
"""


def test_two_fresh_inspectors_identical_zero_mutation(completed):
    root, digest = completed
    before = {f.name: p.file_hash(f) for f in root.iterdir()}
    results = []
    for _ in range(2):
        c = child(VERIFY_CODE, root, digest)
        assert c.returncode == 0, c.stdout + c.stderr
        results.append(json.loads(c.stdout))
    assert len({os.getpid(), *(r["pid"] for r in results)}) == 3
    assert results[0]["result"] == results[1]["result"]
    assert results[0]["result"]["new_orders"] == results[0]["result"]["new_fills"] == 0
    assert before == {f.name: p.file_hash(f) for f in root.iterdir()}
    print(json.dumps({"inspectors": results, "immutable_files": before}))


def test_actual_os_kill_open_position_unsealed_refused(tmp_path):
    code = """
import asyncio,runpy,sys
from pathlib import Path
ns=runpy.run_path('tests/test_nautilus_noncapital_integrated_session.py')
asyncio.run(ns['produce'](Path(sys.argv[1]),pause=True))
"""
    proc = subprocess.Popen([sys.executable, "-B", "-c", code, str(tmp_path)],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        env={k: os.environ[k] for k in ("PATH", "PYTHONPATH", "SystemRoot", "TEMP", "TMP") if k in os.environ})
    try:
        deadline = time.monotonic() + 25
        ready = tmp_path / "kill-ready.json"
        while not ready.exists() and proc.poll() is None and time.monotonic() < deadline:
            time.sleep(.05)
        assert ready.exists(), proc.communicate(timeout=5)
        witness = json.loads(ready.read_bytes())
        assert witness["pid"] == proc.pid and witness["native"]["quantity"] == "0.001"
        proc.kill()
        out, err = proc.communicate(timeout=10)
        assert proc.returncode != 0
        original = p.file_hash(tmp_path / "events.jsonl")
        assert original == witness["journal_sha256"] and not (tmp_path / "manifest.json").exists()
        inspections = [child(VERIFY_CODE, tmp_path, "0" * 64) for _ in range(2)]
        assert all(c.returncode == 1 and "RECONCILIATION_REQUIRED" in c.stdout for c in inspections)
        assert original == p.file_hash(tmp_path / "events.jsonl")
        print(json.dumps({"killed_pid": proc.pid, "exit_code": proc.returncode, "boundary": witness,
                          "refusals": [json.loads(c.stdout) for c in inspections], "unchanged_sha256": original}))
    finally:
        if proc.poll() is None:
            proc.kill()
            proc.communicate(timeout=10)


def rebind(root, rows, manifest):
    for seq, row in enumerate(rows):
        row.update(seq=seq, previous=rows[seq-1]["sha256"] if seq else None)
        row["sha256"] = p.n2._hash({k: v for k, v in row.items() if k != "sha256"})
    raw = b"".join(p.n2._bytes(r) + b"\n" for r in rows)
    (root / "events.jsonl").write_bytes(raw)
    manifest.update(event_count=len(rows), tail=rows[-1]["sha256"], journal_sha256=hashlib.sha256(raw).hexdigest())
    (root / "manifest.json").write_bytes(p.n2._bytes(manifest))
    return p.file_hash(root / "manifest.json")


@pytest.mark.parametrize("case", ["duplicate_event", "duplicate_trade", "conflicting_trade", "missing_fill",
    "wrong_source", "source_hash", "stale", "account", "instrument", "nonflat", "event_order",
    "mapping", "fees", "balance", "quote_order", "run_id", "source_version", "venue_order", "position_order"])
def test_semantic_negatives_even_with_resealed_outer_hashes(completed, tmp_path, case):
    source, _ = completed
    rows = [json.loads(x) for x in (source / "events.jsonl").read_bytes().splitlines()]
    manifest = json.loads((source / "manifest.json").read_bytes())
    fills = [r for r in rows if r["kind"] == "native" and r["payload"]["type"] == "OrderFilled"]
    quotes = [r for r in rows if r["kind"] == "input"]
    if case == "duplicate_event": rows.insert(rows.index(fills[0])+1, copy.deepcopy(fills[0]))
    elif case == "duplicate_trade": fills[1]["payload"]["trade_id"] = fills[0]["payload"]["trade_id"]
    elif case == "conflicting_trade":
        fills[1]["payload"].update(trade_id=fills[0]["payload"]["trade_id"], last_px="1.00")
    elif case == "missing_fill": rows.remove(fills[0])
    elif case == "wrong_source": quotes[0]["payload"]["quote"]["instrument_id"] = p.LOCAL_ID
    elif case == "source_hash": quotes[0]["payload"]["quote"]["source_hash"] = "0" * 64
    elif case == "stale": quotes[0]["payload"]["observed_ns"] += 6_000_000_000
    elif case == "account": fills[0]["payload"]["account_id"] = "BINANCE-001"
    elif case == "instrument": fills[0]["payload"]["instrument_id"] = p.n3.NATIVE_ID
    elif case == "nonflat": rows[-1]["payload"]["quantity"] = "0.001"
    elif case == "event_order":
        index = rows.index(fills[0])
        rows[index-1], rows[index] = rows[index], rows[index-1]
    elif case == "mapping": rows[0]["payload"]["local_instrument"]["id"] = p.n3.NATIVE_ID
    elif case == "fees": fills[0]["payload"]["commission"] = "0 USDT"
    elif case == "balance": rows[-1]["payload"]["balance"] = "10000"
    elif case == "quote_order": quotes[1]["payload"]["quote"] = copy.deepcopy(quotes[0]["payload"]["quote"])
    elif case == "run_id": rows[-1]["run_id"] = "foreign"
    elif case == "source_version": manifest["version"] = "2.0.0rc7"
    elif case == "venue_order": fills[1]["payload"]["venue_order_id"] = fills[0]["payload"]["venue_order_id"]
    elif case == "position_order":
        next(r for r in rows if r["kind"] == "native" and r["payload"]["type"] == "PositionClosed")["payload"]["closing_order_id"] = fills[0]["payload"]["client_order_id"]
    binding = rebind(tmp_path, rows, manifest)
    with pytest.raises((ValueError, KeyError, IndexError)):
        p.verify(tmp_path, binding)


@pytest.mark.parametrize("case", ["truncated", "missing_event", "manifest", "digest"])
def test_byte_integrity(completed, tmp_path, case):
    root, digest = completed
    for name in ("events.jsonl", "manifest.json"):
        (tmp_path / name).write_bytes((root / name).read_bytes())
    if case == "truncated": (tmp_path / "events.jsonl").write_bytes((tmp_path / "events.jsonl").read_bytes()[:-10])
    elif case == "missing_event":
        (tmp_path / "events.jsonl").write_bytes(b"\n".join((tmp_path / "events.jsonl").read_bytes().splitlines()[:-1])+b"\n")
    elif case == "manifest": (tmp_path / "manifest.json").write_bytes(b"{}")
    else: digest = "0" * 64
    with pytest.raises(ValueError): p.verify(tmp_path, digest)


@pytest.mark.parametrize("fault", ["missing", "stale", "disconnect"])
def test_feed_latches_and_valid_input_never_resumes(fault, tmp_path):
    feed = p.Feed()
    source = source_instrument()
    now = time.time_ns()
    if fault != "missing": feed.accept(tick(now if fault == "disconnect" else now-6_000_000_000), now)
    with pytest.raises(ValueError): feed.gate(source, fault != "disconnect")
    assert feed.accept(tick(time.time_ns()), time.time_ns())
    assert feed.latest["quote"]["instrument_id"] == p.n3.NATIVE_ID
    with pytest.raises(ValueError, match="latched"): feed.gate(source, True)
    async def native_stays_interrupted():
        journal = p.Journal(tmp_path, {"synthetic": True})
        session = p.NativeSession(source, journal)
        try:
            session.step(tick(time.time_ns()))
            before = session.snapshot()
            with pytest.raises(ValueError):
                feed.gate(source, True)
                session.step(feed.tick)
            assert session.snapshot() == before
            assert before["fills"] == before["orders"] == 1 and before["quantity"] == "0.001"
            assert not (tmp_path / "manifest.json").exists()
        finally:
            session.close()
    asyncio.run(native_stays_interrupted())


@pytest.mark.parametrize("change", [{"price_increment": "0.30"}, {"min_notional": "251 USDT"},
    {"min_quantity": "0.002"}, {"quote_currency": "USD"}, {"id": "BTCUSDT-PERP.EVIL"}])
def test_source_filters_and_identity_refuse(change):
    source = source_instrument()
    source.update(change)
    with pytest.raises(ValueError):
        p.local_spec(source)
        now = time.time_ns()
        p.validate_quote(p.n3.observation_projection(tick(now), now), source, now)


def test_default_off_and_no_arbitrary_size_venue_or_endpoint():
    with pytest.raises(SystemExit): p.main([])
    with pytest.raises(SystemExit): p.main(["run", "--output", "/tmp"])
    import ast
    tree = ast.parse(Path(p.__file__).read_text())
    imports = [n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)]
    assert not any(x and ("binance.execution" in x or "binance.futures.execution" in x or x.startswith("src")) for x in imports)
    flags = [n.args[0].value for n in ast.walk(tree) if isinstance(n, ast.Call)
             and isinstance(n.func, ast.Attribute) and n.func.attr == "add_argument" and n.args]
    assert set(flags) == {"--output", "--public-noncapital-proof", "--expected-manifest-sha256"}


def test_public_transport_cannot_submit_cancel_sign_or_query_account():
    from nautilus_trader.common.component import LiveClock
    from nautilus_trader.core.nautilus_pyo3 import HttpMethod
    requests = []
    http = p.public_http(LiveClock(), requests)
    async def negatives():
        for method, path in [(HttpMethod.POST, "/fapi/v1/order"), (HttpMethod.DELETE, "/fapi/v1/order"),
                             (HttpMethod.GET, "/fapi/v2/account"), (HttpMethod.POST, "/fapi/v1/listenKey")]:
            with pytest.raises(ValueError): await http.send_request(method, path)
        with pytest.raises(ValueError): await http.sign_request(HttpMethod.GET, "/fapi/v1/exchangeInfo")
        with pytest.raises(ValueError): await http.send_request(HttpMethod.GET, "/fapi/v1/exchangeInfo", {"signature": "forbidden"})
    asyncio.run(negatives())
    assert requests == []


def test_rejected_output_does_not_write(tmp_path):
    (tmp_path / "foreign.txt").write_text("preserve")
    assert p.main(["run", "--public-noncapital-proof", "--output", str(tmp_path)]) == 1
    assert [f.name for f in tmp_path.iterdir()] == ["foreign.txt"]
