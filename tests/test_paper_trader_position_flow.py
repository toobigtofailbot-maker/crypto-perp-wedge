from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

from src.paper.position_state import PositionState, save_position_state
from src.runtime.paper_trader import run_once


def test_flat_signal_emits_position_and_ledger_events_without_fill(tmp_path: Path) -> None:
    event_log_path = tmp_path / "logs" / "paper_trader" / "events.jsonl"
    ledger_path = tmp_path / "logs" / "paper_trader" / "ledger.jsonl"
    ledger_state_path = tmp_path / "logs" / "paper_trader" / "ledger_state.json"
    position_state_path = tmp_path / "logs" / "paper_trader" / "position_state.json"
    config_path = tmp_path / "paper_runtime.json"

    config = {
        "env": "PAPER",
        "symbol": "BTCUSDT",
        "decision_id": "D-0001",
        "macro_flags_path": str(tmp_path / "missing_macro_window_flags.json"),
        "event_log_path": str(event_log_path),
        "evaluation_time_source": "fixed",
        "evaluation_time_utc": "2026-01-01T01:00:00Z",
        "run_id": "RUN-TEST-POSITION-1",
        "correlation_id": "RUN-TEST-POSITION-1",
        "signal_provider": "flat",
        "paper_position_state_path": str(position_state_path),
        "paper_ledger_path": str(ledger_path),
        "paper_ledger_state_path": str(ledger_state_path),
        "paper_fill_price_mode": "fixed",
        "paper_fill_price_fixed": 100000,
        "slippage_bps": 10,
        "fee_bps": 5,
        "initial_equity": 250000,
    }
    config_path.write_text(json.dumps(config), encoding="utf-8")

    exit_code = run_once(str(config_path))

    assert exit_code == 0

    events = [json.loads(line) for line in event_log_path.read_text(encoding="utf-8").splitlines()]
    event_types = [event["event_type"] for event in events]

    assert "PositionEvent" in event_types
    assert "LedgerEvent" in event_types
    assert "FillEvent" not in event_types

    position_event = next(event for event in events if event["event_type"] == "PositionEvent")
    ledger_event = next(event for event in events if event["event_type"] == "LedgerEvent")

    assert position_event["payload"]["traded"] is False
    assert position_event["payload"]["current_qty_before"] == "0"
    assert position_event["payload"]["position_qty_after"] == "0"

    assert ledger_event["payload"]["traded"] is False
    assert ledger_event["payload"]["position_qty"] == "0"
    assert ledger_event["payload"]["mark_price"] == "100000"
    assert ledger_event["payload"]["realized_pnl"] == "0"
    assert ledger_event["payload"]["unrealized_pnl"] == "0"
    assert ledger_event["payload"]["cumulative_fees"] == "0"
    assert ledger_event["payload"]["cumulative_slippage"] == "0"

    saved_state = json.loads(position_state_path.read_text(encoding="utf-8"))
    saved_ledger = json.loads(ledger_state_path.read_text(encoding="utf-8"))
    assert saved_state["qty"] == "0"
    assert saved_ledger["cash"] == "250000"
    assert saved_ledger["position_qty"] == "0"
    assert ledger_path.exists() is False


def test_existing_position_flattens_with_fill_and_ledger_event(tmp_path: Path) -> None:
    event_log_path = tmp_path / "logs" / "paper_trader" / "events.jsonl"
    ledger_path = tmp_path / "logs" / "paper_trader" / "ledger.jsonl"
    ledger_state_path = tmp_path / "logs" / "paper_trader" / "ledger_state.json"
    position_state_path = tmp_path / "logs" / "paper_trader" / "position_state.json"
    config_path = tmp_path / "paper_runtime.json"

    save_position_state(
        str(position_state_path),
        PositionState(
            symbol="BTCUSDT",
            qty=Decimal("1.5"),
            avg_entry_price=Decimal("95000"),
            last_fill_price=None,
            last_fill_qty=None,
            updated_at_utc="2025-12-31T23:00:00Z",
        ),
    )

    config = {
        "env": "PAPER",
        "symbol": "BTCUSDT",
        "decision_id": "D-0001",
        "macro_flags_path": str(tmp_path / "missing_macro_window_flags.json"),
        "event_log_path": str(event_log_path),
        "evaluation_time_source": "fixed",
        "evaluation_time_utc": "2026-01-01T01:00:00Z",
        "run_id": "RUN-TEST-POSITION-2",
        "correlation_id": "RUN-TEST-POSITION-2",
        "signal_provider": "flat",
        "paper_position_state_path": str(position_state_path),
        "paper_ledger_path": str(ledger_path),
        "paper_ledger_state_path": str(ledger_state_path),
        "paper_fill_price_mode": "fixed",
        "paper_fill_price_fixed": 100000,
        "slippage_bps": 10,
        "fee_bps": 5,
        "initial_equity": 200000,
    }
    config_path.write_text(json.dumps(config), encoding="utf-8")

    exit_code = run_once(str(config_path))

    assert exit_code == 0

    events = [json.loads(line) for line in event_log_path.read_text(encoding="utf-8").splitlines()]
    event_types = [event["event_type"] for event in events]
    assert "FillEvent" in event_types
    assert "PositionEvent" in event_types
    assert "LedgerEvent" in event_types

    fill_event = next(event for event in events if event["event_type"] == "FillEvent")
    position_event = next(event for event in events if event["event_type"] == "PositionEvent")
    ledger_event = next(event for event in events if event["event_type"] == "LedgerEvent")

    assert fill_event["payload"]["fill"]["side"] == "SELL"
    assert fill_event["payload"]["fill"]["signed_qty"] == "-1.5"
    assert fill_event["payload"]["fill"]["fill_price"] == "99900"
    assert fill_event["payload"]["fill"]["fee_cost"] == "75"
    assert fill_event["payload"]["fill"]["slippage_cost"] == "150"

    assert position_event["payload"]["traded"] is True
    assert position_event["payload"]["current_qty_before"] == "1.5"
    assert position_event["payload"]["position_qty_after"] == "0"

    assert ledger_event["payload"]["traded"] is True
    assert ledger_event["payload"]["position_qty"] == "0"
    assert ledger_event["payload"]["mark_price"] == "100000"
    assert ledger_event["payload"]["realized_pnl"] == "7350"
    assert ledger_event["payload"]["unrealized_pnl"] == "0"
    assert ledger_event["payload"]["cumulative_fees"] == "75"
    assert ledger_event["payload"]["cumulative_slippage"] == "150"

    saved_state = json.loads(position_state_path.read_text(encoding="utf-8"))
    saved_ledger = json.loads(ledger_state_path.read_text(encoding="utf-8"))
    assert saved_state["qty"] == "0"
    assert saved_ledger["realized_pnl"] == "7350"
    assert saved_ledger["cumulative_fees"] == "75"
    assert saved_ledger["cumulative_slippage"] == "150"

    ledger_entries = [json.loads(line) for line in ledger_path.read_text(encoding="utf-8").splitlines()]
    assert len(ledger_entries) == 1
    assert ledger_entries[0]["fill"]["client_order_id"].startswith("PAPER-")
    assert ledger_entries[0]["ledger_state_after"]["realized_pnl"] == "7350"
