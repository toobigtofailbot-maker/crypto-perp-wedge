from __future__ import annotations

import json
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import TYPE_CHECKING, Any


if TYPE_CHECKING:
    from src.paper.paper_broker import PaperFill


ZERO = Decimal("0")


def _decimal_text(value: Decimal | None) -> str | None:
    if value is None:
        return None
    if value == 0:
        return "0"
    return format(value.normalize(), "f")


def _decimal_or_default(value: Any, default: Decimal | None = None) -> Decimal | None:
    if value is None:
        return default
    return Decimal(str(value))


def _same_direction(left: Decimal, right: Decimal) -> bool:
    return (left > ZERO and right > ZERO) or (left < ZERO and right < ZERO)


@dataclass(frozen=True)
class LedgerState:
    symbol: str
    cash: Decimal
    position_qty: Decimal
    avg_entry_price: Decimal | None
    cumulative_fees: Decimal
    cumulative_slippage: Decimal
    realized_pnl: Decimal
    initial_equity: Decimal
    updated_at_utc: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "symbol": self.symbol,
            "cash": _decimal_text(self.cash),
            "position_qty": _decimal_text(self.position_qty),
            "avg_entry_price": _decimal_text(self.avg_entry_price),
            "cumulative_fees": _decimal_text(self.cumulative_fees),
            "cumulative_slippage": _decimal_text(self.cumulative_slippage),
            "realized_pnl": _decimal_text(self.realized_pnl),
            "initial_equity": _decimal_text(self.initial_equity),
            "updated_at_utc": self.updated_at_utc,
        }

    def unrealized_pnl(self, mark_price: Decimal) -> Decimal:
        if self.position_qty == ZERO or self.avg_entry_price is None:
            return ZERO
        return self.position_qty * (mark_price - self.avg_entry_price)

    def equity(self, mark_price: Decimal) -> Decimal:
        return self.cash + (self.position_qty * mark_price)

    def to_event_payload(self, *, evaluation_time_utc: str, mark_price: Decimal) -> dict[str, Any]:
        return {
            "evaluation_time_utc": evaluation_time_utc,
            "cash": _decimal_text(self.cash),
            "position_qty": _decimal_text(self.position_qty),
            "avg_entry_price": _decimal_text(self.avg_entry_price),
            "mark_price": _decimal_text(mark_price),
            "unrealized_pnl": _decimal_text(self.unrealized_pnl(mark_price)),
            "realized_pnl": _decimal_text(self.realized_pnl),
            "cumulative_fees": _decimal_text(self.cumulative_fees),
            "cumulative_slippage": _decimal_text(self.cumulative_slippage),
            "initial_equity": _decimal_text(self.initial_equity),
            "equity": _decimal_text(self.equity(mark_price)),
        }

    def apply_fill(self, fill: PaperFill, *, as_of_utc: str) -> LedgerState:
        if fill.signed_qty == ZERO:
            return snapshot_ledger_state(self, as_of_utc)

        current_qty = self.position_qty
        new_qty = current_qty + fill.signed_qty
        avg_entry_price = self.avg_entry_price
        realized_delta = ZERO

        if current_qty == ZERO or _same_direction(current_qty, fill.signed_qty):
            existing_abs_qty = abs(current_qty)
            incoming_abs_qty = abs(fill.signed_qty)
            combined_abs_qty = existing_abs_qty + incoming_abs_qty
            existing_avg = avg_entry_price if avg_entry_price is not None else fill.fill_price
            avg_entry_price = ((existing_abs_qty * existing_avg) + (incoming_abs_qty * fill.fill_price)) / combined_abs_qty
        else:
            closing_qty = min(abs(current_qty), abs(fill.signed_qty))
            existing_avg = avg_entry_price if avg_entry_price is not None else fill.fill_price
            if current_qty > ZERO:
                realized_delta = (fill.fill_price - existing_avg) * closing_qty
            else:
                realized_delta = (existing_avg - fill.fill_price) * closing_qty

            if new_qty == ZERO:
                avg_entry_price = None
            elif _same_direction(current_qty, new_qty):
                avg_entry_price = existing_avg
            else:
                avg_entry_price = fill.fill_price

        if fill.signed_qty > ZERO:
            cash_delta = -(fill.gross_notional + fill.fee_cost)
        else:
            cash_delta = fill.gross_notional - fill.fee_cost

        return LedgerState(
            symbol=self.symbol,
            cash=self.cash + cash_delta,
            position_qty=new_qty,
            avg_entry_price=avg_entry_price,
            cumulative_fees=self.cumulative_fees + fill.fee_cost,
            cumulative_slippage=self.cumulative_slippage + fill.slippage_cost,
            realized_pnl=self.realized_pnl + realized_delta,
            initial_equity=self.initial_equity,
            updated_at_utc=as_of_utc,
        )


