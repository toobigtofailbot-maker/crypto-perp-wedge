"""Required physical proof: missing owned Redis/native pin fails, never skips."""
import asyncio
import copy
from decimal import Decimal as D
import json
import os
from pathlib import Path
import subprocess
import sys
import sysconfig
import uuid

import pytest

from tools.nautilus_adapter import native_cache_restart as proof

ROOT = Path(__file__).resolve().parents[1]


def trader():
    return "N2R" + uuid.uuid4().hex[:12] + "-001"


def command(action, root, owner, binding):
    # Windows venv python.exe is a launcher with a different PID from its child.
    bootstrap = (f"import site,runpy; site.addsitedir({sysconfig.get_path('purelib')!r}); "
                 "runpy.run_module('tools.nautilus_adapter.native_cache_restart', run_name='__main__')")
    return [sys._base_executable, "-B", "-c", bootstrap,
            action, str(root), owner, binding]


def child(action, root, owner, binding, *, succeeds=True, partial=False):
    result = subprocess.run(command(action, root, owner, binding), cwd=ROOT,
                            capture_output=True, text=True, timeout=60)
    path = Path(root).parent / (Path(root).name + "-" + action + "-" + uuid.uuid4().hex[:6] + ".log")
    path.write_text(result.stdout + result.stderr, encoding="utf-8")
    if partial:
        assert result.returncode == 2, result.stdout + result.stderr
    else:
        assert (result.returncode == 0) == succeeds, result.stdout + result.stderr
    return json.loads(result.stdout.splitlines()[-1]) if succeeds or partial else result.stderr


@pytest.fixture(scope="module")
def native_source(tmp_path_factory):
    parent = tmp_path_factory.mktemp("native-cache-source")
    root, owner = parent / "producer", trader()
    result = child("produce", root, owner, "round_trip")
    manifest = json.loads((root / "manifest.json").read_bytes())
    return root, owner, result, manifest


@pytest.mark.parametrize("scenario", proof.SCENARIOS)
def test_physical_native_determinism_and_cpw(tmp_path, scenario):
    from src.paper.ledger_state import bootstrap_ledger_state
    from src.paper.paper_broker import PaperBroker

    observations = []
    for repeat in range(2):
        owner, root = trader(), tmp_path / str(repeat)
        producer = child("produce", root, owner, scenario)
        manifest = json.loads((root / "manifest.json").read_bytes())
        restart = child("restore", root, owner, producer["sha256"], partial=scenario == "reversal")
        assert producer["pid"] != restart["pid"] != os.getpid()
        assert restart["instance_id"] != manifest["instance_id"]
        assert restart["state_sha256"] == proof.fixture._hash(manifest["state"])
        assert restart["new_orders"] == restart["new_fills"] == restart["execution_clients"] == 0
        assert restart["status"] == proof.STATUS
        normalized = [(o["state"], [(e["type"], e.get("order_side"), e.get("last_qty"),
                       e.get("last_px"), e.get("commission")) for e in o["events"]])
                      for _, o in sorted(manifest["state"]["orders"].items())]
        observations.append((restart["economics"], normalized))
        ledger = bootstrap_ledger_state(symbol="BTCUSDT", initial_equity=D(10000), as_of_utc="2026-01-01T00:00:00Z")
        broker = PaperBroker()
        for step, (target, mark) in enumerate(proof.fixture.SCENARIOS[scenario]):
            intent = broker.build_rebalance_order_intent(symbol="BTCUSDT", current_qty=ledger.position_qty,
                target_qty=D(target), evaluation_time_utc=f"2026-01-01T00:00:0{step}Z",
                decision_id="N2-02-PROOF", correlation_id="N2-02-PROOF")
            if intent:
                fill = broker.simulate_fill(intent, price_ref=D(mark), slippage_bps=D(0), fee_bps=D(4))
                ledger = ledger.apply_fill(fill, as_of_utc="2026-01-01T00:00:00Z")
        economic = restart["economics"]
        assert D(economic["equity"]) == ledger.equity(D(mark))
        assert D(economic["fees"]) == ledger.cumulative_fees
        assert D(economic["quantity"]) == ledger.position_qty == 0
        assert D(economic["equity"]) == D(10000) + ledger.realized_pnl - ledger.cumulative_fees
        assert economic["statuses"] == {"FILLED": economic["fills"], "CANCELED": 1}
        kinds = {key.split(":")[1] for key in manifest["records"]}
        assert {"accounts", "orders", "positions", "instruments"} <= kinds
        assert all(value["count"] for value in manifest["records"].values())
        fills = [e for o in manifest["state"]["orders"].values() for e in o["events"] if e["type"] == "OrderFilled"]
        publications = manifest["publications"]
        assert len([e for e in publications if e["type"] == "OrderSubmitted"]) == economic["orders"]
        assert len([e for e in publications if e["type"] == "OrderFilled"]) == len(fills)
        assert len({e["trade_id"] for e in fills}) == len(fills)
        assert manifest["environment"]["python"] == "3.12.10"
        assert manifest["environment"]["versions"]["nautilus-trader"] == "1.231.0"
        assert restart["native_command_count"] == restart["native_event_count"] == 0
        if scenario == "reversal":
            assert restart["proof_status"] == "PARTIAL_NATIVE_HISTORY_LOSS"
            assert len(manifest["native_history"]["position_snapshots"]) == 1
            assert restart["native_history"]["position_snapshots"] == []
            assert D(manifest["native_history"]["portfolio_realized_net"]) == D("29.836")
            assert D(restart["native_history"]["portfolio_realized_net"]) == D("19.92")
            assert restart["history_equal"] is False
        else:
            assert restart["history_equal"] is True
            assert restart["proof_status"] == "NATIVE_DURABILITY_PROVEN"
        receipt = {"producer": producer, "restart": restart, "cpw_reference": ledger.to_dict(),
                   "manifest": producer["sha256"], "scenario": scenario, "repeat": repeat}
        proof.write_json(tmp_path / f"receipt-{repeat}.json", receipt)
        print(json.dumps(receipt, sort_keys=True))
    assert observations[0] == observations[1]


