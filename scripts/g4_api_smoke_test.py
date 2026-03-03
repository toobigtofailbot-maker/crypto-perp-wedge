#!/usr/bin/env python3
"""G4 live API smoke test for Binance UM Futures.

Workflow implemented by this script:
exchange_info -> compute far-away LIMIT within filters -> optional /fapi/v1/order/test
-> place LIMIT -> immediately cancel -> post checks.

Hard constraints enforced:
- Live endpoint only (https://fapi.binance.com)
- Uses binance-futures-connector (UMFutures)
- Credentials sourced from BINANCE_API_KEY / BINANCE_API_SECRET via os.getenv
- Local logs under logs/g4_api_smoke_test/
- Report written to reports/g4_api_smoke_test/g4_api_smoke_test_report.json
- Exit codes: PASS=>0, FAIL=>1
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import platform
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, ROUND_CEILING, ROUND_DOWN
from pathlib import Path
from typing import Any
from importlib.metadata import PackageNotFoundError, version


BASE_URL = "https://fapi.binance.com"
REPORT_PATH = Path("reports/g4_api_smoke_test/g4_api_smoke_test_report.json")
LOG_DIR = Path("logs/g4_api_smoke_test")


@dataclass
class SymbolFilters:
    min_qty: Decimal
    step_size: Decimal
    min_notional: Decimal
    price_precision: int
    quantity_precision: int
    tick_size: Decimal
    min_price: Decimal
    max_price: Decimal
    multiplier_up: Decimal | None


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def setup_logger() -> Path:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOG_DIR / f"g4_api_smoke_test_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.log"

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    return log_path




def get_connector_version() -> str:
    try:
        return version("binance-futures-connector")
    except PackageNotFoundError:
        return "UNKNOWN"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="G4 API smoke test (live UM Futures)")
    parser.add_argument("--env", required=True, choices=["LIVE"], help="Must be LIVE")
    parser.add_argument("--symbol", required=True, help="UM Futures symbol, e.g. BTCUSDT")
    parser.add_argument(
        "--skip-order-test",
        action="store_true",
        help="Skip /fapi/v1/order/test pre-check before place+cancel",
    )
    return parser.parse_args()


def get_git_commit_id() -> str:
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL)
            .strip()
        )
    except Exception:  # noqa: BLE001
        return "UNKNOWN"


def dec(value: Any) -> Decimal:
    return Decimal(str(value))


def quantize_to_step(value: Decimal, step: Decimal, rounding: str) -> Decimal:
    if step <= 0:
        return value
    units = (value / step).to_integral_value(rounding=rounding)
    return units * step


def extract_filters(exchange_info: dict[str, Any], symbol: str) -> SymbolFilters:
    symbols = exchange_info.get("symbols", [])
    symbol_info = next((item for item in symbols if item.get("symbol") == symbol), None)
    if symbol_info is None:
        raise ValueError(f"Symbol {symbol} not found in exchange_info")

    filters_by_type = {flt["filterType"]: flt for flt in symbol_info.get("filters", [])}
    lot = filters_by_type.get("LOT_SIZE", {})
    notional = filters_by_type.get("MIN_NOTIONAL", {})
    price_filter = filters_by_type.get("PRICE_FILTER", {})
    percent_price = filters_by_type.get("PERCENT_PRICE", {})

    return SymbolFilters(
        min_qty=dec(lot.get("minQty", "0")),
        step_size=dec(lot.get("stepSize", "0.000001")),
        min_notional=dec(notional.get("notional", "0")),
        price_precision=int(symbol_info.get("pricePrecision", 0)),
        quantity_precision=int(symbol_info.get("quantityPrecision", 0)),
        tick_size=dec(price_filter.get("tickSize", "0.01")),
        min_price=dec(price_filter.get("minPrice", "0")),
        max_price=dec(price_filter.get("maxPrice", "0")),
        multiplier_up=dec(percent_price["multiplierUp"]) if "multiplierUp" in percent_price else None,
    )


def compute_order_params(current_price: Decimal, filters: SymbolFilters) -> tuple[str, Decimal, Decimal]:
    side = "SELL"

    candidate_price = current_price * Decimal("1.30")
    if filters.multiplier_up is not None and filters.multiplier_up > 0:
        candidate_price = min(candidate_price, current_price * filters.multiplier_up * Decimal("0.98"))

    if filters.max_price > 0:
        candidate_price = min(candidate_price, filters.max_price)
    if filters.min_price > 0:
        candidate_price = max(candidate_price, filters.min_price)

    price = quantize_to_step(candidate_price, filters.tick_size, ROUND_DOWN)

    qty = filters.min_qty
    if filters.min_notional > 0:
        min_qty_for_notional = filters.min_notional / max(price, Decimal("0.00000001"))
        qty = max(qty, min_qty_for_notional)
    qty = quantize_to_step(qty, filters.step_size, ROUND_CEILING)

    if qty <= 0 or price <= 0:
        raise ValueError("Computed non-positive price/qty")

    return side, price, qty


def main() -> int:
    args = parse_args()
    log_path = setup_logger()

    if args.env != "LIVE":
        logging.error("Only --env LIVE is allowed")
        return 1

    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")
    if not api_key or not api_secret:
        logging.error("Missing BINANCE_API_KEY and/or BINANCE_API_SECRET")
        return 1

    try:
        from binance.um_futures import UMFutures
    except ModuleNotFoundError as exc:
        logging.error("binance-futures-connector is required: %s", exc)
        return 1

    client = UMFutures(key=api_key, secret=api_secret, base_url=BASE_URL)

    report: dict[str, Any] = {
        "status": "FAIL",
        "env": args.env,
        "base_url": BASE_URL,
        "symbol": args.symbol,
        "timestamp_utc": utc_now_iso(),
        "git_commit_id": get_git_commit_id(),
        "python_version": platform.python_version(),
        "connector_version": get_connector_version(),
        "filters_snapshot": {
            "minQty": None,
            "stepSize": None,
            "minNotional": None,
            "pricePrecision": None,
            "quantityPrecision": None,
            "tickSize": None,
            "minPrice": None,
            "maxPrice": None,
        },
        "pre_checks": {
            "server_time_ok": False,
            "permissions_ok": False,
        },
        "order_test": {
            "attempted": False,
            "ok": False,
            "error": None,
        },
        "place_order": {
            "attempted": False,
            "clientOrderId": None,
            "orderId": None,
            "status": None,
            "price": None,
            "qty": None,
        },
        "cancel_order": {
            "attempted": False,
            "ok": False,
            "status": None,
        },
        "post_state": {
            "open_orders_count": None,
            "position_amt": None,
        },
        "exit_code": 1,
    }

    exit_code = 1
    error_summary: str | None = None

    try:
        server_time = client.time()
        report["pre_checks"]["server_time_ok"] = isinstance(server_time, dict) and "serverTime" in server_time

        account_info = client.account()
        report["pre_checks"]["permissions_ok"] = isinstance(account_info, dict)

        exchange_info = client.exchange_info()
        filters = extract_filters(exchange_info, args.symbol)
        report["filters_snapshot"] = {
            "minQty": str(filters.min_qty),
            "stepSize": str(filters.step_size),
            "minNotional": str(filters.min_notional),
            "pricePrecision": filters.price_precision,
            "quantityPrecision": filters.quantity_precision,
            "tickSize": str(filters.tick_size),
            "minPrice": str(filters.min_price),
            "maxPrice": str(filters.max_price),
        }

        ticker = client.ticker_price(symbol=args.symbol)
        current_price = dec(ticker["price"])
        side, price, qty = compute_order_params(current_price, filters)

        order_payload = {
            "symbol": args.symbol,
            "side": side,
            "type": "LIMIT",
            "timeInForce": "GTC",
            "price": format(price, "f"),
            "quantity": format(qty, "f"),
            "newClientOrderId": f"g4-smoke-{int(datetime.now(timezone.utc).timestamp())}",
        }

        report["place_order"]["price"] = order_payload["price"]
        report["place_order"]["qty"] = order_payload["quantity"]
        report["place_order"]["clientOrderId"] = order_payload["newClientOrderId"]

        if not args.skip_order_test:
            report["order_test"]["attempted"] = True
            try:
                client.new_order_test(**order_payload)
                report["order_test"]["ok"] = True
            except Exception as exc:  # noqa: BLE001
                report["order_test"]["ok"] = False
                report["order_test"]["error"] = str(exc)
                raise

        report["place_order"]["attempted"] = True
        placed = client.new_order(**order_payload)
        report["place_order"]["orderId"] = placed.get("orderId")
        report["place_order"]["status"] = placed.get("status")

        report["cancel_order"]["attempted"] = True
        canceled = client.cancel_order(symbol=args.symbol, orderId=placed["orderId"])
        report["cancel_order"]["ok"] = True
        report["cancel_order"]["status"] = canceled.get("status")

        open_orders = client.get_open_orders(symbol=args.symbol)
        report["post_state"]["open_orders_count"] = len(open_orders)

        positions = client.get_position_risk(symbol=args.symbol)
        if not positions:
            raise RuntimeError(f"No position_risk returned for {args.symbol}")
        position_amt = dec(positions[0].get("positionAmt", "0"))
        report["post_state"]["position_amt"] = str(position_amt)

        all_good = (
            report["pre_checks"]["server_time_ok"]
            and report["pre_checks"]["permissions_ok"]
            and report["place_order"]["attempted"]
            and report["cancel_order"]["ok"]
            and report["post_state"]["open_orders_count"] == 0
            and position_amt == 0
        )

        exit_code = 0 if all_good else 1
        if not all_good:
            error_summary = "Post-checks failed (open orders and/or position not flat)."

    except Exception as exc:  # noqa: BLE001
        error_summary = str(exc)
        logging.exception("G4 smoke test failed")

    report["status"] = "PASS" if exit_code == 0 else "FAIL"
    report["exit_code"] = exit_code
    if exit_code != 0 and error_summary:
        report["error_summary"] = error_summary

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    logging.info("Report written to %s", REPORT_PATH)
    logging.info("Local log written to %s", log_path)
    logging.info("Completed status=%s exit_code=%d", report["status"], exit_code)

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
