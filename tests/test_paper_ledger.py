from __future__ import annotations

from decimal import Decimal

from src.paper.ledger_state import bootstrap_ledger_state
from src.paper.paper_broker import PaperBroker


BROKER = PaperBroker()


def _fill(*, current_qty: str, target_qty: str, price_ref: str, slippage_bps: str, fee_bps: str):
    intent = BROKER.build_rebalance_order_intent(
        symbol="BTCUSDT",
        current_qty=Decimal(current_qty),
        target_qty=Decimal(target_qty),
        evaluation_time_utc="2026-01-01T01:00:00Z",
        decision_id="D-LEDGER",
        correlation_id="RUN-LEDGER",
    )
    assert intent is not None
    return BROKER.simulate_fill(
        intent,
        price_ref=Decimal(price_ref),
        slippage_bps=Decimal(slippage_bps),
        fee_bps=Decimal(fee_bps),
    )


def test_apply_fill_updates_ledger_deterministically() -> None:
    ledger = bootstrap_ledger_state(
        symbol="BTCUSDT",
        initial_equity=Decimal("1000"),
        as_of_utc="2026-01-01T00:00:00Z",
    )

    fill = _fill(
        current_qty="0",
        target_qty="1",
        price_ref="100",
        slippage_bps="10",
        fee_bps="5",
    )
    next_ledger = ledger.apply_fill(fill, as_of_utc="2026-01-01T01:00:00Z")

    assert next_ledger.cash == Decimal("899.85")
    assert next_ledger.position_qty == Decimal("1")
    assert next_ledger.avg_entry_price == Decimal("100.1")
    assert next_ledger.realized_pnl == Decimal("0")
    assert next_ledger.cumulative_fees == Decimal("0.05")
    assert next_ledger.cumulative_slippage == Decimal("0.1")


def test_realized_and_unrealized_pnl_are_deterministic() -> None:
    ledger = bootstrap_ledger_state(
        symbol="BTCUSDT",
        initial_equity=Decimal("1000"),
        as_of_utc="2026-01-01T00:00:00Z",
    )
    open_fill = _fill(
        current_qty="0",
        target_qty="1",
        price_ref="100",
        slippage_bps="0",
        fee_bps="0",
    )
    ledger = ledger.apply_fill(open_fill, as_of_utc="2026-01-01T01:00:00Z")

    reduce_fill = _fill(
        current_qty="1",
        target_qty="0.6",
        price_ref="110",
        slippage_bps="0",
        fee_bps="0",
    )
    ledger = ledger.apply_fill(reduce_fill, as_of_utc="2026-01-01T02:00:00Z")

    assert ledger.position_qty == Decimal("0.6")
    assert ledger.avg_entry_price == Decimal("100")
    assert ledger.realized_pnl == Decimal("4")
    assert ledger.unrealized_pnl(Decimal("105")) == Decimal("3")


def test_cumulative_fee_and_slippage_accumulate_deterministically() -> None:
    ledger = bootstrap_ledger_state(
        symbol="BTCUSDT",
        initial_equity=Decimal("1000"),
        as_of_utc="2026-01-01T00:00:00Z",
    )

    buy_fill = _fill(
        current_qty="0",
        target_qty="2",
        price_ref="100",
        slippage_bps="25",
        fee_bps="10",
    )
    ledger = ledger.apply_fill(buy_fill, as_of_utc="2026-01-01T01:00:00Z")

    sell_fill = _fill(
        current_qty="2",
        target_qty="1",
        price_ref="120",
        slippage_bps="25",
        fee_bps="10",
    )
    ledger = ledger.apply_fill(sell_fill, as_of_utc="2026-01-01T02:00:00Z")

    assert ledger.cumulative_fees == Decimal("0.32")
    assert ledger.cumulative_slippage == Decimal("0.8")
    assert ledger.realized_pnl == Decimal("19.45")
