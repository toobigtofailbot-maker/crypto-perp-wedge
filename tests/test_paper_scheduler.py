from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from src.runtime.paper_trader import main as paper_trader_main
from src.runtime.scheduler import next_hour_close_utc


def test_next_hour_close_utc_rounds_forward() -> None:
    now = datetime(2026, 1, 1, 1, 23, 45, tzinfo=timezone.utc)
    expected = datetime(2026, 1, 1, 2, 0, 0, tzinfo=timezone.utc)
    assert next_hour_close_utc(now) == expected


def test_next_hour_close_utc_exact_hour_moves_to_next_hour() -> None:
    now = datetime(2026, 1, 1, 1, 0, 0, tzinfo=timezone.utc)
    expected = datetime(2026, 1, 1, 2, 0, 0, tzinfo=timezone.utc)
    assert next_hour_close_utc(now) == expected


def test_once_at_writes_bar_close_time_utc(tmp_path: Path, monkeypatch) -> None:
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
        "freshness_tolerance_seconds": 60,
        "latest_bar_time_path": str(latest_bar_path),
        "run_id": "RUN-TEST-0002",
        "correlation_id": "RUN-TEST-0002",
    }
    config_path.write_text(json.dumps(config), encoding="utf-8")

    monkeypatch.setattr(
        "sys.argv",
        [
            "paper_trader",
            "--once-at",
            "2026-01-01T01:00:00Z",
            "--config",
            str(config_path),
        ],
    )

    exit_code = paper_trader_main()
    assert exit_code == 0

    events = [json.loads(line) for line in event_log_path.read_text(encoding="utf-8").splitlines()]
    assert len(events) >= 2
    assert all(event["bar_close_time_utc"] == "2026-01-01T01:00:00Z" for event in events)
