from src.costs import fee_pnl_impact, slippage_pnl_impact, funding_pnl_impact

def main():
    fee_rate = 0.0004  # 4 bps taker example

    # Scenario:
    # - Enter long 0.01 BTC at exec 100020, mid 100000
    # - One funding event at mark 100000, funding_rate = +0.0001 (long pays)
    # - Exit long 0.01 BTC at exec 100010, mid 100000 (still slightly worse for sell? actually sell worse if exec < mid)
    #   For exit (sell), qty is negative (closing long = sell 0.01)

    entry_qty = +0.01
    entry_mid = 100_000.0
    entry_exec = 100_020.0

    entry_fee = fee_pnl_impact(entry_qty, entry_exec, fee_rate)
    entry_slip = slippage_pnl_impact(entry_qty, entry_mid, entry_exec)

    pos_qty = +0.01
    funding_mark = 100_000.0
    funding_rate = 0.0001
    funding_cf = funding_pnl_impact(pos_qty, funding_mark, funding_rate)

    exit_qty = -0.01  # sell to close
    exit_mid = 100_000.0
    exit_exec = 99_990.0  # worse for sell (exec < mid) -> negative slippage

    exit_fee = fee_pnl_impact(exit_qty, exit_exec, fee_rate)
    exit_slip = slippage_pnl_impact(exit_qty, exit_mid, exit_exec)

    total = entry_fee + entry_slip + funding_cf + exit_fee + exit_slip

    print("=== BASELINE ACCOUNTING: 1 TRADE + 1 FUNDING + EXIT ===")
    print("entry_fee:", entry_fee)
    print("entry_slippage:", entry_slip)
    print("funding_cashflow:", funding_cf)
    print("exit_fee:", exit_fee)
    print("exit_slippage:", exit_slip)
    print("TOTAL pnl impact:", total)

if __name__ == "__main__":
    main()