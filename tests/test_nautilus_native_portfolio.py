"""P1 exercises native fills from the real CPW CLI and an independent Decimal oracle."""
from datetime import UTC, datetime, timedelta
from decimal import Decimal as D
import json
import os
from pathlib import Path
import subprocess
import sys
import uuid

import pytest

from src.execution import nautilus_portfolio_contract as contract


def requests(symbol="SOLUSDT", targets=None):
    source = contract.decode(contract.SOURCE.read_bytes())
    universe = ("BTCUSDT", symbol)
    rows = {row["symbol"]: row for row in source["symbols"]}
    run = "P1-" + uuid.uuid4().hex.upper()
    now = datetime.now(UTC)
    result = []
    for i, (btc, other) in enumerate(targets or (
        ("0.001", "0.40"), ("0", "0.60"), ("-0.001", "0.40"), ("0", "0.40"),
    )):
        row = {
            "schema": "portfolio_execution_request_v1", "mode": contract.MODE, "authority": contract.AUTHORITY,
            "request_id": f"{run}-{i}", "portfolio_id": "P1-PORTFOLIO", "run_id": run,
            "lineage": {"source": "SYNTHETIC_TEST_ONLY", "strategy_id": "P1-DUMMY-STRATEGY",
                        "candidate_id": None, "approval_id": None},
            "venue": "BINANCE", "market_type": "USD-M_PERPETUAL", "execution_venue": "CPWSIM",
            "evaluation_utc": now.isoformat().replace("+00:00", "Z"),
            "expiry_utc": (now + timedelta(seconds=55)).isoformat().replace("+00:00", "Z"),
            "cycle_index": i, "source_fixture_sha256": contract.SOURCE_SHA256,
            "source_identities": [{"symbol": s, "instrument_id": f"{s}-PERP.BINANCE",
                                   "metadata_sha256": contract.digest(contract.canonical(rows[s]))} for s in universe],
            "targets": [{"symbol": s, "target_qty": q, "units": "BASE_CONTRACT_QUANTITY"}
                        for s, q in zip(universe, (btc, other), strict=True)],
            "limits": {"test_only_per_order_max_notional_usdt": "250",
                       "test_only_portfolio_gross_max_usdt": "250", "leverage": "1"},
        }
        rehash(row)
        result.append(row)
    return result


def rehash(row):
    row.pop("request_content_sha256", None)
    row["request_content_sha256"] = contract.digest(contract.canonical(row))


def launch(path, mode="--native-portfolio"):
    return subprocess.run([sys.executable, "-B", "-m", "src.runtime.paper_trader",
                           mode, "--config", str(path)], capture_output=True, text=True, timeout=55)


@pytest.mark.parametrize("defect", ["private", "approval", "source", "venue", "stale", "hash", "conflict", "reorder"])
def test_refuses_invalid_requests(tmp_path, defect):
    rows = requests()
    first = rows[0]
    if defect == "private":
        first["exec_clients"] = {"BINANCE": {}}
    elif defect == "approval":
        first["lineage"]["approval_id"] = "APPROVED"
    elif defect == "source":
        first["source_identities"][0]["metadata_sha256"] = "sha256:" + "0" * 64
    elif defect == "venue":
        first["source_identities"][0]["instrument_id"] = "BTCUSDT-PERP.CPWSIM"
    elif defect == "stale":
        first["evaluation_utc"], first["expiry_utc"] = "2020-01-01T00:00:00Z", "2020-01-01T00:00:20Z"
    elif defect == "hash":
        first["targets"][0]["target_qty"] = "0"
    elif defect == "conflict":
        rows[1]["request_id"] = first["request_id"]
        rehash(rows[1])
    else:
        rows.reverse()
    if defect != "hash":
        rehash(first)
    path = tmp_path / "request.json"
    path.write_text(json.dumps(rows))
    with pytest.raises(ValueError, match="P1 HOLD"):
        contract.read_requests(path)


def test_duplicate_json_key_and_nonfinite_refused():
    for value in (b'{"x":0,"x":0}', b'{"x":NaN}'):
        with pytest.raises(ValueError, match="P1 HOLD"):
            contract.decode(value)


isolated_redis = pytest.mark.skipif(os.environ.get("CPW_LANEB_P1_TESTS") != "1",
                                  reason="requires dedicated local P1 Redis and pinned native engine")


