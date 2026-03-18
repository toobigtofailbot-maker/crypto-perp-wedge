from __future__ import annotations

import json
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

import pandas as pd

from src.execution.interfaces import DesiredPosition
from src.runtime import paper_trader


def _utc_ms(value: str) -> int:
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return int(dt.astimezone(timezone.utc).timestamp() * 1000)


def _write_parquet(path: Path, rows: list[dict[str, object]]) -> None:
    pd.DataFrame(rows).to_parquet(path, index=False)


def _write_price_ref_files(tmp_path: Path) -> tuple[Path, Path]:
    book_path = tmp_path / "bookticker.parquet"
    premium_path = tmp_path / "premium.parquet"

    _write_parquet(
        book_path,
        [
            {
                "symbol": "BTCUSDT",
                "event_time_ms": _utc_ms("2026-01-01T00:59:50Z"),
                "bestBidPrice": 99999,
                "bestAskPrice": 100001,
            }
        ],
    )
    _write_parquet(
        premium_path,
        [
            {
                "symbol": "BTCUSDT",
                "event_time_ms": _utc_ms("2026-01-01T00:59:45Z"),
                "markPrice": 99888,
            }
        ],
    )

    return book_path, premium_path


def test_flat_signal_still_logs_price_ref_metadata_without_fill(tmp_path: Path) -> None:
    event_log_path = tmp_path / "logs" / "paper_trader" / "events.jsonl"
    ledger_state_path = tmp_path / "logs" / "paper_trader" / "ledger_state.json"
    config_path = tmp_path / "paper_runtime.json"
    book_path, premium_path = _write_price_ref_files(tmp_path)

    config = {
        "env": "PAPER",
        "symbol": "BTCUSDT",
        "decision_id": "D-0001",
        "macro_flags_path": str(tmp_path / "missing_macro_window_flags.json"),
        "event_log_path": str(event_log_path),
        "evaluation_time_source": "fixed",
        "evaluation_time_utc": "2026-01-01T01:00:00Z",
        "run_id": "RUN-TEST-PRICE-REF-1",
        "correlation_id": "RUN-TEST-PRICE-REF-1",
        "signal_provider": "flat",
        "paper_ledger_state_path": str(ledger_state_path),
        "paper_fill_price_mode": "mid_bookticker",
        "paper_fill_price_fixed": 77777,
        "initial_equity": 300000,
        "price_ref_paths": {
            "bookticker_parquet": str(book_path),
            "premiumindex_parquet": str(premium_path),
        },
        "price_ref_lookback_seconds": 3600,
    }
    config_path.write_text(json.dumps(config), encoding="utf-8")

    exit_code = paper_trader.run_once(str(config_path))

    assert exit_code == 0

    events = [json.loads(line) for line in event_log_path.read_text(encoding="utf-8").splitlines()]
    event_types = [event["event_type"] for event in events]

    assert "FillEvent" not in event_types

    signal_event = next(event for event in events if event["event_type"] == "SignalEvent")
    order_event = next(event for event in events if event["event_type"] == "OrderIntent")
    position_event = next(event for event in events if event["event_type"] == "PositionEvent")
    ledger_event = next(event for event in events if event["event_type"] == "LedgerEvent")

    for event in (signal_event, order_event, position_event, ledger_event):
        assert event["price_ref"] == "100000"
        assert event["price_ref_source"] == "mid_bookticker"
        assert event["price_ref_asof_utc"] == "2026-01-01T00:59:50Z"

    assert order_event["payload"]["status"] == "no_trade"
    assert ledger_event["payload"]["mark_price"] == "100000"
    assert ledger_event["payload"]["position_qty"] == "0"
    assert ledger_event["payload"]["unrealized_pnl"] == "0"


