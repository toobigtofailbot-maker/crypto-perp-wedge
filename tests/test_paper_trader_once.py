from __future__ import annotations

import json
from pathlib import Path

from src.runtime.paper_trader import run_once


def test_run_once_writes_structured_events(tmp_path: Path) -> None:
    event_log_path = tmp_path / "logs" / "paper_trader" / "events.jsonl"
    config_path = tmp_path / "paper_runtime.json"

    config = {
        "env": "PAPER",
        "symbol": "BTCUSDT",
        "decision_id": "D-0001",
        "macro_flags_path": str(tmp_path / "missing_macro_window_flags.json"),
        "event_log_path": str(event_log_path),
        "evaluation_time_source": "fixed",
        "evaluation_time_utc": "2026-01-01T00:00:00Z",
        "run_id": "RUN-TEST-0001",
        "correlation_id": "RUN-TEST-0001",
    }
    config_path.write_text(json.dumps(config), encoding="utf-8")

    exit_code = run_once(str(config_path))

    assert exit_code == 0
    assert event_log_path.exists() is True

    lines = event_log_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) >= 5

    events = [json.loads(line) for line in lines]
    event_types = [event["event_type"] for event in events]

    assert event_types[0] == "SystemEvent"
    assert "OverlayDecision" in event_types
    assert "RiskDecision" in event_types
    assert "OrderIntent" in event_types
    assert event_types[-1] == "SystemEvent"

    for event in events:
        assert event["env"] == "PAPER"
        assert event["decision_id"] == "D-0001"
        assert event["run_id"] == "RUN-TEST-0001"
        assert event["correlation_id"] == "RUN-TEST-0001"
        assert "timestamp_utc" in event
