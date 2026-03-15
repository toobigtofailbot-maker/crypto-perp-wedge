from __future__ import annotations

import json
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any


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


@dataclass(frozen=True)
class PositionState:
    symbol: str
    qty: Decimal
    avg_entry_price: Decimal | None
    last_fill_price: Decimal | None
    last_fill_qty: Decimal | None
    updated_at_utc: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "symbol": self.symbol,
            "qty": _decimal_text(self.qty),
            "avg_entry_price": _decimal_text(self.avg_entry_price),
            "last_fill_price": _decimal_text(self.last_fill_price),
            "last_fill_qty": _decimal_text(self.last_fill_qty),
            "updated_at_utc": self.updated_at_utc,
        }


def flat_position_state(symbol: str, as_of_utc: str) -> PositionState:
    return PositionState(
        symbol=symbol,
        qty=ZERO,
        avg_entry_price=None,
        last_fill_price=None,
        last_fill_qty=None,
        updated_at_utc=as_of_utc,
    )


def snapshot_position_state(state: PositionState, as_of_utc: str) -> PositionState:
    return PositionState(
        symbol=state.symbol,
        qty=state.qty,
        avg_entry_price=state.avg_entry_price,
        last_fill_price=state.last_fill_price,
        last_fill_qty=state.last_fill_qty,
        updated_at_utc=as_of_utc,
    )


def load_position_state(path: str, symbol: str, as_of_utc: str) -> PositionState:
    target = Path(path)

    try:
        payload = json.loads(target.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return flat_position_state(symbol, as_of_utc)
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        return flat_position_state(symbol, as_of_utc)

    if not isinstance(payload, dict):
        return flat_position_state(symbol, as_of_utc)

    payload_symbol = str(payload.get("symbol") or symbol)
    if payload_symbol != symbol:
        return flat_position_state(symbol, as_of_utc)

    qty = _decimal_or_default(payload.get("qty"), ZERO)
    avg_entry_price = _decimal_or_default(payload.get("avg_entry_price"))
    last_fill_price = _decimal_or_default(payload.get("last_fill_price"))
    last_fill_qty = _decimal_or_default(payload.get("last_fill_qty"))
    updated_at = str(payload.get("updated_at_utc") or as_of_utc)

    if qty is None:
        qty = ZERO

    return PositionState(
        symbol=symbol,
        qty=qty,
        avg_entry_price=avg_entry_price,
        last_fill_price=last_fill_price,
        last_fill_qty=last_fill_qty,
        updated_at_utc=updated_at,
    )


def save_position_state(path: str, state: PositionState) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(state.to_dict(), sort_keys=True, indent=2), encoding="utf-8")


def position_delta_qty(current_qty: Decimal, target_qty: Decimal) -> Decimal:
    return target_qty - current_qty


def apply_fill_to_position(
    state: PositionState,
    signed_fill_qty: Decimal,
    fill_price: Decimal,
    as_of_utc: str,
) -> PositionState:
    if signed_fill_qty == ZERO:
        return snapshot_position_state(state, as_of_utc)

    current_qty = state.qty
    new_qty = current_qty + signed_fill_qty

    if current_qty == ZERO or (current_qty > ZERO and signed_fill_qty > ZERO) or (current_qty < ZERO and signed_fill_qty < ZERO):
        existing_abs_qty = abs(current_qty)
        incoming_abs_qty = abs(signed_fill_qty)
        combined_abs_qty = existing_abs_qty + incoming_abs_qty
        existing_avg = state.avg_entry_price if state.avg_entry_price is not None else fill_price
        avg_entry_price = ((existing_abs_qty * existing_avg) + (incoming_abs_qty * fill_price)) / combined_abs_qty
    else:
        if new_qty == ZERO:
            avg_entry_price = None
        elif (current_qty > ZERO and new_qty > ZERO) or (current_qty < ZERO and new_qty < ZERO):
            avg_entry_price = state.avg_entry_price
        else:
            avg_entry_price = fill_price

    return PositionState(
        symbol=state.symbol,
        qty=new_qty,
        avg_entry_price=avg_entry_price,
        last_fill_price=fill_price,
        last_fill_qty=signed_fill_qty,
        updated_at_utc=as_of_utc,
    )