def test_fill_uses_resolved_price_ref_and_ledger_marks_same_reference(tmp_path: Path, monkeypatch) -> None:
    event_log_path = tmp_path / "logs" / "paper_trader" / "events.jsonl"
    ledger_path = tmp_path / "logs" / "paper_trader" / "ledger.jsonl"
    ledger_state_path = tmp_path / "logs" / "paper_trader" / "ledger_state.json"
    config_path = tmp_path / "paper_runtime.json"
    book_path, premium_path = _write_price_ref_files(tmp_path)

    class LongSignalProvider:
        def compute_desired_position(self, evaluation_time_utc: str, inputs: dict[str, object]) -> DesiredPosition:
            return DesiredPosition(
                symbol=str(inputs["symbol"]),
                target_qty=Decimal("2"),
                target_notional=None,
                timestamp_utc=evaluation_time_utc,
                source_timeframe="1m",
                decision_id=str(inputs["decision_id"]),
                correlation_id=str(inputs["correlation_id"]),
                run_id=str(inputs["run_id"]),
            )

    monkeypatch.setattr(paper_trader, "build_signal_provider", lambda _name: LongSignalProvider())

    config = {
        "env": "PAPER",
        "symbol": "BTCUSDT",
        "decision_id": "D-0001",
        "macro_flags_path": str(tmp_path / "missing_macro_window_flags.json"),
        "event_log_path": str(event_log_path),
        "evaluation_time_source": "fixed",
        "evaluation_time_utc": "2026-01-01T01:00:00Z",
        "run_id": "RUN-TEST-PRICE-REF-2",
        "correlation_id": "RUN-TEST-PRICE-REF-2",
        "signal_provider": "custom-long",
        "paper_ledger_path": str(ledger_path),
        "paper_ledger_state_path": str(ledger_state_path),
        "paper_fill_price_mode": "mid_bookticker",
        "paper_fill_price_fixed": 77777,
        "slippage_bps": 0,
        "fee_bps": 0,
        "initial_equity": 300000,
        "price_ref_paths": {
            "bookticker_parquet": str(book_path),
            "premiumindex_parquet": str(premium_path),
        },
        "price_ref_lookback_seconds": 3600,
    }
    config_path.write_text(json.dumps(config), encoding="utf-8")

    exit_code = paper_trader.run_once(str(config_path))

    assert exit_code == 0

    events = [json.loads(line) for line in event_log_path.read_text(encoding="utf-8").splitlines()]
    fill_event = next(event for event in events if event["event_type"] == "FillEvent")
    ledger_event = next(event for event in events if event["event_type"] == "LedgerEvent")

    assert fill_event["price_ref"] == "100000"
    assert fill_event["price_ref_source"] == "mid_bookticker"
    assert fill_event["price_ref_asof_utc"] == "2026-01-01T00:59:50Z"
    assert fill_event["payload"]["fill"]["price_ref"] == "100000"
    assert fill_event["payload"]["fill"]["price_ref_source"] == "mid_bookticker"
    assert fill_event["payload"]["fill"]["price_ref_asof_utc"] == "2026-01-01T00:59:50Z"
    assert fill_event["payload"]["fill"]["fill_price"] == "100000"
    assert fill_event["payload"]["fill"]["fill_price"] != "77777"

    assert ledger_event["price_ref"] == "100000"
    assert ledger_event["price_ref_source"] == "mid_bookticker"
    assert ledger_event["price_ref_asof_utc"] == "2026-01-01T00:59:50Z"
    assert ledger_event["payload"]["mark_price"] == "100000"
    assert ledger_event["payload"]["position_qty"] == "2"
    assert ledger_event["payload"]["avg_entry_price"] == "100000"
    assert ledger_event["payload"]["unrealized_pnl"] == "0"

    ledger_entries = [json.loads(line) for line in ledger_path.read_text(encoding="utf-8").splitlines()]
    assert len(ledger_entries) == 1
    assert ledger_entries[0]["fill"]["price_ref"] == "100000"
    assert ledger_entries[0]["fill"]["price_ref_source"] == "mid_bookticker"
