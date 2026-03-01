#!/usr/bin/env python3
"""G4 live API smoke test for Binance UM Futures.

Hard constraints enforced:
- Live endpoint only (https://fapi.binance.com)
- Credentials sourced only from BINANCE_API_KEY / BINANCE_API_SECRET via os.getenv
- No order placement
- Local logs under logs/g4_api_smoke_test/
- Report written to reports/g4_api_smoke_test/g4_api_smoke_test_report.json
- Exit codes: PASS=>0, FAIL=>1
"""

from __future__ import annotations

import json
import logging
import os
import sys
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable

from binance.um_futures import UMFutures

BASE_URL = "https://fapi.binance.com"
REPORT_PATH = Path("reports/g4_api_smoke_test/g4_api_smoke_test_report.json")
LOG_DIR = Path("logs/g4_api_smoke_test")
SYMBOL = "BTCUSDT"


@dataclass
class CheckResult:
    name: str
    passed: bool
    latency_ms: int
    details: dict[str, Any] | None = None
    error: str | None = None


def utc_now_iso() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def setup_logger() -> Path:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOG_DIR / f"g4_api_smoke_test_{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}.log"

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


def run_check(name: str, fn: Callable[[], Any]) -> CheckResult:
    start = time.perf_counter()
    try:
        response = fn()
        latency_ms = int((time.perf_counter() - start) * 1000)
        details: dict[str, Any]
        if isinstance(response, dict):
            details = {"keys": sorted(response.keys())[:10]}
        elif isinstance(response, list):
            details = {"items": len(response)}
        else:
            details = {"type": type(response).__name__}

        logging.info("PASS %s (%d ms)", name, latency_ms)
        return CheckResult(name=name, passed=True, latency_ms=latency_ms, details=details)
    except Exception as exc:  # noqa: BLE001
        latency_ms = int((time.perf_counter() - start) * 1000)
        logging.exception("FAIL %s (%d ms)", name, latency_ms)
        return CheckResult(name=name, passed=False, latency_ms=latency_ms, error=str(exc))


def build_client() -> tuple[UMFutures, bool, bool]:
    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")

    api_key_present = bool(api_key)
    api_secret_present = bool(api_secret)

    client = UMFutures(key=api_key, secret=api_secret, base_url=BASE_URL)
    return client, api_key_present, api_secret_present


def main() -> int:
    log_path = setup_logger()
    started_at = utc_now_iso()

    client, api_key_present, api_secret_present = build_client()

    checks = [
        run_check("ping", lambda: client.ping()),
        run_check("server_time", lambda: client.time()),
        run_check("exchange_info", lambda: client.exchange_info(symbol=SYMBOL)),
        run_check("ticker_price", lambda: client.ticker_price(symbol=SYMBOL)),
        run_check("order_book_depth", lambda: client.depth(symbol=SYMBOL, limit=5)),
    ]

    if api_key_present and api_secret_present:
        checks.append(run_check("account_balance", lambda: client.balance()))
    else:
        checks.append(
            CheckResult(
                name="account_balance",
                passed=False,
                latency_ms=0,
                error="BINANCE_API_KEY and/or BINANCE_API_SECRET not set in environment",
            )
        )
        logging.error("FAIL account_balance (0 ms): missing environment credentials")

    passed_count = sum(1 for item in checks if item.passed)
    failed_count = len(checks) - passed_count
    overall_pass = failed_count == 0
    exit_code = 0 if overall_pass else 1

    report = {
        "g4_spec_version": "1.0",
        "suite": "g4_api_smoke_test",
        "status": "PASS" if overall_pass else "FAIL",
        "exit_code": exit_code,
        "base_url": BASE_URL,
        "started_at_utc": started_at,
        "finished_at_utc": utc_now_iso(),
        "environment": {
            "live_only": True,
            "symbol": SYMBOL,
        },
        "credentials": {
            "api_key_present": api_key_present,
            "api_secret_present": api_secret_present,
            "source": "os.getenv",
        },
        "summary": {
            "total_checks": len(checks),
            "passed_checks": passed_count,
            "failed_checks": failed_count,
        },
        "checks": [
            {
                "name": item.name,
                "passed": item.passed,
                "latency_ms": item.latency_ms,
                "details": item.details,
                "error": item.error,
            }
            for item in checks
        ],
        "artifacts": {
            "report_path": str(REPORT_PATH),
            "log_path": str(log_path),
        },
        "constraints": {
            "orders_placed": False,
            "custom_rest_signer_used": False,
            "framework": "binance-futures-connector (UMFutures)",
        },
    }

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    logging.info("Report written to %s", REPORT_PATH)
    logging.info("Completed with status=%s exit_code=%d", report["status"], exit_code)

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
