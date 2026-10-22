"""Required physical N2-01 proof: missing Nautilus is a failure, never a skip."""
from decimal import Decimal as D
import json
from pathlib import Path
import socket

import pytest

from src.paper.ledger_state import bootstrap_ledger_state
from src.paper.paper_broker import PaperBroker
from tools.nautilus_adapter import paper_sandbox as proof


@pytest.mark.parametrize("scenario", proof.SCENARIOS)
def test_physical_sandbox_repeated_and_cpw_reference(tmp_path, scenario):
    observations = []
    for repeat in range(2):
        root = tmp_path / str(repeat)
        result = proof._run_episode(root, scenario)
        manifest = json.loads((root / "manifest.json").read_bytes())
        rows = [json.loads(line) for line in (root / "events.jsonl").read_bytes().splitlines()]
        projection = proof._reconstruct(root, result["manifest_sha256"])
        assert projection["checkpoints"][-1] == result["source_observation"]
        assert manifest["environment"]["versions"]["nautilus-trader"] == "1.231.0"
        assert len(manifest["environment"]["installed_sha256"]) > 10
        assert all(r["payload"]["event_id"] for r in rows)
        observations.append(([r["observation_key"] for r in rows], projection["checkpoints"]))
        kinds = [r["payload"]["type"] for r in rows]
        fills = [r["payload"] for r in rows if r["payload"]["type"] == "OrderFilled"]
        assert len(fills) == {"flat": 0, "round_trip": 2, "reversal": 3, "cancel": 0}[scenario]
        if scenario in ("round_trip", "reversal"):
            assert "OrderSubmitted" in kinds and "PositionOpened" in kinds and "PositionClosed" in kinds
            # Immediate market fills do not emit OrderAccepted in the pinned sandbox.
            assert "OrderAccepted" not in kinds
            assert [D(f["last_qty"]) for f in fills] == ([D(1), D(2), D(1)] if scenario == "reversal" else [D(1), D(1)])
        if scenario == "cancel":
            assert [kind for kind in kinds if kind != "AccountState"] == ["OrderSubmitted", "OrderAccepted", "OrderCanceled"]
        # CPW reference uses a spot-like cash ledger; compare equity/PnL, not raw cash to margin balance.
        ledger = bootstrap_ledger_state(symbol="BTCUSDT", initial_equity=D(10000), as_of_utc="2026-01-01T00:00:00Z")
        broker = PaperBroker()  # No ledger path: read-only monetary oracle, no writer.
        for index, (target, mark) in enumerate(proof.SCENARIOS[scenario]):
            intent = broker.build_rebalance_order_intent(symbol="BTCUSDT", current_qty=ledger.position_qty,
                target_qty=D(target), evaluation_time_utc=f"2026-01-01T00:00:0{index}Z",
                decision_id="N2-PROOF", correlation_id="N2-PROOF")
            if intent:
                fill = broker.simulate_fill(intent, price_ref=D(mark), slippage_bps=D(0), fee_bps=D(4))
                ledger = ledger.apply_fill(fill, as_of_utc="2026-01-01T00:00:00Z")
            native = projection["checkpoints"][index]
            assert D(native["quantity"]) == ledger.position_qty
            assert D(native["equity"]) == ledger.equity(D(mark))
            assert D(native["unrealized"]) == ledger.unrealized_pnl(D(mark))
            assert D(native["fees"]) == ledger.cumulative_fees
            assert D(native["realized_net"]) == ledger.realized_pnl - ledger.cumulative_fees
            assert D(native["equity"]) == D(10000) + D(native["realized_net"]) + D(native["unrealized"])
        print(json.dumps({"scenario": scenario, "repeat": repeat, "root": str(root),
                          "manifest_sha256": result["manifest_sha256"], "event_types": kinds,
                          "native_source": projection["checkpoints"], "cpw_reference": ledger.to_dict()}, sort_keys=True))
    assert observations[0] == observations[1]


@pytest.mark.parametrize("value", ["NaN", "Infinity", "-Infinity", "bad", 1, None, "1000001"])
def test_invalid_decimal_rejected(value):
    with pytest.raises(ValueError):
        proof._decimal(value)


@pytest.mark.parametrize("scenario", ["BINANCE", "https://exchange.example", "nonzero_funding", "liquidation", "leverage_100", "live", "paper"])
def test_closed_fixture_denies_other_clients_or_economic_modes(tmp_path, scenario):
    with pytest.raises(ValueError, match="unsupported"):
        proof._run_episode(tmp_path / "no-write", scenario)
    assert not (tmp_path / "no-write").exists()


def test_network_access_denied():
    with proof._offline():
        with pytest.raises(RuntimeError, match="denies network"):
            socket.getaddrinfo("example.com", 443)
        with socket.socket() as channel:
            with pytest.raises(RuntimeError, match="denies network"):
                channel.connect(("127.0.0.1", 1))
            with pytest.raises(RuntimeError, match="denies network"):
                channel.sendto(b"test", ("127.0.0.1", 1))


def test_wrong_pin_lock_and_binary_fail_closed(monkeypatch):
    original = proof.metadata.version
    monkeypatch.setattr(proof.metadata, "version", lambda name: "0.0.0" if name == "nautilus-trader" else original(name))
    with pytest.raises(ValueError, match="pinned version"):
        proof._environment()
    monkeypatch.undo()
    original_bytes = Path.read_bytes
    monkeypatch.setattr(Path, "read_bytes", lambda path: b"wrong" if path.name.endswith("lock.txt") else original_bytes(path))
    with pytest.raises(ValueError, match="pinned lock"):
        proof._environment()
    monkeypatch.undo()
    monkeypatch.setattr(Path, "read_bytes", lambda path: b"wrong" if path.suffix in (".pyd", ".so") else original_bytes(path))
    with pytest.raises(ValueError, match="RECORD mismatch"):
        proof._environment()


def test_scratch_is_external_empty_and_no_overwrite(tmp_path):
    with pytest.raises(ValueError, match="OS temp"):
        proof._scratch(Path(__file__).resolve().parents[1])
    root = proof._scratch(tmp_path / "used")
    (root / "existing").write_text("retained")
    with pytest.raises(ValueError, match="empty"):
        proof._scratch(root)
    assert (root / "existing").read_text() == "retained"


def test_reference_fee_basis_difference_is_explicit():
    broker = PaperBroker()
    intent = broker.build_rebalance_order_intent(symbol="BTCUSDT", current_qty=D(0), target_qty=D(1),
        evaluation_time_utc="2026-01-01T00:00:00Z", decision_id="N2", correlation_id="N2")
    fill = broker.simulate_fill(intent, price_ref=D(100), slippage_bps=D(1), fee_bps=D(4))
    assert fill.fee_cost == D('.04')
    assert fill.fill_price * fill.qty * D('.0004') == D('.040004')
    # This is reference arithmetic, not a second native sandbox scenario.
    assert fill.slippage_cost == D('.01')
