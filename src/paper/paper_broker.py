from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any

from src.execution.interfaces import OrderIntent, OrderSide, OrderType


ZERO = Decimal("0")
BPS_DENOMINATOR = Decimal("10000")


def _decimal_text(value: Decimal | None) -> str | None:
    if value is None:
        return None
    if value == 0:
        return "0"
    return format(value.normalize(), "f")


@dataclass(frozen=True)
class PaperFill:
    client_order_id: str
    symbol: str
    side: OrderSide
    qty: Decimal
    signed_qty: Decimal
    fill_price: Decimal
    price_ref: Decimal
    reference_notional: Decimal
    gross_notional: Decimal
    fee_cost: Decimal
    slippage_cost: Decimal
    slippage_bps: Decimal
    fee_bps: Decimal
    reduce_only: bool
    price_ref_source: str | None = None
    price_ref_asof_utc: str | None = None

    @property
    def fee(self) -> Decimal:
        return self.fee_cost

    def to_dict(self) -> dict[str, Any]:
        return {
            "client_order_id": self.client_order_id,
            "symbol": self.symbol,
            "side": self.side.value,
            "qty": _decimal_text(self.qty),
            "signed_qty": _decimal_text(self.signed_qty),
            "fill_price": _decimal_text(self.fill_price),
            "price_ref": _decimal_text(self.price_ref),
            "reference_notional": _decimal_text(self.reference_notional),
            "gross_notional": _decimal_text(self.gross_notional),
            "fee": _decimal_text(self.fee_cost),
            "fee_cost": _decimal_text(self.fee_cost),
            "slippage_cost": _decimal_text(self.slippage_cost),
            "slippage_bps": _decimal_text(self.slippage_bps),
            "fee_bps": _decimal_text(self.fee_bps),
            "reduce_only": self.reduce_only,
            "price_ref_source": self.price_ref_source,
            "price_ref_asof_utc": self.price_ref_asof_utc,
        }


class PaperBroker:
    def __init__(self, ledger_path: str | None = None) -> None:
        self.ledger_path = ledger_path

    def build_rebalance_order_intent(
        self,
        *,
        symbol: str,
        current_qty: Decimal,
        target_qty: Decimal,
        evaluation_time_utc: str,
        decision_id: str,
        correlation_id: str,
    ) -> OrderIntent | None:
        delta_qty = target_qty - current_qty
        if delta_qty == ZERO:
            return None

        side = OrderSide.BUY if delta_qty > ZERO else OrderSide.SELL
        qty = abs(delta_qty)
        reduce_only = current_qty != ZERO and ((current_qty > ZERO and delta_qty < ZERO) or (current_qty < ZERO and delta_qty > ZERO))

        client_order_id_seed = "|".join(
            [
                symbol,
                _decimal_text(current_qty) or "0",
                _decimal_text(target_qty) or "0",
                _decimal_text(delta_qty) or "0",
                evaluation_time_utc,
                decision_id,
                correlation_id,
            ]
        )
        client_order_id = f"PAPER-{hashlib.sha256(client_order_id_seed.encode('utf-8')).hexdigest()[:20]}"

        return OrderIntent(
            symbol=symbol,
            side=side,
            qty=qty,
            price=None,
            order_type=OrderType.MARKET,
            reduce_only=reduce_only,
            client_order_id=client_order_id,
            tif=None,
            urgency="paper-deterministic",
            correlation_id=correlation_id,
            decision_id=decision_id,
        )

    def simulate_fill(
        self,
        order_intent: OrderIntent,
        price_ref: Decimal,
        slippage_bps: Decimal,
        fee_bps: Decimal,
        price_ref_source: str | None = None,
        price_ref_asof_utc: str | None = None,
    ) -> PaperFill:
        if price_ref <= ZERO:
            raise ValueError("price_ref must be positive for paper fill simulation")
        if order_intent.qty <= ZERO:
            raise ValueError("order_intent.qty must be positive for paper fill simulation")

        direction = Decimal("1") if order_intent.side == OrderSide.BUY else Decimal("-1")
        slippage_multiplier = Decimal("1") + ((slippage_bps / BPS_DENOMINATOR) * direction)
        fill_price = price_ref * slippage_multiplier
        reference_notional = order_intent.qty * price_ref
        gross_notional = order_intent.qty * fill_price
        slippage_cost = reference_notional * (slippage_bps / BPS_DENOMINATOR)
        fee_cost = reference_notional * (fee_bps / BPS_DENOMINATOR)
        signed_qty = order_intent.qty if order_intent.side == OrderSide.BUY else -order_intent.qty

        return PaperFill(
            client_order_id=order_intent.client_order_id,
            symbol=order_intent.symbol,
            side=order_intent.side,
            qty=order_intent.qty,
            signed_qty=signed_qty,
            fill_price=fill_price,
            price_ref=price_ref,
            reference_notional=reference_notional,
            gross_notional=gross_notional,
            fee_cost=fee_cost,
            slippage_cost=slippage_cost,
            slippage_bps=slippage_bps,
            fee_bps=fee_bps,
            reduce_only=order_intent.reduce_only,
            price_ref_source=price_ref_source,
            price_ref_asof_utc=price_ref_asof_utc,
        )

    def append_fill_ledger(
        self,
        fill: PaperFill,
        *,
        timestamp_utc: str,
        run_id: str,
        correlation_id: str,
        decision_id: str,
        current_qty_before: Decimal,
        target_qty_after: Decimal,
        position_qty_after: Decimal,
        ledger_state_after: dict[str, Any] | None = None,
    ) -> None:
        if not self.ledger_path:
            return

        payload = {
            "timestamp_utc": timestamp_utc,
            "event_type": "PaperLedgerEntry",
            "run_id": run_id,
            "correlation_id": correlation_id,
            "decision_id": decision_id,
            "symbol": fill.symbol,
            "current_qty_before": _decimal_text(current_qty_before),
            "target_qty_after": _decimal_text(target_qty_after),
            "position_qty_after": _decimal_text(position_qty_after),
            "fill": fill.to_dict(),
        }
        if ledger_state_after is not None:
            payload["ledger_state_after"] = ledger_state_after

        target = Path(self.ledger_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, sort_keys=True) + "\n")
