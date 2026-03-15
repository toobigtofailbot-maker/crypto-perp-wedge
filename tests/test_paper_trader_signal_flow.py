from __future__ import annotations

import json
from pathlib import Path

from src.runtime.paper_trader import run_once


def test_signal_event_precedes_overlay_and_uses_consistent_bar_close_time(tmp_path: Path) -> None:
    event_log_path = tmp_path / "logs" / "paper_trader" / "events.jsonl"
    config_path = tmp_path / "paper_runtime.json"
    latest_bar_path = tmp_path / "reports" / "runtime" / "latest_bar_timestamp.json"
    latest_bar_path.parent.mkdir(parents=True, exist_ok=True)
    latest_bar_path.write_text(
        json.dumps({"latest_bar_timestamp_utc": "2026-01-01T01:00:00Z"}),
        encoding="utf-8",
    )

    config = {
        "env": "PAPER",
        "symbol": "BTCUSDT",
        "decision_id": "D-0001",
        "macro_flags_path": str(tmp_path / "missing_macro_window_flags.json"),
        "event_log_path": str(event_log_path),
        "signal_provider": "flat",
        "freshness_tolerance_seconds": 60,
        "latest_bar_time_path": str(latest_bar_path),
        "run_id": "RUN-TEST-0004",
        "correlation_id": "RUN-TEST-0004",
    }
    config_path.write_text(json.dumps(config), encoding="utf-8")

    exit_code = run_once(str(config_path), bar_close_time_utc="2026-01-01T01:00:00Z")

    assert exit_code == 0

    events = [json.loads(line) for line in event_log_path.read_text(encoding="utf-8").splitlines()]
    event_types = [event["event_type"] for event in events]

    signal_idx = event_types.index("SignalEvent")
    overlay_idx = event_types.index("OverlayDecision")
    order_intent_idx = event_types.index("OrderIntent")

    assert signal_idx < overlay_idx < order_intent_idx

    for event in events:
        assert event["bar_close_time_utc"] == "2026-01-01T01:00:00Z"

    signal_event = events[signal_idx]
    overlay_event = events[overlay_idx]
    assert signal_event["payload"]["evaluation_time_utc"] == "2026-01-01T01:00:00Z"
    assert overlay_event["payload"]["evaluation_time_utc"] == "2026-01-01T01:00:00Z"


def test_null_like_latest_bar_path_does_not_skip_signal_flow(tmp_path: Path) -> None:
    event_log_path = tmp_path / "logs" / "paper_trader" / "events.jsonl"
    config_path = tmp_path / "paper_runtime.json"

    config = {
        "env": "PAPER",
        "symbol": "BTCUSDT",
        "decision_id": "D-0001",
        "macro_flags_path": str(tmp_path / "missing_macro_window_flags.json"),
        "event_log_path": str(event_log_path),
        "signal_provider": "flat",
        "freshness_tolerance_seconds": 60,
        "latest_bar_time_path": "null",
        "run_id": "RUN-TEST-0005",
        "correlation_id": "RUN-TEST-0005",
    }
    config_path.write_text(json.dumps(config), encoding="utf-8")

    exit_code = run_once(str(config_path), bar_close_time_utc="2026-01-01T01:00:00Z")

    assert exit_code == 0

    events = [json.loads(line) for line in event_log_path.read_text(encoding="utf-8").splitlines()]
    event_types = [event["event_type"] for event in events]

    assert "SignalEvent" in event_types
    assert "OverlayDecision" in event_types
    assert event_types.index("SignalEvent") < event_types.index("OverlayDecision")