def bootstrap_ledger_state(
    *,
    symbol: str,
    initial_equity: Decimal,
    as_of_utc: str,
    position_qty: Decimal = ZERO,
    avg_entry_price: Decimal | None = None,
) -> LedgerState:
    position_cost_basis = ZERO if avg_entry_price is None else position_qty * avg_entry_price
    return LedgerState(
        symbol=symbol,
        cash=initial_equity - position_cost_basis,
        position_qty=position_qty,
        avg_entry_price=avg_entry_price,
        cumulative_fees=ZERO,
        cumulative_slippage=ZERO,
        realized_pnl=ZERO,
        initial_equity=initial_equity,
        updated_at_utc=as_of_utc,
    )


def snapshot_ledger_state(state: LedgerState, as_of_utc: str) -> LedgerState:
    return LedgerState(
        symbol=state.symbol,
        cash=state.cash,
        position_qty=state.position_qty,
        avg_entry_price=state.avg_entry_price,
        cumulative_fees=state.cumulative_fees,
        cumulative_slippage=state.cumulative_slippage,
        realized_pnl=state.realized_pnl,
        initial_equity=state.initial_equity,
        updated_at_utc=as_of_utc,
    )


def bootstrap_ledger_state_from_position(
    *,
    symbol: str,
    initial_equity: Decimal,
    as_of_utc: str,
    position_qty: Decimal,
    avg_entry_price: Decimal | None,
) -> LedgerState:
    return bootstrap_ledger_state(
        symbol=symbol,
        initial_equity=initial_equity,
        as_of_utc=as_of_utc,
        position_qty=position_qty,
        avg_entry_price=avg_entry_price,
    )


def load_ledger_state(
    path: str,
    *,
    symbol: str,
    initial_equity: Decimal,
    as_of_utc: str,
    position_qty: Decimal = ZERO,
    avg_entry_price: Decimal | None = None,
) -> LedgerState:
    target = Path(path)

    try:
        payload = json.loads(target.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return bootstrap_ledger_state_from_position(
            symbol=symbol,
            initial_equity=initial_equity,
            as_of_utc=as_of_utc,
            position_qty=position_qty,
            avg_entry_price=avg_entry_price,
        )
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        return bootstrap_ledger_state_from_position(
            symbol=symbol,
            initial_equity=initial_equity,
            as_of_utc=as_of_utc,
            position_qty=position_qty,
            avg_entry_price=avg_entry_price,
        )

    if not isinstance(payload, dict):
        return bootstrap_ledger_state_from_position(
            symbol=symbol,
            initial_equity=initial_equity,
            as_of_utc=as_of_utc,
            position_qty=position_qty,
            avg_entry_price=avg_entry_price,
        )

    payload_symbol = str(payload.get("symbol") or symbol)
    if payload_symbol != symbol:
        return bootstrap_ledger_state_from_position(
            symbol=symbol,
            initial_equity=initial_equity,
            as_of_utc=as_of_utc,
            position_qty=position_qty,
            avg_entry_price=avg_entry_price,
        )

    cash = _decimal_or_default(payload.get("cash"), initial_equity)
    saved_position_qty = _decimal_or_default(payload.get("position_qty"), position_qty)
    saved_avg_entry_price = _decimal_or_default(payload.get("avg_entry_price"), avg_entry_price)
    cumulative_fees = _decimal_or_default(payload.get("cumulative_fees"), ZERO)
    cumulative_slippage = _decimal_or_default(payload.get("cumulative_slippage"), ZERO)
    realized_pnl = _decimal_or_default(payload.get("realized_pnl"), ZERO)
    saved_initial_equity = _decimal_or_default(payload.get("initial_equity"), initial_equity)
    updated_at = str(payload.get("updated_at_utc") or as_of_utc)

    return LedgerState(
        symbol=symbol,
        cash=cash if cash is not None else initial_equity,
        position_qty=saved_position_qty if saved_position_qty is not None else position_qty,
        avg_entry_price=saved_avg_entry_price,
        cumulative_fees=cumulative_fees if cumulative_fees is not None else ZERO,
        cumulative_slippage=cumulative_slippage if cumulative_slippage is not None else ZERO,
        realized_pnl=realized_pnl if realized_pnl is not None else ZERO,
        initial_equity=saved_initial_equity if saved_initial_equity is not None else initial_equity,
        updated_at_utc=updated_at,
    )


def save_ledger_state(path: str, state: LedgerState) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(state.to_dict(), sort_keys=True, indent=2), encoding="utf-8")
