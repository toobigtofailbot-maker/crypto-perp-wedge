from __future__ import annotations

from src.execution.interfaces import DesiredPosition
from src.signal.provider import build_signal_provider


def test_flat_signal_provider_returns_deterministic_flat_desired_position() -> None:
    provider = build_signal_provider("flat")
    inputs = {
        "symbol": "BTCUSDT",
        "decision_id": "D-0001",
        "correlation_id": "RUN-TEST-0003",
        "run_id": "RUN-TEST-0003",
        "source_timeframe": "1m",
    }

    first = provider.compute_desired_position("2026-01-01T01:00:00Z", inputs)
    second = provider.compute_desired_position("2026-01-01T01:00:00Z", inputs)

    assert isinstance(first, DesiredPosition)
    assert first == second
    assert first.symbol == "BTCUSDT"
    assert str(first.target_qty) == "0"
    assert first.target_notional is None
    assert first.timestamp_utc == "2026-01-01T01:00:00Z"
    assert first.source_timeframe == "1m"
