"""Real consumer/native engine tests; synthetic data is not private reconciliation."""
import asyncio
from decimal import Decimal
import json
import time
import uuid

import pytest

from src.execution.interfaces import DesiredPosition
from src.execution.nautilus_native_backend import validate_config
from src.execution.nautilus_recovery_hold_guard import RecoveryHoldRefusal
from src.runtime import paper_trader


def profile(tmp_path, **changes):
    return {"profile": "NONCAPITAL_NATIVE", "trader_id": "CPWNATIVE-" + uuid.uuid4().hex[:12],
            "macro_flags_path": str(tmp_path / "missing.json"), **changes}


@pytest.mark.parametrize("changes", [{"api_key": "synthetic"}, {"exec_clients": {}},
    {"profile": "LIVE"}, {"endpoint": "https://example.invalid"}])
def test_private_config_denied_before_native_import(tmp_path, changes):
    with pytest.raises(RecoveryHoldRefusal):
        validate_config(profile(tmp_path, **changes))


def fixture_inputs(count=2, *, bad=None):
    from nautilus_trader.model.data import QuoteTick
    from nautilus_trader.model.identifiers import InstrumentId
    from nautilus_trader.model.objects import Price, Quantity
    from nautilus_trader.test_kit.providers import TestInstrumentProvider

    source = TestInstrumentProvider.btcusdt_perp_binance()
    def ticks():
        previous = None
        for i in range(count):
            now = time.time_ns()
            if bad == "stale":
                now -= 10_000_000_000
            if bad == "duplicate" and previous is not None:
                now = previous
            if bad == "reordered" and previous is not None:
                now = previous - 1
            previous = now
            yield QuoteTick(InstrumentId.from_str("BTCUSDT-PERP.BINANCE"),
                Price.from_str("99999.01" if bad == "off_tick" else "99999.0"),
                Price.from_str("100000.00" if bad == "off_tick" else "100000.0"),
                Quantity.from_str("1.000"), Quantity.from_str("1.000"), now, now)
    return source, ticks()


class Targets:
    def __init__(self, targets=("0.001", "0")):
        self.targets = iter(targets)
        self.calls = 0

    def compute_desired_position(self, evaluation_time_utc, inputs):
        self.calls += 1
        return DesiredPosition(symbol="BTCUSDT", target_qty=Decimal(next(self.targets)),
            target_notional=None, timestamp_utc=evaluation_time_utc,
            source_timeframe="1m", decision_id="D-0001", correlation_id=inputs["correlation_id"],
            run_id=inputs["run_id"])


def invoke(tmp_path, *, count=2, targets=("0.001", "0"), bad=None, config=None):
    pytest.importorskip("nautilus_trader")
    source, ticks = fixture_inputs(count, bad=bad)
    path = tmp_path / "native.json"
    path.write_text(json.dumps(config or profile(tmp_path)))
    return asyncio.run(paper_trader.run_native_noncapital(str(path), signal_provider=Targets(targets),
                                                        ticks=ticks, instrument=source))


def test_actual_consumer_native_orders_accounting_no_legacy_writes(tmp_path, monkeypatch):
    def forbidden(*a, **kw):
        raise AssertionError("legacy economic owner reached")
    for name in ("simulate_fill", "append_fill_ledger"):
        monkeypatch.setattr(paper_trader.PaperBroker, name, forbidden)
    for name in ("apply_fill_to_position", "save_position_state", "save_ledger_state"):
        monkeypatch.setattr(paper_trader, name, forbidden)
    result = invoke(tmp_path)
    assert result["quantity"] == "0"
    assert Decimal(result["balance"]) == Decimal("9999.91900040")
    assert len(result["orders"]) == len(result["intent_ids"]) == 2
    assert all(o["status"] == "FILLED" for o in result["orders"])
    assert result["private_clients"] == 0
    assert result["source"] == "SYNTHETIC_NATIVE"
    assert "NO_RESUME" in result["authority"]


@pytest.mark.parametrize("bad", ["stale", "reordered"])
def test_bad_data_latches_refusal(tmp_path, bad):
    with pytest.raises(ValueError, match="stale/duplicate/reordered"):
        invoke(tmp_path, bad=bad)


def test_duplicate_quote_has_no_duplicate_economic_effect(tmp_path):
    result = invoke(tmp_path, bad="duplicate")
    assert len(result["orders"]) == len(result["intent_ids"]) == 1
    assert result["quantity"] == "0.001"


def test_off_tick_price_refuses_without_rounding(tmp_path):
    with pytest.raises(ValueError, match="price increment"):
        invoke(tmp_path, bad="off_tick")


@pytest.mark.parametrize("targets", [("0.002",), ("-0.001",), ("NaN",), ("0.001", "0", "0.001")])
def test_unsupported_target_or_reversal_refuses(tmp_path, targets):
    with pytest.raises((ValueError, ArithmeticError)):
        invoke(tmp_path, count=len(targets), targets=targets)
