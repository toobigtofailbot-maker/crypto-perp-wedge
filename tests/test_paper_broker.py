from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

from src.paper.paper_broker import PaperBroker


def test_paper_broker_is_deterministic_for_same_inputs() -> None:
    broker = PaperBroker()

    intent_a = broker.build_rebalance_order_intent(
        symbol="BTCUSDT",
        current_qty=Decimal("0"),
        target_qty=Decimal("2"),
        evaluation_time_utc="2026-01-01T01:00:00Z",
        decision_id="D-0001",
        correlation_id="RUN-TEST-BROKER-1",
    )
    intent_b = broker.build_rebalance_order_intent(
        symbol="BTCUSDT",
        current_qty=Decimal("0"),
        target_qty=Decimal("2"),
        evaluation_time_utc="2026-01-01T01:00:00Z",
        decision_id="D-0001",
        correlation_id="RUN-TEST-BROKER-1",
    )

    assert intent_a is not None
    assert intent_b is not None
    assert intent_a.client_order_id == intent_b.client_order_id

    fill_a = broker.simulate_fill(
        intent_a,
        price_ref=Decimal("100000"),
        slippage_bps=Decimal("10"),
        fee_bps=Decimal("5"),
    )
    fill_b = broker.simulate_fill(
        intent_b,
        price_ref=Decimal("100000"),
        slippage_bps=Decimal("10"),
        fee_bps=Decimal("5"),
    )

    assert fill_a == fill_b
    assert fill_a.to_dict()["fill_price"] == "100100"
    assert fill_a.to_dict()["reference_notional"] == "200000"
    assert fill_a.to_dict()["gross_notional"] == "200200"
    assert fill_a.to_dict()["fee"] == "100"
    assert fill_a.to_dict()["fee_cost"] == "100"
    assert fill_a.to_dict()["slippage_cost"] == "200"


def test_paper_broker_appends_local_fill_ledger_entries(tmp_path: Path) -> None:
    ledger_path = tmp_path / "logs" / "paper_trader" / "ledger.jsonl"
    broker = PaperBroker(str(ledger_path))

    intent = broker.build_rebalance_order_intent(
        symbol="BTCUSDT",
        current_qty=Decimal("1.5"),
        target_qty=Decimal("0"),
        evaluation_time_utc="2026-01-01T01:00:00Z",
        decision_id="D-0001",
        correlation_id="RUN-TEST-BROKER-2",
    )

    assert intent is not None

    fill = broker.simulate_fill(
        intent,
        price_ref=Decimal("100000"),
        slippage_bps=Decimal("10"),
        fee_bps=Decimal("5"),
    )
    broker.append_fill_ledger(
        fill,
        timestamp_utc="2026-01-01T01:00:00Z",
        run_id="RUN-TEST-BROKER-2",
        correlation_id="RUN-TEST-BROKER-2",
        decision_id="D-0001",
        current_qty_before=Decimal("1.5"),
        target_qty_after=Decimal("0"),
        position_qty_after=Decimal("0"),
        ledger_state_after={"realized_pnl": "7350"},
    )

    entries = [json.loads(line) for line in ledger_path.read_text(encoding="utf-8").splitlines()]
    assert len(entries) == 1
    assert entries[0]["event_type"] == "PaperLedgerEntry"
    assert entries[0]["fill"]["side"] == "SELL"
    assert entries[0]["fill"]["fill_price"] == "99900"
    assert entries[0]["fill"]["reference_notional"] == "150000"
    assert entries[0]["fill"]["fee_cost"] == "75"
    assert entries[0]["fill"]["slippage_cost"] == "150"
    assert entries[0]["position_qty_after"] == "0"
    assert entries[0]["ledger_state_after"]["realized_pnl"] == "7350"
