from __future__ import annotations

from dataclasses import dataclass

# ----------------------------
# Core conventions
# ----------------------------
# qty_base: signed quantity in BTC
#   + = long / buy
#   - = short / sell
#
# All functions return PnL impact in USDT:
#   negative -> cost (PnL decreases)
#   positive -> gain (PnL increases)


def _sign(x: float) -> int:
    return 1 if x > 0 else (-1 if x < 0 else 0)


def notional_usdt(qty_base: float, price_usdt: float) -> float:
    """Absolute notional in USDT."""
    return abs(qty_base) * price_usdt


def fee_pnl_impact(qty_base: float, exec_price_usdt: float, fee_rate: float) -> float:
    """
    Trading fee PnL impact in USDT.

    fee_rate example: 0.0004 = 4 bps taker.
    Convention: always negative (fee reduces PnL).
    """
    return -notional_usdt(qty_base, exec_price_usdt) * fee_rate


def slippage_pnl_impact(qty_base: float, mid_price_usdt: float, exec_price_usdt: float) -> float:
    """
    Slippage PnL impact vs mid, in USDT.

    Interpretation:
      buy (qty>0): exec > mid => negative (worse fill)
      sell (qty<0): exec < mid => negative (worse fill)
    """
    return (mid_price_usdt - exec_price_usdt) * qty_base


def funding_pnl_impact(position_qty_base: float, mark_price_usdt: float, funding_rate: float) -> float:
    """
    Funding cashflow PnL impact in USDT for ONE funding event.

    Binance perp convention (typical):
      funding_rate > 0: longs pay, shorts receive
      funding_rate < 0: shorts pay, longs receive

    We model funding as a cashflow:
      positive -> you receive funding
      negative -> you pay funding
    """
    pos_notional = abs(position_qty_base) * mark_price_usdt
    return -pos_notional * funding_rate * _sign(position_qty_base)


def total_cost_pnl_impact(
    trade_qty_base: float,
    mid_price_usdt: float,
    exec_price_usdt: float,
    fee_rate: float,
    *,
    position_qty_base_for_funding: float | None = None,
    mark_price_usdt_for_funding: float | None = None,
    funding_rate: float | None = None,
) -> float:
    """
    Aggregate costs for convenience: fees + slippage + optional funding.

    Funding is optional; if requested, pass position_qty_base_for_funding,
    mark_price_usdt_for_funding, funding_rate.
    """
    pnl = 0.0
    pnl += fee_pnl_impact(trade_qty_base, exec_price_usdt, fee_rate)
    pnl += slippage_pnl_impact(trade_qty_base, mid_price_usdt, exec_price_usdt)

    if position_qty_base_for_funding is not None:
        if mark_price_usdt_for_funding is None or funding_rate is None:
            raise ValueError("Funding requested but mark_price_usdt_for_funding or funding_rate missing.")
        pnl += funding_pnl_impact(position_qty_base_for_funding, mark_price_usdt_for_funding, funding_rate)

    return pnl