@pytest.mark.parametrize("mutation", ["missing_account", "missing_order", "missing_position", "bad_state",
    "fee_currency", "nonfinite", "duplicate_fill", "duplicate_economic_id", "position_binding"])
def test_semantic_negative_independent_fixture(native_source, mutation):
    _, owner, _, manifest = native_source
    state = copy.deepcopy(manifest["state"])
    filled = [o for o in state["orders"].values() if o["state"] == "FILLED"]
    fills = [e for o in filled for e in o["events"] if e["type"] == "OrderFilled"]
    if mutation == "missing_account":
        state["accounts"] = {}
    elif mutation == "missing_order":
        state["orders"] = {}
    elif mutation == "missing_position":
        state["positions"] = {}
    elif mutation == "bad_state":
        filled[0]["state"] = "SUBMITTED"
    elif mutation == "fee_currency":
        fills[0]["commission"] = ".04 BTC"
    elif mutation == "nonfinite":
        fills[0]["last_qty"] = "NaN"
    elif mutation == "duplicate_fill":
        filled[0]["events"].append(copy.deepcopy(fills[0]))
    elif mutation == "duplicate_economic_id":
        fills[1]["trade_id"] = fills[0]["trade_id"]
    elif mutation == "position_binding":
        next(iter(state["positions"].values()))["state"]["opening_order_id"] = "unknown"
    db, _ = proof.backend()
    before = proof.records(db, owner)
    with pytest.raises(ValueError):
        proof.validate_state(state, owner, "round_trip")
    assert proof.records(db, owner) == before == manifest["records"]


@pytest.mark.parametrize("bad", ["BINANCE", "localhost", "https://example.com", "N2Rfoo-001", "../x"])
def test_closed_namespace(bad):
    with pytest.raises(ValueError):
        proof.namespace(bad)


def test_startup_flush_and_submit_rejected_before_native():
    with pytest.raises(ValueError, match="flush forbidden"):
        proof.node(trader(), flush_on_start=True)
    with pytest.raises(ValueError, match="NO_NEW_ORDERS"):
        proof.no_resume()


def test_native_empty_status_reports_and_reset_limitation():
    # Invoke the real pinned methods; they have no status capability or use of self.
    from nautilus_trader.adapters.sandbox.execution import SandboxExecutionClient

    async def reports():
        assert await SandboxExecutionClient.generate_order_status_report(None, None) is None
        for name in ("generate_order_status_reports", "generate_fill_reports", "generate_position_status_reports"):
            assert await getattr(SandboxExecutionClient, name)(None, None) == []
    asyncio.run(reports())
    with pytest.raises(ValueError, match="RECONCILIATION_UNVERIFIED"):
        proof.no_resume()


def test_actual_simulated_venue_reset_is_not_reconciliation(tmp_path, native_source):
    _, valid_owner, _, valid_manifest = native_source
    owner, root = trader(), tmp_path / "reset-only"
    producer = child("produce", root, owner, "round_trip")
    db, _ = proof.backend()
    valid_before = proof.records(db, valid_owner)
    # Only this disposable producer's namespace is exposed to the native reset.
    code = f'''
import asyncio, json
from tools.nautilus_adapter import native_cache_restart as p
async def reset():
    instance = p.node({owner!r}, producer=True)
    engine = instance.kernel.exec_engine
    engine.start()
    await asyncio.sleep(.2)
    from nautilus_trader.model.currencies import USDT
    balance = str(instance.kernel.cache.accounts()[0].balance_total(USDT).as_decimal())
    assert p.D(balance) == p.D(10000), balance
    try:
        p.no_resume()
    except ValueError as exc:
        refusal = str(exc)
    assert engine.command_count == 0
    engine.stop()
    await asyncio.sleep(.05)
    instance.kernel.cache.dispose()
    print(json.dumps(dict(reset_balance=balance, status=refusal, commands=engine.command_count)))
asyncio.run(reset())
'''
    result = subprocess.run([sys.executable, "-B", "-c", code], cwd=ROOT,
                            capture_output=True, text=True, timeout=30)
    (tmp_path / "native-reset.log").write_text(result.stdout + result.stderr)
    assert result.returncode == 0, result.stdout + result.stderr
    error = child("restore", root, owner, producer["sha256"], succeeds=False)
    assert "missing/corrupt native records" in error
    assert proof.records(db, valid_owner) == valid_before == valid_manifest["records"]