@isolated_redis
@pytest.mark.parametrize("symbol", ["SOLUSDT", "ETHUSDT"])
def test_real_portfolio_cli_and_native_fee_oracle(tmp_path, symbol):
    path = tmp_path / "request.json"
    targets = None if symbol == "SOLUSDT" else [
        ("0.001", "0.010"), ("0", "0.020"), ("-0.001", "0.010"), ("0", "0.010")]
    rows = requests(symbol, targets)
    path.write_text(json.dumps([rows[0], *rows]))
    proc = launch(path)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    result = json.loads(proc.stdout.splitlines()[-1])
    assert result["request_file_sha256"] == contract.digest(path.read_bytes())
    observations = result["observations"]
    assert len(observations) == 4
    assert len({obs["native_engine"]["node_id"] for obs in observations}) == 1
    assert len({obs["portfolio"]["account_id"] for obs in observations}) == 1
    for request, obs in zip(rows, observations, strict=True):
        assert obs["execution"]["registered_clients"] == obs["portfolio"]["native_accounts"] == 1
        assert obs["request_content_sha256"] == request["request_content_sha256"]
        digest = obs["evidence"].pop("observation_sha256")
        assert digest == contract.digest(contract.canonical(obs))
        obs["evidence"]["observation_sha256"] = digest
        expected = {row["symbol"]: D(row["target_qty"]) for row in request["targets"]}
        gross = net = realized = D(0)
        for item in obs["per_symbol"]:
            assert all(o["status"] == "FILLED" for o in item["orders"])
            assert all(fill["commission"].endswith(" USDT") for fill in item["fills"])
            qty = sum((D(fill["last_qty"]) * (1 if fill["order_side"] == "BUY" else -1)
                       for fill in item["fills"]), D(0))
            assert qty == D(item["position_qty"]) == expected[item["symbol"]]
            fees = sum(((D(fill["last_qty"]) * D(fill["last_px"]) * D("0.0004")).quantize(D("0.00000001"))
                        for fill in item["fills"]), D(0))
            assert fees == D(item["fees_usdt"])
            realized -= fees
            position = average = D(0)
            for fill in sorted(item["fills"], key=lambda event: event["ts_event"]):
                price = D(fill["last_px"])
                delta = D(fill["last_qty"]) * (1 if fill["order_side"] == "BUY" else -1)
                if position * delta >= 0:
                    average = (position * average + delta * price) / (position + delta)
                else:
                    assert abs(delta) <= abs(position)
                    realized += (average - price) * delta
                position += delta
            exposure = qty * D(item["quote"]["ask_price"])
            gross += abs(exposure)
            net += exposure
        assert gross == D(obs["portfolio"]["gross_exposure_usdt"]) <= 250
        assert net == D(obs["portfolio"]["net_exposure_usdt"])
        assert D(obs["portfolio"]["available_balance_usdt"]) > 0
        assert realized == D(obs["portfolio"]["realized_pnl_usdt"])
        assert D(10000) + realized == D(obs["portfolio"]["total_balance_usdt"])
    assert sum(len(o["execution"]["cycle_order_ids"]) for o in observations) == 7
    assert "no automatic resume" in launch(path).stderr
    if evidence := os.environ.get("CPW_LANEB_P1_EVIDENCE"):
        out = Path(evidence)
        (out / f"{symbol}-request.json").write_bytes(path.read_bytes())
        (out / f"{symbol}-observations.json").write_text(proc.stdout)
        (out / f"{symbol}-native.stderr").write_text(proc.stderr)


@isolated_redis
@pytest.mark.parametrize(("targets", "message"), [
    (("0.002", "0.40"), "portfolio gross veto"),
    (("0.003", "0.40"), "per-order notional veto"),
    (("0.001", "0.001"), "native quantity precision"),
    (("0.001", "0.01"), "native min notional"),
])
def test_basket_veto_leaves_no_native_orders(tmp_path, targets, message):
    import redis

    path = tmp_path / "request.json"
    rows = requests(targets=[targets])
    path.write_text(json.dumps(rows))
    proc = launch(path)
    assert proc.returncode and message in proc.stderr, proc.stdout + proc.stderr
    prefix = "trader-" + contract.profile(rows[0])["trader_id"]
    db = redis.Redis(port=16379)
    assert not list(db.scan_iter(prefix + ":orders:*"))

@isolated_redis
@pytest.mark.parametrize("fault", ["stale", "inflight", "rejected", "canceled", "partial"])
def test_fault_stops_before_next_native_send(tmp_path, monkeypatch, fault):
    import asyncio

    from nautilus_trader.adapters.binance.futures import providers
    from nautilus_trader.adapters.sandbox import factory
    from nautilus_trader.test_kit.stubs.events import TestEventStubs
    from nautilus_trader.trading import strategy
    from src.execution import nautilus_native_backend as native
    from src.runtime import paper_trader

    # Import the native extension graph before swapping the Python lookup.
    assert providers.BinanceFuturesInstrumentProvider and factory.SandboxLiveExecClientFactory

    def legacy(*args, **kwargs):
        pytest.fail("legacy economic owner reached")

    for name in ("apply_fill_to_position", "save_position_state", "save_ledger_state"):
        monkeypatch.setattr(paper_trader, name, legacy)
    monkeypatch.setattr(paper_trader.PaperBroker, "simulate_fill", legacy)
    attempts = []

    class FaultyStrategy(strategy.Strategy):
        def submit_order(self, order, *args, **kwargs):
            attempts.append(str(order.client_order_id))
            if fault == "stale":
                return super().submit_order(order, *args, **kwargs)
            self.cache.add_order(order)
            order.apply(TestEventStubs.order_submitted(order))
            if fault == "rejected":
                order.apply(TestEventStubs.order_rejected(order))
            elif fault in {"canceled", "partial"}:
                order.apply(TestEventStubs.order_accepted(order))
                if fault == "canceled":
                    order.apply(TestEventStubs.order_canceled(order))
                else:
                    instrument = self.cache.instrument(order.instrument_id)
                    order.apply(TestEventStubs.order_filled(
                        order, instrument, last_qty=instrument.make_qty(order.quantity.as_decimal() / 2)))

    quotes = native._fixture_quotes

    def stale_quote(source, instruments):
        ticks = quotes(source, instruments)
        tick = ticks["SOLUSDT"]
        row = type(tick).to_dict(tick)
        row["ts_event"] -= 6_000_000_000
        ticks["SOLUSDT"] = type(tick).from_dict(row)
        return ticks

    monkeypatch.setattr(strategy, "Strategy", FaultyStrategy)
    if fault == "stale":
        monkeypatch.setattr(native, "_fixture_quotes", stale_quote)
    path = tmp_path / "request.json"
    path.write_text(json.dumps(requests(targets=[("0.002", "0"), ("0", "0.40")])))
    cycles, source, _ = contract.read_requests(path)
    with pytest.raises(ValueError, match="stale or mismatched|acknowledgement|rejected native fill"):
        asyncio.run(native.run_portfolio(cycles, source))
    assert len(attempts) == (0 if fault == "stale" else 1)
