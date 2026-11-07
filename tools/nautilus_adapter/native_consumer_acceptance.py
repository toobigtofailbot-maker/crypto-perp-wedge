"""Manual acceptance of the real consumer, not a runtime supervisor or evidence authority."""
import argparse
import asyncio
import json
import time
from decimal import Decimal


async def execute(config_path, *, synthetic_case=None, recovery=False):
    from src.runtime.paper_trader import run_native_noncapital

    if recovery:
        from src.execution.nautilus_native_backend import recover
        with open(config_path, encoding="utf-8") as stream:
            return await recover(json.load(stream))
    if synthetic_case is None:
        return await run_native_noncapital(config_path)
    from nautilus_trader.model.data import QuoteTick
    from nautilus_trader.model.objects import Price, Quantity
    from nautilus_trader.test_kit.providers import TestInstrumentProvider
    from src.execution.interfaces import DesiredPosition

    instrument = TestInstrumentProvider.btcusdt_perp_binance()
    targets = iter(["0.001"] if synthetic_case == "open" else ["0.001", "0"])

    class FixtureProvider:
        def compute_desired_position(self, evaluation_time_utc, inputs):
            return DesiredPosition(symbol="BTCUSDT", target_qty=Decimal(next(targets)),
                target_notional=None, timestamp_utc=evaluation_time_utc, source_timeframe="1m",
                decision_id="D-0001", correlation_id=inputs["correlation_id"], run_id=inputs["run_id"])

    def ticks():
        for _ in range(1 if synthetic_case == "open" else 2):
            now = time.time_ns()
            yield QuoteTick(instrument.id, Price.from_str("99999.0"), Price.from_str("100000.0"),
                Quantity.from_str("1.000"), Quantity.from_str("1.000"), now, now)

    return await run_native_noncapital(config_path, signal_provider=FixtureProvider(),
                                      ticks=ticks(), instrument=instrument)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--synthetic-case", choices=("open", "flat"))
    modes.add_argument("--recover", action="store_true")
    args = parser.parse_args()
    result = asyncio.run(execute(args.config, synthetic_case=args.synthetic_case, recovery=args.recover))
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
