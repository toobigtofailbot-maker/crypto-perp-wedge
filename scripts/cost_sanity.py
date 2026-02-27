from src.costs import fee_pnl_impact, slippage_pnl_impact, funding_pnl_impact, total_cost_pnl_impact

def main():
    fee_rate_taker = 0.0004  # 4 bps example

    # --- Trade example: BUY 0.01 BTC ---
    qty = 0.01
    mid = 100_000.0
    exe = 100_020.0  # worse for buy
    fee = fee_pnl_impact(qty, exe, fee_rate_taker)
    slip = slippage_pnl_impact(qty, mid, exe)

    print("=== TRADE EXAMPLE (BUY) ===")
    print("fee pnl impact:", fee)      # expected negative
    print("slip pnl impact:", slip)    # expected negative
    print("trade total:", fee + slip)

    # --- Funding example: LONG pays when funding_rate > 0 ---
    pos_long = +0.01
    mark = 100_000.0
    fr = 0.0001  # 0.01%
    f_long = funding_pnl_impact(pos_long, mark, fr)

    print("\n=== FUNDING EXAMPLE (LONG, positive rate) ===")
    print("funding pnl impact:", f_long)  # expected negative

    # --- Funding example: SHORT receives when funding_rate > 0 ---
    pos_short = -0.01
    f_short = funding_pnl_impact(pos_short, mark, fr)

    print("\n=== FUNDING EXAMPLE (SHORT, positive rate) ===")
    print("funding pnl impact:", f_short)  # expected positive

    # --- Aggregate example ---
    agg = total_cost_pnl_impact(
        trade_qty_base=qty,
        mid_price_usdt=mid,
        exec_price_usdt=exe,
        fee_rate=fee_rate_taker,
        position_qty_base_for_funding=pos_long,
        mark_price_usdt_for_funding=mark,
        funding_rate=fr,
    )

    print("\n=== AGGREGATE (trade + funding) ===")
    print("aggregate pnl impact:", agg)

if __name__ == "__main__":
    main()